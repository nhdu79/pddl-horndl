import pddl.datalog as datalog
import pddl.parser as pddl
from coherence_update import HornUpdateRunner, transform_incompatible_update
from compilation.domain_transforms import (
    adjust_actions,
    construct_update_action,
    extend_problem_for_coherence_update,
)
from compilation.naming import (
    INCONSISTENCY_PREDICATE_NAME,
    QUERY_PREDICATE_NAME,
    get_parameter_list,
    is_coherence_update_predicate_name,
    is_non_horn_aux_predicate_name,
    is_primed_predicate_name,
    prime_predicate_name,
    query_predicate_name,
    unprime_predicate_name,
)
from compilation.query_rewriter import prepare_queries
from compilation.ucq_collector import UCQCollector
from utils.helpers import parse_name
from utils.timer import Timer
from variant_options import COMPATIBLE_UPDATE, INCOMPATIBLE_UPDATE

from .datalog import (
    _filter_irrelevant_rules,
    _filter_raw_rules_for_ekab,
    _filter_raw_rules_from_reachable_predicates,
    _parse_datalog_rules,
)


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
        fragment=None,
        variant=None,
        task=None,
        element=None,
        tseitin=None,
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
        self.fragment = fragment
        self.variant = variant
        self.task = task
        self.element = element
        self.tseitin = tseitin

    def __call__(self):
        with Timer(
            "compilation",
            block=True,
            file=self.timer_output,
            fragment=self.fragment,
            variant=self.variant,
            task=self.task,
            element=self.element,
            tseitin=self.tseitin,
        ):
            if self.update_runner:
                self._extend_for_coherence_update()

            self._apply_to_all_conditions(
                pddl.MinimalKnowledgeOperator, self.ucq_collector
            )

            self._queries, unparameterized = prepare_queries(
                self.ucq_collector.ucqs
            )
            raw_rules = self._rewrite_via_clipper(self._queries)

            initial_predicates = self._collect_initial_predicates()

            if self.update_runner:
                update_rules = self.update_runner.run()
                update_rules += self._missing_predicate_rules()
                update_rules, kept = (
                    self.update_runner.filter_non_reachable_predicates(
                        update_rules, self.domain.actions, initial_predicates
                    )
                )
                if kept is not None:
                    raw_rules = _filter_raw_rules_from_reachable_predicates(
                        raw_rules, kept
                    )
                    existing = {p.name for p in self.domain.predicates}
                    for p in kept:
                        if (
                            p.name not in existing
                            and not is_non_horn_aux_predicate_name(p.name)
                        ):
                            self.domain.predicates.append(p)
                construct_update_action(
                    self.domain,
                    self.update_runner.updating_pred_type,
                    self.update_runner.incompatible_update_pred_type,
                    horn=self._is_horn,
                    kept=kept,
                )
                extend_problem_for_coherence_update(self.problem)
                raw_rules += update_rules
            else:
                raw_rules, _ = _filter_raw_rules_for_ekab(
                    raw_rules, self.domain.actions, initial_predicates
                )

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
                == COMPATIBLE_UPDATE
            ):
                self._datalog_rules, compatible_update = (
                    transform_incompatible_update(self._datalog_rules)
                )
                self.domain.derived_predicates.append(compatible_update)
            self._compile_datalog_rules()

            self._unprime_conditions_and_enforce_consistency()

    # -------------------------------------------------------------------------
    # Pipeline steps
    # -------------------------------------------------------------------------

    def _extend_for_coherence_update(self):
        self._is_horn = isinstance(self.update_runner, HornUpdateRunner)
        adjust_actions(
            self.domain, self.update_runner.updating_pred_type, horn=self._is_horn
        )

    def _rewrite_via_clipper(self, queries):
        if self.clipper.supports_simultaneous_rewriting() and queries:
            rules = self.clipper.rewrite_all("\n".join("\n".join(qs) for qs in queries))
        else:
            rules = self.clipper.rewrite_ontology()
            for qs in queries:
                for q in qs:
                    rules.extend(self.clipper.rewrite_cq(q))
        return rules

    def _collect_initial_predicates(self):
        seen: dict = {}
        for fact in self.problem.initial_state:
            if isinstance(fact, pddl.Fact) and fact.predicate not in seen:
                arity = len(fact.parameters)
                params = (
                    [pddl.TypedList([f"?x{i}" for i in range(arity)])]
                    if arity > 0
                    else []
                )
                seen[fact.predicate] = pddl.Predicate(fact.predicate, params)
        return list(seen.values())

    def _missing_predicate_rules(self):
        appeared_in_domain = {
            p.name
            for p in self.domain.predicates
            if not is_coherence_update_predicate_name(p.name)
            and not is_non_horn_aux_predicate_name(p.name)
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
            and self.update_runner.incompatible_update_pred_type == COMPATIBLE_UPDATE
        ):
            assert (
                INCOMPATIBLE_UPDATE not in self.predicates
                and COMPATIBLE_UPDATE in self.predicates
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
                                rule.head.name,
                                [subst[x] for x in rule.head.parameters],
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
