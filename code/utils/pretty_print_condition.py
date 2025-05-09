#!/usr/bin/env python

import argparse

import planning.pddl as pddl

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    args = p.parse_args()
    with open(args.path) as f:
        tok = pddl.TokenList(f.read())
    cond = pddl.parse_condition(tok)
    print(cond.pretty_str())
