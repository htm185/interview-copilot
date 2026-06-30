from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    cv_text = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=False)
    interview_notes = Column(Text, nullable=False)

    result_json = Column(Text, nullable=False)   # lưu response JSON string
    status = Column(Text, nullable=False, default="success")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)