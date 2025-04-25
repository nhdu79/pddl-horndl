## Desktop
clipper="/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
nmo="/home/zinzin2312/repos/nemo/target/release/nmo"
fastdownward="/home/zinzin2312/repos/downward/fast-downward.py"
parser="/home/zinzin2312/repos/validator/linux64/Val-20211204.1-Linux/bin/Parser"

## Laptop
# clipper="/Users/duynhu/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
# nmo="/Users/duynhu/.appimages/nemo_v0.7.1_aarch64-apple-darwin/nmo"
# fastdownward="/Users/duynhu/repos/downward/fast-downward.py"

compiler="code/compiler.py"
tseitin="code/new_tseitin.py"
rls="code/nemo/t_closure.rls"
parser="code/utils/parser_wrapper.py"
tasks=(catOG elevator robot task order trip tripv2)

for task in ${tasks[@]};
do
  if [ $task == "catOG" ]; then
    elements=(6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25)
  elif [ $task == "elevator" ]; then
    elements=(15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34)
  elif [ $task == "robot" ] || [ $task == "task" ]; then
    elements=(3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22)
  else # order, trip, tripv2
    elements=(4 5 6 7 10 15 20 25 30 35 40 45 50 55 60)
  fi

  prefix="benchmarks/$task"


  for i in ${elements[@]};
  do
    if [ $task == "robot" ]; then
      owl="$prefix/original/TTL${i}.owl"
      input_domain="$prefix/original/robotDomain${i}.pddl"
    else
      owl=$prefix/original/TTL.owl
      input_domain=$prefix/original/domain.pddl
    fi
    input_problem="$prefix/original/${task}Problem${i}.pddl"

    result_domain="benchmarks/outputs/${task}_no_tseitin/domain_${i}.pddl"
    result_problem="benchmarks/outputs/${task}_no_tseitin/problem_${i}.pddl"
    tseitin_domain="benchmarks/outputs/${task}_tseitin/domain_${i}.pddl"
    tseitin_problem="benchmarks/outputs/${task}_tseitin/problem_${i}.pddl"

    python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --rls "$rls" --nmo "$nmo"$@

    python3 "$tseitin" "$result_domain" "$result_problem" -d "$tseitin_domain" -p "$tseitin_problem" --keep-name$@

    python3 "$parser" "$result_domain" "$result_problem"

    python3 "$parser" "$tseitin_domain" "$tseitin_problem"
  done
done
