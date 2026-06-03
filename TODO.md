- Mb change name of benchmark to phone?
- [ ] Inverse role functional for *InstalledIn
- [ ] Problem use (for all ?p (and (Phone ?P) (ProductRecord ?P)))
- [ ] Filter reachability for predicate after rule generation!

=========================

(nonHornAuxRainyEnvironment ?x ?y)
(nonHornAuxLowVisibilityEnvironment ?x ?y)
(nonHornAuxNearMovingObject ?x ?y)
(nonHornAuxVeryCloseObjectX ?x ?y)
(nonHornAuxNearObjectX ?x ?y)

(:derived (nonHornAuxRainyEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (Rain ?y1))))
(:derived (nonHornAuxLowVisibilityEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (LowVisibility ?y1))))
(:derived (nonHornAuxNearMovingObject ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (MovingObject ?y1))))
(:derived (nonHornAuxNearObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (mko Objectx ?y1))))
(:derived (nonHornAuxVeryCloseObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (veryClose ?y0 ?y1) (Objectx ?y1))))

(:derived (rainyEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (Rain ?y1))))
(:derived (lowVisibilityEnvironment ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (environment ?y0 ?y1) (LowVisibility ?y1))))
(:derived (nearMovingObject ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (MovingObject ?y1))))
(:derived (nearObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (near ?y0 ?y1) (Objectx ?y1))))
(:derived (veryCloseObjectX ?y0 ?y1)
          (exists (?y0 ?y1 - object) (and (veryClose ?y0 ?y1) (Objectx ?y1))))


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


(forall (?y0 ?y1)
      (when
        (mko (and (environment ?y0 ?y1) (Rain ?y1)))
        (and (rainyEnvironment ?y0 ?y1))
      )
    )
    (forall (?y0 ?y1)
      (when
        (mko (and (environment ?y0 ?y1) (LowVisibility ?y1)))
        (and (lowVisibilityEnvironment ?y0 ?y1))
      )
    )
    (forall (?y0 ?y1)
      (when
        (mko (and (near ?y0 ?y1) (MovingObject ?y1)))
        (and (nearMovingObject ?y0 ?y1))
      )
    )
    (forall (?y0 ?y1)
      (when
        (mko (and (near ?y0 ?y1) (Objectx ?y1)))
        (and (nearObjectX ?y0 ?y1))
      )
    )
    (forall (?y0 ?y1)
      (when
        (mko (and (veryClose ?y0 ?y1) (Objectx ?y1)))
        (and (veryCloseObjectX ?y0 ?y1))
      )
    )
