(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf8 robot)
		(AboveOf0 robot)
		(BelowOf8 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)