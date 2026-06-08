(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d - object)
(:init
       (designer a)
       (engineer d))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)