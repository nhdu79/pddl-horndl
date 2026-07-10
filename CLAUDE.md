# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

This is a research tool that compiles PDDL planning tasks enriched with OWL ontologies (Horn-DL / EL family) into standard PDDL via query rewriting. The pipeline:

1. **UCQ collection** – scans PDDL domain/problem for `MinimalKnowledgeOperator` nodes and extracts union-of-conjunctive-queries (UCQs).
2. **Ontology rewriting** – calls the external tool **Clipper** (patched) to rewrite the OWL ontology + UCQs into Datalog rules.
3. **Coherence update** (optional) – for the `core` fragment, uses **Nemo** (Datalog engine) with `code/nemo/t_closure.rls`; for the `horn` fragment, uses the Python OWL parser directly. Activated by `--dl-lite-fragment`.
4. **Compilation** – Datalog rules are turned into PDDL derived predicates and injected into the output domain/problem.
5. **Tseitin transformation** (optional, separate step) – flattens complex PDDL conditions into auxiliary derived predicates to satisfy planner restrictions.

Output PDDL is then run through **Fast Downward**.

## External dependencies

External tools are auto-detected from candidate path lists near the top of `generate_pddl.py`. Add your machine's paths to the relevant list if not already present:

| Tool | Candidate list | Notes |
|------|----------------|-------|
| Clipper (patched) | `CLIPPER` | Apply both patches in `patches/` before building; required for all runs |
| Nemo binary (`nmo`) | `_NMO_CANDIDATES` | v0.6.0 used in experiments; required for `core` fragment only |
| Fast Downward | `FAST_DOWNWARD` | Standard installation |
| VAL Parser | `_PARSER_CANDIDATES` | Optional — PDDL validation; skipped gracefully when not found |

Python dependency: **rdflib** (used by `code/owl/` for OWL Turtle parsing). Install into the `.venv` with `pip install rdflib`.

## Running the compilation pipeline

```bash
# Full benchmark generation — defaults to fragment=ekab, task=blocks
python3 generate_pddl.py

# Select fragments, variants, and tasks explicitly
python3 generate_pddl.py --fragments horn --variants var0 var1 --tasks blocks robot

# Run the full benchmark suite
# (--all-fragments implies var0+var3 for core/horn; --all-tasks filters tasks per fragment)
python3 generate_pddl.py --all-fragments --all-tasks

# Control Tseitin output (default: both)
python3 generate_pddl.py --tseitin none   # no-tseitin output only
python3 generate_pddl.py --tseitin only   # tseitin output only
python3 generate_pddl.py --tseitin both   # both (default)

# Single test case (edit test.sh variables: task, semantics, i, update)
bash test.sh

# Manual single compilation — no coherence update (ekab semantics)
PYTHONPATH=code python3 -m compilation <ontology.owl> <domain.pddl> <problem.pddl> \
  -d out_domain.pddl -p out_problem.pddl \
  --clipper /path/to/clipper.sh --clipper-mqf

# With coherence update — core fragment (uses Nemo)
PYTHONPATH=code python3 -m compilation <ontology.owl> <domain.pddl> <problem.pddl> \
  -d out_domain.pddl -p out_problem.pddl \
  --clipper /path/to/clipper.sh --clipper-mqf \
  --dl-lite-fragment core \
  --rls code/nemo/t_closure.rls --nmo /path/to/nmo \
  --updating-pred-type derived_predicate \
  --incompatible-update-pred-type incompatible_update

# With coherence update — horn fragment (uses Python OWL parser, no Nemo needed)
PYTHONPATH=code python3 -m compilation <ontology.owl> <domain.pddl> <problem.pddl> \
  -d out_domain.pddl -p out_problem.pddl \
  --clipper /path/to/clipper.sh --clipper-mqf \
  --dl-lite-fragment horn \
  --updating-pred-type derived_predicate \
  --incompatible-update-pred-type incompatible_update

# Tseitin transformation (post-compilation step)
PYTHONPATH=code python3 code/rewriting/new_tseitin.py <domain.pddl> <problem.pddl> \
  -d tseitin_domain.pddl -p tseitin_problem.pddl --keep-name

# Fast Downward planning
fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
```

