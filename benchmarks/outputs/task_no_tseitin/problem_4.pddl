(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (designer a)
       (engineer d))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (incompatible_update))))
)