import re

import pddl.datalog as datalog
from compilation.naming import (
    INCONSISTENCY_PREDICATE_NAME,
    encodes_inconsistency,
    get_query_id,
    is_coherence_update_predicate_name,
    is_update_predicate_name,
    query_predicate_name,
)
from pddl.logic import Predicate, TypedList
from utils.helpers import parse_name


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


def _filter_raw_rules_from_reachable_predicates(raw_rules, reachable_predicates):
    """Filter raw Datalog rule strings, keeping only those whose every positive
    body atom is present in reachable_predicates.

    raw_rules: list of rule strings (Clipper output or strata rules)
    reachable_predicates: iterable of Predicate objects
    Returns: filtered list of rule strings
    """
    reachable_names = {p.name for p in reachable_predicates}
    filtered = []
    for rule_str in raw_rules:
        sep_idx = rule_str.find(" :- ")
        if sep_idx < 0:
            filtered.append(rule_str)  # fact with no body — always keep
            continue
        tail = rule_str[sep_idx + len(" :- ") :]
        # Atom pattern: optional leading '-' for negation, then identifier, then '('.
        atoms = re.findall(r"(-?)([A-Za-z][A-Za-z0-9_]*)\(", tail)
        positive_names = {name for neg, name in atoms if not neg}
        if not positive_names or positive_names.issubset(reachable_names):
            filtered.append(rule_str)
    return filtered


def _predicate_from_rule_head(head_str: str) -> Predicate:
    """Build a Predicate from a Datalog rule head string like 'PredName(X,Y)'."""
    paren = head_str.find("(")
    if paren < 0:
        return Predicate(head_str.strip(), [])
    name = head_str[:paren].strip()
    params_str = head_str[paren + 1 :].rstrip(")").strip()
    if not params_str:
        return Predicate(name, [])
    arity = len(params_str.split(","))
    return Predicate(name, [TypedList([f"?x{i}" for i in range(arity)])])


def _collect_effect_predicates(effect, result: dict) -> None:
    """Recursively collect all Fact predicates from an effect tree as Predicate objects."""
    from pddl.logic import (
        AddEffect,
        ConditionalEffect,
        ConjunctiveEffect,
        DelEffect,
        ForallEffect,
    )

    if isinstance(effect, (AddEffect, DelEffect)):
        fact = effect.fact
        if fact.predicate not in result:
            arity = len(fact.parameters)
            params = [TypedList([f"?x{i}" for i in range(arity)])] if arity > 0 else []
            result[fact.predicate] = Predicate(fact.predicate, params)
    elif isinstance(effect, ConjunctiveEffect):
        for e in effect.elements:
            _collect_effect_predicates(e, result)
    elif isinstance(effect, (ConditionalEffect, ForallEffect)):
        _collect_effect_predicates(effect.effect, result)


def _filter_raw_rules_for_ekab(raw_rules, actions=None, initial_predicates=None):
    """Filter Clipper rules for the eKAB formalism (no UpdateRunner).

    Seeds reachability from action effects and initial_predicates, then
    propagates through raw_rules via fixpoint: a rule is reachable when all
    its positive body atoms are already reachable.

    Returns (filtered_rules, kept_predicates) where kept_predicates is a list of
    Predicate objects covering all reachable names.
    """
    kept_predicates: dict = {}
    for action in actions or []:
        effect_preds: dict = {}
        _collect_effect_predicates(action.effect, effect_preds)
        for name, pred in effect_preds.items():
            norm = parse_name(name)
            kept_predicates.setdefault(norm, Predicate(norm, pred.parameters))
    for pred in initial_predicates or []:
        name = parse_name(pred.name)
        kept_predicates.setdefault(name, Predicate(name, pred.parameters))

    kept_rules = []
    remaining = list(raw_rules)
    while True:
        new_predicates: dict = {}
        new_remaining = []
        for rule_str in remaining:
            sep_idx = rule_str.find(" :- ")
            if sep_idx < 0:
                kept_rules.append(rule_str)
                continue
            tail = rule_str[sep_idx + len(" :- ") :]
            atoms = re.findall(r"(-?)([A-Za-z][A-Za-z0-9_]*)\(", tail)
            positive_names = {parse_name(n) for neg, n in atoms if not neg}
            if not positive_names or positive_names.issubset(kept_predicates):
                kept_rules.append(rule_str)
                raw_head = _predicate_from_rule_head(rule_str[:sep_idx].strip())
                head_name = parse_name(raw_head.name)
                new_predicates[head_name] = Predicate(head_name, raw_head.parameters)
            else:
                new_remaining.append(rule_str)
        newly_added = set(new_predicates) - set(kept_predicates)
        if not newly_added:
            break
        kept_predicates.update(new_predicates)
        remaining = new_remaining

    # if len(raw_rules) - len(kept_rules) > 0:
    #     print(f"Filtered {len(raw_rules) - len(kept_rules)} unreachable rules.")
    #     print(f"Kept {len(kept_predicates)} reachable predicates.")
    return kept_rules, list(kept_predicates.values())


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
