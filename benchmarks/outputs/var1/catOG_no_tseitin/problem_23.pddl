(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (cat aa)
       (cat ac)
       (bomb ae)
       (bomb an)
       (cat ao)
       (bomb ap)
       (bomb aq)
       (bomb ar)
       (cat av)
       (cat aw)
       (bomb bb)
       (cat bd)
       (cat be)
       (cat bf)
       (cat bj)
       (cat bm)
       (cat bq)
       (cat br)
       (cat bs)
       (contains ab ae)
       (contains as aq)
       (contains bp bb)
       (contains bi ap)
       (contains ba ar)
       (contains bk an)
       (contains ah aw)
       (contains ai br)
       (contains aj bq)
       (contains ad av)
       (contains az bm)
       (contains bh bs)
       (contains af ac)
       (contains bc bf)
       (contains al aa)
       (contains ag bd)
       (contains am bj)
       (contains bn ao)
       (contains bt be))
(:goal (and (forall (?x - object) (or (disarmed ?x) (not (DATALOG_PACKAGE ?x)))) (not (updating))))
)