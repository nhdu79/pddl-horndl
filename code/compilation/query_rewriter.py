import planning.pddl as pddl
from compilation.utils import query_predicate_name


def _format_cq(query_id, cq):
    """Format a single conjunctive query as a Clipper-compatible Datalog string.

    Returns (formatted_string, is_unparameterized).
    """
    free_vars = list(sorted(cq.free_vars()))
    has_free_vars = bool(free_vars)
    if has_free_vars:
        var_map = {x: f"?{i}" for i, x in enumerate(free_vars)}
        next_idx = len(free_vars)
    else:
        var_map = {}
        next_idx = 1
    if isinstance(cq, pddl.Exists):
        cq = cq.formula
        for x in cq.free_vars():
            if x not in var_map:
                var_map[x] = f"?{next_idx}"
                next_idx += 1
    elements = cq.elements if isinstance(cq, pddl.And) else [cq]
    head = (
        f"{query_predicate_name(query_id)}"
        f"({','.join(var_map[x] for x in free_vars) if has_free_vars else '?0'})"
    )
    tail = [
        f"{f.predicate}({','.join(var_map.get(t, t) for t in f.parameters)})"
        for f in elements
    ]
    return f"{head} <- {', '.join(tail)}", not has_free_vars


def prepare_queries(ucqs):
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
            formatted, is_unparameterized = _format_cq(idx, cq)
            group.append(formatted)
            if is_unparameterized:
                unparameterized.add(idx)
        queries.append(group)
    return queries, unparameterized
