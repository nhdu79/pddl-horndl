(define (domain Blocks)

(:predicates
	(onBlock ?x ?y)
	(onTable ?x ?y)
	(on ?x ?y)
	(Block ?x)
	(Table ?x)
	(Blocked ?x)
  (Holding ?x)
  (Clear ?x)
  (HandEmpty)
)

(:derived (Clear ?x)
  (not (mko (Blocked ?x)))
)

(:derived (HandEmpty)
  (not (mko (exists (?x) (Holding ?x))))
)

(:action pick-up
  :parameters (?x ?y)
  :precondition (and (mko (on ?x ?y))
                     (Clear ?x)
                     (HandEmpty)
  )
  :effect (and (not (on ?x ?y))
               (Holding ?x)
  )
)

(:action put-down
  :parameters (?x ?y)
  :precondition (and (Holding ?x)
                     (Clear ?y))
  :effect (and (not (Holding ?x))
               (when (mko (Table ?y))
                     (onTable ?x ?y))
               (when (mko (Block ?y))
                     (onBlock ?x ?y))
  )
)

)
