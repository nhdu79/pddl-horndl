#!/usr/bin/env python3
"""Generator for the dronesv2 benchmark (Horn DL-Lite fragment).

Grid layout for an N×N grid:
  Rows/columns are labelled a..z (indices 0..N-1).
  Cell (row i, col j) is named chr('a'+i) + chr('a'+j), e.g. (1,2) → "bc".

Spatial relations stored in the ABox (both directions for symmetry):
  veryClose  — orthogonal neighbours (Manhattan distance 1)
  near       — diagonal neighbours (Chebyshev distance 1, non-orthogonal)

Sub-role ABox facts (maintained by the Move action):
  nearObject(a,b)      — a is near b, and b is an Objectx (Drone/Human/Tree)
  nearMoving(a,b)      — a is near b, and b is a MovingObject (Drone/Human)
  veryCloseObject(a,b) — a is veryClose to b, and b is an Objectx

Output: benchmarks/inputs/horn/dronesv2/droneProblem{N}-{M}.pddl
"""

import os
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "benchmarks" / "inputs" / "horn" / "dronesv2"


# ─── Cell helpers ─────────────────────────────────────────────────────────────

def cell(r: int, c: int) -> str:
    return chr(ord('a') + r) + chr(ord('a') + c)


# ─── Grid topology ────────────────────────────────────────────────────────────

def veryclose_pairs(n: int) -> set[tuple[str, str]]:
    """Orthogonal neighbours, both directions."""
    pairs: set[tuple[str, str]] = set()
    for r in range(n):
        for c in range(n - 1):
            pairs.add((cell(r, c), cell(r, c + 1)))
            pairs.add((cell(r, c + 1), cell(r, c)))
    for r in range(n - 1):
        for c in range(n):
            pairs.add((cell(r, c), cell(r + 1, c)))
            pairs.add((cell(r + 1, c), cell(r, c)))
    return pairs


def near_diagonal_pairs(n: int) -> set[tuple[str, str]]:
    """Diagonal neighbours, both directions."""
    pairs: set[tuple[str, str]] = set()
    for r in range(n - 1):
        for c in range(n - 1):
            pairs.add((cell(r, c), cell(r + 1, c + 1)))
            pairs.add((cell(r + 1, c + 1), cell(r, c)))
        for c in range(1, n):
            pairs.add((cell(r, c), cell(r + 1, c - 1)))
            pairs.add((cell(r + 1, c - 1), cell(r, c)))
    return pairs


# ─── Object placement ─────────────────────────────────────────────────────────
#
# Deterministic placement that scales cleanly with N and M:
#
#   WetDrone : grid centre (N//2, N//2) — also an environmentRain cell so the
#              3-way risk axiom (Drone ⊓ ∃environmentLow ⊓ ∃nearObject ⊑ Risk)
#              fires via the environmentRain ⊑ environmentLow sub-role.
#
#   Drones   : M-1 regular drones at the 8 compass/diagonal offsets from centre.
#              For M up to 8 (WetDrone + 7 offsets) this never goes out of bounds
#              for N ≥ 4.
#
#   Humans   : 3 fixed positions at far corners/edges.
#   Trees    : 3 fixed positions at edges.
#
#   Env cells: 5 positions in low-visibility zone get (environmentLow cell env).
#              WetDrone centre gets (environmentRain cell rain_env) instead.

