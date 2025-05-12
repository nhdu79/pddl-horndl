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
tseitin="code/rewriting/new_tseitin.py"
rls="code/nemo/t_closure.rls"
parser="code/utils/parser_wrapper.py"

variants=(var0 var1 var2 var3)
tasks=(blocks catOG elevator robot task order trip tripv2)

for variant in ${variants[@]};
do
  if [ $variant == "var0" ]; then
    updating_pred_type="derived_predicate"
    incompatible_update_pred_type="incompatible_update"
  elif [ $variant == "var1" ]; then
    updating_pred_type="action_effect"
    incompatible_update_pred_type="compatible_update"
  elif [ $variant == "var2" ]; then
    updating_pred_type="derived_predicate"
    incompatible_update_pred_type="compatible_update"
  else # var3
    updating_pred_type="action_effect"
    incompatible_update_pred_type="incompatible_update"
  fi

  for task in ${tasks[@]};
  do
    if [ $task == "catOG" ]; then
      elements=(6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25)
    elif [ $task == "elevator" ]; then
      elements=(15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34)
    elif [ $task == "robot" ] || [ $task == "task" ]; then
      elements=(3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22)
    elif [ $task == "blocks" ]; then
      elements=("-6-2" "-10-2" "-16-1" "-13-1" "-11-0" "-7-2" "-9-0" "-5-0" "-8-0" "-7-1" "-17-0" "-14-0" "-6-0" "-16-2" "-5-1" "-15-0" "-8-1" "-14-1" "-6-1" "-5-2" "-10-1" "-15-1" "-11-1" "-4-1" "-7-0" "-8-2" "-4-2" "-12-0" "-13-0" "-4-0" "-12-1" "-10-0" "-11-2" "-9-2" "-9-1")
    else # order, trip, tripv2
      elements=(4 5 6 7 10 15 20 25 30 35 40 45 50 55 60)
    fi

    prefix="benchmarks/$task"

    for i in ${elements[@]};
    do
      if [ $task == "robot" ]; then
        owl="$prefix/original/TTL${i}.owl"
        input_domain="$prefix/original/robotDomain${i}.pddl"
      elif [ $task == "blocks" ]; then
        owl="$prefix/original/blocks.owl"
        input_domain=$prefix/original/domain.pddl
      else
        owl=$prefix/original/TTL.owl
        input_domain=$prefix/original/domain.pddl
      fi

      if [ $task == "blocks" ]; then
        input_problem="$prefix/original/probBLOCKS${i}.pddl"
      else
        input_problem="$prefix/original/${task}Problem${i}.pddl"
      fi

      result_domain="benchmarks/outputs/${variant}/${task}_no_tseitin/domain_${i}.pddl"
      result_problem="benchmarks/outputs/${variant}/${task}_no_tseitin/problem_${i}.pddl"
      tseitin_domain="benchmarks/outputs/${variant}/${task}_tseitin/domain_${i}.pddl"
      tseitin_problem="benchmarks/outputs/${variant}/${task}_tseitin/problem_${i}.pddl"

      PYTHONPATH=code python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --rls "$rls" --nmo "$nmo" --updating-pred-type "$updating_pred_type" --incompatible-update-pred-type "$incompatible_update_pred_type"$@

      PYTHONPATH=code python3 "$tseitin" "$result_domain" "$result_problem" -d "$tseitin_domain" -p "$tseitin_problem" --keep-name$@

      python3 "$parser" "$result_domain" "$result_problem"

      python3 "$parser" "$tseitin_domain" "$tseitin_problem"
    done
  done
done
