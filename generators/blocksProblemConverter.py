import os
import re

def transform_content(text):
    parts = text.split(':goal', 1)
    if len(parts) != 2:
        raise "No goal specification!"
    before, after = parts[0], parts[1]
    before = re.sub(r'\(:objects ', r'(:objects T ', before)
    before = re.sub(r' \(CLEAR [A-Za-z]+\)', '', before)
    before = re.sub(r' \(HANDEMPTY\)', '', before)
    before = re.sub(r'\(ON ([A-Za-z]+) ([A-Za-z]+)\)', r'(ONBLOCK \1 \2)', before)
    before = re.sub(r'\(ONTABLE ([A-Za-z]+)\)', r'(ONTABLE \1 T)', before)
    after = re.sub(r'\(ON ([A-Za-z]+) ([A-Za-z]+)\)', r'(MKO (ON \1 \2))', after)
    return before + ':goal' + after

def process_pddl_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith('.pddl'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            with open(input_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
            transformed = transform_content(content)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                outfile.write(transformed)
            print(f"Processed: {filename}")

if __name__ == "__main__":
  process_pddl_files("benchmarks/blocks/original/original_ppdl/", "benchmarks/blocks/original/")
