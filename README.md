## Prerequisite:

The following software is required for running `generate_pddl.py`, which generates the compiled PDDL files for the benchmarks:
- Patched version of Clipper (with the two patches in `patches/`)
- Nemo (required for the `core` fragment only)
- Fast Downward (for planning on the generated files)
- VAL Parser (optional — used for PDDL validation; compilation proceeds without it)

## Installation Instructions:
#### Clipper:
* Clone the repo (the patches apply to upstream `master`, commit `23153e9`):
```sh
  $ git clone https://github.com/ghxiao/clipper
  $ cd clipper
```
* Apply the two patches from this repo's `patches/` folder, in this order:
```sh
  $ git am --keep-cr --signoff < /path/to/pddl-horndl/patches/clipper.patch
  $ git am --keep-cr --signoff < /path/to/pddl-horndl/patches/support_multiple_queries_with_the_same_body.patch
```
  (`git apply <patch>` works too if you do not want the patches as commits.)
* Within the Clipper repo, build from source:
```sh
  $ ./build.sh
```

#### Nemo:
* For the experiment, we used Nemo version 0.6.0.
* (From [Nemo](https://github.com/knowsys/nemo) repo): The fastest way to run Nemo is to use system-specific binaries of our command-line client. Archives with pre-compiled binaries for various platforms are available from the Nemo releases page
  - Download a precompiled binary from releases: https://github.com/knowsys/nemo/releases
  - Extract `tar -xvf [your-chosen-nemo-release].tar`
* There will be a binary `nmo` file in the extracted folder; add its full path to `tools.toml` (see below)

#### Fast Downward:
* Detailed installation on [the official Webpage](https://www.fast-downward.org/latest/documentation/quick-start/)


## Running the compilation (`generate_pddl.py`):

#### Configuring the corresponding paths in your system:
Each external tool is looked up in this order:
1. the command-line option: `--clipper`, `--nmo`, `--val` (and `--config FILE` to use a different config file);
2. the `[tools]` table of `tools.toml` in the repo root (git-ignored; copy `tools.example.toml` to start);
3. the executable's usual name on `PATH`: `clipper.sh`, `nmo`, `Parser`.

```sh
cp tools.example.toml tools.toml   # then edit the paths
```

* `clipper` — required for all runs.
* `nmo` — required for the `core` fragment only; `horn`/`ekab` runs work without Nemo.
* `val` — optional; if the [VAL](https://github.com/KCL-Planning/VAL) Parser binary is not found, PDDL validation is skipped with a warning and compilation still completes.

The same lookup is used by `python3 -m compilation` (`--clipper`, `--nmo`, `--config`) and `code/utils/parser_wrapper.py` (`--parser`).

#### Basic usage:
```sh
# Run with defaults (fragment: ekab, variant: none, task: blocks)
python3 generate_pddl.py

# Choose a DL-Lite fragment
python3 generate_pddl.py --fragments horn
python3 generate_pddl.py --fragments ekab        # no coherence update
python3 generate_pddl.py --fragments core horn   # or --all-fragments (also includes ekab)

# Run specific variants and/or tasks
python3 generate_pddl.py --fragments horn --variants var0 var1 --tasks blocks robot

# Run the full benchmark suite
# (--all-fragments implies var0 + var3 for core/horn; --all-tasks filters tasks per fragment)
python3 generate_pddl.py --all-fragments --all-tasks

# Control which outputs are produced (default: both)
python3 generate_pddl.py --tseitin none  # no-tseitin output only
python3 generate_pddl.py --tseitin only  # tseitin output only
python3 generate_pddl.py --tseitin both  # both (default)

# Show all available options
python3 generate_pddl.py --help
```

Available fragments: `ekab`, `core`, `horn`
  (`ekab` compiles without coherence update; variants are ignored for it.)
Available variants: `var0`, `var1`, `var2`, `var3`
  (Benchmark suite uses `var0` and `var3` when `--all-fragments` is active.)

| Task group | Tasks | Fragments |
|---|---|---|
| Shared | `blocks`, `catOG`, `cat_2022`, `elevator`, `robot`, `task`, `order`, `trip`, `tripv2` | all |
| Horn + ekab | `dronesv2`, `robotConj`, `phone_assembly` | horn, ekab |
| ekab only | `drones`, `queens`, `catImproved_2025` | ekab |

> **Task–fragment compatibility** — `--all-tasks` automatically restricts each fragment to its supported tasks. Explicitly passing unsupported tasks (e.g. `--fragments core --tasks drones`) will fail at input-file lookup.

#### Where are the written .pddl files?
* Outputs are written to:
  * `benchmarks/outputs/[fragment]/[variant]/[task]/` for `core` and `horn` fragments
  * `benchmarks/outputs/ekab/[task]/` for the `ekab` fragment (no variant subfolder)
  * With Tseitin transformation: `[task]_tseitin/domain_[i].pddl` and `[task]_tseitin/problem_[i].pddl`
  * Without: `[task]_no_tseitin/domain_[i].pddl` and `[task]_no_tseitin/problem_[i].pddl`
* The `--tseitin` flag controls which of the above are produced (`none`, `only`, `both`; default `both`).

#### How do I run the planning benchmarks?
* Detailed instructions on the official Fast Downward webpage: https://www.fast-downward.org/latest/documentation/planner-usage/
    - Quick start:
    ``` shell
        fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
    ```

## The Benchmark folder:
* Input PDDL and OWL files are stored under `benchmarks/inputs/<fragment>/<task>/`, one directory per fragment (`core`, `ekab`, `horn`). For example, `benchmarks/inputs/horn/blocks/` holds the Horn-specific blocks inputs.
* Outputs are stored in `benchmarks/outputs/<fragment>/<variant>/<task>/` for `core`/`horn`, and `benchmarks/outputs/ekab/<task>/` for `ekab`.

#### Notes on input/output PDDL
* Typed input domains are supported: `:types`, typed parameters and domain `:constants` are kept as declared. Untyped input stays untyped (no implicit `object` type is added).
* Variables quantified *inside* an `mko` query must be untyped (Clipper has no notion of PDDL types); model the type as an ontology concept instead.
* Problem `:objects` are moved into the domain's `:constants` (the compiled derived predicates may mention them), next to any constants the input domain already declares.
* The output `:requirements` are inferred from the compiled domain (e.g. `:derived-predicates`, `:negative-preconditions`, `:conditional-effects`).
* Compilation is deterministic: the same inputs always produce byte-identical outputs.
* Names are matched case-insensitively: `onBlock` in the PDDL files and `OnBlock` in the OWL file are the same predicate. Internally every name is lowercased and stripped of `_`/`-` (`onblock`), which is also how Clipper writes its Datalog output. Because that would silently merge spellings like `on_block` and `onBlock`, such mixes are rejected (see below): use one spelling per name, up to letter case.
* Clipper itself is case-sensitive when *reading* names: a query atom must be spelled exactly like the OWL name, or Clipper silently drops it. The compiler takes care of this: it sends query atoms in their exact OWL spelling and declares PDDL-only query predicates to Clipper. Note that Clipper's `-name` option (e.g. `-name FRAGMENT` to keep case) has no effect, due to an upstream bug; the compiler relies on the default lowercase output anyway.
* Before compiling, the compiler checks names and stops with a `NameClashError` if:
  * different spellings of the same name are mixed (e.g. declaring `onBlock` but using `on_block`);
  * two OWL names differ only in letter case (e.g. `Block` and `block`), which PDDL cannot tell apart;
  * an OWL name contains characters other than letters, digits, `_` and `-` (e.g. `.`);
  * a name is reserved: `inconsistent`, `nothing`, `query<N>`, `updating`, `exists<role>`/`existsinv<role>` (horn), and the action name `update`.
* `mko` queries may mix ontology predicates with PDDL-only predicates.

## Mapping from Benchmark names in paper to folder names:

| Paper name | Folder | Fragment |
|---|---|---|
| Cats\* | `catOG` | all |
| Cats 2022 | `cat_2022` | all |
| Cats Improved 2025 | `catImproved_2025` | ekab only |
| Drones | `drones` | ekab only |
| DronesV2 | `dronesv2` | horn + ekab |
| Elevator | `elevator` | all |
| N-Queens | `queens` | ekab only |
| TPSA | `order` | all |
| Robot\* | `robot` | all |
| RobotConj | `robotConj` | horn + ekab |
| VTA | `trip` | all |
| VTA-Roles | `tripv2` | all |
| TaskAssign | `task` | all |
| Assembly | `phone_assembly` | horn + ekab |

### DronesV2 benchmark

`dronesv2` is a Horn DL-Lite rewrite of the `drones` benchmark. The original `drones` ontology (`benchmarks/inputs/ekab/drones/TTL.owl`) is unsupported by the parser (`is_supported=False`) because it uses `owl:someValuesFrom` with non-`owl:Thing` fillers and `owl:SymmetricProperty`. Since the `ekab` fragment does not invoke the coherence-update pipeline, `drones` can still be compiled under `ekab`. `dronesv2` fixes both issues for `horn`/`core` using **sub-role splitting** (Option A):

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
