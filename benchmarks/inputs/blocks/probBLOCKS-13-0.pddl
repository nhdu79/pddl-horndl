(define (problem BLOCKS-13-0)
(:domain BLOCKS)
(:objects T L H E A J C D F G K M I B )
(:INIT (ONTABLE K T) (ONTABLE G T) (ONTABLE M T)
 (ONBLOCK B F) (ONBLOCK F D) (ONBLOCK D C) (ONBLOCK C J) (ONBLOCK J A) (ONBLOCK A E) (ONBLOCK E H) (ONBLOCK H L)
 (ONBLOCK L K) (ONBLOCK I G))
(:goal (AND (MKO (ON G I)) (MKO (ON I C)) (MKO (ON C D)) (MKO (ON D F)) (MKO (ON F A)) (MKO (ON A M)) (MKO (ON M H))
            (MKO (ON H E)) (MKO (ON E L)) (MKO (ON L J)) (MKO (ON J B)) (MKO (ON B K))))
)