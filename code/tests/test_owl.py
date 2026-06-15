"""Tests for code/owl/ public API and coherence_update.horn_update."""

import os
import tempfile
from pathlib import Path

import pytest

from coherence_update.horn_update import build_rules_for_pus
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
    NegatedConcept,
    NegatedRole,
    Ontology,
    RoleInclusion,
    parse_owl,
    saturate_role_inclusions,
)

_REPO = Path(__file__).parents[2]
_ROBOT_OWL = _REPO / "benchmarks" / "inputs" / "horn" / "robotConj" / "TTL3.owl"
_DRONES_OWL = _REPO / "benchmarks" / "inputs" / "etc" / "drones" / "TTL.owl"

_PREFIXES = """\
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test.org/> .
<http://test.org/> rdf:type owl:Ontology .
"""


def _make_ontology(ttl: str) -> Ontology:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write(ttl)
        path = f.name
    try:
        return parse_owl(path)
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def robot_on():
    return parse_owl(str(_ROBOT_OWL))


@pytest.fixture(scope="module")
def drones_on():
    return parse_owl(str(_DRONES_OWL))


@pytest.fixture(scope="module")
def robot_rules(robot_on):
    on = parse_owl(str(_ROBOT_OWL))
    saturate_role_inclusions(on)
    return build_rules_for_pus(on)


@pytest.fixture
def simple_on():
    return _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:A rdfs:subClassOf :B .
