(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (bomb a)
       (bomb d)
       (cat g)
       (cat i)
       (cat j)
       (cat m)
       (cat n)
       (cat s)
       (bomb t)
       (contains r a)
       (contains e t)
       (contains f d)
       (contains p g)
       (contains l s)
       (contains h j)
       (contains k i)
       (contains c n)
       (contains b m))
(:goal (and (forall (?x - object) (or (disarmed ?x) (not (DATALOG_PACKAGE ?x)))) (not (DATALOG_INCONSISTENT))))
)