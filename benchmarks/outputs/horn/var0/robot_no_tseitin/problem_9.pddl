(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof8 robot)
       (aboveof0 robot)
       (belowof8 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)