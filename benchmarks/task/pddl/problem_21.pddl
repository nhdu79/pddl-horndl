(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer a)
       (developer d)
       (engineer f)
       (designer g)
       (developer h)
       (designer i)
       (engineer k)
       (engineer n)
       (developer o)
       (engineer p)
       (developer s)
       (developer t))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (DATALOG_INCONSISTENT))))
)