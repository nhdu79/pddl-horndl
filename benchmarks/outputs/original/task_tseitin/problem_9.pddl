(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer a)
       (designer d)
       (developer e)
       (designer f)
       (engineer g))
(:goal (and (AUX12) (not (DATALOG_INCONSISTENT))))
)