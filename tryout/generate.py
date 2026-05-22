#!/usr/bin/env python3
"""Generate compiled PDDL outputs for the tryout blocks instance."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))

from compiler import compile_pddl  # noqa: E402
from rewriting.new_tseitin import tseitin_pddl  # noqa: E402

# ── Tool paths ────────────────────────────────────────────────────────────────


def _resolve(name: str, candidates: list[str]) -> str:
    for path in candidates:
        if Path(path).exists():
            return path
    raise FileNotFoundError(
        f"{name} not found. Searched:\n" + "\n".join(f"  {p}" for p in candidates)
    )


def _try_resolve(name: str, candidates: list[str]) -> Optional[str]:
    try:
        return _resolve(name, candidates)
    except FileNotFoundError:
        return None


CLIPPER = _resolve(
    "Clipper",
    [
        "/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh",
        "/Users/duynhu/repos/clipper/clipper-distribution/target/clipper/clipper.sh",
    ],
)

_NMO_CANDIDATES = [
    "/home/zinzin2312/repos/nemo/nmo",
    "/Users/duynhu/.appimages/nemo_v0.7.1_aarch64-apple-darwin/nmo",
]

RLS = str(ROOT / "code/nemo/t_closure.rls")

# ── Inputs ────────────────────────────────────────────────────────────────────

TRYOUT = Path(__file__).resolve().parent
OWL = str(TRYOUT / "blocks.owl")
DOMAIN = str(TRYOUT / "domain.pddl")
PROBLEM = str(TRYOUT / "blocksProb.pddl")
TIMER = str(TRYOUT / "result.csv")

# ── Variants ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VariantConfig:
    updating_pred_type: str
    incompatible_update_pred_type: str


VARIANTS: dict[str, Optional[VariantConfig]] = {
    "original": None,
    "var0": VariantConfig("derived_predicate", "incompatible_update"),
    "var1": VariantConfig("action_effect", "compatible_update"),
    "var2": VariantConfig("derived_predicate", "compatible_update"),
    "var3": VariantConfig("action_effect", "incompatible_update"),
}

# ── Runner ────────────────────────────────────────────────────────────────────


def compile_instance(fragment: str, variant: str) -> None:
    config = VARIANTS[variant]
    out_dir = TRYOUT / fragment / variant
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_dir = TRYOUT / fragment / (variant + "_tseitin")
    ts_dir.mkdir(parents=True, exist_ok=True)

    out_domain = str(out_dir / "domain.pddl")
    out_problem = str(out_dir / "problem.pddl")
    ts_domain = str(ts_dir / "domain.pddl")
    ts_problem = str(ts_dir / "problem.pddl")

    kwargs: dict = dict(
        ontology=OWL,
        in_domain=DOMAIN,
        in_problem=PROBLEM,
        out_domain=out_domain,
        out_problem=out_problem,
        clipper_path=CLIPPER,
        clipper_mqf=True,
        timer_output=TIMER,
        verbose=True,
    )

    if config is not None:
        if fragment == "horn":
            kwargs["dl_lite_fragment"] = "horn"
        else:
            nmo = _try_resolve("Nemo (nmo)", _NMO_CANDIDATES)
            if nmo is None:
                print(
                    f"  Skipping [{fragment}/{variant}]: Nemo not found.",
                    file=sys.stderr,
                )
                return
            kwargs.update(dl_lite_fragment="core", rls_path=RLS, nmo_path=nmo)
        kwargs.update(
            updating_pred_type=config.updating_pred_type,
            incompatible_update_pred_type=config.incompatible_update_pred_type,
        )

    compile_pddl(**kwargs)
    tseitin_pddl(
        in_domain=out_domain,
        in_problem=out_problem,
        out_domain=ts_domain,
        out_problem=ts_problem,
        keep_name=True,
    )
    print(f"  → {out_dir}/  and  {ts_dir}/")


def main() -> None:
    for fragment in ("horn", "core"):
        print(f"[{fragment}/var0]")
        compile_instance(fragment, "var0")


if __name__ == "__main__":
    main()
