import pddl.parser as pddl
from compilation.naming import query_predicate_name


def _format_cq(query_id, cq, spelling):
    """Format a single conjunctive query as a Clipper-compatible Datalog string.

    spelling maps each (normalized) predicate name to the name Clipper knows.

    Returns (formatted_string, is_unparameterized).
    """
    free_vars = sorted(cq.free_vars())
    has_free_vars = bool(free_vars)
    if has_free_vars:
        var_map = {x: f"?{i}" for i, x in enumerate(free_vars)}
        next_idx = len(free_vars)
    else:
        var_map = {}
        next_idx = 1
    if isinstance(cq, pddl.Exists):
        # Clipper knows nothing about PDDL types, so a typed quantified
        # variable would silently lose its type restriction in the rewriting.
        typed = [str(tl) for tl in cq.parameters if tl.type not in (None, "object")]
        if typed:
            raise NotImplementedError(
                f"Typed variables inside an mko query are not supported "
                f"({', '.join(typed)} in {cq}); express the type as an ontology "
                f"concept instead."
            )
        cq = cq.formula
        for x in sorted(cq.free_vars()):
            if x not in var_map:
                var_map[x] = f"?{next_idx}"
                next_idx += 1
    elements = cq.elements if isinstance(cq, pddl.And) else [cq]
    head = (
        f"{query_predicate_name(query_id)}"
        f"({','.join(var_map[x] for x in free_vars) if has_free_vars else '?0'})"
    )
    tail = [
        f"{spelling(f.predicate)}({','.join(var_map.get(t, t) for t in f.parameters)})"
        for f in elements
    ]
    return f"{head} <- {', '.join(tail)}", not has_free_vars


def query_atoms(ucqs):
    """{predicate name: arity} of every atom occurring in the UCQs."""
    atoms = {}

    def record(fact):
        atoms[fact.predicate] = len(fact.parameters)
        return fact

    for ucq in ucqs:
        ucq.apply(pddl.Fact, record)
    return atoms


def prepare_queries(ucqs, spelling=lambda name: name):
    """Format PDDL UCQs as Clipper-compatible Datalog query strings.

    Returns:
        queries: per-UCQ list of formatted CQ strings
        unparameterized: set of UCQ indices with no free variables
    """
    queries = []
    unparameterized = set()
    for idx, ucq in enumerate(ucqs):
        cqs = ucq.elements if isinstance(ucq, pddl.Or) else [ucq]
        group = []
        for cq in cqs:
            formatted, is_unparameterized = _format_cq(idx, cq, spelling)
            group.append(formatted)
            if is_unparameterized:
                unparameterized.add(idx)
        queries.append(group)
    return queries, unparameterized
