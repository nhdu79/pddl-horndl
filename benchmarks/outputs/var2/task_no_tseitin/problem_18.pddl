(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (designer a)
       (engineer c)
       (developer d)
       (designer f)
       (designer g)
       (engineer h)
       (engineer j)
       (developer m)
       (developer n)
       (engineer p))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (updating))))
)