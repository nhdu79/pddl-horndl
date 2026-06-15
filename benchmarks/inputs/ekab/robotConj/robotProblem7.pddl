(define (problem robotProblem)
	(:domain robot)
	(:objects robot)
	(:init
		(RightOf0 robot)
		(LeftOf6 robot)
		(AboveOf0 robot)
		(BelowOf6 robot)
	)
	(:goal (and (mko (Column2 robot)) (mko (Row1 robot))))

)
