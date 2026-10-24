from decimal import Decimal
from app.domain.money import (
    to_paise,
    paise_to_inr_decimal,
    calculate_percent_difference,
    round_paise,
)
from app.domain.quantities import calculate_pack_breakdown


def test_deterministic_demo_arithmetic_unit_dispensing():
    # Brand A: INR 30 for 15 tablets (pack_qty=15, pack_price=3000 paise)
    # Product B: INR 10 for 10 tablets (pack_qty=10, pack_price=1000 paise)
    # Requested units: 15
    # Allowed unit dispensing:
    # Brand A: 1 pack, supplied 15, cost 3000 paise (INR 30)
    p_packs, p_supp, p_excess, p_cost = calculate_pack_breakdown(
        requested_units=15,
        pack_quantity=15,
        pack_price_paise=3000,
        pack_break_allowed=True,
    )
    assert p_packs == 1
    assert p_supp == 15
    assert p_cost == 3000

    # Product B: pack breaking allowed -> 15 units * (1000 / 10) = 1500 paise (INR 15)
    b_packs, b_supp, b_excess, b_cost = calculate_pack_breakdown(
        requested_units=15,
        pack_quantity=10,
        pack_price_paise=1000,
        pack_break_allowed=True,
    )
    assert b_supp == 15
    assert b_cost == 1500

    diff = calculate_percent_difference(p_cost, b_cost)
    assert diff == Decimal("50.00")


def test_deterministic_demo_arithmetic_whole_pack_dispensing():
    # Under whole-pack dispensing:
    # Product B requires ceil(15 / 10) = 2 packs, costs 2 * 1000 = 2000 paise (INR 20), supplies 20 tablets (5 excess)
    b_packs, b_supp, b_excess, b_cost = calculate_pack_breakdown(
        requested_units=15,
        pack_quantity=10,
        pack_price_paise=1000,
        pack_break_allowed=False,
    )
    assert b_packs == 2
    assert b_supp == 20
    assert b_excess == 5
    assert b_cost == 2000

    # Baseline cost: INR 30 (3000 paise)
    diff = calculate_percent_difference(3000, 2000)
    # ((3000 - 2000) / 3000) * 100 = 33.3333... -> 33.33%
    assert diff == Decimal("33.33")


def test_more_expensive_alternative_not_clamped():
    # Baseline INR 20 (2000 paise), Alternative INR 30 (3000 paise)
    diff = calculate_percent_difference(2000, 3000)
    # ((2000 - 3000) / 2000) * 100 = -50.00%
    assert diff == Decimal("-50.00")


def test_zero_or_negative_baseline_unavailable():
    assert calculate_percent_difference(0, 1000) is None
    assert calculate_percent_difference(-100, 1000) is None


def test_paise_conversions():
    assert to_paise(Decimal("10.50")) == 1050
    assert to_paise(Decimal("10.505")) == 1051  # ROUND_HALF_UP
    assert paise_to_inr_decimal(1050) == Decimal("10.50")
    assert round_paise(Decimal("123.49")) == 123
    assert round_paise(Decimal("123.50")) == 124
