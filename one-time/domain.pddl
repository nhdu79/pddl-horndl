(define (domain Test)
(:constants
  a - object
  b - object
  c - object)
(:predicates
  (preda ?x - object)
  (predb ?x - object)
  (predc ?x - object)
  (predd ?x - object)
  (prede ?x - object)
  (predf ?x - object)
  (predg ?x - object))
(:derived (predg ?x - object)
          (or (and (preda ?x) (exists (?y - object) (or (predb ?y) (predc ?x)))) (and (predd ?x) (prede ?x))))
)
