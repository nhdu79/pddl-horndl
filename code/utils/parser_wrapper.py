import argparse
import os
import subprocess

from utils.tools import require_tool

LOG_FOLDER = "logs"


def validate_pddl(domain: str, problem: str, parser_path: str | None = None) -> None:
    """Run VAL's Parser on domain/problem; parser_path defaults to tools.toml, then PATH."""
    parser_path = require_tool("val", parser_path)
    process = subprocess.Popen(
        [parser_path, domain, problem],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, _ = process.communicate()

    errors = [
        line for line in stdout.splitlines()
        if ("Error" in line or "error" in line) and not line.startswith("Errors: 0")
    ]

    timestamp = subprocess.check_output("date", shell=True).decode().strip()
    # print("\n\033[93m =============================== PARSER OUTPUT ====================================\033[0m")
    print(f"File: {domain} and {problem}")
    if errors:
        for error in errors:
            print("\033[91m" + error + "\033[0m")
    else:
        print("\033[92mNo errors found!\033[0m")
    # print("\033[93m =============================== END OF OUTPUT ====================================\033[0m")

    os.makedirs(LOG_FOLDER, exist_ok=True)
    with open(f"{LOG_FOLDER}/parser_output.log", "a") as f:
        f.write(f"{timestamp}\n")
        f.write(f"File: {domain} and {problem}\n")
        f.write("\n".join(errors) if errors else "No errors found!")
        f.write("\n")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("domain")
    arg_parser.add_argument("problem")
    arg_parser.add_argument(
        "--parser", default=None, help="VAL Parser binary (default: tools.toml, then PATH)"
    )
    args = arg_parser.parse_args()
    validate_pddl(args.domain, args.problem, args.parser)
