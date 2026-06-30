from app.core.llm_client import call_llm_json
from app.core.prompt_loader import load_prompt

def run_evaluation(interview_notes: str) -> dict:
    system_prompt = load_prompt("evaluation_prompt.txt")
    user_input = f"Interview Notes:\n{interview_notes}"
    return call_llm_json(system_prompt, user_input, tag="evaluation")