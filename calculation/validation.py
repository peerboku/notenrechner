def validate_weights(weights: dict[int, float]) -> bool:
    total = sum(weights.values())
    return abs(total - 100.0) < 0.01


def validate_grade_value(value: float, input_type: str, discrete_values: str | None = None) -> bool:
    from database.settings import get_setting
    scale = get_setting("grading_scale") or "austria"

    if scale == "austria":
        min_val, max_val = 1.0, 5.0
    else:
        min_val, max_val = 1.0, 6.0

    if input_type == "continuous":
        return min_val <= value <= max_val
    if input_type == "discrete":
        if not discrete_values:
            return False
        allowed = {float(v.strip()) for v in discrete_values.split(",")}
        return float(value) in allowed
    return False
