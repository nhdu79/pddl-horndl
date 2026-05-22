(define (domain Blocks)

(:predicates
	(onBlock ?x ?y)
	(on ?x ?y)
	(Block ?x)
	(Blocked ?x)
)

(:action move
  :parameters (?x ?y ?z)
  :precondition (and (not (mko (Blocked ?x)))
                     (not (mko (Blocked ?z)))
                     (mko (on ?x ?y))
  )
  :effect (and (not (on ?x ?y))
    (onBlock ?x ?z)
  )
)

)
