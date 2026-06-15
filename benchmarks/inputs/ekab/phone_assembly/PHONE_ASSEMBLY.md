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
∃processorInstalledIn⁻ ⊑  HasProcessor
```

The three defect-tracking roles are functional and inverse-functional, each
appearing on the LHS of a domain axiom:

```
∃hasBrokenScreen  ⊑  HasDefect
∃hasBrokenBattery ⊑  HasDefect
∃hasBrokenProcessor ⊑  HasDefect
```

Broken components are **not** typed as `Screen`/`Battery`/`Processor`, so they
cannot be inspected or installed.  In problem init, only `(hasBrokenX phone_i comp_i)`
is asserted — no separate `BrokenX` concept is needed.  A separate `spare_X_i`
object (typed as the working type) serves as the replacement.
At most one `hasBrokenX` role is asserted per phone.

> **Design note — sub-property axioms deliberately omitted.**
>
> An earlier version of the ontology included role inclusions
> `hasBrokenScreen ⊑ screenInstalledIn⁻` (and the analogous lines for battery
> and processor).  These caused a fatal **stratum 3 re-insertion loop**:
>
> When `repair` cascade deleted `hasBrokenScreen(p,c)` via `Am_BrokenPhone`,
> stratum 3 rules 18–19 for the role inclusion fired.  `preInsCl_τ` saw
> `AOrApCl_hasBrokenScreen` still true at evaluation time (the deletion had
> not yet completed) and `DelCl_screenInstalledIn_inv` unset — because rule 14
> for role inclusions propagates deletion *super→sub* only (not *sub→super*),
> so deleting `hasBrokenScreen` does not trigger `DelCl_screenInstalledIn`.
> As a result `insCl_screenInstalledIn_inv` fired and `screenInstalledIn(c,p)`
> was permanently asserted into the ABox, re-deriving `HasScreen` from the
> broken component and making the spare screen impossible to install.
>
> With sub-property axioms removed, the role inclusion no longer exists, so
> stratum 3 never fires for it.  Instead, each broken phone's init ABox now
> **explicitly includes both `hasBrokenX(phone,comp)` and `XInstalledIn(comp,phone)`**,
> modelling the physical reality that all three components are in the phone
> (one is broken).  This means `HasX`, `FullyEquipped`, and `BrokenPhone` are
> all derivable from the initial state, so `authorize-repair` is applicable
> immediately.  The `forall (?b) (not (hasBrokenX ?p ?b))` guard on each
> `install-X` action prevents the spare from being installed while the broken
> component is still tracked.  After `repair` removes `hasBrokenX`, the spare
> can be installed; the InverseFunctional rule 8 side-effect then displaces
> the broken component's `XInstalledIn` when the spare's installation is asserted.

### Assembly — three-way concept conjunction

```
HasScreen  ⊓  HasBattery  ⊓  HasProcessor  ⊑  FullyEquipped   [HasScreen first]
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
| `install-screen(?s, ?p)` | `mko(ReadyToUse ?s)`, `Screen ?s`, `Phone ?p`, `¬mko(HasScreen ?p)`, `∀b.¬hasBrokenScreen ?p ?b` | `screenInstalledIn ?s ?p` |
| `install-battery(?b, ?p)` | `mko(ReadyToUse ?b)`, `Battery ?b`, `Phone ?p`, `¬mko(HasBattery ?p)`, `∀b.¬hasBrokenBattery ?p ?b` | `batteryInstalledIn ?b ?p` |
| `install-processor(?r, ?p)` | `mko(ReadyToUse ?r)`, `Processor ?r`, `Phone ?p`, `¬mko(HasProcessor ?p)`, `∀b.¬hasBrokenProcessor ?p ?b` | `processorInstalledIn ?r ?p` |
| `authorize-repair(?p)` | `Phone ?p`, `mko(BrokenPhone ?p)`, `UnderWarranty ?p` | `RepairAuthorized ?p` |
| `repair(?p)` | `Phone ?p`, `mko(BrokenPhone ?p)`, `RepairAuthorized ?p` | `¬BrokenPhone ?p`; conditional: `¬XInstalledIn(broken,p)`, `¬FullyEquipped ?p` — see below |

