# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

This is a research tool that compiles PDDL planning tasks enriched with OWL ontologies (Horn-DL / EL family) into standard PDDL via query rewriting. The pipeline:

1. **UCQ collection** – scans PDDL domain/problem for `MinimalKnowledgeOperator` nodes and extracts union-of-conjunctive-queries (UCQs).
2. **Ontology rewriting** – calls the external tool **Clipper** (patched) to rewrite the OWL ontology + UCQs into Datalog rules.
3. **Coherence update** (optional) – uses **Nemo** (Datalog engine) with `code/nemo/t_closure.rls` to compute a transitive closure and generate PDDL update rules; activated when `--rls` and `--nmo` are supplied.
4. **Compilation** – Datalog rules are turned into PDDL derived predicates and injected into the output domain/problem.
5. **Tseitin transformation** (optional, separate step) – flattens complex PDDL conditions into auxiliary derived predicates to satisfy planner restrictions.

Output PDDL is then run through **Fast Downward**.

## External dependencies

Three external tools must be installed and their paths configured in `generate_pddl.sh` before running benchmarks:

| Tool | Variable | Notes |
|------|----------|-------|
| Clipper (patched) | `clipper` | Apply both patches in `patches/` before building |
| Nemo binary (`nmo`) | `nmo` | v0.6.0 used in experiments |
| Fast Downward | `fastdownward` | Standard installation |
| VAL Parser | `parser` | Used only for PDDL validation step |

## Running the compilation pipeline

```bash
# Full benchmark generation (edit variants/tasks arrays in script first)
bash generate_pddl.sh

# Single test case (edit test.sh variables: task, semantics, i, update)
bash test.sh

# Manual single compilation — eKAB semantics (no coherence update)
PYTHONPATH=code python3 code/compiler.py <ontology.owl> <domain.pddl> <problem.pddl> \
  -d out_domain.pddl -p out_problem.pddl \
  --clipper /path/to/clipper.sh --clipper-mqf

# With coherence update (eKAB + update semantics)
PYTHONPATH=code python3 code/compiler.py <ontology.owl> <domain.pddl> <problem.pddl> \
  -d out_domain.pddl -p out_problem.pddl \
  --clipper /path/to/clipper.sh --clipper-mqf \
  --rls code/nemo/t_closure.rls --nmo /path/to/nmo \
  --updating-pred-type derived_predicate \
  --incompatible-update-pred-type incompatible_update

# Tseitin transformation (post-compilation step)
PYTHONPATH=code python3 code/rewriting/new_tseitin.py <domain.pddl> <problem.pddl> \
  -d tseitin_domain.pddl -p tseitin_problem.pddl --keep-name

# Fast Downward planning
fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
```

Always set `PYTHONPATH=code` when running any script under `code/`.

## Compilation variants

`generate_pddl.sh` iterates over four variants (var0–var3) which are combinations of two axes:

- `--updating-pred-type`: `derived_predicate` (var0, var2) or `action_effect` (var1, var3)
- `--incompatible-update-pred-type`: `incompatible_update` (var0, var3) or `compatible_update` (var1, var2)

Output goes to `benchmarks/outputs/<variant>/<task>_no_tseitin/` and `<task>_tseitin/`.

## Code architecture

```
code/
├── compiler.py              # Entry point; orchestrates the full pipeline via Compiler class
├── update_runner.py         # UpdateRunner: calls Nemo, builds update Datalog rules; Timer utility
├── planning/
│   ├── pddl.py              # PDDL parser + AST nodes (Domain, Problem, actions, derived predicates, logic)
│   ├── domain.py            # Domain class (adjust_actions, construct_update_action)
│   ├── problem.py           # Problem class (extend_for_coherence_update)
│   ├── logic.py             # Logic AST: And, Or, Not, Forall, Exists, Fact, Comparison, etc.
│   └── datalog.py           # Datalog AST: Rule, Atom, Negated, Equality; parse_rule()
├── compilation/
│   ├── compiler.py          # (see code/compiler.py above — main file)
│   ├── ucq_collector.py     # UCQCollector: walks PDDL AST, extracts UCQs, replaces with primed query facts
│   ├── utils.py             # Predicate naming conventions (prime_, query_, is_update_, etc.)
│   └── variant_options.py   # UPDATING_PREDICATE_TYPES / INCOMPATIBLE_UPDATE_PREDICATE_TYPES dicts
├── rewriting/
│   ├── clipper.py           # Clipper wrapper: calls clipper.sh subprocess, parses Datalog output
│   ├── new_tseitin.py       # Tseitin class: flattens complex conditions into auxiliary derived predicates
│   └── tseitin.py           # (older version, superseded by new_tseitin.py)
├── coherence_update/
│   ├── update.py            # CohrenceUpdate: builds all 14 inclusion-type update rules from TBox
│   ├── classes/             # TBox, inclusion types, OWL parsing
│   └── rules/               # Rule builders: atomic, positive, negative inclusions
├── nemo/
│   ├── t_closure.rls        # Nemo Datalog rules for transitive closure computation
│   └── fact_counter.rls
└── utils/
    ├── functions.py         # parse_name, read_predicates, get_repr helpers
    └── parser_wrapper.py    # Thin wrapper calling VAL Parser for PDDL validation
```

### Key naming conventions in the codebase

- **Primed predicates** (`prime_predicate_name`): ontology-derived predicates get a prime suffix; they represent the "derived" version that is inferred, while the unprimed name is the planning-visible predicate.
- **Query predicates** (`QUERY_N`): each UCQ extracted from the PDDL gets a fresh `QUERY_<index>` name; these become derived predicates in the output domain.
- **Coherence update predicates**: `incompatible_update` / `compatible_update` — special predicates added to the domain during update extension; detected via `is_coherence_update_predicate_name()`.

## Benchmark inputs

```
benchmarks/inputs/
├── robot/        # Per-instance TTL<i>.owl + robotDomain<i>.pddl (robot has per-instance ontologies)
├── catOG/        # Single TTL.owl + per-instance problem files
├── elevator/
├── order/        # TPSA benchmark
├── trip/         # VTA benchmark
├── tripv2/       # VTA-Roles benchmark
├── task/         # TaskAssign benchmark
└── blocks/       # blocks.owl + per-instance probBLOCKS<suffix>.pddl
```

Paper name → folder: Cats\* → catOG, Robot\* → robot, TPSA → order, VTA → trip, VTA-Roles → tripv2, TaskAssign → task.

## Tests

There is no automated test suite. The `test/` directory contains hand-crafted PDDL + OWL files for manual spot-checks. Run via `bash test.sh` (edit variables at the top of the script to select the scenario).

## Python environment

The project uses a `.venv` at the repo root (Python 3.12 confirmed in `__pycache__`). Activate with:
```bash
source .venv/bin/activate
```
No `requirements.txt` or `pyproject.toml` is present; dependencies appear to be stdlib only (the code calls external tools as subprocesses).
