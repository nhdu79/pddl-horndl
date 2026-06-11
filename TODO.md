- [ ] Find out why `phone_assembly doesn't have a plan!

- [x] Change goals for `phone_assembly` as in PROB1
- [x] Remove `Repaired` predicate!
- [x] Extend `hasBrokenScreen -> hasScreenInstalled^-`
- [x] Remove `min_*` for `Horn` whenever there is only 1 concept on LHS or role (by `AorApCl`)

- Mb change name of benchmark to phone?
- [x] Inverse role functional for *InstalledIn
- [x] Problem use (for all ?p (and (Phone ?P) (ProductRecord ?P)))
- [x] Filter reachability for predicate after rule generation!
- [x] Machanism for extending ontology!
- [x] RobotConj: `RightOf0` instead of `RightOf1` in prob file

=========================

;; ── nearObject: ?x vacated (no longer Objectx); ?y occupied (now Objectx)
(forall (?z) (when (near ?z ?x)      (not (nearObject ?z ?x))))
(forall (?z) (when (veryClose ?z ?x) (not (nearObject ?z ?x))))
(forall (?z) (when (near ?z ?y)      (nearObject ?z ?y)))
(forall (?z) (when (veryClose ?z ?y) (nearObject ?z ?y)))

;; ── nearMoving: same update (MovingObject ⊆ Objectx, drone is MovingObject)
(forall (?z) (when (near ?z ?x)      (not (nearMoving ?z ?x))))
(forall (?z) (when (veryClose ?z ?x) (not (nearMoving ?z ?x))))
(forall (?z) (when (near ?z ?y)      (nearMoving ?z ?y)))
(forall (?z) (when (veryClose ?z ?y) (nearMoving ?z ?y)))

;; ── veryCloseObject: only veryClose (orthogonal) neighbours
(forall (?z) (when (veryClose ?z ?x) (not (veryCloseObject ?z ?x))))
(forall (?z) (when (veryClose ?z ?y) (veryCloseObject ?z ?y)))
