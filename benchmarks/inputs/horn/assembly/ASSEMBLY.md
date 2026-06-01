# Assembly Benchmark — Horn DL-Lite

A smartphone assembly-line planning problem that exercises the Horn DL-Lite
fragment.  The ontology captures **component certification**, **assembly
completeness**, and **quality records** through three families of conjunction
axioms, connected by a chain: the RHS of the first assembly conjunction is a
conjunct in the second.

---

## Files

| File | Description |
|---|---|
| `assembly.owl` | Shared TBox — single ontology for all instances |
| `domain.pddl` | PDDL domain with 6 actions |
| `gen_assembly.py` | Problem-instance generator |
| `probASSEMBLY-{N}-0.pddl` | Clean-start instances, N = 1..5 phones |
| `probASSEMBLY-{N}-1.pddl` | Rework + quality-record instances, N = 2..6 phones |

```bash
python3 generate_pddl.py --fragments horn --variants var0 --tasks assembly
```

---

## Ontology design

### Roles — three functional roles

All three roles are functional.  Each appears only as the base role of an
inverse existential on the **LHS** of a range axiom — never on the RHS of any
inclusion — satisfying the DL-Lite Horn grammar restriction on functional roles.

```
∃screenInstalledIn⁻  ⊑  HasScreen     (screenInstalledIn  functional)
∃batteryInstalledIn⁻ ⊑  HasBattery    (batteryInstalledIn functional)
∃boardInstalledIn⁻   ⊑  HasBoard      (boardInstalledIn   functional)
```

### Assembly — two-step concept conjunction chain

The RHS of the first conjunction (`HasCoreComponents`) is a conjunct in the
second, creating a genuine two-step derivation chain:

```
HasScreen  ⊓  HasBattery        ⊑  HasCoreComponents   [HasScreen first]
HasCoreComponents  ⊓  HasBoard  ⊑  FullyEquipped        [HasCoreComponents first]
```

### Certification — one conjunction

```
Inspected  ⊓  Tested  ⊑  ReadyToUse   [Inspected first]
```

LTR ordering is exploited by `remove-and-rework-screen` (see below).

### Quality record — information preservation conjunction

```
FullyEquipped  ⊓  Validated  ⊑  ProductRecord   [FullyEquipped first]
```

`Validated` is set directly by the `validate-assembly` planning action.
`ProductRecord` is the RHS: once derived, it is **explicitly preserved in the
ABox** by the Horn update when `FullyEquipped` is deleted but `Validated` still
holds (see *information preservation* below).

LTR ordering: if `ProductRecord` itself is explicitly revoked
(`Am_ProductRecord`), `FullyEquipped` is the first non-Ap conjunct deleted
(not `Validated`).

---

## PDDL domain (6 actions)

| Action | Key precondition | Effect |
|---|---|---|
| `certify(?c)` | `Screen ?c` ∨ `Battery ?c` ∨ `Processor ?c` | `Inspected ?c`, `Tested ?c` |
| `install-screen(?s, ?p)` | `mko(ReadyToUse ?s)`, `Screen ?s`, `∀?p2 ¬screenInstalledIn(?s,?p2)`, `¬mko(HasScreen ?p)` | `screenInstalledIn ?s ?p` |
| `install-battery(?b, ?p)` | `mko(ReadyToUse ?b)`, `Battery ?b`, `¬mko(HasBattery ?p)` | `batteryInstalledIn ?b ?p` |
| `install-board(?r, ?p)` | `mko(ReadyToUse ?r)`, `Processor ?r`, `¬mko(HasBoard ?p)` | `boardInstalledIn ?r ?p` |
| `validate-assembly(?p)` | `mko(FullyEquipped ?p)` | `Validated ?p` |
| `remove-and-rework-screen(?s, ?p)` | `screenInstalledIn ?s ?p`, `mko(ReadyToUse ?s)` | see below |

### `remove-and-rework-screen` — two simultaneous Horn cascades

Raw effects: `¬FullyEquipped ?p`, `Inspected ?s`, `¬ReadyToUse ?s`

After compilation: `Am_FullyEquipped`, `Ap_Inspected`, `Am_ReadyToUse`.

Note: `¬screenInstalledIn ?s ?p` is **not** a direct effect — the role fact is
deleted entirely by the cascade from `Am_FullyEquipped` (see below).

**Why rework is the only path to install a screen:** `install-screen` carries a
universal precondition `(forall ?p2 (not (screenInstalledIn ?s ?p2)))`.  In var1
init, every screen already has a `screenInstalledIn` fact, so this precondition
fails.  After the cascade fires (update action deletes all `screenInstalledIn` facts
for phone ?p), **both** the reworked screen and the partner screen satisfy the
precondition and become installable.

