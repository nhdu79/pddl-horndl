from collections import defaultdict

from coherence_update.rules.atomic import *
from coherence_update.rules.negative import *
from coherence_update.rules.positive import *
from compilation.variant_options import UPDATING_PREDICATE_TYPES


class CohrenceUpdate:
    def run(tbox, updating_pred_type):
        update = CohrenceUpdate(tbox, updating_pred_type)
        rules = []
        rules.extend(update.build_rules_for_atomic_concepts_and_roles())
        rules.extend(update.build_update_rules("positive"))
        rules.extend(update.build_update_rules("negative"))
        rules.extend(update.build_positive_inclusions_update_rules())
        rules.extend(update.build_negative_inclusions_update_rules())
        return rules

    def __init__(self, tbox, updating_pred_type):
        """
        A in A_i => type 1
        P in P_i => type 2
        P in P_i^- => type 3
        A in not A_i => type 4
        A in not dom(P_i) => type 5
        A in not rng(P_i) => type 6
        P in not P_i => type 7
        !!! P in not rng(S_i) => type 8 !!!
        dom(P) in not dom(T_i) => type 9
        dom(P) in not rng(Q_i) => type 10
        rng(P) in not dom(W_i) => type 11
        rng(P) in not rng(U_i) => type 12
        dom(P) in not A_i => type 13
        rng(P) in not B_i => type 14
        """
        self.tbox = tbox
        self.updating_pred_type = updating_pred_type
        self._type1, self._type2, self._type3 = [defaultdict(list) for _ in range(3)]
        self._type4, self._type5, self._type6 = [defaultdict(list) for _ in range(3)]
        self._type7, self._type8, self._type9 = [defaultdict(list) for _ in range(3)]
        self._type10, self._type11, self._type12 = [defaultdict(list) for _ in range(3)]
        self._type13, self._type14 = [defaultdict(list) for _ in range(2)]

    def build_rules_for_atomic_concepts_and_roles(self):
        atomic_concepts = self.tbox.repr_of("a_concepts")
        atomic_roles = self.tbox.repr_of("roles")
        functs, inv_functs = self.tbox.repr_of("functs"), self.tbox.repr_of(
            "inv_functs"
        )

        r_concepts = (
            build_insert_and_delete_rules_and_incompatible_update_for_atomic_concepts(
                atomic_concepts
            )
        )
        r_roles = (
            build_insert_and_delete_rules_and_incompatible_update_for_atomic_roles(
                atomic_roles
            )
        )
        r_functs = build_delete_rules_and_incompatible_update_for_functs(functs)
        r_inv_functs = build_delete_rules_and_incompatible_update_for_inv_functs(
            inv_functs
        )
        if self.updating_pred_type == UPDATING_PREDICATE_TYPES["derived_predicate"]:
            r_concepts.extend(build_updating_rules_for_atomic_concepts(atomic_concepts))
            r_roles.extend(build_updating_rules_for_atomic_roles(atomic_roles))
            r_functs.extend(build_updating_rules_for_functs(functs))
            r_inv_functs.extend(build_updating_rules_for_inv_functs(inv_functs))

        return r_concepts + r_roles + r_functs + r_inv_functs

    def build_update_rules(self, closure_type):
        rules = []
        mapping = (
            (closure_type == "positive" and POS_INCL_METHOD_MAP)
            or (closure_type == "negative" and NEG_INCL_METHOD_MAP)
            or None
        )
        if not mapping:
            raise ValueError("Invalid closure type")

        for key, builder_method in mapping.items():
            inclusions = self.tbox.incl_dict[key]
            for incl in inclusions:
                left_closure_repr = incl.get_left_closure_repr()
                right_closure_repr = incl.get_right_closure_repr()
                rules.extend(builder_method(left_closure_repr, right_closure_repr))
                if closure_type == "positive":
                    if key == "aAInaBSub":
                        self._type1[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "rInPSub":
                        self._type2[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "rInPMinusSub":
                        self._type3[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                elif closure_type == "negative":
                    if key == "aAInNotaBSub":
                        self._type4[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "aBInNotePSub":
                        self._type5[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "aBInNotePMinusSub":
                        self._type6[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "rInNotPSub":
                        self._type7[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "rInNotPMinusSub":
                        self._type8[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRInNotePSub":
                        self._type9[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRInNotePMinusSub":
                        self._type10[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRMinusInNotePSub":
                        self._type11[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRMinusInNotePMinusSub":
                        self._type12[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRInNotaASub":
                        self._type13[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )
                    elif key == "eRMinusInNotaASub":
                        self._type14[left_closure_repr].append(
                            incl.get_right_closure_repr()
                        )

        return rules

    def build_positive_inclusions_update_rules(self):
        rules = []
        for key, builder_method in POS_INCL_CLOSURE_METHOD_MAP.items():
            inclusions = self.tbox.incl_dict[key]
            for incl in inclusions:
                left_repr = incl.get_left_closure_repr()
                right_repr = incl.get_right_closure_repr()
                if key in ["aAInaBSub", "ePInaBSub", "ePMinusInaBSub"]:
                    # passed
                    closure_reprs = self._type1[left_repr]
                    rules.extend(builder_method(left_repr, right_repr, closure_reprs))
                elif key in ["rInPSub", "rInPMinusSub"]:
                    pi_reprs = self._type2[left_repr]
                    si_reprs = self._type3[left_repr]
                    rules.extend(
                        builder_method(left_repr, right_repr, pi_reprs, si_reprs)
                    )

        return rules

    def build_negative_inclusions_update_rules(self):
        rules = []
        atomic_concepts = self.tbox.repr_of("a_concepts")
        for a_concept in atomic_concepts:
            b_reprs, j_reprs, r_reprs = (
                self._type4[a_concept],
                self._type5[a_concept],
                self._type6[a_concept],
            )
            rules.extend(atomicA_closure(a_concept, b_reprs, j_reprs, r_reprs))

        atomic_roles = self.tbox.repr_of("roles")
        for a_role in atomic_roles:
            r_reprs, s_reprs, t_reprs = (
                self._type7[a_role],
                self._type8[a_role],
                self._type9[a_role],
            )
            q_reprs, w_reprs, u_reprs = (
                self._type10[a_role],
                self._type11[a_role],
                self._type12[a_role],
            )
            a_reprs, b_reprs = self._type13[a_role], self._type14[a_role]
            rules.extend(
                roleP_closure(
                    a_role,
                    r_reprs,
                    s_reprs,
                    t_reprs,
                    q_reprs,
                    w_reprs,
                    u_reprs,
                    a_reprs,
                    b_reprs,
                )
            )

        return rules
