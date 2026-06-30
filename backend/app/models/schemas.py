from pydantic import BaseModel, Field
from typing import List, Dict


class PipelineRunRequest(BaseModel):
    cv_text: str = Field(..., min_length=20)
    jd_text: str = Field(..., min_length=20)
    interview_notes: str = Field(..., min_length=20)


class InterviewQuestion(BaseModel):
    question: str
    why_ask: str
    signal_to_look_for: str


class RubricScores(BaseModel):
    communication: int
    problem_solving: int
    technical_depth: int
    ownership: int
    culture_fit: int
    overall_recommendation: str
    risk_flags: List[str]
    follow_up_questions: List[str]


class PipelineRunResponse(BaseModel):
    candidate_profile: Dict
    interview_questions: List[InterviewQuestion]
    rubric_scores: RubricScores
    final_report: str