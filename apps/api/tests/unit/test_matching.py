from app.domain.enums import MatchOutcome
from app.domain.matching_rules import evaluate_formulation_match


def test_exact_formulation_candidate():
    prescribed = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "paracetamol", "strength": "500", "unit": "mg"}],
    }
    candidate = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "paracetamol", "strength": "500", "unit": "mg"}],
    }
    outcome, reason = evaluate_formulation_match(prescribed, candidate)
    assert outcome == MatchOutcome.EXACT_FORMULATION_CANDIDATE
    assert "Exact" in reason


def test_strength_mismatch():
    prescribed = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "paracetamol", "strength": "500", "unit": "mg"}],
    }
    candidate = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "paracetamol", "strength": "650", "unit": "mg"}],
    }
    outcome, reason = evaluate_formulation_match(prescribed, candidate)
    assert outcome == MatchOutcome.STRENGTH_MISMATCH
    assert "Strength mismatch" in reason


def test_release_type_mismatch():
    prescribed = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "metformin", "strength": "500", "unit": "mg"}],
    }
    candidate = {
        "form": "tablet",
        "route": "oral",
        "release": "extended_release",
        "components": [{"ingredient": "metformin", "strength": "500", "unit": "mg"}],
    }
    outcome, reason = evaluate_formulation_match(prescribed, candidate)
    assert outcome == MatchOutcome.FORM_ROUTE_RELEASE_MISMATCH


def test_ingredient_subset_rejected():
    prescribed = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [
            {"ingredient": "amoxicillin", "strength": "500", "unit": "mg"},
            {"ingredient": "clavulanic_acid", "strength": "125", "unit": "mg"},
        ],
    }
    # Candidate with only amoxicillin (subset) must be rejected
    candidate = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [{"ingredient": "amoxicillin", "strength": "500", "unit": "mg"}],
    }
    outcome, reason = evaluate_formulation_match(prescribed, candidate)
    assert outcome == MatchOutcome.INGREDIENT_SET_MISMATCH


def test_unreviewed_combination_requires_manual_review():
    prescribed = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [
            {"ingredient": "amoxicillin", "strength": "500", "unit": "mg"},
            {"ingredient": "clavulanic_acid", "strength": "125", "unit": "mg"},
        ],
    }
    candidate = {
        "form": "tablet",
        "route": "oral",
        "release": "immediate_release",
        "components": [
            {"ingredient": "amoxicillin", "strength": "500", "unit": "mg"},
            {"ingredient": "clavulanic_acid", "strength": "125", "unit": "mg"},
        ],
    }
    outcome, reason = evaluate_formulation_match(prescribed, candidate)
    assert outcome == MatchOutcome.MANUAL_REVIEW_REQUIRED
