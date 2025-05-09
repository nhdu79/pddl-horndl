from planning.logic import And, Fact, Not
from planning.domain import UPDATING

class Problem:
    def __init__(self):
        self.name = None
        self.domain = None
        self.objects = None
        self.initial_state = None
        self.goal = None
        self.constraints = None
        self.metric = None

    def __str__(self):
        res = [ "(define (problem %s)" % self.name ]
        res.append("(:domain %s)" % self.domain)
        if self.objects != None:
            res.append("(:objects")
            for tl in self.objects:
                res.append("  " + str(tl))
            res[-1] += ")"
        res.append("(:init")
        res.extend(["       %s" % f for f in self.initial_state])
        res[-1] += ")"
        if self.constraints != None:
            res.append("(:constraints %s)" % self.constraints)
        res.append("(:goal %s)" % str(self.goal))
        if self.metric != None:
            res.append(str(self.metric))
        res.append(")")
        return "\n".join(res)

    def get_type_to_object_map(self, type_relation):
        objects = { t: list() for t in type_relation.keys() }
        if self.objects != None:
            for tl in self.objects:
                for super_type in type_relation.get(tl.type, []):
                    objects[super_type].extend(tl.elements)
        return objects

    def extend_for_coherence_update(self):
        goal = self.goal
        not_updating = Not(Fact(UPDATING))
        new_goal = And([goal, not_updating])
        self.goal = new_goal
