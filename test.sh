task="cat"
i=6
prefix="benchmarks/$task"
## path to a (patched) clipper
clipper="/Users/duynhu/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
nmo="/Users/duynhu/.appimages/nemo_v0.7.1_aarch64-apple-darwin/nmo"
rls="code/nemo/t_closure.rls"
fastdownward="/Users/duynhu/repos/downward/fast-downward.py"
# path to compiler.py
compiler="code/compiler.py"
tseitin="code/tseitin.py"

owl=$prefix/original/TTL.owl
input_domain=$prefix/original/domain.pddl
input_problem="$prefix/original/${task}Problem${i}.pddl"
result_domain="test/test_domain.pddl"
result_problem="test/test_problem.pddl"

python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --rls "$rls" --nmo "$nmo"

$fastdownward $result_domain $result_problem --search "let(hff,ff(axioms=approximate_negative),lazy_greedy([hff],preferred=[hff]))"
