In the `pceKAB` (`horn`) implementation, following problems are found:

- [x] We should not use the "object" type at all - just declare no type.
- [x] It would also be problematic if we had types in the input domain.pddl - right now they are deleted and replaced by "object". (We don't have such benchmarks so far, but someone who wants to try out the compiler may use types.
Similarly, `d.constants = p.objects` overwrites any constants that are declared in the input domain file.
- [x] :derived-predicates should be added to the :requirements section
- [x] _drop_irrelevant_datalog_rules() does not seem to work properly, sometimes it keeps irrelevant rules (Do we need this? We also check for reachability of predicates!)
- [x] For reproducibility, it would be good if the output of the compiler is always the same. Right now, due to some unstable collections used in the code, the order of rules in the output is nondeterministic
- [x] Clipper errors are silently ignored. If the return code of Clipper indicates some problem, the compiler just continues with an empty set of rules
- [x] According to the README, the Clipper patch should be applied with 'git am', which fails because of a missing 'From:' line
- [x] Instead of hard-coded paths, the various scripts should use command-line arguments, a configuration file, or PATH lookup (or a combination of all three in that order of priority)

All fixed — decisions, verification and open points are in `FIXES.md`.

Fix the above problems and write down decision made/progress in a separate `.md` file. You can try to run the compiler on the benchmarks but only use the smallest instance, do not run it on larger instances.
