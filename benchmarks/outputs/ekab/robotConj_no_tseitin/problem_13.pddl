(define (problem robotProblem)
(:domain robot)
(:objects
  robot - object)
(:init
       (rightof0 robot)
       (leftof12 robot)
       (aboveof0 robot)
       (belowof12 robot))
(:goal (and (DATALOG_COLUMN2 robot) (DATALOG_ROW1 robot) (not (DATALOG_INCONSISTENT))))
)