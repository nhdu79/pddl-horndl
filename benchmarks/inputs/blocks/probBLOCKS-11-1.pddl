(define (problem BLOCKS-11-1)
(:domain BLOCKS)
(:objects T B C E A H K I G D F J )
(:INIT (ONTABLE I T) (ONTABLE K T)
 (ONTABLE H T) (ONTABLE A T) (ONBLOCK J I) (ONBLOCK F E) (ONBLOCK E K) (ONBLOCK D C) (ONBLOCK C H) (ONBLOCK G B)
 (ONBLOCK B A))
(:goal (AND (MKO (ON B D)) (MKO (ON D J)) (MKO (ON J K)) (MKO (ON K H)) (MKO (ON H A)) (MKO (ON A C)) (MKO (ON C F))
            (MKO (ON F G)) (MKO (ON G I)) (MKO (ON I E))))
)