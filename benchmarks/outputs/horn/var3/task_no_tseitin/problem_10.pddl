(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h i j - object)
(:init
       (engineer a)
       (developer f)
       (engineer h)
       (developer i)
       (designer j))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)