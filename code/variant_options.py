DERIVED_PREDICATE = "derived_predicate"
ACTION_EFFECT = "action_effect"
INCOMPATIBLE_UPDATE = "incompatible_update"
COMPATIBLE_UPDATE = "compatible_update"

UPDATING_PRED_TYPES: frozenset[str] = frozenset({DERIVED_PREDICATE, ACTION_EFFECT})
INCOMPATIBLE_UPDATE_PRED_TYPES: frozenset[str] = frozenset({INCOMPATIBLE_UPDATE, COMPATIBLE_UPDATE})
