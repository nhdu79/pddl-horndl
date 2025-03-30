(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof11 robot)
       (aboveof0 robot)
       (belowof11 robot))
(:goal (and (column2 robot) (compatible_update) (row1 robot)))
)