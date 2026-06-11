from coherence_update.rules.symbols import (
    ACTION_UPDATE_NAME,
    ADEL,
    APLUS,
    CLOSURE,
    COMPATIBLE_UPDATE,
    DEL,
    INCOMPATIBLE_UPDATE,
    INS,
    REQUEST,
    UPDATING,
)
from compilation.utils import is_non_horn_aux_predicate_name
from compilation.variant_options import (
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
    UPDATING_PREDICATE_TYPES,
)
from planning.logic import (
    Action,
    AddEffect,
    And,
    ConditionalEffect,
    ConjunctiveEffect,
    DelEffect,
    Fact,
    ForallEffect,
    Not,
    Predicate,
)
from utils.functions import parse_name


def _rewrite_as_update_requests(eff, horn=False):
    if isinstance(eff, AddEffect):
        name = parse_name(eff.fact.predicate)
        pred = APLUS + name if horn else INS + name + REQUEST
        return AddEffect(Fact(pred, eff.fact.parameters))
    if isinstance(eff, DelEffect):
        name = parse_name(eff.fact.predicate)
        # dnh: Skipping boolean predicate for drones benchmark
        if is_non_horn_aux_predicate_name(name):
            return eff
        pred = ADEL + name if horn else DEL + name + REQUEST
        return AddEffect(Fact(pred, eff.fact.parameters))
    if isinstance(eff, ConditionalEffect):
        return ConditionalEffect(
            eff.condition, _rewrite_as_update_requests(eff.effect, horn)
        )
    if isinstance(eff, ConjunctiveEffect):
        return ConjunctiveEffect(
            [_rewrite_as_update_requests(e, horn) for e in eff.elements]
        )
    if isinstance(eff, ForallEffect):
        return ForallEffect(
            eff.parameters, _rewrite_as_update_requests(eff.effect, horn)
        )
    raise ValueError(f"Unknown effect type: {eff!r}")


