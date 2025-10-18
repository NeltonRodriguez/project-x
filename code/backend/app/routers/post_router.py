from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from app.database import get_session
from app.services import post_service
from app.schemas.post_schema import PostRead, PostCreate
from app.models.post_model import Post
from typing import List, Optional
import json

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


# NEW: File upload endpoint
@router.post("/", response_model=PostRead, status_code=201)
async def create_post_with_files(
    name: str = Form(...),
    content: str = Form(...),
    price: float = Form(...),
    images: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    """
    Create a new post with file uploads.
    Accepts multipart/form-data with:
    - name: string
    - content: string  
    - price: float
    - images: multiple image files (max 10)
    
    Allowed image types: JPEG, PNG, GIF, WEBP, BMP, SVG
    """
    try:
        # Validate number of images
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Máximo 10 imágenes permitidas")
        
        # Validate all files are images before processing
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg+xml']
        for file in images:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo '{file.filename}' no es una imagen válida. Tipo: {file.content_type}. "
                           f"Formatos permitidos: JPEG, PNG, GIF, WEBP, BMP, SVG"
                )
        
        # Create post with file uploads
        new_post = await post_service.create_post_with_files(
            session=session,
            name=name,
            content=content,
            price=price,
            image_files=images
        )
        
        return new_post
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")