import shutil

import pddl.parser as pddl
from rewriting.clipper import Clipper
from variant_options import DERIVED_PREDICATE, INCOMPATIBLE_UPDATE

from .pipeline import Compiler
from .ontology import TEMPORARY_ONTOLOGY_FILE, construct_ontology_for_clipper

__all__ = [
    "compile_pddl",
    "Compiler",
    "construct_ontology_for_clipper",
    "TEMPORARY_ONTOLOGY_FILE",
]


def compile_pddl(
    ontology: str,
    in_domain: str,
    in_problem: str,
    out_domain: str,
    out_problem: str,
    clipper_path: str,
    clipper_mqf: bool = True,
    dl_lite_fragment: str = "core",
    rls_path: str = "",
    nmo_path: str = "",
    updating_pred_type: str = DERIVED_PREDICATE,
    incompatible_update_pred_type: str = INCOMPATIBLE_UPDATE,
    filter_unimportant: bool = True,
    expensive_filtering: bool = True,
    timer_output: str = "result.csv",
    verbose: bool = False,
    debug: bool = False,
    fragment: str = None,
    variant: str = None,
    task: str = None,
    element: str = None,
    tseitin: bool = None,
) -> None:

    from coherence_update import make_update_runner

    do_coherence_update = dl_lite_fragment == "horn" or bool(rls_path and nmo_path)
    update_runner = (
        make_update_runner(
            fragment=dl_lite_fragment,
            ontology_file_path=ontology,
            nmo_path=nmo_path,
            rls_file_path=rls_path,
            timer_output=timer_output,
            updating_pred_type=updating_pred_type,
            incompatible_update_pred_type=incompatible_update_pred_type,
        )
        if do_coherence_update
        else None
    )

    ontology_file_path = (
        construct_ontology_for_clipper(ontology)
        if do_coherence_update and dl_lite_fragment == "horn"
        else ontology
    )

    if shutil.which(clipper_path) is None:
        raise FileNotFoundError(f"Clipper not found: {clipper_path!r}")
    clipper = Clipper(clipper_path, ontology_file_path, clipper_mqf, debug)
    with open(in_domain) as f:
        domain = pddl.parse_domain(f.read())
    with open(in_problem) as f:
        problem = pddl.parse_problem(f.read())

    compiler = Compiler(
        domain,
        problem,
        clipper,
        filter_unimportant_atoms=filter_unimportant,
        expensive_duplicate_filtering=expensive_filtering,
        update_runner=update_runner,
        timer_output=timer_output,
        fragment=fragment,
        variant=variant,
        task=task,
        element=element,
        tseitin=tseitin,
    )
    compiler()

    domain.constants = problem.objects
    problem.objects = None

    if verbose:
        compiler.print_compilation_information()

    with open(out_domain, "w") as f:
        f.write(str(domain))
    with open(out_problem, "w") as f:
        f.write(str(problem))
