(define (problem BLOCKS-15-1)
(:domain BLOCKS)
(:objects T J B K A D H E N C F L M I O G )
(:INIT (ONTABLE I T) (ONTABLE M T) (ONBLOCK G L) (ONBLOCK L F) (ONBLOCK F C)
 (ONBLOCK C N) (ONBLOCK N E) (ONBLOCK E H) (ONBLOCK H D) (ONBLOCK D A) (ONBLOCK A K) (ONBLOCK K B) (ONBLOCK B J)
 (ONBLOCK J I) (ONBLOCK O M))
(:goal (AND (MKO (ON D G)) (MKO (ON G F)) (MKO (ON F K)) (MKO (ON K J)) (MKO (ON J E)) (MKO (ON E M)) (MKO (ON M A))
            (MKO (ON A B)) (MKO (ON B C)) (MKO (ON C N)) (MKO (ON N O)) (MKO (ON O I)) (MKO (ON I L)) (MKO (ON L H))))
)