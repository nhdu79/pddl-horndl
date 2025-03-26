# General rules for deleting atomic concepts and roles
# ~ First 2 bullet points/Sec 2.4
from coherence_update.rules.symbols import RULE_SEPARATOR, NOT, INS, DEL, REQUEST, INCOMPATIBLE_UPDATE, UPDATING, END


def build_del_concept_and_incompatible_rules_for_atomic_concepts(a_concepts):
    """
        Build rules for deleting atomic concepts and their incompatible rules
        param:
            a_concepts: string[]
    """
    rules = []
    for a_concept in a_concepts:
        r_ins = f"{INS}{a_concept}(X){RULE_SEPARATOR}{INS}{a_concept}{REQUEST}(X), {NOT}{a_concept}(X){END}"
        r_del = f"{DEL}{a_concept}(X){RULE_SEPARATOR}{DEL}{a_concept}{REQUEST}(X), {a_concept}(X){END}"
        r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{a_concept}{REQUEST}(X), {DEL}{a_concept}{REQUEST}(X){END}"
        r_update_ins = f"{UPDATING}(){RULE_SEPARATOR}{INS}{a_concept}{REQUEST}(X){END}"
        r_update_del = f"{UPDATING}(){RULE_SEPARATOR}{DEL}{a_concept}{REQUEST}(X){END}"
        rules.extend([r_del, r_inc, r_update_ins, r_update_del, r_ins])

    return rules


def build_del_role_and_incompatible_rules_for_roles(roles):
    """
        Build rules for deleting roles and their incompatible rules
        param:
            roles: string[]
    """
    rules = []
    for role in roles:
        r_ins = f"{INS}{role}(X,Y){RULE_SEPARATOR}{INS}{role}{REQUEST}(X,Y), {NOT}{role}(X,Y){END}"
        r_del = f"{DEL}{role}(X,Y){RULE_SEPARATOR}{DEL}{role}{REQUEST}(X,Y), {role}(X,Y){END}"
        r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{role}{REQUEST}(X,Y), {DEL}{role}{REQUEST}(X,Y){END}"
        r_update_ins = f"{UPDATING}(){RULE_SEPARATOR}{INS}{role}{REQUEST}(X,Y){END}"
        r_update_del = f"{UPDATING}(){RULE_SEPARATOR}{DEL}{role}{REQUEST}(X,Y){END}"
        rules.extend([r_del, r_inc, r_update_ins, r_update_del, r_ins])

    return rules


def build_funct_P_and_funct_inv_P_rules(functs, functs_inv):
    """
        Build rules for funct(P) and invFunct(P)
        param:
            functs: string[]
            functs_inv: string[]
    """
    rules = []
    for funct in functs:
        rules.extend(functP(funct))
    for funct_inv in functs_inv:
        rules.extend(functInvP(funct_inv))

    return rules


def functP(repr):
    """
        Caution: repr is representation of `P`, not `functP`
    """
    r_del = f"{DEL}{repr}(X,Y){RULE_SEPARATOR}{repr}(X,Y), {INS}{repr}{REQUEST}(X,Z), Y!=Z{END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{repr}{REQUEST}(X,Y), {INS}{repr}{REQUEST}(X,Z), Y!=Z{END}"
    r_update_ins = f"{UPDATING}(){RULE_SEPARATOR}{INS}{repr}{REQUEST}(X,Y){END}"
    r_update_del = f"{UPDATING}(){RULE_SEPARATOR}{DEL}{repr}{REQUEST}(X,Y){END}"
    return [r_del, r_inc, r_update_ins, r_update_del]


def functInvP(repr):
    """
        Caution: repr is representation of `P`, not `functP`
    """
    r_del = f"{DEL}{repr}(X,Y){RULE_SEPARATOR}{repr}(X,Y), {INS}{repr}{REQUEST}(Z,Y), X!=Z{END}"
    r_inc = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{repr}{REQUEST}(X,Y), {INS}{repr}{REQUEST}(Z,Y), X!=Z{END}"
    r_update_ins = f"{UPDATING}(){RULE_SEPARATOR}{INS}{repr}{REQUEST}(X,Y){END}"
    r_update_del = f"{UPDATING}(){RULE_SEPARATOR}{DEL}{repr}{REQUEST}(X,Y){END}"
    return [r_del, r_inc, r_update_ins, r_update_del]

