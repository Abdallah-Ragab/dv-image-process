from PIL import Image
import io, os
from pathlib import Path
from exceptions import SaveError
from log_config import logger

def compress(input_image, output_path, output_filename = None, min_resolution=600, max_resolution=1200, max_file_size=240):
    try:
        logger.trace(f"Saving image to {output_path}...")
        input_filename = Path(input_image).name.split(".")[0]
        input_extension = Path(input_image).name.split(".")[1]
        filename = output_filename or f"{input_filename}_compressed.{input_extension}"
        output_path = os.path.join(output_path, filename)

        # Open the input image
        if isinstance(input_image, str) or isinstance(input_image, bytes) or isinstance(input_image, Path):
            img = Image.open(input_image)
        elif isinstance(input_image, Image.Image):
            img = input_image
        elif isinstance(input_image, list):
            img = Image.fromarray(input_image, "RGB")
        else:
            raise SaveError(f"Invalid input image type: {type(input_image)}")

        # Get the original image dimensions
        width, height = img.size

        # Check if the image is already within the desired resolution and aspect ratio
        if width == height and min_resolution <= width <= max_resolution:
            # No need to compress, just save the original image
            logger.info("Image already within desired resolution and aspect ratio. No need to compress. Saving original image...")
            img.save(output_path)
            return True

        # Calculate the new dimensions while maintaining the aspect ratio
        new_width, new_height = width, height
        if width > max_resolution:
            new_width = max_resolution
            new_height = int((max_resolution / width) * height)

        # Resize the image to the new dimensions
        img = img.resize((new_width, new_height), Image.LANCZOS)
        logger.trace(f"Image resized to {new_width}x{new_height}")

        # Save the compressed image with varying quality
        quality = 95
        while True:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality,)
            buffer_size = buffer.tell()
            if buffer_size / 1024 <= max_file_size:
                break
            quality -= 5

        filename = output_filename or f"{input_filename}_compressed_{quality}.{input_extension}"
        output_path = os.path.join(output_path, filename)

        # Save the final compressed image
        img.save(output_path, format="JPEG", quality=quality)
        logger.success(f"Image saved with quality {quality} and size {buffer_size / 1024} KB to {output_path}")
        return True

    except Exception as e:
        raise SaveError(e)


