(define (problem robotProblem)
    (:domain robot)
	(:objects robot)
	(:init
		(RightOf1 robot)
		(LeftOf9 robot)
		(AboveOf0 robot)
		(BelowOf9 robot)
	)
	(:goal (and (Column2 robot) (Row1 robot)))

)