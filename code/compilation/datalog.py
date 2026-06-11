import re

import planning.datalog as datalog
from compilation.utils import (
    INCONSISTENCY_PREDICATE_NAME,
    encodes_inconsistency,
    get_query_id,
    is_coherence_update_predicate_name,
    is_update_predicate_name,
    query_predicate_name,
)


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
        tail = rule_str[sep_idx + len(" :- "):]
        # Atom pattern: optional leading '-' for negation, then identifier, then '('.
        atoms = re.findall(r"(-?)([A-Za-z][A-Za-z0-9_]*)\(", tail)
        positive_names = {name for neg, name in atoms if not neg}
        if not positive_names or positive_names.issubset(reachable_names):
            filtered.append(rule_str)
    return filtered

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