**Why validate-then-rework is the only feasible ordering:** without prior
validation, stratum 3 does not fire, `ProductRecord` for ?p is not preserved, and
no screen can be reinstalled on ?p (the partner is installable elsewhere but the
reworked screen needs certify first; reinstalling either on ?p would satisfy
`HasScreen` but `FullyEquipped` and `Validated` are both gone — `ProductRecord`
remains unachievable).  Validate first so stratum 3 preserves `ProductRecord`;
then rework to release the screens.

**Stratum 2 — deletion cascades from `Am_FullyEquipped`:**

```
DelCl_FullyEquipped
  → rules 13-14 (HasCoreComponents ⊓ HasBoard ⊑ FullyEquipped):
      Min picks HasCoreComponents (first non-Ap) → DelCl_HasCoreComponents
  → rules 13-14 (HasScreen ⊓ HasBattery ⊑ HasCoreComponents):
      Min picks HasScreen (first non-Ap) → DelCl_HasScreen
  → rules 13-14 k=1 (∃screenInstalledIn⁻ ⊑ HasScreen):
      min trivially true (Ap_∃screenInstalledIn⁻ never asserted)
      → DelCl_∃screenInstalledIn⁻(p)
  → rule 7 for InverseRole(screenInstalledIn):
      DelCl_inv_screenInstalledIn(p, s)
  → rule 6: DelCl_screenInstalledIn(s, p) → del_screenInstalledIn(s, p)
```

```
DelCl_ReadyToUse (from Am_ReadyToUse)
  → rules 13-14 (Inspected ⊓ Tested ⊑ ReadyToUse):
      Ap_Inspected shields Inspected; Min picks Tested → DelCl_Tested
```

`HasBoard` and `HasBattery` are **not** deleted: Min always picks the first
non-Ap conjunct (`HasCoreComponents`, not `HasBoard`; `HasScreen`, not
`HasBattery`).

**Stratum 3 — information preservation** (fires when `Validated ?p` holds):

```
preInsCl_{FullyEquipped⊓Validated⊑ProductRecord}:
    AOrApCl_FullyEquipped  — FullyEquipped currently true  ✓
    AOrApCl_Validated      — Validated still holds         ✓
    ¬DelCl_ProductRecord   — nobody requests its deletion  ✓
  → fires

insCl_ProductRecord ← DelCl_FullyEquipped ∧ preInsCl → fires
ins_ProductRecord: ProductRecord explicitly inserted in ABox
```

The preInsCl rules for the assembly chain do **not** fire spuriously:
`¬DelCl_HasCoreComponents` is false (it IS being deleted), so `HasCoreComponents`
is not preserved; `¬DelCl_FullyEquipped` is false, so `FullyEquipped` is not
preserved.  Only `ProductRecord` is preserved because nobody deleted it.

**Net state after the update action:**

| Predicate | Status | Reason |
|---|---|---|
| `screenInstalledIn` | ✗ | cascade: rules 13-14 k=1 → rule 7 → rule 6 from `Am_FullyEquipped` |
| `HasScreen` | ✗ | cascade: rules 13-14 from `Am_FullyEquipped` |
| `HasCoreComponents` | ✗ | cascade: rules 13-14 from `Am_FullyEquipped` |
| `HasBoard`, `HasBattery` | ✓ | not in any cascade path (Min never picks them) |
| `FullyEquipped` | ✗ | direct `Am_FullyEquipped` |
| `Inspected` | ✓ | shielded by `Ap_Inspected` |
| `Tested` | ✗ | first non-Ap in certification cascade from `Am_ReadyToUse` |
| `ReadyToUse` | ✗ | direct `Am_ReadyToUse` |
| `Validated` | ✓ | untouched |
| `ProductRecord` | ✓ | **explicitly asserted** by information preservation (rules 18-19) |

Recovery: one `certify` re-sets `Tested` (Inspected was already shielded),
re-deriving `ReadyToUse`, then `install-screen` re-derives
`HasScreen → HasCoreComponents → FullyEquipped`.  `ProductRecord` was never lost.

---

## Instance variants

### Variant 0 — clean start (`probASSEMBLY-N-0`, N = 1..5)

- N phones; nothing certified or installed.
- Goal: `mko(FullyEquipped phone_i)` for all i.
- Minimal plan: certify + install per component × 3 × N = **6N** steps.

### Variant 1 — rework + quality-record (`probASSEMBLY-N-1`, N = 2..6)

