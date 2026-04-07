import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image(file, folder="eduprova"):
    """
    Safely uploads a file-like object to Cloudinary by first saving to a temp file.
    This prevents stream-closure issues in certain cloud deployments.
    """
    import tempfile
    import os
    try:
        # Crucial: Ensure we are at the start of the file for reading
        if hasattr(file, "seek"):
            file.seek(0)
            
        # Create a temp file to ensure the data is fully read/available
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        
        try:
            response = cloudinary.uploader.upload(tmp_path, folder=folder)
            return response.get("secure_url")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        print(f"Cloudinary Robust Upload Error: {e}")
        return None

def upload_base64_image(base64_str, folder="projects"):
    """
    Uploads a base64 encoded image to Cloudinary.
    :param base64_str: The base64 string
    :param folder: Cloudinary folder name
    :return: Secure URL of the uploaded image
    """
    try:
        # Cloudinary handles base64 strings directly if they are properly formatted
        # e.g., "data:image/png;base64,iVBORw0KG..."
        response = cloudinary.uploader.upload(base64_str, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary Base64 Upload Error: {e}")
        return None
