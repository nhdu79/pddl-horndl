(define (domain elevators)
(:constants
  pass_an pass_al pass_ax pass_aa pass_as pass_au pass_ae pass_bb pass_ab pass_ad pass_bc pass_ba ac af ag ah ai aj ak am ao ap aq ar at av aw ay az bd - object)
(:predicates
  (passenger ?p - object)
  (boarded ?p - object)
  (served ?p - object)
  (floor ?p - object)
  (origin ?p ?f - object)
  (destin ?p ?f - object)
  (liftat ?f - object)
  (next ?f1 ?f2 - object)
  (updating)
  (incompatible_update)
  (ins_passenger ?p - object)
  (del_passenger ?p - object)
  (ins_passenger_request ?p - object)
  (del_passenger_request ?p - object)
  (ins_passenger_closure ?p - object)
  (ins_boarded ?p - object)
  (del_boarded ?p - object)
  (ins_boarded_request ?p - object)
  (del_boarded_request ?p - object)
  (ins_boarded_closure ?p - object)
  (ins_served ?p - object)
  (del_served ?p - object)
  (ins_served_request ?p - object)
  (del_served_request ?p - object)
  (ins_served_closure ?p - object)
  (ins_floor ?p - object)
  (del_floor ?p - object)
  (ins_floor_request ?p - object)
  (del_floor_request ?p - object)
  (ins_floor_closure ?p - object)
  (ins_origin ?p ?f - object)
  (del_origin ?p ?f - object)
  (ins_origin_request ?p ?f - object)
  (del_origin_request ?p ?f - object)
  (ins_origin_closure ?p ?f - object)
  (ins_destin ?p ?f - object)
  (del_destin ?p ?f - object)
  (ins_destin_request ?p ?f - object)
  (del_destin_request ?p ?f - object)
  (ins_destin_closure ?p ?f - object)
  (ins_liftat ?f - object)
  (del_liftat ?f - object)
  (ins_liftat_request ?f - object)
  (del_liftat_request ?f - object)
  (ins_liftat_closure ?f - object)
  (ins_next ?f1 ?f2 - object)
  (del_next ?f1 ?f2 - object)
  (ins_next_request ?f1 ?f2 - object)
  (del_next_request ?f1 ?f2 - object)
  (ins_next_closure ?f1 ?f2 - object)
  (DATALOG_FLOOR ?x0 - object)
  (DATALOG_QUERY0 ?x0 ?x1 - object)
  (DATALOG_PASSENGER ?x0 - object))
(:derived (updating )
          (exists (?y0 - object) (ins_passenger_request ?y0)))
(:derived (ins_destin ?x0 ?x1 - object)
          (ins_destin_closure ?x0 ?x1))
(:derived (ins_origin ?x0 ?x1 - object)
          (ins_origin_closure ?x0 ?x1))
(:derived (del_served ?x0 - object)
          (and (del_served_request ?x0) (served ?x0)))
(:derived (ins_passenger_closure ?x0 - object)
          (and (del_served ?x0) (not (DATALOG_PASSENGER ?x0)) (not (del_passenger_request ?x0)) (not (ins_passenger_request ?x0))))
(:derived (ins_boarded ?x0 - object)
          (and (ins_boarded_request ?x0) (not (boarded ?x0))))
(:derived (del_origin ?x0 ?x1 - object)
          (and (del_passenger_request ?x0) (origin ?x0 ?x1)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_floor_request ?y0) (ins_destin_request ?y1 ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_floor_request ?y0) (ins_floor_request ?y0))))
(:derived (del_boarded ?x0 - object)
          (and (boarded ?x0) (ins_liftat_request ?x0)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (ins_liftat_request ?y0) (ins_origin_request ?y0 ?y1))))
(:derived (ins_served ?x0 - object)
          (and (ins_served_request ?x0) (not (served ?x0))))
(:derived (del_passenger ?x0 - object)
          (and (DATALOG_PASSENGER ?x0) (ins_liftat_request ?x0)))
(:derived (del_passenger ?x0 - object)
          (and (DATALOG_PASSENGER ?x0) (ins_floor_request ?x0)))
(:derived (del_origin ?x0 ?x1 - object)
          (and (ins_liftat_request ?x0) (origin ?x0 ?x1)))
(:derived (updating )
          (exists (?y0 - object) (del_floor_request ?y0)))
(:derived (del_origin ?x0 ?x1 - object)
          (and (del_floor_request ?x1) (origin ?x0 ?x1)))
(:derived (updating )
          (exists (?y0 ?y1 - object) (del_destin_request ?y0 ?y1)))
(:derived (updating )
          (exists (?y0 ?y1 - object) (ins_next_request ?y0 ?y1)))
(:derived (DATALOG_FLOOR ?x0 - object)
          (floor ?x0))
