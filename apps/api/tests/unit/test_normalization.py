from decimal import Decimal
from app.domain.normalization import (
    normalize_ingredient_name,
    normalize_strength,
    normalize_dosage_form,
    normalize_release_type,
)


def test_normalize_strength_units():
    # 0.5 g -> 500 mg
    amt, unit = normalize_strength(Decimal("0.5"), "g")
    assert amt == Decimal("500")
    assert unit == "mg"

    # 500 mg -> 500 mg
    amt, unit = normalize_strength(Decimal("500"), "mg")
    assert amt == Decimal("500")
    assert unit == "mg"

    # 1000 mcg -> 1 mg
    amt, unit = normalize_strength(Decimal("1000"), "mcg")
    assert amt == Decimal("1")
    assert unit == "mg"

    # 5 ml -> 5 ml
    amt, unit = normalize_strength(Decimal("5"), "ml")
    assert amt == Decimal("5")
    assert unit == "ml"


def test_normalize_ingredient_names():
    assert normalize_ingredient_name("Acetaminophen") == "paracetamol"
    assert normalize_ingredient_name("Paracetamol IP") == "paracetamol"
    assert normalize_ingredient_name("Amoxycillin") == "amoxicillin"
    assert normalize_ingredient_name("Metformin Hydrochloride") == "metformin_hydrochloride"


def test_normalize_dosage_forms():
    assert normalize_dosage_form("Tablet") == "tablet"
    assert normalize_dosage_form("Film Coated TAB") == "tablet"
    assert normalize_dosage_form("Capsule") == "capsule"
    assert normalize_dosage_form("Syrup") == "syrup"


def test_normalize_release_types():
    assert normalize_release_type(None) == "immediate_release"
    assert normalize_release_type("ER") == "extended_release"
    assert normalize_release_type("Sustained Release") == "sustained_release"
    assert normalize_release_type("Enteric Coated") == "delayed_release"
    assert normalize_release_type("IR") == "immediate_release"
