import itertools
import re

LINEW=80
WS = 2

class TraversableBaseClass:
    def __hash__(self):
        return hash(self.__repr__())
    def __eq__(self, other):
        return type(self) == type(other) and self.__repr__() == other.__repr__()
    def __lt__(self, other):
        return repr(self) < repr(other)
    def __le__(self, other):
        return self < other or self == other
    def __gt__(self, other):
        return repr(self) > repr(other)
    def __ge__(self, other):
        return self > other or self == other
    def apply(self, typ, func):
        stop_here = False
        try:
            if any([isinstance(self, t) for t in typ]):
                stop_here = True
        except TypeError:
            pass
        try:
            if isinstance(self, typ):
                stop_here = True
        except TypeError:
            pass
        try:
            if not isinstance(typ, type) and typ(self):
                stop_here = True
        except TypeError:
            pass
        if stop_here:
            return func(self)
        return self._apply_recursively(typ, func)
    def _apply_recursively(self, typ, func):
        return self

class LogicBaseClass(TraversableBaseClass):
    def __str__(self):
        raise NotImplementedError()
    def __repr__(self):
        raise NotImplementedError()
    def simplified(self):
        raise NotImplementedError()
    def negate(self):
        raise NotImplementedError()
    def push_negation_inwards(self):
        raise NotImplementedError()
    def free_vars(self):
        raise NotImplementedError()
    def is_satisfied_by_state(self, objects, state):
        raise NotImplementedError()
    def is_satisfied_by_state_sequence(self, objects, states):
        return self.is_satisfied_by_state(objects, states[-1])
    def instantiate(self, object_assignment):
        return self
    def pretty_str(self, ws = 0):
        res = " " * ws + str(self)
        if len(res) > LINEW:
            return self._pretty_str(ws)
        return res
    def _pretty_str(self, ws = 0):
        return " " * ws + str(self)

class Falsity(LogicBaseClass):
    def __str__(self):
        return "(or )"
    def __repr__(self):
        return "Falsity()"
    def simplified(self):
        return self
    def negate(self):
        return Truth()
    def push_negation_inwards(self):
        return self
    def free_vars(self):
        return set()
    def is_satisfied_by_state(self, objects, state):
        return False

class Truth(LogicBaseClass):
    def __str__(self):
        return "(and )"
    def __repr__(self):
        return "Truth()"
    def simplified(self):
        return self
    def negate(self):
        return Falsity()
    def push_negation_inwards(self):
        return self
    def free_vars(self):
        return set()
    def is_satisfied_by_state(self, objects, state):
        return True

class Fact(LogicBaseClass):
    def __init__(self, name, parameters = None):
        self.predicate = name
        self.parameters = parameters or []
    def __str__(self):
        return "(" + " ".join([self.predicate] + self.parameters) + ")"
    def __repr__(self):
        return "Fact(%s, %r)" % (self.predicate, self.parameters)
    def simplified(self):
        return self
    def negate(self):
        return Not(self)
    def push_negation_inwards(self):
        return self
    def simplified_ucq(self, substitution):
        f = Fact(self.predicate)
        f.parameters = [ (t if not t.startswith('?') else substitution.get(t, t)) for t in self.parameters ]
        return f
    def free_vars(self):
        return set([x for x in self.parameters if x.startswith('?')])
    def is_satisfied_by_state(self, objects, state):
        return self in state
    def instantiate(self, object_assignment):
        instantiated = [ object_assignment.get(v, v) if v.startswith('?') else v for v in self.parameters ]
        return Fact(self.predicate, instantiated)


