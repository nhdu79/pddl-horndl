#!/usr/bin/env python

import argparse
import sys
import pddl
import datalog
import shutil

from clipper import Clipper
from update_runner import UpdateRunner, Timer

QUERY_PREDICATE_NAME = "QUERY"

def is_primed_predicate_name(name):
    return name.startswith("DATALOG_")

def prime_predicate_name(original):
    return "DATALOG_%s" % original.upper()

def unprime_predicate_name(primed_name):
    if primed_name.startswith("DATALOG_"):
        return primed_name[8:].lower()
    return primed_name

def query_predicate_name(idx):
    return QUERY_PREDICATE_NAME + str(idx)

def get_query_id(name):
    if name.lower().startswith(QUERY_PREDICATE_NAME.lower()):
        return int(name[len(QUERY_PREDICATE_NAME):])
    return None

def get_parameter_list(length, var_name="?x%d"):
    if length == 0:
        return []
    else:
        return [pddl.TypedList([var_name % j for j in range(length)])]

def pddl_predicate(name, num_parameters, primed=False):
    return pddl.Predicate(
            prime_predicate_name(name) if primed else name,
            get_parameter_list(num_parameters))


INCONSISTENCY_PREDICATE_NAME = "inconsistent"


def encodes_inconsistency(head):
    return isinstance(head, datalog.Falsity) or head.name == 'nothing'


class UCQCollector:
    def __init__(self, clipper):
        self.ucqs = []
        self.equality = False
        self.queried_predicates = set()
        self.clipper = clipper

    def __call__(self, mko):
        s = pddl.Substitution()
        ucq = mko.ucq.simplified_ucq(s)
        if isinstance(ucq, pddl.Comparison):
            assert False
        elif isinstance(ucq, pddl.Fact):
            p = self.clipper.adapt_predicate_name(ucq.predicate)
            self.queried_predicates.add(p)
            return pddl.Fact(
                    prime_predicate_name(p),
                    ucq.parameters)
        else:
            self.ucqs.append(ucq)
            return pddl.Fact(
                    prime_predicate_name(query_predicate_name(len(self.ucqs)-1)),
                    list(sorted(ucq.free_vars())))


