#!/usr/bin/env python

import argparse

import pddl
from update_runner import Timer

AUX_PREDICATE_NAME = "AUX"

def get_params(el):
    try:
        if isinstance(el, pddl.Not):
            return get_params(el.element)
        if isinstance(el, pddl.Comparison):
            return get_params(el.left) + get_params(el.right)
        if isinstance(el, pddl.SimpleFExpression):
            return [el.expression]
        # if isinstance(el, pddl.FExpression):
        #     return get_params(el.elements)
        return el.parameters
    except AttributeError:
        breakpoint()

class Tseitin:
    def __init__(self,
                 domain,
                 problem):
        self.domain = domain
        self.problem = problem

    def __call__(self):
        with Timer("tseitin_transformation", file=args.output_csv):
            self._derived_predicates_count = 0
            self._new_derived_predicates = []
            self._create_shortcuts_conditions()
            self.domain.derived_predicates.extend(self._new_derived_predicates)

    def _create_shortcuts_conditions(self):
        for deriv in self.domain.derived_predicates:
            new_formula = self._create_shortcuts_all(deriv.condition, deriv.predicate.parameters)
            deriv.condition = new_formula
        for action in self.domain.actions:
            new_formula = self._create_shortcuts_all(action.precondition, action.parameters)
            action.precondition = new_formula
            new_effect = self._create_shortcuts_effect(action.effect, action.parameters)
            action.effect = new_effect
        new_goal = self._create_shortcuts_all(self.problem.goal, [])
        self.problem.goal = new_goal

    def _create_shortcuts_effect(self, eff, par):
        if isinstance(eff, pddl.ConditionalEffect):
            cond = self._create_shortcuts_all(eff.condition, par)
            eff.condition = cond
            new_eff = self._create_shortcuts_effect(eff.effect, par)
            eff.effect = new_eff
            return eff
        if isinstance(eff, pddl.ConjunctiveEffect):
            effects = []
            for e in eff.elements:
                effects.append(self._create_shortcuts_effect(e, par))
            return pddl.ConjunctiveEffect(effects)
        return eff

    def _create_shortcuts_all(self, formula, par):
        if isinstance(formula, (pddl.Exists, pddl.Or)):
            return self._create_shortcuts_disjunction(formula, par)
        if isinstance(formula, (pddl.Forall, pddl.And)):
            return self._create_shortcuts_conjunction(formula, par)
        return formula

    def _create_shortcuts_disjunction(self, formula, free_parameters):
        if isinstance(formula, pddl.Exists):
            new_formula = self._create_shortcuts_disjunction(formula.formula, free_parameters + formula.parameters)
            return pddl.Exists(formula.parameters, new_formula)
        if isinstance(formula, pddl.Or):
            new_conjuncts = []
            for element in formula.elements:
                pred = self._create_shortcuts_disjunction(element, free_parameters)
                new_conjuncts.append(pred)
            return pddl.Or(new_conjuncts)
        if isinstance(formula, (pddl.Forall, pddl.And)):
            new_form = self._create_shortcuts_conjunction(formula, free_parameters)
            shortcut = self._create_shortcut(new_form, free_parameters)
            fact = pddl.Fact(shortcut.name, [tl.elements[0] for tl in shortcut.parameters])
            return fact
        return formula

    def _create_shortcuts_conjunction(self, formula, free_parameters):
        if isinstance(formula, pddl.Forall):
            pred = self._create_shortcuts_conjunction(formula.formula, free_parameters + formula.parameters)
            return pddl.Forall(formula.parameters, pred)
        if isinstance(formula, pddl.And):
            shortcuts = []
            for element in formula.elements:
                pred = self._create_shortcuts_conjunction(element, free_parameters)
                shortcuts.append(pred)
            return pddl.And(shortcuts)
        if isinstance(formula, (pddl.Exists, pddl.Or)):
            new_form = self._create_shortcuts_disjunction(formula, free_parameters)
            pred = self._create_shortcut(new_form, free_parameters)
            fact = pddl.Fact(pred.name, [tl.elements[0] for tl in pred.parameters])
            return fact
        return formula

    def _create_shortcut(self, formula, par):
        if isinstance(formula, pddl.Fact):
            return formula
        name = AUX_PREDICATE_NAME + str(self._derived_predicates_count)
        self._derived_predicates_count += 1
        vars = formula.free_vars()
        params = []
        for var in vars:
            for typed_list in reversed(par):
                if var in typed_list.elements:
                    params.append(pddl.TypedList([var], typed_list.type))
                    break

        pred = pddl.Predicate(name, params)
        dp = pddl.DerivedPredicate(pred, formula)
        self.domain.predicates.append(pred)
        self._new_derived_predicates.append(dp)
        return pred

    def print_information(self):
        print("%% Tseitin transformation for PDDL using derived predicates")
        print("")
        if len(self._new_derived_predicates) > 0:
            print("%% NEW DERIVED PREDICATES:")
            for dp in self._new_derived_predicates:
                print("%% %s" % dp)
            print("")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain")
    p.add_argument("problem")
    p.add_argument("--out-domain", "-d", default="one-time/outputs/domain_test.pddl")
    p.add_argument("--out-problem", "-p", default="one-time/outputs/problem_test.pddl")
    p.add_argument("--verbose", "-v", default=False, action='store_true')
    p.add_argument("--keep-name", "-n", default=False, action='store_true')
    p.add_argument("--output-csv", default="results.csv")
    p.add_argument("--benchmark-name", default="test 1")

    args = p.parse_args()
    preserve_names = args.keep_name
    with open(args.domain) as f:
        d = pddl.parse_domain(f.read(), preserve_predicate_names=preserve_names)
    with open(args.problem) as f:
        p = pddl.parse_problem(f.read())
    tseitin = Tseitin(d, p)
    tseitin()
    with open(args.out_domain, "w") as f:
        f.write(str(d))
    with open(args.out_problem, "w") as f:
        f.write(str(p))
    if args.verbose:
        tseitin.print_information()
