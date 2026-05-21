#!/usr/bin/env python

import argparse
import shutil
import sys

import planning.datalog as datalog
import planning.pddl as pddl
from compilation.query_rewriter import prepare_queries
from compilation.ucq_collector import UCQCollector
from compilation.utils import (
    INCONSISTENCY_PREDICATE_NAME,
    QUERY_PREDICATE_NAME,
    encodes_inconsistency,
    get_parameter_list,
    get_query_id,
    is_coherence_update_predicate_name,
    is_primed_predicate_name,
    is_update_predicate_name,
    prime_predicate_name,
    query_predicate_name,
    unprime_predicate_name,
)
from compilation.variant_options import (
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
    UPDATING_PREDICATE_TYPES,
)
from rewriting.clipper import Clipper
from update_runner import Timer, make_update_runner, transform_incompatible_update
from utils.functions import parse_name


def _parse_datalog_rules(
    raw_rules, unparameterized, update_runner, filter_duplicates, expensive
):
    """Parse raw Datalog strings into rule objects, deduplicating if requested.

    Returns (rules, duplicate_rules).
    """
    rules = set() if filter_duplicates else []
    duplicates = set()
    inconsistent_atom = datalog.Atom(INCONSISTENCY_PREDICATE_NAME, [])

    for dlr in raw_rules:
        if not dlr.strip():
            continue
        rule = datalog.parse_rule(dlr)
        if encodes_inconsistency(rule.head):
            rule.head = inconsistent_atom
        if expensive:
            rule = rule.canonical()
        query_id = get_query_id(rule.head.name)
        if (query_id is not None and query_id in unparameterized) or (
            update_runner and is_update_predicate_name(rule.head.name)
        ):
            rule.head.parameters = []
        if filter_duplicates:
            old_size = len(rules)
            rules.add(rule)
            if old_size == len(rules):
                duplicates.add(rule)
        else:
            rules.append(rule)

    if filter_duplicates:
        rules = list(rules)
    return rules, duplicates


def _filter_irrelevant_rules(rules, queried_predicates, num_ucqs, update_runner):
    """Remove Datalog rules whose heads cannot contribute to any queried predicate.

    Returns (relevant_rules, irrelevant_rules).
    """
    necessary = queried_predicates | {query_predicate_name(i) for i in range(num_ucqs)}
    if not update_runner:
        necessary = necessary | {INCONSISTENCY_PREDICATE_NAME}

    conditioned = necessary  # same object; necessary grows monotonically below
    for rule in rules:
        for t in rule.tail:
            if isinstance(t, datalog.Negated):
                t = t.element
            if isinstance(t, datalog.Atom):
                conditioned.add(t.name)
        if update_runner and is_coherence_update_predicate_name(rule.head.name):
            conditioned.add(rule.head.name)

    irrelevant = []
    while True:
        relevant = []
        for rule in rules:
            if rule.head.name in conditioned:
                relevant.append(rule)
                for t in rule.tail:
                    if isinstance(t, datalog.Negated):
                        t = t.element
                    if isinstance(t, datalog.Atom):
                        conditioned.add(t.name)
            else:
                irrelevant.append(rule)
        if len(rules) == len(relevant):
            break
        rules = relevant

    return rules, irrelevant