class Or(LogicBaseClass):
    def __init__(self, elements):
        self.elements = elements
    def _pretty_str(self, ws=0):
        single = " " * ws + str(self)
        if len(single) > LINEW:
            return " " * ws + "(or\n" + "\n".join([x.pretty_str(ws + WS) for x in self.elements]) + ")"
        return single
    def __str__(self):
        return "(or %s)" % " ".join([str(x) for x in self.elements])
    def __repr__(self):
        return "Or(%s)" % ", ".join([repr(x) for x in self.elements])
    def negate(self):
        return And([e.negate() for e in self.elements])
    def simplified(self):
        elements = set([])
        for e in self.elements:
            se = e.simplified()
            if isinstance(se, Falsity):
                continue
            elif isinstance(se, Truth):
                return Truth()
            elif isinstance(se, Or):
                elements = elements | set(se.elements)
            else:
                elements.add(se)
        elements = sorted(elements)
        if len(elements) == 0:
            return Falsity()
        elif len(elements) == 1:
            return elements[0]
        else:
            return Or(elements)
    def push_negation_inwards(self):
        return Or([e.push_negation_inwards() for e in self.elements])
    def simplified_ucq(self, substitution):
        return Or([ e.simplified_ucq(substitution) for e in self.elements ])
    def free_vars(self):
        res = set()
        for e in self.elements:
            res |= e.free_vars()
        return res
    def _apply_recursively(self, typ, func):
        return Or([e.apply(typ, func) for e in self.elements]).simplified()
    def is_satisfied_by_state(self, objects, state):
        for x in self.elements:
            if x.is_satisfied_by_state(objects, state):
                return True
        return False
    def instantiate(self, vars_to_obj):
        return Or([e.instantiate(vars_to_obj) for e in self.elements])

class And(LogicBaseClass):
    def __init__(self, elements):
        self.elements = elements
    def _pretty_str(self, ws=0):
        single = " " * ws + str(self)
        if len(single) > LINEW:
            return " " * ws + "(and\n" + "\n".join([x.pretty_str(ws + WS) for x in self.elements]) + ")"
        return single
    def __str__(self):
        return "(and %s)" % " ".join([str(x) for x in self.elements])
    def __repr__(self):
        return "And(%s)" % ", ".join([repr(x) for x in self.elements])
    def negate(self):
        return Or([e.negate() for e in self.elements])
    def simplified(self):
        elements = set([])
        for e in self.elements:
            se = e.simplified()
            if isinstance(se, Truth):
                continue
            elif isinstance(se, Falsity):
                return Falsity()
            elif isinstance(se, And):
                elements = elements | set(se.elements)
            else:
                elements.add(se)
        elements = sorted(elements)
        if len(elements) == 0:
            return Truth()
        elif len(elements) == 1:
            return elements[0]
        else:
            return And(elements)
    def push_negation_inwards(self):
        return And([e.push_negation_inwards() for e in self.elements])
    def simplified_ucq(self, substitution):
        basic = []
        existential = []
        for e in self.elements:
            e = e.simplified_ucq(substitution)
            if isinstance(e, Exists):
                existential.extend(e.parameters)
                basic.append(e.formula)
            else:
                basic.append(e)
        res = And(basic).simplified()
        if len(existential) > 0:
            res = Exists(existential, res)
        return res
    def free_vars(self):
        res = set()
        for e in self.elements:
            res |= e.free_vars()
        return res
    def _apply_recursively(self, typ, func):
        return And([e.apply(typ, func) for e in self.elements]).simplified()
    def is_satisfied_by_state(self, objects, state):
        for x in self.elements:
            if not x.is_satisfied_by_state(objects, state):
                return False
        return True
    def instantiate(self, vars_to_obj):
        return And([e.instantiate(vars_to_obj) for e in self.elements])

class Not(LogicBaseClass):
    def __init__(self, e):
        self.element = e
    def __str__(self):
        return "(not %s)" % (str(self.element))
    def __repr__(self):
        return "Not(%r)" % (repr(self.element))
    def negate(self):
        return self.element
    def simplified(self):
        neg = self.element.negate()
        if isinstance(neg, Not):
            e = self.element.simplified()
            if isinstance(e, Truth):
                return Falsity()
            elif isinstance(e, Falsity):
                return Truth()
            else:
                return Not(e)
        else:
            return neg.simplified()
    def push_negation_inwards(self):
        return self.element.push_negation_inwards().negate()
    def free_vars(self):
        return self.element.free_vars()
    def _apply_recursively(self, typ, func):
        return Not(self.element.apply(typ, func)).simplified()
    def is_satisfied_by_state(self, objects, state):
        return not self.element.is_satisfied_by_state(objects, state)
    def instantiate(self, vars_to_obj):
        return Not(self.element.instantiate(vars_to_obj))

