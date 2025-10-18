from sqlmodel import Session, select
from app.models.post_model import Post
from datetime import datetime
import cloudinary.uploader
from fastapi import UploadFile
from typing import List


async def upload_files_to_cloudinary(
    files: List[UploadFile], 
    public_prefix: str = "post"
) -> List[str]:
    """
    Upload actual files to Cloudinary.
    Accepts UploadFile objects from FastAPI.
    Validates that all files are images.
    """
    uploaded_urls = []
    
    # Allowed image MIME types
    allowed_types = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
        'image/webp', 'image/bmp', 'image/svg+xml', 'image/tiff'
    }
    
    # Allowed file extensions
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.tif'}
    
    for i, file in enumerate(files):
        try:
            # Validate file has a filename
            if not file.filename:
                raise ValueError(f"Archivo en posición {i} no tiene nombre")
            
            # Get file extension
            file_extension = None
            if '.' in file.filename:
                file_extension = '.' + file.filename.rsplit('.', 1)[1].lower()
            
            # Validate MIME type
            if file.content_type not in allowed_types:
                raise ValueError(
                    f"Archivo '{file.filename}' tiene un tipo no permitido: {file.content_type}. "
                    f"Solo se permiten imágenes (JPEG, PNG, GIF, WEBP, BMP, SVG, TIFF)"
                )
            
            # Validate file extension
            if file_extension and file_extension not in allowed_extensions:
                raise ValueError(
                    f"Archivo '{file.filename}' tiene una extensión no permitida: {file_extension}. "
                    f"Extensiones permitidas: {', '.join(sorted(allowed_extensions))}"
                )
            
            # Read file content
            file_content = await file.read()
            
            # Validate file size (e.g., max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if len(file_content) > max_size:
                raise ValueError(
                    f"Archivo '{file.filename}' es demasiado grande ({len(file_content) / (1024*1024):.2f}MB). "
                    f"Tamaño máximo permitido: 10MB"
                )
            
            # Validate file is not empty
            if len(file_content) == 0:
                raise ValueError(f"Archivo '{file.filename}' está vacío")
            
            # Upload to Cloudinary
            print(f"📤 Uploading {file.filename} ({len(file_content) / 1024:.2f}KB)...")
            result = cloudinary.uploader.upload(
                file_content,
                public_id=f"{public_prefix}_{i}_{datetime.now().timestamp()}",
                resource_type="image",
                folder="posts"  # Organize in a folder
            )
            
            uploaded_urls.append(result["secure_url"])
            print(f"✅ {file.filename} uploaded successfully")
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
        except ValueError as ve:
            # Re-raise validation errors
            raise ve
        except Exception as e:
            print(f"❌ Error uploading {file.filename}: {str(e)}")
            raise ValueError(f"Error al subir '{file.filename}': {str(e)}")
    
    return uploaded_urls


def upload_images_to_cloudinary(
    image_data_list: list[str], 
    public_prefix: str = "post"
) -> list[str]:
    """
    Upload images from URLs or base64.
    (Keep this for URL-based uploads)
    """
    uploaded_urls = []
    
    for i, image_data in enumerate(image_data_list):
        try:
            if not image_data or image_data.strip() == "":
                print(f"⚠️ Skipping empty image at index {i}")
                continue
            
            if "cloudinary.com" in image_data:
                print(f"✅ Image {i} is already on Cloudinary")
                uploaded_urls.append(image_data)
                continue
            
            if image_data.startswith('http://') or image_data.startswith('https://'):
                print(f"📤 Uploading image {i} from URL...")
                result = cloudinary.uploader.upload(
                    image_data,
                    public_id=f"{public_prefix}_{i}_{datetime.now().timestamp()}",
                    resource_type="image",
                    folder="posts"
                )
                uploaded_urls.append(result["secure_url"])
                print(f"✅ Image {i} uploaded successfully")
                
            elif image_data.startswith('data:image'):
                print(f"📤 Uploading image {i} from base64...")
                result = cloudinary.uploader.upload(
                    image_data,
                    public_id=f"{public_prefix}_{i}_{datetime.now().timestamp()}",
                    resource_type="image",
                    folder="posts"
                )
                uploaded_urls.append(result["secure_url"])
                print(f"✅ Image {i} uploaded successfully")
                
            else:
                raise ValueError(
                    f"Invalid image data at index {i}. "
                    f"Expected URL or base64, got: '{image_data[:50]}'"
                )
                
        except Exception as e:
            print(f"❌ Error uploading image {i}: {str(e)}")
            raise Exception(f"Failed to upload image {i}: {str(e)}")
    
    return uploaded_urls


async def create_post_with_files(
    session: Session,
    name: str,
    content: str,
    price: float,
    image_files: List[UploadFile]
) -> Post:
    """
    Create a post with file uploads.
    """
    # Validate number of images
    if len(image_files) > 10:
        raise ValueError("Máximo 10 imágenes permitidas")
    
    # Upload files to Cloudinary
    print(f"📤 Processing {len(image_files)} file uploads...")
    image_urls = await upload_files_to_cloudinary(
        image_files,
        public_prefix=f"post_{datetime.now().timestamp()}"
    )
    
    # Create post object
    new_post = Post(
        name=name,
        content=content,
        price=price,
        images=image_urls
    )
    
    # Save to database
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    
    return new_post


def create_post(session: Session, post_data: Post) -> Post:
    """
    Create a post with URLs (legacy support).
    """
    if len(post_data.images) > 10:
        raise ValueError("Máximo 10 imágenes permitidas")
    
    if post_data.images and len(post_data.images) > 0:
        print(f"📤 Processing {len(post_data.images)} images...")
        post_data.images = upload_images_to_cloudinary(
            post_data.images,
            public_prefix=f"post_{datetime.now().timestamp()}"
        )
    
    session.add(post_data)
    session.commit()
    session.refresh(post_data)
    
    return post_data


def get_posts(session: Session):
    return session.exec(select(Post)).all()


def get_post(session: Session, post_id: int):
    return session.get(Post, post_id)


def update_post(session: Session, post_id: int, data: dict) -> Post | None:
    post = session.get(Post, post_id)
    if not post:
        return None
    
    if "images" in data and len(data["images"]) > 10:
        raise ValueError("Máximo 10 imágenes permitidas")
    
    if "images" in data and data["images"]:
        print(f"📤 Processing {len(data['images'])} images for update...")
        data["images"] = upload_images_to_cloudinary(
            data["images"],
            public_prefix=f"post_{post_id}"
        )
    
    for key, value in data.items():
        setattr(post, key, value)
    
    post.updated_at = datetime.now()
    
    session.add(post)
    session.commit()
    session.refresh(post)
    
    return post


def delete_post(session: Session, post_id: int):
    post = session.get(Post, post_id)
    if not post:
        return None
    
    session.delete(post)
    session.commit()
    
    return True