#!/usr/bin/env python

import argparse

import planning.pddl as pddl
from update_runner import Timer

AUX_PREDICATE_NAME = "AUX"

"""
dnh: Flattening structures of PDDL files for faster planning
    And other stuffs
"""

class Tseitin:
    def __init__(self,
                 domain,
                 problem):
        self.domain = domain
        self.problem = problem

    def __call__(self):
        with Timer("tseitin_transformation", file=args.output_csv):
            self._derived_predicates_count = 0
            self._merged_derived_predicates = []
            self._new_derived_predicates = []
            # TODO: remove negation first, because that is not allowed in derived predicates
            self._merge_derived_predicates()
            self._create_shortcuts_conditions()
            # self._split_derived_predicates()
            # TODO: optimization: deal with isormophic subformulas -> only introduce one derived predicate per equivalence class?
            self._replace_subformulas()
            self.domain.derived_predicates.extend(self._new_derived_predicates)

    def _merge_derived_predicates(self):
        # merge rules with the same head into single disjunctive rules
        for pred in self.domain.predicates:
            rules = [rule for rule in self.domain.derived_predicates if rule.predicate.name == pred.name]
            if len(rules) > 1:
                disjuncts = []
                for rule in rules:
                    substitution = {}
                    for i in range(len(rule.predicate.parameters)):
                        for j in range(len(rule.predicate.parameters[i].elements)):
                            substitution[rule.predicate.parameters[i].elements[j]] = pred.parameters[i].elements[j]
                    disjuncts.append(rule.condition.instantiate(substitution))
                body = pddl.Or(disjuncts)
                dp = pddl.DerivedPredicate(pred, body)
                self.domain.derived_predicates.append(dp)
                self._merged_derived_predicates.append(dp)
                for rule in rules:
                    self.domain.derived_predicates.remove(rule)

    def _split_derived_predicates(self):
        # (optional) split derived predicates with "or"-rules again if they are
        # easier to handle that way
        obsolete = []
        for dp in self.domain.derived_predicates:
            if isinstance(dp.condition, pddl.Or):
                for disjunct in dp.condition.elements:
                    self.domain.derived_predicates.append(pddl.DerivedPredicate(dp.predicate, disjunct))
                obsolete.append(dp)
        for dp in obsolete:
            self.domain.derived_predicates.remove(dp)

    def _apply_to_all_conditions(self, typ, fn):
        def ce_wrapper(eff):
            new_cond = eff.condition.apply(typ, fn)
            new_eff = eff.effect.apply(pddl.ConditionalEffect, ce_wrapper)
            return pddl.ConditionalEffect(new_cond, new_eff)
        for deriv in self.domain.derived_predicates:
            deriv.condition = deriv.condition.apply(typ, fn)
        for action in self.domain.actions:
            action.precondition = action.precondition.apply(typ, fn)
            action.effect = action.effect.apply(
                    pddl.ConditionalEffect,
                    ce_wrapper)
        self.problem.goal = self.problem.goal.apply(typ, fn)

    def _create_shortcuts_effect(self, eff, par):
        if isinstance(eff, pddl.ConditionalEffect):
            self._create_shortcuts_all(eff.condition, par)
            self._create_shortcuts_effect(eff.effect, par)
        if isinstance(eff, pddl.ConjunctiveEffect):
            for e in eff.elements:
                self._create_shortcuts_effect(e, par)

    def _create_shortcuts_conditions(self):
        for deriv in self.domain.derived_predicates:
            self._create_shortcuts_all(deriv.condition, deriv.predicate.parameters)
        for action in self.domain.actions:
            self._create_shortcuts_all(action.precondition, action.parameters)
            self._create_shortcuts_effect(action.effect, action.parameters)
        self._create_shortcuts_all(self.problem.goal, [])

    def _create_shortcuts_all(self, formula, par):
        # Detect which type of formula is at the top level (disjunctive or
        # conjunctive) and create shortcuts for all largest subformulas of the
        # opposite type. Don't create shortcuts for literals.
        if isinstance(formula, (pddl.Exists, pddl.Or)):
            self._create_shortcuts_disjunction(formula, par)
        if isinstance(formula, (pddl.Forall, pddl.And)):
            self._create_shortcuts_conjunction(formula, par)

    def _create_shortcuts_disjunction(self, formula, par):
        # Traverse a disjunctive formula and create shortcuts for all
        # conjunctive subformulas.
        if isinstance(formula, pddl.Exists):
            self._create_shortcuts_disjunction(formula.formula, par + formula.parameters)
        if isinstance(formula, pddl.Or):
            for element in formula.elements:
                self._create_shortcuts_disjunction(element, par)
        if isinstance(formula, (pddl.Forall, pddl.And)):
            self._create_shortcut(formula, par)
            self._create_shortcuts_conjunction(formula, par)

    def _create_shortcuts_conjunction(self, formula, par):
        # Traverse a conjunctive formula and create shortcuts for all
        # disjunctive subformulas.
        if isinstance(formula, pddl.Forall):
            self._create_shortcuts_conjunction(formula.formula, par + formula.parameters)
        if isinstance(formula, pddl.And):
            for element in formula.elements:
                self._create_shortcuts_conjunction(element, par)
        if isinstance(formula, (pddl.Exists, pddl.Or)):
            self._create_shortcut(formula, par)
            self._create_shortcuts_disjunction(formula, par)

    def _create_shortcuts_effect_old(self, eff, par):
        if isinstance(eff, pddl.ConditionalEffect):
            self._create_shortcuts_dnf(eff.condition, par)
            self._create_shortcuts_effect_old(eff.effect, par)
        if isinstance(eff, pddl.ConjunctiveEffect):
            for e in eff.elements:
                self._create_shortcuts_effect_old(e, par)

    def _create_shortcuts_conditions_old(self):
        for deriv in self.domain.derived_predicates:
            self._create_shortcuts_dnf(deriv.condition, deriv.predicate.parameters)
        for action in self.domain.actions:
            self._create_shortcuts_dnf(action.precondition, action.parameters)
            self._create_shortcuts_effect_old(action.effect, action.parameters)
        self._create_shortcuts_dnf(self.problem.goal, [])

    def _create_shortcuts_dnf(self, formula, par):
        # Traverse down a disjunction until we come to a conjunctive "layer".
        # Collect all (typed) parameters encountered in the process.
        if isinstance(formula, pddl.Exists):
            self._create_shortcuts_dnf(formula.formula, par + formula.parameters)
        if isinstance(formula, pddl.Or):
            for element in formula.elements:
                self._create_shortcuts_dnf(element, par)
        if isinstance(formula, pddl.Forall):
            self._create_shortcuts_cnf(formula.formula, par + formula.parameters)
        if isinstance(formula, pddl.And):
            for element in formula.elements:
                self._create_shortcuts_cnf(element, par)

    def _create_shortcuts_cnf(self, formula, par):
        # Traverse down a conjunction until we come to a disjunctive "layer".
        # Add a new derived predicate for the disjunctive formula, continue
        # recursively with _create_shortcuts_dnf.
        if isinstance(formula, pddl.Forall):
            self._create_shortcuts_cnf(formula.formula, par + formula.parameters)
        if isinstance(formula, pddl.And):
            for element in formula.elements:
                self._create_shortcuts_cnf(element, par)
        if isinstance(formula, (pddl.Exists, pddl.Or)):
            self._create_shortcut(formula, par)
            self._create_shortcuts_dnf(formula, par)

    def _create_shortcut(self, formula, par):
        # first check whether a shortcut for the formula already exists
        for dp in self._new_derived_predicates:
            if dp.condition == formula:
                return
        # create new shortcut
        name = AUX_PREDICATE_NAME + str(self._derived_predicates_count)
        self._derived_predicates_count += 1
        vars = formula.free_vars()
        params = []
        for var in vars:
            # iterate through parameter list in reverse order, in case that the same
            # variable name was used multiple times
            for typed_list in reversed(par):
                if var in typed_list.elements:
                    params.append(pddl.TypedList([var], typed_list.type))
                    break
        pred = pddl.Predicate(name, params)
        dp = pddl.DerivedPredicate(pred, formula)
        self.domain.predicates.append(pred)
        self._new_derived_predicates.append(dp)

    def _replace_subformulas(self):
        for dp in self._new_derived_predicates:
            pred = dp.predicate
            cond = dp.condition
            fact = pddl.Fact(pred.name, [tl.elements[0] for tl in pred.parameters])
            # This should work with nested replacements, because the larger
            # formulas always come first in _new_derived_predicates, and
            # thus they are replaced first.
            def replace_cond(formula):
                if formula == cond:
                    return fact
                return formula
            self._apply_to_all_conditions(type(cond), replace_cond)
            for dp2 in self._new_derived_predicates:
                if dp2 is not dp:
                    dp2.condition = dp2.condition.apply(type(cond), replace_cond)

    def print_information(self):
        print("%% Tseitin transformation for PDDL using derived predicates")
        print("")
        if len(self._merged_derived_predicates) > 0:
            print("%% MERGED DERIVED PREDICATES:")
            for dp in self._merged_derived_predicates:
                print("%% %s" % dp)
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
    p.add_argument("--out-domain", "-d", default="domain.pddl")
    p.add_argument("--out-problem", "-p", default="problem.pddl")
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
