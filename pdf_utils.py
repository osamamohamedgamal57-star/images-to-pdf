"""Turns a list of image files into one PDF file, and cleans the name the user chooses for it."""
import re

from PIL import Image, ImageOps

DEFAULT_NAME = "images"
MAX_NAME_LENGTH = 100


def clean_pdf_name(text):
    """Turn what the user typed into a safe file name that ends with .pdf.
    Removes characters that are not allowed in file names, and falls back to a default name."""
    name = (text or "").strip()
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", name)  # characters Windows does not allow
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    name = name.strip(" .")[:MAX_NAME_LENGTH].strip(" .")
    return (name or DEFAULT_NAME) + ".pdf"


def images_to_pdf(image_paths, output_path):
    """Create a PDF with one page per image, in the order given."""
    if not image_paths:
        raise ValueError("No images were given")

    pages = []
    for path in image_paths:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)  # fix photos that are rotated sideways
            pages.append(img.convert("RGB"))    # PDF pages cannot have transparency

    pages[0].save(output_path, "PDF", save_all=True, append_images=pages[1:])
    return output_path
