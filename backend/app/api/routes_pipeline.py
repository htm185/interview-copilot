import json
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import PipelineRunRequest, PipelineRunResponse
from app.orchestrator.pipeline import run_pipeline
from app.db.deps import get_db
from app.db.models_pipeline_run import PipelineRun

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
def pipeline_run(payload: PipelineRunRequest, db: Session = Depends(get_db)):
    started = time.time()
    try:
        result = run_pipeline(payload)

        row = PipelineRun(
            cv_text=payload.cv_text,
            jd_text=payload.jd_text,
            interview_notes=payload.interview_notes,
            result_json=result.model_dump_json(),
            status="success",
            error_message=None,
        )
        db.add(row)
        db.commit()

        duration_ms = int((time.time() - started) * 1000)
        print(f"[pipeline] success duration_ms={duration_ms}")
        return result

    except Exception as e:
        db.add(PipelineRun(
            cv_text=payload.cv_text,
            jd_text=payload.jd_text,
            interview_notes=payload.interview_notes,
            result_json="{}",
            status="failed",
            error_message=str(e),
        ))
        db.commit()
        duration_ms = int((time.time() - started) * 1000)
        print(f"[pipeline] failed duration_ms={duration_ms} error={e}")
        raise HTTPException(status_code=500, detail="Pipeline execution failed")


@router.get("/runs")
def list_pipeline_runs(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(PipelineRun)
        .order_by(PipelineRun.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "status": r.status,
            "error_message": r.error_message,
            "created_at": r.created_at,
        }
        for r in rows
    ]