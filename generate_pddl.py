#!/usr/bin/env python3
"""Generate compiled PDDL benchmarks for all configured variants and tasks."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Allow direct imports from code/ without setting PYTHONPATH externally.
sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))
from compilation import compile_pddl  # noqa: E402
from rewriting.tseitin import tseitin_pddl  # noqa: E402
from utils.parser_wrapper import validate_pddl  # noqa: E402
from utils.timer import Timer  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# External tool paths — first existing candidate is used automatically
# ──────────────────────────────────────────────────────────────────────────────


def _resolve(name: str, candidates: list[str]) -> str:
    for path in candidates:
        if Path(path).exists():
            return path
    raise FileNotFoundError(
        f"{name} not found. Searched:\n" + "\n".join(f"  {p}" for p in candidates)
    )


CLIPPER = _resolve(
    "Clipper",
    [
        "/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh",
        "/Users/duynhu/repos/clipper/clipper-distribution/target/clipper/clipper.sh",
    ],
)


def _try_resolve(name: str, candidates: list[str]) -> Optional[str]:
    """Like _resolve, but returns None instead of raising if nothing is found."""
    try:
        return _resolve(name, candidates)
    except FileNotFoundError:
        return None


# NMO is only required for the "core" fragment; resolution is deferred to run time.
_NMO_CANDIDATES = [
    "/home/zinzin2312/repos/nemo/nmo",
    "/Users/duynhu/.appimages/nemo_v0.7.1_aarch64-apple-darwin/nmo",
]

# VAL Parser is optional; validation is skipped gracefully when not found.
_PARSER_CANDIDATES = [
    "/home/zinzin2312/repos/Val-20211204.1-Linux/bin/Parser",
]

FAST_DOWNWARD = _resolve(
    "Fast Downward",
    [
        "/home/zinzin2312/repos/downward/fast-downward.py",
        "/Users/duynhu/repos/downward/fast-downward.py",
    ],
)

# ──────────────────────────────────────────────────────────────────────────────
# Internal scripts
# ──────────────────────────────────────────────────────────────────────────────

RLS = "code/nemo/t_closure.rls"

# ──────────────────────────────────────────────────────────────────────────────
# Benchmark configuration
# ──────────────────────────────────────────────────────────────────────────────

# "ekab" is the no-update fragment (plain compilation, no coherence update).
# "core" and "horn" are update fragments that must be paired with a variant.
ALL_FRAGMENTS = ["ekab", "core", "horn"]
ALL_VARIANTS = ["var0", "var1", "var2", "var3"]
# Variants used when running the full benchmark suite (--all-fragments).
BENCHMARK_VARIANTS = ["var0", "var3"]

# ── Task groups ───────────────────────────────────────────────────────────────
# Shared across all three fragments (inputs exist in core/, ekab/, and horn/).
SHARED_TASKS = ["blocks", "catOG", "cat_2022", "elevator", "robot", "task", "order", "trip", "tripv2"]
# Available in ekab and horn, but NOT in core (no core/ inputs).
HORN_EKAB_TASKS = ["dronesv2", "robotConj", "phone_assembly"]
# Available only in ekab (no inputs in core/ or horn/).
EKAB_ONLY_TASKS = ["drones", "queens", "catImproved_2025"]

ALL_TASKS = SHARED_TASKS + HORN_EKAB_TASKS + EKAB_ONLY_TASKS

# Tasks that cannot run under "core" (no inputs in core/).
NOT_CORE_TASKS = set(HORN_EKAB_TASKS) | set(EKAB_ONLY_TASKS)


@dataclass(frozen=True)
class VariantConfig:
    updating_pred_type: str
    incompatible_update_pred_type: str


VARIANT_CONFIGS: dict[str, VariantConfig] = {
    "var0": VariantConfig("derived_predicate", "incompatible_update"),
    "var1": VariantConfig("action_effect", "compatible_update"),
    "var2": VariantConfig("derived_predicate", "compatible_update"),
    "var3": VariantConfig("action_effect", "incompatible_update"),
}

TASK_ELEMENTS: dict[str, list[str]] = {
    # ── Shared tasks ──────────────────────────────────────────────────────────
    "blocks": ["-6-2", "-10-2", "-16-1", "-13-1", "-11-0", "-7-2", "-9-0", "-5-0", "-8-0", "-7-1", "-17-0", "-14-0", "-6-0", "-16-2", "-5-1", "-15-0", "-8-1", "-14-1", "-6-1", "-5-2", "-10-1", "-15-1", "-11-1", "-4-1", "-7-0", "-8-2", "-4-2", "-12-0", "-13-0", "-4-0", "-12-1", "-10-0", "-11-2", "-9-2", "-9-1"],
    "catOG": [str(i) for i in range(6, 26)],
    "cat_2022": [str(i) for i in range(6, 26)],
    "catImproved_2025": [str(i) for i in range(6, 26)],
    "elevator": [str(i) for i in range(15, 35)],
    "robot": [str(i) for i in range(3, 23)],
    "task": [str(i) for i in range(3, 23)],
    # order, trip, tripv2 share the same element list:
    "order": ["4", "5", "6", "7", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"],
    "trip": ["4", "5", "6", "7", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"],
    "tripv2": ["4", "5", "6", "7", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"],
    # ── Horn + ekab tasks (not in core) ───────────────────────────────────────
    # 24 instances: N×N grid (N=5..10) with M drones (M=5..8).
    # Sub-role approach replaces qualified someValuesFrom with owl:Thing fillers.
    "dronesv2": [f"{n}-{m}" for n in range(5, 11) for m in range(5, 9)],
    "robotConj": [str(i) for i in range(3, 23)],
    # Mixed scenario: ceil(N/2) broken phones + floor(N/2) incomplete phones.
    # Goal = FullyEquipped for all, Repaired ∧ WarrantyClaim for warranty phones.
    "phone_assembly": ["1-0", "2-0", "3-0", "4-0", "5-0", "6-0", "7-0", "8-0", "9-0", "10-0"],
    # ── ekab-only tasks ───────────────────────────────────────────────────────
    # 24 instances: N×N grid (N=5..10) with M drones (M=5..8).
    "drones": [f"{n}-{m}" for n in range(5, 11) for m in range(5, 9)],
    # N-queens: N queens on an N×N board, K pre-placed (N=5..10, K=N-4..N).
    "queens": [f"{n}-{k}" for n in range(5, 11) for k in range(n - 4, n + 1)],
}


# ──────────────────────────────────────────────────────────────────────────────
# Path helpers
# ──────────────────────────────────────────────────────────────────────────────


def owl_path(fragment: str, task: str, element: str) -> str:
    prefix = f"benchmarks/inputs/{fragment}/{task}"
    if task == "phone_assembly":
        return f"{prefix}/assembly.owl"
    if task in ("drones", "dronesv2"):
        return f"{prefix}/TTL.owl"
    if task in ("robot", "robotConj"):
        return f"{prefix}/TTL{element}.owl"
    return f"{prefix}/blocks.owl" if task == "blocks" else f"{prefix}/TTL.owl"


def domain_path(fragment: str, task: str, element: str) -> str:
    prefix = f"benchmarks/inputs/{fragment}/{task}"
    if task in ("drones", "dronesv2"):
        return f"{prefix}/drone.pddl"
    if task in ("robot", "robotConj"):
        return f"{prefix}/robotDomain{element}.pddl"
    return f"{prefix}/domain.pddl"


def problem_path(fragment: str, task: str, element: str) -> str:
    prefix = f"benchmarks/inputs/{fragment}/{task}"
    if task == "phone_assembly":
        return f"{prefix}/probPHONE_ASSEMBLY-{element}.pddl"
    if task in ("drones", "dronesv2"):
        return f"{prefix}/droneProblem{element}.pddl"
    if task == "blocks":
        return f"{prefix}/probBLOCKS{element}.pddl"
    if task in ("robot", "robotConj"):
        return f"{prefix}/robotProblem{element}.pddl"
    if task == "queens":
        return f"{prefix}/problem{element}.pddl"
    if task in ("cat_2022", "catImproved_2025"):
        return f"{prefix}/catProblem{element}.pddl"
    return f"{prefix}/{task}Problem{element}.pddl"


def _tasks_for_fragment(fragment: str, tasks: list[str]) -> list[str]:
    """Return the subset of *tasks* that have inputs for *fragment*."""
    if fragment == "core":
        return [t for t in tasks if t not in NOT_CORE_TASKS]
    if fragment == "horn":
        return [t for t in tasks if t not in EKAB_ONLY_TASKS]
    return tasks  # ekab supports all tasks


def output_paths(
    fragment: str, variant: Optional[str], task: str, element: str
) -> tuple[str, str, str, str]:
    base = f"benchmarks/outputs/{fragment}"
    if variant:
        base += f"/{variant}"
    base += f"/{task}"
    return (
        f"{base}_no_tseitin/domain_{element}.pddl",
        f"{base}_no_tseitin/problem_{element}.pddl",
        f"{base}_tseitin/domain_{element}.pddl",
        f"{base}_tseitin/problem_{element}.pddl",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────


def compile_instance(
    fragment: str,
    variant: Optional[str],
    task: str,
    element: str,
    tseitin_mode: str = "both",
) -> None:
    owl = owl_path(fragment, task, element)
    in_domain = domain_path(fragment, task, element)
    in_problem = problem_path(fragment, task, element)
    out_domain, out_problem, ts_domain, ts_problem = output_paths(
        fragment, variant, task, element
    )

    do_tseitin = tseitin_mode in ("only", "both")

    # Ensure output directories exist; tseitin dirs only needed when tseitin runs.
    for path in (out_domain, out_problem):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    if do_tseitin:
        for path in (ts_domain, ts_problem):
            Path(path).parent.mkdir(parents=True, exist_ok=True)

    compile_kwargs: dict = dict(
        ontology=owl,
        in_domain=in_domain,
        in_problem=in_problem,
        out_domain=out_domain,
        out_problem=out_problem,
        clipper_path=CLIPPER,
    )

    if fragment != "ekab":
        config = VARIANT_CONFIGS[variant]
        if fragment == "horn":
            compile_kwargs["dl_lite_fragment"] = "horn"
        else:  # core
            nmo = _try_resolve("Nemo (nmo)", _NMO_CANDIDATES)
            if nmo is None:
                print(
                    f"Skipping [{fragment}/{variant}] {task}/{element}: "
                    "Nemo (nmo) not found. Add its path to _NMO_CANDIDATES.",
                    file=sys.stderr,
                )
                return
            compile_kwargs.update(dl_lite_fragment="core", rls_path=RLS, nmo_path=nmo)
        compile_kwargs.update(
            updating_pred_type=config.updating_pred_type,
            incompatible_update_pred_type=config.incompatible_update_pred_type,
        )

    timer_output = compile_kwargs.get("timer_output", "result.csv")
    compile_pddl(
        **compile_kwargs,
        fragment=fragment,
        variant=variant or "",
        task=task,
        element=element,
        tseitin=False,
    )

    if do_tseitin:
        with Timer(
            "tseitin",
            block=True,
            file=timer_output,
            fragment=fragment,
            variant=variant or "",
            task=task,
            element=element,
            tseitin=True,
        ):
            tseitin_pddl(
                in_domain=out_domain,
                in_problem=out_problem,
                out_domain=ts_domain,
                out_problem=ts_problem,
                keep_name=True,
            )

    val = _try_resolve("VAL Parser", _PARSER_CANDIDATES)
    if val is not None:
        if tseitin_mode in ("none", "both"):
            validate_pddl(out_domain, out_problem, val)
        if do_tseitin:
            validate_pddl(ts_domain, ts_problem, val)
    else:
        print("Skipping validation: VAL Parser not found. Add its path to _PARSER_CANDIDATES.", file=sys.stderr)


def parse_args() -> tuple[list[str], list[str], list[str], bool, str]:
    parser = argparse.ArgumentParser(
        description="Generate compiled PDDL benchmarks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"available fragments: {', '.join(ALL_FRAGMENTS)}\n"
            f"  'ekab'  compiles without coherence update (no variant required).\n"
            f"  'core' and 'horn' apply coherence update and must be paired with a variant.\n"
            f"available variants:  {', '.join(ALL_VARIANTS)}\n"
            f"  benchmark suite (--all-fragments) uses {', '.join(BENCHMARK_VARIANTS)} for core/horn.\n"
            f"task groups:\n"
            f"  shared (all fragments): {', '.join(SHARED_TASKS)}\n"
            f"  horn + ekab only:       {', '.join(HORN_EKAB_TASKS)}\n"
            f"  ekab only:              {', '.join(EKAB_ONLY_TASKS)}\n"
        ),
    )
    parser.add_argument(
        "--fragments",
        "-F",
        nargs="+",
        metavar="FRAGMENT",
        default=["ekab"],
        choices=ALL_FRAGMENTS,
        help="DL-Lite fragments to run (default: ekab)",
    )
    parser.add_argument(
        "--variants",
        "-V",
        nargs="+",
        metavar="VARIANT",
        default=["var0"],
        choices=ALL_VARIANTS,
        help="variants to run for core/horn fragments (default: var0); ignored for 'ekab'",
    )
    parser.add_argument(
        "--tasks",
        "-T",
        nargs="+",
        metavar="TASK",
        default=["blocks"],
        choices=ALL_TASKS,
        help="tasks to run (default: blocks)",
    )
    parser.add_argument(
        "--all-fragments",
        action="store_true",
        help=f"run all fragments ({', '.join(ALL_FRAGMENTS)}); "
             f"sets core/horn variants to {', '.join(BENCHMARK_VARIANTS)}",
    )
    parser.add_argument(
        "--all-variants",
        action="store_true",
        help=f"run all variants for core/horn fragments ({', '.join(ALL_VARIANTS)})",
    )
    parser.add_argument(
        "--all-tasks",
        action="store_true",
        help="run all tasks supported by each fragment",
    )
    parser.add_argument(
        "--tseitin",
        choices=["none", "only", "both"],
        default="both",
        help=(
            "which outputs to produce: 'none' = no-tseitin only, "
            "'only' = tseitin only, 'both' = both (default: both)"
        ),
    )
    args = parser.parse_args()

    fragments = ALL_FRAGMENTS if args.all_fragments else args.fragments
    # --all-fragments activates benchmark-suite mode: var0 and var3 only for core/horn.
    if args.all_fragments:
        variants = BENCHMARK_VARIANTS
    elif args.all_variants:
        variants = ALL_VARIANTS
    else:
        variants = args.variants
    tasks = ALL_TASKS if args.all_tasks else args.tasks
    # filter_tasks: when True, main() restricts each fragment to its supported tasks.
    filter_tasks = args.all_tasks
    return fragments, variants, tasks, filter_tasks, args.tseitin


def main() -> None:
    fragments, variants, tasks, filter_tasks, tseitin_mode = parse_args()
    for fragment in fragments:
        # "ekab" has no update semantics — no variant dimension applies.
        effective_variants: list[Optional[str]] = [None] if fragment == "ekab" else variants
        # When --all-tasks is active, restrict to tasks that have inputs for this fragment.
        effective_tasks = _tasks_for_fragment(fragment, tasks) if filter_tasks else tasks
        for variant in effective_variants:
            for task in effective_tasks:
                for element in TASK_ELEMENTS[task]:
                    label = f"{fragment}/{variant}" if variant else fragment
                    print(f"  [{label}] {task} / {element}")
                    compile_instance(fragment, variant, task, element, tseitin_mode=tseitin_mode)


if __name__ == "__main__":
    main()
