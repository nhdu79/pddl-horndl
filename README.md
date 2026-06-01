## Prerequisite:

The following software is required for running `generate_pddl.py`, which generates the compiled PDDL files for the benchmarks:
- Patched version of Clipper (with `clipper.patch`)
- Nemo (required for the `core` fragment only)
- Fast Downward
- VAL Parser (optional — used for PDDL validation; compilation proceeds without it)

## Installation Instructions:
#### Clipper:
* Clone the repo:
```sh
  $ git clone https://github.com/ghxiao/clipper
```
* Copy the `clipper.patch` in this repo to the Clipper repo (above)
* Apply the patches (2 patches need to be applied):
```sh
  $ git am --keep-cr --signoff < clipper.patch
  $ git am --keep-cr --signoff < support_multiple_queries_with_the_same_body.patch
```
* Within the Clipper repo, build from source:
```sh
  $ ./build.sh
```

#### Nemo:
* For the experiment, we used Nemo version 0.6.0.
* (From [Nemo](https://github.com/knowsys/nemo) repo): The fastest way to run Nemo is to use system-specific binaries of our command-line client. Archives with pre-compiled binaries for various platforms are available from the Nemo releases page
  - Download a precompiled binary from releases: https://github.com/knowsys/nemo/releases
  - Extract `tar -xvf [your-chosen-nemo-release].tar`
* There will be a binary `nmo` file in the extracted folder; add its full path to `_NMO_CANDIDATES` in `generate_pddl.py`

#### Fast Downward:
* Detailed installation on [the official Webpage](https://www.fast-downward.org/latest/documentation/quick-start/)


## Running the compilation (`generate_pddl.py`):

#### Configuring the corresponding paths in your system:
* `generate_pddl.py` automatically detects tool paths by trying a list of known locations in order. Add your machine's paths to the relevant candidate lists near the top of the script if they are not already present:
  * `CLIPPER` — required for all runs.
  * `_NMO_CANDIDATES` — required for the `core` fragment only; `horn`-only runs work without Nemo.
  * `_PARSER_CANDIDATES` — optional; if the [VAL](https://github.com/KCL-Planning/VAL) Parser binary is not found, PDDL validation is skipped with a warning and compilation still completes.

#### Basic usage:
```sh
# Run with defaults (fragment: core, variant: var0, task: blocks)
python3 generate_pddl.py

# Choose a DL-Lite fragment
python3 generate_pddl.py --fragments horn
python3 generate_pddl.py --fragments core horn   # or --all-fragments

# Run specific variants and/or tasks
python3 generate_pddl.py --fragments horn --variants var0 var1 --tasks blocks robot

# Run the full benchmark suite
python3 generate_pddl.py --all-fragments --all-variants --all-tasks

# Show all available options
python3 generate_pddl.py --help
```

Available fragments: `core`, `horn`
Available variants: `original`, `var0`, `var1`, `var2`, `var3`
Available tasks: `blocks`, `catOG`, `drones`, `elevator`, `robot`, `robotConj`, `task`, `order`, `trip`, `tripv2`, `assembly`

> **Horn-only tasks** — `assembly`, `drones`, and `robotConj` have inputs only under `benchmarks/inputs/horn/` and must be run with `--fragments horn`. Selecting them with `--fragments core` will fail at input-file lookup.

#### Where are the written .pddl files?
* Outputs are written to `benchmarks/outputs/[fragment]/[variant]/[task]/`
  * With Tseitin transformation: `[task]_tseitin/domain_[i].pddl` and `[task]_tseitin/problem_[i].pddl`
  * Without: `[task]_no_tseitin/domain_[i].pddl` and `[task]_no_tseitin/problem_[i].pddl`

#### How do I run the planning benchmarks?
* Detailed instructions on the official Fast Downward webpage: https://www.fast-downward.org/latest/documentation/planner-usage/
    - Quick start:
    ``` shell
        fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
    ```

## The Benchmark folder:
* Input PDDL and OWL files are stored under `benchmarks/inputs/<fragment>/<task>/`, split by DL-Lite fragment (`core` or `horn`). For example, `benchmarks/inputs/horn/blocks/` holds the Horn-specific blocks inputs.
* All outputs of our pipeline are stored in `benchmarks/outputs/<fragment>/<variant>/<task>/`.

## Mapping from Benchmark names in paper to folder names:

| Paper name | Folder | Fragment |
|---|---|---|
| Cats\* | `catOG` | core + horn |
| Drones | `drones` | horn only |
| Elevator | `elevator` | core + horn |
| TPSA | `order` | core + horn |
| Robot\* | `robot` | core + horn |
| RobotConj | `robotConj` | horn only |
| VTA | `trip` | core + horn |
| VTA-Roles | `tripv2` | core + horn |
| TaskAssign | `task` | core + horn |
| Assembly | `assembly` | horn only |
