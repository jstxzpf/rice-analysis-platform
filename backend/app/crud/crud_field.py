from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.db import models
from app.schemas import field as field_schema

def get_field(db: Session, field_id: int):
    return db.query(models.Field).filter(models.Field.id == field_id).first()

def get_fields_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Field]:
    return db.query(models.Field).filter(models.Field.owner_id == owner_id).offset(skip).limit(limit).all()

def create_field_for_user(db: Session, field: field_schema.FieldCreate, owner_id: int) -> models.Field:
    field_data = field.dict()
    planting_date = field_data.get("planting_date")
    if isinstance(planting_date, datetime):
        field_data["planting_date"] = planting_date.date()
        
    db_field = models.Field(**field_data, owner_id=owner_id)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

def update_field(db: Session, field_id: int, field_update: field_schema.FieldUpdate) -> models.Field:
    db_field = get_field(db, field_id)
    if db_field:
        update_data = field_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_field, key, value)
        db.commit()
        db.refresh(db_field)
    return db_field

def delete_field(db: Session, field_id: int) -> models.Field:
    db_field = get_field(db, field_id)
    if db_field:
        db.delete(db_field)
        db.commit()
    return db_field