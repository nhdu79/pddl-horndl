(define (problem robotProblem)
(:domain robot)
(:init
       (rightof1 robot)
       (leftof8 robot)
       (aboveof0 robot)
       (belowof8 robot))
(:goal (and (column2 robot) (compatible_update) (row1 robot)))
)