(:derived (DATALOG_FLOOR ?x0 - object)
          (exists (?y0 - object) (origin ?y0 ?x0)))
(:derived (ins_liftat ?x0 - object)
          (and (ins_liftat_request ?x0) (not (liftat ?x0))))
(:derived (DATALOG_FLOOR ?x0 - object)
          (exists (?y0 - object) (destin ?y0 ?x0)))
(:derived (DATALOG_QUERY0 ?x0 ?x1 - object)
          (and (boarded ?x1) (destin ?x1 ?x0)))
(:derived (del_boarded ?x0 - object)
          (and (boarded ?x0) (ins_floor_request ?x0)))
(:derived (ins_liftat ?x0 - object)
          (and (ins_liftat_closure ?x0) (not (ins_boarded_request ?x0)) (not (ins_passenger_request ?x0)) (not (ins_served_request ?x0))))
(:derived (ins_floor ?x0 - object)
          (and (ins_floor_request ?x0) (not (DATALOG_FLOOR ?x0))))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (passenger ?x0))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (boarded ?x0))
(:derived (del_origin ?x0 ?x1 - object)
          (and (ins_floor_request ?x0) (origin ?x0 ?x1)))
(:derived (updating )
          (exists (?y0 ?y1 - object) (ins_origin_request ?y0 ?y1)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_next_request ?y0 ?y1) (ins_next_request ?y0 ?y1))))
(:derived (ins_origin ?x0 ?x1 - object)
          (and (ins_origin_request ?x0 ?x1) (not (origin ?x0 ?x1))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_passenger_request ?y0) (ins_served_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_boarded_request ?y0) (ins_liftat_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_liftat_request ?y0) (ins_liftat_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_destin_request ?y0 ?y1) (ins_destin_request ?y0 ?y1))))
(:derived (ins_passenger_closure ?x0 - object)
          (and (del_boarded ?x0) (not (DATALOG_PASSENGER ?x0)) (not (del_passenger_request ?x0)) (not (ins_passenger_request ?x0))))
(:derived (del_served ?x0 - object)
          (and (del_passenger_request ?x0) (served ?x0)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_floor_request ?y0) (ins_origin_request ?y1 ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_passenger_request ?y0) (ins_boarded_request ?y0))))
(:derived (del_liftat ?x0 - object)
          (and (ins_passenger_request ?x0) (liftat ?x0)))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_boarded_request ?y0) (ins_floor_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_floor_request ?y0) (ins_passenger_request ?y0))))
(:derived (ins_boarded ?x0 - object)
          (and (ins_boarded_closure ?x0) (not (ins_floor_request ?x0)) (not (ins_liftat_request ?x0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_boarded_request ?y0) (ins_boarded_request ?y0))))
(:derived (ins_floor ?x0 - object)
          (and (ins_floor_closure ?x0) (not (ins_boarded_request ?x0)) (not (ins_passenger_request ?x0)) (not (ins_served_request ?x0))))
(:derived (ins_floor_closure ?x0 - object)
          (and (del_liftat ?x0) (not (DATALOG_FLOOR ?x0)) (not (del_floor_request ?x0)) (not (ins_floor_request ?x0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_floor_request ?y0) (ins_served_request ?y0))))
(:derived (updating )
          (exists (?y0 - object) (del_liftat_request ?y0)))
(:derived (del_passenger ?x0 - object)
          (and (DATALOG_PASSENGER ?x0) (del_passenger_request ?x0)))
(:derived (updating )
          (exists (?y0 ?y1 - object) (del_next_request ?y0 ?y1)))
(:derived (ins_next ?x0 ?x1 - object)
          (ins_next_closure ?x0 ?x1))
(:derived (updating )
          (exists (?y0 - object) (del_served_request ?y0)))
(:derived (del_served ?x0 - object)
          (and (ins_liftat_request ?x0) (served ?x0)))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_served_request ?y0) (ins_served_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 ?y1 ?y2 ?y3 - object) (and (ins_next_request ?y0 ?y1) (ins_next_request ?y0 ?y2) (not (= ?y1 ?y3)))))
(:derived (del_liftat ?x0 - object)
          (and (del_liftat_request ?x0) (liftat ?x0)))
(:derived (updating )
          (exists (?y0 - object) (ins_liftat_request ?y0)))
(:derived (del_destin ?x0 ?x1 - object)
          (and (del_passenger_request ?x0) (destin ?x0 ?x1)))
(:derived (updating )
          (exists (?y0 - object) (del_boarded_request ?y0)))
(:derived (ins_floor_closure ?x0 - object)
          (exists (?y0 - object) (and (del_destin ?y0 ?x0) (not (DATALOG_FLOOR ?x0)) (not (del_floor_request ?x0)) (not (ins_floor_request ?x0)))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_liftat_request ?y0) (ins_passenger_request ?y0))))
