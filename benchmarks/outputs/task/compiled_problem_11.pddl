(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (engineer d)
       (developer e)
       (developer f)
       (developer g)
       (engineer i)
       (developer k))
(:goal (and (AUX239) (not (incompatible_update))))
)