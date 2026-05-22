from __future__ import annotations

from coherence_update.rules.horn.strata import (
    build_actual_deletion_rules_for_concepts,
    build_actual_deletion_rules_for_roles,
    build_actual_insertion_rules_for_concepts,
    build_actual_insertion_rules_for_roles,
    build_connective_rules_for_propagation_role,
    build_connnective_rules_for_deletion_role,
    build_deletion_rules_for_negative_role_inclusion,
    build_incompatibility_rule_for_conjunction_concept_with_bottom,
    build_incompatibility_rules_for_direct_deletion_concepts,
    build_incompatibility_rules_for_direct_deletion_roles,
    build_insertion_closure_rule_for_existential,
    build_insertion_closure_rules_for_conjunction_concept,
    build_insertion_closure_rules_for_role,
    build_min_and_deletion_rules_for_conjunction_concept,
    build_min_and_deletion_rules_for_role,
    build_pre_insertion_rules_for_conjunction_concept,
    build_pre_insertion_rules_for_role,
    build_propagation_rules_for_concept,
    build_propagation_rules_for_role,
    build_rules_for_functional_roles,
    build_trigger_rules_for_deletion_concepts,
    build_trigger_rules_for_deletion_roles,
    build_trigger_rules_for_propagation_concepts,
    build_trigger_rules_for_propagation_roles,
    build_updating_rules_for_concepts,
    build_updating_rules_for_roles,
)
from owl import (
    OWL_NOTHING,
    OWL_THING,
    AtomicConcept,
    AtomicRole,
    ConceptInclusion,
    ExistentialConcept,
    FunctionalRole,
    IntersectionConcept,
    InverseExistentialConcept,
    InverseFunctionalRole,
    InverseRole,
    NegatedRole,
    Ontology,
    RoleInclusion,
)


def _positive_concepts(on: Ontology) -> list:
    """All positive concept expression objects (atomic excl. ⊤/⊥, existential, inv-existential)."""
    result = []
    for c in on.concepts.values():
        if isinstance(c, AtomicConcept) and c not in (OWL_THING, OWL_NOTHING):
            result.append(c)
        elif isinstance(c, (ExistentialConcept, InverseExistentialConcept)):
            result.append(c)
    return result


def _positive_roles(on: Ontology) -> list:
    """All AtomicRole and InverseRole objects registered in the ontology."""
    return [r for r in on.roles.values() if isinstance(r, (AtomicRole, InverseRole))]


def _sub_concepts(sub) -> list:
    """Extract sub-concept expression objects from the sub side of a ConceptInclusion."""
    if isinstance(sub, IntersectionConcept):
        return list(sub.operands)
    return [sub]


def _is_valid_ontology_for_pus(on: Ontology) -> bool:
    for ax in on.axioms:
        if isinstance(ax, ConceptInclusion):
            if ax.sup == OWL_NOTHING and _sub_concepts(ax.sub) == 1:
                return False

    return True


