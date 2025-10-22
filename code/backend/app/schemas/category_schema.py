from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    
    @field_validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Category name is required")
        return v.strip()


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    category_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True