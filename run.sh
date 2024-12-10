keep_pddl=0
updates=(1)
tseitins=(0 1)
mode="cea"
# supported: cea/cea_negative/ff

for do_update in ${updates[@]};
do
  for do_tseitin in ${tseitins[@]};
  do
    csv="csvs/update${do_update}_tseitin${do_tseitin}_${mode}.csv"
    rm -rf $csv
    if [ $do_update -eq 1 ]; then
      if [ $do_tseitin -eq 1 ]; then
        echo "benchmark name,t closure,domain extension,collecting queries,rewriting,update rules const,gen derived preds,finalize,total complation,tseitin transformation, solution, size(KB)" >> $csv
      else
        echo "benchmark name,t closure,domain extension,collecting queries,rewriting,update rules const,gen derived preds,finalize,total complation, solution, size(KB)" >> $csv
      fi
    else
      if [ $do_tseitin -eq 1 ]; then
        echo "benchmark name,collecting queries,rewriting,gen derived preds,finalize,total complation,tseitin transformation, solution, size(KB)" >> $csv
      else
        echo "benchmark name,collecting queries,rewriting,gen derived preds,finalize,total complation, solution, size(KB)" >> $csv
      fi
    fi

    tasks=(cat elevator task order trip tripv2 robot)
    # tasks=(cat)
    for task in ${tasks[@]};
    do
      if [ $task == "cat" ]; then
        elements=(17)
      elif [ $task == "elevator" ]; then
        elements=(22)
      elif [ $task == "robot" ] || [ $task == "task" ]; then
        elements=(15)
      else # order, trip, tripv2
        elements=(15 5 10)
      fi

      prefix="benchmarks/$task"
      ## path to a (patched) clipper
      clipper="/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
      nmo="/home/zinzin2312/repos/nemo/target/release/nmo"
      rls="code/nemo/t_closure.rls"
      fastdownward="/home/zinzin2312/repos/downward/fast-downward.py"
      # path to compiler.py
      compiler="code/compiler.py"
      tseitin="code/tseitin.py"

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
        # With update semantics
        if [ $do_update -eq 1 ]; then
          result_domain="benchmarks/outputs/$task/domain_${i}.pddl"
          result_problem="benchmarks/outputs/$task/problem_${i}.pddl"
          tseitin_domain="benchmarks/outputs/$task/compiled_domain_${i}.pddl"
          tseitin_problem="benchmarks/outputs/$task/compiled_problem_${i}.pddl"

          # echo "Compiling dom & prob $i with update"
          python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --rls "$rls" --nmo "$nmo" --output-csv "$csv" --benchmark-name "$task $i"$@

          if [ $do_tseitin -eq 1 ]; then
            python3 "$tseitin" "$result_domain" "$result_problem" -d "$tseitin_domain" -p "$tseitin_problem" --keep-name  --keep-name --output-csv "$csv" --benchmark-name "$task $i"$@
            output_domain="$tseitin_domain"
            output_problem="$tseitin_problem"
          else
            output_domain="$result_domain"
            output_problem="$result_problem"
          fi
        else
          result_domain="$prefix/pddl/domain_${i}.pddl"
          result_problem="$prefix/pddl/problem_${i}.pddl"
          tseitin_domain="$prefix/pddl/compiled_domain_${i}.pddl"
          tseitin_problem="$prefix/pddl/compiled_problem_${i}.pddl"

          # echo "Compiling dom & prob $i"
          python3 "$compiler" "$owl" "$input_domain" "$input_problem" -d "$result_domain" -p "$result_problem" --clipper "$clipper" --clipper-mqf  --output-csv "$csv" --benchmark-name "$task $i"$@

          if [ $do_tseitin -eq 1 ]; then
            python3 "$tseitin" "$result_domain" "$result_problem" -d "$tseitin_domain" -p "$tseitin_problem" --keep-name --output-csv "$csv" --benchmark-name "$task $i"$@
            output_domain="$tseitin_domain"
            output_problem="$tseitin_problem"
          else
            output_domain="$result_domain"
            output_problem="$result_problem"
          fi
        fi

        echo "========================== Solving $task $i with $mode heuristic; do_update=$do_update; do_tseitin=$do_tseitin; keep_pddl=$keep_pddl =========================="

        if [ $mode == "cea" ]; then
          planner_output=$(timeout 600 $fastdownward $output_domain $output_problem --search "let(hcea,cea(),lazy_greedy([hcea],preferred=[hcea]))">&1)
        elif [ $mode == "ff" ]; then
          planner_output=$(timeout 600 $fastdownward $output_domain $output_problem --search "let(hff,ff(),lazy_greedy([hff],preferred=[hff]))">&1)
        elif [ $mode == "cea_negative" ]; then
          planner_output=$(timeout 600 $fastdownward $output_domain $output_problem --search "let(hcea,cea(axioms=approximate_negative),lazy_greedy([hcea],preferred=[hcea]))">&1)
        else
          planner_output=$(timeout 600 $fastdownward $output_domain $output_problem --search "let(hcea,cea(),lazy_greedy([hcea],preferred=[hcea]))">&1)
        fi
        python helpers.py --output "$planner_output" --csv "$csv"

        echo "" >> $csv

        if [ $keep_pddl -eq 0 ]; then
          rm -rf $result_domain
          rm -rf $result_problem
          rm -rf $tseitin_domain
          rm -rf $tseitin_problem
        fi
      done
    done
  done
done

rm -rf __temp_clipper_*
rm -rf sas_plan
rm -rf sas_plan.*
