"""
Concept and role expression types used in the normalised TBox representation.

These mirror the Nemo predicates in t_closure.rls:

  concept(?X), atomic(?X)   →  AtomicConcept
  domOf(!U, P)              →  ExistentialConcept(P)         ∃P.⊤
  rngOf(!U, P)              →  InverseExistentialConcept(P)  ∃P⁻.⊤
  negOf(!U, X)              →  NegatedConcept(X)             ¬X
                               IntersectionConcept(ops)       X₁ ⊓ … ⊓ Xₙ

  role(?P), atomic(?P)      →  AtomicRole
  invOf(!U, P)              →  InverseRole(P)                P⁻
  negOf(!U, P)              →  NegatedRole(P)                ¬P
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from rdflib.namespace import OWL

from utils.functions import parse_name

# ---------------------------------------------------------------------------
# Naming constants — used to build compound expression IDs and importable
# by any module that needs to construct or recognise those names.
# ---------------------------------------------------------------------------

EXISTENTIAL_PREFIX = "exists_"
INVERSE_EXISTENTIAL_PREFIX = "exists_inv_"
INVERSE_PREFIX = "inv_"
NOT_PREFIX = "not_"
AND_SEP = "_and_"


def _local_name(iri: str) -> str:
    """Return the normalised local name of an IRI.

    Extracts the fragment (after #) or last path segment (after /), then
    applies parse_name — the same transformation used by Clipper and Compiler
    so that all three components agree on predicate names.
    """
    for sep in ("#", "/"):
        if sep in iri:
            return parse_name(iri.rsplit(sep, 1)[-1])
    return parse_name(iri)


# ---------------------------------------------------------------------------
# Concept expressions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AtomicConcept:
    """Named (atomic) concept — concept(?X), atomic(?X) in t_closure.rls."""
    iri: str

    @property
    def id(self) -> str:
        return _local_name(self.iri)

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class ExistentialConcept:
    """∃P.⊤ — domain concept of role P; corresponds to domOf nodes in t_closure.rls."""
    role: "AtomicRole"

    @property
    def id(self) -> str:
        return f"{EXISTENTIAL_PREFIX}{self.role.id}"

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class InverseExistentialConcept:
    """∃P⁻.⊤ — range concept of role P; corresponds to rngOf nodes in t_closure.rls."""
    role: "AtomicRole"

    @property
    def id(self) -> str:
        return f"{INVERSE_EXISTENTIAL_PREFIX}{self.role.id}"

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class NegatedConcept:
    """¬X — negation of any concept expression; corresponds to negOf nodes in t_closure.rls."""
    concept: "ConceptExpression"

    @property
    def id(self) -> str:
        return f"{NOT_PREFIX}{self.concept.id}"

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class IntersectionConcept:
    """X₁ ⊓ … ⊓ Xₙ — conjunction of concepts (Horn DL-Lite); from owl:intersectionOf."""
    operands: tuple  # tuple[ConceptExpression, ...]

    @property
    def id(self) -> str:
        return AND_SEP.join(o.id for o in self.operands)

    def __str__(self) -> str:
        return self.id


ConceptExpression = Union[
    AtomicConcept,
    ExistentialConcept,
    InverseExistentialConcept,
    NegatedConcept,
    IntersectionConcept,
]

OWL_THING = AtomicConcept(str(OWL.Thing))
OWL_NOTHING = AtomicConcept(str(OWL.Nothing))


# ---------------------------------------------------------------------------
# Role expressions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AtomicRole:
    """Named (atomic) role — role(?P), atomic(?P) in t_closure.rls."""
    iri: str

    @property
    def id(self) -> str:
        return _local_name(self.iri)

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class InverseRole:
    """P⁻ — inverse of a role; corresponds to invOf nodes in t_closure.rls."""
    role: AtomicRole

    @property
    def id(self) -> str:
        return f"{INVERSE_PREFIX}{self.role.id}"

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class NegatedRole:
    """¬P — negation of a role; corresponds to negOf nodes for roles in t_closure.rls."""
    role: AtomicRole | InverseRole

    @property
    def id(self) -> str:
        return f"{NOT_PREFIX}{self.role.id}"

    def __str__(self) -> str:
        return self.id


RoleExpression = Union[AtomicRole, InverseRole, NegatedRole]
