(define (problem robotProblem)
(:domain robot)
(:init
       (rightof0 robot)
       (leftof2 robot)
       (aboveof0 robot)
       (belowof2 robot))
(:goal (and (DATALOG_COLUMN2 robot) (DATALOG_ROW1 robot) (not (updating))))
)