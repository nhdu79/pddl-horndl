(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer c)
       (designer d))
(:goal (and (exists (?x ?y) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)