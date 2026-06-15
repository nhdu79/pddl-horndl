#!/usr/bin/env/python

import os
import subprocess

from utils.helpers import parse_name

TEMPORARY_DATALOG_FILE = "__temp_clipper_datalog{0}.txt"
TEMPORARY_QUERY_FILE = "__temp_clipper_query{0}.cq"


class Clipper:
    def __init__(self, path, ontology_path, mqf=False, debug_mode=False):
        self.path = path
        self.ontology_path = ontology_path
        self.mqf = mqf
        self.debug_mode = debug_mode
        self.num_calls = 0

    def supports_simultaneous_rewriting(self):
        return self.mqf

    def rewrite_all(self, queries):
        assert self.supports_simultaneous_rewriting()
        qf = TEMPORARY_QUERY_FILE.format(self.num_calls)
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        with open(qf, "w") as f:
            f.write(queries)
            f.write("\n")
        subprocess.call(
            [self.path, "rewrite", "-cq", qf, "-mqf", "-d", df, self.ontology_path]
        )
        if not self.debug_mode:
            os.remove(qf)
        return self._read_datalog_file(df)

    def rewrite_ontology(self):
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        subprocess.call(
            [self.path, "rewrite", "-d", df, "-o", self.ontology_path]
        )
        return self._read_datalog_file(df)

    def rewrite_cq(self, cq):
        qf = TEMPORARY_QUERY_FILE.format(self.num_calls)
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        with open(qf, "w") as f:
            f.write(cq)
            f.write("\n")
        subprocess.call(
            [self.path, "rewrite", "-cq", qf, "-d", df, self.ontology_path]
        )
        if not self.debug_mode:
            os.remove(qf)
        return self._read_datalog_file(df, skip_until="rewritten queries")

    def adapt_predicate_name(self, predicate_name):
        return parse_name(predicate_name)

    def _read_datalog_file(self, df, skip_until=None):
        """Read a Clipper output file, strip comments, and split into rules.

        If skip_until is given, lines are discarded until one containing that
        substring is found; subsequent lines are then parsed normally.
        """
        rules = []
        try:
            with open(df) as f:
                lines = f.readlines()
            if skip_until is not None:
                for i, line in enumerate(lines):
                    if skip_until in line:
                        lines = lines[i + 1:]
                        break
            for line in lines:
                comment_pos = line.find("%")
                if comment_pos >= 0:
                    line = line[:comment_pos]
                line = line.strip()
                if line:
                    rules.append(line)
            if not self.debug_mode:
                os.remove(df)
        except FileNotFoundError:
            print(f"{df} does not exist")
        return "\n".join(rules).split(".")
