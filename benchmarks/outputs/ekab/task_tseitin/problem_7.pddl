(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g - object)
(:init
       (developer a)
       (designer b)
       (developer c)
       (designer f))
(:goal (and (AUX12) (not (DATALOG_INCONSISTENT))))
)