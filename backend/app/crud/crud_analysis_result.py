from sqlalchemy.orm import Session, joinedload
from app.db import models
from app.schemas import analysis_result as ar_schema
from datetime import date
from typing import List, Optional

def get_analysis_result(db: Session, result_id: int, owner_id: int) -> models.AnalysisResult | None:
    return (
        db.query(models.AnalysisResult)
        .options(joinedload(models.AnalysisResult.photo_group))
        .join(models.PhotoGroup, models.AnalysisResult.photo_group_id == models.PhotoGroup.id)
        .join(models.Field, models.PhotoGroup.field_id == models.Field.id)
        .filter(models.Field.owner_id == owner_id)
        .filter(models.AnalysisResult.id == result_id)
        .first()
    )

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


def get_analysis_results_for_field(db: Session, field_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[models.AnalysisResult]:
    query = (
        db.query(models.AnalysisResult)
        .join(models.PhotoGroup, models.AnalysisResult.photo_group_id == models.PhotoGroup.id)
        .filter(models.PhotoGroup.field_id == field_id)
    )
    
    if start_date:
        query = query.filter(models.PhotoGroup.capture_date >= start_date)
    
    if end_date:
        query = query.filter(models.PhotoGroup.capture_date <= end_date)
    
    return query.all()
