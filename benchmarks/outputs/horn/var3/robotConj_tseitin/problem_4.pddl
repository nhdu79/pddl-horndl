(define (problem robotProblem)
(:domain robot)
(:init
       (rightof0 robot)
       (leftof3 robot)
       (aboveof0 robot)
       (belowof3 robot))
(:goal (and (DATALOG_COLUMN2 robot) (DATALOG_ROW1 robot) (not (updating))))
)