# Phone Assembly Benchmark — Horn DL-Lite

A smartphone assembly-line planning problem that exercises the Horn DL-Lite
fragment, demonstrating conjunction-based update semantics across two scenarios.

---

## Files

| File | Description |
|---|---|
| `assembly.owl` | Shared TBox — single ontology for all instances |
| `domain.pddl` | PDDL domain with 7 actions (`phone_assembly`) |
| `gen_phone_assembly.py` | Problem-instance generator |
| `probPHONE_ASSEMBLY-{N}-0.pddl` | Mixed instances (broken + incomplete phones), N = 1..10 |

```bash
python3 generate_pddl.py --fragments horn --variants var0 --tasks phone_assembly
```

---

## Ontology design

### Roles — three installation roles + three defect-tracking roles

The three installation roles are functional and inverse-functional; each appears
only as the base role of an inverse existential on the LHS of a range axiom:

```
∃screenInstalledIn⁻  ⊑  HasScreen
∃batteryInstalledIn⁻ ⊑  HasBattery
∃boardInstalledIn⁻   ⊑  HasBoard
```

The three defect-tracking roles are functional and inverse-functional, each
appearing only on the LHS of a domain axiom:

```
∃hasBrokenScreen  ⊑  HasDefect
∃hasBrokenBattery ⊑  HasDefect
∃hasBrokenBoard   ⊑  HasDefect
```

Broken components are **not** typed as `Screen`/`Battery`/`Processor`, so they
cannot be inspected or installed.  In problem init, only `(hasBrokenX phone_i comp_i)`
is asserted — no separate `BrokenX` concept is needed.  A separate `spare_X_i`
object (typed as the working type) serves as the replacement.
At most one `hasBrokenX` role is asserted per phone.

### Assembly — three-way concept conjunction

```
HasScreen  ⊓  HasBattery  ⊓  HasBoard  ⊑  FullyEquipped   [HasScreen first]
```

LTR ordering: Min picks the leftmost non-Ap conjunct when FullyEquipped is deleted.

### Certification — one conjunction

```
Inspected  ⊓  Tested  ⊑  ReadyToUse   [Inspected first]
```

LTR ordering: asserting `Ap_Inspected` shields Inspected, so Tested is deleted
instead — a component retains Inspected and needs only one `test` to recertify.

### Defect and warranty — two conjunction axioms

```
HasDefect  ⊓  FullyEquipped  ⊑  BrokenPhone   [HasDefect first]
HasDefect  ⊓  UnderWarranty  ⊑  WarrantyClaim  [HasDefect first]
```

`BrokenPhone` drives the **stratum 2** cascade in the `repair` action.
`WarrantyClaim` is preserved by **stratum 3** when the defect is fixed but
`UnderWarranty` still holds — fixing a defect does not revoke the warranty claim.

### Component super-concept (TBox-derived)

```
Screen  ⊑  Component
Battery ⊑  Component
Processor ⊑ Component
```

`Component` is queried via `mko(Component ?c)`; never directly in the ABox.

---

## PDDL domain (7 actions)

| Action | Key precondition | Effect |
|---|---|---|
| `inspect(?c)` | `mko(Component ?c)` | `Inspected ?c` |
| `test(?c)` | `mko(Component ?c)`, `Inspected ?c` | `Tested ?c` |
| `install-screen(?s, ?p)` | `mko(ReadyToUse ?s)`, `Screen ?s`, `Phone ?p`, `¬mko(HasScreen ?p)` | `screenInstalledIn ?s ?p` |
| `install-battery(?b, ?p)` | `mko(ReadyToUse ?b)`, `Battery ?b`, `Phone ?p`, `¬mko(HasBattery ?p)` | `batteryInstalledIn ?b ?p` |
| `install-board(?r, ?p)` | `mko(ReadyToUse ?r)`, `Processor ?r`, `Phone ?p`, `¬mko(HasBoard ?p)` | `boardInstalledIn ?r ?p` |
| `authorize-repair(?p)` | `Phone ?p`, `mko(BrokenPhone ?p)`, `UnderWarranty ?p` | `RepairAuthorized ?p` |
| `repair(?p)` | `Phone ?p`, `mko(BrokenPhone ?p)`, `RepairAuthorized ?p` | `¬BrokenPhone ?p`, `Repaired ?p` — see below |

### `authorize-repair` — warranty gate before repair

`authorize-repair` requires:
- `mko(BrokenPhone ?p)` — only derivable after the spare component is installed
  (restoring `FullyEquipped`); this is the same prerequisite as `repair` itself.
- `UnderWarranty ?p` directly in the ABox — the predicate that also guards the
  stratum 3 `WarrantyClaim` preservation, making warranty status load-bearing in
  the workflow rather than just a side condition.

The action produces `RepairAuthorized ?p`, which gates the `repair` action.

### `repair` — stratum 2 cascade + stratum 3 warranty preservation

`repair` requires `mko(BrokenPhone ?p)` (only derivable once `FullyEquipped`
holds) and `RepairAuthorized ?p`.  The plan for any broken phone is therefore:
`inspect(spare) → test(spare) → install-X(spare, phone) → authorize-repair(phone) → repair(phone)`.

Raw effects: `¬BrokenPhone ?p`, `Repaired ?p`.

After compilation: `Am_BrokenPhone`, `Ap_Repaired`.

**Stratum 2 cascade from `Am_BrokenPhone`:**

```
DelCl_BrokenPhone
  → rule 14 (HasDefect ⊓ FullyEquipped ⊑ BrokenPhone):
      Min picks HasDefect (first non-Ap); AOrApCl_FullyEquipped required
      → DelCl_HasDefect
  → k=1 rule for each domain axiom (∃hasBrokenX ⊑ HasDefect):
      → DelCl_∃hasBrokenScreen(p)   ]
      → DelCl_∃hasBrokenBattery(p)  ]  all three fire
      → DelCl_∃hasBrokenBoard(p)    ]
  → rule 7 for each → DelCl_hasBrokenX(p, c)
  → rule 17: del_hasBrokenX(p, c)   [fires only for the one role in the ABox]
```

