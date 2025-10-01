from sqlalchemy.orm import Session
from app.db import models
from app.schemas import photogroup as photogroup_schema

def create_photo_group(db: Session, field_id: int, capture_date: str, rice_variety: str, drone_photo_path: str, side_photo_05m_path: str, side_photo_3m_horizontal_path: str, side_photo_3m_vertical_path: str) -> models.PhotoGroup:
    db_photogroup = models.PhotoGroup(
        field_id=field_id,
        capture_date=capture_date,
        rice_variety=rice_variety,
        drone_photo_path=drone_photo_path,
        side_photo_05m_path=side_photo_05m_path,
        side_photo_3m_horizontal_path=side_photo_3m_horizontal_path,
        side_photo_3m_vertical_path=side_photo_3m_vertical_path
    )
    db.add(db_photogroup)
    db.commit()
    db.refresh(db_photogroup)
    return db_photogroup

def update_task_id(db: Session, photo_group_id: int, task_id: str) -> models.PhotoGroup:
    db_photogroup = db.query(models.PhotoGroup).filter(models.PhotoGroup.id == photo_group_id).first()
    if db_photogroup:
        db_photogroup.celery_task_id = task_id
        db.commit()
        db.refresh(db_photogroup)
    return db_photogroup