_DRONE_OFFSETS = [(0, 1), (-1, 0), (1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]


def place_objects(n: int, m: int) -> dict:
    """Return placement dicts for an N×N grid with M drones (1 WetDrone + M-1 Drones)."""
    cr, cc = n // 2, n // 2  # grid centre

    wetdrone = (cr, cc)

    # Drones at the first M-1 compass/diagonal offsets from centre
    drones = [(cr + dr, cc + dc) for dr, dc in _DRONE_OFFSETS[:m - 1]]

    # Fixed humans: bottom-right corner, second-to-last row left edge, top near-left
    humans = [(n - 1, n - 1), (n - 2, 0), (0, 1)]

    # Fixed trees: bottom near-right, centre-right edge, top-centre
    trees = [(n - 1, n - 2), (n // 2, n - 1), (0, n // 2)]

    # Env cells (all get environmentLow; centre gets environmentRain separately)
    # Formula produces 5 cells spread across the grid; centre is excluded here.
    env_cells = [
        (1, n - 1),          # top-right area
        (n // 2, n - 1),     # middle-right edge
        (1, 1),              # top-left area
        (n - 2, n - 2),      # bottom-right area
        (n - 1, n - 1),      # bottom-right corner (same as human — cells can overlap)
    ]

    return dict(
        wetdrone=wetdrone,
        drones=drones,
        humans=humans,
        trees=trees,
        env_cells=env_cells,
    )


# ─── Problem generator ────────────────────────────────────────────────────────

def generate_problem(n: int, m: int) -> str:
    placement = place_objects(n, m)
    wetdrone_rc = placement["wetdrone"]
    drone_rcs   = placement["drones"]
    human_rcs   = placement["humans"]
    tree_rcs    = placement["trees"]
    env_rcs     = placement["env_cells"]

    wetdrone_cell = cell(*wetdrone_rc)
    drone_cells   = [cell(r, c) for r, c in drone_rcs]
    human_cells   = [cell(r, c) for r, c in human_rcs]
    tree_cells    = [cell(r, c) for r, c in tree_rcs]
    env_cell_names = [cell(r, c) for r, c in env_rcs]

    # Objects block
    grid_cells = [cell(r, c) for r in range(n) for c in range(n)]
    objects = " ".join(grid_cells) + " env rain_env"

    # ── Init facts ────────────────────────────────────────────────────────────
    init: list[str] = []

    # Drone/WetDrone type facts
    init.append(f"(WetDrone {wetdrone_cell})")
    for c in drone_cells:
        init.append(f"(Drone {c})")

    # Human and Tree type facts
    for c in human_cells:
        init.append(f"(Human {c})")
    for c in tree_cells:
        init.append(f"(Tree {c})")

    # LowVisibility environment object (and Rain object)
    init.append("(LowVisibility env)")
    init.append("(Rain rain_env)")

    # Environment role facts
    # WetDrone centre: environmentRain (demonstrates Rain ⊑ LowVisibility sub-role chain)
    init.append(f"(environmentRain {wetdrone_cell} rain_env)")
    # Other env cells: environmentLow
    for c in env_cell_names:
        init.append(f"(environmentLow {c} env)")
    # Also add base environment facts (mirrors original structure)
    init.append(f"(environment {wetdrone_cell} rain_env)")
    for c in env_cell_names:
        init.append(f"(environment {c} env)")

    # Spatial topology (both directions for symmetry)
    vc_pairs = sorted(veryclose_pairs(n))
    nd_pairs = sorted(near_diagonal_pairs(n))
    for a, b in vc_pairs:
        init.append(f"(veryClose {a} {b})")
    for a, b in nd_pairs:
        init.append(f"(near {a} {b})")

    # ── Sub-role ABox facts ───────────────────────────────────────────────────
    # Objectx = WetDrone + Drones + Humans + Trees
    objectx_set: set[str] = (
        {wetdrone_cell} | set(drone_cells) | set(human_cells) | set(tree_cells)
    )
    # MovingObject = WetDrone + Drones + Humans
    moving_set: set[str] = {wetdrone_cell} | set(drone_cells) | set(human_cells)

    # All directed adjacency edges (both directions, near + veryClose)
    all_adj = vc_pairs + nd_pairs  # already both-directional sets

    near_object_facts: set[tuple[str, str]] = set()
    near_moving_facts: set[tuple[str, str]] = set()
    very_close_object_facts: set[tuple[str, str]] = set()

    for a, b in all_adj:
        if b in objectx_set:
            near_object_facts.add((a, b))
        if b in moving_set:
            near_moving_facts.add((a, b))

    for a, b in vc_pairs:
        if b in objectx_set:
            very_close_object_facts.add((a, b))

    for a, b in sorted(near_object_facts):
        init.append(f"(nearObject {a} {b})")
    for a, b in sorted(near_moving_facts):
        init.append(f"(nearMoving {a} {b})")
    for a, b in sorted(very_close_object_facts):
        init.append(f"(veryCloseObject {a} {b})")

    init_str = "\n\t\t".join(init)

    # Goal: no two things with RiskOfPhysicalDamage that are near each other
    goal = "(not (mko (exists (?x ?y)\n\t\t\t(and\n\t\t\t\t(RiskOfPhysicalDamage ?x)\n\t\t\t\t(RiskOfPhysicalDamage ?y)\n\t\t\t\t(near ?x ?y)\n\t\t\t))))"

    return f"""\
(define (problem drone_problem)
\t(:domain drone)
\t(:objects {objects} )
\t(:init
\t\t{init_str}
\t)
\t(:goal {goal}
\t)

)"""


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out = DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    for n in range(5, 11):
        for m in range(5, 9):
            path = out / f"droneProblem{n}-{m}.pddl"
            path.write_text(generate_problem(n, m))
            print(f"wrote {path.name}")
    print(f"\nTotal: {6 * 4} instances in {out}")
