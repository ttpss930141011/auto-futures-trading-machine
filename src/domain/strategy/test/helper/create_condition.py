from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation


def create_condition(
    cond_id: str,
    action: OrderOperation,
    trigger: int,
    quantity: int,
    tp_points: int = 90,
    sl_points: int = 30,
    turning_points: int = 15,
    is_following: bool = False,
) -> Condition:
    """Creates a Condition object for testing."""
    condition = Condition(
        condition_id=cond_id,
        action=action,
        trigger_price=trigger,
        quantity=quantity,
        take_profit_point=tp_points,
        stop_loss_point=sl_points,
        turning_point=turning_points,
        is_following=is_following,
    )
    return condition
