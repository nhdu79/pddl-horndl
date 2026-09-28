import csv
import os
import re
from collections import defaultdict


def read_csv(file_name):
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def get_repr(uri):
    name = uri.split("/")[-1].split("#")[-1]
    # remove all _
    if name.startswith("_:"):
        name = f"blank{name[2:]}"
    else:
        name = normalize_user_name(name)
    return name


def normalize_user_name(name):
    """Normalize a predicate/concept/role name coming from the user's input.

    Lowercases and drops every character except [a-z0-9].  This mirrors what
    Clipper does to ontology names (it lowercases and strips "_" and "-"), so
    PDDL, OWL and Clipper output agree on one spelling.

    It also reserves a namespace: user names never contain "_" or uppercase
    letters, so every generated name containing "_" (ins_, Ap_, DelCl_, ...)
    or written in uppercase (QUERY<i>, DATALOG_...) is collision-free.  Apply
    this exactly once, when names enter the pipeline, and never to generated
    names: it would mangle them (e.g. PreInsCl_a_sub_b -> PreInsCl_asubb).
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def read_predicates(tmp_dir, pred_types):
    predicates = defaultdict(list)
    for ns in pred_types:
        file_name = os.path.join(tmp_dir, f"{ns}.csv")
        data = read_csv(file_name)
        predicates[ns] = data

    # pprint(predicates)
    return predicates


def read_unary_predicate(tmp_dir, pred_name):
    predicates = []
    file_name = os.path.join(tmp_dir, f"{pred_name}.csv")
    data = read_csv(file_name)
    for row in data:
        predicates.append(row[0])

    return predicates
