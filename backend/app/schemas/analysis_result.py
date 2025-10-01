from typing import Optional
from pydantic import BaseModel
from datetime import date

class AnalysisResultBase(BaseModel):
    coverage: Optional[float] = None
    avg_plant_height: Optional[float] = None
    height_std_dev: Optional[float] = None
    canopy_color_index: Optional[float] = None
    uniformity_index: Optional[float] = None
    tiller_density_estimate: Optional[float] = None
    panicles_per_mu: Optional[float] = None
    lodging_status: Optional[str] = None
    estimated_leaf_age: Optional[float] = None
    estimated_tillers_per_plant: Optional[float] = None
    notes: Optional[str] = None
    gemini_analysis_text: Optional[str] = None
    gemini_suggestions: Optional[str] = None
    pest_risk: Optional[str] = None
    leaf_color_health: Optional[str] = None

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResult(AnalysisResultBase):
    id: int
    photo_group_id: int

    class Config:
        from_attributes = True

# Schema for providing field info along with analysis
class FieldForAnalysis(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class PhotoGroupForAnalysis(BaseModel):
    capture_date: date
    field: FieldForAnalysis
    class Config:
        from_attributes = True

class AnalysisResultWithField(AnalysisResult):
    photo_group: PhotoGroupForAnalysis
