## Prerequisite:

The following software is required for a complete run of the pipeline written in `run.sh`:
- Patched version of Clipper (with `clipper.patch`) 
- Nemo
- Fastdownward

### Installation Intructions:
#### Clipper:
* Clone the repo:
```sh
  $ git clone https://github.com/ghxiao/clipper
``` 
* Copy the `clipper.patch` in this repo to the Clipper repo (above)
* Apply the patch:
```sh
  $ git am --keep-cr --signoff < clipper.patch
```
* Within the Clipper repo, build from source:
```sh
  $ ./build.sh
```


#### Nemo:
* At the time of writing, we used Nemo version 0.5.2-dev. Though this version is retracted, in principle, later versions of Nemo should also work
* (From [Nemo](https://github.com/knowsys/nemo]) repo): The fastest way to run Nemo is to use system-specific binaries of our command-line client. Archives with pre-compiled binaries for various platforms are available from the Nemo releases page
  - Download a precompiled binary from releases: https://github.com/knowsys/nemo/releases
  - Extract `tar -xvf [your-chosen-nemo-release].tar`
* There will be a binary `nmo` file in the extracted folder, whose path we will use in later in `run.sh` 


#### Fastdownward:
* Detailed installation on webpage: https://www.fast-downward.org/latest/documentation/quick-start/


### Running the pipeline (`run.sh`):

#### Appending the corresponding in your system:
* The script in `run.sh` requires path `clipper.sh` to the patched Clipper above, path to a command-line client `nmo` for Nemo, and path to `fast-downward.py` for Fastdownward
  * For Clipper, the path is `/your_full_path_to_clipper/clipper/clipper-distribution/target/clipper/clipper.sh`
  * For nmo, the path is `your_full_path_to_nemo/nmo`
  * For Fastdownward, the path is `your_full_path_to_fastdownward/downward/fast-downward.py`
* In `run.sh`, change the variables in line 43 (clipper), 44 (nmo), and 46 (fastdownward) to the above corresponding paths 

#### Before running the script:
* `run.sh` has uses 4 variables defined in lines 1-4 for a quicker run of the pipeline
  * `keep_pddl` tells the script to write the corresponding .pddl files in `/benchmarks/outputs/` (value 1) or not (value 0)
  * `updates=(1)` tells the script to run the benchmarks with the coherence update semantics (for both use `updates=(0 1)`)
  * `tseitin=(1)` is similar to `updates=(1)`, which runs the Tseitin transformation after compiling the domain/problem files.
  * `mode="cea_negative"` tells the script which heuristic to run Fastdownward with, supported ones are: cea/cea_negative/ff/ff_negative

#### Where are the written .pddl files?
* By default (in `run.sh`), they are in `/benchmarks/outputs/[corresponding-folder-name-of-benchmark]/`
  * If Tseitin transformation is turned on, then the file (domain/problem) names will be `compiled_*.pddl`
  * Otherwise, it will only be `domain_[benchmark-instance].pddl` or `problem_[benchmark-instance].pddl`

### Mapping from Benchmark names in Thesis to folder names:

* Cats => cat
* Elevator => elevator
* TPSA => order
* Robot => robot (No result yet)
* VTA => trip
* VTA-Roles => tripv2
* TaskAssign => task
