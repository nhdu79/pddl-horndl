(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (engineer a)
       (developer b)
       (developer e))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (incompatible_update))))
)