"""Regression tests for compilation fixes (types, constants, requirements,
rule filtering, determinism, Clipper errors, tool lookup)."""

import os
import stat

import pytest

import pddl.datalog as datalog
import pddl.parser as pddl
from compilation.datalog import _filter_irrelevant_rules, _parse_datalog_rules
from compilation.domain_transforms import (
    _construct_effects_for_update_action_core,
    ensure_requirements,
    merge_problem_objects_into_constants,
)
from compilation.query_rewriter import prepare_queries
from rewriting.clipper import Clipper, ClipperError
from utils import tools

_TYPED_DOMAIN = """
(define (domain d)
(:requirements :typing)
(:types block surface - object)
(:constants floor - surface)
(:predicates (on ?x - block ?y - surface) (clear ?x))
(:action put
  :parameters (?x - block ?y - surface)
  :precondition (and (clear ?x) (not (on ?x ?y)))
  :effect (and (on ?x ?y) (forall (?z) (when (on ?z ?y) (not (clear ?z))))))
)
"""

_PROBLEM = """
(define (problem p)
(:domain d)
(:objects a b - block floor t - surface c)
(:init (clear a))
(:goal (exists (?x) (on ?x t)))
)
"""


# --- types -------------------------------------------------------------------


def test_untyped_lists_print_without_object_type():
    domain = pddl.parse_domain(
        "(define (domain d) (:predicates (p ?x ?y))"
        " (:action a :parameters (?x) :precondition (p ?x ?x) :effect (p ?x ?x)))"
    )
    text = str(domain)
    assert "object" not in text
    assert "(p ?x ?y)" in text


def test_typed_domain_keeps_types():
    text = str(pddl.parse_domain(_TYPED_DOMAIN))
    assert "block surface - object" in text
    assert "(on ?x - block ?y - surface)" in text
    assert "floor - surface" in text


def test_predicate_arity_counts_all_typed_groups():
    domain = pddl.parse_domain(_TYPED_DOMAIN)
    on = next(p for p in domain.predicates if p.name == "on")
    assert len(on.parameters) == 2  # two TypedLists ...
    assert on.arity() == 2  # ... but also arity 2
    assert on.variables() == ["?x", "?y"]


def test_core_update_effects_use_all_parameters_of_typed_predicates():
    domain = pddl.parse_domain(_TYPED_DOMAIN)
    on = next(p for p in domain.predicates if p.name == "on")
    effects = _construct_effects_for_update_action_core([on], [])
    assert all(str(e).startswith("(forall (?x ?y)") for e in effects)


def test_typed_existential_in_mko_query_is_rejected():
    domain = pddl.parse_domain(
        "(define (domain d) (:types t) (:predicates (p ?x))"
        " (:action a :parameters () :precondition (mko (exists (?x - t) (p ?x)))"
        " :effect (p c)))"
    )
    ucq = domain.actions[0].precondition.ucq
    with pytest.raises(NotImplementedError, match="Typed variables"):
        prepare_queries([ucq])


# --- constants ---------------------------------------------------------------


def test_problem_objects_are_merged_into_existing_constants():
    domain = pddl.parse_domain(_TYPED_DOMAIN)
    problem = pddl.parse_problem(_PROBLEM)
    merge_problem_objects_into_constants(domain, problem)
    constants = {(x, tl.type) for tl in domain.constants for x in tl.elements}
    assert constants == {
        ("floor", "surface"),  # declared in the domain, kept once
        ("a", "block"),
        ("b", "block"),
        ("t", "surface"),
        ("c", None),
    }
    assert problem.objects is None


# --- requirements ------------------------------------------------------------


def test_requirements_are_inferred_from_the_compiled_domain():
    domain = pddl.parse_domain(_TYPED_DOMAIN)
    problem = pddl.parse_problem(_PROBLEM)
    domain.derived_predicates.append(
        pddl.DerivedPredicate(
            pddl.Predicate("q", []),
            pddl.Or([pddl.Fact("clear", ["floor"]), pddl.Truth()]),
        )
    )
    ensure_requirements(domain, problem)
    assert domain.requirements == [
        ":typing",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":existential-preconditions",  # from the goal
        ":conditional-effects",
        ":derived-predicates",
    ]


def test_requirements_implied_by_adl_are_not_repeated():
    domain = pddl.parse_domain(_TYPED_DOMAIN.replace(":typing", ":adl"))
    ensure_requirements(domain)
    assert domain.requirements == [":adl"]


# --- datalog rules -----------------------------------------------------------


def _rules(*texts):
    return [datalog.parse_rule(t) for t in texts]


