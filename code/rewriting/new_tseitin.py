import argparse

from update_runner import Timer
import planning.pddl as pddl

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
    def __init__(self, domain, problem, output_csv="results.csv"):
        self.domain = domain
        self.problem = problem
        self.output_csv = output_csv

    def __call__(self):
        with Timer("tseitin_transformation", file=self.output_csv):
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

def tseitin_pddl(
    in_domain: str,
    in_problem: str,
    out_domain: str,
    out_problem: str,
    keep_name: bool = False,
    timer_output: str = "result.csv",
    verbose: bool = False,
) -> None:
    with open(in_domain) as f:
        domain = pddl.parse_domain(f.read(), preserve_predicate_names=keep_name)
    with open(in_problem) as f:
        problem = pddl.parse_problem(f.read())
    tseitin = Tseitin(domain, problem, output_csv=timer_output)
    tseitin()
    with open(out_domain, "w") as f:
        f.write(str(domain))
    with open(out_problem, "w") as f:
        f.write(str(problem))
    if verbose:
        tseitin.print_information()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("domain")
    arg_parser.add_argument("problem")
    arg_parser.add_argument("--out-domain", "-d", default="one-time/outputs/domain_test.pddl")
    arg_parser.add_argument("--out-problem", "-p", default="one-time/outputs/problem_test.pddl")
    arg_parser.add_argument("--verbose", "-v", default=False, action="store_true")
    arg_parser.add_argument("--keep-name", "-n", default=False, action="store_true")
    arg_parser.add_argument("--output-csv", default="results.csv")
    args = arg_parser.parse_args()
    tseitin_pddl(
        in_domain=args.domain,
        in_problem=args.problem,
        out_domain=args.out_domain,
        out_problem=args.out_problem,
        keep_name=args.keep_name,
        timer_output=args.output_csv,
        verbose=args.verbose,
    )
