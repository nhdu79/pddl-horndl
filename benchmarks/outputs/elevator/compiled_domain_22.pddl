(define (domain elevators)
(:constants
  pass_u pass_r pass_l pass_o pass_b pass_c pass_v pass_d a e f g h i j k m n p q s t - object)
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
  (compatible_update)
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
  (DATALOG_PASSENGER ?x0 - object)
  (DATALOG_QUERY0 ?x0 ?x1 - object)
  (DATALOG_FLOOR ?x0 - object)
  (AUX0)
  (AUX1)
  (AUX2)
  (AUX3)
  (AUX4)
  (AUX5)
  (AUX6)
  (AUX7)
  (AUX8)
  (AUX9)
  (AUX10)
  (AUX11)
  (AUX12)
  (AUX13)
  (AUX14)
  (AUX15)
  (AUX16)
  (AUX17)
  (AUX18)
  (AUX19)
  (AUX20)
  (AUX21)
  (AUX22)
  (AUX23)
  (AUX24)
  (AUX25 ?p - object)
  (AUX26 ?p - object)
  (AUX27 ?p - object)
  (AUX28 ?p - object)
  (AUX29 ?p - object)
  (AUX30 ?p - object ?y0 - object)
  (AUX31 ?p - object)
  (AUX32 ?p - object ?y0 - object)
  (AUX33 ?p - object)
  (AUX34 ?p - object)
  (AUX35 ?p - object)
  (AUX36 ?p - object)
  (AUX37 ?p - object)
  (AUX38 ?p - object)
  (AUX39 ?p - object)
  (AUX40 ?p - object)
  (AUX41 ?p - object)
  (AUX42 ?p - object)
  (AUX43 ?p - object)
  (AUX44 ?p - object)
  (AUX45 ?p - object)
  (AUX46 ?p - object)
  (AUX47 ?p - object)
  (AUX48 ?p - object ?y0 - object)
  (AUX49 ?p - object)
  (AUX50 ?p - object)
  (AUX51 ?p - object)
  (AUX52 ?p - object)
  (AUX53 ?p - object ?y0 - object)
  (AUX54 ?p - object)
  (AUX55 ?p - object ?y0 - object)
  (AUX56 ?p - object ?y0 - object)
  (AUX57 ?p - object ?f - object)
  (AUX58 ?p - object ?f - object)
  (AUX59 ?p - object ?f - object)
  (AUX60 ?p - object ?f - object)
  (AUX61 ?p - object ?f - object)
  (AUX62 ?p - object ?f - object)
  (AUX63 ?p - object ?f - object)
  (AUX64 ?p - object ?f - object)
  (AUX65 ?p - object ?f - object)
  (AUX66 ?p - object ?f - object)
  (AUX67 ?p - object ?f - object)
  (AUX68 ?p - object ?f - object)
  (AUX69 ?f - object)
  (AUX70 ?f - object)
  (AUX71 ?f - object)
  (AUX72 ?y0 - object ?f - object)
  (AUX73 ?f - object)
  (AUX74 ?f - object)
  (AUX75 ?f - object)
  (AUX76 ?f - object)
  (AUX77 ?y0 - object ?f - object)
  (AUX78 ?f2 - object ?f1 - object)
  (AUX79 ?f2 - object ?f1 - object)
  (AUX80 ?f1 - object ?f2 - object ?y1 - object ?y0 - object)
  (AUX81 ?x - object))
(:derived (compatible_update)
          (and (AUX0) (AUX1) (AUX10) (AUX11) (AUX12) (AUX13) (AUX14) (AUX15) (AUX16) (AUX17) (AUX18) (AUX19) (AUX2) (AUX20) (AUX21) (AUX22) (AUX23) (AUX24) (AUX3) (AUX4) (AUX5) (AUX6) (AUX7) (AUX8) (AUX9)))
(:derived (DATALOG_QUERY0 ?x0 ?x1 - object)
          (and (boarded ?x1) (destin ?x1 ?x0)))
(:derived (ins_passenger ?p - object)
          (or (AUX25 ?p) (AUX26 ?p)))
(:derived (del_passenger ?p - object)
          (or (AUX27 ?p) (AUX28 ?p) (AUX29 ?p)))
