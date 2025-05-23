(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (bomb c)
       (cat f)
       (cat j)
       (cat k)
       (cat n)
       (cat p)
       (bomb q)
       (cat r)
       (cat v)
       (bomb w)
       (contains l c)
       (contains o w)
       (contains t q)
       (contains g f)
       (contains a k)
       (contains e n)
       (contains m j)
       (contains u r)
       (contains h p)
       (contains x v))
(:goal (and (forall (?x - object) (or (disarmed ?x) (not (DATALOG_PACKAGE ?x)))) (not (updating))))
)