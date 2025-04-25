log_folder="logs"
pddl_parser="/home/zinzin2312/repos/validator/linux64/Val-20211204.1-Linux/bin/Parser"

if __name__ == "__main__":
    import sys
    import subprocess
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("domain")
    parser.add_argument("problem")

    if len(sys.argv) < 3:
        print("Usage: python parser_wrapper.py <domain> <problem>")
        sys.exit(1)

    domain = parser.parse_args().domain
    problem = parser.parse_args().problem

    # run the pddl parser and read the output
    process = subprocess.Popen(
        [pddl_parser, domain, problem],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    errors = []
    for line in stdout.splitlines():
        if line.startswith("Errors: 0"):
            continue
        if "Error" in line or "error" in line:
            errors.append(line)

    print("\n")
    print("\n")
    print("\033[93m" + " =============================== PARSER OUTPUT ====================================" + "\033[0m")
    with open(log_folder + "/parser_output.log", "a") as f:
        timestamp = subprocess.check_output("date", shell=True).decode().strip()
        f.write(timestamp + "\n")
        f.write("File: " + domain + " and " + problem + "\n")
        print("File: " + domain + " and " + problem)
        if len(errors) == 0:
            f.write("No errors found!")
            print("\033[92m" + "No errors found!" + "\033[0m")
        else:
            for error in errors:
                print("\033[91m" + error + "\033[0m")
                f.write(error+"\n")
        f.write("\n")

    print("\033[93m" + " =============================== END OF OUTPUT ====================================" + "\033[0m")
