import re
from decimal import Decimal
from typing import Optional, Tuple


UNIT_CONVERSIONS = {
    # target base is 'mg' for solids
    ("g", "mg"): Decimal("1000"),
    ("gm", "mg"): Decimal("1000"),
    ("gram", "mg"): Decimal("1000"),
    ("grams", "mg"): Decimal("1000"),
    ("mg", "mg"): Decimal("1"),
    ("milligram", "mg"): Decimal("1"),
    ("milligrams", "mg"): Decimal("1"),
    ("mcg", "mg"): Decimal("0.001"),
    ("ug", "mg"): Decimal("0.001"),
    ("microgram", "mg"): Decimal("0.001"),
    ("micrograms", "mg"): Decimal("0.001"),
    # liquids
    ("ml", "ml"): Decimal("1"),
    ("l", "ml"): Decimal("1000"),
    ("liter", "ml"): Decimal("1000"),
    ("liters", "ml"): Decimal("1000"),
}

# Standardized aliases
INGREDIENT_ALIASES = {
    "paracetamol": "paracetamol",
    "acetaminophen": "paracetamol",
    "amoxicillin": "amoxicillin",
    "amoxycillin": "amoxicillin",
    "clavulanate": "clavulanic_acid",
    "clavulanic acid": "clavulanic_acid",
    "pantoprazole": "pantoprazole",
    "atorvastatin": "atorvastatin",
    "metformin": "metformin",
    "metformin hydrochloride": "metformin_hydrochloride",
    "telmisartan": "telmisartan",
    "amlodipine": "amlodipine",
    "amlodipine besylate": "amlodipine_besylate",
    "cetirizine": "cetirizine",
    "cetirizine dihydrochloride": "cetirizine_dihydrochloride",
}


def normalize_ingredient_name(raw_name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", raw_name).strip().lower()
    # Strip common pharmacopoeia suffixes (IP, BP, USP)
    cleaned = re.sub(r"\b(ip|bp|usp)\b", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return INGREDIENT_ALIASES.get(cleaned, cleaned)


def normalize_strength(amount: Decimal, unit: str) -> Tuple[Decimal, str]:
    """Convert amount and unit into a canonical unit (such as mg for mass).
    
    E.g. (0.5, 'g') -> (500, 'mg')
    """
    cleaned_unit = unit.strip().lower()
    key = (cleaned_unit, "mg")
    if key in UNIT_CONVERSIONS:
        factor = UNIT_CONVERSIONS[key]
        normalized_amount = (amount * factor).normalize()
        return normalized_amount, "mg"
    key_ml = (cleaned_unit, "ml")
    if key_ml in UNIT_CONVERSIONS:
        factor = UNIT_CONVERSIONS[key_ml]
        normalized_amount = (amount * factor).normalize()
        return normalized_amount, "ml"
    return amount.normalize(), cleaned_unit


def normalize_dosage_form(raw_form: str) -> str:
    cleaned = raw_form.strip().lower()
    if "tab" in cleaned:
        return "tablet"
    if "cap" in cleaned:
        return "capsule"
    if "syr" in cleaned or "susp" in cleaned or "liquid" in cleaned:
        return "syrup"
    if "inj" in cleaned:
        return "injection"
    if "oint" in cleaned:
        return "ointment"
    if "cream" in cleaned:
        return "cream"
    return cleaned


def normalize_release_type(raw_release: Optional[str]) -> str:
    if not raw_release:
        return "immediate_release"
    cleaned = raw_release.strip().lower()
    if "dr" in cleaned or "delayed" in cleaned or "enteric" in cleaned:
        return "delayed_release"
    if re.search(r"\ber\b", cleaned) or "extended" in cleaned:
        return "extended_release"
    if re.search(r"\bsr\b", cleaned) or "sustained" in cleaned:
        return "sustained_release"
    if re.search(r"\bpr\b", cleaned) or "prolonged" in cleaned:
        return "prolonged_release"
    return "immediate_release"