### `authorize-repair` — warranty gate before repair

`authorize-repair` requires:
- `mko(BrokenPhone ?p)` — derivable from the initial ABox because each broken
  phone carries both `hasBrokenX(phone,comp)` (→ HasDefect) and
  `XInstalledIn(comp,phone)` (→ HasX → FullyEquipped), so
  `HasDefect ⊓ FullyEquipped ⊑ BrokenPhone` fires from the start.
- `UnderWarranty ?p` directly in the ABox — the predicate that also guards the
  stratum 3 `WarrantyClaim` preservation, making warranty status load-bearing in
  the workflow rather than just a side condition.

The action produces `RepairAuthorized ?p`, which gates the `repair` action.

### `repair` — stratum 2 cascade + stratum 3 warranty preservation

`repair` requires `mko(BrokenPhone ?p)` and `RepairAuthorized ?p`.

The plan for any broken phone is 5 steps:
`authorize-repair(phone) → repair(phone) → inspect(spare) → test(spare) → install-X(spare, phone)`.
The authorize/repair pair and the inspect/test pair are mutually independent and
can be freely interleaved, but both must complete before `install-X`.

Raw effects: `¬BrokenPhone ?p`  **and**  one conditional branch that fires for the
broken component type — e.g. `(when (hasBrokenScreen ?p ?s) (and (not (screenInstalledIn ?s ?p)) (not (FullyEquipped ?p))))`.

After compilation: `Am_BrokenPhone` + `Am_XInstalledIn(broken_comp, p)` + `Am_FullyEquipped(p)` (all simultaneously).

`Am_FullyEquipped` is included because prior coherence updates may have asserted
`FullyEquipped` as an explicit ABox fact (e.g. via `ins_FullyEquipped` in a
previous step); the explicit deletion ensures it is removed regardless of how it
was last asserted.

**Stratum 2 — three concurrent cascades:**

