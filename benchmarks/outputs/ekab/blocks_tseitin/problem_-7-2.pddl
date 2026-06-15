(define (problem BLOCKS-7-2)
(:domain BLOCKS)
(:objects
  T E G C D F A B - object)
(:init
       (ontable F T)
       (ontable D T)
       (onblock B C)
       (onblock C G)
       (onblock G E)
       (onblock E F)
       (onblock A D))
(:goal (and (DATALOG_ON A C) (DATALOG_ON B F) (DATALOG_ON C G) (DATALOG_ON D A) (DATALOG_ON E B) (DATALOG_ON F D) (not (DATALOG_INCONSISTENT))))
)