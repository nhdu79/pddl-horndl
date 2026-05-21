"""
Basic tests for code/owl/ public API and coherence_update.prioritized_update.

Run with:
    PYTHONPATH=code python3 -m unittest code/tests/test_owl.py
or (from repo root, with venv active):
    python3 -m pytest code/tests/test_owl.py -v
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Locate benchmark ontologies relative to this file
_REPO = Path(__file__).parents[2]
_ROBOT_OWL = _REPO / "benchmarks" / "inputs" / "robotConj" / "TTL3.owl"
_DRONES_OWL = _REPO / "benchmarks" / "inputs" / "drones" / "TTL.owl"

sys.path.insert(0, str(_REPO / "code"))

from owl import (
    parse_owl,
    saturate_role_inclusions,
    Ontology,
    AtomicConcept,
    AtomicRole,
    ConceptInclusion,
    ExistentialConcept,
    FunctionalRole,
    IntersectionConcept,
    InverseFunctionalRole,
    InverseExistentialConcept,
    InverseRole,
    NegatedConcept,
    NegatedRole,
    OWL_NOTHING,
    OWL_THING,
    RoleInclusion,
)
from coherence_update.prioritized_update import (
    build_rules_for_prioritized_coherence_update_semantics,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ontology(ttl: str) -> Ontology:
    """Write ttl to a temp file, parse, and return the Ontology."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write(ttl)
        path = f.name
    try:
        return parse_owl(path)
    finally:
        os.unlink(path)


_PREFIXES = """\
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test.org/> .
<http://test.org/> rdf:type owl:Ontology .
"""


# ---------------------------------------------------------------------------
# TestExpressions — dataclass properties and ids
# ---------------------------------------------------------------------------

class TestExpressions(unittest.TestCase):

    def test_atomic_concept_id(self):
        c = AtomicConcept("http://test.org/SomeConcept")
        self.assertEqual(c.id, "someconcept")

    def test_atomic_concept_fragment_after_hash(self):
        c = AtomicConcept("http://example.com/ont#Column0")
        self.assertEqual(c.id, "column0")

    def test_owl_thing_and_nothing_ids(self):
        self.assertEqual(OWL_THING.id, "thing")
        self.assertEqual(OWL_NOTHING.id, "nothing")

    def test_atomic_role_id(self):
        r = AtomicRole("http://test.org/hasRole")
        self.assertEqual(r.id, "hasrole")

    def test_inverse_role_id(self):
        r = AtomicRole("http://test.org/R")
        inv = InverseRole(r)
        self.assertEqual(inv.id, "inv_r")
        self.assertIs(inv.role, r)

    def test_negated_role_wrapping_atomic(self):
        r = AtomicRole("http://test.org/R")
        neg = NegatedRole(r)
        self.assertEqual(neg.id, "not_r")

    def test_negated_role_wrapping_inverse(self):
        r = AtomicRole("http://test.org/R")
        inv = InverseRole(r)
        neg = NegatedRole(inv)
        self.assertEqual(neg.id, "not_inv_r")
        self.assertIsInstance(neg.role, InverseRole)

    def test_existential_concept_id(self):
        r = AtomicRole("http://test.org/R")
        ex = ExistentialConcept(r)
        self.assertEqual(ex.id, "exists_r")

    def test_inverse_existential_concept_id(self):
        r = AtomicRole("http://test.org/R")
        inv_ex = InverseExistentialConcept(r)
        self.assertEqual(inv_ex.id, "exists_inv_r")

    def test_negated_concept_id(self):
        c = AtomicConcept("http://test.org/A")
        neg = NegatedConcept(c)
        self.assertEqual(neg.id, "not_a")

    def test_intersection_concept_id(self):
        a = AtomicConcept("http://test.org/A")
        b = AtomicConcept("http://test.org/B")
        inter = IntersectionConcept((a, b))
        self.assertEqual(inter.id, "a_and_b")

    def test_frozen_atomic_concept(self):
        c = AtomicConcept("http://test.org/A")
        with self.assertRaises((AttributeError, TypeError)):
            c.iri = "http://other.org/"  # type: ignore[misc]

    def test_frozen_inverse_role(self):
        r = AtomicRole("http://test.org/R")
        inv = InverseRole(r)
        with self.assertRaises((AttributeError, TypeError)):
            inv.role = r  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TestOntologyContainer — Ontology helper methods
