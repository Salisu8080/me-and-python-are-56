import os
import sys
from PIL import Image

def optimize_image(image_path, output_path, quality=10):
    try:
        with Image.open(image_path) as img:
            img_format = img.format
            if img_format not in ["JPEG", "JPG", "PNG", "WEBP"]:
                print(f"Skipping unsupported format: {image_path}")
                return
            
            # Convert PNG to RGB before saving to optimize
            if img_format == "PNG":
                img = img.convert("RGB")
            
            img.save(output_path, format=img_format, optimize=True, quality=quality)
            print(f"Optimized: {output_path}")
    except Exception as e:
        print(f"Error optimizing {image_path}: {e}")

def optimize_images_in_folder(input_folder, output_folder, quality=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_folder, file)
                optimize_image(input_path, output_path, quality)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python optimize_images.py <input_folder> <output_folder> [quality]")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    optimize_images_in_folder(input_folder, output_folder, quality)
    
#RUN
#python optimize_image.py image_input image_output 10