class Exists(LogicBaseClass):
    def __init__(self, params, f):
        self.parameters = params
        self.formula = f
    def _pretty_str(self, ws=0):
        return " " * ws + "(exists (%s) " % (" ".join([str(x) for x in self.parameters])) + "\n" + self.formula.pretty_str(ws + WS) + ")"
    def __str__(self):
        return "(exists (%s) %s)" % (" ".join([str(x) for x in self.parameters]), str(self.formula))
    def __repr__(self):
        return "Exists(%r, %r)" % (self.parameters, self.formula)
    def negate(self):
        return Forall(self.parameters, self.formula.negate())
    def simplified(self):
        f = self.formula.simplified()
        if isinstance(f, Falsity):
            return Falsity()
        elif isinstance(f, Truth):
            return Truth()
        free_vars = f.free_vars()
        new_parameters = []
        for tl in self.parameters:
            new_tl = TypedList([x for x in tl.elements if x in free_vars], tl.type)
            if len(new_tl.elements) > 0:
                new_parameters.append(new_tl)
        if len(new_parameters) == 0:
            return f
        else:
            return Exists(new_parameters, f)
    def push_negation_inwards(self):
        return Exists(self.parameters, self.formula.push_negation_inwards())
    def simplified_ucq(self, substitution):
        i = substitution.num
        for tl in self.parameters:
            for x in tl.elements:
                substitution.add(x, tl.type)
        f = self.formula.simplified_ucq(substitution)
        n = 0
        for tl in self.parameters:
            for x in tl.elements:
                substitution.pop(x)
                n += 1
        if isinstance(f, Exists):
            return Exists(substitution.std_vars(i, n) + f.parameters, f.formula)
        return Exists(substitution.std_vars(i, n), f)
    def free_vars(self):
        myvars = set([x for y in self.parameters for x in y.elements])
        return self.formula.free_vars() - myvars
    def _apply_recursively(self, typ, func):
        return Exists(self.parameters, self.formula.apply(typ, func))
    def instantiate(self, objects):
        my_objects = set()
        for tl in self.parameters:
            my_objects = my_objects | set(tl.elements)
        new_objects = { var_name: obj for (var_name, obj) in objects.items() if not var_name in my_objects }
        return Exists(self.parameters, self.formula.instantiate(new_objects))
    def is_satisfied_by_state(self, objects, state):
        params = [ x for tl in self.parameters for x in tl.elements ]
        obj_list = [ objects[tl.type] for tl in self.parameters for x in tl.elements ]
        for selection in itertools.product(*obj_list):
            ground = self.formula.instantiate({params[i]: selection[i] for i in range(len(params))})
            if ground.is_satisfied_by_state(objects, state):
                return True
        return False

class Forall(LogicBaseClass):
    def __init__(self, params, f):
        self.parameters = params
        self.formula = f
    def _pretty_str(self, ws=0):
        return " " * ws + "(forall (%s) " % (" ".join([str(x) for x in self.parameters])) + "\n" + self.formula.pretty_str(ws + WS) + ")"
    def __str__(self):
        return "(forall (%s) %s)" % (" ".join([str(x) for x in self.parameters]), str(self.formula))
    def __repr__(self):
        return "Forall(%r, %r)" % (self.parameters, self.formula)
    def negate(self):
        return Exists(self.parameters, self.formula.negate())
    def push_negation_inwards(self):
        return Forall(self.parameters, self.formula.push_negation_inwards())
    def simplified(self):
        f = self.formula.simplified()
        if isinstance(f, Falsity):
            return Falsity()
        elif isinstance(f, Truth):
            return Truth()
        free_vars = f.free_vars()
        new_parameters = []
        for tl in self.parameters:
            new_tl = TypedList([x for x in tl.elements if x in free_vars], tl.type)
            if len(new_tl.elements) > 0:
                new_parameters.append(new_tl)
        if len(new_parameters) == 0:
            return f
        else:
            return Forall(new_parameters, f)
    def free_vars(self):
        myvars = set([x for y in self.parameters for x in y.elements])
        return self.formula.free_vars() - myvars
    def _apply_recursively(self, typ, func):
        return Forall(self.parameters, self.formula.apply(typ, func))
    def instantiate(self, objects):
        my_objects = set()
        for tl in self.parameters:
            my_objects = my_objects | set(tl.elements)
        new_objects = { var_name: obj for (var_name, obj) in objects.items() if not var_name in my_objects }
        return Forall(self.parameters, self.formula.instantiate(new_objects))
    def is_satisfied_by_state(self, objects, state):
        params = [ x for tl in self.parameters for x in tl.elements ]
        obj_list = [ objects[tl.type] for tl in self.parameters for x in tl.elements ]
        for selection in itertools.product(*obj_list):
            ground = self.formula.instantiate({params[i]: selection[i] for i in range(len(params))})
            if not ground.is_satisfied_by_state(objects, state):
                return False
        return True

