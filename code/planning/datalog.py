class __base:
    def __neq__(self, other):
        return not self.__eq__(other)
    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)
    def __ge__(self, other):
        return not self.__lt__(other)
    def __gt__(self, other):
        return not self.__le__(other)

class Falsity(__base):
    def substitute(self, var_map):
        return self
    def free_vars(self):
        return set()
    def __eq__(self, other):
        return isinstance(other, Falsity)
    def __lt__(self, other):
        return other != None and not isinstance(other, Falsity)
    def __hash__(self):
        return hash(self.__class__)

class Negated(__base):
    def __init__(self, element):
        self.element = element
    def free_vars(self):
        return self.element.free_vars()
    def substitute(self, var_map):
        return Negated(self.element.substitute(var_map))
    def __eq__(self, other):
        return isinstance(other, Negated) and other.element == self.element
    def __lt__(self, other):
        if other is None or isinstance(other, Falsity):
            return False
        if not isinstance(other, Negated):
            return True
        return self.element < other.element
    def __hash__(self):
        return hash((self.__class__, self.element))
    def __str__(self):
        if isinstance(self.element, Equality):
            return "%s!=%s" % (self.element.left, self.element.right)
        return "-%s" % self.element

class Atom(__base):
    def __init__(self, name, params):
        self.name = name
        self.parameters = params
    def free_vars(self):
        return set(self.parameters)
    def substitute(self, var_map):
        return Atom(self.name, tuple([var_map.get(p, p) for p in self.parameters]))
    def __str__(self):
        return "%s(%s)" % (self.name, ",".join(self.parameters))
    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name and all([self.parameters[i] == other.parameters[i] for i in range(len(self.parameters))])
    def __lt__(self, other):
        if other is None or isinstance(other, Falsity) or isinstance(other, Negated):
            return False
        if not isinstance(other, Atom):
            return True
        return self.name < other.name or (self.name == other.name and tuple(self.parameters) < tuple(other.parameters))
    def __hash__(self):
        return hash((self.__class__, self.name, tuple(self.parameters)))

class Equality(__base):
    def __init__(self, l, r):
        if l < r:
            self.left = l
            self.right = r
        else:
            self.left = r
            self.right = l
    def free_vars(self):
        return set([self.left, self.right])
    def __eq__(self, other):
        return isinstance(other, Equality) and (other.left == self.left and other.right == self.right)
    def __lt__(self, other):
        if other is None or isinstance(other, Falsity) or isinstance(other, Negated) or isinstance(other, Atom):
            return False
        if not isinstance(other, Equality):
            return True
        return self.left < other.left or (self.left == other.left and self.right < other.right)
    def __hash__(self):
        return hash((self.__class__, self.left, self.right))
    def __str__(self):
        return "%s=%s" % (self.left, self.right)

