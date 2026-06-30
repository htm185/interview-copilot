from app.core.llm_client import call_llm_text
from app.core.prompt_loader import load_prompt

def run_report(candidate_profile: dict, interview_questions: list[dict], rubric_scores: dict) -> str:
    system_prompt = load_prompt("report_prompt.txt")
    user_input = (
        f"Candidate Profile:\n{candidate_profile}\n\n"
        f"Interview Questions:\n{interview_questions}\n\n"
        f"Rubric Scores:\n{rubric_scores}\n"
    )
    return call_llm_text(system_prompt, user_input)