class Compiler:
    def __init__(
        self,
        domain,
        problem,
        clipper,
        filter_duplicates=True,
        filter_unimportant_atoms=True,
        expensive_duplicate_filtering=False,
        update_runner=None,
        timer_output=None,
    ):
        self.domain = domain
        self.problem = problem
        self.clipper = clipper
        self.ucq_collector = UCQCollector(clipper)
        self.filter_unimportant_atoms = filter_unimportant_atoms
        self.filter_duplicates = filter_duplicates
        self.expensive_duplicate_filtering = expensive_duplicate_filtering
        self.update_runner = update_runner
        self.timer_output = timer_output

    def __call__(self):
        with Timer("compilation", block=True, file=self.timer_output):
            if self.update_runner:
                with Timer("domain_extension", file=self.timer_output):
                    self._extend_for_coherence_update()

            with Timer("collecting_queries", file=self.timer_output):
                self._apply_to_all_conditions(
                    pddl.MinimalKnowledgeOperator, self.ucq_collector
                )

            with Timer("rewriting", file=self.timer_output):
                self._queries, unparameterized = prepare_queries(
                    self.ucq_collector.ucqs
                )
                raw_rules = self._rewrite_via_clipper(self._queries)

            if self.update_runner:
                with Timer("construct_update_rules", file=self.timer_output):
                    raw_rules.extend(self.update_runner.run())
                    raw_rules.extend(self._missing_predicate_rules())

            with Timer("gen_derived_predicates", file=self.timer_output):
                self._adapt_predicate_names_to_clipper()
                self._collect_predicate_information()
                self._datalog_rules, self._duplicate_rules = _parse_datalog_rules(
                    raw_rules,
                    unparameterized,
                    self.update_runner,
                    self.filter_duplicates,
                    self.expensive_duplicate_filtering,
                )
                if self.filter_unimportant_atoms:
                    self._datalog_rules, self._unimportant_rules = (
                        _filter_irrelevant_rules(
                            self._datalog_rules,
                            self.ucq_collector.queried_predicates,
                            len(self.ucq_collector.ucqs),
                            self.update_runner,
                        )
                    )
                else:
                    self._unimportant_rules = []
                if (
                    self.update_runner
                    and self.update_runner.incompatible_update_pred_type
                    == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]
                ):
                    self._datalog_rules, compatible_update = (
                        transform_incompatible_update(self._datalog_rules)
                    )
                    self.domain.derived_predicates.append(compatible_update)
                self._compile_datalog_rules()

            with Timer("finalizing", file=self.timer_output):
                self._unprime_conditions_and_enforce_consistency()

    # -------------------------------------------------------------------------
    # Pipeline steps
    # -------------------------------------------------------------------------

    def _extend_for_coherence_update(self):
        self.domain.adjust_actions(self.update_runner.updating_pred_type)
        self.domain.construct_update_action(
            self.update_runner.updating_pred_type,
            self.update_runner.incompatible_update_pred_type,
        )
        self.problem.extend_for_coherence_update()

    def _rewrite_via_clipper(self, queries):
        if self.clipper.supports_simultaneous_rewriting() and queries:
            return self.clipper.rewrite_all("\n".join("\n".join(qs) for qs in queries))
        rules = self.clipper.rewrite_ontology()
        for qs in queries:
            for q in qs:
                rules.extend(self.clipper.rewrite_cq(q))
        return rules

    def _missing_predicate_rules(self):
        appeared_in_domain = {
            p.name
            for p in self.domain.predicates
            if not is_coherence_update_predicate_name(p.name)
        }
        missing = appeared_in_domain - self.update_runner.atomic_predicates()
        concepts, roles = [], []
        for pred in self.domain.predicates:
            if pred.name not in missing:
                continue
            name = parse_name(pred.name)
            if len(pred.parameters) == 1:
                concepts.append(name)
            elif len(pred.parameters) == 2:
                roles.append(name)
            else:
                raise ValueError(f"Unexpected predicate arity for {pred.name!r}")
        return self.update_runner.run_for_missing_predicates(concepts, roles)

    def _adapt_predicate_names_to_clipper(self):
        for p in self.domain.predicates:
            if is_coherence_update_predicate_name(p.name):
                continue
            p.name = self.clipper.adapt_predicate_name(p.name)

        def apply_to_fact(fact):
            if is_primed_predicate_name(
                fact.predicate
            ) or is_coherence_update_predicate_name(fact.predicate):
                return fact
            return pddl.Fact(
                self.clipper.adapt_predicate_name(fact.predicate), fact.parameters
            )

        def apply_to_effect(eff):
            return eff.__class__(apply_to_fact(eff.fact))

        self._apply_to_all_conditions(pddl.Fact, apply_to_fact)
        self._apply_to_all_effects(pddl.AddEffect, apply_to_effect)
        self._apply_to_all_effects(pddl.DelEffect, apply_to_effect)
        for i, p in enumerate(self.problem.initial_state):
            if isinstance(p, pddl.Fact):
                self.problem.initial_state[i] = apply_to_fact(p)

    def _collect_predicate_information(self):
        self.predicates = {p.name for p in self.domain.predicates}

        if (
            self.update_runner
            and self.update_runner.incompatible_update_pred_type
            == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]
        ):
            assert (
                "incompatible_update" not in self.predicates
                and "compatible_update" in self.predicates
            ), "incompatible_update should not be in predicates"

        self.predicate_arity = {
            p.name: sum(len(tl.elements) for tl in p.parameters)
            for p in self.domain.predicates
        }
        self.num_derived_predicates = len(self.domain.derived_predicates)

    def _compile_datalog_rules(self):
        self.predicates_in_ontology = set(self.ucq_collector.queried_predicates)

        for rule in self._datalog_rules:
            subst = {}
            num_ext = 0
            for i, x in enumerate(sorted(rule.distinguished_vars())):
                subst[x] = f"?x{i}"
            for i, x in enumerate(sorted(rule.existential_vars())):
                constant = x.split('"')
                if len(constant) == 3:
                    subst[x] = constant[1]
                else:
                    subst[x] = f"?y{num_ext}"
                    num_ext += 1

            is_update_rule = is_coherence_update_predicate_name(rule.head.name)
            if self.update_runner and is_update_rule:
                head_pred_name = rule.head.name
            else:
                head_pred_name = prime_predicate_name(rule.head.name)

            predicate = pddl.Predicate(
                head_pred_name,
                [pddl.TypedList([subst[x] for x in rule.head.parameters])],
            )

            if head_pred_name not in self.predicates:
                self.domain.predicates.append(predicate)
                self.predicates.add(head_pred_name)
                if (
                    rule.head.name in self.predicates
                    and not rule.head.name.startswith(QUERY_PREDICATE_NAME)
                    and rule.head.name != INCONSISTENCY_PREDICATE_NAME
                    and not is_update_rule
                ):
                    self.domain.derived_predicates.append(
                        pddl.DerivedPredicate(
                            predicate,
                            pddl.Fact(
                                rule.head.name, [subst[x] for x in rule.head.parameters]
                            ),
                        )
                    )

            self.predicates_in_ontology.add(rule.head.name)

            cond = []
            for t in rule.tail:
                neg = isinstance(t, datalog.Negated)
                if neg:
                    t = t.element
                if isinstance(t, datalog.Atom):
                    if self.update_runner and is_update_rule:
                        cond.append(pddl.Fact(t.name, [subst[x] for x in t.parameters]))
                    else:
                        cond.append(
                            pddl.Fact(
                                prime_predicate_name(t.name),
                                [subst[x] for x in t.parameters],
                            )
                        )
                    self.predicates_in_ontology.add(t.name)
                else:
                    cond.append(
                        pddl.Comparison(
                            "=",
                            pddl.SimpleFExpression(subst[t.left]),
                            pddl.SimpleFExpression(subst[t.right]),
                        )
                    )
                if neg:
                    cond[-1] = pddl.Not(cond[-1])

            cond = pddl.And(cond)
            if num_ext > 0:
                cond = pddl.Exists(get_parameter_list(num_ext, "?y%d"), cond)
            self.domain.derived_predicates.append(
                pddl.DerivedPredicate(predicate, cond)
            )

    def _unprime_conditions_and_enforce_consistency(self):
        def unprimer(fact):
            if fact.predicate not in self.predicates:
                assert is_primed_predicate_name(fact.predicate), (
                    f"{fact.predicate} does not appear in predicates"
                )
                unprimed = unprime_predicate_name(fact.predicate)
                if unprimed.startswith(QUERY_PREDICATE_NAME.lower()):
                    return pddl.Falsity()
                return pddl.Fact(unprimed, fact.parameters)
            return fact

        self._apply_to_all_conditions(pddl.Fact, unprimer)
        if (
            prime_predicate_name(INCONSISTENCY_PREDICATE_NAME) in self.predicates
            and not self.update_runner
        ):
            is_consistent = pddl.Not(
                pddl.Fact(prime_predicate_name(INCONSISTENCY_PREDICATE_NAME), [])
            )
            for action in self.domain.actions:
                action.precondition = pddl.And(
                    [is_consistent, action.precondition]
                ).simplified()
            self.problem.goal = pddl.And(
                [is_consistent, self.problem.goal]
            ).simplified()
        else:
            for action in self.domain.actions:
                action.precondition = pddl.And([action.precondition]).simplified()
            self.problem.goal = pddl.And([self.problem.goal]).simplified()

    # -------------------------------------------------------------------------
    # AST visitor helpers
    # -------------------------------------------------------------------------

    def _apply_to_all_conditions(self, typ, fn):
        def ce_wrapper(eff):
            new_cond = eff.condition.apply(typ, fn)
            new_eff = eff.effect.apply(pddl.ConditionalEffect, ce_wrapper)
            return pddl.ConditionalEffect(new_cond, new_eff)

        for deriv in self.domain.derived_predicates:
            deriv.condition = deriv.condition.apply(typ, fn)
        for action in self.domain.actions:
            action.precondition = action.precondition.apply(typ, fn)
            action.effect = action.effect.apply(pddl.ConditionalEffect, ce_wrapper)
        self.problem.goal = self.problem.goal.apply(typ, fn)

    def _apply_to_all_effects(self, typ, fn):
        for action in self.domain.actions:
            action.effect = action.effect.apply(typ, fn)

    # -------------------------------------------------------------------------
    # Debug output
    # -------------------------------------------------------------------------

    def print_compilation_information(self):
        ontology = []
        queries = []
        updates = []
        for rule in self._datalog_rules:
            if rule.head.name.startswith(QUERY_PREDICATE_NAME):
                queries.append(rule)
            elif is_coherence_update_predicate_name(rule.head.name):
                updates.append(rule)
            else:
                ontology.append(rule)
        print("%% ONTOLOGY")
        for rule in sorted(ontology):
            print(rule)
        queries = list(sorted(queries))
        i = 0
        for j, qs in enumerate(self._queries):
            print("")
            for q in qs:
                print("%% " + q)
            for k in range(i, len(queries)):
                if queries[k].head.name != query_predicate_name(j):
                    i = k
                    break
                print(queries[k])
        print("")

        if self._duplicate_rules:
            print("%% DUPLICATE RULES:")
            for rule in self._duplicate_rules:
                print(f"%% {rule}")
            print("")

        if self.update_runner:
            print("%% UPDATE RULES:")
            for rule in sorted(updates):
                print(f"%% {rule}")
            print("")

        if self._unimportant_rules:
            print("%% IRRELEVANT RULES:")
            for rule in self._unimportant_rules:
                print(f"%% {rule}")
            print("")

        static_datalog_atoms = sorted(
            p
            for p in self.predicates_in_ontology
            if prime_predicate_name(p) not in self.predicates
            and not is_coherence_update_predicate_name(p)
        )
        if static_datalog_atoms:
            print("%% CONCEPTS/RELATIONS NOT DERIVABLE FROM ONTOLOGY:")
            for name in static_datalog_atoms:
                print(f"%% {name}")
            print("")


