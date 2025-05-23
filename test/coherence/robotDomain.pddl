(define (domain robot)
	(:predicates
		(Columns ?x)
		(Rows ?x)
		(Column0 ?x)
		(Column1 ?x)
		(RightOf0 ?x)
		(RightOf1 ?x)
		(LeftOf1 ?x)
		(LeftOf2 ?x)
		(Row0 ?x)
		(AboveOf0 ?x)
		(BelowOf1 ?x)
    (Clear ?x)
    (Blocked ?x)
	)
  (:derived (Clear ?x)
     (not (mko (Blocked ?x)))
  )
	(:action moveRight
		:parameters (?x)
		:precondition (and (mko (Columns ?x)))
		:effect (and
			(when (mko (RightOf0 ?x))
				(and (RightOf1 ?x))
				)
			(when (mko (LeftOf1 ?x))
				(and (LeftOf2 ?x))
				)
			(when (and (mko (LeftOf2 ?x)) (not (LeftOf1 ?x)))
				(and (not (LeftOf2 ?x)))
				)
			(when (mko (Column0 ?x))
				(and (Column1 ?x)
				(not (Column0 ?x)))
				)
			(when (mko (and (RightOf0 ?x) (LeftOf1 ?x)))
				(and (Column1 ?x))
				)
		))
	(:action moveLeft
		:parameters (?x)
		:precondition (and (mko (Columns ?x)))
		:effect (and
			(when (mko (LeftOf2 ?x))
				(and (LeftOf1 ?x))
				)
			(when (mko (RightOf1 ?x))
				(and (RightOf0 ?x)
				(RightOf1 ?x))
				)
			(when (mko (Column1 ?x))
				(and (Column0 ?x)
				(not (Column1 ?x)))
				)
			(when (mko (and (RightOf1 ?x) (LeftOf2 ?x)))
				(and (Column0 ?x))
				)
		))
)