# ---------------------------------------------------------------------------

class TestOntologyContainer(unittest.TestCase):

    def setUp(self):
        self.on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:A rdfs:subClassOf :B .
""")

    def test_is_supported_true(self):
        self.assertTrue(self.on.is_supported)
        self.assertEqual(self.on.warnings, [])

    def test_atomic_concepts_filter(self):
        ac = self.on.atomic_concepts
        self.assertIn("a", ac)
        self.assertIn("b", ac)
        # NegatedConcept, ExistentialConcept etc. must be excluded
        for v in ac.values():
            self.assertIsInstance(v, AtomicConcept)

    def test_atomic_roles_filter(self):
        ar = self.on.atomic_roles
        self.assertIn("r", ar)
        for v in ar.values():
            self.assertIsInstance(v, AtomicRole)

    def test_find_concept(self):
        result = self.on.find("a")
        self.assertIsInstance(result, AtomicConcept)
        self.assertEqual(result.id, "a")

    def test_find_role(self):
        result = self.on.find("r")
        self.assertIsInstance(result, AtomicRole)

    def test_find_axiom(self):
        result = self.on.find("a_sub_b")
        self.assertIsInstance(result, ConceptInclusion)

    def test_find_missing(self):
        self.assertIsNone(self.on.find("does_not_exist"))

    def test_repr_contains_counts(self):
        r = repr(self.on)
        self.assertIn("concepts=", r)
        self.assertIn("roles=", r)
        self.assertIn("axioms=", r)


# ---------------------------------------------------------------------------
# TestParseOwlRobotConj — benchmarks/inputs/robotConj/TTL3.owl
# ---------------------------------------------------------------------------

class TestParseOwlRobotConj(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.on = parse_owl(str(_ROBOT_OWL))

    def test_is_supported(self):
        self.assertTrue(self.on.is_supported)

    def test_axiom_count(self):
        self.assertEqual(len(self.on.axioms), 22)

    def test_no_roles(self):
        self.assertEqual(len(self.on.atomic_roles), 0)

    def test_atomic_concept_count(self):
        # 17 named concepts, excluding OWL_THING / OWL_NOTHING
        atomic = [
            c for c in self.on.concepts.values()
            if isinstance(c, AtomicConcept) and c not in (OWL_THING, OWL_NOTHING)
        ]
        self.assertEqual(len(atomic), 17)

    def test_negated_concept_sup_count(self):
        neg_sup = [
            ax for ax in self.on.axioms
            if isinstance(ax, ConceptInclusion) and isinstance(ax.sup, NegatedConcept)
        ]
        self.assertEqual(len(neg_sup), 4)

    def test_intersection_sub_count(self):
        inter_sub = [
            ax for ax in self.on.axioms
            if isinstance(ax, ConceptInclusion) and isinstance(ax.sub, IntersectionConcept)
        ]
        self.assertEqual(len(inter_sub), 6)

    def test_no_owl_nothing_sup(self):
        nothing_sup = [
            ax for ax in self.on.axioms
            if isinstance(ax, ConceptInclusion) and ax.sup is OWL_NOTHING
        ]
        self.assertEqual(len(nothing_sup), 0)

    def test_all_axioms_are_concept_inclusions(self):
        for ax in self.on.axioms:
            self.assertIsInstance(ax, ConceptInclusion)


# ---------------------------------------------------------------------------
# TestParseOwlDrones — benchmarks/inputs/drones/TTL.owl
# ---------------------------------------------------------------------------

class TestParseOwlDrones(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.on = parse_owl(str(_DRONES_OWL))

    def test_is_not_supported(self):
        self.assertFalse(self.on.is_supported)

    def test_warning_count(self):
        self.assertEqual(len(self.on.warnings), 10)

    def test_symmetric_property_warnings(self):
        sym_warns = [w for w in self.on.warnings if "owl:SymmetricProperty" in w]
        self.assertEqual(len(sym_warns), 2)

    def test_atomic_role_count(self):
        self.assertEqual(len(self.on.atomic_roles), 3)
        self.assertIn("near", self.on.atomic_roles)
        self.assertIn("veryclose", self.on.atomic_roles)
        self.assertIn("environment", self.on.atomic_roles)

    def test_inverse_roles_registered(self):
        self.assertIn("inv_near", self.on.roles)
        self.assertIn("inv_veryclose", self.on.roles)
        self.assertIsInstance(self.on.roles["inv_near"], InverseRole)

    def test_negated_inverse_roles_registered(self):
        # NegatedRole(InverseRole(r)) must be registered
        self.assertIn("not_inv_near", self.on.roles)
        neg_inv = self.on.roles["not_inv_near"]
        self.assertIsInstance(neg_inv, NegatedRole)
        self.assertIsInstance(neg_inv.role, InverseRole)

    def test_atomic_concept_count(self):
        atomic = [
            c for c in self.on.concepts.values()
            if isinstance(c, AtomicConcept) and c not in (OWL_THING, OWL_NOTHING)
        ]
        self.assertEqual(len(atomic), 9)

    def test_role_inclusion_veryclose_sub_near(self):
        found = any(
            isinstance(ax, RoleInclusion)
            and ax.sub.id == "veryclose"
            and ax.sup.id == "near"
            for ax in self.on.axioms
        )
        self.assertTrue(found, "Expected RoleInclusion veryclose ⊑ near")


# ---------------------------------------------------------------------------
# TestParseOwlInline — domain/range/disjoint/functional/intersection/OWL_NOTHING
# ---------------------------------------------------------------------------

class TestParseOwlInline(unittest.TestCase):

    def test_simple_concept_inclusion(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:A rdfs:subClassOf :B .
""")
        axioms = [ax for ax in on.axioms if isinstance(ax, ConceptInclusion)]
        self.assertTrue(any(ax.sub.id == "a" and ax.sup.id == "b" for ax in axioms))

    def test_disjoint_generates_negated_sup(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:A owl:disjointWith :B .
""")
        axioms = [ax for ax in on.axioms if isinstance(ax, ConceptInclusion)]
        neg_sups = [ax for ax in axioms if isinstance(ax.sup, NegatedConcept)]
        self.assertTrue(any(ax.sub.id == "a" for ax in neg_sups))
        for ax in neg_sups:
            if ax.sub.id == "a":
                self.assertEqual(ax.sup.concept.id, "b")

    def test_domain_generates_existential_inclusion(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:domain :A .
""")
        found = any(
            isinstance(ax, ConceptInclusion)
            and isinstance(ax.sub, ExistentialConcept)
            and ax.sub.role.id == "r"
            and ax.sup.id == "a"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected ∃R ⊑ A from rdfs:domain")

    def test_range_generates_inverse_existential_inclusion(self):
        on = _make_ontology(_PREFIXES + """
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:range :B .
""")
        found = any(
            isinstance(ax, ConceptInclusion)
            and isinstance(ax.sub, InverseExistentialConcept)
            and ax.sub.role.id == "r"
            and ax.sup.id == "b"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected ∃R⁻ ⊑ B from rdfs:range")

    def test_functional_property(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:FunctionalProperty .
""")
        funcs = [ax for ax in on.axioms if isinstance(ax, FunctionalRole)]
        self.assertEqual(len(funcs), 1)
        self.assertEqual(funcs[0].role.id, "r")

    def test_inverse_functional_property(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:InverseFunctionalProperty .
""")
        inv_funcs = [ax for ax in on.axioms if isinstance(ax, InverseFunctionalRole)]
        self.assertEqual(len(inv_funcs), 1)
        self.assertEqual(inv_funcs[0].role.id, "r")

    def test_role_inclusion(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:S rdf:type owl:ObjectProperty .
:R rdfs:subPropertyOf :S .
""")
        ri = [ax for ax in on.axioms if isinstance(ax, RoleInclusion)]
        self.assertTrue(any(ax.sub.id == "r" and ax.sup.id == "s" for ax in ri))

    def test_role_inclusion_with_inverse(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:S rdf:type owl:ObjectProperty .
:R rdfs:subPropertyOf [ owl:inverseOf :S ] .
""")
        ri = [ax for ax in on.axioms if isinstance(ax, RoleInclusion)]
        inv_sups = [ax for ax in ri if isinstance(ax.sup, InverseRole)]
        self.assertTrue(
            any(ax.sub.id == "r" and ax.sup.id == "inv_s" for ax in inv_sups),
            "Expected RoleInclusion R ⊑ S⁻ from [owl:inverseOf :S]"
        )

    def test_intersection_sub_concept(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:C rdf:type owl:Class .
[ rdf:type owl:Class ; owl:intersectionOf ( :A :B ) ] rdfs:subClassOf :C .
""")
        inter_axioms = [
            ax for ax in on.axioms
            if isinstance(ax, ConceptInclusion) and isinstance(ax.sub, IntersectionConcept)
        ]
        self.assertEqual(len(inter_axioms), 1)
        ax = inter_axioms[0]
        op_ids = {op.id for op in ax.sub.operands}
        self.assertEqual(op_ids, {"a", "b"})
        self.assertEqual(ax.sup.id, "c")

    def test_owl_nothing_sup(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:A rdfs:subClassOf owl:Nothing .
""")
        nothing_axioms = [
            ax for ax in on.axioms
            if isinstance(ax, ConceptInclusion) and ax.sup is OWL_NOTHING
        ]
        self.assertEqual(len(nothing_axioms), 1)
        self.assertEqual(nothing_axioms[0].sub.id, "a")

    def test_unsupported_construct_generates_warning(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:TransitiveProperty .
""")
        self.assertFalse(on.is_supported)
        self.assertTrue(any("owl:TransitiveProperty" in w for w in on.warnings))


# ---------------------------------------------------------------------------
# TestSaturateRoleInclusions
# ---------------------------------------------------------------------------

class TestSaturateRoleInclusions(unittest.TestCase):

    def _make_role_ontology(self, sub_iri: str, sup_iri: str) -> Ontology:
        return _make_ontology(_PREFIXES + f"""
:{sub_iri} rdf:type owl:ObjectProperty .
:{sup_iri} rdf:type owl:ObjectProperty .
:{sub_iri} rdfs:subPropertyOf :{sup_iri} .
""")

    def test_saturation_derives_three_axioms(self):
        on = self._make_role_ontology("R", "P")
        before = len(on.axioms)
        saturate_role_inclusions(on)
        # Should add: ∃R ⊑ ∃P, ∃R⁻ ⊑ ∃P⁻, R⁻ ⊑ P⁻
        self.assertEqual(len(on.axioms), before + 3)

    def test_existential_domain_derived(self):
        on = self._make_role_ontology("R", "P")
        saturate_role_inclusions(on)
        found = any(
            isinstance(ax, ConceptInclusion)
            and isinstance(ax.sub, ExistentialConcept) and ax.sub.role.id == "r"
            and isinstance(ax.sup, ExistentialConcept) and ax.sup.role.id == "p"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected ∃R ⊑ ∃P after saturation")

    def test_existential_range_derived(self):
        on = self._make_role_ontology("R", "P")
        saturate_role_inclusions(on)
        found = any(
            isinstance(ax, ConceptInclusion)
            and isinstance(ax.sub, InverseExistentialConcept) and ax.sub.role.id == "r"
            and isinstance(ax.sup, InverseExistentialConcept) and ax.sup.role.id == "p"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected ∃R⁻ ⊑ ∃P⁻ after saturation")

    def test_inverse_role_derived(self):
        on = self._make_role_ontology("R", "P")
        saturate_role_inclusions(on)
        found = any(
            isinstance(ax, RoleInclusion)
            and isinstance(ax.sub, InverseRole) and ax.sub.role.id == "r"
            and isinstance(ax.sup, InverseRole) and ax.sup.role.id == "p"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected R⁻ ⊑ P⁻ after saturation")

    def test_saturation_idempotent(self):
        on = self._make_role_ontology("R", "P")
        saturate_role_inclusions(on)
        count_after_first = len(on.axioms)
        saturate_role_inclusions(on)
        self.assertEqual(len(on.axioms), count_after_first, "Saturation should be idempotent")

    def test_drones_saturation(self):
        on = parse_owl(str(_DRONES_OWL))
        saturate_role_inclusions(on)
        # veryclose ⊑ near should produce ∃veryclose ⊑ ∃near, ∃vc⁻ ⊑ ∃near⁻, vc⁻ ⊑ near⁻
        found = any(
            isinstance(ax, ConceptInclusion)
            and isinstance(ax.sub, ExistentialConcept) and ax.sub.role.id == "veryclose"
            and isinstance(ax.sup, ExistentialConcept) and ax.sup.role.id == "near"
            for ax in on.axioms
        )
        self.assertTrue(found, "Expected ∃veryclose ⊑ ∃near after saturation of drones")


# ---------------------------------------------------------------------------
# TestPrioritizedUpdate
# ---------------------------------------------------------------------------

class TestPrioritizedUpdate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.robot_on = parse_owl(str(_ROBOT_OWL))
        saturate_role_inclusions(cls.robot_on)
        cls.robot_rules = build_rules_for_prioritized_coherence_update_semantics(cls.robot_on)

    def test_robot_rule_count(self):
        self.assertEqual(len(self.robot_rules), 250)

    def test_trigger_rules_present(self):
        # Rule 1: AOrApCl_X(X) :- X(X) for some concept
        trigger = [r for r in self.robot_rules if r.startswith("AOrApCl_") and " :- " in r]
        self.assertGreater(len(trigger), 0)

    def test_deletion_trigger_rules_present(self):
        # Rule 5: DelCl_X(X) :- del_X_request(X)
        del_trigger = [r for r in self.robot_rules if r.startswith("DelCl_") and "request" in r]
        self.assertGreater(len(del_trigger), 0)

    def test_actual_deletion_rules_present(self):
        # Rule 17: del_X(X) :- X(X), DelCl_X(X)
        del_rules = [r for r in self.robot_rules if r.startswith("del_") and "DelCl_" in r]
        self.assertGreater(len(del_rules), 0)

    def test_actual_insertion_rules_present(self):
        # Rule 21: ins_X(X) :- -X(X), InsCl_X(X)
        ins_rules = [r for r in self.robot_rules if r.startswith("ins_") and "InsCl_" in r]
        self.assertGreater(len(ins_rules), 0)

    def test_no_role_rules_for_robot(self):
        # robotConj has no roles, so no binary rules should be generated
        binary_rules = [r for r in self.robot_rules if "(X,Y)" in r]
        self.assertEqual(len(binary_rules), 0)

    def test_intersection_generates_min_rules(self):
        # IntersectionConcept subs should produce Min_ rules (rule 13)
        min_rules = [r for r in self.robot_rules if r.startswith("Min_")]
        self.assertGreater(len(min_rules), 0)

    def test_pre_insertion_rules_present(self):
        # Rule 18: PreInsCl_τ(X) :- ...
        pre_ins = [r for r in self.robot_rules if r.startswith("PreInsCl_")]
        self.assertGreater(len(pre_ins), 0)

    def test_insertion_closure_rules_present(self):
        # Rule 19: InsCl_X(X) :- DelCl_Xi(X), PreInsCl_τ(X)
        ins_cl = [r for r in self.robot_rules if r.startswith("InsCl_")]
        self.assertGreater(len(ins_cl), 0)

    def test_incompatibility_rules_for_direct_clash(self):
        # Rule 16: incompatible_update() :- ApCl_X(X), del_X_request(X)
        incompat = [
            r for r in self.robot_rules
            if r.startswith("incompatible_update()") and "del_" in r and "request" in r
        ]
        self.assertGreater(len(incompat), 0)

    def test_negated_sup_skips_propagation(self):
        # Axioms with NegatedConcept sup should not generate AOrApCl propagation rules for them
        # robotConj has 4 such axioms; verify no propagation rule for a negated sup
        # (negated concepts themselves are not "positive" concepts and won't appear in rule LHS)
        prop_rules = [
            r for r in self.robot_rules
            if r.startswith("AOrApCl_not_") or r.startswith("ApCl_not_")
        ]
        self.assertEqual(len(prop_rules), 0)

    def test_role_ontology_generates_binary_rules(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
:R rdf:type owl:ObjectProperty .
:R rdfs:domain :A .
:R rdfs:range :B .
""")
        saturate_role_inclusions(on)
        rules = build_rules_for_prioritized_coherence_update_semantics(on)
        binary = [r for r in rules if "(X,Y)" in r]
        self.assertGreater(len(binary), 0, "Expected binary (role) rules for ontology with R")

    def test_functional_role_generates_functional_rules(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:R rdf:type owl:FunctionalProperty .
""")
        saturate_role_inclusions(on)
        rules = build_rules_for_prioritized_coherence_update_semantics(on)
        # Rules 8-9: functional role conflict
        func_rules = [r for r in rules if "!=Z" in r]
        self.assertEqual(len(func_rules), 2)

    def test_owl_nothing_generates_incompatibility(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:A rdfs:subClassOf owl:Nothing .
""")
        saturate_role_inclusions(on)
        rules = build_rules_for_prioritized_coherence_update_semantics(on)
        incompat = [r for r in rules if r.startswith("incompatible_update()") and "ApCl_a" in r]
        self.assertGreater(len(incompat), 0, "Expected incompatibility rule for A ⊑ ⊥")

    def test_conjunction_bottom_incompatibility(self):
        on = _make_ontology(_PREFIXES + """
:A rdf:type owl:Class .
:B rdf:type owl:Class .
[ rdf:type owl:Class ; owl:intersectionOf ( :A :B ) ] rdfs:subClassOf owl:Nothing .
""")
        saturate_role_inclusions(on)
        rules = build_rules_for_prioritized_coherence_update_semantics(on)
        incompat = [
            r for r in rules
            if r.startswith("incompatible_update()") and "ApCl_a" in r and "ApCl_b" in r
        ]
        self.assertGreater(len(incompat), 0, "Expected incompatibility rule for A ⊓ B ⊑ ⊥")

    def test_negative_role_inclusion_generates_deletion_rules(self):
        on = _make_ontology(_PREFIXES + """
:R rdf:type owl:ObjectProperty .
:S rdf:type owl:ObjectProperty .
:R owl:disjointWith :S .
""")
        # owl:disjointWith on properties is not directly supported; test via NegatedRole axiom
        # directly instead, by constructing it programmatically
        r = AtomicRole("http://test.org/r")
        s = AtomicRole("http://test.org/s")
        from owl.expressions import NegatedRole
        from owl.axioms import RoleInclusion
        on2 = Ontology(iri="http://test.org/")
        on2.roles[r.id] = r
        on2.roles[s.id] = s
        on2.roles[InverseRole(r).id] = InverseRole(r)
        on2.roles[InverseRole(s).id] = InverseRole(s)
        on2.roles[NegatedRole(r).id] = NegatedRole(r)
        on2.roles[NegatedRole(s).id] = NegatedRole(s)
        on2.axioms.append(RoleInclusion(r, NegatedRole(s)))
        rules = build_rules_for_prioritized_coherence_update_semantics(on2)
        neg_role_rules = [
            r_str for r_str in rules
            if "DelCl_s(X,Y)" in r_str and "ApCl_r(X,Y)" in r_str
        ]
        self.assertGreater(len(neg_role_rules), 0, "Expected DelCl rule from R ⊑ ¬S")


if __name__ == "__main__":
    unittest.main()
