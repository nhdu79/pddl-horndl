import planning.datalog as datalog
import planning.pddl as pddl
from coherence_update.rules.symbols import (
    A_OR_AP_CL,
    ADEL,
    AP_CL,
    APLUS,
    COMPATIBLE_UPDATE,
    DEL,
    DEL_CL,
    INCOMPATIBLE_UPDATE,
    INS,
    INS_CL,
    MIN_X_IN_TAU,
    PRE_INS,
    UPDATING,
)
from owl.expressions import EXISTENTIAL_PREFIX, INVERSE_PREFIX

QUERY_PREDICATE_NAME = "QUERY"
INCONSISTENCY_PREDICATE_NAME = "inconsistent"


def is_primed_predicate_name(name):
    return name.startswith("DATALOG_")


def is_update_predicate_name(name):
    return name == UPDATING or name == INCOMPATIBLE_UPDATE or name == COMPATIBLE_UPDATE


def is_coherence_update_predicate_name(name):
    return (
        name.startswith(INS)
        or name.startswith(DEL)
        or name.startswith(APLUS)
        or name.startswith(ADEL)
        or name.startswith(A_OR_AP_CL)
        or name.startswith(AP_CL)
        or name.startswith(DEL_CL)
        or name.startswith(MIN_X_IN_TAU)
        or name.startswith(PRE_INS)
        or name.startswith(INS_CL)
        or name.startswith(EXISTENTIAL_PREFIX)
        or name.startswith(INVERSE_PREFIX)
        or is_update_predicate_name(name)
    )

def is_non_horn_aux_predicate_name(name):
    return name.startswith("nonHornAux") or name.startswith("nonhornaux")

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


def encodes_inconsistency(head):
    return isinstance(head, datalog.Falsity) or head.name == "nothing"