Set `PYTHONPATH=code` when calling scripts under `code/` directly. `generate_pddl.py` sets this automatically.

## Compilation variants

`generate_pddl.py` supports four update variants (`var0`–`var3`) for `core` and `horn`, plus the no-update `ekab` fragment. The four update variants are combinations of two axes:

- `--updating-pred-type`: `derived_predicate` (var0, var2) or `action_effect` (var1, var3)
- `--incompatible-update-pred-type`: `incompatible_update` (var0, var3) or `compatible_update` (var1, var2)

`ekab` runs without coherence update (no `--dl-lite-fragment` flag passed to the compiler).

`BENCHMARK_VARIANTS = ["var0", "var3"]` — the subset used when `--all-fragments` is active.

Output goes to `benchmarks/outputs/<fragment>/<variant>/<task>_no_tseitin/` and `<task>_tseitin/` for `core`/`horn`, and `benchmarks/outputs/ekab/<task>_no_tseitin/` for `ekab`. The `--tseitin {none,only,both}` flag controls which of the two output variants are produced (default: `both`).

## Code architecture

```
code/
├── planning/
│   ├── pddl.py              # PDDL parser + AST nodes (Domain, Problem, actions, derived predicates, logic)
│   ├── domain.py            # Domain class (adjust_actions, construct_update_action)
│   ├── problem.py           # Problem class (extend_for_coherence_update)
│   ├── logic.py             # Logic AST: And, Or, Not, Forall, Exists, Fact, Comparison, etc.
│   └── datalog.py           # Datalog AST: Rule, Atom, Negated, Equality; parse_rule()
├── compilation/             # Full compilation pipeline (entry point: python3 -m compilation)
│   ├── __init__.py          # compile_pddl() public function
│   ├── __main__.py          # CLI entry point
│   ├── pipeline.py          # Compiler class (full pipeline)
│   ├── datalog.py           # Datalog rule parsing, deduplication, and filtering helpers
│   ├── ontology.py          # construct_ontology_for_clipper() — extends OWL for Horn fragment
│   ├── ucq_collector.py     # UCQCollector: walks PDDL AST, extracts UCQs, replaces with primed query facts
│   ├── query_rewriter.py    # Query rewriting utilities
│   ├── utils.py             # Predicate naming conventions (prime_, query_, is_update_, etc.)
│   └── variant_options.py   # UPDATING_PREDICATE_TYPES / INCOMPATIBLE_UPDATE_PREDICATE_TYPES dicts
├── rewriting/
│   ├── clipper.py           # Clipper wrapper: calls clipper.sh subprocess, parses Datalog output
│   ├── new_tseitin.py       # tseitin_pddl() public function + Tseitin class
│   └── tseitin.py           # (older version, superseded by new_tseitin.py)
├── owl/                     # OWL ontology parsing package (backed by rdflib)
│   ├── __init__.py          # Re-exports the full public API from all submodules
│   ├── expressions.py       # Concept/role expression dataclasses: AtomicConcept,
│   │                        #   ExistentialConcept, InverseExistentialConcept, NegatedConcept,
│   │                        #   IntersectionConcept, AtomicRole, InverseRole, NegatedRole
│   ├── axioms.py            # Axiom dataclasses (ConceptInclusion, RoleInclusion,
│   │                        #   FunctionalRole, InverseFunctionalRole), Ontology container,
│   │                        #   and DL notation rendering (_dl_concept/_dl_role/_dl_axiom)
│   ├── parser.py            # _OWLBuilder + parse_owl(); unsupported-construct detection
│   └── saturation.py        # saturate_role_inclusions(): derives ∃R⊑∃P, ∃R⁻⊑∃P⁻, R⁻⊑P⁻
│                            #   from every R⊑P in the TBox (one-pass, in-place)
├── coherence_update/
│   ├── __init__.py          # Re-exports Timer, UpdateRunner, CoreUpdateRunner, HornUpdateRunner,
│   │                        #   make_update_runner, transform_incompatible_update
│   ├── timer.py             # Timer context manager (used across compilation and rewriting)
│   ├── transform.py         # transform_incompatible_update(), ensure_pddl_parameter()
│   ├── update.py            # CoherenceUpdate: builds inclusion-type update rules from TBox
│   ├── prioritized_update.py# Horn DL-Lite prioritized update builder (build_rules_for_pus)
│   ├── runners/             # UpdateRunner classes
│   │   ├── __init__.py      # make_update_runner() factory + re-exports
│   │   ├── base.py          # UpdateRunner ABC
│   │   ├── core.py          # CoreUpdateRunner — calls Nemo for DL-Lite Core TBox closure; filter_non_reachable_predicates
│   │   └── horn.py          # HornUpdateRunner — builds rules from OWL directly; filter_non_reachable_predicates
│   ├── classes/
│   │   ├── inclusion.py     # Inclusion dataclass + INCLUSION_TYPES_ORDER
│   │   └── tbox.py          # TBox class
│   └── rules/
│       ├── symbols.py       # Shared Datalog string constants (A_OR_AP_CL, AP_CL, DEL_CL, …)
│       ├── core/            # Original (non-Horn) rule builders
│       │   ├── atomic.py    # Rules for atomic concept/role deletions and incompatibility
│       │   ├── positive.py  # Rules for positive inclusions
│       │   └── negative.py  # Rules for negative inclusions
│       └── horn/            # Horn DL-Lite rule builders (stratified Datalog⁻ program R_T)
│           └── strata.py    # All 22 rules across three strata (see below)
├── nemo/
│   ├── t_closure.rls        # Nemo Datalog rules for transitive closure computation
│   └── fact_counter.rls
└── utils/
    ├── functions.py         # parse_name, read_predicates, get_repr helpers
    ├── parser_wrapper.py    # validate_pddl() — calls VAL Parser for PDDL validation
    └── pretty_print_condition.py
```

