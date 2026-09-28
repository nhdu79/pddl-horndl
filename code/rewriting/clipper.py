#!/usr/bin/env/python

import os
import re
import subprocess


TEMPORARY_DATALOG_FILE = "__temp_clipper_datalog{0}.txt"
TEMPORARY_QUERY_FILE = "__temp_clipper_query{0}.cq"

# Clipper exits with code 0 on some failures (e.g. an unparsable ontology) and
# only prints a Java stack trace, so stderr is scanned for exception lines too.
_JAVA_EXCEPTION = re.compile(r"^[\w.$]+(Exception|Error)\b", re.MULTILINE)


class ClipperError(RuntimeError):
    pass


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
        try:
            self._run(["rewrite", "-cq", qf, "-mqf", "-d", df, self.ontology_path], df)
        finally:
            if not self.debug_mode:
                os.remove(qf)
        return self._read_datalog_file(df)

    def rewrite_ontology(self):
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        self._run(["rewrite", "-d", df, "-o", self.ontology_path], df)
        return self._read_datalog_file(df)

    def rewrite_cq(self, cq):
        qf = TEMPORARY_QUERY_FILE.format(self.num_calls)
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        with open(qf, "w") as f:
            f.write(cq)
            f.write("\n")
        try:
            self._run(["rewrite", "-cq", qf, "-d", df, self.ontology_path], df)
        finally:
            if not self.debug_mode:
                os.remove(qf)
        return self._read_datalog_file(df, skip_until="rewritten queries")

    def _run(self, args, df):
        """Run Clipper and raise ClipperError if it did not produce rules.

        Clipper's (verbose) log output is captured and only shown on failure,
        unless debug mode is on, in which case it goes straight to the terminal.
        """
        cmd = [self.path, *args]
        if os.path.exists(df):
            os.remove(df)  # a stale file must not mask a failed run
        result = subprocess.run(cmd, capture_output=not self.debug_mode, text=True)
        stderr = result.stderr or ""
        problem = None
        if result.returncode != 0:
            problem = f"exited with code {result.returncode}"
        elif _JAVA_EXCEPTION.search(stderr):
            problem = "reported an exception"
        elif not os.path.exists(df):
            problem = f"did not write its output file {df!r}"
        if problem is not None:
            if not self.debug_mode and os.path.exists(df):
                os.remove(df)
            details = "\n".join(stderr.strip().splitlines()[:20])
            raise ClipperError(
                f"Clipper {problem}.\nCommand: {' '.join(cmd)}"
                + (f"\nstderr (first lines):\n{details}" if details else "")
            )

    def _read_datalog_file(self, df, skip_until=None):
        """Read a Clipper output file, strip comments, and split into rules.

        If skip_until is given, lines are discarded until one containing that
        substring is found; subsequent lines are then parsed normally.
        """
        rules = []
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
        return "\n".join(rules).split(".")
