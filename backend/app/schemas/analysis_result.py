from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel
from datetime import date

# 为了避免循环导入，我们只在类型检查时导入
if TYPE_CHECKING:
    from .photogroup import PhotoGroup

class AnalysisResultBase(BaseModel):
    coverage: Optional[float] = None
    avg_plant_height: Optional[float] = None
    height_std_dev: Optional[float] = None
    canopy_color_index: Optional[float] = None
    uniformity_index: Optional[float] = None
    tiller_density_estimate: Optional[float] = None
    panicles_per_mu: Optional[float] = None
    est_basic_seedlings_per_mu: Optional[float] = None
    lodging_status: Optional[str] = None
    estimated_leaf_age: Optional[float] = None
    estimated_tillers_per_plant: Optional[float] = None
    notes: Optional[str] = None
    gemini_analysis_text: Optional[str] = None
    gemini_suggestions: Optional[str] = None
    pest_risk: Optional[str] = None
    leaf_color_health: Optional[str] = None
    estimated_row_spacing_cm: Optional[float] = None
    estimated_plant_spacing_cm: Optional[float] = None
    seedlings_per_mu: Optional[float] = None

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResult(AnalysisResultBase):
    id: int
    photo_group_id: int
    # 使用字符串类型声明避免循环导入
    photo_group: Optional['PhotoGroup'] = None

    class Config:
        from_attributes = True

