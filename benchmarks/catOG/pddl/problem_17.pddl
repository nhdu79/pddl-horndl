(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (cat aa)
       (cat ad)
       (bomb ah)
       (bomb al)
       (cat an)
       (cat ao)
       (bomb ap)
       (cat ar)
       (cat as)
       (bomb at)
       (bomb av)
       (cat aw)
       (cat ax)
       (cat bf)
       (cat bh)
       (contains ay av)
       (contains af at)
       (contains ab ap)
       (contains bb ah)
       (contains ai al)
       (contains bd bh)
       (contains ag ao)
       (contains bc aw)
       (contains ak aa)
       (contains ac as)
       (contains ae an)
       (contains aq ad)
       (contains au bf)
       (contains am ar)
       (contains ba ax))
(:goal (and (forall (?x - object) (or (disarmed ?x) (not (DATALOG_PACKAGE ?x)))) (not (DATALOG_INCONSISTENT))))
)