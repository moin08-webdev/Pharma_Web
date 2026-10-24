import hashlib
import json
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from app.domain.normalization import normalize_ingredient_name, normalize_strength, normalize_dosage_form, normalize_release_type


def build_canonical_component(
    ingredient_name: str,
    strength_numerator: Decimal,
    numerator_unit: str,
    denominator_amount: Decimal = Decimal("1"),
    denominator_unit: str = "unit",
    component_release_type: str = "immediate_release"
) -> Dict[str, Any]:
    norm_name = normalize_ingredient_name(ingredient_name)
    norm_amount, norm_unit = normalize_strength(strength_numerator, numerator_unit)
    return {
        "ingredient": norm_name,
        "strength": str(norm_amount),
        "unit": norm_unit,
        "denominator_amount": str(denominator_amount),
        "denominator_unit": denominator_unit.strip().lower(),
        "release": normalize_release_type(component_release_type)
    }


def compute_formulation_signature(
    dosage_form: str,
    route: str,
    release_type: str,
    components: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Compute canonical signature string and its sha256 hash.
    
    Components must be sorted by ingredient name to ensure determinism.
    """
    norm_form = normalize_dosage_form(dosage_form)
    norm_route = route.strip().lower()
    norm_release = normalize_release_type(release_type)
    
    sorted_comps = sorted(
        components,
        key=lambda c: (c["ingredient"], c["unit"], c["strength"])
    )
    
    payload = {
        "form": norm_form,
        "route": norm_route,
        "release": norm_release,
        "components": sorted_comps
    }
    
    canonical_str = json.dumps(payload, sort_keys=True)
    sig_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
    return canonical_str, sig_hash
