(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof109 robot)
       (aboveof0 robot)
       (belowof109 robot))
(:goal (and (column2 robot) (row1 robot) (not (incompatible_update))))
)