"""
    )


# ---------------------------------------------------------------------------
# Expressions — dataclass properties and ids
# ---------------------------------------------------------------------------


def test_atomic_concept_id():
    assert AtomicConcept("http://test.org/SomeConcept").id == "someconcept"


def test_atomic_concept_fragment_after_hash():
    assert AtomicConcept("http://example.com/ont#Column0").id == "column0"


def test_owl_thing_and_nothing_ids():
    assert OWL_THING.id == "thing"
    assert OWL_NOTHING.id == "nothing"


def test_atomic_role_id():
    assert AtomicRole("http://test.org/hasRole").id == "hasrole"


def test_inverse_role_id():
    r = AtomicRole("http://test.org/R")
    inv = InverseRole(r)
    assert inv.id == "invr"
    assert inv.role is r


def test_negated_role_wrapping_atomic():
    assert NegatedRole(AtomicRole("http://test.org/R")).id == "not_r"


def test_negated_role_wrapping_inverse():
    r = AtomicRole("http://test.org/R")
    neg = NegatedRole(InverseRole(r))
    assert neg.id == "not_invr"
    assert isinstance(neg.role, InverseRole)


def test_existential_concept_id():
    assert ExistentialConcept(AtomicRole("http://test.org/R")).id == "existsr"


def test_inverse_existential_concept_id():
    assert InverseExistentialConcept(AtomicRole("http://test.org/R")).id == "existsinvr"


def test_negated_concept_id():
    assert NegatedConcept(AtomicConcept("http://test.org/A")).id == "not_a"


def test_intersection_concept_id():
    a = AtomicConcept("http://test.org/A")
    b = AtomicConcept("http://test.org/B")
    assert IntersectionConcept((a, b)).id == "a_and_b"


def test_frozen_atomic_concept():
    c = AtomicConcept("http://test.org/A")
    with pytest.raises((AttributeError, TypeError)):
        c.iri = "http://other.org/"  # type: ignore[misc]


def test_frozen_inverse_role():
    r = AtomicRole("http://test.org/R")
    inv = InverseRole(r)
    with pytest.raises((AttributeError, TypeError)):
        inv.role = r  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Ontology container — helper methods
# ---------------------------------------------------------------------------


def test_ontology_is_supported(simple_on):
    assert simple_on.is_supported
    assert simple_on.warnings == []


def test_atomic_concepts_filter(simple_on):
    ac = simple_on.atomic_concepts
    assert "a" in ac
    assert "b" in ac
    for v in ac.values():
        assert isinstance(v, AtomicConcept)


def test_atomic_roles_filter(simple_on):
    ar = simple_on.atomic_roles
    assert "r" in ar
    for v in ar.values():
        assert isinstance(v, AtomicRole)


def test_find_concept(simple_on):
    result = simple_on.find("a")
    assert isinstance(result, AtomicConcept)
    assert result.id == "a"


def test_find_role(simple_on):
    assert isinstance(simple_on.find("r"), AtomicRole)


def test_find_axiom(simple_on):
    assert isinstance(simple_on.find("a_sub_b"), ConceptInclusion)


def test_find_missing(simple_on):
    assert simple_on.find("does_not_exist") is None


def test_repr_contains_counts(simple_on):
    r = repr(simple_on)
    assert "concepts=" in r
    assert "roles=" in r
    assert "axioms=" in r


# ---------------------------------------------------------------------------
# Parse benchmarks/inputs/horn/robotConj/TTL3.owl
# ---------------------------------------------------------------------------


def test_robot_is_supported(robot_on):
    assert robot_on.is_supported


def test_robot_axiom_count(robot_on):
    assert len(robot_on.axioms) == 22


def test_robot_no_roles(robot_on):
    assert len(robot_on.atomic_roles) == 0


def test_robot_atomic_concept_count(robot_on):
    atomic = [
        c
        for c in robot_on.concepts.values()
        if isinstance(c, AtomicConcept) and c not in (OWL_THING, OWL_NOTHING)
    ]
    assert len(atomic) == 18


def test_robot_negated_concept_sup_count(robot_on):
    neg_sup = [
        ax
        for ax in robot_on.axioms
        if isinstance(ax, ConceptInclusion) and isinstance(ax.sup, NegatedConcept)
    ]
    assert len(neg_sup) == 4


def test_robot_intersection_sub_count(robot_on):
    inter_sub = [
        ax
        for ax in robot_on.axioms
        if isinstance(ax, ConceptInclusion) and isinstance(ax.sub, IntersectionConcept)
    ]
    assert len(inter_sub) == 6


def test_robot_no_owl_nothing_sup(robot_on):
    nothing_sup = [
        ax
        for ax in robot_on.axioms
        if isinstance(ax, ConceptInclusion) and ax.sup is OWL_NOTHING
    ]
    assert len(nothing_sup) == 0


def test_robot_all_axioms_are_concept_inclusions(robot_on):
    for ax in robot_on.axioms:
        assert isinstance(ax, ConceptInclusion)


# ---------------------------------------------------------------------------
# Parse benchmarks/inputs/etc/drones/TTL.owl
# ---------------------------------------------------------------------------


def test_drones_is_not_supported(drones_on):
    assert not drones_on.is_supported


def test_drones_warning_count(drones_on):
    assert len(drones_on.warnings) == 8


def test_drones_warnings_about_some_values_from(drones_on):
    some_warns = [w for w in drones_on.warnings if "owl:someValuesFrom" in w]
    assert len(some_warns) > 0


def test_drones_atomic_role_count(drones_on):
    assert len(drones_on.atomic_roles) == 3
    assert "near" in drones_on.atomic_roles
    assert "veryclose" in drones_on.atomic_roles
    assert "environment" in drones_on.atomic_roles


def test_drones_inverse_roles_registered(drones_on):
    assert "invnear" in drones_on.roles
    assert "invveryclose" in drones_on.roles
    assert isinstance(drones_on.roles["invnear"], InverseRole)


def test_drones_negated_inverse_roles_registered(drones_on):
    assert "not_invnear" in drones_on.roles
    neg_inv = drones_on.roles["not_invnear"]
    assert isinstance(neg_inv, NegatedRole)
    assert isinstance(neg_inv.role, InverseRole)


def test_drones_atomic_concept_count(drones_on):
    atomic = [
        c
        for c in drones_on.concepts.values()
        if isinstance(c, AtomicConcept) and c not in (OWL_THING, OWL_NOTHING)
    ]
    assert len(atomic) == 9


def test_drones_role_inclusion_veryclose_sub_near(drones_on):
    found = any(
        isinstance(ax, RoleInclusion)
        and ax.sub.id == "veryclose"
        and ax.sup.id == "near"
        for ax in drones_on.axioms
    )
    assert found, "Expected RoleInclusion veryclose ⊑ near"


# ---------------------------------------------------------------------------
# Inline parse tests — domain/range/disjoint/functional/intersection/OWL_NOTHING
# ---------------------------------------------------------------------------


def test_simple_concept_inclusion():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:A rdfs:subClassOf :B .
"""
    )
    axioms = [ax for ax in on.axioms if isinstance(ax, ConceptInclusion)]
    assert any(ax.sub.id == "a" and ax.sup.id == "b" for ax in axioms)


