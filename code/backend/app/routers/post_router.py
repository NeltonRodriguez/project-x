from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from app.database import get_session
from app.services import post_service
from app.schemas.post_schema import PostRead, PostCreate
from app.models.post_model import Post
from typing import List

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostRead])
def get_all_posts(session: Session = Depends(get_session)):
    return post_service.get_posts(session)


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
    images: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    """Create a new post with file uploads"""
    try:
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Máximo 10 imágenes permitidas")
        
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg+xml']
        for file in images:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo '{file.filename}' no es una imagen válida"
                )
        
        new_post = await post_service.create_post_with_files(
            session=session,
            name=name,
            content=content,
            price=price,
            image_files=images
        )
        
        return new_post
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


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


# ADD THESE TWO ENDPOINTS:

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
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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