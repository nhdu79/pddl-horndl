(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (engineer a)
       (designer f)
       (engineer g)
       (engineer h))
(:goal (and (exists (?x ?y) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)