(:derived (ins_passenger_closure ?p - object)
          (or (exists (?y0 - object) (AUX30 ?p ?y0)) (exists (?y0 - object) (AUX32 ?p ?y0)) (AUX31 ?p) (AUX33 ?p)))
(:derived (ins_boarded ?p - object)
          (or (AUX34 ?p) (AUX35 ?p)))
(:derived (del_boarded ?p - object)
          (or (AUX36 ?p) (AUX37 ?p) (AUX38 ?p) (AUX39 ?p)))
(:derived (ins_served ?p - object)
          (or (AUX40 ?p) (AUX41 ?p)))
(:derived (del_served ?p - object)
          (or (AUX42 ?p) (AUX43 ?p) (AUX44 ?p) (AUX45 ?p)))
(:derived (ins_floor ?p - object)
          (or (AUX46 ?p) (AUX47 ?p)))
(:derived (del_floor ?p - object)
          (or (exists (?y0 - object) (AUX48 ?p ?y0)) (exists (?y0 - object) (AUX53 ?p ?y0)) (AUX49 ?p) (AUX50 ?p) (AUX51 ?p) (AUX52 ?p)))
(:derived (ins_floor_closure ?p - object)
          (or (exists (?y0 - object) (AUX55 ?p ?y0)) (exists (?y0 - object) (AUX56 ?p ?y0)) (AUX54 ?p)))
(:derived (ins_origin ?p ?f - object)
          (or (AUX57 ?p ?f) (ins_origin_closure ?p ?f)))
(:derived (del_origin ?p ?f - object)
          (or (AUX58 ?p ?f) (AUX59 ?p ?f) (AUX60 ?p ?f) (AUX61 ?p ?f) (AUX62 ?p ?f)))
(:derived (ins_destin ?p ?f - object)
          (or (AUX63 ?p ?f) (ins_destin_closure ?p ?f)))
(:derived (del_destin ?p ?f - object)
          (or (AUX64 ?p ?f) (AUX65 ?p ?f) (AUX66 ?p ?f) (AUX67 ?p ?f) (AUX68 ?p ?f)))
(:derived (ins_liftat ?f - object)
          (or (AUX69 ?f) (AUX70 ?f)))
(:derived (del_liftat ?f - object)
          (or (exists (?y0 - object) (AUX72 ?y0 ?f)) (exists (?y0 - object) (AUX77 ?y0 ?f)) (AUX71 ?f) (AUX73 ?f) (AUX74 ?f) (AUX75 ?f) (AUX76 ?f)))
(:derived (ins_next ?f1 ?f2 - object)
          (or (AUX78 ?f2 ?f1) (ins_next_closure ?f1 ?f2)))
(:derived (del_next ?f1 ?f2 - object)
          (or (exists (?y0 ?y1 - object) (AUX80 ?f1 ?f2 ?y1 ?y0)) (AUX79 ?f2 ?f1)))
(:derived (DATALOG_PASSENGER ?x0 - object)
          (or (exists (?y0 - object) (destin ?x0 ?y0)) (exists (?y0 - object) (origin ?x0 ?y0)) (boarded ?x0) (passenger ?x0) (served ?x0)))
(:derived (DATALOG_FLOOR ?x0 - object)
          (or (exists (?y0 - object) (destin ?y0 ?x0)) (exists (?y0 - object) (origin ?y0 ?x0)) (floor ?x0) (liftat ?x0)))
(:derived (AUX0)
          (or (not (del_boarded_request Y0)) (not (ins_boarded_request Y0))))
(:derived (AUX1)
          (or (not (del_destin_request Y0 Y1)) (not (ins_destin_request Y0 Y1))))
(:derived (AUX2)
          (or (not (del_floor_request Y0)) (not (ins_destin_request Y1 Y0))))
(:derived (AUX3)
          (or (not (del_floor_request Y0)) (not (ins_floor_request Y0))))
(:derived (AUX4)
          (or (not (del_floor_request Y0)) (not (ins_liftat_request Y0))))
(:derived (AUX5)
          (or (not (del_floor_request Y0)) (not (ins_origin_request Y1 Y0))))
(:derived (AUX6)
          (or (not (del_liftat_request Y0)) (not (ins_liftat_request Y0))))
(:derived (AUX7)
          (or (not (del_next_request Y0 Y1)) (not (ins_next_request Y0 Y1))))
(:derived (AUX8)
          (or (not (del_origin_request Y0 Y1)) (not (ins_origin_request Y0 Y1))))
