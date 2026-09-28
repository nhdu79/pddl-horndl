"""User names at the pipeline boundary: checks and the Clipper spelling map.

All user names (PDDL predicates, OWL concepts/roles) are normalized once with
normalize_user_name() when they enter the pipeline.  This module

* verifies up front that normalization is safe for the given task
  (check_names), i.e. it neither merges distinct names nor produces a name the
  compiler generates itself, and
* maps normalized names back to the exact spelling Clipper expects in queries
  (OntologyNames): Clipper resolves query atoms against the OWL local names
  case-sensitively and silently drops atoms it does not know.
"""

import re
from collections import defaultdict

from compilation.naming import INCONSISTENCY_PREDICATE_NAME
from coherence_update.rules.symbols import ACTION_UPDATE_NAME, UPDATING
from owl.expressions import EXISTENTIAL_PREFIX, INVERSE_EXISTENTIAL_PREFIX
from pddl.logic import (
    AddEffect,
    ConditionalEffect,
    ConjunctiveEffect,
    DelEffect,
    Fact,
    ForallEffect,
)
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF
from utils.helpers import normalize_user_name

_OWL_NS = str(OWL)
_RDF_TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
_ENTITY_TYPES = {1: OWL.Class, 2: OWL.ObjectProperty}
# Namespace for predicates declared only so that Clipper keeps them in queries.
DECLARED_NAMESPACE = "http://pddl-horndl.local/declared#"
# Characters on which Clipper's own name normalization agrees with ours:
# Clipper lowercases and drops "_" and "-", but keeps e.g. "." (which would
# also break the parsing of its output).
_CLIPPER_SAFE = re.compile(r"[A-Za-z0-9_-]+")
_QUERY_LIKE = re.compile(r"query\d+")


class NameClashError(ValueError):
    pass


def _local_name(iri):
    return re.split(r"[#/]", str(iri))[-1]


class OntologyNames:
    """The named concepts and roles of an OWL (Turtle) ontology."""

    def __init__(self, path):
        graph = Graph()
        graph.parse(path, format="turtle")
        self.raw = defaultdict(set)  # normalized name -> raw local names
        self.roles = set()  # normalized role names
        for typ in (OWL.Class, OWL.ObjectProperty):
            for s in graph.subjects(RDF.type, typ):
                if isinstance(s, URIRef) and not str(s).startswith(_OWL_NS):
                    raw = _local_name(s)
                    self.raw[normalize_user_name(raw)].add(raw)
                    if typ == OWL.ObjectProperty:
                        self.roles.add(normalize_user_name(raw))

    def clipper_spelling(self, name):
        """Exact OWL spelling of normalized *name*, or None if not declared."""
        raws = self.raw.get(name)
        return min(raws) if raws else None  # unique once check_names passed


def declare_for_clipper(ontology_path, predicates, out_path):
    """Write a copy of the ontology that also declares *predicates*.

    predicates: {normalized name: arity}.  Arity 1 becomes an owl:Class and
    arity 2 an owl:ObjectProperty, both with the normalized name as local name,
    which is then also the spelling to use in queries.
    """
    with open(ontology_path) as f:
        text = f.read().rstrip()
    lines = ["", "", "### Declared by pddl-horndl: PDDL predicates used in mko queries"]
    for name, arity in sorted(predicates.items()):
        lines.append(f"<{DECLARED_NAMESPACE}{name}> {_RDF_TYPE} <{_ENTITY_TYPES[arity]}> .")
    with open(out_path, "w") as f:
        f.write(text + "\n".join(lines) + "\n")
    return out_path


# ---------------------------------------------------------------------------
# Collecting the raw names of the input task
# ---------------------------------------------------------------------------


def _facts_in_condition(cond, out):
    cond.apply(Fact, lambda f: out.append(f.predicate) or f)


