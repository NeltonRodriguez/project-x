from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.services import category_service
from app.schemas.category_schema import CategoryRead, CategoryCreate
from app.models.category_model import Category
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryRead])
def get_all_categories(session: Session = Depends(get_session)):
    """Get all categories"""
    return category_service.get_categories(session)


@router.get("/{category_id}", response_model=CategoryRead)
def get_single_category(category_id: int, session: Session = Depends(get_session)):
    """Get a single category by ID"""
    category = category_service.get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=201)
def create_new_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session)
):
    """Create a new category"""
    try:
        new_category = Category(**category_data.model_dump())
        return category_service.create_category(session, new_category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", response_model=CategoryRead)
def update_existing_category(
    category_id: int,
    category_data: CategoryCreate,
    session: Session = Depends(get_session)
):
    """Update a category"""
    try:
        category = category_service.update_category(session, category_id, category_data.model_dump())
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
def delete_existing_category(
    category_id: int,
    session: Session = Depends(get_session)
):
    """Delete a category"""
    try:
        result = category_service.delete_category(session, category_id)
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))