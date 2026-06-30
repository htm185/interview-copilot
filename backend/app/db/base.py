from sqlalchemy.orm import declarative_base
Base = declarative_base()

# đảm bảo model được import để create_all thấy
from app.db.models_pipeline_run import PipelineRun  # noqa