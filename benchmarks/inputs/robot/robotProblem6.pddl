(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf5 robot)
		(AboveOf0 robot)
		(BelowOf5 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)