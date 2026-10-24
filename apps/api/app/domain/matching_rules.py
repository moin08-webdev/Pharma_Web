from typing import List, Dict, Any, Tuple
from app.domain.enums import MatchOutcome


def evaluate_formulation_match(
    prescribed: Dict[str, Any],
    candidate: Dict[str, Any]
) -> Tuple[MatchOutcome, str]:
    """Evaluate whether candidate matches prescribed formulation strictly.
    
    Returns (outcome, reason).
    """
    # 1. Route, Form, Release type check
    p_form = prescribed.get("form")
    c_form = candidate.get("form")
    p_route = prescribed.get("route", "oral")
    c_route = candidate.get("route", "oral")
    p_release = prescribed.get("release", "immediate_release")
    c_release = candidate.get("release", "immediate_release")

    if not p_form or not c_form:
        return MatchOutcome.INCOMPLETE_FORMULATION, "Formulation dosage form is missing or incomplete"

    if p_form != c_form or p_route != c_route or p_release != c_release:
        return (
            MatchOutcome.FORM_ROUTE_RELEASE_MISMATCH,
            f"Form, route or release type mismatch: prescribed ({p_form}, {p_route}, {p_release}) vs candidate ({c_form}, {c_route}, {c_release})"
        )

    p_comps: List[Dict[str, Any]] = prescribed.get("components", [])
    c_comps: List[Dict[str, Any]] = candidate.get("components", [])

    if not p_comps or not c_comps:
        return MatchOutcome.INCOMPLETE_FORMULATION, "Active ingredients or strength components missing"

    # Compare ingredient set
    p_ingredients = {c["ingredient"] for c in p_comps}
    c_ingredients = {c["ingredient"] for c in c_comps}

    if p_ingredients != c_ingredients:
        return (
            MatchOutcome.INGREDIENT_SET_MISMATCH,
            f"Active ingredient set does not match. Prescribed: {sorted(p_ingredients)}, Candidate: {sorted(c_ingredients)}"
        )

    # Compare strengths
    p_map = {c["ingredient"]: (c["strength"], c["unit"]) for c in p_comps}
    c_map = {c["ingredient"]: (c["strength"], c["unit"]) for c in c_comps}

    for ing, (p_str, p_unit) in p_map.items():
        c_str, c_unit = c_map[ing]
        if p_str != c_str or p_unit != c_unit:
            return (
                MatchOutcome.STRENGTH_MISMATCH,
                f"Strength mismatch for {ing}: prescribed {p_str} {p_unit} vs candidate {c_str} {c_unit}"
            )

    # Check automatic vs manual review eligibility:
    # "Initial automatic candidate search is restricted to reviewed oral immediate-release single-ingredient solid products.
    # Mark modified-release formulations, injectables, biologics, narrow-therapeutic-index products and unreviewed combinations as manual-review/unsupported"
    is_solid = p_form in {"tablet", "capsule"}
    is_oral = p_route == "oral"
    is_ir = p_release == "immediate_release"
    is_single = len(p_comps) == 1

    if not (is_solid and is_oral and is_ir and is_single):
        return (
            MatchOutcome.MANUAL_REVIEW_REQUIRED,
            "Formulation contains combination ingredients or non-oral/modified-release form; requires manual clinical review"
        )

    return MatchOutcome.EXACT_FORMULATION_CANDIDATE, "Exact reviewed formulation match"
