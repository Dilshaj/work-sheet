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
    Uploads a file to Cloudinary and returns the secure URL.
    :param file: The file-like object or path
    :param folder: Cloudinary folder name
    :return: Secure URL of the uploaded image
    """
    try:
        response = cloudinary.uploader.upload(file, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
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
