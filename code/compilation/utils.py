from coherence_update.rules.symbols import DEL, INCOMPATIBLE_UPDATE, INS, UPDATING, COMPATIBLE_UPDATE
import planning.datalog as datalog
import planning.pddl as pddl

QUERY_PREDICATE_NAME = "QUERY"
INCONSISTENCY_PREDICATE_NAME = "inconsistent"


def is_primed_predicate_name(name):
    return name.startswith("DATALOG_")


def is_update_predicate_name(name):
    return name == UPDATING or name == INCOMPATIBLE_UPDATE or name == COMPATIBLE_UPDATE


def is_coherence_update_predicate_name(name):
    return (
        name.startswith(INS) or name.startswith(DEL) or is_update_predicate_name(name)
    )


def prime_predicate_name(original):
    return "DATALOG_%s" % original.upper()


def unprime_predicate_name(primed_name):
    if primed_name.startswith("DATALOG_"):
        return primed_name[8:].lower()
    return primed_name


def query_predicate_name(idx):
    return QUERY_PREDICATE_NAME + str(idx)


def get_query_id(name):
    if name.lower().startswith(QUERY_PREDICATE_NAME.lower()):
        return int(name[len(QUERY_PREDICATE_NAME) :])
    return None


def get_parameter_list(length, var_name="?x%d"):
    if length == 0:
        return []
    else:
        return [pddl.TypedList([var_name % j for j in range(length)])]


def pddl_predicate(name, num_parameters, primed=False):
    return pddl.Predicate(
        prime_predicate_name(name) if primed else name,
        get_parameter_list(num_parameters),
    )


def encodes_inconsistency(head):
    return isinstance(head, datalog.Falsity) or head.name == "nothing"
