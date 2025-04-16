(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof5 robot)
       (aboveof0 robot)
       (belowof5 robot))
(:goal (and (column2 robot) (row1 robot) (not (updating))))
)