(define (problem BLOCKS-4-0)
(:domain BLOCKS)
(:init
       (ontable C T)
       (ontable A T)
       (ontable B T)
       (ontable D T))
(:goal (and (DATALOG_ON B A) (DATALOG_ON C B) (DATALOG_ON D C) (not (updating))))
)