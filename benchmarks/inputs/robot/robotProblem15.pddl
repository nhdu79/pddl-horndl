(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf14 robot)
		(AboveOf0 robot)
		(BelowOf14 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)