def test_parse_datalog_rules_is_order_preserving_and_deduplicating():
    raw = ["b(X) :- c(X)", "a(X) :- b(X)", "b(X) :- c(X)", "z(X) :- y(X)"]
    rules, duplicates = _parse_datalog_rules(raw, set(), None, True, False)
    assert [r.head.name for r in rules] == ["b", "a", "z"]
    assert [r.head.name for r in duplicates] == ["b"]


def test_filter_irrelevant_rules_drops_rules_nobody_reads():
    rules = _rules(
        "QUERY0(X) :- b(X)",
        "b(X) :- c(X)",
        "unused(X) :- b(X)",  # head never read -> irrelevant
        "d(X) :- unused(X)",  # only feeds an irrelevant rule -> irrelevant
        "c(X) :- e(X)",  # needed transitively via b
    )
    relevant, irrelevant = _filter_irrelevant_rules(rules, set(), 1, None)
    assert [r.head.name for r in relevant] == ["QUERY0", "b", "c"]
    assert [r.head.name for r in irrelevant] == ["unused", "d"]


def test_filter_irrelevant_rules_is_independent_of_rule_order():
    # c is only discovered to be needed after its rule was first visited.
    rules = _rules("c(X) :- e(X)", "b(X) :- c(X)", "QUERY0(X) :- b(X)")
    relevant, irrelevant = _filter_irrelevant_rules(rules, set(), 1, None)
    assert len(relevant) == 3 and not irrelevant


# --- Clipper -----------------------------------------------------------------


def _fake_clipper(tmp_path, script):
    path = tmp_path / "clipper.sh"
    path.write_text("#!/bin/sh\n" + script)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def test_clipper_nonzero_exit_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    clipper = Clipper(_fake_clipper(tmp_path, "echo boom >&2; exit 3\n"), "x.owl", True)
    with pytest.raises(ClipperError, match="exited with code 3"):
        clipper.rewrite_all("Q(?0) <- A(?0)")
    assert os.listdir(tmp_path) == ["clipper.sh"]  # temp files cleaned up


def test_clipper_exception_with_exit_code_zero_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Mimics an unparsable ontology: stack trace on stderr, exit 0, output written.
    script = (
        'echo "org.semanticweb.owlapi.io.UnparsableOntologyException: bad" >&2\n'
        'touch __temp_clipper_datalog0.txt\n'
    )
    clipper = Clipper(_fake_clipper(tmp_path, script), "x.owl", True)
    with pytest.raises(ClipperError, match="reported an exception"):
        clipper.rewrite_all("Q(?0) <- A(?0)")


def test_clipper_missing_output_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "__temp_clipper_datalog0.txt").write_text("stale(X) :- old(X).\n")
    clipper = Clipper(_fake_clipper(tmp_path, "exit 0\n"), "x.owl", True)
    with pytest.raises(ClipperError, match="did not write"):
        clipper.rewrite_all("Q(?0) <- A(?0)")


# --- tool lookup -------------------------------------------------------------


def test_tool_lookup_priority(tmp_path, monkeypatch):
    cli = tmp_path / "cli_clipper.sh"
    conf = tmp_path / "conf_clipper.sh"
    on_path = tmp_path / "bin" / "clipper.sh"
    on_path.parent.mkdir()
    for p in (cli, conf, on_path):
        p.write_text("#!/bin/sh\n")
        p.chmod(0o755)
    config_file = tmp_path / "tools.toml"
    config_file.write_text(f'[tools]\nclipper = "{conf}"\n')
    monkeypatch.setenv("PATH", str(on_path.parent))

    config = tools.load_config(config_file)
    assert tools.find_tool("clipper", str(cli), config) == str(cli)
    assert tools.find_tool("clipper", None, config) == str(conf)
    assert tools.find_tool("clipper", None, {}) == str(on_path)
    assert tools.find_tool("nmo", None, {}) is None


def test_tool_lookup_rejects_missing_explicit_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        tools.find_tool("clipper", str(tmp_path / "nope"), {})
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        tools.load_config(tmp_path / "missing.toml")


def test_tool_config_rejects_unknown_keys(tmp_path):
    config_file = tmp_path / "tools.toml"
    config_file.write_text('[tools]\nclippr = "/x"\n')
    with pytest.raises(ValueError, match="clippr"):
        tools.load_config(config_file)


# --- names -------------------------------------------------------------------

from compilation.names import (  # noqa: E402
    NameClashError,
    OntologyNames,
    check_names,
    declare_for_clipper,
)
from compilation.naming import get_query_id, is_coherence_update_predicate_name  # noqa: E402
from utils.helpers import normalize_user_name  # noqa: E402

_ONTO = """\
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://t.org/o> rdf:type owl:Ontology .
<http://t.org/o#Invoice> rdf:type owl:Class .
<http://t.org/o#onBlock> rdf:type owl:ObjectProperty .
"""


