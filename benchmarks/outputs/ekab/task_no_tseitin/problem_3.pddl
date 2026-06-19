(define (problem taskAssigment_problem)
(:domain taskAssigment)
(:init
       (developer c))
(:goal (and (exists (?x ?y - object) (and (DATALOG_QUERY0 ?x ?y) (not (= ?x ?y)))) (not (DATALOG_INCONSISTENT))))
)