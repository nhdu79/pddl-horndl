(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f - object)
(:init
       (engineer a)
       (developer b)
       (developer e))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (DATALOG_INCONSISTENT))))
)