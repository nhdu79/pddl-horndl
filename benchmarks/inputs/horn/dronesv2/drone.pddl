(define (domain drone)

(:requirements :conditional-effects)

(:predicates
    ;; Spatial roles — grid topology, set in problem init, never modified by actions
    (near ?x ?y)
    (veryClose ?x ?y)
    ;; Environment role — cell property, set in problem init, never modified by actions
    (environment ?x ?y)
    ;; Drone/object type predicates
    (Drone ?x)
    (WetDrone ?x)
    (Human ?x)
    (MovingObject ?x)
    (Objectx ?x)
    (Tree ?x)
    ;; Environment status predicates
    (Rain ?x)
    (LowVisibility ?x)
    ;; Derived risk
    (RiskOfPhysicalDamage ?x)

    ;; ── Sub-role predicates (Option A: sub-role splitting) ─────────────────────
    ;;
    ;; These replace the qualified someValuesFrom fillers of the original ontology.
    ;; Each fact (subRole a b) means: near/veryClose(a,b) holds AND b satisfies the
    ;; original filler concept.  The sub-role inclusions in TTL.owl ensure Clipper
    ;; uses them for UCQ rewriting.
    ;;
    ;; Invariant maintained by Move: subRole(z, pos) iff the base spatial relation
    ;; holds between z and pos AND pos currently holds an object of the qualifying type.
    ;;
    ;; environmentLow/Rain are cell properties — set in init, NOT updated by Move.
    ;; nearObject, nearMoving, veryCloseObject change whenever a drone moves.

    (environmentLow ?x ?y)      ; x has a LowVisibility environment y  (⊑ environment)
    (environmentRain ?x ?y)     ; x has a Rain environment y            (⊑ environmentLow)
    (nearObject ?x ?y)          ; x is near Objectx y                   (⊑ near)
    (nearMoving ?x ?y)          ; x is near MovingObject y              (⊑ near)
    (veryCloseObject ?x ?y)     ; x is veryClose to Objectx y           (⊑ veryClose)
)


;; ── Move action ───────────────────────────────────────────────────────────────
;;
;; Moves a drone (or WetDrone) from position ?x to adjacent empty position ?y.
;;
;; Preconditions:
;;   • TBox derives Drone(?x) and veryClose(?x,?y)
;;   • Target ?y must not be occupied by any Objectx (Human, Tree, or other Drone)
;;
;; Effects:
;;   1. Transfer Drone / WetDrone to ?y.
;;   2. Update sub-role ABox facts that track which cells are near/veryClose to
;;      a currently-occupied Objectx/MovingObject position:
;;        - Remove {near,veryClose}Object/nearMoving entries pointing TO ?x
;;          (drone left ?x; ?x is no longer an Objectx / MovingObject)
;;        - Add the same entries pointing TO ?y
;;          (drone arrived at ?y; ?y is now an Objectx / MovingObject)
;;
;; Why both `near ?z ?x` and `veryClose ?z ?x` in nearObject/nearMoving effects:
;;   nearObject/nearMoving ⊑ near, and `near` covers BOTH diagonal (explicit near
;;   ABox facts) AND orthogonal (via veryClose ⊑ near).  Because both directions of
;;   near and veryClose are stored in the ABox, the two forall clauses together cover
;;   all neighbours of ?x and ?y.
;;
;; environmentLow and environmentRain are cell properties — they are NOT updated by
;; Move.  A drone entering an env cell automatically satisfies ∃environmentLow.⊤
;; via the existing ABox fact on that cell; a drone leaving an env cell no longer
;; satisfies it.

(:action Move
    :parameters (?x ?y)
    :precondition (and
        (mko (and (Drone ?x) (veryClose ?x ?y)))
        (not (mko (Objectx ?y)))
    )
    :effect (and

        ;; ── Transfer drone/wetdrone ───────────────────────────────────────────
        (when (not (mko (WetDrone ?x)))
            (and (not (Drone ?x)) (Drone ?y)))
        (when (mko (WetDrone ?x))
            (and (not (WetDrone ?x)) (not (Drone ?x)) (WetDrone ?y)))

        ;; ── nearObject: ?x vacated (no longer Objectx); ?y occupied (now Objectx)
        (forall (?z) (when (near ?z ?x)      (not (nearObject ?z ?x))))
        (forall (?z) (when (veryClose ?z ?x) (not (nearObject ?z ?x))))
        (forall (?z) (when (near ?z ?y)      (nearObject ?z ?y)))
        (forall (?z) (when (veryClose ?z ?y) (nearObject ?z ?y)))

        ;; ── nearMoving: same update (MovingObject ⊆ Objectx, drone is MovingObject)
        (forall (?z) (when (near ?z ?x)      (not (nearMoving ?z ?x))))
        (forall (?z) (when (veryClose ?z ?x) (not (nearMoving ?z ?x))))
        (forall (?z) (when (near ?z ?y)      (nearMoving ?z ?y)))
        (forall (?z) (when (veryClose ?z ?y) (nearMoving ?z ?y)))

        ;; ── veryCloseObject: only veryClose (orthogonal) neighbours
        (forall (?z) (when (veryClose ?z ?x) (not (veryCloseObject ?z ?x))))
        (forall (?z) (when (veryClose ?z ?y) (veryCloseObject ?z ?y)))
    )
)

)
