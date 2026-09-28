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
from compilation.naming import is_non_horn_aux_predicate_name
from pddl.logic import (
    Action,
    AddEffect,
    And,
    Comparison,
    ConditionalEffect,
    ConjunctiveEffect,
    DelEffect,
    Exists,
    Fact,
    Falsity,
    Forall,
    ForallEffect,
    Not,
    Or,
    Predicate,
    TypedList,
)
from variant_options import ACTION_EFFECT, DERIVED_PREDICATE


def _rewrite_as_update_requests(eff, horn=False):
    if isinstance(eff, AddEffect):
        name = eff.fact.predicate
        pred = APLUS + name if horn else INS + name + REQUEST
        return AddEffect(Fact(pred, eff.fact.parameters))
    if isinstance(eff, DelEffect):
        name = eff.fact.predicate
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


def adjust_actions(domain, up, horn=False):
    for action in domain.actions:
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
        if up == DERIVED_PREDICATE:
            action.effect = _rewrite_as_update_requests(eff, horn=horn)
        elif up == ACTION_EFFECT:
            wrapped = _rewrite_as_update_requests(eff, horn=horn)
            add_eff = AddEffect(updating)
            if isinstance(wrapped, ConjunctiveEffect):
                new_elements = [*wrapped.elements, add_eff]
                new_eff = ConjunctiveEffect(new_elements)
            else:
                new_eff = ConjunctiveEffect([add_eff, wrapped])
            action.effect = new_eff


def construct_update_action(domain, up, iupt, horn=False, kept=None):
    """
    kept: list of Predicate objects produced by filter_non_reachable_predicates,
          or None for the Core fragment (no filter).
    """
    action = _pre_construct_update_action(iupt)
    new_preds = [Predicate(UPDATING, [])]

    if iupt == INCOMPATIBLE_UPDATE:
        new_preds.append(Predicate(INCOMPATIBLE_UPDATE, []))
    elif iupt == COMPATIBLE_UPDATE:
        new_preds.append(Predicate(COMPATIBLE_UPDATE, []))

    if horn:
        elements = _construct_effects_for_update_action_horn(kept)
    else:
        predicates = [
            p for p in domain.predicates if not is_non_horn_aux_predicate_name(p.name)
        ]
        elements = _construct_effects_for_update_action_core(predicates, new_preds)

    if up == ACTION_EFFECT:
        elements.append(DelEffect(Fact(UPDATING)))

    effects = ConjunctiveEffect(elements)
    action.effect = effects
    domain.actions.append(action)
    existing_names = {p.name for p in domain.predicates}
    domain.predicates.extend(p for p in new_preds if p.name not in existing_names)


def merge_problem_objects_into_constants(domain, problem):
    """Move the problem's objects into the domain's :constants section.

    Clipper rules may mention individuals from the ontology/problem, and the
    compiled derived predicates reference them from inside the domain, so they
    must be declared as domain constants.  Constants already declared in the
    input domain are kept (with their types); problem objects are appended
    unless an object with the same name is already a constant.
    """
    constants = list(domain.constants or [])
    declared = {x for tl in constants for x in tl.elements}
    for tl in problem.objects or []:
        new = [x for x in tl.elements if x not in declared]
        if new:
            constants.append(TypedList(new, tl.type))
            declared.update(new)
    domain.constants = constants or None
    problem.objects = None


# Requirement flag implied by each condition node type.
_CONDITION_REQUIREMENTS = {
    Not: ":negative-preconditions",
    Or: ":disjunctive-preconditions",
    Falsity: ":disjunctive-preconditions",  # printed as "(or )"
    Exists: ":existential-preconditions",
    Forall: ":universal-preconditions",
}
# Flags already covered by an umbrella requirement.
_IMPLIED_REQUIREMENTS = {
    ":adl": {
        ":strips",
        ":typing",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":equality",
        ":quantified-preconditions",
        ":existential-preconditions",
        ":universal-preconditions",
        ":conditional-effects",
    },
    ":quantified-preconditions": {
        ":existential-preconditions",
        ":universal-preconditions",
    },
}


def _condition_requirements(cond, found):
    def visit(node):
        req = _CONDITION_REQUIREMENTS.get(type(node))
        if req:
            found.add(req)
        if isinstance(node, Comparison) and node.op == "=":
            found.add(":equality")
        return False  # never stop: visit every node

    cond.apply(visit, lambda node: node)


def _effect_requirements(eff, found):
    if isinstance(eff, ConjunctiveEffect):
        for e in eff.elements:
            _effect_requirements(e, found)
    elif isinstance(eff, ConditionalEffect):
        found.add(":conditional-effects")
        _condition_requirements(eff.condition, found)
        _effect_requirements(eff.effect, found)
    elif isinstance(eff, ForallEffect):
        found.add(":conditional-effects")
        _effect_requirements(eff.effect, found)


