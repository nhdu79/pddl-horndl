import re

from coherence_update.prioritized_update import build_rules_for_pus
from coherence_update.rules.horn.strata import (
    build_actual_deletion_rules_for_concepts,
    build_actual_deletion_rules_for_roles,
    build_actual_insertion_rules_for_concepts,
    build_actual_insertion_rules_for_roles,
    build_connective_rules_for_propagation_role,
    build_connnective_rules_for_deletion_role,
    build_incompatibility_rules_for_direct_deletion_concepts,
    build_incompatibility_rules_for_direct_deletion_roles,
    build_insertion_closure_rule_for_existential,
    build_trigger_rules_for_deletion_concepts,
    build_trigger_rules_for_deletion_roles,
    build_trigger_rules_for_propagation_concepts,
    build_trigger_rules_for_propagation_roles,
    build_updating_rules_for_concepts,
    build_updating_rules_for_roles,
)
from coherence_update.rules.symbols import (
    A_OR_AP_CL,
    ADEL,
    AP_CL,
    APLUS,
    DEL,
    DEL_CL,
    INS,
    INS_CL,
    MIN_X_IN_TAU,
    NOT,
    PRE_INS,
    RULE_SEPARATOR,
)
from coherence_update.runners.base import UpdateRunner
from compilation.variant_options import UPDATING_PREDICATE_TYPES
from owl import (
    OWL_NOTHING,
    OWL_THING,
    AtomicConcept,
    AtomicRole,
    ExistentialConcept,
    FunctionalRole,
    InverseExistentialConcept,
    InverseFunctionalRole,
    InverseRole,
    normalize_negative_concept_inclusions,
    parse_owl,
    saturate_role_inclusions,
)
from planning.logic import Predicate, TypedList
from utils.functions import parse_name

# Compound-predicate prefixes used by the strata rules, ordered longest-first
# so that startswith() checks are unambiguous (no prefix is a prefix of another).
_COMPOUND_PREFIXES = (
    A_OR_AP_CL,  # "AOrApCl_"
    PRE_INS,     # "PreInsCl_"
    INS_CL,      # "InsCl_"
    DEL_CL,      # "DelCl_"
    AP_CL,       # "ApCl_"
    MIN_X_IN_TAU,# "Min_"
    APLUS,       # "Ap_"
    ADEL,        # "Am_"
    INS,         # "ins_"
    DEL,         # "del_"
)


def _normalize_pred_name(name: str) -> str:
    """Apply parse_name to the base of a compound predicate name, preserving the prefix."""
    for prefix in _COMPOUND_PREFIXES:
        if name.startswith(prefix):
            return prefix + parse_name(name[len(prefix):])
    return parse_name(name)


def _predicate_from_rule_head(head_str: str) -> Predicate:
    """Build a Predicate from a Datalog rule head like 'PredName(X,Y)', using canonical ?x0,?x1,... params."""
    paren = head_str.find("(")
    if paren < 0:
        return Predicate(head_str.strip(), [])
    name = head_str[:paren].strip()
    params_str = head_str[paren + 1:].rstrip(")").strip()
    if not params_str:
        return Predicate(name, [])
    arity = len(params_str.split(","))
    return Predicate(name, [TypedList([f"?x{i}" for i in range(arity)])])


def _predicate_from_tail_atom(atom_name: str, tail: str) -> Predicate:
    """Build a Predicate for atom_name by locating its parameter list in the tail string."""
    match = re.search(rf"\b{re.escape(atom_name)}\(([^)]*)\)", tail)
    if match:
        params_str = match.group(1).strip()
        if not params_str:
            return Predicate(atom_name, [])
        arity = len(params_str.split(","))
        return Predicate(atom_name, [TypedList([f"?x{i}" for i in range(arity)])])
    return Predicate(atom_name, [TypedList(["?x0"])])


def _collect_effect_predicates(effect, result: dict) -> None:
    """Recursively collect all Fact predicates from an effect tree as Predicate objects."""
    from planning.logic import AddEffect, ConjunctiveEffect, ConditionalEffect, DelEffect, ForallEffect
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


