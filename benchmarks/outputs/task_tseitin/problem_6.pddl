(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (engineer a)
       (developer b)
       (developer e))
(:goal (and (AUX80) (not (incompatible_update))))
)