#!/usr/bin/env python3
"""
Generator for the Phone Assembly benchmark (Horn DL-Lite fragment).

Produces 10 problem instances (probPHONE_ASSEMBLY-{N}-0.pddl, N=1..10).

ceil(N/2) broken phones  (phone_1 … phone_{ceil(N/2)}):
    All three components are physically in the phone; the broken one is tracked
    by hasBrokenX(phone_i, comp_i).  The broken component type cycles:
    screen → battery → processor → screen → …
    The faulty component is NOT typed as Screen/Battery/Processor, so it cannot
    be inspected or installed.
    BOTH hasBrokenX AND XInstalledIn are in the init ABox so that HasX is derived,
    FullyEquipped holds, and BrokenPhone is derivable from the initial state.
    hasBrokenX drives HasDefect; HasDefect ⊓ FullyEquipped drives BrokenPhone.
    A spare component spare_X_i is available (uninstalled, typed as the working
    type).  All broken phones are under warranty.
    Plan: authorize-repair(phone) → repair(phone)
          → inspect(spare) → test(spare) → install-X(spare, phone)   [5 steps]
    repair fires Am_BrokenPhone AND Am_XInstalledIn(broken_comp, phone) together
    (via conditional effects), so both hasBrokenX and XInstalledIn(broken, phone)
    are deleted.  This clears HasX, unblocking install-X.  The authorize/repair
    pair and the inspect/test pair are mutually independent and can be freely
    interleaved, but both must complete before install-X.

floor(N/2) incomplete phones  (phone_{ceil(N/2)+1} … phone_N):
    No components installed, no warranty.
    Plan: inspect + test + install per component × 3   [9 steps]

Derived in init for each broken phone p (broken-screen case shown):
    HasDefect(p)     via ∃hasBrokenScreen ⊑ HasDefect
    HasScreen(p)     via ∃screenInstalledIn⁻ ⊑ HasScreen  (screenInstalledIn in ABox)
    HasBattery(p)    via ∃batteryInstalledIn⁻ ⊑ HasBattery
    HasProcessor(p)  via ∃processorInstalledIn⁻ ⊑ HasProcessor
    FullyEquipped(p) via HasScreen ⊓ HasBattery ⊓ HasProcessor ⊑ FullyEquipped
    BrokenPhone(p)   via HasDefect ⊓ FullyEquipped ⊑ BrokenPhone

Goal:
    ∀p. Phone(p) → FullyEquipped(p)
                 ∧ (UnderWarranty(p) → ¬HasDefect(p) ∧ WarrantyClaim(p))

Scaling (n_broken = ceil(N/2), n_incomplete = floor(N/2)):
    broken phone: 5 steps  (authorize-repair + repair + inspect + test + install-X)
    incomplete phone: 9 steps  (inspect + test + install × 3 components)
    N= 1:  1 broken,  0 incomplete  — minimal plan:  5 steps
    N= 2:  1 broken,  1 incomplete  — minimal plan: 14 steps
    N= 3:  2 broken,  1 incomplete  — minimal plan: 19 steps
    N= 4:  2 broken,  2 incomplete  — minimal plan: 28 steps
    N= 5:  3 broken,  2 incomplete  — minimal plan: 33 steps
    N= 6:  3 broken,  3 incomplete  — minimal plan: 42 steps
    N= 7:  4 broken,  3 incomplete  — minimal plan: 47 steps
    N= 8:  4 broken,  4 incomplete  — minimal plan: 56 steps
    N= 9:  5 broken,  4 incomplete  — minimal plan: 61 steps
    N=10:  5 broken,  5 incomplete  — minimal plan: 70 steps
"""

import pathlib

OUT = pathlib.Path(__file__).parent

_GOAL = """\
(forall (?p) (or (not (Phone ?p))
                 (and (MKO (FullyEquipped ?p))
                      (or (not (UnderWarranty ?p))
                          (and (not (MKO (HasDefect ?p)))
                               (MKO (WarrantyClaim ?p)))))))\
"""

# Broken component type cycles: screen → battery → processor → screen → …
_BROKEN_TYPES = ["screen", "battery", "processor"]


def _broken_type(i: int) -> str:
    """Return the broken component type for broken phone i (1-indexed)."""
    return _BROKEN_TYPES[(i - 1) % 3]


