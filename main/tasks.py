import os
import logging
import zipfile
from django.conf import settings
from .models import Product

logger = logging.getLogger(__name__)

def process_pptx_slides(product_id, pptx_path, unique_id):
    logger.info(f"Starting slide processing for product_id={product_id}, pptx_path={pptx_path}")
    try:
        product = Product.objects.get(id=product_id)
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
        logger.info(f"Upload directory: {upload_dir}")

        image_paths = []
        # Extract images from PPTX (it's a ZIP file)
        with zipfile.ZipFile(pptx_path, 'r') as z:
            # First, try to get the default thumbnail
            if 'docProps/thumbnail.jpeg' in z.namelist():
                with z.open('docProps/thumbnail.jpeg') as thumb_file:
                    thumb_path = os.path.join(upload_dir, 'slide1.jpg')
                    with open(thumb_path, 'wb') as f:
                        f.write(thumb_file.read())
                    image_paths.append(os.path.join('uploads', unique_id, 'slide1.jpg'))
                    logger.info("Thumbnail extracted successfully as slide1.jpg")

            # Look for slide-specific images in ppt/media/
            media_files = [name for name in z.namelist() if name.startswith('ppt/media/') and name.endswith('.jpeg')]
            for idx, media_file in enumerate(media_files[:2], start=2):  # Start at 2 since thumbnail is slide1
                if idx > 3:  # Limit to 3 slides total
                    break
                with z.open(media_file) as media_data:
                    media_path = os.path.join(upload_dir, f'slide{idx}.jpg')
                    with open(media_path, 'wb') as f:
                        f.write(media_data.read())
                    image_paths.append(os.path.join('uploads', unique_id, f'slide{idx}.jpg'))
                    logger.info(f"Extracted media file as slide{idx}.jpg")

        # If no images were extracted, log a warning
        if not image_paths:
            logger.warning("No images found in PPTX file")
            product.status = 'failed'
            product.error_message = "No images could be extracted from the PPTX file"
            product.save(update_fields=['status', 'error_message'])
            return

        product.slide_images = image_paths
        product.status = 'processed'
        product.error_message = None
        product.save(update_fields=['slide_images', 'status', 'error_message'])
        logger.info(f"Slide images saved: {image_paths}")

    except Exception as e:
        error_message = f"Error processing product file: {str(e)}"
        logger.error(error_message)
        product = Product.objects.get(id=product_id)
        product.status = 'failed'
        product.error_message = error_message
        product.save(update_fields=['status', 'error_message'])