### Key naming conventions in the codebase

- **Primed predicates** (`prime_predicate_name`): ontology-derived predicates get a prime suffix; they represent the "derived" version that is inferred, while the unprimed name is the planning-visible predicate.
- **Query predicates** (`QUERY_N`): each UCQ extracted from the PDDL gets a fresh `QUERY_<index>` name; these become derived predicates in the output domain.
- **Coherence update predicates**: `incompatible_update` / `compatible_update` — special predicates added to the domain during update extension; detected via `is_coherence_update_predicate_name()`.

## OWL package (`code/owl/`)

Parses OWL Turtle files into a Python object model that mirrors the `sub`-predicate form used by `code/nemo/t_closure.rls`.

### Public API (import from `owl` or any submodule)

```python
from owl import parse_owl, saturate_role_inclusions, Ontology
from owl import AtomicConcept, ExistentialConcept, InverseExistentialConcept
from owl import NegatedConcept, IntersectionConcept, OWL_THING
from owl import AtomicRole, InverseRole, NegatedRole
from owl import ConceptInclusion, RoleInclusion, FunctionalRole, InverseFunctionalRole
```

### `parse_owl(path) -> Ontology`

Parses an OWL Turtle file. Returns an `Ontology` with:
- `.concepts` / `.roles` — dicts of all registered expression objects keyed by `.id`
- `.axioms` — list of `ConceptInclusion | RoleInclusion | FunctionalRole | InverseFunctionalRole`
- `.warnings` — list of strings describing OWL constructs outside the supported fragment
- `.is_supported` — `True` iff `warnings` is empty
- `.print_ontology()` — prints axioms in DL notation (e.g. `∃ontable ⊑ ∃on`)

Unsupported constructs (e.g. `owl:TransitiveProperty`, `owl:equivalentClass`, qualified restrictions) are recorded as warnings rather than raising exceptions. The axiom involving the unsupported construct is silently dropped; all other axioms are still parsed.

