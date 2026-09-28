#!/usr/bin/env python
import argparse
import sys

from variant_options import (
    DERIVED_PREDICATE,
    INCOMPATIBLE_UPDATE,
    INCOMPATIBLE_UPDATE_PRED_TYPES,
    UPDATING_PRED_TYPES,
)

from compilation import compile_pddl
from utils.tools import load_config, require_tool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ontology")
    parser.add_argument("domain")
    parser.add_argument("problem")
    parser.add_argument("--rls", default="")
    parser.add_argument(
        "--nmo",
        default=None,
        help="Nemo binary; only used with --rls (default: tools.toml, then PATH)",
    )
    parser.add_argument(
        "--dl-lite-fragment",
        default="core",
        choices=["core", "horn"],
        help="DL-Lite fragment to use for the coherence update (default: core).",
    )
    parser.add_argument("--output-csv", default="results.csv")
    parser.add_argument("--benchmark-name", default="test 1")
    parser.add_argument(
        "--updating-pred-type", default=DERIVED_PREDICATE
    )
    parser.add_argument(
        "--incompatible-update-pred-type",
        default=INCOMPATIBLE_UPDATE,
    )
    parser.add_argument("--clipper-mqf", default=False, action="store_true")
    parser.add_argument(
        "--clipper",
        default=None,
        help="patched clipper.sh (default: tools.toml, then PATH)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="TOML file with tool paths (default: tools.toml in the repo root)",
    )
    parser.add_argument("--out-domain", "-d", default="domain.pddl")
    parser.add_argument("--out-problem", "-p", default="problem.pddl")
    parser.add_argument("--verbose", "-v", default=False, action="store_true")
    parser.add_argument("--no-filter-unimportant", default=False, action="store_true")
    parser.add_argument("--no-expensive-filtering", default=False, action="store_true")
    parser.add_argument("--debug", default=False, action="store_true")
    args = parser.parse_args()

    if args.updating_pred_type not in UPDATING_PRED_TYPES:
        print(
            "Invalid updating predicate type. Available types are: %s"
            % ", ".join(sorted(UPDATING_PRED_TYPES))
        )
        sys.exit(1)
    if args.incompatible_update_pred_type not in INCOMPATIBLE_UPDATE_PRED_TYPES:
        print(
            "Invalid incompatible update predicate type. Available types are: %s"
            % ", ".join(sorted(INCOMPATIBLE_UPDATE_PRED_TYPES))
        )
        sys.exit(1)

    try:
        config = load_config(args.config)
        clipper = require_tool("clipper", args.clipper, config)
        nmo = require_tool("nmo", args.nmo, config) if args.rls else ""
    except (FileNotFoundError, ValueError) as e:
        parser.error(str(e))

    with open(args.output_csv, "a") as f:
        f.write(args.benchmark_name + ",")

    compile_pddl(
        ontology=args.ontology,
        in_domain=args.domain,
        in_problem=args.problem,
        out_domain=args.out_domain,
        out_problem=args.out_problem,
        clipper_path=clipper,
        clipper_mqf=args.clipper_mqf,
        dl_lite_fragment=args.dl_lite_fragment,
        rls_path=args.rls,
        nmo_path=nmo,
        updating_pred_type=args.updating_pred_type,
        incompatible_update_pred_type=args.incompatible_update_pred_type,
        filter_unimportant=not args.no_filter_unimportant,
        expensive_filtering=not args.no_expensive_filtering,
        timer_output=args.output_csv,
        verbose=args.verbose,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
