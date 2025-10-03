from __future__ import annotations
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.db.models import AnalysisStatusEnum

class PhotoGroupBase(BaseModel):
    capture_date: date
    rice_variety: Optional[str] = None

class PhotoGroupCreate(PhotoGroupBase):
    field_id: int

class PhotoGroupInDBBase(PhotoGroupBase):
    id: int
    field_id: int
    drone_photo_path: str
    side_photo_05m_path: str
    side_photo_3m_horizontal_path: str
    side_photo_3m_vertical_path: str
    analysis_status: AnalysisStatusEnum
    celery_task_id: Optional[str] = None

    class Config:
        from_attributes = True

class PhotoGroup(PhotoGroupInDBBase):
    analysis_result: Optional['AnalysisResult'] = None  # Use string reference to avoid circular import

    class Config:
        from_attributes = True

