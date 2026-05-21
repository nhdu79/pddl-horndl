from coherence_update.rules.symbols import (
    A_OR_AP_CL,
    AP_CL,
    DEL,
    DEL_CL,
    END,
    INCOMPATIBLE_UPDATE,
    INS,
    INS_CL,
    MIN_X_IN_TAU,
    NOT,
    PRE_INS,
    REQUEST,
    RULE_SEPARATOR,
    WORD_SEPARATOR,
)
from owl import OWL_NOTHING
from owl.expressions import (
    AtomicRole,
    ExistentialConcept,
    InverseExistentialConcept,
    InverseRole,
)


def _inverse_of(role):
    """AtomicRole(R) → InverseRole(R);  InverseRole(R) → R (the inner AtomicRole)."""
    if isinstance(role, AtomicRole):
        return InverseRole(role)
    return role.role  # InverseRole.role is the inner AtomicRole


def _existential_of(role):
    """AtomicRole(R) → ExistentialConcept(R);  InverseRole(R) → InverseExistentialConcept(R.role)."""
    if isinstance(role, AtomicRole):
        return ExistentialConcept(role)
    return InverseExistentialConcept(role.role)


# ---------------------------------------------------------------------------
# Stratum 1 — Propagation closure
# ---------------------------------------------------------------------------


#   AOrApCl_X(Ȳ) ← X(Ȳ)                          (1)
#   ApCl_X(Ȳ), AOrApCl_X(Ȳ) ← Ap_X(Ȳ)            (2)  split into two Datalog rules
def build_trigger_rules_for_propagation_concepts(concepts):
    """
    Build rules 1-2 for every positive concept X (unary, Ȳ = X).
    param:
        concepts: list[ConceptExpression]
    """
    rules = []
    for concept in concepts:
        r1 = f"{A_OR_AP_CL}{concept.id}(X){RULE_SEPARATOR}{concept.id}(X){END}"
        r2 = f"{AP_CL}{concept.id}(X){RULE_SEPARATOR}{INS}{concept.id}{REQUEST}(X){END}"
        r3 = f"{A_OR_AP_CL}{concept.id}(X){RULE_SEPARATOR}{INS}{concept.id}{REQUEST}(X){END}"
        rules.extend([r1, r2, r3])
    return rules


#  (binary Ȳ = (X, Y)):
#   AOrApCl_R(Ȳ) ← R(Ȳ)                           (1)
#   ApCl_R(Ȳ), AOrApCl_R(Ȳ) ← Ap_R(Ȳ)             (2)  split into two Datalog rules
def build_trigger_rules_for_propagation_roles(roles):
    """
    Build rules 1-2 for every basic role R (binary, Ȳ = (X, Y)).
    param:
        roles: list[AtomicRole | InverseRole]
    """
    rules = []
    for role in roles:
        r1 = f"{A_OR_AP_CL}{role.id}(X,Y){RULE_SEPARATOR}{role.id}(X,Y){END}"
        r2 = f"{AP_CL}{role.id}(X,Y){RULE_SEPARATOR}{INS}{role.id}{REQUEST}(X,Y){END}"
        r3 = f"{A_OR_AP_CL}{role.id}(X,Y){RULE_SEPARATOR}{INS}{role.id}{REQUEST}(X,Y){END}"
        rules.extend([r1, r2, r3])
    return rules


#   pred_R⁻(Y,X) ← pred_R(X,Y)   for pred ∈ {ApCl, AOrApCl}  (3a)
#   pred_∃R(X)   ← pred_R(X,Y)   for pred ∈ {ApCl, AOrApCl}  (3b)
def build_connective_rules_for_propagation_role(role):
    """
    Build rule 3 for a general role R (AtomicRole or InverseRole).
    Propagates pred ∈ {ApCl, AOrApCl} to the inverse role and the existential restriction.
    The inverse and existential are derived from the role object:
        AtomicRole(R)    → inverse = InverseRole(R),      existential = ExistentialConcept(R)
        InverseRole(R)   → inverse = R (AtomicRole),      existential = InverseExistentialConcept(R)
    param:
        role: AtomicRole | InverseRole
    """
    inv = _inverse_of(role)
    ex = _existential_of(role)
    rules = []
    for symbol in [A_OR_AP_CL, AP_CL]:
        r1 = f"{symbol}{inv.id}(Y,X){RULE_SEPARATOR}{symbol}{role.id}(X,Y){END}"
        r2 = f"{symbol}{ex.id}(X){RULE_SEPARATOR}{symbol}{role.id}(X,Y){END}"
        rules.extend([r1, r2])
    return rules


