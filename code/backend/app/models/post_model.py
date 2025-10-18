from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional

class Post(SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    images: List[str] = Field(sa_column=Column(JSON))  # almacena lista de URLs/paths
    price: float