(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer a)
       (designer b)
       (developer c)
       (designer f))
(:goal (and (AUX10) (not (DATALOG_INCONSISTENT))))
)