import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("LLM_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

def _mock_json_by_tag(tag: str) -> dict:
    if tag == "ingestion":
        return {
            "years_experience": "3+ years",
            "skills_match": {"must_have": ["Python","FastAPI","PostgreSQL"], "nice_to_have": ["Docker"]},
            "project_highlights": ["Improved API latency by 35%"],
            "potential_gaps": ["Limited large-scale architecture examples"]
        }
    if tag == "questions":
        return {
            "interview_questions": [
                {
                    "question": "Bạn tối ưu API chậm như thế nào?",
                    "why_ask": "Đánh giá tư duy performance.",
                    "signal_to_look_for": "Có số liệu trước/sau."
                }
            ]
        }
    if tag == "evaluation":
        return {
            "communication": 4,
            "problem_solving": 4,
            "technical_depth": 3,
            "ownership": 4,
            "culture_fit": 4,
            "overall_recommendation": "Hire",
            "risk_flags": ["Thiếu ví dụ scale lớn"],
            "follow_up_questions": ["Mô tả một incident production end-to-end."]
        }
    return {}

def call_llm_json(system_prompt: str, user_input: str, tag: str, max_retries: int = 1) -> dict:
    for _ in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"[WARN] call_llm_json failed: {e}")
    return _mock_json_by_tag(tag)

def call_llm_text(system_prompt: str, user_input: str, max_retries: int = 1) -> str:
    for _ in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARN] call_llm_text failed: {e}")
    return "Fallback report: Candidate is promising, but needs deeper system design validation."