#   pred_X(Ȳ) ← pred_X1(Ȳ) ∧ … ∧ pred_Xk(Ȳ)     for pred ∈ {ApCl, AOrApCl}  (4)
def build_propagation_rules_for_concept(sub_concepts, super_concept):
    """
    Build rule 4 for concept inclusion X1 ⊓ … ⊓ Xk ⊑ X (unary, Ȳ = X).
    param:
        sub_concepts: list[ConceptExpression]
        super_concept: ConceptExpression
    """
    rules = []
    for symbol in [A_OR_AP_CL, AP_CL]:
        r_body = ", ".join(
            [f"{symbol}{sub_concept.id}(X)" for sub_concept in sub_concepts]
        )
        r = f"{symbol}{super_concept.id}(X){RULE_SEPARATOR}{r_body}{END}"
        rules.append(r)
    return rules


#   pred_P(X,Y) ← pred_R(X,Y)   for pred ∈ {ApCl, AOrApCl}  (4)
def build_propagation_rules_for_role(sub_role, super_role):
    """
    Build rule 4 for role inclusion R ⊑ P (binary, Ȳ = (X, Y)).
    param:
        sub_role:  AtomicRole | InverseRole
        super_role: AtomicRole | InverseRole
    """
    rules = []
    for symbol in [A_OR_AP_CL, AP_CL]:
        r = f"{symbol}{super_role.id}(X,Y){RULE_SEPARATOR}{symbol}{sub_role.id}(X,Y){END}"
        rules.append(r)
    return rules


# ---------------------------------------------------------------------------
# Stratum 2 — Deletion closure
# ---------------------------------------------------------------------------


#   DelCl_X(Ȳ) ← Am_X(Ȳ)   (Am_X = del_X_request)  (5)
def build_trigger_rules_for_deletion_concepts(concepts):
    """
    Build rule 5 for every positive concept X (unary, Ȳ = X).
    param:
        concepts: list[ConceptExpression]
    """
    rules = []
    for concept in concepts:
        r = f"{DEL_CL}{concept.id}(X){RULE_SEPARATOR}{DEL}{concept.id}{REQUEST}(X){END}"
        rules.append(r)
    return rules


#   DelCl_R(X,Y) ← Am_R(X,Y)   (Am_R = del_R_request)  (5)
def build_trigger_rules_for_deletion_roles(roles):
    """
    Build rule 5 for every basic role R (binary, Ȳ = (X, Y)).
    param:
        roles: list[AtomicRole | InverseRole]
    """
    rules = []
    for role in roles:
        r = f"{DEL_CL}{role.id}(X,Y){RULE_SEPARATOR}{DEL}{role.id}{REQUEST}(X,Y){END}"
        rules.append(r)
    return rules


#   DelCl_R⁻(Y,X) ← DelCl_R(X,Y)                       (6)
#   DelCl_R(X,Y)  ← AOrApCl_R(X,Y) ∧ DelCl_∃R(X)       (7)
def build_connnective_rules_for_deletion_role(role):
    """
    Build rules 6-7 for a general role R (AtomicRole or InverseRole).
    The inverse and existential are derived from the role object (see _inverse_of/_existential_of).
    param:
        role: AtomicRole | InverseRole
    """
    inv = _inverse_of(role)
    ex = _existential_of(role)
    r6 = f"{DEL_CL}{inv.id}(Y,X){RULE_SEPARATOR}{DEL_CL}{role.id}(X,Y){END}"
    r7 = f"{DEL_CL}{role.id}(X,Y){RULE_SEPARATOR}{A_OR_AP_CL}{role.id}(X,Y), {DEL_CL}{ex.id}(X){END}"
    return [r6, r7]


