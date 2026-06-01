(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf7 robot)
		(AboveOf0 robot)
		(BelowOf7 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)