def test_disjoint_generates_negated_sup():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:A owl:disjointWith :B .
"""
    )
    axioms = [ax for ax in on.axioms if isinstance(ax, ConceptInclusion)]
    neg_sups = [ax for ax in axioms if isinstance(ax.sup, NegatedConcept)]
    assert any(ax.sub.id == "a" for ax in neg_sups)
    for ax in neg_sups:
        if ax.sub.id == "a":
            assert ax.sup.concept.id == "b"


def test_domain_generates_existential_inclusion():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:domain :A .
"""
    )
    found = any(
        isinstance(ax, ConceptInclusion)
        and isinstance(ax.sub, ExistentialConcept)
        and ax.sub.role.id == "r"
        and ax.sup.id == "a"
        for ax in on.axioms
    )
    assert found, "Expected ∃R ⊑ A from rdfs:domain"


def test_range_generates_inverse_existential_inclusion():
    on = _make_ontology(
        _PREFIXES
        + """
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:range :B .
"""
    )
    found = any(
        isinstance(ax, ConceptInclusion)
        and isinstance(ax.sub, InverseExistentialConcept)
        and ax.sub.role.id == "r"
        and ax.sup.id == "b"
        for ax in on.axioms
    )
    assert found, "Expected ∃R⁻ ⊑ B from rdfs:range"


def test_functional_property():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:FunctionalProperty .
"""
    )
    funcs = [ax for ax in on.axioms if isinstance(ax, FunctionalRole)]
    assert len(funcs) == 1
    assert funcs[0].role.id == "r"


def test_inverse_functional_property():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:InverseFunctionalProperty .
"""
    )
    inv_funcs = [ax for ax in on.axioms if isinstance(ax, InverseFunctionalRole)]
    assert len(inv_funcs) == 1
    assert inv_funcs[0].role.id == "r"


def test_role_inclusion():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:S rdf:type owl:ObjectProperty .
:R rdfs:subPropertyOf :S .
"""
    )
    ri = [ax for ax in on.axioms if isinstance(ax, RoleInclusion)]
    assert any(ax.sub.id == "r" and ax.sup.id == "s" for ax in ri)


def test_role_inclusion_with_inverse():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:S rdf:type owl:ObjectProperty .
:R rdfs:subPropertyOf [ owl:inverseOf :S ] .
"""
    )
    ri = [ax for ax in on.axioms if isinstance(ax, RoleInclusion)]
    inv_sups = [ax for ax in ri if isinstance(ax.sup, InverseRole)]
    assert any(
        ax.sub.id == "r" and ax.sup.id == "invs" for ax in inv_sups
    ), "Expected RoleInclusion R ⊑ S⁻ from [owl:inverseOf :S]"


def test_intersection_sub_concept():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:C rdf:type owl:Class .
[ rdf:type owl:Class ; owl:intersectionOf ( :A :B ) ] rdfs:subClassOf :C .
"""
    )
    inter_axioms = [
        ax
        for ax in on.axioms
        if isinstance(ax, ConceptInclusion) and isinstance(ax.sub, IntersectionConcept)
    ]
    assert len(inter_axioms) == 1
    assert {op.id for op in inter_axioms[0].sub.operands} == {"a", "b"}
    assert inter_axioms[0].sup.id == "c"


def test_owl_nothing_sup():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:A rdfs:subClassOf owl:Nothing .
"""
    )
    nothing_axioms = [
        ax
        for ax in on.axioms
        if isinstance(ax, ConceptInclusion) and ax.sup is OWL_NOTHING
    ]
    assert len(nothing_axioms) == 1
    assert nothing_axioms[0].sub.id == "a"


