import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from coherence_update.inclusion import INCLUSION_TYPES_ORDER
from coherence_update.tbox import TBox
from coherence_update.rules.core.atomic import (
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_concepts,
    build_insert_and_delete_rules_and_incompatible_update_for_atomic_roles,
    build_updating_rules_for_atomic_concepts,
    build_updating_rules_for_atomic_roles,
)
from coherence_update.rules.core.negative import atomicA_closure, roleP_closure
from coherence_update.rules.symbols import (
    CLOSURE,
    COMPATIBLE_UPDATE,
    DEL,
    INCOMPATIBLE_UPDATE,
    INS,
    NOT,
    REQUEST,
    RULE_SEPARATOR,
    UPDATING,
)
from coherence_update.runners.base import UpdateRunner
from utils.timer import Timer
from coherence_update.core_update import CoherenceUpdate
from utils.helpers import get_repr, parse_name, read_predicates, read_unary_predicate
from variant_options import DERIVED_PREDICATE
from pddl.logic import Predicate, TypedList

_CODE_DIR = Path(__file__).resolve().parents[2]  # .../code/
TMP_DIR = str(_CODE_DIR.parent / "tmp")
RULES_FILE_NAME = "_update_rules.txt"

# Core compound names are built as <prefix><base><suffix>, e.g. ins_hasParent_request.
_PREFIXES = (INS, DEL)
_SUFFIXES = (REQUEST, CLOSURE)


def _normalize_pred_name(name: str) -> str:
    """Apply parse_name to the base of a compound predicate name, preserving any
    ins_/del_ prefix and _request/_closure suffix."""
    prefix, body = "", name
    for p in _PREFIXES:
        if body.startswith(p):
            prefix, body = p, body[len(p):]
            break
    suffix = ""
    for s in _SUFFIXES:
        if body.endswith(s):
            suffix, body = s, body[: -len(s)]
            break
    return prefix + parse_name(body) + suffix


def _predicate_from_rule_head(head_str: str) -> Predicate:
    """Build a Predicate from a Datalog rule head like 'PredName(X,Y)', using canonical ?x0,?x1,... params."""
    paren = head_str.find("(")
    if paren < 0:
        return Predicate(head_str.strip(), [])
    name = head_str[:paren].strip()
    params_str = head_str[paren + 1:].rstrip(")").strip()
    if not params_str:
        return Predicate(name, [])
    arity = len(params_str.split(","))
    return Predicate(name, [TypedList([f"?x{i}" for i in range(arity)])])


def _predicate_from_tail_atom(atom_name: str, tail: str) -> Predicate:
    """Build a Predicate for atom_name by locating its parameter list in the tail string."""
    match = re.search(rf"\b{re.escape(atom_name)}\(([^)]*)\)", tail)
    if match:
        params_str = match.group(1).strip()
        if not params_str:
            return Predicate(atom_name, [])
        arity = len(params_str.split(","))
        return Predicate(atom_name, [TypedList([f"?x{i}" for i in range(arity)])])
    return Predicate(atom_name, [TypedList(["?x0"])])


# Compared against already-normalized names, so normalize these too (e.g.
# "incompatible_update" -> "incompatibleupdate" since parse_name strips underscores).
_CONTROL_PREDICATE_NAMES = tuple(
    _normalize_pred_name(n) for n in (UPDATING, INCOMPATIBLE_UPDATE, COMPATIBLE_UPDATE)
)


def _is_base_pred_name(name: str) -> bool:
    """True for bare concept/role names — excludes ins_/del_/_request/_closure
    scaffolding predicates and the nullary update-control predicates, since
    _construct_effects_for_update_action_core rebuilds that scaffolding fresh
    from whatever base predicates are returned as `kept`."""
    if name in _CONTROL_PREDICATE_NAMES:
        return False
    if any(name.startswith(p) for p in _PREFIXES):
        return False
    if any(name.endswith(s) for s in _SUFFIXES):
        return False
    return True


