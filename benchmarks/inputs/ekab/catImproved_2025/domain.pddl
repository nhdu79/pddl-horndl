(define (domain BTcat)

(:predicates 
	(cat ?x)
	(orangecat ?x)
	(blackcat ?x)
	(bomb ?x)
	(jagerbomb ?x)
	(dynamitebomb ?x)
	(smokebomb ?x)
	(contains ?x ?y)
	(package ?x)
	(disarmed ?x)
	(obj ?x)
)

(:action dunk
  :parameters (?x ?y)
  :precondition (mko (package ?x))
  :effect (when (mko (and (contains ?x ?y) (bomb ?y)))
                  (and (disarmed ?x)))
            )

(:action let_the_cats_out
  :parameters (?x ?y)
  :precondition (mko (package ?x))
  :effect (when (mko (and (contains ?x ?y) (cat ?y)))
                  (and (not (package ?x))))
            )

)

