(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof4 robot)
       (aboveof0 robot)
       (belowof4 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)