(:derived (AUX9)
          (or (not (del_passenger_request Y0)) (not (ins_boarded_request Y0))))
(:derived (AUX10)
          (or (not (del_passenger_request Y0)) (not (ins_destin_request Y0 Y1))))
(:derived (AUX11)
          (or (not (del_passenger_request Y0)) (not (ins_origin_request Y0 Y1))))
(:derived (AUX12)
          (or (not (del_passenger_request Y0)) (not (ins_passenger_request Y0))))
(:derived (AUX13)
          (or (not (del_passenger_request Y0)) (not (ins_served_request Y0))))
(:derived (AUX14)
          (or (not (del_served_request Y0)) (not (ins_served_request Y0))))
(:derived (AUX15)
          (or (not (ins_boarded_request Y0)) (not (ins_floor_request Y0))))
(:derived (AUX16)
          (or (not (ins_boarded_request Y0)) (not (ins_liftat_request Y0))))
(:derived (AUX17)
          (or (not (ins_destin_request Y0 Y1)) (not (ins_floor_request Y0))))
(:derived (AUX18)
          (or (not (ins_destin_request Y0 Y1)) (not (ins_liftat_request Y0))))
(:derived (AUX19)
          (or (not (ins_floor_request Y0)) (not (ins_origin_request Y0 Y1))))
(:derived (AUX20)
          (or (not (ins_floor_request Y0)) (not (ins_passenger_request Y0))))
(:derived (AUX21)
          (or (not (ins_floor_request Y0)) (not (ins_served_request Y0))))
(:derived (AUX22)
          (or (not (ins_liftat_request Y0)) (not (ins_origin_request Y0 Y1))))
(:derived (AUX23)
          (or (not (ins_liftat_request Y0)) (not (ins_passenger_request Y0))))
(:derived (AUX24)
          (or (not (ins_liftat_request Y0)) (not (ins_served_request Y0))))
(:derived (AUX25 ?p - object)
          (and (ins_passenger_request ?p) (not (passenger ?p))))
(:derived (AUX26 ?p - object)
          (and (ins_passenger_closure ?p) (not (ins_floor_request ?p)) (not (ins_liftat_request ?p))))
(:derived (AUX27 ?p - object)
          (and (ins_floor_request ?p) (passenger ?p)))
(:derived (AUX28 ?p - object)
          (and (ins_liftat_request ?p) (passenger ?p)))
(:derived (AUX29 ?p - object)
          (and (del_passenger_request ?p) (passenger ?p)))
(:derived (AUX30 ?p - object ?y0 - object)
          (and (del_origin ?p ?y0) (not (del_passenger_request ?p)) (not (ins_passenger_request ?p)) (not (passenger ?p))))
(:derived (AUX31 ?p - object)
          (and (del_boarded ?p) (not (del_passenger_request ?p)) (not (ins_passenger_request ?p)) (not (passenger ?p))))
(:derived (AUX32 ?p - object ?y0 - object)
          (and (del_destin ?p ?y0) (not (del_passenger_request ?p)) (not (ins_passenger_request ?p)) (not (passenger ?p))))
(:derived (AUX33 ?p - object)
          (and (del_served ?p) (not (del_passenger_request ?p)) (not (ins_passenger_request ?p)) (not (passenger ?p))))
(:derived (AUX34 ?p - object)
          (and (ins_boarded_closure ?p) (not (ins_floor_request ?p)) (not (ins_liftat_request ?p))))
(:derived (AUX35 ?p - object)
          (and (ins_boarded_request ?p) (not (boarded ?p))))
(:derived (AUX36 ?p - object)
          (and (boarded ?p) (del_boarded_request ?p)))
(:derived (AUX37 ?p - object)
          (and (boarded ?p) (ins_liftat_request ?p)))
(:derived (AUX38 ?p - object)
          (and (boarded ?p) (del_passenger_request ?p)))
(:derived (AUX39 ?p - object)
          (and (boarded ?p) (ins_floor_request ?p)))
(:derived (AUX40 ?p - object)
          (and (ins_served_request ?p) (not (served ?p))))
(:derived (AUX41 ?p - object)
          (and (ins_served_closure ?p) (not (ins_floor_request ?p)) (not (ins_liftat_request ?p))))
(:derived (AUX42 ?p - object)
          (and (ins_floor_request ?p) (served ?p)))
