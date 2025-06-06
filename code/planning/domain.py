from coherence_update.rules.symbols import (
    ACTION_UPDATE_NAME,
    CLOSURE,
    DEL,
    INCOMPATIBLE_UPDATE,
    INS,
    REQUEST,
    UPDATING,
    COMPATIBLE_UPDATE,
)
from planning.logic import (
    Action,
    AddEffect,
    And,
    ConditionalEffect,
    ConjunctiveEffect,
    ForallEffect,
    DelEffect,
    Fact,
    Not,
    Predicate,
)
from utils.functions import parse_name
from compilation.variant_options import (
    UPDATING_PREDICATE_TYPES,
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
)


def wrapper(eff):
    new_eff = None
    if isinstance(eff, AddEffect):
        params = eff.fact.parameters
        predicate = INS + parse_name(eff.fact.predicate) + REQUEST
        new_eff = AddEffect(Fact(predicate, params))
    elif isinstance(eff, DelEffect):
        params = eff.fact.parameters
        predicate = DEL + parse_name(eff.fact.predicate) + REQUEST
        new_eff = AddEffect(Fact(predicate, params))
    elif isinstance(eff, ConditionalEffect):
        new_eff = ConditionalEffect(eff.condition, wrapper(eff.effect))
    elif isinstance(eff, ConjunctiveEffect):
        new_eff = ConjunctiveEffect([wrapper(e) for e in eff.elements])
    else:
        raise ValueError("Unknown effect type: %r" % eff)
    return new_eff


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

    def adjust_actions(self, up):
        """
            Called in Compiler
        """
        for action in self.actions:
            pre = action.precondition
            updating = Fact(UPDATING)
            not_updating = Not(updating)
            new_pre = And([pre, not_updating])
            action.precondition = new_pre
            eff = action.effect
            if up == UPDATING_PREDICATE_TYPES["derived_predicate"]:
                action.effect = wrapper(eff)
            elif up == UPDATING_PREDICATE_TYPES["action_effect"]:
                wrapped = wrapper(eff)
                add_eff = AddEffect(updating)
                if isinstance(wrapped, ConjunctiveEffect):
                    new_elements = [*wrapped.elements, add_eff]
                    new_eff = ConjunctiveEffect(new_elements)
                else:
                    new_eff = ConjunctiveEffect([add_eff, wrapped])
                action.effect = new_eff

    def construct_update_action(self, up, iupt):
        """
            Called in compiler
        """
        action = self._pre_construct_update_action(iupt)
        new_preds = [Predicate(UPDATING, [])]

        if iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"]:
            new_preds.append(Predicate(INCOMPATIBLE_UPDATE, []))
        elif iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            new_preds.append(Predicate(COMPATIBLE_UPDATE, []))

        elements = self._construct_effects_for_update_action(new_preds)

        if up == UPDATING_PREDICATE_TYPES["action_effect"]:
            elements.append(DelEffect(Fact(UPDATING)))

        effects = ConjunctiveEffect(elements)
        action.effect = effects
        self.actions.append(action)
        self.predicates.extend(new_preds)

    def _pre_construct_update_action(self, iupt):
        action = Action(ACTION_UPDATE_NAME)
        action.parameters = []

        if iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"]:
            compatible_update = Not(Fact(INCOMPATIBLE_UPDATE))
        elif iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            compatible_update = Fact(COMPATIBLE_UPDATE)

        action.precondition = And([Fact(UPDATING), compatible_update])

        return action

    def _construct_effects_for_update_action(self, new_preds):
        elements = []
        for predicate in self.predicates:
            # e_addA and e_delA
            p_params = predicate.parameters
            f_params = p_params[0].elements

            ins_a = INS + parse_name(predicate.name)
            del_a = DEL + parse_name(predicate.name)

            f_add_cond = Fact(ins_a, f_params)
            f_del_cond = Fact(del_a, f_params)

            f = Fact(predicate.name, f_params)
            add_eff = AddEffect(f)
            del_eff = DelEffect(f)

            eff_add = ConditionalEffect(f_add_cond, add_eff)
            eff_del = ConditionalEffect(f_del_cond, del_eff)
            forall_eff_add = ForallEffect(f_params, eff_add)
            forall_eff_del = ForallEffect(f_params, eff_del)

            elements.extend([forall_eff_add, forall_eff_del])
            new_preds.append(Predicate(ins_a, p_params))
            new_preds.append(Predicate(del_a, p_params))

            # e_del_ins_a_request and e_del_del_a_request
            ins_a_request = ins_a + REQUEST
            del_a_request = del_a + REQUEST
            ins_a_closure = ins_a + CLOSURE

            f_del_ins_cond = Fact(ins_a_request, f_params)
            f_del_del_cond = Fact(del_a_request, f_params)

            del_ins_eff = DelEffect(f_del_ins_cond)
            del_del_eff = DelEffect(f_del_del_cond)

            eff_del_ins = ConditionalEffect(f_del_ins_cond, del_ins_eff)
            eff_del_del = ConditionalEffect(f_del_del_cond, del_del_eff)
            forall_eff_del_ins = ForallEffect(f_params, eff_del_ins)
            forall_eff_del_del = ForallEffect(f_params, eff_del_del)

            elements.extend([forall_eff_del_ins, forall_eff_del_del])
            new_preds.append(Predicate(ins_a_request, p_params))
            new_preds.append(Predicate(del_a_request, p_params))
            new_preds.append(Predicate(ins_a_closure, p_params))

        return elements
