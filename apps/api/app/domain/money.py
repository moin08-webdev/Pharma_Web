from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def to_paise(amount: Decimal) -> int:
    """Convert a Decimal INR currency amount into integer paise using ROUND_HALF_UP."""
    paise_val = (amount * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(paise_val)


def paise_to_inr_decimal(paise: int) -> Decimal:
    """Convert integer paise to Decimal INR amount."""
    return (Decimal(paise) / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_percent_difference(baseline_paise: int, selected_paise: int) -> Optional[Decimal]:
    """Calculate ((baseline - selected) / baseline) * 100 as Decimal with 2 decimal places.
    
    If baseline <= 0, returns None (comparison unavailable).
    Positive result indicates savings, negative indicates a cost increase.
    """
    if baseline_paise <= 0:
        return None
    baseline = Decimal(baseline_paise)
    selected = Decimal(selected_paise)
    diff = ((baseline - selected) / baseline) * Decimal(100)
    return diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_paise(amount_paise: Decimal) -> int:
    """Round a fractional paise amount to integer paise using ROUND_HALF_UP."""
    return int(amount_paise.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