### `saturate_role_inclusions(ontology) -> None`

Extends `ontology.axioms` in-place by applying three structural rules from `t_closure.rls` to every `RoleInclusion` R ⊑ P:

```
R ⊑ P  →  ∃R ⊑ ∃P      (domain propagation)
R ⊑ P  →  ∃R⁻ ⊑ ∃P⁻   (range propagation)
R ⊑ P  →  R⁻ ⊑ P⁻      (inverse closure)
```

Works for any combination of `AtomicRole` and `InverseRole` on either side.
A single pass over the original axioms is sufficient.

## Horn DL-Lite coherence update (`code/coherence_update/rules/horn/strata.py`)

Implements the stratified Datalog⁻ program **R_T** described in the paper (AAAI27), which computes the prioritized update of an ABox under a Horn DL-Lite TBox.

The program has three strata; each stratum has concept and role variants (unary/binary predicates respectively).

### Symbol mapping

| Paper symbol | Code constant | Meaning |
|---|---|---|
| `Ap_X` | `ins_X_request` | insertion request for X |
| `Am_X` | `del_X_request` | deletion request for X |
| `AOrApCl_X` | `AOrApCl_X` | X holds or is being inserted (closure) |
| `ApCl_X` | `ApCl_X` | X is being inserted (closure) |
| `DelCl_X` | `DelCl_X` | X should be deleted (closure) |
| `PreInsCl_τ` | `PreInsCl_τ` | pre-insertion closure for axiom τ |
| `InsCl_X` | `InsCl_X` | X should be inserted (closure) |
| `ins_X` | `ins_X` | actual insertion of X |
| `del_X` | `del_X` | actual deletion of X |
| `min_Xi_in_τ` | `Min_Xi_in_axiom_id` | least-preferred deletable conjunct |

### Stratum 1 — Propagation closure

| Rule | Function |
|---|---|
| 1–2: `AOrApCl_X(Ȳ) ← X(Ȳ)` / `ApCl_X(Ȳ) ← Ap_X(Ȳ)` | `build_trigger_rules_for_propagation_concepts/roles` |
| 3: propagate `ApCl`/`AOrApCl` along role to its inverse and existential | `build_connective_rules_for_propagation_role` |
| 4: `pred_X(Ȳ) ← pred_X1(Ȳ) ∧ …` for `pred ∈ {ApCl, AOrApCl}` | `build_propagation_rules_for_concept/role` |

### Stratum 2 — Deletion closure

| Rule | Function |
|---|---|
| 5: `DelCl_X(Ȳ) ← Am_X(Ȳ)` | `build_trigger_rules_for_deletion_concepts/roles` |
| 6–7: propagate `DelCl` along role inverse and existential | `build_connnective_rules_for_deletion_role` |
| 8–9: functional role conflict detection | `build_rules_for_functional_roles` |
| 10–12: negative role inclusion conflicts | `build_deletion_rules_for_negative_role_inclusion` |
| 13–14: `Min` predicate + `DelCl` for conjunctive LHS | `build_min_and_deletion_rules_for_conjunction_concept/role` |
| 15: `incompatible()` for conjunctive conflicts | `build_incompatibility_rule_for_conjunction_concept/role` |
| 16: `incompatible()` for direct deletion/insertion clash | `build_incompatibility_rules_for_direct_deletion_concepts/roles` |
| 17: `del_X(Ȳ) ← X(Ȳ) ∧ DelCl_X(Ȳ)` | `build_actual_deletion_rules_for_concepts/roles` |

### Stratum 3 — Insertion closure

