(define (problem BTcat_problem)
(:domain BTcat)
(:init
       (cat e)
       (bomb f)
       (cat g)
       (cat h)
       (bomb k)
       (bomb m)
       (cat p)
       (cat u)
       (cat v)
       (contains q m)
       (contains c k)
       (contains r f)
       (contains d p)
       (contains t g)
       (contains l e)
       (contains i h)
       (contains b u)
       (contains a v))
(:goal (and (forall (?x - object) (AUX16 ?x)) (not (updating))))
)