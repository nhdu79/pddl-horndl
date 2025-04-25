#!/bin/bash

branches=("main" "update_v2" "update_v3" "update_v4")
eval_script="./generate_pddl.sh"

# Save current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

for branch in "${branches[@]}"; do
    echo "Checking out branch: $branch"
    git checkout "$branch" || { echo "Failed to checkout $branch"; exit 1; }

    echo "Running evaluation on $branch..."
    bash "$eval_script"

    echo "Done with $branch"
    echo "----------------------------------"
done

# Return to original branch
git checkout "$current_branch"