def _has_typed_parameters(typed_lists):
    return any(tl.type is not None for tl in typed_lists or [])


def ensure_requirements(domain, problem=None):
    """Add every :requirements flag the (compiled) domain actually uses.

    The compilation introduces derived predicates, negation, quantifiers and
    conditional effects even when the input domain declares none of them.
    Existing flags are kept in their original order; missing ones are appended
    in a fixed order so the output is deterministic.  The problem's goal is
    scanned too, since requirements are declared in the domain only.
    """
    found = set()
    if domain.derived_predicates:
        found.add(":derived-predicates")
    if (
        domain.types
        or _has_typed_parameters(domain.constants)
        or any(_has_typed_parameters(p.parameters) for p in domain.predicates or [])
        or any(_has_typed_parameters(a.parameters) for a in domain.actions or [])
    ):
        found.add(":typing")
    for deriv in domain.derived_predicates or []:
        _condition_requirements(deriv.condition, found)
    for action in domain.actions or []:
        if action.precondition is not None:
            _condition_requirements(action.precondition, found)
        if action.effect is not None:
            _effect_requirements(action.effect, found)
    if problem is not None and problem.goal is not None:
        _condition_requirements(problem.goal, found)

    requirements = list(domain.requirements or [])
    covered = set(requirements)
    for req in requirements:
        covered |= _IMPLIED_REQUIREMENTS.get(req, set())
    order = [
        ":strips",
        ":typing",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":equality",
        ":existential-preconditions",
        ":universal-preconditions",
        ":conditional-effects",
        ":derived-predicates",
    ]
    requirements += [r for r in order if r in found and r not in covered]
    domain.requirements = requirements or None


def extend_problem_for_coherence_update(problem):
    not_updating = Not(Fact(UPDATING))
    problem.goal = And([problem.goal, not_updating])


def _pre_construct_update_action(iupt):
    action = Action(ACTION_UPDATE_NAME)
    action.parameters = []

    if iupt == INCOMPATIBLE_UPDATE:
        compatible_update = Not(Fact(INCOMPATIBLE_UPDATE))
    elif iupt == COMPATIBLE_UPDATE:
        compatible_update = Fact(COMPATIBLE_UPDATE)

    action.precondition = And([Fact(UPDATING), compatible_update])

    return action


def _construct_effects_for_update_action_core(predicates, new_preds):
    """Build update action effects for the Core fragment."""
    elements = []
    for predicate in predicates:
        p_params = predicate.parameters
        f_params = predicate.variables()
        if not f_params:
            continue

        ins_a = INS + predicate.name
        del_a = DEL + predicate.name
        ins_a_request = ins_a + REQUEST
        del_a_request = del_a + REQUEST
        ins_a_closure = ins_a + CLOSURE

        f = Fact(predicate.name, f_params)
        f_add_cond = Fact(ins_a, f_params)
        f_del_cond = Fact(del_a, f_params)
        f_del_ins_cond = Fact(ins_a_request, f_params)
        f_del_del_cond = Fact(del_a_request, f_params)

        elements.extend(
            [
                ForallEffect(f_params, ConditionalEffect(f_add_cond, AddEffect(f))),
                ForallEffect(f_params, ConditionalEffect(f_del_cond, DelEffect(f))),
                ForallEffect(
                    f_params,
                    ConditionalEffect(f_del_ins_cond, DelEffect(f_del_ins_cond)),
                ),
                ForallEffect(
                    f_params,
                    ConditionalEffect(f_del_del_cond, DelEffect(f_del_del_cond)),
                ),
            ]
        )
        new_preds.extend(
            [
                Predicate(ins_a, p_params),
                Predicate(del_a, p_params),
                Predicate(ins_a_request, p_params),
                Predicate(del_a_request, p_params),
                Predicate(ins_a_closure, p_params),
            ]
        )

    return elements


def _construct_effects_for_update_action_horn(kept):
    """Build update action effects for the Horn fragment."""
    elements = []
    for pred in kept:
        f_params = pred.variables()
        if not f_params:
            continue
        f_pred = Fact(pred.name, f_params)

        if pred.name.startswith(INS):
            base_name = pred.name[len(INS) :]
            elements.append(
                ForallEffect(
                    f_params,
                    ConditionalEffect(f_pred, AddEffect(Fact(base_name, f_params))),
                )
            )
        elif pred.name.startswith(DEL):
            base_name = pred.name[len(DEL) :]
            elements.append(
                ForallEffect(
                    f_params,
                    ConditionalEffect(f_pred, DelEffect(Fact(base_name, f_params))),
                )
            )
        elif pred.name.startswith(APLUS) or pred.name.startswith(ADEL):
            elements.append(
                ForallEffect(f_params, ConditionalEffect(f_pred, DelEffect(f_pred)))
            )

    return elements
