(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c - object)
(:init
       (developer c))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)