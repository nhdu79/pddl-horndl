from owl import EXISTENTIAL_PREFIX, INVERSE_EXISTENTIAL_PREFIX, parse_owl

TEMPORARY_ONTOLOGY_FILE = "__temp_clipper_ontology.owl"


def construct_ontology_for_clipper(ontology_path: str) -> str:
    """
    Extends the OWL Turtle ontology with subClassOf axioms for every atomic role P:

        existsP    ⊑  ∃P     (fresh atomic concept is a subclass of the existential on P)
        existsinvP ⊑  ∃P⁻    (fresh atomic concept is a subclass of the existential on P⁻)

    The fresh concept names match those registered as PDDL predicates by
    domain._construct_effects_for_update_action() in the Horn update fragment:
    EXISTENTIAL_PREFIX + role.id  and  INVERSE_EXISTENTIAL_PREFIX + role.id.

    With these axioms in place, Clipper includes existsP(x) and existsinvP(x) as
    valid witnesses when rewriting queries for ∃P(x) and ∃P⁻(x) respectively —
    covering the ABox facts maintained by the Horn update action.

    Writes the extended ontology to TEMPORARY_ONTOLOGY_FILE and returns its path.
    """
    ontology = parse_owl(ontology_path)
    with open(ontology_path) as f:
        original_text = f.read()

    extra: list[str] = []
    for role in ontology.atomic_roles.values():
        exists_id = EXISTENTIAL_PREFIX + role.id
        existsinv_id = INVERSE_EXISTENTIAL_PREFIX + role.id

        for sep in ("#", "/"):
            if sep in role.iri:
                base = role.iri.rsplit(sep, 1)[0] + sep
                break
        else:
            base = ""

        exists_iri = base + exists_id
        existsinv_iri = base + existsinv_id

        extra += [
            f"### {exists_id} ⊑ ∃{role.id}",
            f"<{exists_iri}> rdf:type owl:Class ;",
            f"    rdfs:subClassOf [ rdf:type owl:Restriction ; owl:onProperty <{role.iri}> ; owl:someValuesFrom owl:Thing ] .",
            "",
            f"### {existsinv_id} ⊑ ∃{role.id}⁻",
            f"<{existsinv_iri}> rdf:type owl:Class ;",
            f"    rdfs:subClassOf [ rdf:type owl:Restriction ; owl:onProperty [ owl:inverseOf <{role.iri}> ] ; owl:someValuesFrom owl:Thing ] .",
            "",
        ]

    extended = original_text.rstrip() + "\n\n" + "\n".join(extra)
    with open(TEMPORARY_ONTOLOGY_FILE, "w") as f:
        f.write(extended)

    return TEMPORARY_ONTOLOGY_FILE
