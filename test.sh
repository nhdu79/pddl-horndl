i=4
task="robot"
## path to a (patched) clipper
clipper="/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
nmo="/home/zinzin2312/repos/nemo/target/release/nmo"
fastdownward="/home/zinzin2312/repos/downward/fast-downward.py"

# clipper="/Users/duynhu/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
# nmo="/Users/duynhu/.appimages/nemo_v0.7.1_aarch64-apple-darwin/nmo"
# fastdownward="/Users/duynhu/repos/downward/fast-downward.py"

compiler="code/compiler.py"
tseitin="code/tseitin.py"
rls="code/nemo/t_closure.rls"

owl=test/TTL${i}.owl
input_domain=test/${task}Domain${i}.pddl
input_problem="test/${task}Problem${i}.pddl"
result_domain="test/test_domain.pddl"
result_problem="test/test_problem.pddl"

python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --rls "$rls" --nmo "$nmo"

# python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf

$fastdownward $result_domain $result_problem --search "let(hff,ff(axioms=approximate_negative),lazy_greedy([hff],preferred=[hff]))"
