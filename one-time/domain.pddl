(define (domain Test)
(:constants
  a - object)
(:predicates
  (preda ?x - object)
  (predb ?x - object)
  (predc ?x - object)
  (predd ?x - object))
(:derived (predd ?x0 - object)
          (and (preda ?x0) (or (predb ?x0) (forall (?x1 - object) (predc ?x1)))))
(:action add
  :parameters (?x - object)
  :precondition (and (not (preda ?x)) (forall (?x1 - object) (predc ?x1)))
  :effect (when (exists (?x - object) (and (preda ?x) (or (predb ?x) (predc ?x))))
                  (and (preda ?x) (predb ?x)))
            )
)
