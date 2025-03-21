(define (domain robot)
(:constants
  robot - object)
(:predicates
  (columns ?x - object)
  (rows ?x - object)
  (column0 ?x - object)
  (column1 ?x - object)
  (column2 ?x - object)
  (column3 ?x - object)
  (column4 ?x - object)
  (column5 ?x - object)
  (column6 ?x - object)
  (column7 ?x - object)
  (column8 ?x - object)
  (column9 ?x - object)
  (column10 ?x - object)
  (column11 ?x - object)
  (column12 ?x - object)
  (column13 ?x - object)
  (column14 ?x - object)
  (rightof0 ?x - object)
  (rightof1 ?x - object)
  (rightof2 ?x - object)
  (rightof3 ?x - object)
  (rightof4 ?x - object)
  (rightof5 ?x - object)
  (rightof6 ?x - object)
  (rightof7 ?x - object)
  (rightof8 ?x - object)
  (rightof9 ?x - object)
  (rightof10 ?x - object)
  (rightof11 ?x - object)
  (rightof12 ?x - object)
  (rightof13 ?x - object)
  (rightof14 ?x - object)
  (leftof1 ?x - object)
  (leftof2 ?x - object)
  (leftof3 ?x - object)
  (leftof4 ?x - object)
  (leftof5 ?x - object)
  (leftof6 ?x - object)
  (leftof7 ?x - object)
  (leftof8 ?x - object)
  (leftof9 ?x - object)
  (leftof10 ?x - object)
  (leftof11 ?x - object)
  (leftof12 ?x - object)
  (leftof13 ?x - object)
  (leftof14 ?x - object)
  (leftof15 ?x - object)
  (row0 ?x - object)
  (row1 ?x - object)
  (row2 ?x - object)
  (row3 ?x - object)
  (row4 ?x - object)
  (row5 ?x - object)
  (row6 ?x - object)
  (row7 ?x - object)
  (row8 ?x - object)
  (row9 ?x - object)
  (row10 ?x - object)
  (row11 ?x - object)
  (row12 ?x - object)
  (row13 ?x - object)
  (row14 ?x - object)
  (aboveof0 ?x - object)
  (aboveof1 ?x - object)
  (aboveof2 ?x - object)
  (aboveof3 ?x - object)
  (aboveof4 ?x - object)
  (aboveof5 ?x - object)
  (aboveof6 ?x - object)
  (aboveof7 ?x - object)
  (aboveof8 ?x - object)
  (aboveof9 ?x - object)
  (aboveof10 ?x - object)
  (aboveof11 ?x - object)
  (aboveof12 ?x - object)
  (aboveof13 ?x - object)
  (aboveof14 ?x - object)
  (belowof1 ?x - object)
  (belowof2 ?x - object)
  (belowof3 ?x - object)
  (belowof4 ?x - object)
  (belowof5 ?x - object)
  (belowof6 ?x - object)
  (belowof7 ?x - object)
  (belowof8 ?x - object)
  (belowof9 ?x - object)
  (belowof10 ?x - object)
  (belowof11 ?x - object)
  (belowof12 ?x - object)
  (belowof13 ?x - object)
  (belowof14 ?x - object)
  (belowof15 ?x - object)
  (DATALOG_INCONSISTENT)
  (DATALOG_ABOVEOF3 ?x0 - object)
  (DATALOG_LEFTOF7 ?x0 - object)
  (DATALOG_ABOVEOF13 ?x0 - object)
  (DATALOG_QUERY8 ?x0 - object)
  (DATALOG_LEFTOF5 ?x0 - object)
  (DATALOG_QUERY11 ?x0 - object)
  (DATALOG_QUERY1 ?x0 - object)
  (DATALOG_QUERY36 ?x0 - object)
  (DATALOG_QUERY38 ?x0 - object)
  (DATALOG_BELOWOF13 ?x0 - object)
  (DATALOG_BELOWOF5 ?x0 - object)
  (DATALOG_ABOVEOF5 ?x0 - object)
  (DATALOG_QUERY5 ?x0 - object)
  (DATALOG_QUERY13 ?x0 - object)
  (DATALOG_BELOWOF15 ?x0 - object)
  (DATALOG_LEFTOF11 ?x0 - object)
  (DATALOG_QUERY9 ?x0 - object)
  (DATALOG_BELOWOF7 ?x0 - object)
  (DATALOG_RIGHTOF6 ?x0 - object)
  (DATALOG_BELOWOF10 ?x0 - object)
  (DATALOG_BELOWOF4 ?x0 - object)
  (DATALOG_QUERY32 ?x0 - object)
  (DATALOG_LEFTOF10 ?x0 - object)
  (DATALOG_LEFTOF15 ?x0 - object)
  (DATALOG_BELOWOF11 ?x0 - object)
  (DATALOG_QUERY30 ?x0 - object)
  (DATALOG_QUERY2 ?x0 - object)
  (DATALOG_RIGHTOF1 ?x0 - object)
  (DATALOG_ABOVEOF8 ?x0 - object)
  (DATALOG_BELOWOF14 ?x0 - object)
  (DATALOG_RIGHTOF10 ?x0 - object)
  (DATALOG_LEFTOF6 ?x0 - object)
  (DATALOG_RIGHTOF3 ?x0 - object)
  (DATALOG_RIGHTOF11 ?x0 - object)
  (DATALOG_LEFTOF4 ?x0 - object)
  (DATALOG_BELOWOF2 ?x0 - object)
  (DATALOG_LEFTOF12 ?x0 - object)
  (DATALOG_LEFTOF3 ?x0 - object)
  (DATALOG_RIGHTOF2 ?x0 - object)
  (DATALOG_COLUMNS ?x0 - object)
  (DATALOG_RIGHTOF4 ?x0 - object)
  (DATALOG_BELOWOF6 ?x0 - object)
  (DATALOG_QUERY12 ?x0 - object)
  (DATALOG_QUERY55 ?x0 - object)
  (DATALOG_RIGHTOF0 ?x0 - object)
  (DATALOG_QUERY31 ?x0 - object)
  (DATALOG_LEFTOF9 ?x0 - object)
  (DATALOG_QUERY33 ?x0 - object)
  (DATALOG_RIGHTOF8 ?x0 - object)
  (DATALOG_RIGHTOF9 ?x0 - object)
  (DATALOG_QUERY3 ?x0 - object)
  (DATALOG_ABOVEOF11 ?x0 - object)
  (DATALOG_QUERY6 ?x0 - object)
  (DATALOG_BELOWOF8 ?x0 - object)
  (DATALOG_BELOWOF3 ?x0 - object)
  (DATALOG_QUERY40 ?x0 - object)
  (DATALOG_ABOVEOF1 ?x0 - object)
  (DATALOG_ROWS ?x0 - object)
  (DATALOG_LEFTOF14 ?x0 - object)
  (DATALOG_QUERY29 ?x0 - object)
  (DATALOG_QUERY39 ?x0 - object)
  (DATALOG_QUERY56)
  (DATALOG_ABOVEOF0 ?x0 - object)
  (DATALOG_ABOVEOF6 ?x0 - object)
  (DATALOG_QUERY34 ?x0 - object)
  (DATALOG_RIGHTOF13 ?x0 - object)
  (DATALOG_ABOVEOF4 ?x0 - object)
  (DATALOG_QUERY37 ?x0 - object)
  (DATALOG_QUERY27 ?x0 - object)
  (DATALOG_LEFTOF2 ?x0 - object)
  (DATALOG_ABOVEOF2 ?x0 - object)
  (DATALOG_QUERY35 ?x0 - object)
  (DATALOG_LEFTOF8 ?x0 - object)
  (DATALOG_RIGHTOF12 ?x0 - object)
  (DATALOG_RIGHTOF7 ?x0 - object)
  (DATALOG_QUERY10 ?x0 - object)
  (DATALOG_LEFTOF13 ?x0 - object)
  (DATALOG_QUERY0 ?x0 - object)
  (DATALOG_ABOVEOF7 ?x0 - object)
  (DATALOG_ABOVEOF9 ?x0 - object)
  (DATALOG_QUERY41 ?x0 - object)
  (DATALOG_ABOVEOF12 ?x0 - object)
  (DATALOG_BELOWOF9 ?x0 - object)
  (DATALOG_QUERY7 ?x0 - object)
  (DATALOG_QUERY4 ?x0 - object)
  (DATALOG_RIGHTOF5 ?x0 - object)
  (DATALOG_BELOWOF12 ?x0 - object)
  (DATALOG_QUERY28 ?x0 - object)
  (DATALOG_ABOVEOF10 ?x0 - object)
  (AUX0 ?y0 - object)
  (AUX1 ?y0 - object)
  (AUX2 ?y0 - object)
  (AUX3 ?y0 - object)
  (AUX4 ?y0 - object)
  (AUX5 ?y0 - object)
  (AUX6 ?y0 - object)
  (AUX7 ?y0 - object)
  (AUX8 ?y0 - object)
  (AUX9 ?y0 - object)
  (AUX10 ?y0 - object)
  (AUX11 ?y0 - object)
  (AUX12 ?y0 - object)
  (AUX13 ?y0 - object)
  (AUX14 ?y0 - object)
  (AUX15 ?y0 - object)
  (AUX16 ?y0 - object)
  (AUX17 ?y0 - object)
  (AUX18 ?y0 - object)
  (AUX19 ?y0 - object)
  (AUX20 ?y0 - object)
  (AUX21 ?y0 - object)
  (AUX22 ?y0 - object)
  (AUX23 ?y0 - object)
  (AUX24 ?y0 - object)
  (AUX25 ?y0 - object)
  (AUX26 ?y0 - object)
  (AUX27 ?y0 - object))
(:derived (DATALOG_QUERY8 ?x0 - object)
          (and (DATALOG_LEFTOF9 ?x0) (DATALOG_RIGHTOF8 ?x0)))
(:derived (DATALOG_QUERY11 ?x0 - object)
          (and (DATALOG_LEFTOF12 ?x0) (DATALOG_RIGHTOF11 ?x0)))
(:derived (DATALOG_QUERY1 ?x0 - object)
          (and (DATALOG_LEFTOF2 ?x0) (DATALOG_RIGHTOF1 ?x0)))
(:derived (DATALOG_QUERY36 ?x0 - object)
          (and (DATALOG_ABOVEOF8 ?x0) (DATALOG_BELOWOF9 ?x0)))
(:derived (DATALOG_QUERY38 ?x0 - object)
          (and (DATALOG_ABOVEOF10 ?x0) (DATALOG_BELOWOF11 ?x0)))
(:derived (DATALOG_QUERY5 ?x0 - object)
          (and (DATALOG_LEFTOF6 ?x0) (DATALOG_RIGHTOF5 ?x0)))
(:derived (DATALOG_QUERY13 ?x0 - object)
          (and (DATALOG_LEFTOF14 ?x0) (DATALOG_RIGHTOF13 ?x0)))
(:derived (DATALOG_QUERY9 ?x0 - object)
          (and (DATALOG_LEFTOF10 ?x0) (DATALOG_RIGHTOF9 ?x0)))
(:derived (DATALOG_QUERY32 ?x0 - object)
          (and (DATALOG_ABOVEOF4 ?x0) (DATALOG_BELOWOF5 ?x0)))
(:derived (DATALOG_QUERY30 ?x0 - object)
          (and (DATALOG_ABOVEOF2 ?x0) (DATALOG_BELOWOF3 ?x0)))
(:derived (DATALOG_QUERY2 ?x0 - object)
          (and (DATALOG_LEFTOF3 ?x0) (DATALOG_RIGHTOF2 ?x0)))
(:derived (DATALOG_QUERY12 ?x0 - object)
          (and (DATALOG_LEFTOF13 ?x0) (DATALOG_RIGHTOF12 ?x0)))
(:derived (DATALOG_QUERY55 ?x0 - object)
          (and (DATALOG_BELOWOF15 ?x0) (aboveof14 ?x0)))
(:derived (DATALOG_QUERY31 ?x0 - object)
          (and (DATALOG_ABOVEOF3 ?x0) (DATALOG_BELOWOF4 ?x0)))
(:derived (DATALOG_QUERY33 ?x0 - object)
          (and (DATALOG_ABOVEOF5 ?x0) (DATALOG_BELOWOF6 ?x0)))
(:derived (DATALOG_QUERY3 ?x0 - object)
          (and (DATALOG_LEFTOF4 ?x0) (DATALOG_RIGHTOF3 ?x0)))
(:derived (DATALOG_QUERY6 ?x0 - object)
          (and (DATALOG_LEFTOF7 ?x0) (DATALOG_RIGHTOF6 ?x0)))
(:derived (DATALOG_QUERY40 ?x0 - object)
          (and (DATALOG_ABOVEOF12 ?x0) (DATALOG_BELOWOF13 ?x0)))
(:derived (DATALOG_QUERY29 ?x0 - object)
          (and (DATALOG_ABOVEOF1 ?x0) (DATALOG_BELOWOF2 ?x0)))
(:derived (DATALOG_QUERY39 ?x0 - object)
          (and (DATALOG_ABOVEOF11 ?x0) (DATALOG_BELOWOF12 ?x0)))
(:derived (DATALOG_QUERY56)
          (and (column2 robot) (row1 robot)))
(:derived (DATALOG_QUERY34 ?x0 - object)
          (and (DATALOG_ABOVEOF6 ?x0) (DATALOG_BELOWOF7 ?x0)))
(:derived (DATALOG_QUERY37 ?x0 - object)
          (and (DATALOG_ABOVEOF9 ?x0) (DATALOG_BELOWOF10 ?x0)))
(:derived (DATALOG_QUERY27 ?x0 - object)
          (and (DATALOG_LEFTOF15 ?x0) (rightof14 ?x0)))
(:derived (DATALOG_QUERY35 ?x0 - object)
          (and (DATALOG_ABOVEOF7 ?x0) (DATALOG_BELOWOF8 ?x0)))
(:derived (DATALOG_QUERY10 ?x0 - object)
          (and (DATALOG_LEFTOF11 ?x0) (DATALOG_RIGHTOF10 ?x0)))
(:derived (DATALOG_QUERY0 ?x0 - object)
          (and (DATALOG_RIGHTOF0 ?x0) (leftof1 ?x0)))
(:derived (DATALOG_QUERY41 ?x0 - object)
          (and (DATALOG_ABOVEOF13 ?x0) (DATALOG_BELOWOF14 ?x0)))
(:derived (DATALOG_QUERY7 ?x0 - object)
          (and (DATALOG_LEFTOF8 ?x0) (DATALOG_RIGHTOF7 ?x0)))
(:derived (DATALOG_QUERY4 ?x0 - object)
          (and (DATALOG_LEFTOF5 ?x0) (DATALOG_RIGHTOF4 ?x0)))
(:derived (DATALOG_QUERY28 ?x0 - object)
          (and (DATALOG_ABOVEOF0 ?x0) (belowof1 ?x0)))
(:derived (DATALOG_INCONSISTENT)
          (or (exists (?y0 - object) (AUX0 ?y0)) (exists (?y0 - object) (AUX1 ?y0)) (exists (?y0 - object) (AUX10 ?y0)) (exists (?y0 - object) (AUX11 ?y0)) (exists (?y0 - object) (AUX12 ?y0)) (exists (?y0 - object) (AUX13 ?y0)) (exists (?y0 - object) (AUX14 ?y0)) (exists (?y0 - object) (AUX15 ?y0)) (exists (?y0 - object) (AUX16 ?y0)) (exists (?y0 - object) (AUX17 ?y0)) (exists (?y0 - object) (AUX18 ?y0)) (exists (?y0 - object) (AUX19 ?y0)) (exists (?y0 - object) (AUX2 ?y0)) (exists (?y0 - object) (AUX20 ?y0)) (exists (?y0 - object) (AUX21 ?y0)) (exists (?y0 - object) (AUX22 ?y0)) (exists (?y0 - object) (AUX23 ?y0)) (exists (?y0 - object) (AUX24 ?y0)) (exists (?y0 - object) (AUX25 ?y0)) (exists (?y0 - object) (AUX26 ?y0)) (exists (?y0 - object) (AUX27 ?y0)) (exists (?y0 - object) (AUX3 ?y0)) (exists (?y0 - object) (AUX4 ?y0)) (exists (?y0 - object) (AUX5 ?y0)) (exists (?y0 - object) (AUX6 ?y0)) (exists (?y0 - object) (AUX7 ?y0)) (exists (?y0 - object) (AUX8 ?y0)) (exists (?y0 - object) (AUX9 ?y0))))
(:derived (DATALOG_ABOVEOF3 ?x0 - object)
          (or (DATALOG_ABOVEOF4 ?x0) (aboveof3 ?x0)))
(:derived (DATALOG_LEFTOF7 ?x0 - object)
          (or (DATALOG_LEFTOF6 ?x0) (leftof7 ?x0)))
(:derived (DATALOG_ABOVEOF13 ?x0 - object)
          (or (aboveof13 ?x0) (aboveof14 ?x0)))
(:derived (DATALOG_LEFTOF5 ?x0 - object)
          (or (DATALOG_LEFTOF4 ?x0) (leftof5 ?x0)))
(:derived (DATALOG_BELOWOF13 ?x0 - object)
          (or (DATALOG_BELOWOF12 ?x0) (belowof13 ?x0)))
(:derived (DATALOG_BELOWOF5 ?x0 - object)
          (or (DATALOG_BELOWOF4 ?x0) (belowof5 ?x0)))
(:derived (DATALOG_ABOVEOF5 ?x0 - object)
          (or (DATALOG_ABOVEOF6 ?x0) (aboveof5 ?x0)))
(:derived (DATALOG_BELOWOF15 ?x0 - object)
          (or (DATALOG_BELOWOF14 ?x0) (belowof15 ?x0)))
(:derived (DATALOG_LEFTOF11 ?x0 - object)
          (or (DATALOG_LEFTOF10 ?x0) (leftof11 ?x0)))
(:derived (DATALOG_BELOWOF7 ?x0 - object)
          (or (DATALOG_BELOWOF6 ?x0) (belowof7 ?x0)))
(:derived (DATALOG_RIGHTOF6 ?x0 - object)
          (or (DATALOG_RIGHTOF7 ?x0) (rightof6 ?x0)))
(:derived (DATALOG_BELOWOF10 ?x0 - object)
          (or (DATALOG_BELOWOF9 ?x0) (belowof10 ?x0)))
(:derived (DATALOG_BELOWOF4 ?x0 - object)
          (or (DATALOG_BELOWOF3 ?x0) (belowof4 ?x0)))
(:derived (DATALOG_LEFTOF10 ?x0 - object)
          (or (DATALOG_LEFTOF9 ?x0) (leftof10 ?x0)))
(:derived (DATALOG_LEFTOF15 ?x0 - object)
          (or (DATALOG_LEFTOF14 ?x0) (leftof15 ?x0)))
(:derived (DATALOG_BELOWOF11 ?x0 - object)
          (or (DATALOG_BELOWOF10 ?x0) (belowof11 ?x0)))
(:derived (DATALOG_RIGHTOF1 ?x0 - object)
          (or (DATALOG_RIGHTOF2 ?x0) (rightof1 ?x0)))
(:derived (DATALOG_ABOVEOF8 ?x0 - object)
          (or (DATALOG_ABOVEOF9 ?x0) (aboveof8 ?x0)))
(:derived (DATALOG_BELOWOF14 ?x0 - object)
          (or (DATALOG_BELOWOF13 ?x0) (belowof14 ?x0)))
(:derived (DATALOG_RIGHTOF10 ?x0 - object)
          (or (DATALOG_RIGHTOF11 ?x0) (rightof10 ?x0)))
(:derived (DATALOG_LEFTOF6 ?x0 - object)
          (or (DATALOG_LEFTOF5 ?x0) (leftof6 ?x0)))
(:derived (DATALOG_RIGHTOF3 ?x0 - object)
          (or (DATALOG_RIGHTOF4 ?x0) (rightof3 ?x0)))
(:derived (DATALOG_RIGHTOF11 ?x0 - object)
          (or (DATALOG_RIGHTOF12 ?x0) (rightof11 ?x0)))
(:derived (DATALOG_LEFTOF4 ?x0 - object)
          (or (DATALOG_LEFTOF3 ?x0) (leftof4 ?x0)))
(:derived (DATALOG_BELOWOF2 ?x0 - object)
          (or (belowof1 ?x0) (belowof2 ?x0)))
(:derived (DATALOG_LEFTOF12 ?x0 - object)
          (or (DATALOG_LEFTOF11 ?x0) (leftof12 ?x0)))
(:derived (DATALOG_LEFTOF3 ?x0 - object)
          (or (DATALOG_LEFTOF2 ?x0) (leftof3 ?x0)))
(:derived (DATALOG_RIGHTOF2 ?x0 - object)
          (or (DATALOG_RIGHTOF3 ?x0) (rightof2 ?x0)))
(:derived (DATALOG_COLUMNS ?x0 - object)
          (or (DATALOG_LEFTOF15 ?x0) (DATALOG_RIGHTOF0 ?x0) (columns ?x0)))
(:derived (DATALOG_RIGHTOF4 ?x0 - object)
          (or (DATALOG_RIGHTOF5 ?x0) (rightof4 ?x0)))
(:derived (DATALOG_BELOWOF6 ?x0 - object)
          (or (DATALOG_BELOWOF5 ?x0) (belowof6 ?x0)))
(:derived (DATALOG_RIGHTOF0 ?x0 - object)
          (or (DATALOG_RIGHTOF1 ?x0) (rightof0 ?x0)))
(:derived (DATALOG_LEFTOF9 ?x0 - object)
          (or (DATALOG_LEFTOF8 ?x0) (leftof9 ?x0)))
(:derived (DATALOG_RIGHTOF8 ?x0 - object)
          (or (DATALOG_RIGHTOF9 ?x0) (rightof8 ?x0)))
(:derived (DATALOG_RIGHTOF9 ?x0 - object)
          (or (DATALOG_RIGHTOF10 ?x0) (rightof9 ?x0)))
(:derived (DATALOG_ABOVEOF11 ?x0 - object)
          (or (DATALOG_ABOVEOF12 ?x0) (aboveof11 ?x0)))
(:derived (DATALOG_BELOWOF8 ?x0 - object)
          (or (DATALOG_BELOWOF7 ?x0) (belowof8 ?x0)))
(:derived (DATALOG_BELOWOF3 ?x0 - object)
          (or (DATALOG_BELOWOF2 ?x0) (belowof3 ?x0)))
(:derived (DATALOG_ABOVEOF1 ?x0 - object)
          (or (DATALOG_ABOVEOF2 ?x0) (aboveof1 ?x0)))
(:derived (DATALOG_ROWS ?x0 - object)
          (or (DATALOG_ABOVEOF0 ?x0) (DATALOG_BELOWOF15 ?x0) (rows ?x0)))
(:derived (DATALOG_LEFTOF14 ?x0 - object)
          (or (DATALOG_LEFTOF13 ?x0) (leftof14 ?x0)))
(:derived (DATALOG_ABOVEOF0 ?x0 - object)
          (or (DATALOG_ABOVEOF1 ?x0) (aboveof0 ?x0)))
(:derived (DATALOG_ABOVEOF6 ?x0 - object)
          (or (DATALOG_ABOVEOF7 ?x0) (aboveof6 ?x0)))
(:derived (DATALOG_RIGHTOF13 ?x0 - object)
          (or (rightof13 ?x0) (rightof14 ?x0)))
(:derived (DATALOG_ABOVEOF4 ?x0 - object)
          (or (DATALOG_ABOVEOF5 ?x0) (aboveof4 ?x0)))
(:derived (DATALOG_LEFTOF2 ?x0 - object)
          (or (leftof1 ?x0) (leftof2 ?x0)))
(:derived (DATALOG_ABOVEOF2 ?x0 - object)
          (or (DATALOG_ABOVEOF3 ?x0) (aboveof2 ?x0)))
(:derived (DATALOG_LEFTOF8 ?x0 - object)
          (or (DATALOG_LEFTOF7 ?x0) (leftof8 ?x0)))
(:derived (DATALOG_RIGHTOF12 ?x0 - object)
          (or (DATALOG_RIGHTOF13 ?x0) (rightof12 ?x0)))
(:derived (DATALOG_RIGHTOF7 ?x0 - object)
          (or (DATALOG_RIGHTOF8 ?x0) (rightof7 ?x0)))
(:derived (DATALOG_LEFTOF13 ?x0 - object)
          (or (DATALOG_LEFTOF12 ?x0) (leftof13 ?x0)))
(:derived (DATALOG_ABOVEOF7 ?x0 - object)
          (or (DATALOG_ABOVEOF8 ?x0) (aboveof7 ?x0)))
(:derived (DATALOG_ABOVEOF9 ?x0 - object)
          (or (DATALOG_ABOVEOF10 ?x0) (aboveof9 ?x0)))
(:derived (DATALOG_ABOVEOF12 ?x0 - object)
          (or (DATALOG_ABOVEOF13 ?x0) (aboveof12 ?x0)))
(:derived (DATALOG_BELOWOF9 ?x0 - object)
          (or (DATALOG_BELOWOF8 ?x0) (belowof9 ?x0)))
(:derived (DATALOG_RIGHTOF5 ?x0 - object)
          (or (DATALOG_RIGHTOF6 ?x0) (rightof5 ?x0)))
(:derived (DATALOG_BELOWOF12 ?x0 - object)
          (or (DATALOG_BELOWOF11 ?x0) (belowof12 ?x0)))
(:derived (DATALOG_ABOVEOF10 ?x0 - object)
          (or (DATALOG_ABOVEOF11 ?x0) (aboveof10 ?x0)))
(:derived (AUX0 ?y0 - object)
          (and (DATALOG_ABOVEOF3 ?y0) (DATALOG_BELOWOF3 ?y0)))
(:derived (AUX1 ?y0 - object)
          (and (DATALOG_ABOVEOF13 ?y0) (DATALOG_BELOWOF13 ?y0)))
(:derived (AUX2 ?y0 - object)
          (and (DATALOG_ABOVEOF8 ?y0) (DATALOG_BELOWOF8 ?y0)))
(:derived (AUX3 ?y0 - object)
          (and (DATALOG_LEFTOF5 ?y0) (DATALOG_RIGHTOF5 ?y0)))
(:derived (AUX4 ?y0 - object)
          (and (DATALOG_ABOVEOF12 ?y0) (DATALOG_BELOWOF12 ?y0)))
(:derived (AUX5 ?y0 - object)
          (and (DATALOG_LEFTOF9 ?y0) (DATALOG_RIGHTOF9 ?y0)))
(:derived (AUX6 ?y0 - object)
          (and (DATALOG_LEFTOF3 ?y0) (DATALOG_RIGHTOF3 ?y0)))
(:derived (AUX7 ?y0 - object)
          (and (DATALOG_LEFTOF12 ?y0) (DATALOG_RIGHTOF12 ?y0)))
(:derived (AUX8 ?y0 - object)
          (and (DATALOG_ABOVEOF9 ?y0) (DATALOG_BELOWOF9 ?y0)))
(:derived (AUX9 ?y0 - object)
          (and (DATALOG_LEFTOF2 ?y0) (DATALOG_RIGHTOF2 ?y0)))
(:derived (AUX10 ?y0 - object)
          (and (DATALOG_LEFTOF14 ?y0) (rightof14 ?y0)))
(:derived (AUX11 ?y0 - object)
          (and (DATALOG_ABOVEOF7 ?y0) (DATALOG_BELOWOF7 ?y0)))
(:derived (AUX12 ?y0 - object)
          (and (DATALOG_LEFTOF11 ?y0) (DATALOG_RIGHTOF11 ?y0)))
(:derived (AUX13 ?y0 - object)
          (and (DATALOG_LEFTOF10 ?y0) (DATALOG_RIGHTOF10 ?y0)))
(:derived (AUX14 ?y0 - object)
          (and (DATALOG_ABOVEOF5 ?y0) (DATALOG_BELOWOF5 ?y0)))
(:derived (AUX15 ?y0 - object)
          (and (DATALOG_ABOVEOF10 ?y0) (DATALOG_BELOWOF10 ?y0)))
(:derived (AUX16 ?y0 - object)
          (and (DATALOG_LEFTOF6 ?y0) (DATALOG_RIGHTOF6 ?y0)))
(:derived (AUX17 ?y0 - object)
          (and (DATALOG_BELOWOF14 ?y0) (aboveof14 ?y0)))
(:derived (AUX18 ?y0 - object)
          (and (DATALOG_LEFTOF13 ?y0) (DATALOG_RIGHTOF13 ?y0)))
(:derived (AUX19 ?y0 - object)
          (and (DATALOG_ABOVEOF4 ?y0) (DATALOG_BELOWOF4 ?y0)))
(:derived (AUX20 ?y0 - object)
          (and (DATALOG_RIGHTOF1 ?y0) (leftof1 ?y0)))
(:derived (AUX21 ?y0 - object)
          (and (DATALOG_LEFTOF4 ?y0) (DATALOG_RIGHTOF4 ?y0)))
(:derived (AUX22 ?y0 - object)
          (and (DATALOG_LEFTOF8 ?y0) (DATALOG_RIGHTOF8 ?y0)))
(:derived (AUX23 ?y0 - object)
          (and (DATALOG_ABOVEOF1 ?y0) (belowof1 ?y0)))
(:derived (AUX24 ?y0 - object)
          (and (DATALOG_LEFTOF7 ?y0) (DATALOG_RIGHTOF7 ?y0)))
(:derived (AUX25 ?y0 - object)
          (and (DATALOG_ABOVEOF6 ?y0) (DATALOG_BELOWOF6 ?y0)))
(:derived (AUX26 ?y0 - object)
          (and (DATALOG_ABOVEOF2 ?y0) (DATALOG_BELOWOF2 ?y0)))
(:derived (AUX27 ?y0 - object)
          (and (DATALOG_ABOVEOF11 ?y0) (DATALOG_BELOWOF11 ?y0)))
(:action moveRight
  :parameters (?x - object)
  :precondition (and (DATALOG_COLUMNS ?x) (not (DATALOG_INCONSISTENT)))
  :effect (and (when (DATALOG_RIGHTOF0 ?x) (and (rightof1 ?x))) (when (DATALOG_RIGHTOF1 ?x) (and (rightof2 ?x))) (when (DATALOG_RIGHTOF2 ?x) (and (rightof3 ?x))) (when (DATALOG_RIGHTOF3 ?x) (and (rightof4 ?x))) (when (DATALOG_RIGHTOF4 ?x) (and (rightof5 ?x))) (when (DATALOG_RIGHTOF5 ?x) (and (rightof6 ?x))) (when (DATALOG_RIGHTOF6 ?x) (and (rightof7 ?x))) (when (DATALOG_RIGHTOF7 ?x) (and (rightof8 ?x))) (when (DATALOG_RIGHTOF8 ?x) (and (rightof9 ?x))) (when (DATALOG_RIGHTOF9 ?x) (and (rightof10 ?x))) (when (DATALOG_RIGHTOF10 ?x) (and (rightof11 ?x))) (when (DATALOG_RIGHTOF11 ?x) (and (rightof12 ?x))) (when (DATALOG_RIGHTOF12 ?x) (and (rightof13 ?x))) (when (DATALOG_RIGHTOF13 ?x) (and (rightof14 ?x))) (when (leftof1 ?x) (and (leftof2 ?x) (not (leftof1 ?x)))) (when (DATALOG_LEFTOF2 ?x) (and (leftof3 ?x) (not (leftof2 ?x)))) (when (DATALOG_LEFTOF3 ?x) (and (leftof4 ?x) (not (leftof3 ?x)))) (when (DATALOG_LEFTOF4 ?x) (and (leftof5 ?x) (not (leftof4 ?x)))) (when (DATALOG_LEFTOF5 ?x) (and (leftof6 ?x) (not (leftof5 ?x)))) (when (DATALOG_LEFTOF6 ?x) (and (leftof7 ?x) (not (leftof6 ?x)))) (when (DATALOG_LEFTOF7 ?x) (and (leftof8 ?x) (not (leftof7 ?x)))) (when (DATALOG_LEFTOF8 ?x) (and (leftof9 ?x) (not (leftof8 ?x)))) (when (DATALOG_LEFTOF9 ?x) (and (leftof10 ?x) (not (leftof9 ?x)))) (when (DATALOG_LEFTOF10 ?x) (and (leftof11 ?x) (not (leftof10 ?x)))) (when (DATALOG_LEFTOF11 ?x) (and (leftof12 ?x) (not (leftof11 ?x)))) (when (DATALOG_LEFTOF12 ?x) (and (leftof13 ?x) (not (leftof12 ?x)))) (when (DATALOG_LEFTOF13 ?x) (and (leftof14 ?x) (not (leftof13 ?x)))) (when (DATALOG_LEFTOF14 ?x) (and (leftof15 ?x) (not (leftof14 ?x)))) (when (column0 ?x) (and (column1 ?x) (not (column0 ?x)))) (when (column1 ?x) (and (column2 ?x) (not (column1 ?x)))) (when (column2 ?x) (and (column3 ?x) (not (column2 ?x)))) (when (column3 ?x) (and (column4 ?x) (not (column3 ?x)))) (when (column4 ?x) (and (column5 ?x) (not (column4 ?x)))) (when (column5 ?x) (and (column6 ?x) (not (column5 ?x)))) (when (column6 ?x) (and (column7 ?x) (not (column6 ?x)))) (when (column7 ?x) (and (column8 ?x) (not (column7 ?x)))) (when (column8 ?x) (and (column9 ?x) (not (column8 ?x)))) (when (column9 ?x) (and (column10 ?x) (not (column9 ?x)))) (when (column10 ?x) (and (column11 ?x) (not (column10 ?x)))) (when (column11 ?x) (and (column12 ?x) (not (column11 ?x)))) (when (column12 ?x) (and (column13 ?x) (not (column12 ?x)))) (when (column13 ?x) (and (column14 ?x) (not (column13 ?x)))) (when (DATALOG_QUERY0 ?x) (and (column1 ?x))) (when (DATALOG_QUERY1 ?x) (and (column2 ?x))) (when (DATALOG_QUERY2 ?x) (and (column3 ?x))) (when (DATALOG_QUERY3 ?x) (and (column4 ?x))) (when (DATALOG_QUERY4 ?x) (and (column5 ?x))) (when (DATALOG_QUERY5 ?x) (and (column6 ?x))) (when (DATALOG_QUERY6 ?x) (and (column7 ?x))) (when (DATALOG_QUERY7 ?x) (and (column8 ?x))) (when (DATALOG_QUERY8 ?x) (and (column9 ?x))) (when (DATALOG_QUERY9 ?x) (and (column10 ?x))) (when (DATALOG_QUERY10 ?x) (and (column11 ?x))) (when (DATALOG_QUERY11 ?x) (and (column12 ?x))) (when (DATALOG_QUERY12 ?x) (and (column13 ?x))) (when (DATALOG_QUERY13 ?x) (and (column14 ?x)))))
(:action moveLeft
  :parameters (?x - object)
  :precondition (and (DATALOG_COLUMNS ?x) (not (DATALOG_INCONSISTENT)))
  :effect (and (when (DATALOG_LEFTOF2 ?x) (and (leftof1 ?x))) (when (DATALOG_LEFTOF3 ?x) (and (leftof2 ?x))) (when (DATALOG_LEFTOF4 ?x) (and (leftof3 ?x))) (when (DATALOG_LEFTOF5 ?x) (and (leftof4 ?x))) (when (DATALOG_LEFTOF6 ?x) (and (leftof5 ?x))) (when (DATALOG_LEFTOF7 ?x) (and (leftof6 ?x))) (when (DATALOG_LEFTOF8 ?x) (and (leftof7 ?x))) (when (DATALOG_LEFTOF9 ?x) (and (leftof8 ?x))) (when (DATALOG_LEFTOF10 ?x) (and (leftof9 ?x))) (when (DATALOG_LEFTOF11 ?x) (and (leftof10 ?x))) (when (DATALOG_LEFTOF12 ?x) (and (leftof11 ?x))) (when (DATALOG_LEFTOF13 ?x) (and (leftof12 ?x))) (when (DATALOG_LEFTOF14 ?x) (and (leftof13 ?x))) (when (DATALOG_LEFTOF15 ?x) (and (leftof14 ?x))) (when (DATALOG_RIGHTOF1 ?x) (and (rightof0 ?x) (rightof1 ?x))) (when (DATALOG_RIGHTOF2 ?x) (and (rightof1 ?x) (rightof2 ?x))) (when (DATALOG_RIGHTOF3 ?x) (and (rightof2 ?x) (rightof3 ?x))) (when (DATALOG_RIGHTOF4 ?x) (and (rightof3 ?x) (rightof4 ?x))) (when (DATALOG_RIGHTOF5 ?x) (and (rightof4 ?x) (rightof5 ?x))) (when (DATALOG_RIGHTOF6 ?x) (and (rightof5 ?x) (rightof6 ?x))) (when (DATALOG_RIGHTOF7 ?x) (and (rightof6 ?x) (rightof7 ?x))) (when (DATALOG_RIGHTOF8 ?x) (and (rightof7 ?x) (rightof8 ?x))) (when (DATALOG_RIGHTOF9 ?x) (and (rightof8 ?x) (rightof9 ?x))) (when (DATALOG_RIGHTOF10 ?x) (and (rightof9 ?x) (rightof10 ?x))) (when (DATALOG_RIGHTOF11 ?x) (and (rightof10 ?x) (rightof11 ?x))) (when (DATALOG_RIGHTOF12 ?x) (and (rightof11 ?x) (rightof12 ?x))) (when (DATALOG_RIGHTOF13 ?x) (and (rightof12 ?x) (rightof13 ?x))) (when (rightof14 ?x) (and (rightof13 ?x) (rightof14 ?x))) (when (column1 ?x) (and (column0 ?x) (not (column1 ?x)))) (when (column2 ?x) (and (column1 ?x) (not (column2 ?x)))) (when (column3 ?x) (and (column2 ?x) (not (column3 ?x)))) (when (column4 ?x) (and (column3 ?x) (not (column4 ?x)))) (when (column5 ?x) (and (column4 ?x) (not (column5 ?x)))) (when (column6 ?x) (and (column5 ?x) (not (column6 ?x)))) (when (column7 ?x) (and (column6 ?x) (not (column7 ?x)))) (when (column8 ?x) (and (column7 ?x) (not (column8 ?x)))) (when (column9 ?x) (and (column8 ?x) (not (column9 ?x)))) (when (column10 ?x) (and (column9 ?x) (not (column10 ?x)))) (when (column11 ?x) (and (column10 ?x) (not (column11 ?x)))) (when (column12 ?x) (and (column11 ?x) (not (column12 ?x)))) (when (column13 ?x) (and (column12 ?x) (not (column13 ?x)))) (when (column14 ?x) (and (column13 ?x) (not (column14 ?x)))) (when (or ) (and (column0 ?x))) (when (or ) (and (column1 ?x))) (when (or ) (and (column2 ?x))) (when (or ) (and (column3 ?x))) (when (or ) (and (column4 ?x))) (when (or ) (and (column5 ?x))) (when (or ) (and (column6 ?x))) (when (or ) (and (column7 ?x))) (when (or ) (and (column8 ?x))) (when (or ) (and (column9 ?x))) (when (or ) (and (column10 ?x))) (when (or ) (and (column11 ?x))) (when (or ) (and (column12 ?x))) (when (DATALOG_QUERY27 ?x) (and (column13 ?x)))))
(:action moveUp
  :parameters (?x - object)
  :precondition (and (DATALOG_ROWS ?x) (not (DATALOG_INCONSISTENT)))
  :effect (and (when (DATALOG_ABOVEOF0 ?x) (and (aboveof1 ?x))) (when (DATALOG_ABOVEOF1 ?x) (and (aboveof2 ?x))) (when (DATALOG_ABOVEOF2 ?x) (and (aboveof3 ?x))) (when (DATALOG_ABOVEOF3 ?x) (and (aboveof4 ?x))) (when (DATALOG_ABOVEOF4 ?x) (and (aboveof5 ?x))) (when (DATALOG_ABOVEOF5 ?x) (and (aboveof6 ?x))) (when (DATALOG_ABOVEOF6 ?x) (and (aboveof7 ?x))) (when (DATALOG_ABOVEOF7 ?x) (and (aboveof8 ?x))) (when (DATALOG_ABOVEOF8 ?x) (and (aboveof9 ?x))) (when (DATALOG_ABOVEOF9 ?x) (and (aboveof10 ?x))) (when (DATALOG_ABOVEOF10 ?x) (and (aboveof11 ?x))) (when (DATALOG_ABOVEOF11 ?x) (and (aboveof12 ?x))) (when (DATALOG_ABOVEOF12 ?x) (and (aboveof13 ?x))) (when (DATALOG_ABOVEOF13 ?x) (and (aboveof14 ?x))) (when (belowof1 ?x) (and (belowof2 ?x) (not (belowof1 ?x)))) (when (DATALOG_BELOWOF2 ?x) (and (belowof3 ?x) (not (belowof2 ?x)))) (when (DATALOG_BELOWOF3 ?x) (and (belowof4 ?x) (not (belowof3 ?x)))) (when (DATALOG_BELOWOF4 ?x) (and (belowof5 ?x) (not (belowof4 ?x)))) (when (DATALOG_BELOWOF5 ?x) (and (belowof6 ?x) (not (belowof5 ?x)))) (when (DATALOG_BELOWOF6 ?x) (and (belowof7 ?x) (not (belowof6 ?x)))) (when (DATALOG_BELOWOF7 ?x) (and (belowof8 ?x) (not (belowof7 ?x)))) (when (DATALOG_BELOWOF8 ?x) (and (belowof9 ?x) (not (belowof8 ?x)))) (when (DATALOG_BELOWOF9 ?x) (and (belowof10 ?x) (not (belowof9 ?x)))) (when (DATALOG_BELOWOF10 ?x) (and (belowof11 ?x) (not (belowof10 ?x)))) (when (DATALOG_BELOWOF11 ?x) (and (belowof12 ?x) (not (belowof11 ?x)))) (when (DATALOG_BELOWOF12 ?x) (and (belowof13 ?x) (not (belowof12 ?x)))) (when (DATALOG_BELOWOF13 ?x) (and (belowof14 ?x) (not (belowof13 ?x)))) (when (DATALOG_BELOWOF14 ?x) (and (belowof15 ?x) (not (belowof14 ?x)))) (when (row0 ?x) (and (row1 ?x) (not (row0 ?x)))) (when (row1 ?x) (and (row2 ?x) (not (row1 ?x)))) (when (row2 ?x) (and (row3 ?x) (not (row2 ?x)))) (when (row3 ?x) (and (row4 ?x) (not (row3 ?x)))) (when (row4 ?x) (and (row5 ?x) (not (row4 ?x)))) (when (row5 ?x) (and (row6 ?x) (not (row5 ?x)))) (when (row6 ?x) (and (row7 ?x) (not (row6 ?x)))) (when (row7 ?x) (and (row8 ?x) (not (row7 ?x)))) (when (row8 ?x) (and (row9 ?x) (not (row8 ?x)))) (when (row9 ?x) (and (row10 ?x) (not (row9 ?x)))) (when (row10 ?x) (and (row11 ?x) (not (row10 ?x)))) (when (row11 ?x) (and (row12 ?x) (not (row11 ?x)))) (when (row12 ?x) (and (row13 ?x) (not (row12 ?x)))) (when (row13 ?x) (and (row14 ?x) (not (row13 ?x)))) (when (DATALOG_QUERY28 ?x) (and (row1 ?x))) (when (DATALOG_QUERY29 ?x) (and (row2 ?x))) (when (DATALOG_QUERY30 ?x) (and (row3 ?x))) (when (DATALOG_QUERY31 ?x) (and (row4 ?x))) (when (DATALOG_QUERY32 ?x) (and (row5 ?x))) (when (DATALOG_QUERY33 ?x) (and (row6 ?x))) (when (DATALOG_QUERY34 ?x) (and (row7 ?x))) (when (DATALOG_QUERY35 ?x) (and (row8 ?x))) (when (DATALOG_QUERY36 ?x) (and (row9 ?x))) (when (DATALOG_QUERY37 ?x) (and (row10 ?x))) (when (DATALOG_QUERY38 ?x) (and (row11 ?x))) (when (DATALOG_QUERY39 ?x) (and (row12 ?x))) (when (DATALOG_QUERY40 ?x) (and (row13 ?x))) (when (DATALOG_QUERY41 ?x) (and (row14 ?x)))))
(:action moveDown
  :parameters (?x - object)
  :precondition (and (DATALOG_ROWS ?x) (not (DATALOG_INCONSISTENT)))
  :effect (and (when (DATALOG_BELOWOF2 ?x) (and (belowof1 ?x))) (when (DATALOG_BELOWOF3 ?x) (and (belowof2 ?x))) (when (DATALOG_BELOWOF4 ?x) (and (belowof3 ?x))) (when (DATALOG_BELOWOF5 ?x) (and (belowof4 ?x))) (when (DATALOG_BELOWOF6 ?x) (and (belowof5 ?x))) (when (DATALOG_BELOWOF7 ?x) (and (belowof6 ?x))) (when (DATALOG_BELOWOF8 ?x) (and (belowof7 ?x))) (when (DATALOG_BELOWOF9 ?x) (and (belowof8 ?x))) (when (DATALOG_BELOWOF10 ?x) (and (belowof9 ?x))) (when (DATALOG_BELOWOF11 ?x) (and (belowof10 ?x))) (when (DATALOG_BELOWOF12 ?x) (and (belowof11 ?x))) (when (DATALOG_BELOWOF13 ?x) (and (belowof12 ?x))) (when (DATALOG_BELOWOF14 ?x) (and (belowof13 ?x))) (when (DATALOG_BELOWOF15 ?x) (and (belowof14 ?x))) (when (DATALOG_ABOVEOF1 ?x) (and (aboveof0 ?x) (not (aboveof1 ?x)))) (when (DATALOG_ABOVEOF2 ?x) (and (aboveof1 ?x) (not (aboveof2 ?x)))) (when (DATALOG_ABOVEOF3 ?x) (and (aboveof2 ?x) (not (aboveof3 ?x)))) (when (DATALOG_ABOVEOF4 ?x) (and (aboveof3 ?x) (not (aboveof4 ?x)))) (when (DATALOG_ABOVEOF5 ?x) (and (aboveof4 ?x) (not (aboveof5 ?x)))) (when (DATALOG_ABOVEOF6 ?x) (and (aboveof5 ?x) (not (aboveof6 ?x)))) (when (DATALOG_ABOVEOF7 ?x) (and (aboveof6 ?x) (not (aboveof7 ?x)))) (when (DATALOG_ABOVEOF8 ?x) (and (aboveof7 ?x) (not (aboveof8 ?x)))) (when (DATALOG_ABOVEOF9 ?x) (and (aboveof8 ?x) (not (aboveof9 ?x)))) (when (DATALOG_ABOVEOF10 ?x) (and (aboveof9 ?x) (not (aboveof10 ?x)))) (when (DATALOG_ABOVEOF11 ?x) (and (aboveof10 ?x) (not (aboveof11 ?x)))) (when (DATALOG_ABOVEOF12 ?x) (and (aboveof11 ?x) (not (aboveof12 ?x)))) (when (DATALOG_ABOVEOF13 ?x) (and (aboveof12 ?x) (not (aboveof13 ?x)))) (when (aboveof14 ?x) (and (aboveof13 ?x) (not (aboveof14 ?x)))) (when (row1 ?x) (and (row0 ?x) (not (row1 ?x)))) (when (row2 ?x) (and (row1 ?x) (not (row2 ?x)))) (when (row3 ?x) (and (row2 ?x) (not (row3 ?x)))) (when (row4 ?x) (and (row3 ?x) (not (row4 ?x)))) (when (row5 ?x) (and (row4 ?x) (not (row5 ?x)))) (when (row6 ?x) (and (row5 ?x) (not (row6 ?x)))) (when (row7 ?x) (and (row6 ?x) (not (row7 ?x)))) (when (row8 ?x) (and (row7 ?x) (not (row8 ?x)))) (when (row9 ?x) (and (row8 ?x) (not (row9 ?x)))) (when (row10 ?x) (and (row9 ?x) (not (row10 ?x)))) (when (row11 ?x) (and (row10 ?x) (not (row11 ?x)))) (when (row12 ?x) (and (row11 ?x) (not (row12 ?x)))) (when (row13 ?x) (and (row12 ?x) (not (row13 ?x)))) (when (row14 ?x) (and (row13 ?x) (not (row14 ?x)))) (when (or ) (and (row0 ?x))) (when (or ) (and (row1 ?x))) (when (or ) (and (row2 ?x))) (when (or ) (and (row3 ?x))) (when (or ) (and (row4 ?x))) (when (or ) (and (row5 ?x))) (when (or ) (and (row6 ?x))) (when (or ) (and (row7 ?x))) (when (or ) (and (row8 ?x))) (when (or ) (and (row9 ?x))) (when (or ) (and (row10 ?x))) (when (or ) (and (row11 ?x))) (when (or ) (and (row12 ?x))) (when (DATALOG_QUERY55 ?x) (and (row13 ?x)))))
)