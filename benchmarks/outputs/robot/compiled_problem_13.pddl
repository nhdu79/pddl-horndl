(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof12 robot)
       (aboveof0 robot)
       (belowof12 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)