(:derived (AUX43 ?p - object)
          (and (del_served_request ?p) (served ?p)))
(:derived (AUX44 ?p - object)
          (and (ins_liftat_request ?p) (served ?p)))
(:derived (AUX45 ?p - object)
          (and (del_passenger_request ?p) (served ?p)))
(:derived (AUX46 ?p - object)
          (and (ins_floor_closure ?p) (not (ins_boarded_request ?p)) (not (ins_passenger_request ?p)) (not (ins_served_request ?p))))
(:derived (AUX47 ?p - object)
          (and (ins_floor_request ?p) (not (floor ?p))))
(:derived (AUX48 ?p - object ?y0 - object)
          (and (floor ?p) (ins_origin_request ?p ?y0)))
(:derived (AUX49 ?p - object)
          (and (floor ?p) (ins_boarded_request ?p)))
(:derived (AUX50 ?p - object)
          (and (del_floor_request ?p) (floor ?p)))
(:derived (AUX51 ?p - object)
          (and (floor ?p) (ins_served_request ?p)))
(:derived (AUX52 ?p - object)
          (and (floor ?p) (ins_passenger_request ?p)))
(:derived (AUX53 ?p - object ?y0 - object)
          (and (floor ?p) (ins_destin_request ?p ?y0)))
(:derived (AUX54 ?p - object)
          (and (del_liftat ?p) (not (del_floor_request ?p)) (not (floor ?p)) (not (ins_floor_request ?p))))
(:derived (AUX55 ?p - object ?y0 - object)
          (and (del_destin ?y0 ?p) (not (del_floor_request ?p)) (not (floor ?p)) (not (ins_floor_request ?p))))
(:derived (AUX56 ?p - object ?y0 - object)
          (and (del_origin ?y0 ?p) (not (del_floor_request ?p)) (not (floor ?p)) (not (ins_floor_request ?p))))
(:derived (AUX57 ?p - object ?f - object)
          (and (ins_origin_request ?p ?f) (not (origin ?p ?f))))
(:derived (AUX58 ?p - object ?f - object)
          (and (del_floor_request ?f) (origin ?p ?f)))
(:derived (AUX59 ?p - object ?f - object)
          (and (del_passenger_request ?p) (origin ?p ?f)))
(:derived (AUX60 ?p - object ?f - object)
          (and (ins_floor_request ?p) (origin ?p ?f)))
(:derived (AUX61 ?p - object ?f - object)
          (and (del_origin_request ?p ?f) (origin ?p ?f)))
(:derived (AUX62 ?p - object ?f - object)
          (and (ins_liftat_request ?p) (origin ?p ?f)))
(:derived (AUX63 ?p - object ?f - object)
          (and (ins_destin_request ?p ?f) (not (destin ?p ?f))))
(:derived (AUX64 ?p - object ?f - object)
          (and (del_destin_request ?p ?f) (destin ?p ?f)))
(:derived (AUX65 ?p - object ?f - object)
          (and (destin ?p ?f) (ins_floor_request ?p)))
(:derived (AUX66 ?p - object ?f - object)
          (and (destin ?p ?f) (ins_liftat_request ?p)))
(:derived (AUX67 ?p - object ?f - object)
          (and (del_passenger_request ?p) (destin ?p ?f)))
(:derived (AUX68 ?p - object ?f - object)
          (and (del_floor_request ?f) (destin ?p ?f)))
(:derived (AUX69 ?f - object)
          (and (ins_liftat_closure ?f) (not (ins_boarded_request ?f)) (not (ins_passenger_request ?f)) (not (ins_served_request ?f))))
(:derived (AUX70 ?f - object)
          (and (ins_liftat_request ?f) (not (liftat ?f))))
(:derived (AUX71 ?f - object)
          (and (del_floor_request ?f) (liftat ?f)))
(:derived (AUX72 ?y0 - object ?f - object)
          (and (ins_origin_request ?f ?y0) (liftat ?f)))
(:derived (AUX73 ?f - object)
          (and (del_liftat_request ?f) (liftat ?f)))
(:derived (AUX74 ?f - object)
          (and (ins_boarded_request ?f) (liftat ?f)))
(:derived (AUX75 ?f - object)
          (and (ins_served_request ?f) (liftat ?f)))
