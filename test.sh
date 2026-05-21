#!/bin/sh
PYTHONPATH=code python3 -c "
from owl import parse_owl, saturate_role_inclusions, normalize_negative_concept_inclusions
from coherence_update.prioritized_update import build_rules_for_pus
robot_path='benchmarks/inputs/robotConj/TTL3.owl'
blocks_path='benchmarks/inputs/blocks/blocks.owl'
ontology = parse_owl(robot_path)
saturate_role_inclusions(ontology)
normalize_negative_concept_inclusions(ontology)
rules = build_rules_for_pus(ontology)
import pprint
pprint.pprint(rules)
breakpoint()
"
