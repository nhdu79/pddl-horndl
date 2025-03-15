(define (domain Test)
(:constants
  a - object)
(:predicates
  (preda ?x - object)
  (predb ?x - object)
  (predc ?x - object)
  (predd ?x - object)
  (prede ?x - object)
  (predh ?x - object))
(:derived (predh ?x0 - object)
          (or
            (preda ?x0)
            (and (predb ?x0) (exists (?x1 - object) (predc ?x1)))
            (and (forall (?x2 - object) (predd ?x2)) (or (prede ?x0) (not (prede ?x0))))
          )
)
(:action add
  :parameters (?x - object)
  :precondition (and (not (preda ?x)) (forall (?x1 - object) (predc ?x1)))
  :effect (when (exists (?x - object) (and (preda ?x) (or (predb ?x) (predc ?x))))
                  (and (preda ?x) (predb ?x)))
            )
)