def _facts_in_effect(eff, out):
    if isinstance(eff, (AddEffect, DelEffect)):
        out.append(eff.fact.predicate)
    elif isinstance(eff, ConjunctiveEffect):
        for e in eff.elements:
            _facts_in_effect(e, out)
    elif isinstance(eff, ConditionalEffect):
        _facts_in_condition(eff.condition, out)
        _facts_in_effect(eff.effect, out)
    elif isinstance(eff, ForallEffect):
        _facts_in_effect(eff.effect, out)


def pddl_predicate_names(domain, problem):
    """All predicate names as written in the (not yet normalized) input."""
    names = [p.name for p in domain.predicates or []]
    names += [d.predicate.name for d in domain.derived_predicates or []]
    for d in domain.derived_predicates or []:
        _facts_in_condition(d.condition, names)
    for a in domain.actions or []:
        if a.precondition is not None:
            _facts_in_condition(a.precondition, names)
        if a.effect is not None:
            _facts_in_effect(a.effect, names)
    names += [f.predicate for f in problem.initial_state if isinstance(f, Fact)]
    if problem.goal is not None:
        _facts_in_condition(problem.goal, names)
    return names


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_names(domain, problem, ontology, coherence_update, horn):
    """Raise NameClashError if normalizing the task's names is unsafe.

    Must run on the raw (not yet normalized) domain and problem.
    """
    problems = []
    pddl_raw = defaultdict(set)
    for raw in pddl_predicate_names(domain, problem):
        pddl_raw[normalize_user_name(raw)].add(raw)

    # 1. Distinct names merged by normalization.  PDDL is case-insensitive, so
    #    PDDL spellings may differ in case; OWL names are case-sensitive.
    for name in sorted(set(pddl_raw) | set(ontology.raw)):
        spellings = {s.lower() for s in pddl_raw[name] | ontology.raw[name]}
        if len(spellings) > 1:
            # one representative per case-insensitive spelling
            shown = sorted({s.lower(): s for s in sorted(pddl_raw[name] | ontology.raw[name])}.values())
            problems.append(
                f"{' / '.join(shown)} differ by more than letter case but all "
                f"normalize to '{name}'; use one spelling"
            )
        elif len(ontology.raw[name]) > 1:
            shown = sorted(ontology.raw[name])
            problems.append(
                f"OWL names {' / '.join(shown)} differ only in letter case, which "
                f"PDDL cannot distinguish; rename one of them"
            )

    # 2. OWL names Clipper would normalize differently from us.
    for name, raws in sorted(ontology.raw.items()):
        for raw in sorted(raws):
            if not _CLIPPER_SAFE.fullmatch(raw):
                problems.append(
                    f"OWL name '{raw}' may only contain letters, digits, '_' and '-'"
                )

    # 3. User names equal to names the compiler generates.
    reserved = {INCONSISTENCY_PREDICATE_NAME: "the inconsistency predicate",
                "nothing": "owl:Nothing"}
    if coherence_update:
        reserved[UPDATING] = "the update flag"
    if horn:
        for role in ontology.roles:
            reserved[EXISTENTIAL_PREFIX + role] = f"the generated concept for ∃{role}"
            reserved[INVERSE_EXISTENTIAL_PREFIX + role] = f"the generated concept for ∃{role}⁻"
    for name in sorted(set(pddl_raw) | set(ontology.raw)):
        spelled = sorted(pddl_raw[name] | ontology.raw[name])[0]
        if name in reserved:
            problems.append(f"'{spelled}' is reserved for {reserved[name]}")
        elif _QUERY_LIKE.fullmatch(name):
            problems.append(f"'{spelled}' is reserved for generated query predicates")
    if coherence_update:
        for a in domain.actions or []:
            if a.name.lower() == ACTION_UPDATE_NAME:
                problems.append(f"action name '{a.name}' is reserved for the update action")

    if problems:
        raise NameClashError(
            "Predicate names cannot be compiled safely:\n  - " + "\n  - ".join(problems)
        )