def _task(domain_text, problem_text="(define (problem p) (:domain d) (:init) (:goal (and)))"):
    return (
        pddl.parse_domain(domain_text, preserve_predicate_names=True),
        pddl.parse_problem(problem_text),
    )


def _names(tmp_path, extra=""):
    path = tmp_path / "o.owl"
    path.write_text(_ONTO + extra)
    return OntologyNames(str(path))


def test_normalize_user_name():
    assert normalize_user_name("on_Block-2") == "onblock2"


def test_user_names_are_never_update_predicates():
    for name in ("invoice", "inventory", "existsfoo", "delivery", "insurance"):
        assert not is_coherence_update_predicate_name(name)
    for name in ("ins_x", "Ap_x", "DelCl_x", "PreInsCl_a_sub_b", "updating"):
        assert is_coherence_update_predicate_name(name)


def test_get_query_id_is_exact():
    assert get_query_id("QUERY12") == 12
    assert get_query_id("queryresult") is None  # used to crash int()
    assert get_query_id("query3") is None


def test_ontology_names_give_exact_clipper_spelling(tmp_path):
    names = _names(tmp_path)
    assert names.clipper_spelling("invoice") == "Invoice"
    assert names.clipper_spelling("onblock") == "onBlock"
    assert names.clipper_spelling("sticky") is None
    assert names.roles == {"onblock"}


def test_declare_for_clipper_adds_parseable_declarations(tmp_path):
    source = tmp_path / "o.owl"
    source.write_text(_ONTO)
    out = declare_for_clipper(str(source), {"sticky": 1, "near": 2}, str(tmp_path / "decl.owl"))
    declared = OntologyNames(out)  # also proves the result is valid Turtle
    assert {"sticky", "near", "invoice", "onblock"} <= set(declared.raw)
    assert declared.roles == {"onblock", "near"}


def test_check_names_accepts_case_variants(tmp_path):
    domain, problem = _task(
        "(define (domain d) (:predicates (Invoice ?x) (ONBLOCK ?x ?y)) "
        "(:action a :parameters (?x) :precondition (invoice ?x) :effect (onBlock ?x ?x)))"
    )
    check_names(domain, problem, _names(tmp_path), coherence_update=True, horn=True)


def test_check_names_rejects_lossy_merges(tmp_path):
    domain, problem = _task(
        "(define (domain d) (:predicates (onBlock ?x ?y)) "
        "(:action a :parameters (?x) :precondition (and) :effect (on_block ?x ?x)))"
    )
    with pytest.raises(NameClashError, match="onBlock / on_block"):
        check_names(domain, problem, _names(tmp_path), False, False)


def test_check_names_rejects_owl_case_clash_and_unsafe_chars(tmp_path):
    extra = (
        "<http://t.org/o#invoice> rdf:type owl:Class .\n"
        "<http://t.org/o#Lift.v2> rdf:type owl:Class .\n"
    )
    domain, problem = _task("(define (domain d) (:predicates (p ?x)))")
    with pytest.raises(NameClashError) as e:
        check_names(domain, problem, _names(tmp_path, extra), False, False)
    assert "differ only in letter case" in str(e.value)
    assert "'Lift.v2' may only contain" in str(e.value)


@pytest.mark.parametrize(
    "predicate, horn, message",
    [
        ("(Updating)", False, "reserved for the update flag"),
        ("(inconsistent)", False, "inconsistency predicate"),
        ("(query2 ?x)", False, "generated query predicates"),
        ("(existsOnBlock ?x)", True, "generated concept for ∃onblock"),
    ],
)
def test_check_names_rejects_reserved_names(tmp_path, predicate, horn, message):
    domain, problem = _task(f"(define (domain d) (:predicates {predicate}))")
    with pytest.raises(NameClashError, match=message):
        check_names(domain, problem, _names(tmp_path), coherence_update=True, horn=horn)


def test_generated_exists_name_is_only_reserved_for_horn(tmp_path):
    domain, problem = _task("(define (domain d) (:predicates (existsOnBlock ?x)))")
    check_names(domain, problem, _names(tmp_path), coherence_update=True, horn=False)


def test_check_names_rejects_update_action_name(tmp_path):
    domain, problem = _task(
        "(define (domain d) (:predicates (p)) "
        "(:action Update :parameters () :precondition (and) :effect (p)))"
    )
    with pytest.raises(NameClashError, match="reserved for the update action"):
        check_names(domain, problem, _names(tmp_path), coherence_update=True, horn=False)
    check_names(domain, problem, _names(tmp_path), coherence_update=False, horn=False)
