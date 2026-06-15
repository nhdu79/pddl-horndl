(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d - object)
(:init
       (designer a)
       (engineer d))
(:goal (and (AUX12) (not (DATALOG_INCONSISTENT))))
)