| Rule | Function |
|---|---|
| 18: `preInsCl_τ(Ȳ) ← AOrApCl_X1(Ȳ) ∧ … ∧ ¬DelCl_X(Ȳ)` | `build_pre_insertion_rules_for_conjunction_concept/role` |
| 19: `insCl_X(Ȳ) ← DelCl_Xi(Ȳ) ∧ preInsCl_τ(Ȳ)` | `build_insertion_closure_rules_for_conjunction_concept/role` |
| 20: `insCl_∃R(X) ← DelCl_R(X,Y) ∧ AOrApCl_R(X,Y) ∧ ¬DelCl_∃R(X)` | `build_insertion_closure_rule_for_existential` |
| 21–22: `ins_X(Ȳ) ← ¬X(Ȳ) ∧ insCl_X(Ȳ)` / `← ¬X(Ȳ) ∧ Ap_X(Ȳ)` | `build_actual_insertion_rules_for_concepts/roles` |

**Note on rule 14**: when `k=1` (single sub-concept/role), the `Min` predicate is unnecessary and the rule reduces directly to `DelCl_X1(Ȳ) ← DelCl_X(Ȳ) ∧ AOrApCl_X1(Ȳ)`. This special case is handled automatically.

## Benchmark inputs

Each fragment has its own input directory. Task availability per fragment:

```
benchmarks/inputs/
├── core/               # Shared tasks only
│   ├── blocks/         # blocks.owl + probBLOCKS<suffix>.pddl
│   ├── catOG/          # TTL.owl + catOGProblem<i>.pddl
│   ├── cat_2022/       # TTL.owl + catProblem<i>.pddl
│   ├── elevator/
│   ├── order/          # TPSA benchmark
│   ├── robot/          # Per-instance TTL<i>.owl + robotDomain<i>.pddl
│   ├── task/           # TaskAssign benchmark
│   ├── trip/           # VTA benchmark
│   └── tripv2/         # VTA-Roles benchmark
├── ekab/               # All tasks (shared + horn+ekab + ekab-only)
│   ├── blocks/         #   ┐
│   ├── catOG/          #   │ shared with core and horn
│   ├── cat_2022/       #   │
│   ├── elevator/       #   │
│   ├── order/          #   │
│   ├── robot/          #   │
│   ├── task/           #   │
│   ├── trip/           #   │
│   ├── tripv2/         #   ┘
│   ├── dronesv2/       #   ┐ shared with horn (not core)
│   ├── robotConj/      #   │
│   ├── phone_assembly/ #   ┘
│   ├── drones/         #   ┐ ekab-only; TTL.owl uses unsupported OWL constructs
│   ├── queens/         #   │ (parse_owl() sets is_supported=False for drones)
│   └── catImproved_2025/ # ┘ ekab-only; ontology uses owl:unionOf (unsupported by core/horn)
└── horn/               # Shared tasks + horn+ekab tasks
    ├── blocks/         #   ┐
    ├── catOG/          #   │ shared with core and ekab
    ├── cat_2022/       #   │
    ├── elevator/       #   │
    ├── order/          #   │
    ├── robot/          #   │
    ├── task/           #   │
    ├── trip/           #   │
    ├── tripv2/         #   ┘
    ├── dronesv2/       #   ┐ shared with ekab (not core)
    ├── robotConj/      #   │
    └── phone_assembly/ #   ┘
```

Paper name → folder: Cats\* → catOG, Cats 2022 → cat_2022, Cats Improved 2025 → catImproved_2025 (ekab only), Robot\* → robot, TPSA → order, VTA → trip, VTA-Roles → tripv2, TaskAssign → task.

## Tests

There is no automated test suite. The `test/` directory contains hand-crafted PDDL + OWL files for manual spot-checks. Run via `bash test.sh` (edit variables at the top of the script to select the scenario).

`code/test_parser.py` is a standalone script for manually inspecting the OWL parser output:
```bash
PYTHONPATH=code python3 code/test_parser.py
```

## Python environment

The project uses a `.venv` at the repo root (Python 3.12). Activate with:
```bash
source .venv/bin/activate
```

Known Python dependencies (install into `.venv`):
- **rdflib** — OWL Turtle parsing (`code/owl/` package)

No `requirements.txt` or `pyproject.toml` is present. Clipper is the only remaining external tool called as a subprocess at runtime (via `code/rewriting/clipper.py`).
