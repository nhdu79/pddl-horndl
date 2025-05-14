# from hashlib import md5
import pprint

from utils.functions import get_repr

INCLUSION_TYPES_ORDER = [
    # positive
    "aAInaBSub",  # 1. appearing atomic concepts
    "rInPSub",  # 2. appearing atomic roles
    "rInPMinusSub",  # 3. appearing inverse roles
    "rMinusInPSub",  # 4. appearing inverse roles
    "ePInaBSub",  # 5. dom
    "ePMinusInaBSub",  # 6. rng
    # negative
    "aAInNotaBSub",  # 7. appearing atomic concepts
    "aBInNotePSub",
    "ePInNotaBSub",
    "aBInNotePMinusSub",
    "ePMinusInNotaBSub",
    "rInNotPSub",
    "rInNotPMinusSub",
]


class Inclusion:
    def __init__(
        self, incl_type, left_uri, right_uri, left_atomic_uri, right_atomic_uri
    ):
        """
        :param inclusion: string separated by ','
            inclusion_type: positive or negative
        """
        self.left_uri = left_uri
        self.left_atomic_uri = left_atomic_uri
        self.right_uri = right_uri
        self.right_atomic_uri = right_atomic_uri
        self.incl_type = incl_type
        self._left_atomic_repr = get_repr(left_atomic_uri)
        self._right_atomic_repr = get_repr(right_atomic_uri)
        self._left_repr = get_repr(left_uri)
        self._right_repr = get_repr(right_uri)

    def __dict__(self):
        return {
            "uri": {
                "left": self.left_uri,
                "right": self.right_uri,
                "left_atomic": self.left_atomic_uri,
                "right_atomic": self.right_atomic_uri,
            },
            "repr": {
                "left": self._left_repr,
                "right": self._right_repr,
                "left_atomic": self._left_atomic_repr,
                "right_atomic": self._right_atomic_repr,
            },
            "incl_type": self.incl_type,
        }

    def pprint(self):
        pprint.pprint(self.__dict__())

    def __str__(self):
        return f"{self.incl_type}: {self.left_pred.repr} {self.right_pred.repr}"

    def get_left_closure_repr(self):
        """
        Repr for cl(T) closure; i.e. "root" role/ concept
        """
        return self._left_atomic_repr

    def get_right_closure_repr(self):
        return self._right_atomic_repr

    def get_left_repr(self):
        """
        Repr for update rules
        """
        return self._left_repr

    def get_right_repr(self):
        return self._right_repr
