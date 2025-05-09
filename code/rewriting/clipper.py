#!/usr/bin/env/python

import os
import subprocess

from utils.functions import parse_name

TEMPORARY_DATALOG_FILE = "__temp_clipper_datalog{0}.txt"
TEMPORARY_QUERY_FILE = "__temp_clipper_query{0}.cq"

class Clipper:
    def __init__(self, path, ontology_path, mqf = False, debug_mode = False):
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
                # , stderr=subprocess.PIPE
        ) # stdout=subprocess.PIPE
        if not self.debug_mode:
            os.remove(qf)
        ontology = []
        try:
            with open(df) as f:
                #ontology = []
                for l in f.readlines():
                    i = l.find("%")
                    if i >= 0:
                         l = l[:i]
                    l = l.strip()
                    if len(l) > 0:
                        ontology.append(l)
                ontology = "\n".join(ontology).split(".")
            if not self.debug_mode:
                os.remove(df)
        except FileNotFoundError:
            print('{0} does not exist'.format(df))
        return ontology

    def rewrite_ontology(self):
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        subprocess.call(
                [self.path, "rewrite", "-d", df, "-o", self.ontology_path]
                # stderr=subprocess.PIPE,
                # stdout=subprocess.PIPE
        )
        ontology = []
        try:
            with open(df) as f:
                for l in f.readlines():
                    i = l.find("%")
                    if i >= 0:
                        l = l[:i]
                    l = l.strip()
                    if len(l) > 0:
                        ontology.append(l)
                ontology = "\n".join(ontology).split(".")
            if not self.debug_mode:
                os.remove(df)
        except FileNotFoundError:
            print('{0} does not exist'.format(df))
        return ontology

    def rewrite_cq(self, cq):
        qf = TEMPORARY_QUERY_FILE.format(self.num_calls)
        df = TEMPORARY_DATALOG_FILE.format(self.num_calls)
        self.num_calls += 1
        with open(qf, "w") as f:
            f.write(cq)
            f.write("\n")
        subprocess.call(
                [self.path, "rewrite", "-cq", qf, "-d", df, self.ontology_path]
                # , stderr=subprocess.PIPE
        ) # stdout=subprocess.PIPE
        if not self.debug_mode:
            os.remove(qf)
        ontology = []
        try:
            with open(df) as f:
                for l in f:
                    if "rewritten queries" in l:
                        break
                    #ontology = []
                for l in f:
                    i = l.find("%")
                    if i >= 0:
                        l = l[:i]
                    l = l.strip()
                    if len(l) > 0:
                        ontology.append(l)
                ontology = "\n".join(ontology).split(".")
            if not self.debug_mode:
                os.remove(df)
        except FileNotFoundError:
            print('{0} does not exist'.format(df))
        return ontology

    def adapt_predicate_name(self, predicate_name):
        return parse_name(predicate_name)
        # return re.sub(r"[^a-zA-Z0-9]", "", predicate_name.lower())

