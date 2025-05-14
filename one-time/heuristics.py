def variable_name(variable):
    return "h" + variable

def variable_definition(variable, args):
    return f"{variable}({args})"

def expression(variable):
    return f"eager_greedy([{variable_name(variable)}],preferred=[{variable_name(variable)}])"

def build_arguments(heuristic):
    var = variable_name(heuristic["variable"])
    definition = variable_definition(heuristic["variable"], heuristic["args"])
    exp = expression(heuristic["variable"])
    return f'"let({var},{definition},{exp})"'

def result_domain(task, i):
    return f"benchmarks/outputs/{task}/domain_{i}.pddl"

def result_problem(task, i):
    return f"benchmarks/outputs/{task}/problem_{i}.pddl"

def compiled_domain(task, i):
    return f"benchmarks/outputs/{task}/compiled_domain_{i}.pddl"

def compiled_problem(task, i):
    return f"benchmarks/outputs/{task}/compiled_problem_{i}.pddl"

heuristics = [
    # {"variable": "cea", "args": "", "name": "cea"},
    {"variable": "cea", "args": "axioms=approximate_negative", "name": "cea_approximate_negative"},
    # {"variable": "ff", "args": "", "name": "hff"},
    # {"variable": "ff", "args": "axioms=approximate_negative", "name": "hff_approximate_negative"},
    # {"variable": "cg", "args": "", "name": "cg"},
    # {"variable": "cg", "args": "axioms=approximate_negative", "name": "cg_approximate_negative"},
]

# pddl = [("cat",17), ("elevator",22), ("task", 15), ("order", 5), ("order", 10), ("order", 15), ("trip", 5), ("trip", 10), ("trip", 15), ("tripv2",5), ("tripv2",10),("tripv2", 15), ("robot", 10), ("robot", 11), ("robot", 12)]

pddl = [
    # ("cat",18), ("cat",19), ("cat",20),
    ("catOG",15), ("catOG",16), ("catOG",17),
    # ("elevator",20), ("elevator",21),
    # ("task",13), ("task",14)
]

if __name__ == "__main__":
    import os
    import time
    fastdownward="/home/zinzin2312/repos/downward/fast-downward.py"
    file="csvs/heuristics_test.csv"

    timeouts = []

    for h in heuristics:
        arg = build_arguments(h)
        for i in range(3):
            for tsk in pddl:
                task, nr = tsk[0], tsk[1]
                dom = result_domain(task, nr)
                prob = result_problem(task, nr)
                start = time.time()
                command = f"timeout 50 {fastdownward} {dom} {prob} --search {arg}"
                if command in timeouts:
                    with open(file, 'a') as f:
                        f.write(f"{h['name']},{dom},50\n")
                    continue

                os.system(command)
                end = time.time()
                elapsed = end - start
                elapsed = round(elapsed, 2)
                if elapsed >= 50:
                    timeouts.append(command)
                with open(file, 'a') as f:
                    f.write(f"{h['name']},{dom},{elapsed}\n")

        for i in range(3):
            for tsk in pddl:
                task, nr = tsk[0], tsk[1]
                com_d = compiled_domain(task, nr)
                com_p = compiled_problem(task, nr)
                start = time.time()
                command = f"timeout 50 {fastdownward} {com_d} {com_p} --search '{arg}'"
                if command in timeouts:
                    # write timeout
                    with open(file, 'a') as f:
                        f.write(f"{h['name']},{com_d},50\n")
                    continue

                os.system(command)
                end = time.time()
                elapsed = end - start
                elapsed = round(elapsed, 2)
                if elapsed >= 50:
                    timeouts.append(command)
                with open(file, 'a') as f:
                    f.write(f"{h['name']},{com_d},{elapsed}\n")
