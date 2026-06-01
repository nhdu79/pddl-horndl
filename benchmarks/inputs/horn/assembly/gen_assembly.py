#!/usr/bin/env python3
"""
Generator for the Assembly benchmark (Horn DL-Lite fragment).

Produces 10 problem instances that scale linearly:

  probASSEMBLY-{N}-0.pddl  (N=1..5)  — clean start: all components uncertified,
      nothing installed.  Goal = FullyEquipped for all phones.

  probASSEMBLY-{N}-1.pddl  (N=2..6)  — rework + quality-record: odd-indexed phones
      start fully assembled and pre-validated (ProductRecord derived in init); even
      phones start empty.  The planner must rework a dual-screen odd phone to release
      a screen for each empty even phone; stratum 3 preserves ProductRecord on the
      reworked phone (Validated holds at rework time).  Goal = ProductRecord for all.

Objects per instance: N phones + N screens (Screen) + N batteries (Battery)
                      + N boards (Processor).
"""

import pathlib

OUT = pathlib.Path(__file__).parent


def objects_block(n: int) -> str:
    phones    = [f"phone_{i}" for i in range(1, n + 1)]
    screens   = [f"screen_{i}" for i in range(1, n + 1)]
    batteries = [f"battery_{i}" for i in range(1, n + 1)]
    boards    = [f"board_{i}" for i in range(1, n + 1)]
    return "(:objects " + " ".join(phones + screens + batteries + boards) + " )"


# ── Variant 0: clean start ────────────────────────────────────────────────────
#
# All components uncertified and uninstalled.
# Minimal plan: certify + install per component × 3 × N = 6N steps.

def gen_var0(n: int) -> str:
    init_facts: list[str] = []
    for i in range(1, n + 1):
        init_facts += [
            f"(Screen screen_{i})",
            f"(Battery battery_{i})",
            f"(Processor board_{i})",
        ]
    init_str = "\n ".join(init_facts)
    goals = " ".join(f"(MKO (FullyEquipped phone_{i}))" for i in range(1, n + 1))
    return f"""\
(define (problem ASSEMBLY-{n}-0)
(:domain assembly)
{objects_block(n)}
(:init
 {init_str})
(:goal (AND {goals}))
)"""


# ── Variant 1: rework + quality-record ───────────────────────────────────────
#
# Odd phones start fully assembled (all 3 components installed) but NOT validated:
#   FullyEquipped is derived in init; Validated is absent.
#   The goal (ProductRecord) is therefore unsatisfied for every phone at the start.
#
# Screens are stacked in pairs on odd phones:
#   screen_i → phone_{2⌈i/2⌉ − 1}  (sequence: 1, 1, 3, 3, 5, 5, …)
# Batteries and boards for odd phones are pre-installed (no certification needed).
#
# Even phones start empty — no installed components, no certification.
#
# Optimal plan: validate odd phones FIRST (requiring FullyEquipped, already derived),
# then call remove-and-rework-screen.  Because Validated is now set when the rework
# fires, stratum 3 (rules 18-19) triggers:
#   preInsCl: AOrApCl_FullyEquipped ∧ AOrApCl_Validated ∧ ¬DelCl_ProductRecord
#   insCl_ProductRecord ← DelCl_FullyEquipped ∧ preInsCl
#   ins_ProductRecord: ProductRecord explicitly asserted — no re-validation needed.
#
# Alternative (suboptimal): rework without validating first → stratum 3 does not fire
# → planner must reinstall a screen + re-validate afterwards (2 extra steps per phone).
# The planner therefore discovers that validate-then-rework is strictly optimal.
#
# The non-reworked screen (still certified) installs immediately on the even phone.
# The reworked screen has Inspected shielded, Tested deleted; one certify restores it.
#
# Minimal plan (N=2): validate(1) + rework(1) + install-screen(1) + certify-battery(1)
#   + install-battery(1) + certify-board(1) + install-board(1) + validate(1) = 8 steps.
# General: ≈ 4N steps.

def gen_var1(n: int) -> str:
    """Odd phones fully assembled but not validated; even phones empty; goal = ProductRecord."""
    init_facts: list[str] = []

    # ── Screens: pre-certified, stacked in pairs on odd phones ─────────────────
    for i in range(1, n + 1):
        # screen_i → phone_{2⌈i/2⌉ − 1}  (sequence: 1, 1, 3, 3, 5, 5, …)
        target_phone = 2 * ((i + 1) // 2) - 1
        init_facts += [
            f"(Screen screen_{i})",
            f"(Inspected screen_{i})",
            f"(Tested screen_{i})",
            f"(screenInstalledIn screen_{i} phone_{target_phone})",
        ]

    # ── Batteries and boards: type predicates for all ─────────────────────────
    for i in range(1, n + 1):
        init_facts += [
            f"(Battery battery_{i})",
            f"(Processor board_{i})",
        ]

    # ── Odd phones: battery + board pre-installed; Validated intentionally absent ──
    for i in range(1, n + 1, 2):   # i = 1, 3, 5, …
        init_facts += [
            f"(batteryInstalledIn battery_{i} phone_{i})",
            f"(boardInstalledIn board_{i} phone_{i})",
        ]

    init_str = "\n ".join(init_facts)
    goals = " ".join(f"(MKO (ProductRecord phone_{i}))" for i in range(1, n + 1))
    return f"""\
(define (problem ASSEMBLY-{n}-1)
(:domain assembly)
{objects_block(n)}
(:init
 {init_str})
(:goal (AND {goals}))
)"""


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for n in range(1, 6):
        path = OUT / f"probASSEMBLY-{n}-0.pddl"
        path.write_text(gen_var0(n))
        print(f"wrote {path.name}")

    for n in range(2, 7):
        path = OUT / f"probASSEMBLY-{n}-1.pddl"
        path.write_text(gen_var1(n))
        print(f"wrote {path.name}")

    print(f"\nTotal: 10 instances in {OUT}")
