from sqlmodel import Session, select
from app.models.category_model import Category
from typing import List


def get_categories(session: Session) -> List[Category]:
    """Get all categories"""
    return session.exec(select(Category)).all()


def get_category(session: Session, category_id: int) -> Category | None:
    """Get a single category by ID"""
    return session.get(Category, category_id)


def get_category_by_name(session: Session, name: str) -> Category | None:
    """Get category by name (case-insensitive)"""
    return session.exec(
        select(Category).where(Category.name.ilike(name))
    ).first()


def create_category(session: Session, category_data: Category) -> Category:
    """Create a new category"""
    # Check if category with same name exists
    existing = get_category_by_name(session, category_data.name)
    if existing:
        raise ValueError(f"Category '{category_data.name}' already exists")
    
    session.add(category_data)
    session.commit()
    session.refresh(category_data)
    return category_data


def update_category(session: Session, category_id: int, data: dict) -> Category | None:
    """Update a category"""
    category = session.get(Category, category_id)
    if not category:
        return None
    
    # Check if new name conflicts with existing category
    if "name" in data:
        existing = get_category_by_name(session, data["name"])
        if existing and existing.category_id != category_id:
            raise ValueError(f"Category '{data['name']}' already exists")
    
    for key, value in data.items():
        setattr(category, key, value)
    
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category_id: int) -> bool:
    """Delete a category"""
    category = session.get(Category, category_id)
    if not category:
        return False
    
    # Check if category has posts
    if category.posts:
        raise ValueError(
            f"Cannot eliminate '{category.name}' because it has {len(category.posts)} posts"
        )
    
    session.delete(category)
    session.commit()
    return True