```
Am_BrokenPhone:
  DelCl_BrokenPhone  [rule 5]
    → rule 14 (HasDefect ⊓ FullyEquipped ⊑ BrokenPhone):
        Min = HasDefect; AOrApCl_FullyEquipped ✓
        → DelCl_HasDefect(p)
    → k=1 for each ∃hasBrokenX ⊑ HasDefect:
        → DelCl_∃hasBrokenX, rule 7 → DelCl_hasBrokenX(p,c)
        → rule 17: del_hasBrokenX(p,c)

Am_XInstalledIn(broken,p):
  DelCl_XInstalledIn(broken,p)  [rule 5]
    → rule 6:  DelCl_XInstalledIn_inv(p, broken)
    → rule 7:  DelCl_∃XInstalledIn_inv(p)
    → rule 14 k=1 (∃XInstalledIn_inv ⊑ HasX): DelCl_HasX(p)
    → rule 17: del_XInstalledIn(broken,p)  [ABox fact present ✓]

Am_FullyEquipped(p):
  DelCl_FullyEquipped(p)  [rule 5]
    → rule 17: del_FullyEquipped(p)  [if FullyEquipped is an ABox fact ✓]

Stratum 3 re-insertion blocked:
  rule 20 requires ¬DelCl_HasX — but DelCl_HasX IS set → preInsCl does not fire ✓
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

**Net state after `repair(phone)`:**

| Predicate | Status | Reason |
|---|---|---|
| `hasBrokenX` | ✗ | `Am_BrokenPhone` cascade: rule 14 + k=1 + rule 7 + rule 17 |
| `HasDefect` | ✗ | cascade via `DelCl_HasDefect` |
| `XInstalledIn(broken,p)` | ✗ | `Am_XInstalledIn` conditional effect → rule 17 |
| `HasX` | ✗ | `XInstalledIn` deleted; `DelCl_HasX` set; re-insertion blocked |
| `FullyEquipped` | ✗ | `Am_FullyEquipped` conditional effect → rule 17 (also no longer derivable: `HasX` absent) |
| `BrokenPhone` | ✗ | `HasDefect` absent |
| `UnderWarranty` | ✓ | untouched |
| `WarrantyClaim` | ✓ | **explicitly asserted** by stratum 3 (rules 18–19) |
| `RepairAuthorized` | ✓ | set by `authorize-repair`; not deleted by repair |
| `install-X` applicable? | ✓ | `¬mko(HasX)` ✓, `∀b.¬hasBrokenX` ✓ — unblocked after repair |

---

## Instance variants

### Mixed scenario (`probPHONE_ASSEMBLY-N-0`, N = 1..10)

`ceil(N/2)` broken phones + `floor(N/2)` incomplete phones in a single instance.
The broken component type cycles: phone_1 → broken screen, phone_2 → broken battery,
phone_3 → broken processor, phone_4 → broken screen, …

**Broken-screen phone init** (i ≡ 1 mod 3):
- `UnderWarranty phone_i`
- `hasBrokenScreen phone_i screen_i` — tracks defect; `screen_i` not typed as Screen
- `screenInstalledIn screen_i phone_i` — broken screen physically in slot
- Battery and processor installed
- `Screen spare_screen_i` — uncertified replacement, not yet installed

**Broken-battery phone init** (i ≡ 2 mod 3):
- `UnderWarranty phone_i`
- Screen installed
- `hasBrokenBattery phone_i battery_i` — tracks defect; `battery_i` not typed as Battery
- `batteryInstalledIn battery_i phone_i` — broken battery physically in slot
- Processor installed
- `Battery spare_battery_i` — uncertified replacement, not yet installed

**Broken-processor phone init** (i ≡ 0 mod 3):
- `UnderWarranty phone_i`
- Screen and battery installed
- `hasBrokenProcessor phone_i processor_i` — tracks defect; `processor_i` not typed as Processor
- `processorInstalledIn processor_i phone_i` — broken processor physically in slot
- `Processor spare_processor_i` — uncertified replacement, not yet installed

Derived in init per broken phone (regardless of which component is broken):
- `HasDefect` (from `∃hasBrokenX ⊑ HasDefect`)
- All three of `HasScreen`, `HasBattery`, `HasProcessor` (from all three `XInstalledIn` facts)
- `FullyEquipped` (from the three-way conjunction)
- `BrokenPhone` (from `HasDefect ⊓ FullyEquipped ⊑ BrokenPhone`)

**Incomplete phone init** (phone_i, i > ceil(N/2)):
- `Screen screen_i`, `Battery battery_i`, `Processor processor_i` — not installed

**Goal:** `∀?p. Phone(?p) → mko(FullyEquipped ?p) ∧ (UnderWarranty(?p) → ¬mko(HasDefect ?p) ∧ mko(WarrantyClaim ?p))`.

**Plan per broken phone (5 steps):** `authorize-repair(phone) → repair(phone) → inspect(spare) → test(spare) → install-X(spare, phone)`.  `repair` fires `Am_BrokenPhone` and `Am_XInstalledIn(broken,phone)` together via conditional effects, clearing both `hasBrokenX` and the broken component's installation slot so install-X is unblocked.

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
| Three-way conjunction | `HasScreen ⊓ HasBattery ⊓ HasProcessor ⊑ FullyEquipped` |
| Functional + inverse-functional roles | All six roles; rules 8–9 detect insertion conflicts |
| Range axioms (`∃R⁻ ⊑ A`) | Three installation roles derive assembly-status concepts |
| Domain axioms (`∃R ⊑ A`) | Three defect-tracking roles all derive `HasDefect` |
| Horn LTR ordering (stratum 2) | `repair`: `Am_BrokenPhone` → Min picks `HasDefect` (first conjunct in `HasDefect ⊓ FullyEquipped`) |
| Top-down cascade deletion | `Am_BrokenPhone` → rules 14, 7, 17 → `del_hasBrokenX`; concurrent `Am_XInstalledIn` (conditional effect) → rule 17 → `del_XInstalledIn` |
| Conjunction-based information preservation (stratum 3) | `WarrantyClaim` explicitly asserted after repair when `UnderWarranty` holds |
| TBox-derived super-concept via `mko` | `Component` queried as MKO; never in ABox |
| Workflow precondition via direct ABox fact | `authorize-repair` requires `UnderWarranty` in ABox before `repair` is enabled |
