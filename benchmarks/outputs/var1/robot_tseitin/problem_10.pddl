(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof9 robot)
       (aboveof0 robot)
       (belowof9 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)