def test_unsupported_construct_generates_warning():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:TransitiveProperty .
"""
    )
    assert not on.is_supported
    assert any("owl:TransitiveProperty" in w for w in on.warnings)


# ---------------------------------------------------------------------------
# Saturation
# ---------------------------------------------------------------------------


def _make_role_ontology(sub: str, sup: str) -> Ontology:
    return _make_ontology(
        _PREFIXES
        + f"""
:{sub} rdf:type owl:ObjectProperty .
:{sup} rdf:type owl:ObjectProperty .
:{sub} rdfs:subPropertyOf :{sup} .
"""
    )


def test_saturation_derives_three_axioms():
    on = _make_role_ontology("R", "P")
    before = len(on.axioms)
    saturate_role_inclusions(on)
    assert len(on.axioms) == before + 3


def test_saturation_existential_domain():
    on = _make_role_ontology("R", "P")
    saturate_role_inclusions(on)
    found = any(
        isinstance(ax, ConceptInclusion)
        and isinstance(ax.sub, ExistentialConcept)
        and ax.sub.role.id == "r"
        and isinstance(ax.sup, ExistentialConcept)
        and ax.sup.role.id == "p"
        for ax in on.axioms
    )
    assert found, "Expected ∃R ⊑ ∃P after saturation"


def test_saturation_existential_range():
    on = _make_role_ontology("R", "P")
    saturate_role_inclusions(on)
    found = any(
        isinstance(ax, ConceptInclusion)
        and isinstance(ax.sub, InverseExistentialConcept)
        and ax.sub.role.id == "r"
        and isinstance(ax.sup, InverseExistentialConcept)
        and ax.sup.role.id == "p"
        for ax in on.axioms
    )
    assert found, "Expected ∃R⁻ ⊑ ∃P⁻ after saturation"


def test_saturation_inverse_role():
    on = _make_role_ontology("R", "P")
    saturate_role_inclusions(on)
    found = any(
        isinstance(ax, RoleInclusion)
        and isinstance(ax.sub, InverseRole)
        and ax.sub.role.id == "r"
        and isinstance(ax.sup, InverseRole)
        and ax.sup.role.id == "p"
        for ax in on.axioms
    )
    assert found, "Expected R⁻ ⊑ P⁻ after saturation"


def test_saturation_idempotent():
    on = _make_role_ontology("R", "P")
    saturate_role_inclusions(on)
    count_after_first = len(on.axioms)
    saturate_role_inclusions(on)
    assert len(on.axioms) == count_after_first, "Saturation should be idempotent"


def test_drones_saturation_derives_existential(drones_on):
    on = parse_owl(str(_DRONES_OWL))
    saturate_role_inclusions(on)
    found = any(
        isinstance(ax, ConceptInclusion)
        and isinstance(ax.sub, ExistentialConcept)
        and ax.sub.role.id == "veryclose"
        and isinstance(ax.sup, ExistentialConcept)
        and ax.sup.role.id == "near"
        for ax in on.axioms
    )
    assert found, "Expected ∃veryclose ⊑ ∃near after saturation of drones"


# ---------------------------------------------------------------------------
# Prioritized update rules (build_rules_for_pus)
# ---------------------------------------------------------------------------


def test_robot_rule_count(robot_rules):
    assert len(robot_rules) == 314


def test_trigger_rules_present(robot_rules):
    trigger = [r for r in robot_rules if r.startswith("AOrApCl_") and " :- " in r]
    assert len(trigger) > 0


def test_deletion_trigger_rules_present(robot_rules):
    # Rule 5: DelCl_X(X) :- Am_X(X)  (Am_ = deletion marker)
    del_trigger = [r for r in robot_rules if r.startswith("DelCl_") and "Am_" in r]
    assert len(del_trigger) > 0


def test_actual_deletion_rules_present(robot_rules):
    del_rules = [r for r in robot_rules if r.startswith("del_") and "DelCl_" in r]
    assert len(del_rules) > 0


def test_actual_insertion_rules_present(robot_rules):
    ins_rules = [r for r in robot_rules if r.startswith("ins_") and "InsCl_" in r]
    assert len(ins_rules) > 0


def test_no_role_rules_for_robot(robot_rules):
    binary_rules = [r for r in robot_rules if "(X,Y)" in r]
    assert len(binary_rules) == 0


def test_intersection_generates_min_rules(robot_rules):
    min_rules = [r for r in robot_rules if r.startswith("Min_")]
    assert len(min_rules) > 0


def test_pre_insertion_rules_present(robot_rules):
    pre_ins = [r for r in robot_rules if r.startswith("PreInsCl_")]
    assert len(pre_ins) > 0


def test_insertion_closure_rules_present(robot_rules):
    ins_cl = [r for r in robot_rules if r.startswith("InsCl_")]
    assert len(ins_cl) > 0


def test_incompatibility_rules_for_direct_clash(robot_rules):
    # Rule 16: incompatible_update() :- ApCl_X(X), Am_X(X)
    incompat = [
        r
        for r in robot_rules
        if r.startswith("incompatible_update()") and "ApCl_" in r and "Am_" in r
    ]
    assert len(incompat) > 0


def test_negated_sup_generates_propagation(robot_rules):
    # Axioms with NegatedConcept sup (e.g. rightof ⊑ not_leftof) produce
    # propagation rules AOrApCl_not_X :- AOrApCl_Y and ApCl_not_X :- ApCl_Y.
    # robotConj has 4 such axioms, so these rules must be present.
    prop_rules = [
        r
        for r in robot_rules
        if r.startswith("AOrApCl_not_") or r.startswith("ApCl_not_")
    ]
    assert len(prop_rules) > 0


def test_role_ontology_generates_binary_rules():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:domain :A .
:R rdfs:range :B .
"""
    )
    saturate_role_inclusions(on)
    rules = build_rules_for_pus(on)
    binary = [r for r in rules if "(X,Y)" in r]
    assert len(binary) > 0, "Expected binary (role) rules for ontology with R"


