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


def _parse_datalog_rules(
    raw_rules, unparameterized, update_runner, filter_duplicates, expensive
):
    """Parse raw Datalog strings into rule objects, deduplicating if requested.

    Returns (rules, duplicate_rules).
    """
    # A dict (not a set) deduplicates while keeping Clipper's rule order, so
    # the compiled output does not depend on string hash randomisation.
    unique = {}
    ordered = []
    duplicates = []
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
            if rule in unique:
                duplicates.append(rule)
                continue
            unique[rule] = None
        ordered.append(rule)

    return ordered, duplicates


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
            kept_predicates.setdefault(name, pred)
    for pred in initial_predicates or []:
        kept_predicates.setdefault(pred.name, pred)

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
            positive_names = {n for neg, n in atoms if not neg}
            if not positive_names or positive_names.issubset(kept_predicates):
                kept_rules.append(rule_str)
                head = _predicate_from_rule_head(rule_str[:sep_idx].strip())
                new_predicates[head.name] = head
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


def _body_atom_names(rule):
    for t in rule.tail:
        if isinstance(t, datalog.Negated):
            t = t.element
        if isinstance(t, datalog.Atom):
            yield t.name


def _filter_irrelevant_rules(rules, queried_predicates, num_ucqs, update_runner):
    """Remove Datalog rules whose heads cannot contribute to any queried predicate.

    Backward reachability from the predicates the compiled task actually reads:
    the queried atoms, the QUERY_i heads and (without an update runner) the
    inconsistency atom.  A rule is relevant iff its head is needed; the body
    atoms of relevant rules become needed in turn.

    Coherence-update rules are always kept.  Their bodies refer to the ABox
    predicates themselves (compiled unprimed), not to the ontology-derived
    primed predicates, so they do not make any ontology rule relevant.

    Returns (relevant_rules, irrelevant_rules), both in input order.
    """

    def is_update_rule(rule):
        return update_runner is not None and is_coherence_update_predicate_name(
            rule.head.name
        )

    needed = set(queried_predicates)
    needed |= {query_predicate_name(i) for i in range(num_ucqs)}
    if not update_runner:
        needed.add(INCONSISTENCY_PREDICATE_NAME)

    ontology_rules = [r for r in rules if not is_update_rule(r)]
    changed = True
    while changed:
        changed = False
        for rule in ontology_rules:
            if rule.head.name not in needed:
                continue
            for name in _body_atom_names(rule):
                if name not in needed:
                    needed.add(name)
                    changed = True

    relevant, irrelevant = [], []
    for rule in rules:
        if is_update_rule(rule) or rule.head.name in needed:
            relevant.append(rule)
        else:
            irrelevant.append(rule)
    return relevant, irrelevant
