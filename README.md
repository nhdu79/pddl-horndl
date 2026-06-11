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
python3 generate_pddl.py --fragments original     # no coherence update
python3 generate_pddl.py --fragments core horn   # or --all-fragments (also includes original)

# Run specific variants and/or tasks
python3 generate_pddl.py --fragments horn --variants var0 var1 --tasks blocks robot

# Run the full benchmark suite
python3 generate_pddl.py --all-fragments --all-variants --all-tasks

# Show all available options
python3 generate_pddl.py --help
```

Available fragments: `original`, `core`, `horn`
  (`original` compiles without coherence update and shares inputs with `core`; variants are ignored for it.)
Available variants: `var0`, `var1`, `var2`, `var3`
Available tasks: `blocks`, `catOG`, `elevator`, `dronesv2`, `robot`, `robotConj`, `task`, `order`, `trip`, `tripv2`, `phone_assembly`

> **Horn-only tasks** — `phone_assembly`, `dronesv2`, and `robotConj` have inputs only under `benchmarks/inputs/horn/` and must be run with `--fragments horn`. Selecting them with `--fragments core` or `--fragments original` will fail at input-file lookup.

#### Where are the written .pddl files?
* Outputs are written to:
  * `benchmarks/outputs/[fragment]/[variant]/[task]/` for `core` and `horn` fragments
  * `benchmarks/outputs/original/[task]/` for the `original` fragment (no variant subfolder)
  * With Tseitin transformation: `[task]_tseitin/domain_[i].pddl` and `[task]_tseitin/problem_[i].pddl`
  * Without: `[task]_no_tseitin/domain_[i].pddl` and `[task]_no_tseitin/problem_[i].pddl`

#### How do I run the planning benchmarks?
* Detailed instructions on the official Fast Downward webpage: https://www.fast-downward.org/latest/documentation/planner-usage/
    - Quick start:
    ``` shell
        fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
    ```

## The Benchmark folder:
* Input PDDL and OWL files are stored under `benchmarks/inputs/<fragment>/<task>/`, split by DL-Lite fragment (`core` or `horn`). The `original` fragment reuses `core` inputs. For example, `benchmarks/inputs/horn/blocks/` holds the Horn-specific blocks inputs.
* Outputs are stored in `benchmarks/outputs/<fragment>/<variant>/<task>/` for `core`/`horn`, and `benchmarks/outputs/original/<task>/` for `original`.

## Mapping from Benchmark names in paper to folder names:

| Paper name | Folder | Fragment |
|---|---|---|
| Cats\* | `catOG` | core + horn |
| DronesV2 | `dronesv2` | horn only |
| Elevator | `elevator` | core + horn |
| TPSA | `order` | core + horn |
| Robot\* | `robot` | core + horn |
| RobotConj | `robotConj` | horn only |
| VTA | `trip` | core + horn |
| VTA-Roles | `tripv2` | core + horn |
| TaskAssign | `task` | core + horn |
| Assembly | `phone_assembly` | horn only |

### DronesV2 benchmark

`dronesv2` is a Horn DL-Lite rewrite of the `drones` benchmark. The original `drones` ontology (`benchmarks/inputs/etc/drones/TTL.owl`) is unsupported by the parser (`is_supported=False`) because it uses `owl:someValuesFrom` with non-`owl:Thing` fillers and `owl:SymmetricProperty`. `dronesv2` fixes both issues using **sub-role splitting** (Option A):

| Original qualified restriction | Replacement sub-role | Sub-role inclusion |
|---|---|---|
| `∃environment.LowVisibility` | `∃environmentLow.⊤` | `environmentLow ⊑ environment` |
| `∃environment.Rain` | `∃environmentRain.⊤` | `environmentRain ⊑ environmentLow` |
| `∃near.Objectx` | `∃nearObject.⊤` | `nearObject ⊑ near` |
| `∃near.MovingObject` | `∃nearMoving.⊤` | `nearMoving ⊑ near` |
| `∃veryClose.Objectx` | `∃veryCloseObject.⊤` | `veryCloseObject ⊑ veryClose` |

The three risk axioms become:
```
Drone ⊓ ∃environmentLow.⊤ ⊓ ∃nearObject.⊤  ⊑  RiskOfPhysicalDamage
Drone ⊓ ∃nearMoving.⊤                        ⊑  RiskOfPhysicalDamage
Drone ⊓ ∃veryCloseObject.⊤                   ⊑  RiskOfPhysicalDamage
```

The `Move` action in `drone.pddl` maintains the sub-role ABox facts (`nearObject`, `nearMoving`, `veryCloseObject`) via universally quantified conditional effects whenever a drone vacates or occupies a cell. Environment facts (`environmentLow`, `environmentRain`) are static cell properties set in the problem init.

Instances are generated by `generators/hornDroneGenerator.py` (24 instances: N×N grid for N=5..10, M=5..8 drones). To regenerate:
```sh
python3 generators/hornDroneGenerator.py
```
