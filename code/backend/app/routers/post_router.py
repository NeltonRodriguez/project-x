from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlmodel import Session
from app.database import get_session
from app.services import post_service
from app.schemas.post_schema import PostRead, PostCreate
from app.models.post_model import Post
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostRead])
def get_all_posts(session: Session = Depends(get_session)):
    return post_service.get_posts(session)


@router.get("/search/", response_model=List[PostRead])
def search_posts(
    name: str = Query(..., min_length=2, description="Search term (min 2 characters)"),
    session: Session = Depends(get_session)
):
    posts = post_service.search_posts_by_name(session, name.strip())
    
    if not posts:
        raise HTTPException(
            status_code=404,
            detail=f"Not found by name '{name}'"
        )
    
    return posts

@router.get("/{post_id}", response_model=PostRead)
def get_single_post(post_id: int, session: Session = Depends(get_session)):
    post = post_service.get_post(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostRead, status_code=201)
async def create_post_with_files(
    name: str = Form(...),
    content: str = Form(...),
    price: float = Form(...),
    category_id: Optional[int] = Form(None),
    images: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    """Create a new post with file uploads"""
    try:
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Max 10 images")
        
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg+xml']
        for file in images:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{file.filename}' is not a valid type"
                )
        
        new_post = await post_service.create_post_with_files(
            session=session,
            name=name,
            content=content,
            price=price,
            image_files=images,
            category_id=category_id
        )
        
        return new_post
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/from-urls", response_model=PostRead, status_code=201)
def create_post_from_urls(
    post_data: PostCreate,
    session: Session = Depends(get_session)
):
    """Create a post with image URLs"""
    try:
        new_post = Post(**post_data.model_dump())
        return post_service.create_post(session, new_post)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{post_id}", response_model=PostRead)
def update_existing_post(
    post_id: int,
    post_data: PostCreate,
    session: Session = Depends(get_session)
):
    """Update an existing post"""
    try:
        post = post_service.update_post(session, post_id, post_data.model_dump())
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return post
    except ValueError as e:
        # Category doesn't exist, validation errors → 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors → 500
        print(f"❌ Unexpected error in update_post: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/category/{category_id}", response_model=List[PostRead])
def get_posts_by_category(
    category_id: int,
    session: Session = Depends(get_session)
):
    """Get all posts in a specific category"""
    from app.models.category_model import Category
    
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    if not category.posts:
        raise HTTPException(
            status_code=404,
            detail=f"No hay posts en la categoría '{category.name}'"
        )
    
    return category.posts

@router.delete("/{post_id}", status_code=204)
def delete_existing_post(
    post_id: int,
    session: Session = Depends(get_session)
):
    """Delete a post"""
    result = post_service.delete_post(session, post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return None