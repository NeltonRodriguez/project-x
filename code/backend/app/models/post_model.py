from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category_model import Category


class Post(SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    images: List[str] = Field(sa_column=Column(JSON))
    price: float
    
    # Foreign Key to Category
    category_id: Optional[int] = Field(default=None, foreign_key="category.category_id")
    
    # Relationship: Many posts belong to one category
    category: Optional["Category"] = Relationship(back_populates="posts")