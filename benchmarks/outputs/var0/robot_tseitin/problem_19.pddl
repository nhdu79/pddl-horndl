(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof18 robot)
       (aboveof0 robot)
       (belowof18 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)