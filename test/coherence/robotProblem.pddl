(define (problem robotProblem)
	(:domain robot)
	(:objects robot)
	(:init
		(RightOf0 robot)
		(LeftOf1 robot)
    (Row0 robot)
	)
	(:goal (and (Column1 robot) (Row0 robot)))
)
