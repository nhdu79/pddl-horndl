from collections import defaultdict

from coherence_update.classes.inclusion import Inclusion
from utils.functions import get_repr


class TBox:
    def __init__(self, inclusions, **kwargs):
        """
        :param inclusions: dict of inclusions
            key: inclusion type
            value: list of inclusions
        :param roles: list of roles
        :param a_concepts: list of atomic concepts
        """
        self.roles = kwargs.get("roles", [])
        self.a_concepts = kwargs.get("a_concepts", [])
        self.functs = kwargs.get("functs", [])
        self.inv_functs = kwargs.get("functs_inv", [])

        self.incl_dict = defaultdict(lambda: [])
        for incl_type, incl_list in inclusions.items():
            for incl in incl_list:
                left_uri, right_uri = incl[0], incl[1]
                left_atomic_uri, right_atomic_uri = incl[2], incl[3]
                new_incl = Inclusion(
                    incl_type, left_uri, right_uri, left_atomic_uri, right_atomic_uri
                )
                self.incl_dict[incl_type].append(new_incl)

    def repr_of(self, collection):
        if collection not in self.__dict__:
            return []

        return [get_repr(item) for item in self.__dict__[collection]]
