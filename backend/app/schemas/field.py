from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, validator

# Shared properties
class FieldBase(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    area: Optional[float] = None
    planting_date: Optional[date] = None

    @validator("planting_date", pre=True, always=True)
    def validate_planting_date(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
            except ValueError:
                raise ValueError(f"Unable to parse date from string: {v}")
        return v

# Properties to receive on item creation
class FieldCreate(FieldBase):
    name: str
    
# Properties to receive on item update
class FieldUpdate(FieldBase):
    pass

# Properties shared by models stored in DB
class FieldInDBBase(FieldBase):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Field(FieldInDBBase):
    pass

# Properties properties stored in DB
class FieldInDB(FieldInDBBase):
    pass