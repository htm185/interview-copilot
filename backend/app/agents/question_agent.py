from app.core.llm_client import call_llm_json
from app.core.prompt_loader import load_prompt

def run_question_generation(candidate_profile: dict, jd_text: str) -> list[dict]:
    system_prompt = load_prompt("question_prompt.txt")
    user_input = f"Candidate Profile:\n{candidate_profile}\n\nJD:\n{jd_text}"
    data = call_llm_json(system_prompt, user_input, tag="questions")
    return data.get("interview_questions", [])