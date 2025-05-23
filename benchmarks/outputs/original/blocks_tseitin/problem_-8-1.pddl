(define (problem BLOCKS-8-1)
(:domain BLOCKS)
(:init
       (ontable C T)
       (ontable G T)
       (ontable D T)
       (ontable F T)
       (onblock E C)
       (onblock H A)
       (onblock A B)
       (onblock B G))
(:goal (and (DATALOG_ON A E) (DATALOG_ON B G) (DATALOG_ON C D) (DATALOG_ON D B) (DATALOG_ON F H) (DATALOG_ON G F) (DATALOG_ON H A) (not (DATALOG_INCONSISTENT))))
)