class Compilation:
    def __init__(self,
                 domain,
                 problem,
                 clipper,
                 filter_duplicates = True,
                 filter_unimportant_atoms = True,
                 expensive_duplicate_filtering = False,
                 update_runner = None):
        self.domain = domain
        self.problem = problem
        self.clipper = clipper
        self.ucq_collector = UCQCollector(clipper)
        self.filter_unimportant_atoms = filter_unimportant_atoms
        self.filter_duplicates = filter_duplicates
        self.expensive_duplicate_filtering = expensive_duplicate_filtering
        self.update_runner = update_runner

    def __call__(self):
        with Timer("Compilation", block=True):
            with Timer("Collecting queries"):
                self._collect_and_replace_ucqs()
            with Timer("Rewriting"):
                self._prepare_queries_for_rewriting()
                self._rewrite_ontology_and_ucqs()
            if self.update_runner:
                with Timer("Constructing and adding coherence update rules"):
                    self._add_update_rules()
            with Timer("Generating derived predicated from datalog rules"):
                self._adapt_predicate_names_to_clipper()
                self._collect_predicate_information()
                self._create_datalog_rule_objects()
                if self.filter_unimportant_atoms:
                    self._drop_irrelevant_datalog_rules()
                self._compile_datalog_rules()
            with Timer("Finalizing PDDL"):
                self._unprime_conditions_and_enforce_consistency()
        print("")

    def _apply_to_all_conditions(self, typ, fn):
        def ce_wrapper(eff):
            new_cond = eff.condition.apply(typ, fn)
            new_eff = eff.effect.apply(pddl.ConditionalEffect, ce_wrapper)
            return pddl.ConditionalEffect(new_cond, new_eff)
        for i, deriv in enumerate(self.domain.derived_predicates):
            deriv.condition = deriv.condition.apply(typ, fn)
        for action in self.domain.actions:
            action.precondition = action.precondition.apply(typ, fn)
            action.effect = action.effect.apply(
                    pddl.ConditionalEffect,
                    ce_wrapper)
        self.problem.goal = self.problem.goal.apply(typ, fn)

    def _apply_to_all_effects(self, typ, fn):
        for action in self.domain.actions:
            action.effect = action.effect.apply(typ, fn)

    def _collect_predicate_information(self):
        self.predicates = set([ p.name for p in self.domain.predicates ])
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
        head = query_predicate_name(query_id) + "(" + (",".join([var_map[x] for x in free_vars]) if has_free_vars else "?0") + ")"
        tail = [ f.predicate + "(" + ",".join([var_map.get(t, t) for t in f.parameters]) + ")" for f in elements ]
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
            rewritten_rules = self.clipper.rewrite_all("\n".join(["\n".join(qs) for qs in self._queries]))
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

    def _adapt_predicate_names_to_clipper(self):
        for p in self.domain.predicates:
            p.name = self.clipper.adapt_predicate_name(p.name)
        def apply_to_fact(fact):
            if is_primed_predicate_name(fact.predicate):
                return fact
            return pddl.Fact(self.clipper.adapt_predicate_name(fact.predicate), fact.parameters)
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
        for idx, s in enumerate(datalog_rules):
            if len(s.strip()) == 0:
                continue
            rule = datalog.parse_rule(s)
            if encodes_inconsistency(rule.head):
                rule.head = inconsistent_atom
            if self.expensive_duplicate_filtering:
                rule = rule.canonical()
            query_id = get_query_id(rule.head.name)
            if query_id != None and query_id in self._unparameterized_queries:
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
        necessary_predicates = self.ucq_collector.queried_predicates \
            | set([INCONSISTENCY_PREDICATE_NAME]) \
            | set([query_predicate_name(i) for i in range(len(self.ucq_collector.ucqs))])
        conditioned_predicates = necessary_predicates
        for rule in self._datalog_rules:
            for t in rule.tail:
                if isinstance(t, datalog.Negated):
                    t = t.element
                if isinstance(t, datalog.Atom):
                    conditioned_predicates.add(t.name)
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
            primed_predicate_name = prime_predicate_name(rule.head.name)
            predicate = pddl.Predicate(
                    primed_predicate_name,
                    [pddl.TypedList([subst[x] for x in rule.head.parameters])])
            if not primed_predicate_name in self.predicates:
                self.domain.predicates.append(predicate)
                self.predicates.add(primed_predicate_name)
                if rule.head.name in self.predicates \
                        and not rule.head.name.startswith(QUERY_PREDICATE_NAME) \
                        and rule.head.name != INCONSISTENCY_PREDICATE_NAME:
                    self.domain.derived_predicates.append(pddl.DerivedPredicate(
                        predicate,
                        pddl.Fact(rule.head.name, [subst[x] for x in rule.head.parameters])))
            self.predicates_in_ontology.add(rule.head.name)

            cond = []
            for t in rule.tail:
                neg = False
                if isinstance(t, datalog.Negated):
                    neg = True
                    t = t.element
                if isinstance(t, datalog.Atom):
                    cond.append(pddl.Fact(
                        prime_predicate_name(t.name),
                        [ subst[x] for x in t.parameters ]))
                    self.predicates_in_ontology.add(t.name)
                else:
                    # TODO correct?
                    cond.append(pddl.Comparison(
                        '=',
                        pddl.SimpleFExpression(subst[t.left]),
                        pddl.SimpleFExpression(subst[t.right])))
                if neg:
                    cond[-1] = pddl.Not(cond[-1])
            cond = pddl.And(cond)
            if num_ext > 0:
                cond = pddl.Exists(
                        get_parameter_list(num_ext, "?y%d"),
                        cond)
            self.domain.derived_predicates.append(pddl.DerivedPredicate(predicate, cond))

    def _unprime_conditions_and_enforce_consistency(self):
        def unprimer(fact):
            if not fact.predicate in self.predicates:
                assert is_primed_predicate_name(fact.predicate), "%s does not appear in predicates" % fact.predicate
                unprimed = unprime_predicate_name(fact.predicate)
                if unprimed.startswith(QUERY_PREDICATE_NAME.lower()):
                    return pddl.Falsity()
                return pddl.Fact(unprimed, fact.parameters)
            return fact
        self._apply_to_all_conditions(pddl.Fact, unprimer)
        if (prime_predicate_name(INCONSISTENCY_PREDICATE_NAME) in self.predicates):
            is_consistent = pddl.Not(pddl.Fact(prime_predicate_name(INCONSISTENCY_PREDICATE_NAME), []))
            for action in self.domain.actions:
                action.precondition = pddl.And([is_consistent, action.precondition]).simplified()
            self.problem.goal = pddl.And([is_consistent, self.problem.goal]).simplified()
        else:
            for action in self.domain.actions:
                action.precondition = pddl.And([action.precondition]).simplified()
            self.problem.goal = pddl.And([self.problem.goal]).simplified()

    def print_compilation_information(self):
        ontology = []
        queries =  []
        for rule in self._datalog_rules:
            if rule.head.name.startswith(QUERY_PREDICATE_NAME):
                queries.append(rule)
            else:
                ontology.append(rule)
        print("%% ONTOLOGY")
        for rule in sorted(ontology):
            print(rule)
        queries = list(sorted(queries))
        i = 0
        for (j, qs) in enumerate(self._queries):
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

        if len(self._unimportant_rules) > 0:
            print("%% IRRELEVANT RULES:")
            for rule in self._unimportant_rules:
                print("%% %s" % rule)
            print("")

        static_datalog_atoms = sorted([p for p in self.predicates_in_ontology
            if not prime_predicate_name(p) in self.predicates])
        if len(static_datalog_atoms) > 0:
            print("%% CONCEPTS/RELATIONS NOT DERIVABLE FROM ONTOLOGY:")
            for name in static_datalog_atoms:
                print("%% %s" % name)
            print("")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("ontology")
    p.add_argument("domain")
    p.add_argument("problem")

    p.add_argument("--rls", default="t_closure.rls")
    p.add_argument("--nmo", default="nmo")

    p.add_argument("--clipper-mqf", default=False, action="store_true", help="Use multiple-query feature of clipper.")
    p.add_argument("--clipper", default="clipper.sh")
    p.add_argument("--out-domain", "-d", default="domain.pddl")
    p.add_argument("--out-problem", "-p", default="problem.pddl")
    p.add_argument("--verbose", "-v", default=False, action='store_true')
    p.add_argument("--no-filter-unimportant", default=False, action="store_true")
    p.add_argument("--no-expensive-filtering", default=False, action="store_true")
    p.add_argument("--debug", default=False, action="store_true")
    args = p.parse_args()
    clipper = shutil.which(args.clipper)
    if clipper is None:
        print("clipper was not found.")
        sys.exit(1)
    clipper = Clipper(clipper, args.ontology, args.clipper_mqf, args.debug)

    with open(args.domain) as f:
        d = pddl.parse_domain(f.read())
    with open(args.problem) as f:
        p = pddl.parse_problem(f.read())

    do_coherence_update = args.rls and args.nmo
    if do_coherence_update:
        update_runner = UpdateRunner(nmo_path=args.nmo, rls_file_path=args.rls, ontology_file_path=args.ontology)
        d.extend_for_coherence_update()
        p.extend_for_coherence_update()
    else:
        update_runner = None

    compilation = Compilation(d, p, clipper, filter_unimportant_atoms = not args.no_filter_unimportant, expensive_duplicate_filtering = not args.no_expensive_filtering, update_runner=update_runner)
    compilation()
    d.constants = p.objects
    p.objects = None
    with open(args.out_domain, "w") as f:
        f.write(str(d))
    with open(args.out_problem, "w") as f:
        f.write(str(p))
    if args.verbose:
        compilation.print_compilation_information()