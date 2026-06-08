(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:objects
  a b c d e f g h i j k l m - object)
(:init
       (designer b)
       (engineer c)
       (developer e)
       (designer f)
       (developer i)
       (engineer k)
       (engineer m))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)