class Preference(LogicBaseClass):
    def __init__(self, name, condition):
        self.name = name
        self.condition = condition
    def __str__(self):
        return "(preference %s %s)" % (self.name, self.condition)
    def __repr__(self):
        return "Preference(%s, %r)" % (self.name, self.condition)
    def push_negation_inwards(self):
        return Preference(self.name, self.condition.push_negation_inwards())
    def simplified(self):
        return Preference(self.name, self.condition.simplified())
    def free_vars(self):
        return self.condition.free_vars()
    def _apply_recursively(self, typ, func):
        return Preference(self.name, self.condition.apply(typ, func))
    def instantiate(self, objects):
        return Preference(self.name, self.condition.instantiate(objects))
    def is_satisfied_by_state(self, objects, state):
        # return self.condition.is_satisfied_by_state(objects, state)
        return True
    def is_satisfied_by_state_sequence(self, objects, state_sequence):
        # return self.condition.is_satisfied_by_state_sequence(objects, state_sequence)
        return True

class TemporalLogicBaseClass(LogicBaseClass):
    def is_satisfied_by_state(self, objects, state):
        raise TypeError('Temporal properties cannot be evaluated on a single state')

class UnaryTemporalOperator(TemporalLogicBaseClass):
    OPERATORS = [ "always", "sometime", "at-most-once", "at-end" ]
    def __init__(self, op, condition):
        self.op = op
        self.condition = condition
        assert self.op in UnaryTemporalOperator.OPERATORS
    def __str__(self):
        return "(%s %s)" % (self.op, self.condition)
    def __repr__(self):
        return "UnaryTemporalOperator(%s, %r)" % (self.op, self.condition)
    def push_negation_inwards(self):
        return self.__class__(self.op, self.condition.push_negation_inwards())
    def simplified(self):
        cond = self.condition.simplified()
        if isinstance(cond, Truth):
            return Truth()
        elif isinstance(cond, Falsity):
            return Truth() if self.op == 'at-most-once' else Falsity()
        return self.__class__(self.op, cond)
    def free_vars(self):
        return self.condition.free_vars()
    def _apply_recursively(self, typ, func):
        return self.__class__(self.op, self.condition.apply(typ, func))
    def instantiate(self, objects):
        return self.__class__(self.op, self.condition.instantiate(objects))
    def is_satisfied_by_state_sequence(self, objects, state_sequence):
        if self.op == 'always':
            for state in state_sequence:
                if not self.condition.is_satisfied_by_state(objects, state):
                    return False
            return True
        elif self.op == 'sometime':
            for state in state_sequence:
                if self.condition.is_satisfied_by_state(objects, state):
                    return True
            return False
        elif self.op == 'at-most-once':
            for i in range(len(state_sequence)):
                if self.condition.is_satisfied_by_state(objects, state_sequence[i]):
                    break
            if i + 1 >= len(state_sequence):
                return True
            j = i + 1
            while j < len(state_sequence) \
                    and self.condition.is_satisfied_by_state(objects, state_sequence[j]):
                j += 1
            if j + 1 >= len(state_sequence):
                return True
            for k in range(j + 1, len(state_sequence)):
                if self.condition.is_satisfied_by_state(objects, state_sequence[k]):
                    return False
            return True
        elif self.op == 'at-end':
            return self.condition.is_satisfied_by_state(objects, state_sequence[-1])
        else:
            assert False, "Unknown temporal operator %s" % self.op

