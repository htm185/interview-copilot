from typing import Any, Dict, Tuple

REQUIRED_KEYS = ["candidate_profile", "interview_questions", "final_report"]


def validate_pipeline_output(data: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "Output is not a JSON object"

    for k in REQUIRED_KEYS:
        if k not in data:
            return False, f"Missing key: {k}"

    if "evaluation" not in data and "rubric_scores" not in data:
        return False, "Missing key: evaluation or rubric_scores"

    if not isinstance(data["interview_questions"], list):
        return False, "interview_questions must be a list"

    return True, "ok"