def objects_block(n: int) -> str:
    n_broken = (n + 1) // 2
    phones = [f"phone_{i}" for i in range(1, n + 1)]

    components: list[str] = []
    for i in range(1, n_broken + 1):
        bt = _broken_type(i)
        if bt == "screen":
            components += [f"screen_{i}", f"spare_screen_{i}", f"battery_{i}", f"processor_{i}"]
        elif bt == "battery":
            components += [f"screen_{i}", f"battery_{i}", f"spare_battery_{i}", f"processor_{i}"]
        else:  # processor
            components += [f"screen_{i}", f"battery_{i}", f"processor_{i}", f"spare_processor_{i}"]

    for i in range(n_broken + 1, n + 1):
        components += [f"screen_{i}", f"battery_{i}", f"processor_{i}"]

    all_objs = phones + components
    return "(:objects " + " ".join(all_objs) + " )"


def gen_instance(n: int) -> str:
    n_broken = (n + 1) // 2   # ceil(N/2)

    init_facts: list[str] = []

    for i in range(1, n + 1):
        init_facts.append(f"(Phone phone_{i})")

    for i in range(1, n_broken + 1):
        bt = _broken_type(i)
        init_facts.append(f"(UnderWarranty phone_{i})")

        if bt == "screen":
            # Broken screen: all three components physically in phone.
            # screenInstalledIn(screen_i, phone_i) + hasBrokenScreen → HasScreen +
            # HasDefect → FullyEquipped → BrokenPhone derivable from init.
            # spare_screen_i is the uncertified replacement.
            init_facts += [
                f"(hasBrokenScreen phone_{i} screen_{i})",
                f"(screenInstalledIn screen_{i} phone_{i})",
                f"(Battery battery_{i})",
                f"(batteryInstalledIn battery_{i} phone_{i})",
                f"(Processor processor_{i})",
                f"(processorInstalledIn processor_{i} phone_{i})",
                f"(Screen spare_screen_{i})",
            ]
        elif bt == "battery":
            # Broken battery: all three components physically in phone.
            # batteryInstalledIn(battery_i, phone_i) + hasBrokenBattery → HasBattery +
            # HasDefect → FullyEquipped → BrokenPhone derivable from init.
            # spare_battery_i is the uncertified replacement.
            init_facts += [
                f"(Screen screen_{i})",
                f"(screenInstalledIn screen_{i} phone_{i})",
                f"(hasBrokenBattery phone_{i} battery_{i})",
                f"(batteryInstalledIn battery_{i} phone_{i})",
                f"(Processor processor_{i})",
                f"(processorInstalledIn processor_{i} phone_{i})",
                f"(Battery spare_battery_{i})",
            ]
        else:  # processor
            # Broken processor: all three components physically in phone.
            # processorInstalledIn(processor_i, phone_i) + hasBrokenProcessor → HasProcessor +
            # HasDefect → FullyEquipped → BrokenPhone derivable from init.
            # spare_processor_i is the uncertified replacement.
            init_facts += [
                f"(Screen screen_{i})",
                f"(screenInstalledIn screen_{i} phone_{i})",
                f"(Battery battery_{i})",
                f"(batteryInstalledIn battery_{i} phone_{i})",
                f"(hasBrokenProcessor phone_{i} processor_{i})",
                f"(processorInstalledIn processor_{i} phone_{i})",
                f"(Processor spare_processor_{i})",
            ]

    # Incomplete phones: components present but not installed, no warranty.
    for i in range(n_broken + 1, n + 1):
        init_facts += [
            f"(Screen screen_{i})",
            f"(Battery battery_{i})",
            f"(Processor processor_{i})",
        ]

    init_str = "\n ".join(init_facts)
    return f"""\
(define (problem PHONE_ASSEMBLY-{n}-0)
(:domain phone_assembly)
{objects_block(n)}
(:init
 {init_str})
(:goal {_GOAL})
)"""


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for n in range(1, 11):
        path = OUT / f"probPHONE_ASSEMBLY-{n}-0.pddl"
        path.write_text(gen_instance(n))
        print(f"wrote {path.name}")

    print(f"\nTotal: 10 instances in {OUT}")
