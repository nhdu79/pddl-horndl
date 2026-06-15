(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h i - object)
(:init
       (developer a)
       (designer d)
       (developer e)
       (designer f)
       (engineer g))
(:goal (and (AUX12) (not (DATALOG_INCONSISTENT))))
)