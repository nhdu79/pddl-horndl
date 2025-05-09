#!/usr/bin/env python

import argparse
from planning.domain import Domain
from planning.problem import Problem
from planning.logic import *
from utils.functions import parse_name


SUPPORTED_FEATURES = [
    ":strips",
    ":typing",
    ":negative-preconditions",
    ":disjunctive-preconditions",
    ":equality",
    ":existential-preconditions",
    ":universal-preconditions",
    ":quantified-preconditions",
    ":existential-preconditions",
    ":universal-preconditions",
    ":conditional-effects",
    ":fluents",
    ":adl",
    ":action-costs",
    ":derived-predicates",
    ":constraints",
    ":preferences",
]

def simplify(cond):
    return cond.push_negation_inwards().simplified()

def parse_variable(tokens):
    assert tokens.get() != '-' and tokens.get() != ')'
    return tokens.pop()

def parse_typed_list(tokens, element_parser = parse_variable):
    result = []
    tklist = []
    while True:
        if tokens.get() == '-':
            tokens.pop()
            result.append(TypedList(tklist, tokens.pop()))
            assert len(tklist) > 0
            assert result[-1].type != '('
            tklist = []
        elif tokens.get() == ')':
            tokens.pop()
            break
        else:
            tklist.append(element_parser(tokens))
    if len(tklist) > 0:
        result.append(TypedList(tklist))
    return result

def parse_function(tokens):
    assert tokens.get() == '('
    tokens.pop()
    return Function(tokens.pop(), parse_typed_list(tokens))


def parse_f_expression(tokens):
    t = tokens.get()
    if t == ')':
        return None
    tokens.pop()
    if t == '(':
        op = tokens.pop()
        if op in FExpression.OPERATORS:
            elements = []
            f = parse_f_expression(tokens)
            while f != None:
                elements.append(f)
                f = parse_f_expression(tokens)
            assert tokens.get() == ')'
            tokens.pop()
            return FExpression(op, elements)
        else:
            f = Fact(op)
            t = tokens.pop()
            while t != ')':
                f.parameters.append(t)
                t = tokens.pop()
            return f
    else:
        return SimpleFExpression(t)


