"""
OWL ontology parser backed by rdflib.

Parses an OWL Turtle file and normalises the TBox into the same `sub`-predicate
form that `code/nemo/t_closure.rls` computes, using the expression and axiom
types defined in owl.expressions and owl.axioms.

Supported OWL constructors:
  owl:ObjectProperty, owl:FunctionalProperty, owl:InverseFunctionalProperty
  owl:SymmetricProperty                                                    → P ⊑ P⁻
  rdfs:subPropertyOf, rdfs:domain, rdfs:range
  owl:Class with rdfs:subClassOf, owl:disjointWith
  owl:Nothing                                                              → ⊥  (OWL_NOTHING)
  Blank-node restriction  owl:onProperty P + owl:someValuesFrom owl:Thing → ∃P
  Blank-node intersection owl:intersectionOf (A B …)                      → A ⊓ B
  General (blank-node subject) subClassOf / disjointWith axioms

Unsupported constructs are recorded in Ontology.warnings rather than raising;
call Ontology.is_supported to check.
"""

from __future__ import annotations

from rdflib import Graph, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS

from owl.axioms import (
    ConceptInclusion,
    FunctionalRole,
    InverseFunctionalRole,
    Ontology,
    RoleInclusion,
)
from owl.expressions import (
    AtomicConcept,
    AtomicRole,
    ConceptExpression,
    ExistentialConcept,
    IntersectionConcept,
    InverseExistentialConcept,
    InverseRole,
    NegatedConcept,
    NegatedRole,
    OWL_NOTHING,
    OWL_THING,
    RoleExpression,
    _local_name,
)


# ---------------------------------------------------------------------------
# Known-unsupported OWL constructs  (post-parse coverage scan)
# ---------------------------------------------------------------------------

# Property characteristic types beyond owl:ObjectProperty that carry axiom semantics
_UNSUPPORTED_PROP_TYPES: list[tuple] = [
    (OWL.DatatypeProperty,    "owl:DatatypeProperty"),
    (OWL.TransitiveProperty,  "owl:TransitiveProperty"),
    (OWL.AsymmetricProperty,  "owl:AsymmetricProperty"),
    (OWL.ReflexiveProperty,   "owl:ReflexiveProperty"),
    (OWL.IrreflexiveProperty, "owl:IrreflexiveProperty"),
]

# Axiom-forming predicates not iterated by any collection method
_UNSUPPORTED_AXIOM_PREDS: list[tuple] = [
    (OWL.equivalentClass,    "owl:equivalentClass"),
    (OWL.equivalentProperty, "owl:equivalentProperty"),
    (OWL.propertyChainAxiom, "owl:propertyChainAxiom"),
    (OWL.inverseOf,          "owl:inverseOf"),
    (OWL.hasKey,             "owl:hasKey"),
]

# Meta-class types whose instances represent ignored axioms
_UNSUPPORTED_META_TYPES: list[tuple] = [
    (OWL.AllDisjointClasses,        "owl:AllDisjointClasses"),
    (OWL.AllDisjointProperties,     "owl:AllDisjointProperties"),
    (OWL.NegativePropertyAssertion, "owl:NegativePropertyAssertion"),
]

# Class-expression predicates detected inside _resolve_concept
_UNSUPPORTED_CLASS_EXPRS: list[tuple] = [
    (OWL.unionOf,      "owl:unionOf"),
    (OWL.complementOf, "owl:complementOf"),
    (OWL.oneOf,        "owl:oneOf"),
]

# Restriction predicates other than owl:someValuesFrom
_UNSUPPORTED_RESTRICTIONS: list[tuple] = [
    (OWL.allValuesFrom,           "owl:allValuesFrom"),
    (OWL.hasValue,                "owl:hasValue"),
    (OWL.maxCardinality,          "owl:maxCardinality"),
    (OWL.minCardinality,          "owl:minCardinality"),
    (OWL.cardinality,             "owl:cardinality"),
    (OWL.maxQualifiedCardinality, "owl:maxQualifiedCardinality"),
    (OWL.minQualifiedCardinality, "owl:minQualifiedCardinality"),
    (OWL.qualifiedCardinality,    "owl:qualifiedCardinality"),
]


# ---------------------------------------------------------------------------
# Internal builder
# ---------------------------------------------------------------------------

