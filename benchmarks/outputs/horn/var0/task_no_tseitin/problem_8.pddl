(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h - object)
(:init
       (engineer a)
       (designer f)
       (engineer g)
       (engineer h))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)