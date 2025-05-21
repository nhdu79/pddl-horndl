## Prerequisite:

The following software is required for running `generate_pddl.sh`, which generates the compiled PDDL files for the benchmarks:
- Patched version of Clipper (with `clipper.patch`)
- Nemo
- Fast Downward

## Installation Instructions:
#### Clipper:
* Clone the repo:
```sh
  $ git clone https://github.com/ghxiao/clipper
```
* Copy the `clipper.patch` in this repo to the Clipper repo (above)
* Apply the patches (2 patches need to be applied):
```sh
  $ git am --keep-cr --signoff < clipper.patch
  $ git am --keep-cr --signoff < support_multiple_queries_with_the_same_body.patch
```
* Within the Clipper repo, build from source:
```sh
  $ ./build.sh
```

#### Nemo:
* For the experiment, we used Nemo version 0.6.0.
* (From [Nemo](https://github.com/knowsys/nemo) repo): The fastest way to run Nemo is to use system-specific binaries of our command-line client. Archives with pre-compiled binaries for various platforms are available from the Nemo releases page
  - Download a precompiled binary from releases: https://github.com/knowsys/nemo/releases
  - Extract `tar -xvf [your-chosen-nemo-release].tar`
* There will be a binary `nmo` file in the extracted folder, whose path we will use in later in `run.sh`

#### Fast Downward:
* Detailed installation on [the official Webpage](https://www.fast-downward.org/latest/documentation/quick-start/)


## Running the compilation (`generate_pddl.sh`):

#### Configuring the corresponding paths in your system:
* The script in `generate_pddl.sh` requires the path to `clipper.sh` from the patched Clipper above, the path to a command-line client `nmo` for Nemo, and the path to `fast-downward.py` from the planner
  * For Clipper, the path is `/your_full_path_to_clipper/clipper/clipper-distribution/target/clipper/clipper.sh`
  * For Nemo, the path is `your_full_path_to_nemo/nmo`
  * Additionally, we use a parser from the PDDL Validator [VAL](https://github.com/KCL-Planning/VAL)
    - After installation, change the `parser` variable in the script to the path pointing to the VAL Parser file

#### Where are the written .pddl files?
* By default (in `generate_pddl.sh`), they are in `/benchmarks/outputs/[variant]/[corresponding-folder-name-of-benchmark]/`
  * If Tseitin transformation is turned on, then the file (domain/problem) will be in `[benchmark_name]_tseitin`
  * Otherwise, it will be in `[benchmark_name]_no_tseitin`

#### How do I run the planning benchmarks?
* Detailed instructions on the official Fast Downward webpage: https://www.fast-downward.org/latest/documentation/planner-usage/
    - Quick start:
    ``` shell
        fast-downward.py domain.pddl problem.pddl --search "lazy_greedy([ff()], preferred=[ff()])"
    ```

## The Benchmark folder:
* We keep the original .pddl files (domain + problem) from the work of Borgwardt et al. intact in their corresponding subfolders e.g. `benchmarks/robot`
* All outputs of our pipeline are stored in `benchmarks/outputs/`

## Mapping from Benchmark names in paper to folder names:

* Cats^* => catOG
* Elevator => elevator
* TPSA => order
* Robot^* => robot
* VTA => trip
* VTA-Roles => tripv2
* TaskAssign => task