(:derived (updating )
          (exists (?y0 - object) (del_passenger_request ?y0)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (ins_destin_request ?y0 ?y1) (ins_liftat_request ?y0))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (ins_liftat_request ?y0) (ins_served_request ?y0))))
(:derived (del_destin ?x0 ?x1 - object)
          (and (destin ?x0 ?x1) (ins_liftat_request ?x0)))
(:derived (updating )
          (exists (?y0 - object) (ins_served_request ?y0)))
(:derived (del_floor ?x0 - object)
          (and (DATALOG_FLOOR ?x0) (ins_served_request ?x0)))
(:derived (updating )
          (exists (?y0 - object) (ins_floor_request ?y0)))
(:derived (del_next ?x0 ?x1 - object)
          (and (del_next_request ?x0 ?x1) (next ?x0 ?x1)))
(:derived (ins_passenger ?x0 - object)
          (and (ins_passenger_request ?x0) (not (DATALOG_PASSENGER ?x0))))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (ins_floor_request ?y0) (ins_origin_request ?y0 ?y1))))
(:derived (ins_floor_closure ?x0 - object)
          (exists (?y0 - object) (and (del_origin ?y0 ?x0) (not (DATALOG_FLOOR ?x0)) (not (del_floor_request ?x0)) (not (ins_floor_request ?x0)))))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_passenger_request ?y0) (ins_passenger_request ?y0))))
(:derived (del_boarded ?x0 - object)
          (and (boarded ?x0) (del_passenger_request ?x0)))
(:derived (DATALOG_FLOOR ?x0 - object)
          (liftat ?x0))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_passenger_request ?y0) (ins_origin_request ?y0 ?y1))))
(:derived (updating )
          (exists (?y0 - object) (ins_boarded_request ?y0)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (ins_destin_request ?y0 ?y1) (ins_floor_request ?y0))))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (exists (?y0 - object) (origin ?x0 ?y0)))
(:derived (del_boarded ?x0 - object)
          (and (boarded ?x0) (del_boarded_request ?x0)))
(:derived (ins_served ?x0 - object)
          (and (ins_served_closure ?x0) (not (ins_floor_request ?x0)) (not (ins_liftat_request ?x0))))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (exists (?y0 - object) (destin ?x0 ?y0)))
(:derived (ins_passenger_closure ?x0 - object)
          (exists (?y0 - object) (and (del_origin ?x0 ?y0) (not (DATALOG_PASSENGER ?x0)) (not (del_passenger_request ?x0)) (not (ins_passenger_request ?x0)))))
(:derived (ins_next ?x0 ?x1 - object)
          (and (ins_next_request ?x0 ?x1) (not (next ?x0 ?x1))))
(:derived (ins_destin ?x0 ?x1 - object)
          (and (ins_destin_request ?x0 ?x1) (not (destin ?x0 ?x1))))
(:derived (del_liftat ?x0 - object)
          (exists (?y0 - object) (and (ins_destin_request ?x0 ?y0) (liftat ?x0))))
(:derived (del_liftat ?x0 - object)
          (and (del_floor_request ?x0) (liftat ?x0)))
(:derived (del_liftat ?x0 - object)
          (exists (?y0 - object) (and (ins_origin_request ?x0 ?y0) (liftat ?x0))))
(:derived (del_destin ?x0 ?x1 - object)
          (and (destin ?x0 ?x1) (ins_floor_request ?x0)))
(:derived (del_floor ?x0 - object)
          (exists (?y0 - object) (and (DATALOG_FLOOR ?x0) (ins_destin_request ?x0 ?y0))))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_passenger_request ?y0) (ins_destin_request ?y0 ?y1))))
(:derived (ins_passenger ?x0 - object)
          (and (ins_passenger_closure ?x0) (not (ins_floor_request ?x0)) (not (ins_liftat_request ?x0))))
(:derived (del_floor ?x0 - object)
          (and (DATALOG_FLOOR ?x0) (del_floor_request ?x0)))
(:derived (del_next ?x0 ?x1 - object)
          (exists (?y0 ?y1 - object) (and (ins_next_request ?x0 ?y0) (next ?x0 ?x1) (not (= ?x1 ?y1)))))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (served ?x0))
(:derived (del_liftat ?x0 - object)
          (and (ins_served_request ?x0) (liftat ?x0)))
(:derived (del_liftat ?x0 - object)
          (and (ins_boarded_request ?x0) (liftat ?x0)))
(:derived (updating )
          (exists (?y0 ?y1 - object) (ins_destin_request ?y0 ?y1)))
(:derived (incompatible_update )
          (exists (?y0 ?y1 - object) (and (del_origin_request ?y0 ?y1) (ins_origin_request ?y0 ?y1))))
(:derived (del_floor ?x0 - object)
          (and (DATALOG_FLOOR ?x0) (ins_passenger_request ?x0)))
