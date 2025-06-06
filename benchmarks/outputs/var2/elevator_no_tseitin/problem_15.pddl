(define (problem elevators_problem)
(:domain elevators)
(:init
       (origin pass_n i)
       (destin pass_n h)
       (origin pass_e j)
       (destin pass_e f)
       (origin pass_g k)
       (destin pass_g d)
       (origin pass_c h)
       (destin pass_c i)
       (origin pass_m i)
       (destin pass_m l)
       (origin pass_o d)
       (destin pass_o j)
       (next a b)
       (next b d)
       (next d f)
       (next f h)
       (next h i)
       (next i j)
       (next j k)
       (next k l)
       (liftat i))
(:goal (and (forall (?x - object) (or (served ?x) (not (DATALOG_PASSENGER ?x)))) (not (updating))))
)