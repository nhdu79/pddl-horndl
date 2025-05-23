(define (domain robot)
	(:predicates
		(Columns ?x)
		(Rows ?x)
		(Column0 ?x)
		(Column1 ?x)
		(Column2 ?x)
		(Column3 ?x)
		(Column4 ?x)
		(RightOf0 ?x)
		(RightOf1 ?x)
		(RightOf2 ?x)
		(RightOf3 ?x)
		(RightOf4 ?x)
		(LeftOf1 ?x)
		(LeftOf2 ?x)
		(LeftOf3 ?x)
		(LeftOf4 ?x)
		(LeftOf5 ?x)
		(Row0 ?x)
		(Row1 ?x)
		(Row2 ?x)
		(Row3 ?x)
		(Row4 ?x)
		(AboveOf0 ?x)
		(AboveOf1 ?x)
		(AboveOf2 ?x)
		(AboveOf3 ?x)
		(AboveOf4 ?x)
		(BelowOf1 ?x)
		(BelowOf2 ?x)
		(BelowOf3 ?x)
		(BelowOf4 ?x)
		(BelowOf5 ?x)
	)
	(:action moveRight
		:parameters (?x)
		:precondition (and (mko (Columns ?x)))
		:effect (and 
			(when (mko (RightOf0 ?x))
				(and (RightOf1 ?x))
				)
			(when (mko (RightOf1 ?x))
				(and (RightOf2 ?x))
				)
			(when (mko (RightOf2 ?x))
				(and (RightOf3 ?x))
				)
			(when (mko (RightOf3 ?x))
				(and (RightOf4 ?x))
				)
			(when (mko (LeftOf1 ?x))
				(and (LeftOf2 ?x)
				(not (LeftOf1 ?x)))
				)
			(when (and (mko (LeftOf2 ?x)) (not (LeftOf1 ?x)))
				(and (LeftOf3 ?x)
				(not (LeftOf2 ?x)))
				)
			(when (and (mko (LeftOf3 ?x)) (not (LeftOf2 ?x)))
				(and (LeftOf4 ?x)
				(not (LeftOf3 ?x)))
				)
			(when (and (mko (LeftOf4 ?x)) (not (LeftOf3 ?x)))
				(and (LeftOf5 ?x)
				(not (LeftOf4 ?x)))
				)
			(when (mko (Column0 ?x))
				(and (Column1 ?x)
				(not (Column0 ?x)))
				)
			(when (mko (Column1 ?x))
				(and (Column2 ?x)
				(not (Column1 ?x)))
				)
			(when (mko (Column2 ?x))
				(and (Column3 ?x)
				(not (Column2 ?x)))
				)
			(when (mko (Column3 ?x))
				(and (Column4 ?x)
				(not (Column3 ?x)))
				)
			(when (mko (and (RightOf0 ?x) (LeftOf1 ?x)))
				(and (Column1 ?x))
				)
			(when (mko (and (RightOf1 ?x) (LeftOf2 ?x)))
				(and (Column2 ?x))
				)
			(when (mko (and (RightOf2 ?x) (LeftOf3 ?x)))
				(and (Column3 ?x))
				)
			(when (mko (and (RightOf3 ?x) (LeftOf4 ?x)))
				(and (Column4 ?x))
				)
		))
	(:action moveLeft
		:parameters (?x)
		:precondition (and (mko (Columns ?x)))
		:effect (and 
			(when (mko (LeftOf2 ?x))
				(and (LeftOf1 ?x))
				)
			(when (mko (LeftOf3 ?x))
				(and (LeftOf2 ?x))
				)
			(when (mko (LeftOf4 ?x))
				(and (LeftOf3 ?x))
				)
			(when (mko (LeftOf5 ?x))
				(and (LeftOf4 ?x))
				)
			(when (and (mko (RightOf1 ?x)) (not (RightOf2 ?x)))
				(and (RightOf0 ?x)
				(not (RightOf1 ?x)))
				)
			(when (and (mko (RightOf2 ?x)) (not (RightOf3 ?x)))
				(and (RightOf1 ?x)
				(not (RightOf2 ?x)))
				)
			(when (and (mko (RightOf3 ?x)) (not (RightOf4 ?x)))
				(and (RightOf2 ?x)
				(not (RightOf3 ?x)))
				)
			(when (mko (RightOf4 ?x))
				(and (RightOf3 ?x)
				(not (RightOf4 ?x)))
				)
			(when (mko (Column1 ?x))
				(and (Column0 ?x)
				(not (Column1 ?x)))
				)
			(when (mko (Column2 ?x))
				(and (Column1 ?x)
				(not (Column2 ?x)))
				)
			(when (mko (Column3 ?x))
				(and (Column2 ?x)
				(not (Column3 ?x)))
				)
			(when (mko (Column4 ?x))
				(and (Column3 ?x)
				(not (Column4 ?x)))
				)
			(when (mko (and (RightOf1 ?x) (LeftOf2 ?x)))
				(and (Column0 ?x))
				)
			(when (mko (and (RightOf2 ?x) (LeftOf3 ?x)))
				(and (Column1 ?x))
				)
			(when (mko (and (RightOf3 ?x) (LeftOf4 ?x)))
				(and (Column2 ?x))
				)
			(when (mko (and (RightOf4 ?x) (LeftOf5 ?x)))
				(and (Column3 ?x))
				)
		))
	(:action moveUp
		:parameters (?x)
		:precondition (and (mko (Rows ?x)))
		:effect (and 
			(when (mko (AboveOf0 ?x))
				(and (AboveOf1 ?x))
				)
			(when (mko (AboveOf1 ?x))
				(and (AboveOf2 ?x))
				)
			(when (mko (AboveOf2 ?x))
				(and (AboveOf3 ?x))
				)
			(when (mko (AboveOf3 ?x))
				(and (AboveOf4 ?x))
				)
			(when (mko (BelowOf1 ?x))
				(and (BelowOf2 ?x)
				(not (BelowOf1 ?x)))
				)
			(when (and (mko (BelowOf2 ?x)) (not (BelowOf1 ?x)))
				(and (BelowOf3 ?x)
				(not (BelowOf2 ?x)))
				)
			(when (and (mko (BelowOf3 ?x)) (not (BelowOf2 ?x)))
				(and (BelowOf4 ?x)
				(not (BelowOf3 ?x)))
				)
			(when (and (mko (BelowOf4 ?x)) (not (BelowOf3 ?x)))
				(and (BelowOf5 ?x)
				(not (BelowOf4 ?x)))
				)
			(when (mko (Row0 ?x))
				(and (Row1 ?x)
				(not (Row0 ?x)))
				)
			(when (mko (Row1 ?x))
				(and (Row2 ?x)
				(not (Row1 ?x)))
				)
			(when (mko (Row2 ?x))
				(and (Row3 ?x)
				(not (Row2 ?x)))
				)
			(when (mko (Row3 ?x))
				(and (Row4 ?x)
				(not (Row3 ?x)))
				)
			(when (mko (and (AboveOf0 ?x) (BelowOf1 ?x)))
				(and (Row1 ?x))
				)
			(when (mko (and (AboveOf1 ?x) (BelowOf2 ?x)))
				(and (Row2 ?x))
				)
			(when (mko (and (AboveOf2 ?x) (BelowOf3 ?x)))
				(and (Row3 ?x))
				)
			(when (mko (and (AboveOf3 ?x) (BelowOf4 ?x)))
				(and (Row4 ?x))
				)
		))
	(:action moveDown
		:parameters (?x)
		:precondition (and (mko (Rows ?x)))
		:effect (and 
			(when (mko (BelowOf2 ?x))
				(and (BelowOf1 ?x))
				)
			(when (mko (BelowOf3 ?x))
				(and (BelowOf2 ?x))
				)
			(when (mko (BelowOf4 ?x))
				(and (BelowOf3 ?x))
				)
			(when (mko (BelowOf5 ?x))
				(and (BelowOf4 ?x))
				)
			(when (and (mko (AboveOf1 ?x)) (not (AboveOf2 ?x)))
				(and (AboveOf0 ?x)
				(not (AboveOf1 ?x)))
				)
			(when (and (mko (AboveOf2 ?x)) (not (AboveOf3 ?x)))
				(and (AboveOf1 ?x)
				(not (AboveOf2 ?x)))
				)
			(when (and (mko (AboveOf3 ?x)) (not (AboveOf4 ?x)))
				(and (AboveOf2 ?x)
				(not (AboveOf3 ?x)))
				)
			(when (mko (AboveOf4 ?x))
				(and (AboveOf3 ?x)
				(not (AboveOf4 ?x)))
				)
			(when (mko (Row1 ?x))
				(and (Row0 ?x)
				(not (Row1 ?x)))
				)
			(when (mko (Row2 ?x))
				(and (Row1 ?x)
				(not (Row2 ?x)))
				)
			(when (mko (Row3 ?x))
				(and (Row2 ?x)
				(not (Row3 ?x)))
				)
			(when (mko (Row4 ?x))
				(and (Row3 ?x)
				(not (Row4 ?x)))
				)
			(when (mko (and (AboveOf1 ?x) (BelowOf2 ?x)))
				(and (Row0 ?x))
				)
			(when (mko (and (AboveOf2 ?x) (BelowOf3 ?x)))
				(and (Row1 ?x))
				)
			(when (mko (and (AboveOf3 ?x) (BelowOf4 ?x)))
				(and (Row2 ?x))
				)
			(when (mko (and (AboveOf4 ?x) (BelowOf5 ?x)))
				(and (Row3 ?x))
				)
		))

)