def _collect_effect_predicates(effect, result: dict) -> None:
    """Recursively collect all Fact predicates from an effect tree as Predicate objects."""
    from pddl.logic import AddEffect, ConjunctiveEffect, ConditionalEffect, DelEffect, ForallEffect
    if isinstance(effect, (AddEffect, DelEffect)):
        fact = effect.fact
        if fact.predicate not in result:
            arity = len(fact.parameters)
            params = [TypedList([f"?x{i}" for i in range(arity)])] if arity > 0 else []
            result[fact.predicate] = Predicate(fact.predicate, params)
    elif isinstance(effect, ConjunctiveEffect):
        for e in effect.elements:
            _collect_effect_predicates(e, result)
    elif isinstance(effect, (ConditionalEffect, ForallEffect)):
        _collect_effect_predicates(effect.effect, result)


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
        if self.updating_pred_type == DERIVED_PREDICATE:
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
        # Collect seeds: ins_*_request/del_*_request predicates set by action
        # effects (adjust_actions has already rewritten AddEffect/DelEffect into
        # these request forms by the time this runs), excluding the UPDATE
        # action whose effects are not part of the original planning model.
        seed_predicates: dict = {}
        for action in actions:
            _collect_effect_predicates(action.effect, seed_predicates)

        kept_predicates: dict = {
            _normalize_pred_name(k): Predicate(_normalize_pred_name(k), v.parameters)
            for k, v in seed_predicates.items()
        }

        # Seed from initial state facts: predicates that hold in the initial state
        # may appear in ontology rule bodies, so they must be reachable.
        if initial_predicates:
            for pred in initial_predicates:
                name = _normalize_pred_name(pred.name)
                kept_predicates.setdefault(name, Predicate(name, pred.parameters))

        # An ins_X_request/del_X_request seed implies the base predicate X is also
        # reachable, since the corresponding ins_X/del_X rule tests X(...) directly.
        for name, pred in list(kept_predicates.items()):
            for prefix in _PREFIXES:
                if name.startswith(prefix) and name.endswith(REQUEST):
                    base = name[len(prefix): -len(REQUEST)]
                    kept_predicates.setdefault(base, Predicate(base, pred.parameters))
                    break

        # Reachability fixpoint: fire rules whose positive body atoms are all already
        # in kept_predicates, adding the head and any negated body atoms as new
        # Predicate objects.
        kept_rules = []
        remaining = list(rules)
        while True:
            new_predicates: dict = {}
            new_remaining = []
            for rule_str in remaining:
                sep_idx = rule_str.find(RULE_SEPARATOR)
                if sep_idx < 0:
                    new_remaining.append(rule_str)
                    continue
                tail = rule_str[sep_idx + len(RULE_SEPARATOR):]
                atoms = re.findall(
                    rf"({re.escape(NOT)}?)([A-Za-z][A-Za-z0-9_]*)\(", tail
                )
                positive_names = {
                    _normalize_pred_name(n) for neg, n in atoms if not neg
                }
                if positive_names and positive_names.issubset(kept_predicates):
                    kept_rules.append(rule_str)
                    raw_head = _predicate_from_rule_head(rule_str[:sep_idx].strip())
                    head_name = _normalize_pred_name(raw_head.name)
                    head_pred = Predicate(head_name, raw_head.parameters)
                    new_predicates[head_name] = head_pred
                    # ins_X / del_X (without a _request/_closure suffix) reachability
                    # implies X itself is also needed.
                    for prefix in _PREFIXES:
                        if head_name.startswith(prefix) and not any(
                            head_name.endswith(s) for s in _SUFFIXES
                        ):
                            base = head_name[len(prefix):]
                            new_predicates.setdefault(
                                base, Predicate(base, head_pred.parameters)
                            )
                            break
                    # Negated body atoms must also be declared in the domain.
                    for neg, neg_name in atoms:
                        if neg:
                            norm_neg = _normalize_pred_name(neg_name)
                            if norm_neg not in kept_predicates:
                                new_predicates[norm_neg] = _predicate_from_tail_atom(
                                    norm_neg, tail
                                )
                else:
                    new_remaining.append(rule_str)
            newly_added = set(new_predicates) - set(kept_predicates)
            if not newly_added:
                break
            kept_predicates.update(new_predicates)
            remaining = new_remaining

        # Only bare base concepts/roles are returned: _construct_effects_for_update_action_core
        # rebuilds the ins_/del_/_request/_closure scaffolding fresh from these.
        base_predicates = {
            name: pred
            for name, pred in kept_predicates.items()
            if _is_base_pred_name(name)
        }
        if len(rules) - len(kept_rules) > 0:
            print(f"Filtered {len(rules) - len(kept_rules)} unreachable rules.")
            print(f"Kept {len(base_predicates)} reachable predicates.")

        return kept_rules, list(base_predicates.values())

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
