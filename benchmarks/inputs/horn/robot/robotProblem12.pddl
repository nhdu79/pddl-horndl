(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf11 robot)
		(AboveOf0 robot)
		(BelowOf11 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)