class Domain:
    def __init__(self):
        self.name = None
        self.requirements = None
        self.types = None
        self.constants = None
        self.predicates = None
        self.functions = None
        self.actions = None
        self.derived_predicates = None

    def __str__(self):
        res = ["(define (domain %s)" % self.name]
        if self.requirements != None:
            res.append("(:requirements %s)" % " ".join(self.requirements))
        if self.types != None:
            res.append("(:types")
            for tl in self.types:
                res.append("  " + str(tl))
            res[-1] += ")"
        if self.constants != None:
            res.append("(:constants")
            for tl in self.constants:
                res.append("  " + str(tl))
            res[-1] += ")"
        if self.predicates != None:
            res.append("(:predicates")
            for p in self.predicates:
                res.append("  " + str(p))
            res[-1] += ")"
        if self.functions != None:
            res.append("(:functions")
            for p in self.functions:
                res.append("  " + str(p))
            res[-1] += ")"
        if self.derived_predicates != None:
            res.extend([str(d) for d in self.derived_predicates])
        if self.actions != None:
            res.extend([str(a) for a in self.actions])
        res.append(")")
        return "\n".join(res)

    def get_type_relation(self):
        type_relation = {}
        if self.types != None:
            for tl in self.types:
                for t in tl.elements:
                    type_relation[t] = tl.type
        closure = {"object": ["object"]}
        for t in type_relation:
            closure[t] = [t]
            st = type_relation[t]
            while True:
                closure[t].append(st)
                if st == "object":
                    break
                assert st in type_relation
                st = type_relation[st]
        return closure

    def get_type_to_constant_map(self, type_relation):
        constants = {t: list() for t in type_relation.keys()}
        constants["object"] = list()
        if self.constants != None:
            for tl in self.constants:
                for super_type in type_relation.get(tl.type, []):
                    constants[super_type].extend(tl.elements)
        return constants

    def adjust_actions(self, up, horn=False):
        """
        Called in Compiler
        """
        for action in self.actions:
            updating = Fact(UPDATING)
            not_updating = Not(updating)
            # nonHornAux actions are auxiliary materialization actions that exist
            # outside the standard planning/update cycle (e.g. they materialise
            # facts derived from non-Horn OWL constructs).  They may fire at any
            # point — including during an update — so both the (not updating) guard
            # and the effect wrapping are intentionally left unchanged for them.
            if is_non_horn_aux_predicate_name(action.name):
                continue
            action.precondition = And([action.precondition, not_updating])
            eff = action.effect
            if up == UPDATING_PREDICATE_TYPES["derived_predicate"]:
                action.effect = _rewrite_as_update_requests(eff, horn=horn)
            elif up == UPDATING_PREDICATE_TYPES["action_effect"]:
                wrapped = _rewrite_as_update_requests(eff, horn=horn)
                add_eff = AddEffect(updating)
                if isinstance(wrapped, ConjunctiveEffect):
                    new_elements = [*wrapped.elements, add_eff]
                    new_eff = ConjunctiveEffect(new_elements)
                else:
                    new_eff = ConjunctiveEffect([add_eff, wrapped])
                action.effect = new_eff

    def construct_update_action(self, up, iupt, horn=False, kept=None):
        """
        Called in compiler.
        kept: list of Predicate objects produced by filter_non_reachable_predicates,
              or None for the Core fragment (no filter).
        """
        action = self._pre_construct_update_action(iupt)
        new_preds = [Predicate(UPDATING, [])]

        if iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"]:
            new_preds.append(Predicate(INCOMPATIBLE_UPDATE, []))
        elif iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            new_preds.append(Predicate(COMPATIBLE_UPDATE, []))

        if horn:
            elements = self._construct_effects_for_update_action_horn(kept)
        else:
            predicates = [
                p for p in self.predicates if not is_non_horn_aux_predicate_name(p.name)
            ]
            elements = self._construct_effects_for_update_action_core(predicates, new_preds)

        if up == UPDATING_PREDICATE_TYPES["action_effect"]:
            elements.append(DelEffect(Fact(UPDATING)))

        effects = ConjunctiveEffect(elements)
        action.effect = effects
        self.actions.append(action)
        existing_names = {p.name for p in self.predicates}
        self.predicates.extend(p for p in new_preds if p.name not in existing_names)

    def _pre_construct_update_action(self, iupt):
        action = Action(ACTION_UPDATE_NAME)
        action.parameters = []

        if iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"]:
            compatible_update = Not(Fact(INCOMPATIBLE_UPDATE))
        elif iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            compatible_update = Fact(COMPATIBLE_UPDATE)

        action.precondition = And([Fact(UPDATING), compatible_update])

        return action

    def _construct_effects_for_update_action_core(self, predicates, new_preds):
        """Build update action effects for the Core fragment."""
        elements = []
        for predicate in predicates:
            p_params = predicate.parameters
            if len(p_params) == 0:
                continue

            f_params = p_params[0].elements

            ins_a = INS + parse_name(predicate.name)
            del_a = DEL + parse_name(predicate.name)
            ins_a_request = ins_a + REQUEST
            del_a_request = del_a + REQUEST
            ins_a_closure = ins_a + CLOSURE

            f = Fact(predicate.name, f_params)
            f_add_cond = Fact(ins_a, f_params)
            f_del_cond = Fact(del_a, f_params)
            f_del_ins_cond = Fact(ins_a_request, f_params)
            f_del_del_cond = Fact(del_a_request, f_params)

            elements.extend([
                ForallEffect(f_params, ConditionalEffect(f_add_cond, AddEffect(f))),
                ForallEffect(f_params, ConditionalEffect(f_del_cond, DelEffect(f))),
                ForallEffect(f_params, ConditionalEffect(f_del_ins_cond, DelEffect(f_del_ins_cond))),
                ForallEffect(f_params, ConditionalEffect(f_del_del_cond, DelEffect(f_del_del_cond))),
            ])
            new_preds.extend([
                Predicate(ins_a, p_params),
                Predicate(del_a, p_params),
                Predicate(ins_a_request, p_params),
                Predicate(del_a_request, p_params),
                Predicate(ins_a_closure, p_params),
            ])

        return elements

    def _construct_effects_for_update_action_horn(self, kept):
        """Build update action effects for the Horn fragment."""
        elements = []
        for pred in kept:
            p_params = pred.parameters
            if len(p_params) == 0:
                continue
            f_params = p_params[0].elements
            f_pred = Fact(pred.name, f_params)

            if pred.name.startswith(INS):
                base_name = pred.name[len(INS):]
                elements.append(
                    ForallEffect(f_params, ConditionalEffect(f_pred, AddEffect(Fact(base_name, f_params))))
                )
            elif pred.name.startswith(DEL):
                base_name = pred.name[len(DEL):]
                elements.append(
                    ForallEffect(f_params, ConditionalEffect(f_pred, DelEffect(Fact(base_name, f_params))))
                )
            elif pred.name.startswith(APLUS) or pred.name.startswith(ADEL):
                elements.append(
                    ForallEffect(f_params, ConditionalEffect(f_pred, DelEffect(f_pred)))
                )

        return elements
