(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (bomb ab)
       (cat ad)
       (cat ah)
       (cat am)
       (cat ao)
       (cat ar)
       (bomb as)
       (cat au)
       (bomb av)
       (cat az)
       (contains ak as)
       (contains aq av)
       (contains ax ab)
       (contains an ar)
       (contains aw au)
       (contains al am)
       (contains af az)
       (contains ap ao)
       (contains ay ad)
       (contains ac ah))
(:goal (and (forall (?x - object) (AUX16 ?x)) (not (updating))))
)