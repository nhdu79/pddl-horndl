import os
import shutil
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod

from coherence_update.classes.inclusion import INCLUSION_TYPES_ORDER
from coherence_update.classes.tbox import TBox
from coherence_update.rules.horn.strata import (
    build_actual_deletion_rules_for_concepts,
    build_actual_deletion_rules_for_roles,
    build_actual_insertion_rules_for_concepts,
    build_actual_insertion_rules_for_roles,
    build_connective_rules_for_propagation_role,
    build_connnective_rules_for_deletion_role,
    build_incompatibility_rules_for_direct_deletion_concepts,
    build_incompatibility_rules_for_direct_deletion_roles,
    build_insertion_closure_rule_for_existential,
    build_trigger_rules_for_deletion_concepts,
    build_trigger_rules_for_deletion_roles,
    build_trigger_rules_for_propagation_concepts,
    build_trigger_rules_for_propagation_roles,
    build_updating_rules_for_concepts,
    build_updating_rules_for_roles,
)
from coherence_update.rules.core.atomic import (
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_concepts,
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_roles,
    build_updating_rules_for_atomic_concepts,
    build_updating_rules_for_atomic_roles,
)
from coherence_update.rules.core.negative import atomicA_closure, roleP_closure
from coherence_update.rules.symbols import COMPATIBLE_UPDATE, INCOMPATIBLE_UPDATE
from coherence_update.update import CoherenceUpdate
from coherence_update.prioritized_update import build_rules_for_pus
from compilation.variant_options import (
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
    UPDATING_PREDICATE_TYPES,
)
from owl import (
    AtomicConcept,
    AtomicRole,
    ExistentialConcept,
    FunctionalRole,
    InverseExistentialConcept,
    InverseFunctionalRole,
    InverseRole,
    OWL_NOTHING,
    OWL_THING,
    normalize_negative_concept_inclusions,
    parse_owl,
    saturate_role_inclusions,
)
from planning.datalog import Equality, Negated
from planning.logic import (
    And,
    Comparison,
    DerivedPredicate,
    Fact,
    Forall,
    Or,
    Predicate,
    SimpleFExpression,
    TypedList,
)
from utils.functions import get_repr, read_predicates, read_unary_predicate

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp")
RULES_FILE_NAME = "_update_rules.txt"


def transform_incompatible_update(rules):
    """
    Convert incompatible_update Datalog rules into a single compatible_update derived predicate.

    Returns (filtered_rules, compatible_update_derived_predicate).
    """
    new_rules = []
    cond = []
    for rule in rules:
        if rule.head.name == INCOMPATIBLE_UPDATE:
            params = set()
            disjunctions = []
            for literal in rule.tail:
                if isinstance(literal, Negated):
                    if isinstance(literal.element, Equality):
                        left_exp = SimpleFExpression(
                            ensure_pddl_parameter(literal.element.left)
                        )
                        right_exp = SimpleFExpression(
                            ensure_pddl_parameter(literal.element.right)
                        )
                        f = Comparison("=", left_exp, right_exp)
                        neg = f
                    else:
                        raise ValueError("Unknown literal type: %r" % literal)
                elif isinstance(literal, Equality):
                    left_exp = SimpleFExpression(ensure_pddl_parameter(literal.left))
                    right_exp = SimpleFExpression(ensure_pddl_parameter(literal.right))
                    f = Comparison("=", left_exp, right_exp)
                    neg = f.negate()
                else:
                    f = Fact(
                        literal.name,
                        [ensure_pddl_parameter(x) for x in [*literal.parameters]],
                    )
                    neg = f.negate()
                params.update(f.free_vars())
                disjunctions.append(neg)
            tl = [TypedList([*params])]
            forall = Forall(tl, Or(disjunctions))
            cond.append(forall)
        else:
            new_rules.append(rule)

    cond = And(cond)
    predicate = Predicate(COMPATIBLE_UPDATE, [])
    compatible_update = DerivedPredicate(predicate, cond)

    return new_rules, compatible_update


def ensure_pddl_parameter(parameter):
    if not parameter.startswith("?"):
        return "?" + parameter
    return parameter


class Timer:
    def __init__(self, message=None, end=",", file="result.csv", block=False):
        self.message = message
        self.block = block
        self._t = None
        self.end = end
        self.file = file

    def __enter__(self):
        self._t = time.time()

    def __exit__(self, *args, **kwargs):
        elapsed = time.time() - self._t
        with open(self.file, "a") as f:
            f.write("%.6f" % elapsed + self.end)


class UpdateRunner(ABC):
    """Abstract base class defining the interface the Compiler depends on."""

    def __init__(
        self,
        updating_pred_type=UPDATING_PREDICATE_TYPES["derived_predicate"],
        incompatible_update_pred_type=INCOMPATIBLE_UPDATE_PREDICATE_TYPES[
            "incompatible_update"
        ],
        timer_output="result.csv",
    ):
        self.updating_pred_type = updating_pred_type
        self.incompatible_update_pred_type = incompatible_update_pred_type
        self.timer_output = timer_output

    @abstractmethod
    def run(self) -> list:
        """Return all Datalog update rules derived from the full TBox."""

    @abstractmethod
    def run_for_missing_predicates(self, missing_concepts, missing_roles) -> list:
        """Return update rules for predicates present in the domain but absent from the ontology."""

    @abstractmethod
    def atomic_predicates(self) -> set:
        """Normalised names of all atomic predicates seen in the ontology."""

    @abstractmethod
    def predicates_for_domain(self, pddl_predicates: list) -> list:
        """
        Returns the unified list of Predicate objects that should have
        ins/del/request/closure machinery registered in the domain:
            pddl_predicates ∪ (ontology predicates not already in pddl_predicates)
        """


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


