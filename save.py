from PIL import Image
import numpy, cv2
import io, os
from pathlib import Path
from exceptions import SaveError
from log_config import logger
from models.constants import OBJ

def compress(input_image, output_dir, output_filename = None, min_resolution=600, max_resolution=1000, max_file_size=240, quality_suffix=False):
    try:
        logger.trace(f"Saving image to {output_dir}...")

        if output_filename:
            filename = output_filename
        elif isinstance(input_image, str) or isinstance(input_image, Path):
            filename = Path(input_image).name
        else:
            filename = "output.jpg"

        file_name = Path(filename).name.split(".")[0]
        file_extension = Path(filename).name.split(".")[1]

        output_filename = f"{file_name}.{file_extension}"
        output_path = os.path.join(output_dir, output_filename)



        if isinstance(input_image, str) or isinstance(input_image, Path):
            img = Image.open(input_image)
        elif isinstance(input_image, Image.Image):
            img = input_image
        elif isinstance(input_image, (list, numpy.ndarray)):
            if isinstance(input_image, list):
                input_image = numpy.array(input_image)
            if len(input_image.shape) == 2:  # Grayscale image
                img = Image.fromarray(input_image, "L")
            elif len(input_image.shape) == 3:  # Color image
                input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(input_image, "RGB")
        else:
            raise SaveError(f"Invalid input image type: {type(input_image)}")

        # Get the original image dimensions
        width, height = img.size

        # Check if the image is already within the desired resolution and aspect ratio
        if width == height and min_resolution <= width <= max_resolution and os.path.getsize(output_path) / 1024 <= max_file_size:
            # No need to compress, just save the original image
            logger.info("Image already within desired resolution and aspect ratio. No need to compress. Saving original image...")
            img.save(output_path)
            return OBJ(success=True, path=output_path, size=os.path.getsize(output_path) / 1024, quality=100, dimensions=OBJ(width=width, height=height))

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

        output_filename = f"{file_name}{'_' + quality if quality_suffix else ''}.{file_extension}"
        output_path = os.path.join(output_dir, output_filename)

        # Save the final compressed image
        img.save(output_path, format="JPEG", quality=quality)
        logger.success(f"Image saved with quality {quality} and size {buffer_size / 1024} KB to {output_path}")
        return OBJ(success=True, path=output_path, size=buffer_size / 1024, quality=quality, dimensions=OBJ(width=new_width, height=new_height))

    except Exception as e:
        raise SaveError(f'{e.__traceback__.tb_lineno}:{e}')


