# Interview Copilot (FastAPI + Next.js)

AI-powered interview assistant for screening candidates from **CV**, **Job Description (JD)**, and **interview notes**.  
This version includes **guardrails** and **basic evaluation metrics** to reduce hallucinations and make outputs more production-like.

---

## Features

- Candidate screening from 3 inputs:
  - CV text
  - JD text
  - Interview notes
- Structured output:
  - `candidate_profile`
  - `interview_questions`
  - `rubric_scores`
  - `final_report`
- Guardrails:
  - **Schema validation** (`schema_guard`)
  - **PII masking** (`pii_guard`: email/phone/ID)
  - **Insufficient-data fallback** (safe response instead of over-claiming)
- Metrics (MVP):
  - `schema_pass`
  - `faithfulness_score`
  - `relevance_score`
  - `pii_leak_flag`
  - `latency_ms`

---

## Tech Stack

### Backend
- FastAPI
- Pydantic
- Uvicorn
- SQLAlchemy (prepared for persistence)

### Frontend
- Next.js
- React

---

## Project Structure

```text
interview-copilot/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ eval_routes.py
│  │  ├─ evals/
│  │  │  ├─ metrics.py
│  │  │  └─ judges.py
│  │  ├─ guardrails/
│  │  │  ├─ schema_guard.py
│  │  │  └─ pii_guard.py
│  │  └─ main.py
│  └─ requirements.txt
└─ frontend/
   └─ (Next.js app)
```

---

## Quick Start

## 1) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Open Swagger:
- http://localhost:8000/docs

## 2) Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:
- http://localhost:3000

---

## API

### `POST /pipeline/run_with_eval`

Runs screening pipeline + guardrails + metrics.

### Request body

```json
{
  "cv_text": "Tôi có 2 năm làm backend với Python, FastAPI, PostgreSQL...",
  "jd_text": "Tuyển AI Engineer, cần Python, FastAPI, SQL...",
  "interview_notes": "Ứng viên mô tả pipeline xử lý CV..."
}
```

### Response (example)

```json
{
  "result": {
    "candidate_profile": {
      "years_experience": "2 years",
      "skills_match": {
        "must_have": ["python", "fastapi", "sql"],
        "nice_to_have": []
      },
      "project_highlights": ["Đã xây API tuyển dụng và tối ưu truy vấn SQL"],
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
      "overall_recommendation": "Consider",
      "risk_flags": ["Limited evidence from current inputs."],
      "follow_up_questions": [
        "Bạn đã tối ưu hiệu năng hoặc chi phí trong dự án nào chưa?"
      ]
    },
    "final_report": "Initial screening generated from available evidence."
  },
  "guardrails": {
    "schema_ok": true,
    "schema_message": "ok",
    "pii_masked": false,
    "insufficient_data": false
  },
  "metrics": {
    "schema_pass": true,
    "faithfulness_score": 1.0,
    "relevance_score": 0.5,
    "pii_leak_flag": false,
    "latency_ms": 12,
    "token_cost_est": null
  },
  "judge": {
    "judge_comment": "MVP judge placeholder"
  }
}
```

---

## Guardrails Design

- **Schema Guard**
  - Ensures required keys exist
  - Supports `evaluation` or `rubric_scores`
- **PII Guard**
  - Masks:
    - Email
    - Phone number
    - ID-like numeric strings
- **Insufficient Data Policy**
  - If input context/signals are too weak, return a conservative fallback:
    - no strong claims
    - recommendation = `Need more information`

---

## Testing Checklist

- Open `http://localhost:8000/docs`
- Test:
  - normal case (enough technical content)
  - short/weak input (fallback expected)
  - PII input (masking expected)
- Verify:
  - `guardrails.schema_ok == true`
  - `metrics.latency_ms > 0`
  - `guardrails.insufficient_data` behavior is correct

---

## Known Limitations (MVP)

- Heuristic scoring (not true LLM-as-a-judge yet)
- Simple keyword extraction for skills
- No database persistence for eval runs (planned)

---

## Roadmap

- Persist eval runs to DB (`eval_runs`)
- Add LLM-based judges for faithfulness/relevance
- Add citation/evidence spans from CV/JD/notes
- Improve recommendation calibration

---
