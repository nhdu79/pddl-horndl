#!/bin/sh
clipper="/home/zinzin2312/repos/clipper/clipper-distribution/target/clipper/clipper.sh"
nmo="/home/zinzin2312/repos/nemo/nmo"
fastdownward="/home/zinzin2312/repos/downward/fast-downward.py"
rls="/home/zinzin2312/repos/pddl-horndl/code/nemo/t_star.rls"

rm -rf tmp/
$nmo $rls --export all --export-dir tmp/