#   DelCl_R(X,Z) ← Ap_R(X,Y) ∧ R(X,Z) ∧ Y ≠ Z           (8)
#   incompatible() ← Ap_R(X,Y) ∧ Ap_R(X,Z) ∧ Y ≠ Z      (9)
def build_rules_for_functional_roles(functional_roles):
    """
    Build rules 8-9 for each functional role R.
    param:
        functional_roles: list[AtomicRole | InverseRole]
    """
    rules = []
    for f_role in functional_roles:
        r8 = f"{DEL_CL}{f_role.id}(X,Z){RULE_SEPARATOR}{INS}{f_role.id}{REQUEST}(X,Y), {f_role.id}(X,Z), Y!=Z{END}"
        r9 = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{INS}{f_role.id}{REQUEST}(X,Y), {INS}{f_role.id}{REQUEST}(X,Z), Y!=Z{END}"
        rules.extend([r8, r9])
    return rules


def _tau_name(sub_concept, axiom_id):
    return f"{MIN_X_IN_TAU}{sub_concept.id}{WORD_SEPARATOR}in{WORD_SEPARATOR}{axiom_id}"


# Corresponds to rules 10, 11, 12 of Stratum 2
def build_deletion_rules_for_negative_role_inclusion(role_r, role_r_prime):
    """
    For R ⊑ ¬R' ∈ T*: inserting R forces deletion of R' (and vice versa);
    having both in ApCl is incompatible.
    param:
        role_r:       AtomicRole | InverseRole  (the sub role R)
        role_r_prime: AtomicRole | InverseRole  (inner role of ¬R')
    """
    r10 = f"{DEL_CL}{role_r_prime.id}(X,Y){RULE_SEPARATOR}{AP_CL}{role_r.id}(X,Y), {A_OR_AP_CL}{role_r_prime.id}(X,Y){END}"
    r11 = f"{DEL_CL}{role_r.id}(X,Y){RULE_SEPARATOR}{AP_CL}{role_r_prime.id}(X,Y), {A_OR_AP_CL}{role_r.id}(X,Y){END}"
    r12 = f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{AP_CL}{role_r.id}(X,Y), {AP_CL}{role_r_prime.id}(X,Y){END}"
    return [r10, r11, r12]


# Corresponds to rules 13, 14 of Stratum 2
def build_min_and_deletion_rules_for_conjunction_concept(
    sub_concepts, super_concept, axiom_id
):
    """
    For τ = X1 ⊓ … ⊓ Xk ⊑ X ∈ T* (concept case), and each i ∈ {1,…,k}:
    - Rule 13: min_Xi_in_τ(X) ← ApCl_X1(X) ∧ … ∧ ApCl_{Xi-1}(X) ∧ ¬ApCl_Xi(X)
    - Rule 14: DelCl_Xi(X) ← DelCl_X(X) ∧ min_Xi_in_τ(X) ∧ AOrApCl_X1(X) ∧ … ∧ AOrApCl_Xk(X)
    param:
        sub_concepts: list[ConceptExpression]
        super_concept: ConceptExpression
        axiom_id: str
    """

    rules = []
    # dnh: Order assumed via `i`!!!
    for i, xi in enumerate(sub_concepts):
        min_pred = _tau_name(xi, axiom_id)
        body13 = (
            [f"{AP_CL}{sub_concepts[j].id}(X)" for j in range(i)]
            + [f"{NOT}{AP_CL}{xi.id}(X)"]
            + [f"{A_OR_AP_CL}{xi.id}(X)"]
        )
        r13 = f"{min_pred}(X){RULE_SEPARATOR}{', '.join(body13)}{END}"
        body14 = [f"{min_pred}(X)"]
        if super_concept != OWL_NOTHING:
            body14 += [f"{DEL_CL}{super_concept.id}(X)"]
        body14 += [
            f"{A_OR_AP_CL}{sub_concepts[j].id}(X)"
            for j in range(min(i + 1, len(sub_concepts)), len(sub_concepts))
        ]

        r14 = f"{DEL_CL}{xi.id}(X){RULE_SEPARATOR}{', '.join(body14)}{END}"
        rules.extend([r13, r14])

    return rules


