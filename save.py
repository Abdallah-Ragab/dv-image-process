from PIL import Image
import io, os
from exceptions import SaveError

def save(input_path, output_path, min_resolution=600, max_resolution=1200, max_file_size=240):
    try:
        # Open the input image
        img = Image.open(input_path)

        # Get the original image dimensions
        width, height = img.size

        # Check if the image is already within the desired resolution and aspect ratio
        if width == height and min_resolution <= width <= max_resolution:
            # No need to compress, just save the original image
            img.save(output_path)
            return

        # Calculate the new dimensions while maintaining the aspect ratio
        new_width, new_height = width, height
        if width > max_resolution:
            new_width = max_resolution
            new_height = int((max_resolution / width) * height)

        # Resize the image to the new dimensions
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Save the compressed image with varying quality
        quality = 95
        while True:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality,)
            buffer_size = buffer.tell()
            if buffer_size / 1024 <= max_file_size:
                break
            quality -= 5

        # Save the final compressed image
        img.save(output_path, format="JPEG", quality=quality)

    except Exception as e:
        raise SaveError(f"Error: {e}")

