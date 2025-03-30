(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof3 robot)
       (aboveof0 robot)
       (belowof3 robot))
(:goal (and (column2 robot) (compatible_update) (row1 robot)))
)