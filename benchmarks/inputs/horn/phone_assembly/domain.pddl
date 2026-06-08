(define (domain phone_assembly)

(:requirements :universal-preconditions)

(:predicates
    ;; Installation roles — ABox facts managed by actions; functional in the TBox
    (screenInstalledIn ?s ?p)
    (batteryInstalledIn ?b ?p)
    (boardInstalledIn ?r ?p)

    ;; Typing predicates — set in problem init
    (Phone ?x)
    (Screen ?x)
    (Battery ?x)
    (Processor ?x)

    ;; Ontology-derived typing — Component is inferred from Screen/Battery/Processor
    ;; via TBox axioms Screen ⊑ Component, Battery ⊑ Component, Processor ⊑ Component
    (Component ?x)

    ;; Certification status — directly managed by actions
    (Inspected ?x)
    (Tested ?x)

    ;; Ontology-derived assembly status — queried via MKO
    ;; HasScreen/HasBattery/HasBoard come from range axioms on the three roles.
    ;; FullyEquipped comes from the three-way conjunction HasScreen ⊓ HasBattery ⊓ HasBoard.
    (HasScreen ?p)
    (HasBattery ?p)
    (HasBoard ?p)
    (FullyEquipped ?p)

    ;; Ontology-derived certification status — queried via MKO
    (ReadyToUse ?x)

    ;; Defect-tracking roles — one per component type, asserted in problem init.
    ;; hasBrokenX(p, c): phone p has broken component c; derives HasDefect(p) via
    ;; the three domain axioms in the TBox.  Broken components are never typed as
    ;; Screen/Battery/Processor, so they cannot be inspected or installed.
    ;; At most one hasBrokenX role is asserted per phone in any problem instance.
    (hasBrokenScreen ?p ?s)
    (hasBrokenBattery ?p ?b)
    (hasBrokenBoard ?p ?r)

    ;; Ontology-derived defect/warranty status — queried via MKO
    ;; HasDefect:     ∃hasBrokenX ⊑ HasDefect   (three domain axioms, one per component type)
    ;; BrokenPhone:   HasDefect ⊓ FullyEquipped ⊑ BrokenPhone
    ;; WarrantyClaim: HasDefect ⊓ UnderWarranty ⊑ WarrantyClaim (preserved by stratum 3)
    (HasDefect ?p)
    (BrokenPhone ?p)
    (WarrantyClaim ?p)

    ;; Warranty status — asserted directly in problem init for phones in warranty period
    (UnderWarranty ?p)

    ;; Repair workflow state
    ;; RepairAuthorized: set by authorize-repair; gates the repair action.
    ;; Repaired: set directly by the repair action.
    (RepairAuthorized ?p)
    (Repaired ?p)
)

;; ── Certification pipeline ───────────────────────────────────────────────────
;;
;; Two-step certification: inspect then test.  The predicates remain distinct so
;; that Inspected can be shielded (Ap_Inspected) independently of Tested,
;; exploiting the LTR Min rule (stratum 2, rules 13-14) in ReadyToUse derivations.

(:action inspect
    :parameters (?c)
    :precondition (mko (Component ?c))
    :effect (Inspected ?c))

(:action test
    :parameters (?c)
    :precondition (and (mko (Component ?c)) (Inspected ?c))
    :effect (Tested ?c))

;; ── Component installation ───────────────────────────────────────────────────
;;
;; Each install action requires ReadyToUse (certified) and the corresponding
;; HasX slot to be empty on the target phone.  InverseFunctional constraints
;; on the three roles enforce that each component can be installed in at most
;; one phone at a time.

(:action install-screen
    :parameters (?s ?p)
    :precondition (and (mko (ReadyToUse ?s))
                       (mko (Component ?s))
                       (Screen ?s)
                       (Phone ?p)
                       (not (mko (HasScreen ?p))))
    :effect (screenInstalledIn ?s ?p))

(:action install-battery
    :parameters (?b ?p)
    :precondition (and (mko (ReadyToUse ?b))
                       (mko (Component ?b))
                       (Battery ?b)
                       (Phone ?p)
                       (not (mko (HasBattery ?p))))
    :effect (batteryInstalledIn ?b ?p))

(:action install-board
    :parameters (?r ?p)
    :precondition (and (mko (ReadyToUse ?r))
                       (mko (Component ?r))
                       (Processor ?r)
                       (Phone ?p)
                       (not (mko (HasBoard ?p))))
    :effect (boardInstalledIn ?r ?p))

;; ── Repair workflow ───────────────────────────────────────────────────────────
;;
;; Repair is a two-step process: authorize-repair followed by repair.
;;
;; authorize-repair: a warranty check before the technician begins work.
;;   Requires mko(BrokenPhone ?p) — only satisfiable after the spare component
;;   has been installed (restoring FullyEquipped), and UnderWarranty holds directly
;;   in the ABox.  Sets RepairAuthorized to gate the repair action.
;;
;; repair: executes Am_BrokenPhone, driving the stratum 2 cascade and
;;   stratum 3 WarrantyClaim preservation (see cascade detail below).
;;
;; Plan for any broken phone:
;;   inspect(spare) → test(spare) → install-X(spare, phone)
;;   → authorize-repair(phone) → repair(phone)   [5 steps]

(:action authorize-repair
    :parameters (?p)
    :precondition (and (Phone ?p) (mko (BrokenPhone ?p)) (UnderWarranty ?p))
    :effect (RepairAuthorized ?p))

;; repair — Am_BrokenPhone cascade + stratum 3 warranty preservation ────────
;;
;; Stratum 2 cascade from Am_BrokenPhone:
;;   DelCl_BrokenPhone
;;     → rule 14 (HasDefect ⊓ FullyEquipped ⊑ BrokenPhone):
;;         Min picks HasDefect (first non-Ap); AOrApCl_FullyEquipped required
;;         → DelCl_HasDefect
;;     → k=1 rule for each of the three domain axioms (∃hasBrokenX ⊑ HasDefect):
;;         → DelCl_∃hasBrokenX(?p)
;;     → rule 7: DelCl_hasBrokenX(?p, ?c)
;;     → rule 17: del_hasBrokenX(?p, ?c)   [fires only for the role in the ABox]
;;
;; Stratum 3 — WarrantyClaim preservation (fires when UnderWarranty holds):
;;   preInsCl_{HasDefect⊓UnderWarranty⊑WarrantyClaim}:
;;       AOrApCl_HasDefect ✓  AOrApCl_UnderWarranty ✓  ¬DelCl_WarrantyClaim ✓  → fires
;;   insCl_WarrantyClaim ← DelCl_HasDefect ∧ preInsCl → ins_WarrantyClaim
;;   WarrantyClaim is explicitly asserted in ABox — persists after defect is fixed.

(:action repair
    :parameters (?p)
    :precondition (and (Phone ?p) (mko (BrokenPhone ?p)) (RepairAuthorized ?p))
    :effect (and (not (BrokenPhone ?p))
                 (Repaired ?p)))

)