class HornUpdateRunner(UpdateRunner):
    """DL-Lite Horn: TBox built directly from the OWL ontology via the Python parser."""

    def __init__(self, ontology_file_path, **kwargs):
        super().__init__(**kwargs)
        self.ontology = parse_owl(ontology_file_path)
        saturate_role_inclusions(self.ontology)
        normalize_negative_concept_inclusions(self.ontology)

    def run(self):
        include_updating = (
            self.updating_pred_type == UPDATING_PREDICATE_TYPES["derived_predicate"]
        )
        return build_rules_for_pus(
            self.ontology, include_updating_rules=include_updating
        )

    def run_for_missing_predicates(self, missing_concepts, missing_roles):
        # Wrap plain names as expression objects so the strata functions can use them.
        atomic_role_objs = [AtomicRole(name) for name in missing_roles]
        inv_role_objs = [InverseRole(r) for r in atomic_role_objs]
        all_role_objs = atomic_role_objs + inv_role_objs

        concept_objs = [AtomicConcept(name) for name in missing_concepts]
        ex_concept_objs = [ExistentialConcept(r) for r in atomic_role_objs]
        inv_ex_concept_objs = [InverseExistentialConcept(r) for r in atomic_role_objs]
        all_concept_objs = concept_objs + ex_concept_objs + inv_ex_concept_objs

        rules = []
        # Stratum 1 — trigger propagation (rules 1-3; rule 4 skipped: no TBox)
        rules.extend(build_trigger_rules_for_propagation_concepts(all_concept_objs))
        rules.extend(build_trigger_rules_for_propagation_roles(all_role_objs))
        for role in all_role_objs:
            rules.extend(build_connective_rules_for_propagation_role(role))
        # Stratum 2 — deletion closure (rules 5-7, 16-17; rules 8-15 skipped: no TBox)
        rules.extend(build_trigger_rules_for_deletion_concepts(all_concept_objs))
        rules.extend(build_trigger_rules_for_deletion_roles(all_role_objs))
        for role in all_role_objs:
            rules.extend(build_connnective_rules_for_deletion_role(role))
        rules.extend(
            build_incompatibility_rules_for_direct_deletion_concepts(all_concept_objs)
        )
        rules.extend(
            build_incompatibility_rules_for_direct_deletion_roles(all_role_objs)
        )
        rules.extend(build_actual_deletion_rules_for_concepts(all_concept_objs))
        rules.extend(build_actual_deletion_rules_for_roles(all_role_objs))
        # Stratum 3 — insertion closure (rules 20-22; rules 18-19 skipped: no TBox)
        for role in all_role_objs:
            rules.extend(build_insertion_closure_rule_for_existential(role))
        rules.extend(build_actual_insertion_rules_for_concepts(all_concept_objs))
        rules.extend(build_actual_insertion_rules_for_roles(all_role_objs))
        # Updating trigger — only when updating() is a derived predicate
        if self.updating_pred_type == UPDATING_PREDICATE_TYPES["derived_predicate"]:
            rules.extend(build_updating_rules_for_concepts(all_concept_objs))
            rules.extend(build_updating_rules_for_roles(all_role_objs))
        return rules

    def atomic_predicates(self) -> set:
        concepts = set(self.ontology.atomic_concepts.keys())
        roles = set(self.ontology.atomic_roles.keys())
        functs = {
            ax.role.id for ax in self.ontology.axioms if isinstance(ax, FunctionalRole)
        }
        inv_functs = {
            ax.role.id
            for ax in self.ontology.axioms
            if isinstance(ax, InverseFunctionalRole)
        }
        return concepts | roles | functs | inv_functs

    def predicates_for_domain(self, pddl_predicates):
        pddl_names = {p.name for p in pddl_predicates}
        extra = []
        for c in self.ontology.atomic_concepts.values():
            if c not in (OWL_THING, OWL_NOTHING) and c.id not in pddl_names:
                extra.append(Predicate(c.id, [TypedList(["?x0"])]))
        for r in self.ontology.atomic_roles.values():
            if r.id not in pddl_names:
                extra.append(Predicate(r.id, [TypedList(["?x0", "?x1"])]))
        return list(pddl_predicates) + extra

    def filter_non_reachable_predicates(
        self, rules: list, actions: list, initial_predicates=None
    ) -> tuple:
        # Collect seeds: Ap_* and Am_* predicates set by action effects as Predicate
        # objects, excluding the UPDATE action whose effects are not part of the
        # original planning model.
        seed_predicates: dict = {}
        for action in actions:
            _collect_effect_predicates(action.effect, seed_predicates)

        # Normalize all seed names so they agree with the expression IDs used in
        # rule strings (prefix preserved, base part run through parse_name).
        kept_predicates: dict = {
            _normalize_pred_name(k): Predicate(_normalize_pred_name(k), v.parameters)
            for k, v in seed_predicates.items()
        }

        # Seed from initial state facts: predicates that hold in the initial state
        # may appear in ontology rule bodies, so they must be reachable.
        if initial_predicates:
            for pred in initial_predicates:
                name = _normalize_pred_name(pred.name)
                kept_predicates.setdefault(name, Predicate(name, pred.parameters))

        # Strip Ap_/Am_ to recover base predicate names with the same arity so
        # that rule 1 (AOrApCl_X :- X) is reachable alongside rule 2 (AOrApCl_X :- Ap_X).
        for name, pred in list(kept_predicates.items()):
            if name.startswith(APLUS):
                base = parse_name(name[len(APLUS):])
                kept_predicates[base] = Predicate(base, pred.parameters)
            elif name.startswith(ADEL):
                base = parse_name(name[len(ADEL):])
                kept_predicates.setdefault(base, Predicate(base, pred.parameters))

        # Reachability fixpoint: fire rules whose positive body atoms are all already
        # in kept_predicates, adding the head and any negated body atoms as new
        # Predicate objects.  kept_predicates serves as both the name-reachability set
        # (dict key lookup) and the Predicate accumulator — no separate string set needed.
        kept_rules = []
        remaining = list(rules)
        while True:
            new_predicates: dict = {}
            new_remaining = []
            for rule_str in remaining:
                sep_idx = rule_str.find(RULE_SEPARATOR)
                if sep_idx < 0:
                    new_remaining.append(rule_str)
                    continue
                tail = rule_str[sep_idx + len(RULE_SEPARATOR):]
                atoms = re.findall(
                    rf"({re.escape(NOT)}?)([A-Za-z][A-Za-z0-9_]*)\(", tail
                )
                positive_names = {
                    _normalize_pred_name(n) for neg, n in atoms if not neg
                }
                if positive_names and positive_names.issubset(kept_predicates):
                    kept_rules.append(rule_str)
                    raw_head = _predicate_from_rule_head(rule_str[:sep_idx].strip())
                    head_name = _normalize_pred_name(raw_head.name)
                    head_pred = Predicate(head_name, raw_head.parameters)
                    new_predicates[head_name] = head_pred
                    # ins_X / del_X reachability implies X itself is also needed.
                    if head_name.startswith(INS):
                        base = parse_name(head_name[len(INS):])
                        new_predicates.setdefault(
                            base, Predicate(base, head_pred.parameters)
                        )
                    elif head_name.startswith(DEL):
                        base = parse_name(head_name[len(DEL):])
                        new_predicates.setdefault(
                            base, Predicate(base, head_pred.parameters)
                        )
                    # Negated body atoms must also be declared in the domain.
                    for neg, neg_name in atoms:
                        if neg:
                            norm_neg = _normalize_pred_name(neg_name)
                            if norm_neg not in kept_predicates:
                                new_predicates[norm_neg] = _predicate_from_tail_atom(
                                    norm_neg, tail
                                )
                else:
                    new_remaining.append(rule_str)
            newly_added = set(new_predicates) - set(kept_predicates)
            if not newly_added:
                break
            kept_predicates.update(new_predicates)
            remaining = new_remaining

        return kept_rules, list(kept_predicates.values())