def test_functional_role_generates_two_conflict_rules():
    on = _make_ontology(
        _PREFIXES
        + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:FunctionalProperty .
"""
    )
    saturate_role_inclusions(on)
    rules = build_rules_for_pus(on)
    func_rules = [r for r in rules if "!=Z" in r]
    assert len(func_rules) == 2


def test_owl_nothing_generates_incompatibility():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:A rdfs:subClassOf owl:Nothing .
"""
    )
    saturate_role_inclusions(on)
    rules = build_rules_for_pus(on)
    incompat = [r for r in rules if r.startswith("incompatible_update()") and "ApCl_a" in r]
    assert len(incompat) > 0, "Expected incompatibility rule for A ⊑ ⊥"


def test_conjunction_bottom_incompatibility():
    on = _make_ontology(
        _PREFIXES
        + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
[ rdf:type owl:Class ; owl:intersectionOf ( :A :B ) ] rdfs:subClassOf owl:Nothing .
"""
    )
    saturate_role_inclusions(on)
    rules = build_rules_for_pus(on)
    incompat = [
        r
        for r in rules
        if r.startswith("incompatible_update()") and "ApCl_a" in r and "ApCl_b" in r
    ]
    assert len(incompat) > 0, "Expected incompatibility rule for A ⊓ B ⊑ ⊥"


def test_negative_role_inclusion_generates_deletion_rules():
    from owl.axioms import RoleInclusion as _RI
    from owl.expressions import NegatedRole as _NR

    r = AtomicRole("http://test.org/r")
    s = AtomicRole("http://test.org/s")
    on2 = Ontology(iri="http://test.org/")
    on2.roles[r.id] = r
    on2.roles[s.id] = s
    on2.roles[InverseRole(r).id] = InverseRole(r)
    on2.roles[InverseRole(s).id] = InverseRole(s)
    on2.roles[_NR(r).id] = _NR(r)
    on2.roles[_NR(s).id] = _NR(s)
    on2.axioms.append(_RI(r, _NR(s)))
    rules = build_rules_for_pus(on2)
    neg_role_rules = [
        r_str for r_str in rules if "DelCl_s(X,Y)" in r_str and "ApCl_r(X,Y)" in r_str
    ]
    assert len(neg_role_rules) > 0, "Expected DelCl rule from R ⊑ ¬S"
