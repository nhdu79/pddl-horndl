(define (problem BLOCKS-9-0)
(:domain BLOCKS)
(:objects T H D I A E G B F C )
(:INIT (ONTABLE C T) (ONTABLE B T) (ONBLOCK F G) (ONBLOCK G E) (ONBLOCK E A)
 (ONBLOCK A I) (ONBLOCK I D) (ONBLOCK D H) (ONBLOCK H B))
(:goal (AND (MKO (ON G D)) (MKO (ON D B)) (MKO (ON B C)) (MKO (ON C A)) (MKO (ON A I)) (MKO (ON I F)) (MKO (ON F E))
            (MKO (ON E H))))
)