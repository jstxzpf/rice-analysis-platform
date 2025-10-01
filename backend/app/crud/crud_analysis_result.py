from sqlalchemy.orm import Session
from app.db import models
from app.schemas import analysis_result as ar_schema
from datetime import date
from typing import List

def create_analysis_result(db: Session, photo_group_id: int, result_data: dict) -> models.AnalysisResult:
    db_result = models.AnalysisResult(
        photo_group_id=photo_group_id,
        **result_data
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_analysis_results_for_period(db: Session, owner_id: int, start_date: date, end_date: date) -> List[models.AnalysisResult]:
    return (
        db.query(models.AnalysisResult)
        .join(models.PhotoGroup, models.AnalysisResult.photo_group_id == models.PhotoGroup.id)
        .join(models.Field, models.PhotoGroup.field_id == models.Field.id)
        .filter(models.Field.owner_id == owner_id)
        .filter(models.PhotoGroup.capture_date >= start_date)
        .filter(models.PhotoGroup.capture_date <= end_date)
        .all()
    )