def parse_cq_condition(tokens, t = None):
    if t is None:
        t = tokens.get()
        if t == ')':
            return None
        assert t == '('
        tokens.pop()
        t = tokens.pop()
    kw = t.lower()
    if kw == 'and':
        elements = []
        while True:
            elements.append(parse_cq_condition(tokens))
            if elements[-1] is None:
                elements.pop(-1)
                break
        assert tokens.get() == ')'
        tokens.pop()
        return And(elements)
    elif kw == 'exists':
        assert tokens.get() == '('
        tokens.pop()
        vars = parse_typed_list(tokens)
        ucq = parse_cq_condition(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return Exists(vars, ucq)
    elif kw == '=':
        left = parse_f_expression(tokens)
        right = parse_f_expression(tokens)
        assert  tokens.get() == ')'
        tokens.pop()
        return Comparison(kw, left, right)
    else:
        f = Fact(t)
        t = tokens.pop()
        while t != ')':
            f.parameters.append(t)
            t = tokens.pop()
        assert len(f.parameters) <= 2
        return f


def parse_ucq_condition(tokens):
    t = tokens.get()
    if t == ')':
        return None
    tokens.pop()
    assert t == '('
    t = tokens.pop()
    kw = t.lower()
    if kw == 'or':
        elements = []
        while True:
            elements.append(parse_ucq_condition(tokens))
            if elements[-1] is None:
                elements.pop(-1)
                break
        assert tokens.get() == ')'
        tokens.pop()
        return Or(elements)
    return parse_cq_condition(tokens, t)


def parse_preference_condition(tokens, condition_parser):
    t = tokens.get()
    if t == ')':
        return None
    assert t == '('
    kw = tokens.get(1).lower()
    if kw == 'preference':
        name = tokens.pop(2)
        cond = condition_parser(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return Preference(name, cond)
    elif kw == 'and':
        tokens.pop(1)
        elements = []
        gd = parse_preference_condition(tokens, condition_parser)
        while gd != None:
            elements.append(gd)
            gd = parse_preference_condition(tokens, condition_parser)
        t = tokens.pop()
        assert t == ')'
        return And(elements)
    elif kw == 'forall':
        t = tokens.pop(2)
        assert t == '('
        params = parse_typed_list(tokens)
        gd = parse_preference_condition(tokens, condition_parser)
        assert gd != None
        assert tokens.pop() == ')'
        return Forall(params, gd)
    else:
        return condition_parser(tokens)


def parse_temporal_condition(tokens):
    t = tokens.get()
    if t == ')':
        return None
    assert t == '('
    kw = tokens.get(1).lower()
    if not kw in UnaryTemporalOperator.OPERATORS and not kw in BinaryTemporalOperator.OPERATORS:
        return parse_condition(tokens)
    tokens.pop(1)
    if kw in UnaryTemporalOperator.OPERATORS:
        cond = parse_condition(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return UnaryTemporalOperator(kw, cond)
    else:
        left = parse_condition(tokens)
        right = parse_condition(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return BinaryTemporalOperator(kw, left, right)


def parse_condition(tokens):
    t = tokens.get()
    if t == ')':
        return None
    assert t == '('
    tokens.pop()
    t = tokens.pop()
    kw = t.lower()
    if kw == 'and' or kw == 'or':
        elements = []
        gd = parse_condition(tokens)
        while gd != None:
            elements.append(gd)
            gd = parse_condition(tokens)
        t = tokens.pop()
        assert t == ')'
        if kw == 'and':
            return And(elements)
        else:
            return Or(elements)
    elif kw == 'not':
        gd = parse_condition(tokens)
        assert gd != None
        assert tokens.pop() == ')'
        return Not(gd)
    elif kw == 'imply':
        x = parse_condition(tokens)
        assert x != None
        y = parse_condition(tokens)
        assert y != None
        assert tokens.pop() == ')'
        return Or([Not(x), y])
    elif kw == 'exists' or kw == 'forall':
        t = tokens.pop()
        assert t == '('
        params = parse_typed_list(tokens)
        gd = parse_condition(tokens)
        assert gd != None
        assert tokens.pop() == ')'
        if kw == 'exists':
            return Exists(params, gd)
        else:
            return Forall(params, gd)
    elif kw in Comparison.OPERATORS:
        left = parse_f_expression(tokens)
        right = parse_f_expression(tokens)
        assert  tokens.get() == ')'
        tokens.pop()
        return Comparison(kw, left, right)
    elif kw == 'mko':
        ucq = parse_ucq_condition(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        if isinstance(ucq, Comparison):
            return ucq
        return MinimalKnowledgeOperator(ucq)
    elif kw == 'mko-eq':
        x = tokens.pop()
        y = tokens.pop()
        assert tokens.get() == ')'
        tokens.pop()
        comp = Comparison('=', SimpleFExpression(x), SimpleFExpression(y))
        return MinimalKnowledgeOperator(comp)
    elif kw == 'neq':
        x = SimpleFExpression(tokens.pop())
        y = SimpleFExpression(tokens.pop())
        assert tokens.get() == ')'
        tokens.pop()
        comp = Comparison('=', x, y)
        return Not(comp)
    else:
        f = Fact(t)
        t = tokens.pop()
        while t != ')':
            f.parameters.append(t)
            t = tokens.pop()
        return f


def parse_p_effect(tokens, t = None):
    if t is None:
        t = tokens.get()
        if t == ')':
            return None
        assert t == "("
        tokens.pop()
        t = tokens.pop()
    kw = t.lower()
    assert kw != ')'
    if kw == 'and':
        inner = []
        e = parse_p_effect(tokens)
        while e != None:
            inner.append(e)
            e = parse_p_effect(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return ConjunctiveEffect(inner)
    elif kw in AssignEffect.OPERATORS:
        if tokens.get() == '(':
            tokens.pop()
            head = Fact(tokens.pop())
            t = tokens.pop()
            while t != ')':
                head.parameters.append(t)
                t = tokens.pop()
        else:
            head = tokens.pop()
        expr = parse_f_expression(tokens)
        assert tokens.get() == ')'
        tokens.pop()
        return AssignEffect(kw, head, expr)
    else:
        neg = False
        if kw == 'not':
            neg = True
            t = tokens.pop()
            assert t == '('
            t = tokens.pop()
        f = Fact(t)
        t = tokens.pop()
        while t != ')':
            f.parameters.append(t)
            t = tokens.pop()
        if neg:
            t = tokens.pop()
            assert t == ')'
            return DelEffect(f)
        return AddEffect(f)


def parse_c_effect(tokens):
    t = tokens.get()
    if t == ')':
        return None
    assert t == "("
    tokens.pop()
    t = tokens.pop()
    kw = t.lower()
    if kw == ')':
        return None
    elif kw == 'and':
        inner = []
        e = parse_c_effect(tokens)
        while e != None:
            inner.append(e)
            e = parse_c_effect(tokens)
        tokens.pop()
        return ConjunctiveEffect(inner)
    elif kw == 'forall':
        t = tokens.pop()
        assert t == '('
        vars = parse_typed_list(tokens)
        r = ForallEffect(vars, parse_c_effect(tokens))
        tokens.pop()
        return r
    elif kw == 'when':
        r = ConditionalEffect(simplify(parse_condition(tokens)), parse_c_effect(tokens))
        tokens.pop()
        return r
    else:
        return parse_p_effect(tokens, t)


def parse_effect(tokens):
    return parse_c_effect(tokens)


def parse_domain(content, preserve_predicate_names=False):
    result = Domain()
    result.actions = []
    result.derived_predicates = []
    tokens = TokenList(content)
    tokens.skip('define', 'domain')
    result.name = tokens.pop()
    tokens.close()
    while not tokens.empty():
        t = tokens.pop()
        if t == ')':
            break
        assert t == '('
        t = tokens.pop().lower()
        # print(t)
        if t == ":requirements":
            result.requirements = []
            t = tokens.pop()
            while t != ')':
                assert t in SUPPORTED_FEATURES, "requirement %s is not supported" % t
                result.requirements.append(t)
                t = tokens.pop()
        elif t == ':types':
            result.types = parse_typed_list(tokens)
        elif t == ':constants':
            result.constants = parse_typed_list(tokens)
        elif t == ':predicates':
            result.predicates = []
            while True:
                name = tokens.next()
                if not preserve_predicate_names:
                    name = parse_name(name)
                predicate = Predicate(name, parse_typed_list(tokens))
                result.predicates.append(predicate)
                assert not tokens.empty()
                if tokens.get() == ')':
                    break
            t = tokens.pop()
            assert t == ')'
        elif t == ':functions':
            result.functions = parse_typed_list(tokens, parse_function)
            # print("\n".join([repr(x) for x in result.functions]))
        elif t == ":derived":
            name = tokens.next()
            if not preserve_predicate_names:
                name = parse_name(name)
            p = Predicate(name, parse_typed_list(tokens))
            cond = simplify(parse_condition(tokens))
            assert tokens.get() == ')'
            tokens.pop()
            result.derived_predicates.append(DerivedPredicate(p, cond))
        elif t == ':action':
            action = Action(tokens.pop())
            # print(action.name)
            t = tokens.pop()
            while t != ')':
                if t == ':parameters':
                    t = tokens.pop()
                    assert t == '('
                    action.parameters = parse_typed_list(tokens)
                    # print(" ".join([str(x) for x in action.parameters]))
                elif t == ':precondition':
                    pre = simplify(parse_preference_condition(tokens, parse_condition))
                    action.precondition = pre
                    # print(repr(action.precondition))
                elif t == ':effect':
                    eff = parse_effect(tokens)
                    action.effect = eff
                    # print(repr(action.effect))
                else:
                    assert False, t
                t = tokens.pop()
            result.actions.append(action)
        else:
            assert False, "Unexpected keyword '%s'" % t
    assert tokens.empty()
    return result


def parse_problem(content):
    tokens = TokenList(content)
    tokens.skip('define', 'problem')
    result = Problem()
    result.initial_state = []
    result.name = tokens.pop()
    tokens.close()
    while not tokens.empty():
        t = tokens.pop()
        if t == ')':
            break
        assert t == '('
        t = tokens.pop().lower()
        if t == ':domain':
            result.domain = tokens.pop()
            assert tokens.get() == ')'
            tokens.pop()
        elif t == ':objects':
            typed_objects = parse_typed_list(tokens)
            grouped_by_type = {}
            for tl in typed_objects:
                if tl.type in grouped_by_type:
                    grouped_by_type[tl.type].extend(tl.elements)
                else:
                    grouped_by_type[tl.type] = tl.elements
            result.objects = [TypedList(elems, typ) for (typ, elems) in grouped_by_type.items()]
        elif t == ':init':
            t = tokens.pop()
            while t != ')':
                assert t == '('
                t = tokens.pop()
                if t == '=':
                    result.initial_state.append(Assignment(parse_f_expression(tokens), parse_f_expression(tokens)))
                    assert tokens.get() == ')'
                    tokens.pop()
                    t = tokens.pop()
                else:
                    f = Fact(t)
                    t = tokens.pop()
                    while t != ')':
                        f.parameters.append(t)
                        t = tokens.pop()
                    t = tokens.pop()
                    result.initial_state.append(f)
        elif t == ":goal":
            result.goal = parse_preference_condition(tokens, parse_condition).simplified()
            assert tokens.get() == ')'
            tokens.pop()
        elif t == ':constraints':
            result.constraints = parse_preference_condition(tokens, parse_temporal_condition).simplified()
            assert tokens.get() == ')'
            tokens.pop()
        elif t == ":metric":
            metric =  tokens.pop().lower()
            expression = parse_f_expression(tokens)
            assert metric in Metric.METRICS
            assert tokens.get() == ')'
            tokens.pop()
            result.metric = Metric(metric, expression)
        else:
            assert False, 'unexpected keyword "%s"' % t
    assert tokens.empty()
    return result


def parse_problem_file(path):
    with open(path) as f:
        return parse_problem(f.read())


def parse_domain_file(path):
    with open(path) as f:
        return parse_domain(f.read())


def parse_files(domain_path, problem_path):
    return parse_domain_file(domain_path), parse_problem_file(problem_path)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("f")
    args = p.parse_args()
    with open(args.f) as f:
        d = parse_problem(f.read())
    print(str(d))