class BinaryTemporalOperator(TemporalLogicBaseClass):
    OPERATORS = [ "sometime-after", "sometime-before" ]
    def __init__(self, op, c0, c1):
        self.op = op
        self.left = c0
        self.right = c1
        assert self.op in BinaryTemporalOperator.OPERATORS
    def __str__(self):
        return "(%s %s %s)" % (self.op, self.left, self.right)
    def __repr__(self):
        return "BinaryTemporalOperator(%s, %r, %r)" % (self.op, self.left, self.right)
    def push_negation_inwards(self):
        return self.__class__(self.op, self.left.push_negation_inwards(), self.right.push_negation_inwards())
    def simplified(self):
        left = self.left.simplified()
        right = self.right.simplified()
        if isinstance(left, Falsity):
            return Truth()
        if isinstance(left, Truth):
            if self.op == 'sometime-before' or isinstance(right, Falsity):
                return Falsity()
            if isinstance(right, Truth):
                return Truth()
            return UnaryTemporalOperator('sometime', right)
        if isinstance(right, Falsity):
            return UnaryTemporalOperator('always', left.negate()).simplified()
        return self.__class__(self.op, left, right)
    def _apply_recursively(self, typ, func):
        return self.__class__(self.op, self.left.apply(typ, func), self.right.apply(typ, func))
    def free_vars(self):
        return self.left.free_vars() | self.right.free_vars()
    def instantiate(self, objects):
        return BinaryTemporalOperator(self.op, self.left.instantiate(objects), self.right.instantiate(objects))
    def is_satisfied_by_state_sequence(self, objects, state_sequence):
        if self.op == 'sometime-after':
            for i in reversed(range(len(state_sequence))):
                state = state_sequence[i]
                if self.right.is_satisfied_by_state(objects, state):
                    return True
                elif self.left.is_satisfied_by_state(objects, state):
                    return False
            return True
        elif self.op == 'sometime-before':
            for i in range(len(state_sequence)):
                state = state_sequence[i]
                if self.left.is_satisfied_by_state(objects, state):
                    return False
                elif self.right.is_satisfied_by_state(objects, state):
                    return True
            return True
        else:
            assert False, "Unknown binary temporal operator %s" % self.op

class Comparison(LogicBaseClass):
    OPERATORS = [ "=", "<", ">", "<=", ">=" ]
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        assert isinstance(left, FExpression) or isinstance(left, SimpleFExpression)
        assert isinstance(right, FExpression) or isinstance(right, SimpleFExpression)
    def __str__(self):
        return "(%s %s %s)" % (self.op, str(self.left), str(self.right))
    def __repr__(self):
        return "Comparison(%s, %r, %r)" % (self.op, self.left, self.right)
    def negate(self):
        if self.op == '=':
            return Not(self)
        if self.op.startswith('<'):
            op = self.op.replace('<', '>')
        else:
            op = self.op.replace('>', '<')
        return Comparison(op, self.left, self.right)
    def push_negation_inwards(self):
        return self
    def simplified(self):
        if self.op == '=':
            if isinstance(self.left, SimpleFExpression) \
                    and isinstance(self.right, SimpleFExpression) \
                    and not self.left.expression.startswith('?') \
                    and not self.right.expression.startswith('?'):
                return Truth() if self.left.expression == self.right.expression else Falsity()
        return self
    def simplified_ucq(self, substitution):
        return Comparison(self.op, substitution.get(self.left, self.left), substitution.get(self.right, self.right))
    def free_vars(self):
        return self.left.free_vars() | self.right.free_vars()
    def _apply_recursively(self, typ, func):
        return Comparison(self.op, self.left.apply(typ, func), self.right.apply(typ, func))
    def is_satisfied_by_state(self, objects, state):
        assert self.op == '='
        return self.left == self.right
    def instantiate(self, vars_to_obj):
        return Comparison(self.op, self.left.instantiate(vars_to_obj), self.right.instantiate(vars_to_obj))

class ConditionalEffect(TraversableBaseClass):
    def __init__(self, condition, effect):
        self.condition = condition
        self.effect = effect
    def __str__(self):
        return "(when %s %s)" % (str(self.condition), str(self.effect))
    def __repr__(self):
        return "When(%r, %r)" % (self.condition, self.effect)
    def _apply_recursively(self, t, f):
        return ConditionalEffect(self.condition, self.effect.apply(t, f))
    def instantiate(self, objects):
        return ConditionalEffect(self.condition.instantiate(objects), self.effect.instantiate(objects))
    def get_effects(self, objects, state):
        if self.condition.is_satisfied_by_state(objects, state):
            return self.effect.get_effects(objects, state)
        return set(), set()
    def get_fluent_predicates(self):
        return self.effect.get_fluent_predicates()

