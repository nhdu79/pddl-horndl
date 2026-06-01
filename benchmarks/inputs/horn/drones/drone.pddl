(define (domain drone)

(:predicates
	(environment ?x ?y)
  (rainyEnvironment ?x ?y)
  (lowVisibilityEnvironment ?x ?y)
	(Rain ?x)
	(Drone ?x)
	(WetDrone ?x)
	(LowVisibility ?x)
	(near ?x ?y)
  (nearMovingObject ?x ?y)
  (nearObjectX ?x ?y)
	(veryClose ?x ?y)
  (veryCloseObjectX ?x ?y)
	(Human ?x)
	(MovingObject ?x)
	(Objectx ?x)
	(RiskOfPhysicalDamage ?x)
  (Tree ?x)
  (nonHornAuxRainyEnvironment ?x ?y)
  (nonHornAuxLowVisibilityEnvironment ?x ?y)
  (nonHornAuxNearMovingObject ?x ?y)
  (nonHornAuxVeryCloseObjectX ?x ?y)
  (nonHornAuxNearObjectX ?x ?y)
)

(:derived (nonHornAuxRainyEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (Rain ?y1))))
(:derived (nonHornAuxLowVisibilityEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (LowVisibility ?y1))))
(:derived (nonHornAuxNearMovingObject ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (MovingObject ?y1))))
(:derived (nonHornAuxNearObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (Objectx ?y1))))
(:derived (nonHornAuxVeryCloseObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (veryClose ?y0 ?y1) (Objectx ?y1))))

(:action Move
  :parameters (?x ?y)
  :precondition (and
    (mko (and (Drone ?x) (veryClose ?x ?y)))
    (not (mko (Objectx ?y)))
  )
  :effect (and
    (when
      (not (mko (WetDrone ?x)))
      (and (not (Drone ?x)) (Drone ?y))
    )
    (when
      (mko (WetDrone ?x))
      (and (not (WetDrone ?x)) (not (Drone ?x)) (WetDrone ?y))
    )
  )
)

(:action nonHornAuxAddRainyEnvironment
  :parameters (?x ?y)
  :precondition (nonHornAuxRainyEnvironment ?x ?y)
  :effect (rainyEnvironment ?x ?y))
(:action nonHornAuxAddLowVisibilityEnvironment
  :parameters (?x ?y)
  :precondition (nonHornAuxLowVisibilityEnvironment ?x ?y)
  :effect (lowVisibilityEnvironment ?x ?y))
(:action nonHornAuxAddNearMovingObject
  :parameters (?x ?y)
  :precondition (nonHornAuxNearMovingObject ?x ?y)
  :effect (nearMovingObject ?x ?y))
(:action nonHornAuxAddNearObjectX
  :parameters (?x ?y)
  :precondition (nonHornAuxNearMovingObject ?x ?y)
  :effect (nearObjectx ?x ?y))
(:action nonHornAuxAddVeryCloseObjectX
  :parameters (?x ?y)
  :precondition (nonHornAuxVeryCloseObjectX ?x ?y)
  :effect (veryCloseObjectX ?x ?y))

)
