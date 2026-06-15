(define (domain BTcat)

(:predicates
	(cat ?x)
	(bomb ?x)
	(contains ?x ?y)
	(package ?x)
	(disarmed ?x)
	(objectx ?x)
)

(:action dunk
  :parameters (?x ?y)
  :precondition (and (mko (and (contains ?x ?y) (bomb ?y))))
  :effect (and (disarmed ?x))
)
(:action let_the_cats_out
  :parameters (?x ?y)
  :precondition (mko (contains ?x ?y))
  :effect (and (not (contains ?x ?y)) (not (package ?x)) (cat ?y))
)
)
