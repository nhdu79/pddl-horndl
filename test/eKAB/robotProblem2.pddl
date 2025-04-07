(define (problem robotProblem)
	(:domain robot)
	(:objects robot)
	(:init
		(RightOf0 robot)
		(LeftOf1 robot)
		(AboveOf0 robot)
		(BelowOf2 robot)
	)
	(:goal (and (Column1 robot) (Row1 robot)))

)