(:derived (del_origin ?x0 ?x1 - object)
          (and (del_origin_request ?x0 ?x1) (origin ?x0 ?x1)))
(:derived (ins_passenger_closure ?x0 - object)
          (exists (?y0 - object) (and (del_destin ?x0 ?y0) (not (DATALOG_PASSENGER ?x0)) (not (del_passenger_request ?x0)) (not (ins_passenger_request ?x0)))))
(:derived (updating )
          (exists (?y0 ?y1 - object) (del_origin_request ?y0 ?y1)))
(:derived (del_floor ?x0 - object)
          (exists (?y0 - object) (and (DATALOG_FLOOR ?x0) (ins_origin_request ?x0 ?y0))))
(:derived (del_destin ?x0 ?x1 - object)
          (and (del_floor_request ?x1) (destin ?x0 ?x1)))
(:derived (del_floor ?x0 - object)
          (and (DATALOG_FLOOR ?x0) (ins_boarded_request ?x0)))
(:derived (del_destin ?x0 ?x1 - object)
          (and (del_destin_request ?x0 ?x1) (destin ?x0 ?x1)))
(:derived (incompatible_update )
          (exists (?y0 - object) (and (del_floor_request ?y0) (ins_liftat_request ?y0))))
(:derived (del_served ?x0 - object)
          (and (ins_floor_request ?x0) (served ?x0)))
(:action stop
  :parameters (?p ?f - object)
  :precondition (and (DATALOG_PASSENGER ?p) (liftat ?f) (not (updating)))
  :effect (and (when (and (origin ?p ?f) (not (boarded ?p)) (not (served ?p))) (ins_boarded_request ?p)) (when (DATALOG_QUERY0 ?f ?p) (and (ins_served_request ?p) (del_boarded_request ?p)))))
(:action moveUp
  :parameters (?f1 ?f2 - object)
  :precondition (and (liftat ?f1) (next ?f1 ?f2) (not (updating)))
  :effect (when (and (liftat ?f1) (not (= ?f1 ?f2))) (and (ins_liftat_request ?f2) (del_liftat_request ?f1))))
(:action moveDown
  :parameters (?f1 ?f2 - object)
  :precondition (and (liftat ?f1) (next ?f2 ?f1) (not (updating)))
  :effect (when (and (liftat ?f1) (not (= ?f1 ?f2))) (and (ins_liftat_request ?f2) (del_liftat_request ?f1))))
(:action update
  :parameters ()
  :precondition (and (updating) (not (incompatible_update)))
  :effect (forall (?p ?f) (and (when (ins_passenger ?p) (passenger ?p)) (when (del_passenger ?p) (not (passenger ?p))) (when (ins_passenger_request ?p) (not (ins_passenger_request ?p))) (when (del_passenger_request ?p) (not (del_passenger_request ?p))) (when (ins_boarded ?p) (boarded ?p)) (when (del_boarded ?p) (not (boarded ?p))) (when (ins_boarded_request ?p) (not (ins_boarded_request ?p))) (when (del_boarded_request ?p) (not (del_boarded_request ?p))) (when (ins_served ?p) (served ?p)) (when (del_served ?p) (not (served ?p))) (when (ins_served_request ?p) (not (ins_served_request ?p))) (when (del_served_request ?p) (not (del_served_request ?p))) (when (ins_floor ?p) (floor ?p)) (when (del_floor ?p) (not (floor ?p))) (when (ins_floor_request ?p) (not (ins_floor_request ?p))) (when (del_floor_request ?p) (not (del_floor_request ?p))) (when (ins_origin ?p ?f) (origin ?p ?f)) (when (del_origin ?p ?f) (not (origin ?p ?f))) (when (ins_origin_request ?p ?f) (not (ins_origin_request ?p ?f))) (when (del_origin_request ?p ?f) (not (del_origin_request ?p ?f))) (when (ins_destin ?p ?f) (destin ?p ?f)) (when (del_destin ?p ?f) (not (destin ?p ?f))) (when (ins_destin_request ?p ?f) (not (ins_destin_request ?p ?f))) (when (del_destin_request ?p ?f) (not (del_destin_request ?p ?f))) (when (ins_liftat ?f) (liftat ?f)) (when (del_liftat ?f) (not (liftat ?f))) (when (ins_liftat_request ?f) (not (ins_liftat_request ?f))) (when (del_liftat_request ?f) (not (del_liftat_request ?f))) (when (ins_next ?f1 ?f2) (next ?f1 ?f2)) (when (del_next ?f1 ?f2) (not (next ?f1 ?f2))) (when (ins_next_request ?f1 ?f2) (not (ins_next_request ?f1 ?f2))) (when (del_next_request ?f1 ?f2) (not (del_next_request ?f1 ?f2))))))
)