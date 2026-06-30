from app.core.llm_client import call_llm_json
from app.core.prompt_loader import load_prompt

def run_ingestion(cv_text: str, jd_text: str) -> dict:
    system_prompt = load_prompt("ingestion_prompt.txt")
    user_input = f"CV:\n{cv_text}\n\nJD:\n{jd_text}"
    return call_llm_json(system_prompt, user_input, tag="ingestion")