class Rule(__base):
    def __init__(self):
        self.head = None
        self.tail = None
    def distinguished_vars(self):
        return self.head.free_vars()
    def existential_vars(self):
        dv = self.distinguished_vars()
        tv = set()
        for t in self.tail:
            tv = tv | t.free_vars()
        return tv - dv
    def __eq__(self, other):
        if not isinstance(other, Rule) or self.head != other.head:
            return False
        return tuple(self.tail) == tuple(other.tail)
    def __lt__(self, other):
        if not isinstance(other, Rule):
            return False
        return self.head < other.head or (self.head == other.head and tuple(self.tail) < tuple(other.tail))
    def __hash__(self):
        return hash((self.__class__, self.head, tuple(self.tail)))
    def __str__(self):
        return "%s :- %s." % (self.head, ", ".join([str(x) for x in self.tail]))
    def canonical(self):
        subst = {}
        res = Rule()
        res.head = self.head
        if isinstance(self.head, Atom):
            subst = {
                    x: "X%d" % i for (i, x) in enumerate(self.head.parameters)
            }
            res.head = self.head.substitute(subst)
        n = len(subst)
        free_params = []
        done = []
        que = []
        def restore_original(x):
            negated = False
            atom = x
            if isinstance(x, Negated):
                negated = True
                atom = x.element
            assert isinstance(atom, Atom), "Expected atom, got %r (%s)" % (type(atom), atom)
            if atom.name == "___EQUALS___":
                atom = Equality(*atom.parameters)
                return Negated(atom) if negated else atom
            return x
        def replace_by_auxiliary_atom(x):
            negated = False
            atom = x
            if isinstance(x, Negated):
                negated = True
                atom = x.element
            if isinstance(atom, Atom):
                return x
            assert isinstance(atom, Equality), "Expected =, got %r (%s)" % (type(atom), atom)
            atom = Atom("___EQUALS___", (atom.left, atom.right))
            return Negated(atom) if negated else atom
        for i, atom in enumerate(self.tail):
            neg = False
            atom = replace_by_auxiliary_atom(atom)
            if isinstance(atom, Negated):
                neg = True
                atom = atom.element
            assert isinstance(atom, Atom), "Expected atom, got %r (%s)" % (type(atom), atom)
            params = []
            fp = {}
            for j, x in enumerate(atom.parameters):
                if x.startswith("'") or x.startswith("\""):
                    params.append(x)
                elif x in subst:
                    params.append(subst[x])
                else:
                    params.append('')
                    fp[x] = j
            if len(fp) == 0:
                done.append((neg, atom.name, tuple(params)))
            else:
                que.append((neg, atom.name, tuple(params), len(free_params)))
                free_params.append(fp)
        n = 0
        que = sorted(que)
        while len(que) > 0:
            (neg, name, params, k) = que[0]
            for old in free_params[k].keys():
                break
            new = "Y%d" % n
            n += 1
            i = 0
            while i < len(que):
                (neg, name, params, k) = que[i]
                idx = free_params[k].get(old, None)
                if idx == None:
                    i += 1
                    continue
                params = list(params)
                params[idx] = new
                del(free_params[k][old])
                if len(free_params[k]) == 0:
                    done.append((neg, name, tuple(params)))
                    que.pop(i)
                else:
                    que[i] = (neg, name, tuple(params), k)
                    i += 1
            que = sorted(que)
        atom = lambda neg, name, params: \
                Negated(Atom(name, params)) if neg \
                else Atom(name, params)
        res.tail = [ restore_original(atom(*args)) for args in sorted(done) ]
        return res


def parse_atom(atom):
    assert len(atom) > 0
    if '!=' in atom:
        x, y = atom.split('!=')
        return Negated(Equality(x.strip(), y.strip()))
    elif '=' in atom:
        x, y = atom.split('=')
        return Equality(x.strip(), y.strip())
    else:
        assert '(' in atom and ')' in atom
        name = atom[:atom.find('(')].strip()
        neg = False
        if name.startswith('-'):
            name = name[1:].strip()
            neg = True
        params = [x.strip() for x in atom[atom.find('(')+1:atom.find(')')].split(',')]
        if neg:
            return Negated(Atom(name, params))
        return Atom(name, params)


def parse_rule(rule):
    assert ':-' in rule#  and rule.strip().endswith('.')
    r = Rule()
    # head, tail = rule.strip()[:-1].split(":-")
    head, tail = rule.strip().split(":-")
    head = head.strip()
    tail = tail.strip()
    if len(head) == 0:
        r.head = Falsity()
    else:
        r.head = parse_atom(head)
        assert isinstance(r.head, Atom)
    r.tail = []
    while len(tail) > 0:
        i = tail.find(',')
        j = tail.find(')')
        k = tail.find('(')
        if i < 0 and j < 0:
            r.tail.append(parse_atom(tail))
            break
        if i >= 0 and (i < k or i > j):
            r.tail.append(parse_atom(tail[:i]))
            tail = tail[i+1:].strip()
        else:
            r.tail.append(parse_atom(tail[:j+1]))
            tail = tail[max(i+1,j+2):].strip()
    return r
