(define (problem blocksProb)
(:domain Blocks)
(:init
       (onblock A D)
       (onblock B C))
(:goal (and (DATALOG_ON A B) (DATALOG_ON B C) (not (updating))))
)