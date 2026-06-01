#!/bin/sh
PYTHONPATH=code python3 -c "
from owl import parse_owl, saturate_role_inclusions, normalize_negative_concept_inclusions
from coherence_update.prioritized_update import build_rules_for_pus
drones_path='benchmarks/inputs/horn/drones/TTL.owl'
assembly_path='benchmarks/inputs/horn/assembly/assembly.owl'
ontology = parse_owl(assembly_path)
saturate_role_inclusions(ontology)
normalize_negative_concept_inclusions(ontology)
breakpoint()
rules = build_rules_for_pus(ontology)
import pprint
pprint.pprint(rules)
breakpoint()
"