(:derived (AUX76 ?f - object)
          (and (ins_passenger_request ?f) (liftat ?f)))
(:derived (AUX77 ?y0 - object ?f - object)
          (and (ins_destin_request ?f ?y0) (liftat ?f)))
(:derived (AUX78 ?f2 - object ?f1 - object)
          (and (ins_next_request ?f1 ?f2) (not (next ?f1 ?f2))))
(:derived (AUX79 ?f2 - object ?f1 - object)
          (and (del_next_request ?f1 ?f2) (next ?f1 ?f2)))
(:derived (AUX80 ?f1 - object ?f2 - object ?y1 - object ?y0 - object)
          (and (ins_next_request ?f1 ?y0) (next ?f1 ?f2) (not (= ?f2 ?y1))))
(:derived (AUX81 ?x - object)
          (or (served ?x) (not (DATALOG_PASSENGER ?x))))
(:action stop
  :parameters (?p ?f - object)
  :precondition (and (DATALOG_PASSENGER ?p) (liftat ?f) (not (updating)))
  :effect (and (updating) (and (when (and (origin ?p ?f) (not (boarded ?p)) (not (served ?p))) (ins_boarded_request ?p)) (when (DATALOG_QUERY0 ?f ?p) (and (ins_served_request ?p) (del_boarded_request ?p))))))
(:action moveUp
  :parameters (?f1 ?f2 - object)
  :precondition (and (liftat ?f1) (next ?f1 ?f2) (not (updating)))
  :effect (and (updating) (when (and (liftat ?f1) (not (= ?f1 ?f2))) (and (ins_liftat_request ?f2) (del_liftat_request ?f1)))))
(:action moveDown
  :parameters (?f1 ?f2 - object)
  :precondition (and (liftat ?f1) (next ?f2 ?f1) (not (updating)))
  :effect (and (updating) (when (and (liftat ?f1) (not (= ?f1 ?f2))) (and (ins_liftat_request ?f2) (del_liftat_request ?f1)))))
(:action update
  :parameters ()
  :precondition (and (compatible_update) (updating))
  :effect (and (forall (?p ?f - object) (and (when (ins_passenger ?p) (passenger ?p)) (when (del_passenger ?p) (not (passenger ?p))) (when (ins_passenger_request ?p) (not (ins_passenger_request ?p))) (when (del_passenger_request ?p) (not (del_passenger_request ?p))) (when (ins_boarded ?p) (boarded ?p)) (when (del_boarded ?p) (not (boarded ?p))) (when (ins_boarded_request ?p) (not (ins_boarded_request ?p))) (when (del_boarded_request ?p) (not (del_boarded_request ?p))) (when (ins_served ?p) (served ?p)) (when (del_served ?p) (not (served ?p))) (when (ins_served_request ?p) (not (ins_served_request ?p))) (when (del_served_request ?p) (not (del_served_request ?p))) (when (ins_floor ?p) (floor ?p)) (when (del_floor ?p) (not (floor ?p))) (when (ins_floor_request ?p) (not (ins_floor_request ?p))) (when (del_floor_request ?p) (not (del_floor_request ?p))) (when (ins_origin ?p ?f) (origin ?p ?f)) (when (del_origin ?p ?f) (not (origin ?p ?f))) (when (ins_origin_request ?p ?f) (not (ins_origin_request ?p ?f))) (when (del_origin_request ?p ?f) (not (del_origin_request ?p ?f))) (when (ins_destin ?p ?f) (destin ?p ?f)) (when (del_destin ?p ?f) (not (destin ?p ?f))) (when (ins_destin_request ?p ?f) (not (ins_destin_request ?p ?f))) (when (del_destin_request ?p ?f) (not (del_destin_request ?p ?f))) (when (ins_liftat ?f) (liftat ?f)) (when (del_liftat ?f) (not (liftat ?f))) (when (ins_liftat_request ?f) (not (ins_liftat_request ?f))) (when (del_liftat_request ?f) (not (del_liftat_request ?f))) (when (ins_next ?f1 ?f2) (next ?f1 ?f2)) (when (del_next ?f1 ?f2) (not (next ?f1 ?f2))) (when (ins_next_request ?f1 ?f2) (not (ins_next_request ?f1 ?f2))) (when (del_next_request ?f1 ?f2) (not (del_next_request ?f1 ?f2))))) (not (updating))))
)