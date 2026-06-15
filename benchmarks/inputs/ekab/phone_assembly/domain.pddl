(define (domain phone_assembly)

(:requirements :universal-preconditions :conditional-effects)

(:predicates
    ;; Installation roles — ABox facts managed by actions; functional in the TBox
    (screenInstalledIn ?s ?p)
    (batteryInstalledIn ?b ?p)
    (processorInstalledIn ?r ?p)

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
    ;; HasScreen/HasBattery/HasProcessor come from range axioms on the three roles.
    ;; FullyEquipped comes from the three-way conjunction HasScreen ⊓ HasBattery ⊓ HasProcessor.
    (HasScreen ?p)
    (HasBattery ?p)
    (HasProcessor ?p)
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
    (hasBrokenProcessor ?p ?r)

    ;; Ontology-derived defect/warranty status — queried via MKO
    ;; HasDefect:     ∃hasBrokenX ⊑ HasDefect  (three domain axioms, one per component type;
    ;;                no sub-property axiom — broken component does NOT auto-derive HasX)
    ;; BrokenPhone:   HasDefect ⊓ FullyEquipped ⊑ BrokenPhone  (FullyEquipped holds because
    ;;                the broken component's XInstalledIn role is explicit in the init ABox)
    ;; WarrantyClaim: HasDefect ⊓ UnderWarranty ⊑ WarrantyClaim (preserved by stratum 3)
    (HasDefect ?p)
    (BrokenPhone ?p)
    (WarrantyClaim ?p)

    ;; Warranty status — asserted directly in problem init for phones in warranty period
    (UnderWarranty ?p)

    ;; Repair workflow state
    ;; RepairAuthorized: set by authorize-repair; gates the repair action.
    (RepairAuthorized ?p)
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
;; Each install action requires ReadyToUse (certified), the corresponding HasX
;; slot to be empty, and no broken component of the same type currently tracked.
;; ¬mko(HasX) is the primary guard: broken phones carry XInstalledIn for the
;; broken component in the init ABox (so HasX holds) AND after repair the broken
;; component's XInstalledIn remains, keeping HasX true and blocking redundant
;; installation.  The forall guard additionally blocks install when hasBrokenX is
;; in the ABox but HasX somehow does not hold (belt-and-suspenders).
;;
;; After repair, HasX and FullyEquipped are cleared (via conditional Am effects),
;; so install-X becomes applicable and the spare IS installed in the minimal plan.

(:action install-screen
    :parameters (?s ?p)
    :precondition (and (mko (ReadyToUse ?s))
                       (mko (Component ?s))
                       (Screen ?s)
                       (Phone ?p)
                       (not (mko (HasScreen ?p)))
                       (forall (?b) (not (hasBrokenScreen ?p ?b))))
    :effect (screenInstalledIn ?s ?p))

(:action install-battery
    :parameters (?b ?p)
    :precondition (and (mko (ReadyToUse ?b))
                       (mko (Component ?b))
                       (Battery ?b)
                       (Phone ?p)
                       (not (mko (HasBattery ?p)))
                       (forall (?b2) (not (hasBrokenBattery ?p ?b2))))
    :effect (batteryInstalledIn ?b ?p))

(:action install-processor
    :parameters (?r ?p)
    :precondition (and (mko (ReadyToUse ?r))
                       (mko (Component ?r))
                       (Processor ?r)
                       (Phone ?p)
                       (not (mko (HasProcessor ?p)))
                       (forall (?b) (not (hasBrokenProcessor ?p ?b))))
    :effect (processorInstalledIn ?r ?p))

;; ── Repair workflow ───────────────────────────────────────────────────────────
;;
;; Repair is a two-step process: authorize-repair followed by repair.
;;
;; authorize-repair: a warranty check before the technician begins work.
;;   Requires mko(BrokenPhone ?p) — derivable from the initial ABox because each
;;   broken phone carries both hasBrokenX (→ HasDefect) and XInstalledIn for the
;;   broken component (→ HasX → FullyEquipped), so HasDefect ⊓ FullyEquipped →
;;   BrokenPhone holds from the start.  UnderWarranty held directly in the ABox.
;;   Sets RepairAuthorized to gate the repair action.
;;
;; repair: executes Am_BrokenPhone, driving the stratum 2 cascade via HasDefect
;;   as Min.  WarrantyClaim is preserved by stratum 3.
;;
;; Plan for any broken phone (authorize/repair independent of inspect/test;
;; both must complete before install-X due to the forall guard):
;;   authorize-repair(phone) → repair(phone)
;;   → inspect(spare) → test(spare) → install-X(spare, phone)   [5 steps]

(:action authorize-repair
    :parameters (?p)
    :precondition (and (Phone ?p) (mko (BrokenPhone ?p)) (UnderWarranty ?p))
    :effect (RepairAuthorized ?p))

;; repair — Am_BrokenPhone + Am_XInstalledIn (conditional) cascades ─────────
;;
;; Two Am requests fire simultaneously:
;;   1. Am_BrokenPhone  (primary effect — drives stratum 2 and stratum 3)
;;   2. Am_XInstalledIn(broken_comp, p)  (conditional: exactly one fires, for the
;;      broken component type whose hasBrokenX role is in the ABox)
;;
;; Stratum 2 cascade from Am_BrokenPhone:
;;   DelCl_BrokenPhone  [rule 5]
;;     → rule 14 (HasDefect ⊓ FullyEquipped ⊑ BrokenPhone):
;;         Min picks HasDefect (first non-Ap conjunct); AOrApCl_FullyEquipped required
;;         → DelCl_HasDefect(?p)
;;     → k=1 rule for each domain axiom (∃hasBrokenX ⊑ HasDefect):
;;         → DelCl_∃hasBrokenX(?p); rule 7 → DelCl_hasBrokenX(?p,?c)
;;         → rule 17: del_hasBrokenX(?p,?c)  [fires for the one role in the ABox]
;;
;; Stratum 2 cascade from Am_XInstalledIn(broken,p):
;;   DelCl_XInstalledIn → del_XInstalledIn  [rule 17, ABox fact present]
;;   Also propagates: rule 6 → DelCl_XInstalledIn_inv; rule 7 → DelCl_∃XInstalledIn_inv;
;;                    rule 14 k=1 → DelCl_HasX.
;;   Stratum 3 re-insertion of XInstalledIn is BLOCKED: rule 20 requires
;;   ¬DelCl_HasX, but DelCl_HasX IS set → preInsCl does not fire ✓
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
                 (forall (?s) (when (hasBrokenScreen    ?p ?s) (and (not (screenInstalledIn    ?s ?p)) (not (FullyEquipped ?p)))))
                 (forall (?b) (when (hasBrokenBattery   ?p ?b) (and (not (batteryInstalledIn   ?b ?p)) (not (FullyEquipped ?p)))))
                 (forall (?r) (when (hasBrokenProcessor ?p ?r) (and (not (processorInstalledIn ?r ?p)) (not (FullyEquipped ?p)))))))

)
