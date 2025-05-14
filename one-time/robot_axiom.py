import os
import re
import subprocess

rls_file_path = "code/nemo/fact_counter.rls"
nmo="/home/zinzin2312/repos/nemo/target/release/nmo"
ontology_folder = "/home/zinzin2312/repos/pddl-horndl/benchmarks/robot/original/"

for i in range(3, 23):
    ontology_file_path = os.path.join(ontology_folder, f"TTL{i}.owl")
    with open(rls_file_path, 'r') as f:
        rls = f.read()
        rls = re.sub(r'::DATA_IMPORT_PATH', ontology_file_path, rls)
    with open(rls_file_path, 'w') as f:
        f.write(rls)

    subprocess.call([nmo, rls_file_path])
    with open(rls_file_path, 'r') as f:
        rls = f.read()
        rls = re.sub(ontology_file_path, "::DATA_IMPORT_PATH", rls)
    with open(rls_file_path, 'w') as f:
        f.write(rls)
