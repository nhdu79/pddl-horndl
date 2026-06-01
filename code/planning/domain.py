from coherence_update.rules.symbols import (
    ACTION_UPDATE_NAME,
    ADEL,
    APLUS,
    CLOSURE,
    COMPATIBLE_UPDATE,
    DEL,
    INCOMPATIBLE_UPDATE,
    INS,
    INS_CL,
    REQUEST,
    UPDATING,
)
from compilation.utils import is_non_horn_aux_predicate_name
from compilation.variant_options import (
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
    UPDATING_PREDICATE_TYPES,
)
from owl.expressions import (
    EXISTENTIAL_PREFIX,
    INVERSE_EXISTENTIAL_PREFIX,
    INVERSE_PREFIX,
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
    TypedList,
)
from utils.functions import parse_name


def wrapper(eff, horn=False):
    new_eff = None
    if isinstance(eff, AddEffect):
        params = eff.fact.parameters
        name = parse_name(eff.fact.predicate)
        predicate = APLUS + name if horn else INS + name + REQUEST
        new_eff = AddEffect(Fact(predicate, params))
    elif isinstance(eff, DelEffect):
        params = eff.fact.parameters
        name = parse_name(eff.fact.predicate)
        predicate = ADEL + name if horn else DEL + name + REQUEST
        new_eff = AddEffect(Fact(predicate, params))
    elif isinstance(eff, ConditionalEffect):
        new_eff = ConditionalEffect(eff.condition, wrapper(eff.effect, horn=horn))
    elif isinstance(eff, ConjunctiveEffect):
        new_eff = ConjunctiveEffect([wrapper(e, horn=horn) for e in eff.elements])
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
                action.effect = wrapper(eff, horn=horn)
            elif up == UPDATING_PREDICATE_TYPES["action_effect"]:
                wrapped = wrapper(eff, horn=horn)
                add_eff = AddEffect(updating)
                if isinstance(wrapped, ConjunctiveEffect):
                    new_elements = [*wrapped.elements, add_eff]
                    new_eff = ConjunctiveEffect(new_elements)
                else:
                    new_eff = ConjunctiveEffect([add_eff, wrapped])
                action.effect = new_eff

    def construct_update_action(self, up, iupt, horn=False, predicates=None):
        """
        Called in compiler.
        predicates: explicit list of Predicate objects to build update machinery for;
                    defaults to self.predicates (original PDDL domain predicates only).
        """
        action = self._pre_construct_update_action(iupt)
        new_preds = [Predicate(UPDATING, [])]

        if iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["incompatible_update"]:
            new_preds.append(Predicate(INCOMPATIBLE_UPDATE, []))
        elif iupt == INCOMPATIBLE_UPDATE_PREDICATE_TYPES["compatible_update"]:
            new_preds.append(Predicate(COMPATIBLE_UPDATE, []))

        if predicates is None:
            predicates = self.predicates

        # Predicates that come from the ontology but were not declared in the
        # original PDDL domain must be registered in the domain before their
        # update machinery (ins_X / del_X / …) is built.
        existing_names = {p.name for p in self.predicates}
        for p in predicates:
            if p.name not in existing_names:
                new_preds.append(p)
                existing_names.add(p.name)

        elements = self._construct_effects_for_update_action(
            predicates, new_preds, horn=horn
        )

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

    def _construct_effects_for_update_action(self, predicates, new_preds, horn=False):
        elements = []
        for predicate in predicates:
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
            p_name = parse_name(predicate.name)
            if horn:
                ins_a_request = APLUS + p_name
                del_a_request = ADEL + p_name
                ins_a_closure = INS_CL + p_name
            else:
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

            # Horn fragment: for each binary predicate P also generate effects for
            # the three derived expressions: inv_P (binary), exists_P and
            # exists_inv_P (both unary).  Names are built directly (no parse_name)
            # because the underscore is load-bearing in the Horn Datalog rules.
            if horn and len(f_params) == 2:
                derived = [
                    (INVERSE_PREFIX + predicate.name, ["?x0", "?x1"]),
                    (EXISTENTIAL_PREFIX + predicate.name, ["?x0"]),
                    (INVERSE_EXISTENTIAL_PREFIX + predicate.name, ["?x0"]),
                ]
                for derived_name, d_vars in derived:
                    d_params = [TypedList(d_vars)]
                    ins_d = INS + derived_name
                    del_d = DEL + derived_name
                    ins_d_req = APLUS + derived_name
                    del_d_req = ADEL + derived_name

                    f_d = Fact(derived_name, d_vars)
                    f_ins_d = Fact(ins_d, d_vars)
                    f_del_d = Fact(del_d, d_vars)
                    f_ins_d_req = Fact(ins_d_req, d_vars)
                    f_del_d_req = Fact(del_d_req, d_vars)

                    elements.extend(
                        [
                            ForallEffect(
                                d_vars, ConditionalEffect(f_ins_d, AddEffect(f_d))
                            ),
                            ForallEffect(
                                d_vars, ConditionalEffect(f_del_d, DelEffect(f_d))
                            ),
                            ForallEffect(
                                d_vars,
                                ConditionalEffect(f_ins_d_req, DelEffect(f_ins_d_req)),
                            ),
                            ForallEffect(
                                d_vars,
                                ConditionalEffect(f_del_d_req, DelEffect(f_del_d_req)),
                            ),
                        ]
                    )
                    new_preds.extend(
                        [
                            Predicate(derived_name, d_params),
                            Predicate(ins_d, d_params),
                            Predicate(del_d, d_params),
                            Predicate(ins_d_req, d_params),
                            Predicate(del_d_req, d_params),
                            Predicate(INS_CL + derived_name, d_params),
                        ]
                    )

        return elements
