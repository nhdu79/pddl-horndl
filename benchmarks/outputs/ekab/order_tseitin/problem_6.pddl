(define (problem Wsmo2TPSA_problem)
(:domain Wsmo2TPSA)
(:objects
  voipRequest voip a b c d e f g h i - object)
(:init
       (requestedservice voipRequest voip)
       (service voip)
       (order voipRequest))
(:goal (and (AUX1) (not (DATALOG_INCONSISTENT))))
)