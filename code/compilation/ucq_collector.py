import pddl.parser as pddl
from compilation.naming import prime_predicate_name, query_predicate_name


class UCQCollector:
    def __init__(self):
        self.ucqs = []
        self.equality = False
        self.queried_predicates = set()

    def __call__(self, mko):
        s = pddl.Substitution()
        ucq = mko.ucq.simplified_ucq(s)
        if isinstance(ucq, pddl.Comparison):
            assert False
        elif isinstance(ucq, pddl.Fact):
            p = ucq.predicate  # already normalized by the Compiler
            self.queried_predicates.add(p)
            return pddl.Fact(prime_predicate_name(p), ucq.parameters)
        else:
            self.ucqs.append(ucq)
            return pddl.Fact(
                prime_predicate_name(query_predicate_name(len(self.ucqs) - 1)),
                list(sorted(ucq.free_vars())),
            )
