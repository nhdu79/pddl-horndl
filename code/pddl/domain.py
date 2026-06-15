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
