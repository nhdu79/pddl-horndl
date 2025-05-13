(define (problem BLOCKS-4-2)
(:domain BLOCKS)
(:init
       (ontable A T)
       (ontable B T)
       (ontable D T)
       (onblock C B))
(:goal (and (DATALOG_ON A B) (DATALOG_ON B C) (DATALOG_ON C D) (not (updating))))
)