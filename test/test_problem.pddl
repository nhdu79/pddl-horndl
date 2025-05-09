(define (problem robotProblem)
(:domain robot)
(:init
       (rightof0 robot)
       (leftof1 robot)
       (row0 robot))
(:goal (and (column1 robot) (row0 robot) (not (DATALOG_INCONSISTENT))))
)