class HornUpdateRunner(UpdateRunner):
    """DL-Lite Horn: TBox built directly from the OWL ontology via the Python parser."""

    def __init__(self, ontology_file_path, **kwargs):
        super().__init__(**kwargs)
        self.ontology = parse_owl(ontology_file_path)
        saturate_role_inclusions(self.ontology)
        normalize_negative_concept_inclusions(self.ontology)

    def run(self):
        rules = build_rules_for_pus(self.ontology)
        # TODO(dnh): Support different updating_pred_type options
        # if self.updating_pred_type == UPDATING_PREDICATE_TYPES["derived_predicate"]:
        #     rules, compatible_update = transform_incompatible_update(rules)
        #     rules.append(compatible_update)
        return rules

    def run_for_missing_predicates(self, missing_concepts, missing_roles):
        # Wrap plain names as expression objects so the strata functions can use them.
        atomic_role_objs = [AtomicRole(name) for name in missing_roles]
        inv_role_objs = [InverseRole(r) for r in atomic_role_objs]
        all_role_objs = atomic_role_objs + inv_role_objs

        concept_objs = [AtomicConcept(name) for name in missing_concepts]
        ex_concept_objs = [ExistentialConcept(r) for r in atomic_role_objs]
        inv_ex_concept_objs = [InverseExistentialConcept(r) for r in atomic_role_objs]
        all_concept_objs = concept_objs + ex_concept_objs + inv_ex_concept_objs

        rules = []
        # Stratum 1 — trigger propagation (rules 1-3; rule 4 skipped: no TBox)
        rules.extend(build_trigger_rules_for_propagation_concepts(all_concept_objs))
        rules.extend(build_trigger_rules_for_propagation_roles(all_role_objs))
        for role in all_role_objs:
            rules.extend(build_connective_rules_for_propagation_role(role))
        # Stratum 2 — deletion closure (rules 5-7, 16-17; rules 8-15 skipped: no TBox)
        rules.extend(build_trigger_rules_for_deletion_concepts(all_concept_objs))
        rules.extend(build_trigger_rules_for_deletion_roles(all_role_objs))
        for role in all_role_objs:
            rules.extend(build_connnective_rules_for_deletion_role(role))
        rules.extend(build_incompatibility_rules_for_direct_deletion_concepts(all_concept_objs))
        rules.extend(build_incompatibility_rules_for_direct_deletion_roles(all_role_objs))
        rules.extend(build_actual_deletion_rules_for_concepts(all_concept_objs))
        rules.extend(build_actual_deletion_rules_for_roles(all_role_objs))
        # Stratum 3 — insertion closure (rules 20-22; rules 18-19 skipped: no TBox)
        for role in all_role_objs:
            rules.extend(build_insertion_closure_rule_for_existential(role))
        rules.extend(build_actual_insertion_rules_for_concepts(all_concept_objs))
        rules.extend(build_actual_insertion_rules_for_roles(all_role_objs))
        # Updating trigger
        rules.extend(build_updating_rules_for_concepts(all_concept_objs))
        rules.extend(build_updating_rules_for_roles(all_role_objs))
        return rules

    def atomic_predicates(self) -> set:
        concepts = set(self.ontology.atomic_concepts.keys())
        roles = set(self.ontology.atomic_roles.keys())
        functs = {
            ax.role.id
            for ax in self.ontology.axioms
            if isinstance(ax, FunctionalRole)
        }
        inv_functs = {
            ax.role.id
            for ax in self.ontology.axioms
            if isinstance(ax, InverseFunctionalRole)
        }
        return concepts | roles | functs | inv_functs

    def predicates_for_domain(self, pddl_predicates):
        pddl_names = {p.name for p in pddl_predicates}
        extra = []
        for c in self.ontology.atomic_concepts.values():
            if c not in (OWL_THING, OWL_NOTHING) and c.id not in pddl_names:
                extra.append(Predicate(c.id, [TypedList(["?x0"])]))
        for r in self.ontology.atomic_roles.values():
            if r.id not in pddl_names:
                extra.append(Predicate(r.id, [TypedList(["?x0", "?x1"])]))
        return list(pddl_predicates) + extra


def make_update_runner(
    fragment: str,
    ontology_file_path: str,
    updating_pred_type=UPDATING_PREDICATE_TYPES["derived_predicate"],
    incompatible_update_pred_type=INCOMPATIBLE_UPDATE_PREDICATE_TYPES[
        "incompatible_update"
    ],
    timer_output="result.csv",
    nmo_path="",
    rls_file_path="",
    write_to_file=False,
) -> UpdateRunner:
    """Factory that selects the correct UpdateRunner for the given DL-Lite fragment."""
    common = dict(
        updating_pred_type=updating_pred_type,
        incompatible_update_pred_type=incompatible_update_pred_type,
        timer_output=timer_output,
    )
    if fragment == "core":
        return CoreUpdateRunner(
            nmo_path=nmo_path,
            rls_file_path=rls_file_path,
            ontology_file_path=ontology_file_path,
            write_to_file=write_to_file,
            **common,
        )
    if fragment == "horn":
        return HornUpdateRunner(ontology_file_path=ontology_file_path, **common)
    raise ValueError(f"Unknown DL-Lite fragment: {fragment!r}. Use 'core' or 'horn'.")
