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
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (DATALOG_INCONSISTENT))))
)