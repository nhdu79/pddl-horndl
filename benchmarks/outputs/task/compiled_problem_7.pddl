(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer a)
       (designer b)
       (developer c)
       (designer f))
(:goal (and (AUX80) (not (incompatible_update))))
)