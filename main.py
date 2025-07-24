import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from utils.image_processor import get_max_dimensions, resize_image
import shutil
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/resize-image/")
async def resize_image_api(
    image: UploadFile = File(...),
    blog_name: str = Form(...),
    image_type: str = Form(...),  # "Hauptbild" or "Zusatzbild"
):
    try:
        logger.info(f"Received request: blog_name={blog_name}, image_type={image_type}, filename={image.filename}")

        contents = await image.read()
        logger.info(f"Read {len(contents)} bytes from uploaded image.")

        # Get max dimensions for the blog and image type
        max_w, max_h = get_max_dimensions(blog_name, image_type)
        logger.info(f"Max dimensions for {blog_name} ({image_type}): width={max_w}, height={max_h}")

        # Resize and compress
        resized_image_io = resize_image(contents, max_w, max_h)
        logger.info("Image resized successfully.")

        return StreamingResponse(resized_image_io, media_type="image/jpeg")

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=400, detail=str(e))
