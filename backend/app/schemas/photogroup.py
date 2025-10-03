from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import date
from pydantic import BaseModel
from app.db.models import AnalysisStatusEnum

# 为了避免循环导入，我们只在类型检查时导入
if TYPE_CHECKING:
    from .analysis_result import AnalysisResult

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
    # 使用字符串类型声明避免循环导入
    analysis_result: Optional['AnalysisResult'] = None

    class Config:
        from_attributes = True

