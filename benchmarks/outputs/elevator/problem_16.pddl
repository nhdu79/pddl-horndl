(define (problem elevators_problem)
(:domain elevators)
(:init
       (origin pass_m k)
       (destin pass_m j)
       (origin pass_a k)
       (destin pass_a o)
       (origin pass_n c)
       (destin pass_n o)
       (origin pass_l i)
       (destin pass_l d)
       (origin pass_e k)
       (destin pass_e f)
       (origin pass_b k)
       (destin pass_b k)
       (next c d)
       (next d f)
       (next f g)
       (next g h)
       (next h i)
       (next i j)
       (next j k)
       (next k o)
       (next o p)
       (liftat i))
(:goal (and (forall (?x - object) (or (served ?x) (not (DATALOG_PASSENGER ?x)))) (not (incompatible_update))))
)