**Stratum 3 — WarrantyClaim preservation (fires when UnderWarranty holds):**

```
preInsCl_{HasDefect⊓UnderWarranty⊑WarrantyClaim}:
    AOrApCl_HasDefect     — HasDefect currently true  ✓
    AOrApCl_UnderWarranty — UnderWarranty still holds ✓
    ¬DelCl_WarrantyClaim  — nobody revokes the claim  ✓
  → fires

insCl_WarrantyClaim ← DelCl_HasDefect ∧ preInsCl → fires
ins_WarrantyClaim: WarrantyClaim explicitly inserted in ABox
```

**Net state after `repair(phone)` (phone fully assembled + under warranty):**

| Predicate | Status | Reason |
|---|---|---|
| `hasBrokenX` | ✗ | cascade: k=1 + rule 7 + rule 17 from `Am_BrokenPhone` |
| `HasDefect` | ✗ | cascade: rule 14 from `Am_BrokenPhone` |
| `FullyEquipped` | ✓ | unaffected — HasScreen/HasBattery/HasBoard still hold |
| `BrokenPhone` | ✗ | direct `Am_BrokenPhone` |
| `UnderWarranty` | ✓ | untouched |
| `WarrantyClaim` | ✓ | **explicitly asserted** by stratum 3 (rules 18-19) |
| `RepairAuthorized` | ✓ | set by `authorize-repair`; not deleted by repair |
| `Repaired` | ✓ | direct effect |

---

## Instance variants

### Mixed scenario (`probPHONE_ASSEMBLY-N-0`, N = 1..10)

`ceil(N/2)` broken phones + `floor(N/2)` incomplete phones in a single instance.
The broken component type cycles: phone_1 → broken screen, phone_2 → broken battery,
phone_3 → broken board, phone_4 → broken screen, …

**Broken-screen phone init** (i ≡ 1 mod 3):
- `UnderWarranty phone_i`
- `hasBrokenScreen phone_i screen_i` — tracks defect; `screen_i` not typed as Screen
- Battery and board installed
- `Screen spare_screen_i` — uncertified replacement, not yet installed

**Broken-battery phone init** (i ≡ 2 mod 3):
- `UnderWarranty phone_i`
- Screen and board installed
- `hasBrokenBattery phone_i battery_i` — tracks defect; `battery_i` not typed as Battery
- `Battery spare_battery_i` — uncertified replacement, not yet installed

**Broken-board phone init** (i ≡ 0 mod 3):
- `UnderWarranty phone_i`
- Screen and battery installed
- `hasBrokenBoard phone_i board_i` — tracks defect; `board_i` not typed as Processor
- `Processor spare_board_i` — uncertified replacement, not yet installed

Derived in init per broken phone (regardless of which component is broken):
- `HasDefect` (from `∃hasBrokenX ⊑ HasDefect`)
- Two of {`HasScreen`, `HasBattery`, `HasBoard`} (from the two installed components)
- `FullyEquipped` and `BrokenPhone` are **not** yet derivable (missing one component slot)

**Incomplete phone init** (phone_i, i > ceil(N/2)):
- `Screen screen_i`, `Battery battery_i`, `Processor board_i` — not installed

**Goal:** `∀?p. Phone(?p) → mko(FullyEquipped ?p) ∧ (UnderWarranty(?p) → Repaired(?p) ∧ mko(WarrantyClaim ?p))`.

**Plan per broken phone (5 steps):** `inspect(spare) → test(spare) → install-X(spare, phone) → authorize-repair(phone) → repair(phone)`.

**Plan per incomplete phone (9 steps):** `(inspect + test + install) × 3` components.

| N | broken | incomplete | min steps |
|---|--------|------------|-----------|
| 1 | 1 | 0 | 5 |
| 2 | 1 | 1 | 14 |
| 3 | 2 | 1 | 19 |
| 4 | 2 | 2 | 28 |
| 5 | 3 | 2 | 33 |
| 6 | 3 | 3 | 42 |
| 7 | 4 | 3 | 47 |
| 8 | 4 | 4 | 56 |
| 9 | 5 | 4 | 61 |
| 10 | 5 | 5 | 70 |

---

## What makes this benchmark Horn-specific

| Feature | Where it appears |
|---|---|
| Conjunction on LHS (`A ⊓ B ⊑ C`) | All four TBox axioms; absent in DL-Lite core |
| Three-way conjunction | `HasScreen ⊓ HasBattery ⊓ HasBoard ⊑ FullyEquipped` |
| Functional + inverse-functional roles | All six roles; rules 8–9 detect insertion conflicts |
| Range axioms (`∃R⁻ ⊑ A`) | Three installation roles derive assembly-status concepts |
| Domain axioms (`∃R ⊑ A`) | Three defect-tracking roles all derive `HasDefect` |
| Horn LTR ordering (stratum 2) | `repair`: Min picks HasDefect as first conjunct in `HasDefect ⊓ FullyEquipped` |
| Top-down cascade deletion | `Am_BrokenPhone` → rules 14, 7, 17 → `del_hasBrokenX` (one of three roles) |
| Conjunction-based information preservation (stratum 3) | `WarrantyClaim` explicitly asserted after repair when `UnderWarranty` holds |
| TBox-derived super-concept via `mko` | `Component` queried as MKO; never in ABox |
| Workflow precondition via direct ABox fact | `authorize-repair` requires `UnderWarranty` in ABox before `repair` is enabled |
