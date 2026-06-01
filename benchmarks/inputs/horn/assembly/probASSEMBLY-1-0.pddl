(define (problem ASSEMBLY-1-0)
(:domain assembly)
(:objects phone_1 screen_1 battery_1 board_1 )
(:init
 (Screen screen_1)
 (Battery battery_1)
 (Processor board_1))
(:goal (AND (MKO (FullyEquipped phone_1))))
)