from app.models.schemas import (
    PipelineRunRequest,
    PipelineRunResponse,
    InterviewQuestion,
    RubricScores,
)
from app.agents.ingestion_agent import run_ingestion
from app.agents.question_agent import run_question_generation
from app.agents.evaluation_agent import run_evaluation
from app.agents.report_agent import run_report


def run_pipeline(data: PipelineRunRequest) -> PipelineRunResponse:
    candidate_profile = run_ingestion(data.cv_text, data.jd_text)

    raw_questions = run_question_generation(candidate_profile, data.jd_text)
    interview_questions = [InterviewQuestion(**q) for q in raw_questions]

    evaluation = run_evaluation(data.interview_notes)
    rubric_scores = RubricScores(**evaluation)

    final_report = run_report(
        candidate_profile=candidate_profile,
        interview_questions=raw_questions,
        rubric_scores=evaluation,
    )

    return PipelineRunResponse(
        candidate_profile=candidate_profile,
        interview_questions=interview_questions,
        rubric_scores=rubric_scores,
        final_report=final_report,
    )