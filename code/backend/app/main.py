from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routers import post_router
import cloudinary
import json
from pathlib import Path
import os


def load_secrets():
    """
    Load secrets from environment variables or secrets.json file.
    Priority: Environment variables > secrets.json
    """
    # Try environment variables first (production)
    env_secrets = {
        "cloudinary_cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "cloudinary_api_key": os.getenv("CLOUDINARY_API_KEY"),
        "cloudinary_api_secret": os.getenv("CLOUDINARY_API_SECRET")
    }
    
    if all(env_secrets.values()):
        return env_secrets
    
    # Fallback to secrets.json file (local development)
    secrets_path = Path(__file__).parent / "secrets.json"
    
    if secrets_path.exists():
        try:
            with open(secrets_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in secrets.json: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read secrets.json: {e}")
    
    raise RuntimeError("No secrets found. Set environment variables or create secrets.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    try:
        secrets = load_secrets()
        
        # Validate secrets
        required_keys = ["cloudinary_cloud_name", "cloudinary_api_key", "cloudinary_api_secret"]
        missing_keys = [key for key in required_keys if not secrets.get(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required secrets: {', '.join(missing_keys)}")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=secrets["cloudinary_cloud_name"],
            api_key=secrets["cloudinary_api_key"],
            api_secret=secrets["cloudinary_api_secret"],
            secure=True
        )
        
        # Create database tables
        create_db_and_tables()
        
        yield
        
    except Exception as e:
        print(f"Startup error: {e}")
        raise


# Initialize FastAPI app
app = FastAPI(
    title="Posts API",
    description="API for managing posts with image uploads",
    version="1.0.0",
    root_path="/api/v1",
    lifespan=lifespan
)

# Register routers
app.include_router(post_router.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Posts API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/test-upload")
def test_upload():
    """Test Cloudinary upload"""
    try:
        result = cloudinary.uploader.upload(
            "https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
            public_id="test_upload",
            folder="tests"
        )
        return {"status": "success", "url": result["secure_url"]}
    except Exception as e:
        return {"status": "failed", "error": str(e)}