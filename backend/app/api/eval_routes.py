from fastapi import APIRouter
from pydantic import BaseModel
import time

from app.guardrails.schema_guard import validate_pipeline_output
from app.guardrails.pii_guard import mask_pii
from app.evals.metrics import basic_scores
from app.evals.judges import judge_stub

router = APIRouter(prefix="/pipeline", tags=["pipeline-eval"])


class RunInput(BaseModel):
    cv_text: str
    jd_text: str
    interview_notes: str


def has_enough_context(cv_text: str, jd_text: str, interview_notes: str) -> bool:
    total_len = len((cv_text or "").strip()) + len((jd_text or "").strip()) + len((interview_notes or "").strip())
    return total_len >= 80  # MVP threshold

def has_minimum_signal(cv_text: str, jd_text: str, interview_notes: str) -> bool:
    combined = f"{cv_text} {jd_text} {interview_notes}".lower()
    signals = ["python", "sql", "fastapi", "llm", "rag", "docker", "api", "backend", "machine learning"]
    return sum(1 for s in signals if s in combined) >= 2

def build_insufficient_data_response():
    return {
        "candidate_profile": {
            "years_experience": "unknown",
            "skills_match": {"must_have": [], "nice_to_have": []},
            "project_highlights": [],
            "potential_gaps": ["Insufficient input data to form evidence-based conclusions."]
        },
        "interview_questions": [
            {
                "question": "Bạn có thể mô tả 1 dự án AI đã làm (vai trò, stack, kết quả đo lường)?",
                "why_ask": "Thu thập bằng chứng năng lực kỹ thuật.",
                "signal_to_look_for": "Có nhiệm vụ rõ ràng và kết quả định lượng."
            }
        ],
        "rubric_scores": {
            "communication": 0,
            "problem_solving": 0,
            "technical_depth": 0,
            "ownership": 0,
            "culture_fit": 0,
            "overall_recommendation": "Need more information",
            "risk_flags": ["Insufficient evidence from CV/JD/interview notes."],
            "follow_up_questions": [
                "Liệt kê kỹ năng chính và số năm kinh nghiệm tương ứng.",
                "Mô tả đóng góp cụ thể trong dự án gần nhất."
            ]
        },
        "final_report": "Không đủ dữ liệu để đưa ra đánh giá đáng tin cậy. Vui lòng cung cấp CV/JD chi tiết hơn."
    }


def build_basic_evidence_based_response(cv_text: str, jd_text: str, interview_notes: str):
    combined = f"{cv_text}\n{jd_text}\n{interview_notes}".lower()

    # 1) Skill extraction (heuristic)
    must_have = []
    for kw in ["python", "fastapi", "sql", "postgresql", "docker", "llm", "rag"]:
        if kw in combined:
            must_have.append(kw)

    # 2) Years of experience extraction
    years_experience = "unknown"
    m = re.search(r'(\d+)\s*\+?\s*năm', combined) or re.search(r'(\d+)\s*\+?\s*years?', combined)
    if m:
        years_experience = f"{m.group(1)} years"

    # 3) Project highlights extraction
    highlights = []
    trigger_phrases = [
        "tối ưu", "latency", "improved", "optimiz", "truy vấn", "query", "logging", "pipeline", "api"
    ]
    source_sentences = re.split(r'[.\n;]+', f"{cv_text} {interview_notes}")
    for sent in source_sentences:
        s = sent.strip()
        if not s:
            continue
        if any(tp in s.lower() for tp in trigger_phrases):
            highlights.append(s)

    # limit highlight length
    highlights = highlights[:3]

    # 4) Recommendation rule
    rec = "Consider"
    risk_flags = ["Limited evidence from current inputs."]
    if len(must_have) >= 4 and years_experience != "unknown":
        rec = "Strong Consider"
        risk_flags = ["Need deeper validation on system design depth."]

    return {
        "candidate_profile": {
            "years_experience": years_experience,
            "skills_match": {
                "must_have": must_have,
                "nice_to_have": []
            },
            "project_highlights": highlights,
            "potential_gaps": ["Need clearer evidence on project impact and scope."]
        },
        "interview_questions": [
            {
                "question": "Hãy mô tả dự án gần nhất bạn làm và kết quả định lượng.",
                "why_ask": "Xác minh technical depth và ownership.",
                "signal_to_look_for": "Có số liệu cụ thể, trade-off rõ ràng."
            }
        ],
        "rubric_scores": {
            "communication": 3,
            "problem_solving": 3,
            "technical_depth": 2,
            "ownership": 3,
            "culture_fit": 3,
            "overall_recommendation": rec,
            "risk_flags": risk_flags,
            "follow_up_questions": [
                "Bạn đã tối ưu hiệu năng hoặc chi phí trong dự án nào chưa?",
                "Vai trò cụ thể của bạn trong team là gì?"
            ]
        },
        "final_report": "Initial screening generated from available evidence. More detailed CV/JD/notes recommended."
    }


@router.post("/run_with_eval")
def run_with_eval(payload: RunInput):
    started = time.time()

    # 1) Guard: thiếu dữ liệu -> trả fallback an toàn
    if (not has_enough_context(payload.cv_text, payload.jd_text, payload.interview_notes)) \
    or (not has_minimum_signal(payload.cv_text, payload.jd_text, payload.interview_notes)):
        output = build_insufficient_data_response()
        schema_ok, schema_msg = validate_pipeline_output(output)

        masked_report, pii_flag = mask_pii(output.get("final_report", ""))
        output["final_report"] = masked_report

        metrics = basic_scores(output, started, pii_flag=pii_flag, schema_ok=schema_ok)
        metrics["faithfulness_score"] = 1.0
        metrics["relevance_score"] = 0.3

        return {
            "result": output,
            "guardrails": {
                "schema_ok": schema_ok,
                "schema_message": schema_msg,
                "pii_masked": pii_flag,
                "insufficient_data": True
            },
            "metrics": metrics,
            "judge": {"judge_comment": "Insufficient context; returned safe fallback."}
        }

    # 2) Có dữ liệu -> response MVP bám evidence cơ bản
    output = build_basic_evidence_based_response(
        payload.cv_text, payload.jd_text, payload.interview_notes
    )

    schema_ok, schema_msg = validate_pipeline_output(output)
    masked_report, pii_flag = mask_pii(output.get("final_report", ""))
    output["final_report"] = masked_report

    metrics = basic_scores(output, started, pii_flag=pii_flag, schema_ok=schema_ok)
    judge = judge_stub(output)

    return {
        "result": output,
        "guardrails": {
            "schema_ok": schema_ok,
            "schema_message": schema_msg,
            "pii_masked": pii_flag,
            "insufficient_data": False
        },
        "metrics": metrics,
        "judge": judge
    }