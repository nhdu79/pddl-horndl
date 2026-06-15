(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h - object)
(:init
       (engineer a)
       (designer f)
       (engineer g)
       (engineer h))
(:goal (and (AUX12) (not (DATALOG_INCONSISTENT))))
)