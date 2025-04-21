from src.domain.entities.condition import Condition


def set_condition_state(
    condition: Condition,
    is_trigger: bool = False,
    is_ordered: bool = False,
    is_exited: bool = False,
):
    """Sets the state fields (is_trigger, is_ordered, is_exited) for testing."""
    condition.is_trigger = is_trigger
    condition.is_ordered = is_ordered
    condition.is_exited = is_exited
