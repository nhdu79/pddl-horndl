(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (bomb ad)
       (bomb an)
       (cat ao)
       (cat ar)
       (bomb as)
       (cat at)
       (cat av)
       (cat ax)
       (cat az)
       (bomb ba)
       (bomb bc)
       (cat bd)
       (cat be)
       (cat bg)
       (cat bj)
       (bomb bk)
       (cat bl)
       (cat bn)
       (contains bi ba)
       (contains ag bk)
       (contains au ad)
       (contains aq an)
       (contains ah bc)
       (contains ac as)
       (contains bf az)
       (contains aj ar)
       (contains ai ao)
       (contains ab ax)
       (contains bb bn)
       (contains am bd)
       (contains al bl)
       (contains ap be)
       (contains ay av)
       (contains bm bg)
       (contains aa bj)
       (contains af at))
(:goal (and (forall (?x - object) (or (disarmed ?x) (not (DATALOG_PACKAGE ?x)))) (not (updating))))
)