class AssignEffect(TraversableBaseClass):
    OPERATORS = [ 'assign', 'scale-up', 'scale-down', 'increase', 'decrease' ]
    def __init__(self, op, head, expr):
        self.op = op
        self.head = head
        self.expression = expr
    def __str__(self):
        return "(%s %s %s)" % (self.op, self.head, str(self.expression))
    def __repr__(self):
        return "Assign(%s, %s, %s)" % (self.op, self.head, repr(self.expression))
    def _apply_recursively(self, t, f):
        return AssignEffect(self.op, self.head, self.expression.apply(t, f))
    def instantiate(self, objects):
        return AssignEffect(self.op, self.head.instantiate(objects), self.expression.instantiate(objects))
    def get_effects(self, objects, state):
        # TODO IMPLEMENT
        return set(), set()
    def get_fluent_predicates(self):
        return set()

class Assignment(TraversableBaseClass):
    def __init__(self, fhead, expression):
        self.fhead = fhead
        self.expression = expression
    def __str__(self):
        return "(= %s %s)" % (self.fhead, str(self.expression))
    def __repr__(self):
        return "Assignment(%s, %r)" % (self.fhead, self.expression)
    def instantiate(self, objects):
        return Assignment(self.fhead.instantiate(objects), self.expression.instantiate(objects))
    def get_effects(self, objects, state):
        # TODO
        return set(), set()
    def get_fluent_predicates(self):
        return set()

class ConjunctiveEffect(TraversableBaseClass):
    def __init__(self, fs):
        self.elements = fs
    def __str__(self):
        return "(and %s)" % (" ".join([str(e) for e in self.elements]))
    def __repr__(self):
        return "ConjunctiveEffect(%s)" % ", ".join([repr(e) for e in self.elements])
    def _apply_recursively(self, t, f):
        return ConjunctiveEffect([e.apply(t, f) for e in self.elements])
    def instantiate(self, objects):
        return ConjunctiveEffect([e.instantiate(objects) for e in self.elements])
    def get_effects(self, objects, state):
        (adds, deletes) = (set(), set())
        for eff in self.elements:
            (eff_adds, eff_deletes) = eff.get_effects(objects, state)
            adds = adds | eff_adds
            deletes = deletes | eff_deletes
        return (adds, deletes)
    def get_fluent_predicates(self):
        res = set()
        for eff in self.elements:
            res = res | eff.get_fluent_predicates()
        return res

class AddEffect(TraversableBaseClass):
    def __init__(self, f):
        self.fact = f
    def __str__(self):
        return str(self.fact)
    def __repr__(self):
        return "Add(%r)" % self.fact
    def instantiate(self, objects):
        return AddEffect(self.fact.instantiate(objects))
    def get_effects(self, objects, state):
        return set([self.fact]), set()
    def get_fluent_predicates(self):
        return set([self.fact.predicate])

class DelEffect(TraversableBaseClass):
    def __init__(self, f):
        self.fact = f
    def __str__(self):
        return "(not " + str(self.fact) + ")"
    def __repr__(self):
        return "Del(%r)" % self.fact
    def instantiate(self, objects):
        return DelEffect(self.fact.instantiate(objects))
    def get_effects(self, objects, state):
        return set(), set([self.fact])
    def get_fluent_predicates(self):
        return set([self.fact.predicate])

class ForallEffect(TraversableBaseClass):
    def __init__(self, parameters, effect):
        self.parameters = parameters
        self.effect = effect
    def __str__(self):
        return "(forall (%s) %s)" % (" ".join([str(x) for x in self.parameters]), str(self.effect))
    def __repr__(self):
        return "Forall(%r, %r)" % (self.parameters, self.effect)
    def _apply_recursively(self, t, f):
        return ForallEffect(self.parameters, self.effect.apply(t, f))
    def instantiate(self, objects):
        my_objects = set()
        for tl in self.parameters:
            my_objects = my_objects | set(tl.elements)
        new_objects = { var_name: obj for (var_name, obj) in objects.items() if not var_name in my_objects }
        return ForallEffect(self.parameters, self.effect.instantiate(new_objects))
    def get_effects(self, objects, state):
        adds = set()
        dels = set()
        params = [ x for tl in self.parameters for x in tl.elements ]
        obj_list = [ objects[tl.type] for tl in self.parameters for x in tl.elements ]
        for selection in itertools.product(*obj_list):
            ground = self.effect.instantiate({params[i]: selection[i] for i in range(len(params))})
            (a, b) = ground.get_effects(objects, state)
            adds = adds | a
            dels = dels | b
        return (adds, dels)
    def get_fluent_predicates(self):
        return self.effect.get_fluent_predicates()

