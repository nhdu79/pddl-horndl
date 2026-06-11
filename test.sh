#!/bin/sh
PYTHONPATH=code python3 -c "
from owl import parse_owl, saturate_role_inclusions, normalize_negative_concept_inclusions
drones_path='benchmarks/inputs/horn/drones/TTL.owl'
assembly_path='benchmarks/inputs/horn/phone_assembly/assembly.owl'
ontology = parse_owl(assembly_path)
saturate_role_inclusions(ontology)
normalize_negative_concept_inclusions(ontology)
breakpoint()
"
