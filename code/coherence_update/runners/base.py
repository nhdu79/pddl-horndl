from abc import ABC, abstractmethod

from variant_options import DERIVED_PREDICATE, INCOMPATIBLE_UPDATE


class UpdateRunner(ABC):
    """Abstract base class defining the interface the Compiler depends on."""

    def __init__(
        self,
        updating_pred_type=DERIVED_PREDICATE,
        incompatible_update_pred_type=INCOMPATIBLE_UPDATE,
        timer_output="result.csv",
    ):
        self.updating_pred_type = updating_pred_type
        self.incompatible_update_pred_type = incompatible_update_pred_type
        self.timer_output = timer_output

    @abstractmethod
    def run(self) -> list:
        """Return all Datalog update rules derived from the full TBox."""

    @abstractmethod
    def run_for_missing_predicates(self, missing_concepts, missing_roles) -> list:
        """Return update rules for predicates present in the domain but absent from the ontology."""

    @abstractmethod
    def atomic_predicates(self) -> set:
        """Normalised names of all atomic predicates seen in the ontology."""

    @abstractmethod
    def predicates_for_domain(self, pddl_predicates: list) -> list:
        """
        Returns the unified list of Predicate objects that should have
        ins/del/request/closure machinery registered in the domain:
            pddl_predicates ∪ (ontology predicates not already in pddl_predicates)
        """

    @abstractmethod
    def filter_non_reachable_predicates(
        self, rules: list, actions: list, initial_predicates=None
    ) -> tuple:
        """
        Return (kept_rules, kept) where kept_rules is the list of reachable rules and kept is
        a list of Predicate objects for all reachable base concepts and roles (with correct
        arity encoded in their parameters). Returns (rules, None) when no filtering is applied.
        """