"""
    TypedList: type is optional; which creates Predicates of same type
"""
class TypedList:
    def __init__(self, elements, typ = "object"):
        self.elements = elements
        self.type = typ
    def __str__(self):
        if len(self.elements) == 0:
            return ""
        x = ""
        if self.type != None:
            x = " - " + self.type
        return " ".join([str(y) for y in self.elements]) + x
    def __repr__(self):
        x = ""
        if self.type != None:
            x = " - " + self.type
        return " ".join([repr(y) for y in self.elements]) + x

class FExpression:
    OPERATORS = [ "+", "-", "*", "/" ]
    def __init__(self, op, elements):
        self.op = op
        self.elements = elements
        assert self.op != '/' or len(self.elements) == 2
    def __str__(self):
        return "(%s %s)" % (self.op, " ".join([str(e) for e in self.elements]))
    def __repr__(self):
        return "FExpression(%s, %s)" % (self.op, " ".join([repr(e) for e in self.elements]))
    def __eq__(self, other):
        return isinstance(other, FExpression) and self.op == other.op and len(self.elements) == len(other.elements) and all([self.elements[i] == other.elements[i] for i in range(len(self.elements))])
    def free_vars(self):
        res = set()
        for e in self.elements:
            res = res | e.free_vars()
        return res
    def apply(self, typ, func):
        if isinstance(self, typ):
            return func(self)
        return FExpression(self.op, [e.apply(typ, func) for e in self.elements])

class SimpleFExpression:
    def __init__(self, x):
        self.expression = x
    def __str__(self):
        return self.expression
    def __repr__(self):
        return "SimpleFExpression(%s)" % self.expression
    def __eq__(self, other):
        return isinstance(other, SimpleFExpression) and self.expression == other.expression
    def free_vars(self):
        return set([self.expression]) if self.expression.startswith('?') else set()
    def apply(self, typ, func):
        stop_here = False
        try:
            if any([isinstance(self, t) for t in typ]):
                stop_here = True
        except TypeError:
            pass
        try:
            if isinstance(self, typ):
                stop_here = True
        except TypeError:
            pass
        try:
            if not isinstance(typ, type) and typ(self):
                stop_here = True
        except TypeError:
            pass
        if stop_here:
            return func(self)
        return self
    def instantiate(self, objects):
        if self.expression.startswith('?'):
            return SimpleFExpression(objects.get(self.expression, self.expression))
        return self

class Substitution:
    def __init__(self):
        self.substitutions = {}
        self.typedlist = []
        self.num = 0
    def get(self, key, d = None):
        x = self.substitutions.get(key, None)
        if x is None:
            return d
        assert isinstance(x, list) and len(x) >= 1
        return x[-1]
    def add(self, key, typ):
        self.typedlist.append((key, typ))
        if key in self.substitutions:
            self.substitutions[key].append("?stdVar%d" % self.num)
        else:
            self.substitutions[key] = ["?stdVar%d" % self.num]
        self.num += 1
    def pop(self, key):
        assert key in self.substitutions
        self.substitutions[key].pop(-1)
        if len(self.substitutions[key]) == 0:
            del(self.substitutions[key])
    def std_vars(self, start, num):
        return [TypedList(["?stdVar%d" % i], self.typedlist[i][1]) for i in range(start, start + num)]
    def vars(self, start):
        return [TypedList([x], y) for (x,  y) in self.typedlist[start:]]

class Predicate:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
    def __str__(self):
        res = [self.name] + [str(x) for x in self.parameters]
        return "(%s)" % " ".join(res)
    def __repr__(self):
        return "%s(%s, %r)" % (self.__class__.__name__, self.name, self.parameters)

class Function(Predicate):
    def __init__(self, *args, **kwargs):
        super(Function, self).__init__(*args, **kwargs)

