(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h i j k - object)
(:init
       (engineer d)
       (developer e)
       (developer f)
       (developer g)
       (engineer i)
       (developer k))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)