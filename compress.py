from PIL import Image
import io, os

def compress_image(input_path, output_path, max_compression=20, min_resolution=600, max_resolution=1200, max_file_size=240):
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
            img.save(buffer, format="JPEG", quality=quality)
            buffer_size = buffer.tell()
            if buffer_size / 1024 <= max_file_size:
                break
            quality -= 5

        original_size = img.size[0] * img.size[1]
        compressed_size = new_width * new_height
        if original_size / compressed_size > max_compression:
            raise ValueError("Compression rate exceeds 20:1")

        # Save the final compressed image
        img.save(output_path, format="JPEG", quality=quality)

    except Exception as e:
        print(f"Error: {e}")


# # Example usage:
# for file in sorted(os.listdir("images/output"), key=lambda x: int(x.split(".")[0].split("-")[0])):
#     file_extension = file.split(".")[1]
#     file_name = file.split(".")[0]
#     input_image_path = f"images/output/{file}"
#     output_image_path = f"images/output/{file_name}-compressed.{file_extension}"
#     compress_image(input_image_path, output_image_path)
