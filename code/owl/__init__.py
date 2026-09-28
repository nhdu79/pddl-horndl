from owl.axioms import (
    ConceptInclusion,
    FunctionalRole,
    InverseFunctionalRole,
    Ontology,
    RoleInclusion,
)
from owl.expressions import (
    AND_SEP,
    EXISTENTIAL_PREFIX,
    INVERSE_EXISTENTIAL_PREFIX,
    INVERSE_PREFIX,
    NOT_PREFIX,
    OWL_NOTHING,
    OWL_THING,
    AtomicConcept,
    AtomicRole,
    ConceptExpression,
    ExistentialConcept,
    IntersectionConcept,
    InverseExistentialConcept,
    InverseRole,
    NegatedConcept,
    NegatedRole,
    RoleExpression,
)
from owl.parser import parse_owl
from owl.saturation import (
    normalize_negative_concept_inclusions,
    saturate_role_inclusions,
)

__all__ = [
    # expression ID constants
    "AND_SEP",
    "EXISTENTIAL_PREFIX",
    "INVERSE_EXISTENTIAL_PREFIX",
    "INVERSE_PREFIX",
    "NOT_PREFIX",
    # expressions
    "AtomicConcept",
    "AtomicRole",
    "ConceptExpression",
    "ExistentialConcept",
    "IntersectionConcept",
    "InverseExistentialConcept",
    "InverseRole",
    "NegatedConcept",
    "NegatedRole",
    "OWL_NOTHING",
    "OWL_THING",
    "RoleExpression",
    # axioms + container
    "ConceptInclusion",
    "FunctionalRole",
    "InverseFunctionalRole",
    "Ontology",
    "RoleInclusion",
    # public functions
    "normalize_negative_concept_inclusions",
    "parse_owl",
    "saturate_role_inclusions",
]