def compile_pddl(
    ontology: str,
    in_domain: str,
    in_problem: str,
    out_domain: str,
    out_problem: str,
    clipper_path: str,
    clipper_mqf: bool = True,
    dl_lite_fragment: str = "core",
    rls_path: str = "",
    nmo_path: str = "",
    updating_pred_type: str = UPDATING_PREDICATE_TYPES["derived_predicate"],
    incompatible_update_pred_type: str = INCOMPATIBLE_UPDATE_PREDICATE_TYPES[
        "incompatible_update"
    ],
    filter_unimportant: bool = True,
    expensive_filtering: bool = True,
    timer_output: str = "result.csv",
    verbose: bool = False,
    debug: bool = False,
) -> None:
    if shutil.which(clipper_path) is None:
        raise FileNotFoundError(f"Clipper not found: {clipper_path!r}")

    clipper = Clipper(clipper_path, ontology, clipper_mqf, debug)

    with open(in_domain) as f:
        domain = pddl.parse_domain(f.read())
    with open(in_problem) as f:
        problem = pddl.parse_problem(f.read())

    do_coherence_update = dl_lite_fragment == "horn" or bool(rls_path and nmo_path)
    update_runner = (
        make_update_runner(
            fragment=dl_lite_fragment,
            ontology_file_path=ontology,
            nmo_path=nmo_path,
            rls_file_path=rls_path,
            timer_output=timer_output,
            updating_pred_type=updating_pred_type,
            incompatible_update_pred_type=incompatible_update_pred_type,
        )
        if do_coherence_update
        else None
    )

    compiler = Compiler(
        domain,
        problem,
        clipper,
        filter_unimportant_atoms=filter_unimportant,
        expensive_duplicate_filtering=expensive_filtering,
        update_runner=update_runner,
        timer_output=timer_output,
    )
    compiler()

    if verbose:
        compiler.print_compilation_information()

    domain.constants = problem.objects
    problem.objects = None
    with open(out_domain, "w") as f:
        f.write(str(domain))
    with open(out_problem, "w") as f:
        f.write(str(problem))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ontology")
    parser.add_argument("domain")
    parser.add_argument("problem")
    parser.add_argument("--rls", default="")
    parser.add_argument("--nmo", default="")
    parser.add_argument(
        "--dl-lite-fragment",
        default="core",
        choices=["core", "horn"],
        help="DL-Lite fragment to use for the coherence update (default: core).",
    )
    parser.add_argument("--output-csv", default="results.csv")
    parser.add_argument("--benchmark-name", default="test 1")
    parser.add_argument(
        "--updating-pred-type", default=UPDATING_PREDICATE_TYPES["derived_predicate"]
    )
    parser.add_argument(
        "--incompatible-update-pred-type",
        default=INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"],
    )
    parser.add_argument("--clipper-mqf", default=False, action="store_true")
    parser.add_argument("--clipper", default="clipper.sh")
    parser.add_argument("--out-domain", "-d", default="domain.pddl")
    parser.add_argument("--out-problem", "-p", default="problem.pddl")
    parser.add_argument("--verbose", "-v", default=False, action="store_true")
    parser.add_argument("--no-filter-unimportant", default=False, action="store_true")
    parser.add_argument("--no-expensive-filtering", default=False, action="store_true")
    parser.add_argument("--debug", default=False, action="store_true")
    args = parser.parse_args()

    if args.updating_pred_type not in UPDATING_PREDICATE_TYPES:
        print(
            "Invalid updating predicate type. Available types are: %s"
            % ", ".join(UPDATING_PREDICATE_TYPES.keys())
        )
        sys.exit(1)
    if args.incompatible_update_pred_type not in INCOMPATIBLE_UPDATE_PREDICATE_TYPES:
        print(
            "Invalid incompatible update predicate type. Available types are: %s"
            % ", ".join(INCOMPATIBLE_UPDATE_PREDICATE_TYPES.keys())
        )
        sys.exit(1)

    with open(args.output_csv, "a") as f:
        f.write(args.benchmark_name + ",")

    compile_pddl(
        ontology=args.ontology,
        in_domain=args.domain,
        in_problem=args.problem,
        out_domain=args.out_domain,
        out_problem=args.out_problem,
        clipper_path=args.clipper,
        clipper_mqf=args.clipper_mqf,
        dl_lite_fragment=args.dl_lite_fragment,
        rls_path=args.rls,
        nmo_path=args.nmo,
        updating_pred_type=args.updating_pred_type,
        incompatible_update_pred_type=args.incompatible_update_pred_type,
        filter_unimportant=not args.no_filter_unimportant,
        expensive_filtering=not args.no_expensive_filtering,
        timer_output=args.output_csv,
        verbose=args.verbose,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
