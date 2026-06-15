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
    (NonHornAuxUpdate)
)

(:action _Supplement
  :parameters ()
  :precondition (not (NonHornAuxUpdate))
  :effect (and
    (forall (?x ?y)
      (when (and (environment ?x ?y) (Rain ?y)) (environmentRain ?x ?y))
    )

    (forall (?x ?y)
      (when (and (environmentRain ?x ?y) (not (Rain ?y))) (not (environmentRain ?x ?y)))
    )

    (forall (?x ?y)
      (when (and (environment ?x ?y) (mko (LowVisibility ?y))) (environmentLow ?x ?y))
    )

    (forall (?x ?y)
      (when (and (environmentLow ?x ?y) (not (mko (LowVisibility ?y)))) (not (environmentLow ?x ?y)))
    )

    (forall (?x ?y)
      (when (and (mko (near ?x ?y)) (mko (Objectx ?y))) (nearObject ?x ?y))
    )

    (forall (?x ?y)
      (when (and (nearObject ?x ?y) (not (mko (Objectx ?y)))) (not (nearObject ?x ?y)))
    )

    (forall (?x ?y)
      (when (and (mko (near ?x ?y)) (mko (MovingObject ?y))) (nearMoving ?x ?y))
    )

    (forall (?x ?y)
      (when (and (nearMoving ?x ?y) (not (mko (MovingObject ?y)))) (not (nearMoving ?x ?y)))
    )

    (forall (?x ?y)
      (when (and (veryClose ?x ?y) (mko (Objectx ?y))) (veryCloseObject ?x ?y))
    )

    (forall (?x ?y)
      (when (and (veryCloseObject ?x ?y) (not (mko (Objectx ?y)))) (not (veryCloseObject ?x ?y)))
    )

    (NonHornAuxUpdate)
  )
)

(:action Move
    :parameters (?x ?y)
    :precondition (and
        (mko (and (Drone ?x) (veryClose ?x ?y)))
        (not (mko (Objectx ?y)))
        (NonHornAuxUpdate)
    )
    :effect (and

        ;; ── Transfer drone/wetdrone ───────────────────────────────────────────
        (when (not (mko (WetDrone ?x)))
            (and (not (Drone ?x)) (Drone ?y)))

        (when (mko (WetDrone ?x))
            (and (not (WetDrone ?x)) (not (Drone ?x)) (WetDrone ?y)))

        (not (NonHornAuxUpdate))
    )
)
)