class _OWLBuilder:
    """Walks an rdflib Graph and populates an Ontology."""

    def __init__(self, graph: Graph) -> None:
        self._g = graph
        self._onto = Ontology(iri="")
        # IRI-keyed lookups for resolving named nodes during axiom collection
        self._concepts_by_iri: dict[str, AtomicConcept] = {}
        self._roles_by_iri: dict[str, AtomicRole] = {}

    def _warn(self, msg: str) -> None:
        self._onto.warnings.append(msg)

    # ------------------------------------------------------------------
    # Top-level entry point
    # ------------------------------------------------------------------

    def build(self) -> Ontology:
        self._collect_ontology_iri()
        self._collect_atomic_concepts()  # concept(?X), atomic(?X) + negOf
        self._collect_atomic_roles()     # role(?P), atomic(?P) + invOf + negOf + domOf + rngOf
        self._collect_role_axioms()      # funct, invFunct, symmetric, subPropertyOf, domain, range
        self._collect_concept_axioms()   # subClassOf, disjointWith on named subjects
        self._collect_general_axioms()   # subClassOf, disjointWith on blank-node subjects
        self._scan_unsupported()         # warn about constructs outside the supported fragment
        self._deduplicate_axioms()
        return self._onto

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def _add_concept(self, expr: ConceptExpression) -> ConceptExpression:
        self._onto.concepts[expr.id] = expr
        return expr

    def _add_role(self, expr: RoleExpression) -> RoleExpression:
        self._onto.roles[expr.id] = expr
        return expr

    def _add_axiom(self, ax) -> None:
        self._onto.axioms.append(ax)

    # ------------------------------------------------------------------
    # Entity collection (mirrors t_closure.rls derivation rules)
    # ------------------------------------------------------------------

    def _collect_ontology_iri(self) -> None:
        for s in self._g.subjects(RDF.type, OWL.Ontology):
            self._onto.iri = str(s)
            return

    def _collect_atomic_concepts(self) -> None:
        """
        concept(?X), atomic(?X) :- TRIPLE(?X, rdf:type, owl:Class)
        concept(!notX), negOf(!notX, ?X) :- concept(?X), atomic(?X)
        """
        for s in self._g.subjects(RDF.type, OWL.Class):
            if isinstance(s, BNode):
                continue
            c = AtomicConcept(str(s))
            self._concepts_by_iri[c.iri] = c
            self._add_concept(c)
            self._add_concept(NegatedConcept(c))

    def _collect_atomic_roles(self) -> None:
        """
        role(?P), atomic(?P)    :- TRIPLE(?P, rdf:type, owl:ObjectProperty)
        role(!notP), negOf(…)   :- role(?P), atomic(?P)
        role(!Q),    invOf(…)   :- role(?P), atomic(?P)
        domOf(!U, P) → ∃P       :- role(?P)   (+ negOf for ∃P)
        rngOf(!U, P) → ∃P⁻     :- role(?P)   (+ negOf for ∃P⁻)
        """
        for s in self._g.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(s, BNode):
                continue
            r = AtomicRole(str(s))
            self._roles_by_iri[r.iri] = r
            self._add_role(r)
            self._add_role(NegatedRole(r))
            inv_r = InverseRole(r)
            self._add_role(inv_r)
            self._add_role(NegatedRole(inv_r))

            ex = ExistentialConcept(r)
            self._add_concept(ex)
            self._add_concept(NegatedConcept(ex))

            inv_ex = InverseExistentialConcept(r)
            self._add_concept(inv_ex)
            self._add_concept(NegatedConcept(inv_ex))

    # ------------------------------------------------------------------
    # Axiom collection
    # ------------------------------------------------------------------

    def _collect_role_axioms(self) -> None:
        """
        funct(?P)    :- TRIPLE(?P, rdf:type, owl:FunctionalProperty)
        invFunct(?P) :- TRIPLE(?P, rdf:type, owl:InverseFunctionalProperty)
        sub(?P, ?P⁻) :- TRIPLE(?P, rdf:type, owl:SymmetricProperty)
        sub(?P, ?Q)  :- TRIPLE(?P, rdfs:subPropertyOf, ?Q)
        sub(∃P, X)   :- TRIPLE(?P, rdfs:domain, ?X), domOf(∃P, ?P)
        sub(∃P⁻, X)  :- TRIPLE(?P, rdfs:range,  ?X), rngOf(∃P⁻, ?P)
        """
        for r_iri, role in self._roles_by_iri.items():
            node = URIRef(r_iri)

            if (node, RDF.type, OWL.FunctionalProperty) in self._g:
                self._add_axiom(FunctionalRole(role))

            if (node, RDF.type, OWL.InverseFunctionalProperty) in self._g:
                self._add_axiom(InverseFunctionalRole(role))

            if (node, RDF.type, OWL.SymmetricProperty) in self._g:
                self._add_axiom(RoleInclusion(role, InverseRole(role)))

            for sup_node in self._g.objects(node, RDFS.subPropertyOf):
                sup = self._resolve_role(sup_node)
                if sup is not None:
                    self._add_axiom(RoleInclusion(role, sup))

            for domain_node in self._g.objects(node, RDFS.domain):
                sup = self._resolve_concept(domain_node)
                if sup is not None:
                    self._add_axiom(ConceptInclusion(ExistentialConcept(role), sup))

            for range_node in self._g.objects(node, RDFS.range):
                sup = self._resolve_concept(range_node)
                if sup is not None:
                    self._add_axiom(ConceptInclusion(InverseExistentialConcept(role), sup))

    def _collect_concept_axioms(self) -> None:
        """
        sub(?X, ?Y)        :- TRIPLE(?X, rdfs:subClassOf, ?Y)      (named X)
        sub(?X, negOf(?Y)) :- TRIPLE(?X, owl:disjointWith, ?Y)     (named X)
        """
        for c_iri, concept in self._concepts_by_iri.items():
            node = URIRef(c_iri)

            for sup_node in self._g.objects(node, RDFS.subClassOf):
                sup = self._resolve_concept(sup_node)
                if sup is not None:
                    self._add_axiom(ConceptInclusion(concept, sup))

            for disjoint_node in self._g.objects(node, OWL.disjointWith):
                sup = self._resolve_concept(disjoint_node)
                if sup is not None:
                    self._add_axiom(ConceptInclusion(concept, NegatedConcept(sup)))

    def _collect_general_axioms(self) -> None:
        """
        Same rules applied to blank-node subjects (general TBox axioms).
        rdf:List nodes are skipped.
        """
        visited: set = set()
        for predicate in (RDFS.subClassOf, OWL.disjointWith):
            for subject in self._g.subjects(predicate, None):
                if not isinstance(subject, BNode) or subject in visited:
                    continue
                if (subject, RDF.first, None) in self._g:
                    continue  # rdf:List node — not an axiom subject
                visited.add(subject)

                sub_expr = self._resolve_concept(subject)
                if sub_expr is None:
                    continue
                # Register intersection concepts that appear only in general axioms
                if isinstance(sub_expr, IntersectionConcept):
                    self._add_concept(sub_expr)
                    self._add_concept(NegatedConcept(sub_expr))

                for sup_node in self._g.objects(subject, RDFS.subClassOf):
                    sup = self._resolve_concept(sup_node)
                    if sup is not None:
                        self._add_axiom(ConceptInclusion(sub_expr, sup))
                for disjoint_node in self._g.objects(subject, OWL.disjointWith):
                    sup = self._resolve_concept(disjoint_node)
                    if sup is not None:
                        self._add_axiom(ConceptInclusion(sub_expr, NegatedConcept(sup)))

    # ------------------------------------------------------------------
    # Node resolvers — turn rdflib nodes into expression objects
    # ------------------------------------------------------------------

    def _resolve_concept(self, node) -> ConceptExpression | None:
        """
        Named IRI            → AtomicConcept (looked up by IRI)
        owl:Thing            → OWL_THING singleton
        Restriction BNode    → ExistentialConcept(P)  (owl:someValuesFrom owl:Thing only)
        Intersection BNode   → IntersectionConcept(operands)
        Unsupported node     → None  (warning recorded in ontology.warnings)
        """
        if isinstance(node, URIRef):
            if node == OWL.Thing:
                return OWL_THING
            if node == OWL.Nothing:
                return OWL_NOTHING
            iri = str(node)
            return self._concepts_by_iri.get(iri) or AtomicConcept(iri)

        if (node, RDF.type, OWL.Restriction) in self._g:
            return self._resolve_restriction(node)

        intersection_head = self._g.value(node, OWL.intersectionOf)
        if intersection_head is not None:
            return self._resolve_intersection(intersection_head)

        for pred_uri, label in _UNSUPPORTED_CLASS_EXPRS:
            if (node, pred_uri, None) in self._g:
                self._warn(f"unsupported class expression {label} — axiom ignored")
                return None

        self._warn(f"unrecognized blank-node class expression {node!r} — axiom ignored")
        return None

    def _resolve_restriction(self, node) -> ConceptExpression | None:
        """Handle an owl:Restriction blank node; only owl:someValuesFrom owl:Thing is supported."""
        prop_node = self._g.value(node, OWL.onProperty)
        filler = self._g.value(node, OWL.someValuesFrom)
        if filler is not None:
            if filler != OWL.Thing:
                self._warn(
                    f"owl:someValuesFrom with non-owl:Thing filler <{filler}> — restriction ignored"
                )
                return None
            role = self._resolve_role(prop_node)
            if role is None:
                return None
            if isinstance(role, InverseRole):
                return InverseExistentialConcept(role.role)
            return ExistentialConcept(role)
        for pred_uri, label in _UNSUPPORTED_RESTRICTIONS:
            if (node, pred_uri, None) in self._g:
                self._warn(f"unsupported OWL restriction {label} — axiom containing it ignored")
                return None
        self._warn("unsupported owl:Restriction (no recognized filler predicate) — axiom ignored")
        return None

    def _resolve_intersection(self, list_head) -> ConceptExpression | None:
        """Handle an owl:intersectionOf list; requires at least 2 resolvable operands."""
        operands = tuple(
            op
            for op in (self._resolve_concept(m) for m in self._rdf_list(list_head))
            if op is not None
        )
        if len(operands) < 2:
            self._warn("owl:intersectionOf with fewer than 2 resolvable operands — axiom ignored")
            return None
        return IntersectionConcept(operands)

    def _resolve_role(self, node) -> AtomicRole | InverseRole | None:
        if isinstance(node, BNode):
            # Support [owl:inverseOf :P] as an inline inverse-role expression.
            inverse_of = self._g.value(node, OWL.inverseOf)
            if inverse_of is not None:
                inner = self._roles_by_iri.get(str(inverse_of)) or AtomicRole(str(inverse_of))
                return InverseRole(inner)
            self._warn("anonymous (blank-node) role expression — axiom ignored")
            return None
        iri = str(node)
        return self._roles_by_iri.get(iri) or AtomicRole(iri)

    def _rdf_list(self, head) -> list:
        """Walk an rdf:List and return its items."""
        items = []
        current = head
        while current and current != RDF.nil:
            first = self._g.value(current, RDF.first)
            if first is not None:
                items.append(first)
            current = self._g.value(current, RDF.rest)
        return items

    # ------------------------------------------------------------------
    # Post-parse helpers
    # ------------------------------------------------------------------

    def _deduplicate_axioms(self) -> None:
        seen: set[str] = set()
        deduped = []
        for ax in self._onto.axioms:
            if ax.id not in seen:
                seen.add(ax.id)
                deduped.append(ax)
        self._onto.axioms = deduped

    # ------------------------------------------------------------------
    # Post-parse coverage scan
    # ------------------------------------------------------------------

    def _scan_unsupported(self) -> None:
        """
        Warn about OWL/RDFS predicates and types that carry axiom semantics
        but are not handled by any collection method.  These were silently
        skipped; this scan makes the omission explicit.
        """
        for type_uri, label in _UNSUPPORTED_PROP_TYPES:
            for s in self._g.subjects(RDF.type, type_uri):
                if not isinstance(s, BNode):
                    self._warn(
                        f"unsupported property characteristic {label} on "
                        f"<{_local_name(str(s))}> — axioms involving this property may be incomplete"
                    )

        for pred_uri, label in _UNSUPPORTED_AXIOM_PREDS:
            seen: set[str] = set()
            for s in self._g.subjects(pred_uri, None):
                key = str(s)
                if key not in seen:
                    seen.add(key)
                    subject_repr = _local_name(key) if isinstance(s, URIRef) else "anonymous"
                    self._warn(
                        f"unsupported axiom predicate {label} on "
                        f"<{subject_repr}> — axiom ignored"
                    )

        for type_uri, label in _UNSUPPORTED_META_TYPES:
            for _ in self._g.subjects(RDF.type, type_uri):
                self._warn(f"unsupported axiom type {label} — axiom ignored")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_owl(path: str) -> Ontology:
    """Parse an OWL Turtle file and return a normalised Ontology."""
    g = Graph()
    g.parse(path, format="turtle")
    return _OWLBuilder(g).build()
