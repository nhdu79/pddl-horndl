(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer a)
       (designer b)
       (developer c)
       (designer f))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)