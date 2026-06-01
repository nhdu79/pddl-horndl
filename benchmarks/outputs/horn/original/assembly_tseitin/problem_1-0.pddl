(define (problem ASSEMBLY-1-0)
(:domain assembly)
(:init
       (screen screen_1)
       (battery battery_1)
       (processor board_1))
(:goal (and (DATALOG_FULLYEQUIPPED phone_1) (not (DATALOG_INCONSISTENT))))
)