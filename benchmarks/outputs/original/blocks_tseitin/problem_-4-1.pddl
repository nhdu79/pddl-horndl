(define (problem BLOCKS-4-1)
(:domain BLOCKS)
(:init
       (ontable D T)
       (onblock B C)
       (onblock C A)
       (onblock A D))
(:goal (and (DATALOG_ON A B) (DATALOG_ON C A) (DATALOG_ON D C) (not (DATALOG_INCONSISTENT))))
)