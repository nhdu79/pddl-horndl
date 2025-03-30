(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof17 robot)
       (aboveof0 robot)
       (belowof17 robot))
(:goal (and (column2 robot) (row1 robot) (not (incompatible_update))))
)