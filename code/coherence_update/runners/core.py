import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from coherence_update.classes.inclusion import INCLUSION_TYPES_ORDER
from coherence_update.classes.tbox import TBox
from coherence_update.rules.core.atomic import (
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_concepts,
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_roles,
    build_updating_rules_for_atomic_concepts,
    build_updating_rules_for_atomic_roles,
)
from coherence_update.rules.core.negative import atomicA_closure, roleP_closure
from coherence_update.runners.base import UpdateRunner
from utils.timer import Timer
from coherence_update.update import CoherenceUpdate
from compilation.variant_options import UPDATING_PREDICATE_TYPES
from utils.functions import get_repr, read_predicates, read_unary_predicate

_CODE_DIR = Path(__file__).resolve().parents[2]  # .../code/
TMP_DIR = str(_CODE_DIR.parent / "tmp")
RULES_FILE_NAME = "_update_rules.txt"


class CoreUpdateRunner(UpdateRunner):
    """DL-Lite Core: TBox computed via Nemo + t_closure.rls."""

    def __init__(
        self,
        nmo_path,
        rls_file_path,
        ontology_file_path,
        write_to_file=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.nmo_path = nmo_path
        self.rls_file_path = rls_file_path
        self.ontology_file_path = ontology_file_path
        self.write_to_file = write_to_file
        self.inclusions = None
        self.roles = None
        self.a_atomics = None
        self.functs = None
        self.inv_functs = None
        self._compute_t_closure()

    def run(self):
        tbox = TBox(
            self.inclusions,
            roles=self.roles,
            a_concepts=self.a_atomics,
            functs=self.functs,
            functs_inv=self.inv_functs,
        )
        rules = CoherenceUpdate.run(tbox, self.updating_pred_type)
        if self.write_to_file:
            with open(os.path.join(TMP_DIR, RULES_FILE_NAME), "w") as f:
                for rule in rules:
                    f.write(rule + "\n")
        return rules

    def run_for_missing_predicates(self, missing_concepts, missing_roles):
        rules = []
        rules.extend(
            build_insert_and_delete_rules_and_incompatible_update_for_atomic_concepts(
                missing_concepts
            )
        )
        rules.extend(
            build_insert_and_delete_rules_and_incompatible_update_for_atomic_roles(
                missing_roles
            )
        )
        if self.updating_pred_type == UPDATING_PREDICATE_TYPES["derived_predicate"]:
            rules.extend(build_updating_rules_for_atomic_concepts(missing_concepts))
            rules.extend(build_updating_rules_for_atomic_roles(missing_roles))

        for concept in missing_concepts:
            rules.extend(atomicA_closure(concept, [], [], []))
        for role in missing_roles:
            rules.extend(roleP_closure(role, [], [], [], [], [], [], [], []))
        return rules

    def atomic_predicates(self):
        atomic = self.a_atomics + self.roles + self.functs + self.inv_functs
        return {get_repr(uri) for uri in atomic}

    def predicates_for_domain(self, pddl_predicates):
        return list(pddl_predicates)

    def filter_non_reachable_predicates(
        self, rules: list, actions: list, initial_predicates=None
    ) -> tuple:
        return rules, None

    def _compute_t_closure(self):
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR)

        with open(self.rls_file_path, "r") as f:
            rls_template = f.read()
        rls_with_path = rls_template.replace(
            "::DATA_IMPORT_PATH", self.ontology_file_path
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".rls", delete=False
        ) as tmp_rls:
            tmp_rls.write(rls_with_path)
            tmp_rls_path = tmp_rls.name

        with Timer("tbox_closure", block=True, file=self.timer_output):
            subprocess.call(
                [
                    self.nmo_path,
                    tmp_rls_path,
                    "--export",
                    "all",
                    "--export-dir",
                    TMP_DIR,
                ],
                stderr=subprocess.PIPE,
            )
            try:
                self.inclusions = read_predicates(TMP_DIR, INCLUSION_TYPES_ORDER)
                self.roles = read_unary_predicate(TMP_DIR, "atomicRole")
                self.a_atomics = read_unary_predicate(TMP_DIR, "atomicConcept")
                self.functs = read_unary_predicate(TMP_DIR, "funct")
                self.inv_functs = read_unary_predicate(TMP_DIR, "invFunct")
            except FileNotFoundError as e:
                print(e)

        os.unlink(tmp_rls_path)
        shutil.rmtree(TMP_DIR)
