from collections import defaultdict
import csv
import os
import re

def read_csv(file_name):
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


def get_repr(uri):
    name = uri.split('/')[-1].split('#')[-1]
    # remove all _
    if name.startswith('_:'):
        name = f"blank{name[2:]}"
    else:
        name = parse_name(name)
    return name


def parse_name(name):
    return re.sub(r"[^a-zA-Z0-9]", "", name.lower())
    # return re.sub(r'([a-z])([A-Z])([0-9])', r'\1\2\3', name).lower()


def read_predicates(tmp_dir, pred_types):
    predicates = defaultdict(list)
    for ns in pred_types:
        file_name = os.path.join(tmp_dir, f'{ns}.csv')
        data = read_csv(file_name)
        predicates[ns] = data

    # pprint(predicates)
    return predicates


def read_unary_predicate(tmp_dir, pred_name):
    predicates = []
    file_name = os.path.join(tmp_dir, f'{pred_name}.csv')
    data = read_csv(file_name)
    for row in data:
        predicates.append(row[0])

    return predicates
