(define (problem Wsmo2TPSA_problem)
(:domain Wsmo2TPSA)
(:init
       (requestedservice voipRequest voip)
       (service voip)
       (order voipRequest))
(:goal (and (AUX70) (not (updating))))
)