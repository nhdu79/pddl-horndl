(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (engineer a)
       (designer f)
       (engineer g)
       (engineer h))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)