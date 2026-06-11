from coherence_update.runners.base import UpdateRunner
from coherence_update.runners.core import CoreUpdateRunner
from coherence_update.runners.horn import HornUpdateRunner
from compilation.variant_options import (
    INCOMPATIBLE_UPDATE_PREDICATE_TYPES,
    UPDATING_PREDICATE_TYPES,
)

__all__ = [
    "UpdateRunner",
    "CoreUpdateRunner",
    "HornUpdateRunner",
    "make_update_runner",
]


def make_update_runner(
    fragment: str,
    ontology_file_path: str,
    updating_pred_type=UPDATING_PREDICATE_TYPES["derived_predicate"],
    incompatible_update_pred_type=INCOMPATIBLE_UPDATE_PREDICATE_TYPES[
        "incompatible_update"
    ],
    timer_output="result.csv",
    nmo_path="",
    rls_file_path="",
    write_to_file=False,
) -> UpdateRunner:
    """Factory that selects the correct UpdateRunner for the given DL-Lite fragment."""
    common = dict(
        updating_pred_type=updating_pred_type,
        incompatible_update_pred_type=incompatible_update_pred_type,
        timer_output=timer_output,
    )
    if fragment == "core":
        return CoreUpdateRunner(
            nmo_path=nmo_path,
            rls_file_path=rls_file_path,
            ontology_file_path=ontology_file_path,
            write_to_file=write_to_file,
            **common,
        )
    if fragment == "horn":
        return HornUpdateRunner(ontology_file_path=ontology_file_path, **common)
    raise ValueError(f"Unknown DL-Lite fragment: {fragment!r}. Use 'core' or 'horn'.")
