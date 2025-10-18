from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import List, Optional

class PostBase(BaseModel):
    name: str
    content: str
    images: List[str]
    price: float

    @field_validator("name", "content")
    def not_empty(cls, v, field):
        if not v.strip():
            raise ValueError(f"{field.name} is required")
        return v

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True