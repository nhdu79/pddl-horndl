(define (domain assembly)

(:requirements :universal-preconditions)

(:predicates
    ;; Installation roles — ABox facts managed by actions; functional in the TBox
    (screenInstalledIn ?s ?p)
    (batteryInstalledIn ?b ?p)
    (boardInstalledIn ?r ?p)

    ;; Component type predicates — set in problem init, not reasoned over by TBox
    (Screen ?x)
    (Battery ?x)
    (Processor ?x)

    ;; Certification status — directly managed by actions
    (Inspected ?x)
    (Tested ?x)

    ;; Ontology-derived assembly status — queried via MKO
    ;; HasScreen/HasBattery/HasBoard come from range axioms on the three roles.
    ;; HasCoreComponents and FullyEquipped come from the conjunction chain.
    (HasScreen ?p)
    (HasBattery ?p)
    (HasBoard ?p)
    (HasCoreComponents ?p)
    (FullyEquipped ?p)

    ;; Ontology-derived certification status — queried via MKO
    (ReadyToUse ?x)

    ;; Quality-record concepts — Validated set by validate-assembly action;
    ;; ProductRecord derived from FullyEquipped ⊓ Validated (and preserved
    ;; explicitly in ABox when FullyEquipped is deleted but Validated holds).
    (Validated ?p)
    (ProductRecord ?p)
)

;; ── Certification pipeline ───────────────────────────────────────────────────
;;
;; A single certify action sets both Inspected and Tested.  The two predicates
;; remain distinct because remove-and-rework-screen asserts only Inspected
;; (Ap_Inspected), shielding it so that the LTR Min rule (stratum 2, rules 13-14)
;; deletes Tested and not Inspected when ReadyToUse is revoked.

(:action certify
    :parameters (?c)
    :precondition (or (Screen ?c) (Battery ?c) (Processor ?c))
    :effect (and (Inspected ?c) (Tested ?c)))

;; ── Component installation ───────────────────────────────────────────────────
;;
;; install-screen requires the screen to be ReadyToUse AND not currently installed
;; in any phone.  The universal precondition (forall ?p2 ...) prevents the planner
;; from "moving" a pre-installed screen to a second phone without first reworking.
;; After the cascade from remove-and-rework-screen deletes all screenInstalledIn
;; facts for the reworked phone, every evicted screen satisfies this precondition
;; and can be reinstalled.

(:action install-screen
    :parameters (?s ?p)
    :precondition (and (mko (ReadyToUse ?s))
                       (Screen ?s)
                       (forall (?p2) (not (screenInstalledIn ?s ?p2)))
                       (not (mko (HasScreen ?p))))
    :effect (screenInstalledIn ?s ?p))

(:action install-battery
    :parameters (?b ?p)
    :precondition (and (mko (ReadyToUse ?b))
                       (Battery ?b)
                       (not (mko (HasBattery ?p))))
    :effect (batteryInstalledIn ?b ?p))

(:action install-board
    :parameters (?r ?p)
    :precondition (and (mko (ReadyToUse ?r))
                       (Processor ?r)
                       (not (mko (HasBoard ?p))))
    :effect (boardInstalledIn ?r ?p))

;; ── Quality validation ──────────────────────────────────────────────────────────
;;
;; Sets Validated, which together with FullyEquipped (TBox-derived) gives
;; ProductRecord via the conjunction FullyEquipped ⊓ Validated ⊑ ProductRecord.

(:action validate-assembly
    :parameters (?p)
    :precondition (mko (FullyEquipped ?p))
    :effect (Validated ?p))

;; ── Rework action — exploits Horn LTR ordering ────────────────────────────────
;;
;; The action removes a misplaced screen and simultaneously re-asserts Inspected,
;; exploiting the LTR priority of the conjunction  Inspected ⊓ Tested ⊑ ReadyToUse.
;;
;; After compilation, effects become:
;;   Am_FullyEquipped(?p)   — explicit phone-level deletion (drives the full cascade)
;;   Ap_Inspected(?s)       — shields Inspected in the certification cascade
;;   Am_ReadyToUse(?s)      — revokes the screen's certification
;;
;; Stratum 2 deletion cascades from Am_FullyEquipped:
;;   DelCl_FullyEquipped
;;     → rules 13-14 (HasCoreComponents ⊓ HasBoard ⊑ FullyEquipped):
;;         Min picks HasCoreComponents (first non-Ap) → DelCl_HasCoreComponents
;;     → rules 13-14 (HasScreen ⊓ HasBattery ⊑ HasCoreComponents):
;;         Min picks HasScreen (first non-Ap) → DelCl_HasScreen
;;     → rules 13-14 k=1 (∃screenInstalledIn⁻ ⊑ HasScreen):
;;         min trivially true (Ap_∃screenInstalledIn⁻ never asserted)
;;         → DelCl_∃screenInstalledIn⁻
;;     → rule 7 for InverseRole(screenInstalledIn):
;;         DelCl_inv_screenInstalledIn(p,s)  for EVERY screen on phone p
;;     → rule 6: DelCl_screenInstalledIn(s,p) → del_screenInstalledIn(s,p)
;;
;;   DelCl_ReadyToUse (from Am_ReadyToUse):
;;     → Ap_Inspected shields Inspected; Min picks Tested → DelCl_Tested → del_Tested
;;
;; After the update action fires, ALL screenInstalledIn facts for phone ?p are
;; deleted (both ?s and any partner screen).  Every evicted screen then satisfies
;; install-screen's forall precondition and may be reinstalled.
;; Screen ?s: Inspected ✓, Tested ✗ — needs one certify before reinstallation.
;; Partner screen: Inspected ✓, Tested ✓ — ReadyToUse, can be installed immediately.
;;
;; Stratum 3 information preservation (if Validated holds for ?p):
;;   preInsCl_{FullyEquipped⊓Validated⊑ProductRecord}:
;;     AOrApCl_FullyEquipped ∧ AOrApCl_Validated ∧ ¬DelCl_ProductRecord → fires
;;   insCl_ProductRecord ← DelCl_FullyEquipped ∧ preInsCl → fires
;;   ins_ProductRecord: ProductRecord explicitly inserted in ABox
;;
;; Net state after update action:
;;   screenInstalledIn ✗  HasScreen ✗  HasCoreComponents ✗  FullyEquipped ✗
;;   Inspected ✓  Tested ✗  ReadyToUse ✗   (for screen ?s)
;;   Validated ✓  ProductRecord ✓ (explicitly asserted, persists through disassembly)
;;
;; Validate-then-rework is the only feasible ordering: without prior validation,
;; Stratum 3 does not fire and ProductRecord for ?p is permanently lost (no screen
;; can be reinstalled on ?p while the goal remains unsatisfied).

(:action remove-and-rework-screen
    :parameters (?s ?p)
    :precondition (and (screenInstalledIn ?s ?p)
                       (mko (ReadyToUse ?s)))
    :effect (and (not (FullyEquipped ?p))
                 (Inspected ?s)
                 (not (ReadyToUse ?s))))

)
