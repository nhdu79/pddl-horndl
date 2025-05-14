# Positive inclusion rules (Sec 2.4)
from coherence_update.rules.symbols import (
    CLOSURE,
    DEL,
    END,
    INCOMPATIBLE_UPDATE,
    INS,
    NOT,
    REQUEST,
    RULE_SEPARATOR,
)


def atomicB_in_atomicA(b_repr, a_repr):
    """
    :param b_repr: string
    :param a_repr: string
    :param super_predicates: string[]
    """
    r_del = (
        f"{DEL}{b_repr}(X){RULE_SEPARATOR}{b_repr}(X), {DEL}{a_repr}{REQUEST}(X){END}"
    )
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{b_repr}{REQUEST}(X), {DEL}{a_repr}{REQUEST}(X){END}"

    return [r_del, r_inc]


def atomicB_in_atomicA_closure(b_repr, a_repr, ai_reprs):
    """
    param ai_reprs: list of A_i concepts where
        A in A_i
    """
    r_closure = f"{INS}{a_repr}{CLOSURE}(X){RULE_SEPARATOR}{DEL}{b_repr}(X), {NOT}{a_repr}(X), {NOT}{INS}{a_repr}{REQUEST}(X), {NOT}{DEL}{a_repr}{REQUEST}(X)"

    for ai_repr in ai_reprs:
        if ai_repr == a_repr:
            continue

        r_closure += f", {NOT}{DEL}{ai_repr}{REQUEST}(X)"
    r_closure += END

    return [r_closure]


def domP_in_atomicB(p_repr, b_repr):
    """
    Caution: p_repr is representation of `P`, not `domP` (or existsP)
    """
    r_del = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {DEL}{b_repr}{REQUEST}(X){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{p_repr}{REQUEST}(X,Y), {DEL}{b_repr}{REQUEST}(X){END}"
    return [r_del, r_inc]


def domP_in_atomicB_closure(p_repr, b_repr, bi_reprs):
    """
    param bi_reprs: list of B_i concepts where
        b in B_i
    """
    r_closure = f"{INS}{b_repr}{CLOSURE}(X){RULE_SEPARATOR}{DEL}{p_repr}(X,Y), {NOT}{b_repr}(X), {NOT}{INS}{b_repr}{REQUEST}(X), {NOT}{DEL}{b_repr}{REQUEST}(X)"

    for bi_repr in bi_reprs:
        if bi_repr == b_repr:
            continue

        r_closure += f", {NOT}{DEL}{bi_repr}{REQUEST}(X)"
    r_closure += END

    return [r_closure]


def rngP_in_atomicB(p_repr, b_repr):
    """
    Caution: p_repr is representation of `P`, not `rngP` (or existsPMinus)
    """
    r_del = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {DEL}{b_repr}{REQUEST}(Y){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{p_repr}{REQUEST}(X,Y), {DEL}{b_repr}{REQUEST}(Y){END}"
    return [r_del, r_inc]


def rngP_in_atomicB_closure(p_repr, b_repr, bi_reprs):
    """
    param bi_reprs: list of B_i concepts where
        b in B_i

    """
    r_closure = f"{INS}{b_repr}{CLOSURE}(X){RULE_SEPARATOR}{DEL}{p_repr}(Y,X), {NOT}{b_repr}(X), {NOT}{INS}{b_repr}{REQUEST}(X), {NOT}{DEL}{b_repr}{REQUEST}(X)"

    for bi_repr in bi_reprs:
        if bi_repr == b_repr:
            continue

        r_closure += f", {NOT}{DEL}{bi_repr}{REQUEST}(X)"
    r_closure += END

    return [r_closure]


def roleR_in_roleP(r_repr, p_repr):
    r_del = f"{DEL}{r_repr}(X,Y){RULE_SEPARATOR}{r_repr}(X,Y), {DEL}{p_repr}{REQUEST}(X,Y){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{r_repr}{REQUEST}(X,Y), {DEL}{p_repr}{REQUEST}(X,Y){END}"
    return [r_del, r_inc]


def roleR_in_roleP_closure(r_repr, p_repr, pi_reprs, si_reprs):
    """
    param pi_reprs: list of P_i roles where
        P in P_i
    param si_reprs: list of S_i roles where
        P in inv(S_i)
    """
    r_closure = f"{INS}{p_repr}{CLOSURE}(X,Y){RULE_SEPARATOR}{DEL}{r_repr}(X,Y), {NOT}{p_repr}(X,Y), {NOT}{INS}{p_repr}{REQUEST}(X,Y), {NOT}{DEL}{p_repr}{REQUEST}(X,Y)"

    for pi_repr in pi_reprs:
        if pi_repr == p_repr:
            continue

        r_closure += f", {NOT}{DEL}{pi_repr}{REQUEST}(X,Y)"

    for si_repr in si_reprs:
        r_closure += f", {NOT}{DEL}{si_repr}{REQUEST}(Y,X)"
    r_closure += END

    return [r_closure]


def roleR_in_invP(r_repr, p_repr):
    """
    Caution: p_repr is representation of `P`, not `invP`.
    """
    r_del = f"{DEL}{r_repr}(X,Y){RULE_SEPARATOR}{r_repr}(X,Y), {DEL}{p_repr}{REQUEST}(Y,X){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{r_repr}{REQUEST}(X,Y), {DEL}{p_repr}{REQUEST}(Y,X){END}"
    return [r_del, r_inc]


def roleR_in_invP_closure(r_repr, p_repr, pi_reprs, si_reprs):
    """
    param pi_reprs: list of P_i roles where
        P in P_i
    param si_reprs: list of S_i roles where
        P in inv(S_i)
    """

    r_closure = f"{INS}{p_repr}{CLOSURE}(X,Y){RULE_SEPARATOR}{DEL}{r_repr}(Y,X), {NOT}{p_repr}(X,Y), {NOT}{INS}{p_repr}{REQUEST}(X,Y), {NOT}{DEL}{p_repr}{REQUEST}(X,Y)"
    for pi_repr in pi_reprs:
        if pi_repr == p_repr:
            continue

        r_closure += f", {NOT}{DEL}{pi_repr}{REQUEST}(X,Y)"
    for si_repr in si_reprs:
        r_closure += f", {NOT}{DEL}{si_repr}{REQUEST}(Y,X)"
    r_closure += END
    return [r_closure]


def invR_in_roleP(left_repr, right_repr):
    r_del = f"{DEL}{left_repr}(X,Y){RULE_SEPARATOR}{left_repr}(X,Y), {DEL}{right_repr}{REQUEST}(Y,X){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{left_repr}{REQUEST}(X,Y), {DEL}{right_repr}{REQUEST}(Y,X){END}"

    return [r_del, r_inc]


POS_INCL_METHOD_MAP = {
    "aAInaBSub": atomicB_in_atomicA,
    "rInPSub": roleR_in_roleP,
    "rInPMinusSub": roleR_in_invP,
    "rMinusInPSub": invR_in_roleP,
    "ePInaBSub": domP_in_atomicB,
    "ePMinusInaBSub": rngP_in_atomicB,
}

POS_INCL_CLOSURE_METHOD_MAP = {
    "aAInaBSub": atomicB_in_atomicA_closure,
    "rInPSub": roleR_in_roleP_closure,
    "rInPMinusSub": roleR_in_invP_closure,
    "ePInaBSub": domP_in_atomicB_closure,
    "ePMinusInaBSub": rngP_in_atomicB_closure,
}