def build_rules_for_pus(on: Ontology) -> list[str]:
    """
    Build the complete stratified Datalog⁻ program R_T (22 rules across 3 strata)
    for Horn DL-Lite prioritized ABox update.

    The ontology must already be saturated via saturate_role_inclusions()
    and normalize_negative_concept_inclusions before calling this function
    so that T* is fully reflected in on.axioms.
    """
    if not _is_valid_ontology_for_pus(on):
        raise ValueError(
            "Ontology contains inclusions B ⊑ ⊥. Remove all such axioms before building rules for prioritized update."
        )

    rules: list[str] = []

    concepts = _positive_concepts(on)
    roles = _positive_roles(on)

    # -----------------------------------------------------------------------
    # Stratum 1 — Propagation closure
    # -----------------------------------------------------------------------

    # Rules 1-2: AOrApCl_X(Ȳ) ← X(Ȳ) / ApCl_X(Ȳ) ← Ap_X(Ȳ)
    rules.extend(build_trigger_rules_for_propagation_concepts(concepts))
    rules.extend(build_trigger_rules_for_propagation_roles(roles))

    # Rule 3: pred_R⁻(Y,X) ← pred_R(X,Y) / pred_∃R(X) ← pred_R(X,Y)
    # Generated for every role (AtomicRole and InverseRole) so both directions
    # of each role pair are covered.
    for role in roles:
        rules.extend(build_connective_rules_for_propagation_role(role))

    # Rule 4: pred_X(Ȳ) ← pred_X1(Ȳ) ∧ … ∧ pred_Xk(Ȳ)
    for ax in on.axioms:
        if isinstance(ax, ConceptInclusion):
            if ax.sup == OWL_NOTHING:
                continue
            rules.extend(
                build_propagation_rules_for_concept(_sub_concepts(ax.sub), ax.sup)
            )
        elif isinstance(ax, RoleInclusion) and not isinstance(ax.sup, NegatedRole):
            rules.extend(build_propagation_rules_for_role(ax.sub, ax.sup))

    # -----------------------------------------------------------------------
    # Stratum 2 — Deletion closure
    # -----------------------------------------------------------------------

    # Rule 5: DelCl_X(Ȳ) ← Am_X(Ȳ)
    rules.extend(build_trigger_rules_for_deletion_concepts(concepts))
    rules.extend(build_trigger_rules_for_deletion_roles(roles))

    # Rules 6-7: DelCl_R⁻(Y,X) ← DelCl_R(X,Y) / DelCl_R(X,Y) ← AOrApCl_R(X,Y) ∧ DelCl_∃R(X)
    for role in roles:
        rules.extend(build_connnective_rules_for_deletion_role(role))

    # Rules 8-9: functional role conflict detection
    func_roles = []
    for ax in on.axioms:
        if isinstance(ax, FunctionalRole):
            func_roles.append(ax.role)
        elif isinstance(ax, InverseFunctionalRole):
            func_roles.append(InverseRole(ax.role))
    rules.extend(build_rules_for_functional_roles(func_roles))

    # Rules 10-12: R ⊑ ¬R' — negative role inclusion conflicts
    for ax in on.axioms:
        if isinstance(ax, RoleInclusion) and isinstance(ax.sup, NegatedRole):
            rules.extend(
                build_deletion_rules_for_negative_role_inclusion(
                    ax.sub,
                    ax.sup.role,  # ax.sup.role: inner AtomicRole | InverseRole of ¬R'
                )
            )

    # Rules 13-14: Min predicate + DelCl propagation for positive inclusions
    for ax in on.axioms:
        if isinstance(ax, ConceptInclusion):
            if ax.sup == OWL_NOTHING:
                # TODO(dnh): Extend!
                continue
            rules.extend(
                build_min_and_deletion_rules_for_conjunction_concept(
                    _sub_concepts(ax.sub), ax.sup, ax.id
                )
            )
        elif isinstance(ax, RoleInclusion) and not isinstance(ax.sup, NegatedRole):
            rules.extend(build_min_and_deletion_rules_for_role(ax.sub, ax.sup, ax.id))

    # Rule 15: incompatible() for B1 ⊓ … ⊓ Bk ⊑ ⊥
    for ax in on.axioms:
        if isinstance(ax, ConceptInclusion) and ax.sup == OWL_NOTHING:
            rules.extend(
                build_incompatibility_rule_for_conjunction_concept_with_bottom(
                    _sub_concepts(ax.sub)
                )
            )

    # Rule 16: incompatible() for direct deletion/insertion clash
    rules.extend(build_incompatibility_rules_for_direct_deletion_concepts(concepts))
    rules.extend(build_incompatibility_rules_for_direct_deletion_roles(roles))

    # Rule 17: del_X(Ȳ) ← X(Ȳ) ∧ DelCl_X(Ȳ)
    rules.extend(build_actual_deletion_rules_for_concepts(concepts))
    rules.extend(build_actual_deletion_rules_for_roles(roles))

    # -----------------------------------------------------------------------
    # Stratum 3 — Insertion closure
    # -----------------------------------------------------------------------

    # Rules 18-19: preInsCl_τ and insCl_X for positive inclusions
    for ax in on.axioms:
        if isinstance(ax, ConceptInclusion):
            if ax.sup == OWL_NOTHING:
                # TODO(dnh): Extend!
                continue
            sub_cs = _sub_concepts(ax.sub)
            rules.extend(
                build_pre_insertion_rules_for_conjunction_concept(sub_cs, ax.sup, ax.id)
            )
            rules.extend(
                build_insertion_closure_rules_for_conjunction_concept(
                    sub_cs, ax.sup, ax.id
                )
            )
        elif isinstance(ax, RoleInclusion) and not isinstance(ax.sup, NegatedRole):
            rules.extend(build_pre_insertion_rules_for_role(ax.sub, ax.sup, ax.id))
            rules.extend(build_insertion_closure_rules_for_role(ax.sub, ax.sup, ax.id))

    # Rule 20: insCl_∃R(X) ← DelCl_R(X,Y) ∧ AOrApCl_R(X,Y) ∧ ¬DelCl_∃R(X)
    for role in roles:
        rules.extend(build_insertion_closure_rule_for_existential(role))

    # Rules 21-22: ins_X(Ȳ) ← ¬X(Ȳ) ∧ insCl_X(Ȳ) / ← ¬X(Ȳ) ∧ Ap_X(Ȳ)
    rules.extend(build_actual_insertion_rules_for_concepts(concepts))
    rules.extend(build_actual_insertion_rules_for_roles(roles))

    # Updating trigger: updating() ← Ap_X(Ȳ) / Am_X(Ȳ)
    # All positive concepts and roles, not just atomics.
    rules.extend(build_updating_rules_for_concepts(concepts))
    rules.extend(build_updating_rules_for_roles(roles))

    return rules
