(define (problem BLOCKS-14-0)
(:domain BLOCKS)
(:objects T I D B L C K M H J N E F G A )
(:INIT (ONTABLE E T) (ONTABLE N T) (ONTABLE F T)
 (ONBLOCK A J) (ONBLOCK J H) (ONBLOCK H M) (ONBLOCK M K) (ONBLOCK K C) (ONBLOCK C L) (ONBLOCK L B) (ONBLOCK B E)
 (ONBLOCK G D) (ONBLOCK D I) (ONBLOCK I N))
(:goal (AND (MKO (ON E L)) (MKO (ON L F)) (MKO (ON F B)) (MKO (ON B J)) (MKO (ON J I)) (MKO (ON I N)) (MKO (ON N C))
            (MKO (ON C K)) (MKO (ON K G)) (MKO (ON G D)) (MKO (ON D M)) (MKO (ON M A)) (MKO (ON A H))))
)