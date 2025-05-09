#!/usr/bin/env python

import argparse
import shutil
import sys

import planning.datalog as datalog
import planning.pddl as pddl
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
from update_runner import Timer, UpdateRunner, transform_incompatible_update
from utils.functions import parse_name


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
                    self.domain.adjust_actions(
                        self.update_runner.updating_pred_type,
                    )
                    self.domain.construct_update_action(
                        self.update_runner.updating_pred_type,
                        self.update_runner.incompatible_update_pred_type,
                    )
                    self.problem.extend_for_coherence_update()

            with Timer("collecting_queries", file=self.timer_output):
                self._collect_and_replace_ucqs()
            with Timer("rewriting", file=self.timer_output):
                self._prepare_queries_for_rewriting()
                self._rewrite_ontology_and_ucqs()
            if self.update_runner:
                with Timer("construct_update_rules", file=self.timer_output):
                    self._add_update_rules()
                    self._add_rules_for_missing_predicates()
            with Timer("gen_derived_predicates", file=self.timer_output):
                self._adapt_predicate_names_to_clipper()
                self._collect_predicate_information()
                self._create_datalog_rule_objects()
                if self.filter_unimportant_atoms:
                    self._drop_irrelevant_datalog_rules()
                self._compile_datalog_rules()
            with Timer("finalizing", file=self.timer_output):
                self._unprime_conditions_and_enforce_consistency()

    def _apply_to_all_conditions(self, typ, fn):
        def ce_wrapper(eff):
            new_cond = eff.condition.apply(typ, fn)
            new_eff = eff.effect.apply(pddl.ConditionalEffect, ce_wrapper)
            return pddl.ConditionalEffect(new_cond, new_eff)

        for _, deriv in enumerate(self.domain.derived_predicates):
            deriv.condition = deriv.condition.apply(typ, fn)
        for action in self.domain.actions:
            action.precondition = action.precondition.apply(typ, fn)
            action.effect = action.effect.apply(pddl.ConditionalEffect, ce_wrapper)
        self.problem.goal = self.problem.goal.apply(typ, fn)

    def _apply_to_all_effects(self, typ, fn):
        for action in self.domain.actions:
            action.effect = action.effect.apply(typ, fn)

    def _collect_predicate_information(self):
        self.predicates = set([p.name for p in self.domain.predicates])

        if self.update_runner and self.update_runner.incompatible_update_pred_type == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            assert (
                ('incompatible_update' not in self.predicates) and ('compatible_update' in self.predicates)
            ), "incompatible_update should not be in predicates"

        self.predicate_arity = {}
        for p in self.domain.predicates:
            n = 0
            for tl in p.parameters:
                n += len(tl.elements)
            self.predicate_arity[p.name] = n
        self.num_derived_predicates = len(self.domain.derived_predicates)

    def _collect_and_replace_ucqs(self):
        self._apply_to_all_conditions(pddl.MinimalKnowledgeOperator, self.ucq_collector)

    def _rewrite_cq(self, query_id, cq):
        free_vars = list(sorted(cq.free_vars()))
        has_free_vars = len(free_vars) > 0
        var_map = {}
        if has_free_vars:
            i = 0
            for x in free_vars:
                var_map[x] = "?%d" % i
                i += 1
        else:
            i = 1
        if isinstance(cq, pddl.Exists):
            cq = cq.formula
            for x in cq.free_vars():
                if not x in var_map:
                    var_map[x] = "?%d" % i
                    i += 1
        elements = []
        if isinstance(cq, pddl.And):
            elements = cq.elements
        else:
            assert isinstance(cq, pddl.Fact)
            elements = [cq]
        head = (
            query_predicate_name(query_id)
            + "("
            + (",".join([var_map[x] for x in free_vars]) if has_free_vars else "?0")
            + ")"
        )
        tail = [
            f.predicate
            + "("
            + ",".join([var_map.get(t, t) for t in f.parameters])
            + ")"
            for f in elements
        ]
        query = "%s <- %s" % (head, ", ".join(tail))
        self._queries[-1].append(query)
        if not has_free_vars:
            self._unparameterized_queries.add(query_id)

    def _prepare_queries_for_rewriting(self):
        self._queries = []
        self._unparameterized_queries = set()
        for idx, ucq in enumerate(self.ucq_collector.ucqs):
            self._queries.append([])
            if isinstance(ucq, pddl.Or):
                for cq in ucq.elements:
                    self._rewrite_cq(idx, cq)
            else:
                self._rewrite_cq(idx, ucq)

    def _rewrite_ontology_and_ucqs(self):
        if self.clipper.supports_simultaneous_rewriting() and len(self._queries) > 0:
            rewritten_rules = self.clipper.rewrite_all(
                "\n".join(["\n".join(qs) for qs in self._queries])
            )
            self._datalog_rules = rewritten_rules
        else:
            self._datalog_rules = self.clipper.rewrite_ontology()
            for qs in self._queries:
                for q in qs:
                    rules = self.clipper.rewrite_cq(q)
                    self._datalog_rules.extend(rules)

    def _add_update_rules(self):
        rules = self.update_runner.run()
        self._datalog_rules.extend(rules)

    def _add_rules_for_missing_predicates(self):
        # TODO(dnh): Leave unused predicates in domain and NOT in ontology untouch
        appeared_in_domain = set(
            [
                p.name
                for p in self.domain.predicates
                if not is_coherence_update_predicate_name(p.name)
            ]
        )
        missing = appeared_in_domain - self.update_runner.atomic_predicates()
        missing_predicates = [p for p in self.domain.predicates if p.name in missing]
        concepts = []
        roles = []
        for pred in missing_predicates:
            name = parse_name(pred.name)
            if len(pred.parameters) == 1:
                concepts.append(name)
            elif len(pred.parameters) == 2:
                roles.append(name)
            else:
                raise ValueError("Unexpected predicate arity: %d" % len(p.parameters))
        rules = self.update_runner.run_for_missing_predicates(concepts, roles)
        self._datalog_rules.extend(rules)

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
        for i in range(len(self.problem.initial_state)):
            p = self.problem.initial_state[i]
            if isinstance(p, pddl.Fact):
                self.problem.initial_state[i] = apply_to_fact(p)

    def _create_datalog_rule_objects(self):
        datalog_rules = self._datalog_rules
        self._datalog_rules = set() if self.filter_duplicates else list()
        self._duplicate_rules = set()
        self._unimportant_rules = []
        inconsistent_atom = datalog.Atom(INCONSISTENCY_PREDICATE_NAME, [])
        for _, dlr in enumerate(datalog_rules):
            if len(dlr.strip()) == 0:
                continue
            rule = datalog.parse_rule(dlr)
            if encodes_inconsistency(rule.head):
                rule.head = inconsistent_atom
            if self.expensive_duplicate_filtering:
                rule = rule.canonical()
            query_id = get_query_id(rule.head.name)
            if (
                query_id != None
                and query_id in self._unparameterized_queries
                or (self.update_runner and is_update_predicate_name(rule.head.name))
            ):
                rule.head.parameters = []
            if self.filter_duplicates:
                old_size = len(self._datalog_rules)
                self._datalog_rules.add(rule)
                if old_size == len(self._datalog_rules):
                    self._duplicate_rules.add(rule)
            else:
                self._datalog_rules.append(rule)
        if self.filter_duplicates:
            self._datalog_rules = list(self._datalog_rules)

    def _drop_irrelevant_datalog_rules(self):
        necessary_predicates = self.ucq_collector.queried_predicates | set(
            [query_predicate_name(i) for i in range(len(self.ucq_collector.ucqs))]
        )
        if not self.update_runner:
            necessary_predicates = necessary_predicates | set(
                [INCONSISTENCY_PREDICATE_NAME]
            )

        conditioned_predicates = necessary_predicates
        for rule in self._datalog_rules:
            for t in rule.tail:
                if isinstance(t, datalog.Negated):
                    t = t.element
                if isinstance(t, datalog.Atom):
                    conditioned_predicates.add(t.name)
            if self.update_runner and is_coherence_update_predicate_name(
                rule.head.name
            ):
                conditioned_predicates.add(rule.head.name)
        while True:
            dr = []
            cd = necessary_predicates
            for rule in self._datalog_rules:
                if rule.head.name in conditioned_predicates:
                    dr.append(rule)
                    for t in rule.tail:
                        if isinstance(t, datalog.Negated):
                            t = t.element
                        if isinstance(t, datalog.Atom):
                            cd.add(t.name)
                else:
                    self._unimportant_rules.append(rule)
            if len(self._datalog_rules) == len(dr):
                break
            self._datalog_rules = dr
            conditioned_predicates = cd

    def _compile_datalog_rules(self):
        self.predicates_in_ontology = set(self.ucq_collector.queried_predicates)
        if (
            self.update_runner
            and self.update_runner.incompatible_update_pred_type
            == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]
        ):
            self._datalog_rules, compatible_update = transform_incompatible_update(
                self._datalog_rules
            )
            self.domain.derived_predicates.append(compatible_update)

        for rule in self._datalog_rules:
            subst = {}
            num_ext = 0
            existential = rule.existential_vars()
            for i, x in enumerate(sorted(rule.distinguished_vars())):
                subst[x] = "?x%d" % i
            for i, x in enumerate(sorted(existential)):
                constant = x.split('"')
                if len(constant) == 3:
                    subst[x] = constant[1]
                else:
                    subst[x] = "?y%d" % num_ext
                    num_ext += 1

            # dnh: Do not transform update predicates
            if self.update_runner and is_coherence_update_predicate_name(
                rule.head.name
            ):
                primed_predicate_name = rule.head.name
            else:
                primed_predicate_name = prime_predicate_name(rule.head.name)
            predicate = pddl.Predicate(
                primed_predicate_name,
                [pddl.TypedList([subst[x] for x in rule.head.parameters])],
            )
            is_update_rule = is_coherence_update_predicate_name(rule.head.name)
            if not primed_predicate_name in self.predicates:
                self.domain.predicates.append(predicate)
                self.predicates.add(primed_predicate_name)
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
                neg = False
                if isinstance(t, datalog.Negated):
                    neg = True
                    t = t.element
                if isinstance(t, datalog.Atom):
                    # dnh: Do not transform body if it's update predicates
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
                    # TODO correct?
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
            # dnh: Existential quantifiers are required for updating rules
            if num_ext > 0:
                cond = pddl.Exists(get_parameter_list(num_ext, "?y%d"), cond)
            self.domain.derived_predicates.append(
                pddl.DerivedPredicate(predicate, cond)
            )

    def _unprime_conditions_and_enforce_consistency(self):
        def unprimer(fact):
            if not fact.predicate in self.predicates:
                assert is_primed_predicate_name(fact.predicate), (
                    "%s does not appear in predicates" % fact.predicate
                )
                unprimed = unprime_predicate_name(fact.predicate)
                if unprimed.startswith(QUERY_PREDICATE_NAME.lower()):
                    return pddl.Falsity()
                return pddl.Fact(unprimed, fact.parameters)
            return fact

        self._apply_to_all_conditions(pddl.Fact, unprimer)
        if (
            prime_predicate_name(INCONSISTENCY_PREDICATE_NAME) in self.predicates
        ) and not self.update_runner:
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

        if len(self._duplicate_rules) > 0:
            print("%% DUPLICATE RULES:")
            for rule in self._duplicate_rules:
                print("%% %s" % rule)
            print("")

        if self.update_runner:
            print("%% UPDATE RULES:")
            for rule in sorted(updates):
                print("%% %s" % rule)
            print("")

        if len(self._unimportant_rules) > 0:
            print("%% IRRELEVANT RULES:")
            for rule in self._unimportant_rules:
                print("%% %s" % rule)
            print("")

        static_datalog_atoms = sorted(
            [
                p
                for p in self.predicates_in_ontology
                if not prime_predicate_name(p) in self.predicates
                and not is_coherence_update_predicate_name(p)
            ]
        )
        if len(static_datalog_atoms) > 0:
            print("%% CONCEPTS/RELATIONS NOT DERIVABLE FROM ONTOLOGY:")
            for name in static_datalog_atoms:
                print("%% %s" % name)
            print("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ontology")
    parser.add_argument("domain")
    parser.add_argument("problem")

    parser.add_argument("--rls", default="")
    parser.add_argument("--nmo", default="")
    parser.add_argument("--output-csv", default="results.csv")
    parser.add_argument("--benchmark-name", default="test 1")

    parser.add_argument(
        "--updating-pred-type", default=UPDATING_PREDICATE_TYPES["derived_predicate"]
    )
    parser.add_argument(
        "--incompatible-update-pred-type",
        default=INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"],
    )

    parser.add_argument(
        "--clipper-mqf",
        default=False,
        action="store_true",
        help="Use multiple-query feature of clipper.",
    )
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

    clipper = shutil.which(args.clipper)
    if clipper is None:
        print("clipper was not found.")
        sys.exit(1)
    clipper = Clipper(args.clipper, args.ontology, args.clipper_mqf, args.debug)

    with open(args.domain) as f:
        d = pddl.parse_domain(f.read())
    with open(args.problem) as f:
        p = pddl.parse_problem(f.read())

    with open(args.output_csv, "a") as f:
        f.write(args.benchmark_name + ",")

    do_coherence_update = args.rls != "" and args.nmo != ""
    if do_coherence_update:
        update_runner = UpdateRunner(
            nmo_path=args.nmo,
            rls_file_path=args.rls,
            ontology_file_path=args.ontology,
            timer_output=args.output_csv,
            updating_pred_type=args.updating_pred_type,
            incompatible_update_pred_type=args.incompatible_update_pred_type,
        )
    else:
        update_runner = None

    compiler = Compiler(
        d,
        p,
        clipper,
        filter_unimportant_atoms=not args.no_filter_unimportant,
        expensive_duplicate_filtering=not args.no_expensive_filtering,
        update_runner=update_runner,
        timer_output=args.output_csv,
    )
    compiler()

    d.constants = p.objects
    p.objects = None
    with open(args.out_domain, "w") as f:
        f.write(str(d))
    with open(args.out_problem, "w") as f:
        f.write(str(p))
    if args.verbose:
        compiler.print_compilation_information()
