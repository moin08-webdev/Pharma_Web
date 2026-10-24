import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple


def calculate_pack_breakdown(
    requested_units: int,
    pack_quantity: int,
    pack_price_paise: int,
    pack_break_allowed: bool,
) -> Tuple[int, int, int, int]:
    """Calculate (packs_needed, supplied_units, excess_units, total_cost_paise).
    
    Returns:
        packs_needed: int
        supplied_units: int
        excess_units: int
        total_cost_paise: int
    """
    if requested_units <= 0 or pack_quantity <= 0 or pack_price_paise < 0:
        raise ValueError("Quantities and pack prices must be positive")

    if pack_break_allowed:
        packs_needed = math.ceil(requested_units / pack_quantity)
        supplied_units = requested_units
        excess_units = 0
        # Unit price in fractional paise, then multiply by requested units and round HALF_UP
        unit_price_paise = Decimal(pack_price_paise) / Decimal(pack_quantity)
        total_cost_paise = int((Decimal(requested_units) * unit_price_paise).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return packs_needed, supplied_units, excess_units, total_cost_paise
    else:
        packs_needed = math.ceil(requested_units / pack_quantity)
        supplied_units = packs_needed * pack_quantity
        excess_units = supplied_units - requested_units
        total_cost_paise = packs_needed * pack_price_paise
        return packs_needed, supplied_units, excess_units, total_cost_paise