Combines the rework cascade with stratum 3 information preservation in a single
scenario.

**Init:**
- All N screens are pre-certified (`Inspected + Tested`) and stacked in pairs on
  odd-indexed phones: `screen_{2k−1}` and `screen_{2k}` both start on
  `phone_{2k−1}`.  Even-indexed phones have no screen.
- Odd phones (`phone_1`, `phone_3`, …): battery + board **pre-installed**;
  `FullyEquipped` is derived in init.  `Validated` is **absent** — no phone has
  `ProductRecord` satisfied at the start.
- Even phones (`phone_2`, `phone_4`, …): battery + board uncertified and uninstalled.

**Goal:** `mko(ProductRecord phone_i)` for all i.

**Why rework is forced:** all screens are already installed on odd phones; the planner
cannot certify-and-install a fresh screen for any empty even phone.

**Why validate-then-rework is optimal (stratum 3):** if the planner validates an odd
phone first (`validate-assembly` requires only `FullyEquipped`, already derived), then
calls `remove-and-rework-screen`, `Validated` holds at rework time and stratum 3 fires:

```
preInsCl_{FullyEquipped⊓Validated⊑ProductRecord}:
    AOrApCl_FullyEquipped — FullyEquipped currently true  ✓
    AOrApCl_Validated     — Validated still holds          ✓
    ¬DelCl_ProductRecord  — nobody requests its deletion   ✓
  → fires → ins_ProductRecord: ProductRecord explicitly asserted
```

`ProductRecord` on the odd phone is preserved in the ABox — no reinstallation or
re-validation needed.

**Only feasible ordering (rework without prior validation is unsolvable):**
If the planner reworks before validating, both screens are released (cascade clears
`screenInstalledIn` for all screens on the phone, satisfying the forall precondition
for both).  But `Validated` was never set, so stratum 3 does not fire and
`ProductRecord` for the odd phone is not preserved.  Both screens can be reinstalled
elsewhere, but the odd phone now has no screens and `Validated = false` — it can
never satisfy `ProductRecord` without first reinstalling a screen, then validating;
but the only free screen went to the even phone.  Stratum 3 is therefore required
for solvability, not just efficiency.

**Cascade property:** `Am_FullyEquipped` propagates through the conjunction chain
to `DelCl_∃screenInstalledIn⁻`; rule 7 fires for the **entire phone** — both screens
exit simultaneously.  The non-reworked screen retains its certification and is
immediately installable on the even phone; the reworked screen has `Inspected` shielded
and `Tested` deleted, requiring one `certify` before reinstallation.

**Minimal plan (N = 2):**

| Step | Action | Horn mechanism |
|---|---|---|
| 1 | `validate-assembly(phone_1)` | requires `mko(FullyEquipped)`, sets `Validated` |
| 2 | `remove-and-rework-screen(screen_1, phone_1)` | `Am_FullyEquipped` cascade + stratum 3 preserves `ProductRecord(phone_1)`; cascade deletes `screenInstalledIn` for **both** screens |
| 3 | `install-screen(screen_2, phone_2)` | screen_2 still `ReadyToUse`; forall precondition now satisfied (cascade cleared `screenInstalledIn`) |
| 4 | `certify(battery_2)` | — |
| 5 | `install-battery(battery_2, phone_2)` | — |
| 6 | `certify(board_2)` | — |
| 7 | `install-board(board_2, phone_2)` | — |
| 8 | `validate-assembly(phone_2)` | `ProductRecord(phone_2)` derived |

8 steps; `ProductRecord(phone_1)` preserved by stratum 3.  screen_1 (reworked, needs one certify) is unused for N = 2.

General: ≈ **4N** steps.

---

## What makes this benchmark Horn-specific

| Feature | Where it appears |
|---|---|
| Conjunction on LHS (`A ⊓ B ⊑ C`) | All four TBox axioms; absent in DL-Lite core |
| Two-step conjunction chain | `HasCoreComponents` is both RHS of axiom 1 and conjunct in axiom 2 |
| Functional role conflict (rules 8–9) | All three installation roles |
| Range axioms (`∃R⁻ ⊑ A`) | All three roles derive assembly-status concepts |
| Horn LTR ordering | `remove-and-rework-screen`: Inspected shielded, Tested deleted |
| Top-down cascade deletion | `Am_FullyEquipped` propagates through rules 13-14 all the way to `del_screenInstalledIn` via the k=1 range axiom + rule 7 |
| Information preservation (rules 18-19) | `ProductRecord` explicitly asserted after rework when `Validated` holds |
