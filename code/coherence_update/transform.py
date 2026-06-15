from coherence_update.rules.symbols import COMPATIBLE_UPDATE, INCOMPATIBLE_UPDATE
from pddl.datalog import Equality, Negated
from pddl.logic import (
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