class MinimalKnowledgeOperator:
    def __init__(self, ucq):
        self.ucq = ucq
    def __str__(self):
        return "(mko %s)" % str(self.ucq)
    def __repr__(self):
        return "MinimalKnowledgeOperator(%r)" % self.ucq
    def __eq__(self, other):
        return isinstance(other, MinimalKnowledgeOperator) and self.ucq == other.ucq
    def __lt__(self, other):
        return repr(self) < repr(other)
    def __hash__(self):
        return hash(str(self))
    def negate(self):
        return Not(self)
    def push_negation_inwards(self):
        return self
    def simplified(self):
        return MinimalKnowledgeOperator(self.ucq.simplified())
    def free_vars(self):
        return self.ucq.free_vars()
    def apply(self, typ, func):
        if isinstance(self, typ):
            return func(self)
        return MinimalKnowledgeOperator(self.ucq.apply(typ, func))

class DerivedPredicate:
    def __init__(self, predicate, condition):
        self.predicate = predicate
        self.condition = condition
    def __str__(self):
        return "(:derived %s\n          %s)" % (str(self.predicate), str(self.condition))
    def __repr__(self):
        return "Derived(%r, %r)" % (self.predicate, self.condition)

class Action:
    def __init__(self, name):
        self.name = name
        self.parameters = []
        self.precondition = None
        self.effect = None
    def __str__(self):
        res = ["(:action %s" % self.name]
        res.append("  :parameters (%s)" % " ".join([str(x) for x in self.parameters]))
        res.append("  :precondition %s" % str(self.precondition))
        res.append("  :effect %s)" % str(self.effect))
        return "\n".join(res)
    def __repr__(self):
        return "Action(%s, %r, %r, %r)" % (self.name, self.parameters, self.precondition, self.effect)
    def get_full_name(self):
        return "(%s %s)" % (self.name, " ".join([str(x) for x in self.parameters]))
    def instantiate(self, objects):
        a = Action(self.name)
        a.parameters = [ TypedList([objects.get(x, x)], None if x in objects else tl.type) for tl in self.parameters for x in tl.elements ]
        a.precondition = self.precondition.instantiate(objects)
        a.effect = self.effect.instantiate(objects)
        return a
    def get_successor_state(self, objects, state):
        assert isinstance(state, set)
        adds, dels = self.effect.get_effects(objects, state)
        return (state - dels) | adds

class Metric:
    METRICS = [ "minimize", "maximize" ]
    def __init__(self, metric, fexpr):
        self.metric = metric
        self.expression = fexpr
    def __str__(self):
        return "(:metric %s %s)" % (self.metric, str(self.expression))
    def __repr__(self):
        return "Metric(%s, %r)" % (self.metric, self.expression)

class TokenList:
    def __init__(self, text):
        lines = text.split("\n")
        for i in range(len(lines)):
            j = lines[i].find(";")
            if j >= 0:
                lines[i] = lines[i][:j]
        t = [re.sub(r'\s+', ' ', '\n'.join(lines))]
        for c in [ '(', ' ', ')' ]:
            tp = []
            for s in t:
                splt = s.split(c)
                for i in range(len(splt) - 1):
                    if len(splt[i].strip()) > 0:
                        tp.append(splt[i].strip())
                    if c != ' ':
                        tp.append(c)
                if len(splt[-1].strip()) > 0:
                    tp.append(splt[-1].strip())
            t = tp
        self.tokens = list(reversed(t))

    def pop(self, i = 0):
        if i < 0 or len(self.tokens) - i <= 0:
            raise IndexError()
        res = self.tokens.pop()
        while i > 0:
            res = self.tokens.pop()
            i = i - 1
        return res

    def get(self, i = 0):
        if i < 0 or len(self.tokens) - i <= 0:
            raise IndexError()
        return self.tokens[-1 - i]

    def matches(self, s):
        return self.get() == s

    def is_open_bracket(self):
        return self.matches('(')

    def is_closed_bracket(self):
        return self.matches(')')

    def consume(self, *args):
        for arg in args:
            try:
                tk = self.pop()
                if arg != tk:
                    raise ValueError("expected '%s' but got '%s'" % (arg, tk))
            except IndexError:
                raise ValueError("expected '%s' but received EOF" % arg)
        return True

    def skip(self, *args):
        x = []
        for arg in args:
            x.append('(')
            x.append(arg)
        return self.consume(*x)

    def next(self):
        self.consume('(')
        return self.pop()

    def close(self, num = 1):
        args = [')' for i in range(num)]
        return self.consume(*args)

    def empty(self):
        return len(self.tokens) == 0

