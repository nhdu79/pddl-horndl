# Negation inclusion rules (Sec 2.4)
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


def atomicB_in_not_atomicA(b_repr, a_repr):
    """
    Caution: a_repr is representation of `A`, not `not A`
    """
    r_del_b = (
        f"{DEL}{b_repr}(X){RULE_SEPARATOR}{b_repr}(X), {INS}{a_repr}{REQUEST}(X){END}"
    )
    r_del_a = (
        f"{DEL}{a_repr}(X){RULE_SEPARATOR}{a_repr}(X), {INS}{b_repr}{REQUEST}(X){END}"
    )
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{b_repr}{REQUEST}(X), {INS}{a_repr}{REQUEST}(X){END}"

    return [r_del_b, r_del_a, r_inc]


def atomicA_closure(a_repr, b_reprs, j_reprs, r_reprs):
    """
    param a_repr: string
    param b_reprs: list of B_i concepts where
        A in lnot B_i
    param j_reprs: list of J_i roles where
        A in lnot dom(J_i)
    param r_reprs: list of R_i roles where
        A in lnot rng(R_i)
    """
    r_closure = f"{INS}{a_repr}(X){RULE_SEPARATOR}{INS}{a_repr}{CLOSURE}(X)"
    for b_repr in b_reprs:
        r_closure += f", {NOT}{INS}{b_repr}{REQUEST}(X)"

    for idx, j_repr in enumerate(j_reprs):
        r_closure += f", {NOT}{INS}{j_repr}{REQUEST}(X,Y{idx+1})"

    for idx, r_repr in enumerate(r_reprs):
        r_closure += f", {NOT}{INS}{r_repr}{REQUEST}(Y{idx+1},X)"
    r_closure += END

    return [r_closure]


def roleP_closure(
    p_repr, r_reprs, s_reprs, t_reprs, q_reprs, w_reprs, u_reprs, a_reprs, b_reprs
):
    """
    param p_repr: string
    param r_reprs: list of R_i roles where
        P in lnot r_i
    param s_reprs: list of S_i roles where
        P in lnot rng(S_i)
    param t_reprs: list of T_i roles where
        dom(P) in lnot dom(T_i)
    param q_reprs: list of Q_i roles where
        dom(P) in lnot rng(Q_i)
    param w_reprs: list of W_i roles where
        rng(P) in lnot dom(W_i)
    param u_reprs: list of U_i roles where
        rng(P) in lnot rng(U_i)
    param a_reprs: list of A_i concepts where
        dom(P) in lnot A_i
    param b_reprs: list of B_i concepts where
        rng(P) in lnot B_i
    """
    r_closure = f"{INS}{p_repr}(X,Y){RULE_SEPARATOR}{INS}{p_repr}{CLOSURE}(X,Y)"
    for r_repr in r_reprs:
        r_closure += f", {NOT}{INS}{r_repr}{REQUEST}(X,Y)"
    for s_repr in s_reprs:
        r_closure += f", {NOT}{INS}{s_repr}{REQUEST}(Y,X)"
    for idx, t_repr in enumerate(t_reprs):
        r_closure += f", {NOT}{INS}{t_repr}{REQUEST}(X,Y{idx+1})"
    for idx, q_repr in enumerate(q_reprs):
        r_closure += f", {NOT}{INS}{q_repr}{REQUEST}(Y{idx+1},X)"
    for idx, w_repr in enumerate(w_reprs):
        r_closure += f", {NOT}{INS}{w_repr}{REQUEST}(Y,X{idx+1})"
    for idx, u_repr in enumerate(u_reprs):
        r_closure += f", {NOT}{INS}{u_repr}{REQUEST}(X{idx+1},Y)"
    for a_repr in a_reprs:
        r_closure += f", {NOT}{INS}{a_repr}{REQUEST}(X)"
    for b_repr in b_reprs:
        r_closure += f", {NOT}{INS}{b_repr}{REQUEST}(Y)"
    r_closure += END

    return [r_closure]


def atomicB_in_not_domP(b_repr, p_repr):
    """
    Caution: p_repr is representation of `P`, not `not existsP`
    """
    r_del_b = (
        f"{DEL}{b_repr}(X){RULE_SEPARATOR}{b_repr}(X), {INS}{p_repr}{REQUEST}(X,Y){END}"
    )
    r_del_p = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {INS}{b_repr}{REQUEST}(X){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{b_repr}{REQUEST}(X), {INS}{p_repr}{REQUEST}(X,Y){END}"

    return [r_del_b, r_del_p, r_inc]


def domP_in_not_atomicB(p_repr, b_repr):
    """
    Caution: p_repr is representation of `P`, not `existsP`
        b_repr is representation of `B`
    """
    # dnh: Used to be a bug here
    r_del_p = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {INS}{b_repr}{REQUEST}(X){END}"
    r_del_b = (
        f"{DEL}{b_repr}(X){RULE_SEPARATOR}{b_repr}(X), {INS}{p_repr}{REQUEST}(X,Y){END}"
    )
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{b_repr}{REQUEST}(X), {INS}{p_repr}{REQUEST}(X,Y){END}"

    return [r_del_b, r_del_p, r_inc]


def r_in_not_P(r_repr, p_repr):
    """
    Caution: p_repr is representation of `P`, not `not P`
    """
    r_del_r = f"{DEL}{r_repr}(X,Y){RULE_SEPARATOR}{r_repr}(X,Y), {INS}{p_repr}{REQUEST}(X,Y){END}"
    r_del_p = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {INS}{r_repr}{REQUEST}(X,Y){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{r_repr}{REQUEST}(X,Y), {INS}{p_repr}{REQUEST}(X,Y){END}"

    return [r_del_r, r_del_p, r_inc]


def r_in_not_invP(r_repr, p_repr):
    """
    Caution: p_repr is representation of `P`, not `not invP`
    """
    r_del_r = f"{DEL}{r_repr}(X,Y){RULE_SEPARATOR}{r_repr}(X,Y), {INS}{p_repr}{REQUEST}(Y,X){END}"
    r_del_p = f"{DEL}{p_repr}(X,Y){RULE_SEPARATOR}{p_repr}(X,Y), {INS}{r_repr}{REQUEST}(Y,X){END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{r_repr}{REQUEST}(Y,X), {INS}{p_repr}{REQUEST}(Y,X){END}"

    return [r_del_r, r_del_p, r_inc]


NEG_INCL_METHOD_MAP = {
    "aAInNotaBSub": atomicB_in_not_atomicA,
    "aBInNotePSub": atomicB_in_not_domP,
    "ePInNotaBSub": domP_in_not_atomicB,
    "rInNotPSub": r_in_not_P,
    "rInNotPMinusSub": r_in_not_invP,
}
