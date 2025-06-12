from typing import Dict, List, Any, Optional, Tuple


def min_max_normalization(values: List[float]) -> Tuple[List[float], float, float]:
    """
    Min-max normalize a list of values to [0, 1].
    Returns the normalized list, min, and max for later use.
    If all values are the same, returns 0.5 for all.
    """
    if not values:
        return [], 0, 0
    min_v, max_v = min(values), max(values)
    if min_v == max_v:
        return [0.5 for _ in values], min_v, max_v
    return [(v - min_v) / (max_v - min_v) for v in values], min_v, max_v


def score_property(
    property_dict: Dict[str, Any],
    weights: Dict[str, float],
    normalization_info: Dict[str, Tuple[float, float]],
    return_justification: bool = False
) -> Any:
    """
    Compute a weighted score (0-100) for a single property.
    Args:
        property_dict: Dictionary of property attributes (e.g., price, size).
        weights: Dictionary mapping attribute names to user-defined weights.
        normalization_info: Dict mapping attribute names to (min, max) for normalization.
        return_justification: If True, return dict with id, score, and breakdown.
    Returns:
        Float score (0-100), or dict with id, score, and justification if requested.
    """
    total_weight = sum(abs(w) for w in weights.values() if w != 0)
    if total_weight == 0:
        return 0.0 if not return_justification else {"id": property_dict.get("id"), "score": 0.0, "justification": "All weights are zero."}

    score = 0.0
    breakdown = {}
    for field, weight in weights.items():
        if field not in property_dict or field not in normalization_info:
            continue
        min_v, max_v = normalization_info[field]
        value = property_dict[field]
        # Handle missing or non-numeric values gracefully
        try:
            value = float(value)
        except (ValueError, TypeError):
            continue
        # Normalize
        if min_v == max_v:
            norm = 0.5
        else:
            norm = (value - min_v) / (max_v - min_v)
        weighted = norm * weight
        score += weighted
        breakdown[field] = {"value": value, "normalized": norm, "weight": weight, "contribution": weighted}
    # Scale to 0-100
    score = (score / total_weight) * 100
    if not return_justification:
        return score
    return {
        "id": property_dict.get("id"),
        "score": score,
        "justification": breakdown
    }


def rank_properties(
    properties: List[Dict[str, Any]],
    weights: Dict[str, float],
    return_justification: bool = False
) -> List[Any]:
    """
    Rank a list of properties by weighted score.
    Args:
        properties: List of property dicts.
        weights: Dict mapping attribute names to user-defined weights.
        return_justification: If True, include breakdown for each property.
    Returns:
        List of properties with scores, sorted descending.
    """
    # Compute normalization info for each weighted field
    normalization_info = {}
    for field in weights:
        values = [p[field] for p in properties if field in p and isinstance(p[field], (int, float))]
        if not values:
            # Try to convert to float if possible
            values = []
            for p in properties:
                try:
                    values.append(float(p[field]))
                except (KeyError, ValueError, TypeError):
                    continue
        if values:
            min_v, max_v = min(values), max(values)
            normalization_info[field] = (min_v, max_v)
    # Score each property
    scored = [
        score_property(p, weights, normalization_info, return_justification)
        for p in properties
    ]
    # Sort descending by score
    if return_justification:
        return sorted(scored, key=lambda x: x["score"], reverse=True)
    else:
        return sorted(zip(properties, scored), key=lambda x: x[1], reverse=True) 