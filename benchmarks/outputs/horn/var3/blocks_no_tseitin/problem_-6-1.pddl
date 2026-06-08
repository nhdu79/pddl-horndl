(define (problem BLOCKS-6-1)
(:domain BLOCKS)
(:objects
  T F D C E B A - object)
(:init
       (ontable F T)
       (ontable B T)
       (ontable E T)
       (ontable C T)
       (ontable D T)
       (onblock A F))
(:goal (and (DATALOG_ON A D) (DATALOG_ON B A) (DATALOG_ON C B) (DATALOG_ON E F) (DATALOG_ON F C) (not (updating))))
)