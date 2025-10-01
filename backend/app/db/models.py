# backend/app/db/models.py
from sqlalchemy import (Column, Integer, String, Float, DateTime, Date, Text,
                        ForeignKey, Enum as SQLAlchemyEnum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base

class AnalysisStatusEnum(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    fields = relationship("Field", back_populates="owner")

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    area = Column(Float) # 面积（亩）
    planting_date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="fields")
    photo_groups = relationship("PhotoGroup", back_populates="field", cascade="all, delete-orphan")

class PhotoGroup(Base):
    __tablename__ = "photo_groups"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    capture_date = Column(Date, nullable=False)
    rice_variety = Column(String(100)) # 水稻品种
    drone_photo_path = Column(String(512), nullable=False)
    side_photo_05m_path = Column(String(512), nullable=False)
    side_photo_3m_horizontal_path = Column(String(512), nullable=False)
    side_photo_3m_vertical_path = Column(String(512), nullable=False)
    analysis_status = Column(SQLAlchemyEnum(AnalysisStatusEnum), default=AnalysisStatusEnum.PENDING)
    celery_task_id = Column(String(255), index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", back_populates="photo_groups")
    analysis_result = relationship("AnalysisResult", back_populates="photo_group", uselist=False, cascade="all, delete-orphan")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    photo_group_id = Column(Integer, ForeignKey("photo_groups.id"), unique=True, nullable=False)
    coverage = Column(Float) # 冠层覆盖度 (%)
    avg_plant_height = Column(Float) # 平均株高 (cm)
    height_std_dev = Column(Float) # 株高标准差，反映整齐度
    canopy_color_index = Column(Float) # 冠层颜色指标 (如G/R比)
    uniformity_index = Column(Float) # 均匀度指数 (如CV)
    tiller_density_estimate = Column(Float) # 分蘖密度估算 (株/m²)
    panicles_per_mu = Column(Float, nullable=True) # 亩穗数估算
    lodging_status = Column(String(100), nullable=True) # 倒伏评估
    estimated_leaf_age = Column(Float, nullable=True) # 估算叶龄
    estimated_tillers_per_plant = Column(Float, nullable=True) # 估算单株分蘖数
    notes = Column(String(1000)) # 分析备注或异常
    
    # Fields for Gemini AI Analysis
    gemini_analysis_text = Column(Text, nullable=True) # 详细文字分析
    gemini_suggestions = Column(Text, nullable=True) # 农事建议
    pest_risk = Column(String(100), nullable=True) # 病虫害风险
    leaf_color_health = Column(String(100), nullable=True) # 叶色健康状况

    analysis_time = Column(DateTime(timezone=True), server_default=func.now())

    photo_group = relationship("PhotoGroup", back_populates="analysis_result")
