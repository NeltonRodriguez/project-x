from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import List, Optional


class PostBase(BaseModel):
    name: str
    content: str
    images: List[str]
    price: float
    category_id: Optional[int] = None
    
    @field_validator("name", "content")
    def not_empty(cls, v, field):
        if not v.strip():
            raise ValueError(f"{field.field_name} is required")
        return v


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PostReadWithCategory(PostRead):
    """Post with category details"""
    category: Optional[dict] = None  # Will contain {category_id, name, description}