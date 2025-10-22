import cloudinary
import json
from pathlib import Path

# Ruta al archivo de secretos
secrets_path = Path("code/backend/secrets.json")

# Cargar secretos
with open(secrets_path, "r") as f:
    secrets = json.load(f)

# Configurar Cloudinary
cloudinary.config(
    cloud_name=secrets["cloudinary_cloud_name"],
    api_key=secrets["cloudinary_api_key"],
    api_secret=secrets["cloudinary_api_secret"],
    secure=True
)