def build_min_and_deletion_rules_for_role(sub_role, super_role, axiom_id):
    """
    For τ = R ⊑ P ∈ T* (role case).
    Rule 14 (k=1 special case): DelCl_R(X,Y) ← DelCl_P(X,Y) ∧ AOrApCl_R(X,Y)
    param:
        sub_role:  AtomicRole | InverseRole  (R)
        super_role: AtomicRole | InverseRole  (P)
    """
    min_pred = _tau_name(sub_role, axiom_id)
    r13 = f"{min_pred}(X,Y){RULE_SEPARATOR}{NOT}{AP_CL}{sub_role.id}(X,Y), {A_OR_AP_CL}{sub_role.id}(X,Y){END}"
    r14 = f"{DEL_CL}{sub_role.id}(X,Y){RULE_SEPARATOR}{DEL_CL}{super_role.id}(X,Y), {min_pred}(X,Y){END}"

    return [r13, r14]


# dnh: Based on the comment, this rule is only implemented for superconcept \bot!
def build_incompatibility_rule_for_conjunction_concept_with_bottom(sub_concepts):
    """
    For τ = B1 ⊓ … ⊓ Bk ⊑ ⊥ ∈ T*:
    incompatible() ← ApCl_B1(X) ∧ … ∧ ApCl_Bk(X)
    param:
        sub_concepts: list[ConceptExpression]
    """
    body = [f"{AP_CL}{xi.id}(X)" for xi in sub_concepts]
    return [f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{', '.join(body)}{END}"]


# Corresponds to rule 16 of Stratum 2
def build_incompatibility_rules_for_direct_deletion_concepts(concepts):
    """
    incompatible() ← ApCl_X(X) ∧ Am_X(X)   (Am_X = del_X_request)
    param:
        concepts: list[ConceptExpression]
    """
    return [
        f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{AP_CL}{concept.id}(X), {DEL}{concept.id}{REQUEST}(X){END}"
        for concept in concepts
    ]


def build_incompatibility_rules_for_direct_deletion_roles(roles):
    """
    incompatible() ← ApCl_R(X,Y) ∧ Am_R(X,Y)   (Am_R = del_R_request)
    param:
        roles: list[AtomicRole | InverseRole]
    """
    return [
        f"{INCOMPATIBLE_UPDATE}(){RULE_SEPARATOR}{AP_CL}{role.id}(X,Y), {DEL}{role.id}{REQUEST}(X,Y){END}"
        for role in roles
    ]


# Corresponds to rule 17 of Stratum 2
def build_actual_deletion_rules_for_concepts(concepts):
    """
    del_X(X) ← X(X) ∧ DelCl_X(X)
    param:
        concepts: list[ConceptExpression]
    """
    return [
        f"{DEL}{concept.id}(X){RULE_SEPARATOR}{concept.id}(X), {DEL_CL}{concept.id}(X){END}"
        for concept in concepts
    ]


def build_actual_deletion_rules_for_roles(roles):
    """
    del_R(X,Y) ← R(X,Y) ∧ DelCl_R(X,Y)
    param:
        roles: list[AtomicRole | InverseRole]
    """
    return [
        f"{DEL}{role.id}(X,Y){RULE_SEPARATOR}{role.id}(X,Y), {DEL_CL}{role.id}(X,Y){END}"
        for role in roles
    ]


# ---------------------------------------------------------------------------
# Stratum 3 — Insertion closure
# ---------------------------------------------------------------------------


# Corresponds to rule 18 of Stratum 3
def build_pre_insertion_rules_for_conjunction_concept(
    sub_concepts, super_concept, axiom_id
):
    """
    preInsCl_τ(X) ← AOrApCl_X1(X) ∧ … ∧ AOrApCl_Xk(X) ∧ ¬DelCl_X(X)
    param:
        sub_concepts: list[ConceptExpression]
        super_concept: ConceptExpression
        axiom_id: str
    """
    pre_ins_pred = f"{PRE_INS}{axiom_id}"
    body = [f"{A_OR_AP_CL}{xi.id}(X)" for xi in sub_concepts] + [
        f"{NOT}{DEL_CL}{super_concept.id}(X)"
    ]
    return [f"{pre_ins_pred}(X){RULE_SEPARATOR}{', '.join(body)}{END}"]


def build_pre_insertion_rules_for_role(sub_role, super_role, axiom_id):
    """
    preInsCl_τ(X,Y) ← AOrApCl_R(X,Y) ∧ ¬DelCl_P(X,Y)
    param:
        sub_role:  AtomicRole | InverseRole  (R)
        super_role: AtomicRole | InverseRole  (P)
        axiom_id: str
    """
    pre_ins_pred = f"{PRE_INS}{axiom_id}"
    body = [f"{A_OR_AP_CL}{sub_role.id}(X,Y)", f"{NOT}{DEL_CL}{super_role.id}(X,Y)"]
    return [f"{pre_ins_pred}(X,Y){RULE_SEPARATOR}{', '.join(body)}{END}"]


# Corresponds to rule 19 of Stratum 3
def build_insertion_closure_rules_for_conjunction_concept(
    sub_concepts, super_concept, axiom_id
):
    """
    insCl_X(X) ← DelCl_Xi(X) ∧ preInsCl_τ(X)   for each i ∈ {1,…,k}
    param:
        sub_concepts: list[ConceptExpression]
        super_concept: ConceptExpression
        axiom_id: str
    """
    rules = []
    for sub_concept in sub_concepts:
        r = f"{INS_CL}{super_concept.id}(X){RULE_SEPARATOR}{DEL_CL}{sub_concept.id}(X), {PRE_INS}{axiom_id}(X){END}"
        rules.append(r)
    return rules


def build_insertion_closure_rules_for_role(sub_role, super_role, axiom_id):
    """
    insCl_P(X,Y) ← DelCl_R(X,Y) ∧ preInsCl_τ(X,Y)
    param:
        sub_role:  AtomicRole | InverseRole  (R)
        super_role: AtomicRole | InverseRole  (P)
        axiom_id: str
    """
    return [
        f"{INS_CL}{super_role.id}(X,Y){RULE_SEPARATOR}{DEL_CL}{sub_role.id}(X,Y), {PRE_INS}{axiom_id}(X,Y){END}"
    ]


def build_insertion_closure_rule_for_existential(role):
    """
    insCl_∃R(X) ← DelCl_R(X,Y) ∧ AOrApCl_R(X,Y) ∧ ¬DelCl_∃R(X)   (20)
    The existential restriction ∃R is derived from the role object:
        AtomicRole(R)  → ExistentialConcept(R)         id: exists_R
        InverseRole(R) → InverseExistentialConcept(R)  id: exists_inv_R
    param:
        role: AtomicRole | InverseRole
    """
    ex = _existential_of(role)
    r20 = (
        f"{INS_CL}{ex.id}(X){RULE_SEPARATOR}"
        f"{DEL_CL}{role.id}(X,Y), {A_OR_AP_CL}{role.id}(X,Y), {NOT}{DEL_CL}{ex.id}(X){END}"
    )
    return [r20]


def build_actual_insertion_rules_for_concepts(concepts):
    """
    ins_X(X) ← ¬X(X) ∧ insCl_X(X)   (21)
    ins_X(X) ← ¬X(X) ∧ Ap_X(X)       (22, Ap_X = ins_X_request)
    param:
        concepts: list[ConceptExpression]
    """
    rules = []
    for concept in concepts:
        r21 = f"{INS}{concept.id}(X){RULE_SEPARATOR}{NOT}{concept.id}(X), {INS_CL}{concept.id}(X){END}"
        r22 = f"{INS}{concept.id}(X){RULE_SEPARATOR}{NOT}{concept.id}(X), {INS}{concept.id}{REQUEST}(X){END}"
        rules.extend([r21, r22])
    return rules


def build_actual_insertion_rules_for_roles(roles):
    """
    ins_R(X,Y) ← ¬R(X,Y) ∧ insCl_R(X,Y)   (21)
    ins_R(X,Y) ← ¬R(X,Y) ∧ Ap_R(X,Y)       (22, Ap_R = ins_R_request)
    param:
        roles: list[AtomicRole | InverseRole]
    """
    rules = []
    for role in roles:
        r21 = f"{INS}{role.id}(X,Y){RULE_SEPARATOR}{NOT}{role.id}(X,Y), {INS_CL}{role.id}(X,Y){END}"
        r22 = f"{INS}{role.id}(X,Y){RULE_SEPARATOR}{NOT}{role.id}(X,Y), {INS}{role.id}{REQUEST}(X,Y){END}"
        rules.extend([r21, r22])
    return rules
