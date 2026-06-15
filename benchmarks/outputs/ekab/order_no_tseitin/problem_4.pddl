(define (problem Wsmo2TPSA_problem)
(:domain Wsmo2TPSA)
(:objects
  voipRequest voip a b c d e f g - object)
(:init
       (requestedservice voipRequest voip)
       (service voip)
       (order voipRequest))
(:goal (and (exists (?x - object) (invoice ?x)) (not (DATALOG_INCONSISTENT))))
)