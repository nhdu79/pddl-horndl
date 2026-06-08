(define (problem Wsmo2TPSA_problem)
(:domain Wsmo2TPSA)
(:objects
  voipRequest voip aa ab ac ad ae af ag ah ai aj ak al am - object)
(:init
       (requestedservice voipRequest voip)
       (service voip)
       (order voipRequest))
(:goal (and (exists (?x - object) (invoice ?x)) (not (updating))))
)