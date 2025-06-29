#!/usr/bin/env python3

import sys
import shutil
import tempfile
from pathlib import Path

import zipfile
import rarfile
from PIL import Image
from enum import Enum


# Constants
class SupportedExtensions(Enum):
    CBZ = ".cbz"
    ZIP = ".zip"
    CBR = ".cbr"
    RAR = ".rar"


class ImageExtensions(Enum):
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    GIF = ".gif"
    BMP = ".bmp"
    TIFF = ".tiff"
    WEBP = ".webp"


SUPPORTED_EXTENSIONS = {ext.value for ext in SupportedExtensions}
IMAGE_EXTENSIONS = {ext.value for ext in ImageExtensions}


def collect_image_files(directory: Path) -> list[Path]:
    """Recursively collect all image files from directory."""
    image_files = []

    for item in directory.rglob("*"):
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
            image_files.append(item)

    return sorted(image_files)


def extract_archive(archive_path: Path, extract_to: Path) -> bool:
    """Extract archive to specified directory. Returns True on success."""
    try:
        extract_to.mkdir(parents=True, exist_ok=True)

        ext = archive_path.suffix.lower()
        if ext in {SupportedExtensions.CBZ.value, SupportedExtensions.ZIP.value}:
            print("Extracting pictures from CBZ/ZIP file...")
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                zip_file.extractall(extract_to)

        elif ext in {SupportedExtensions.CBR.value, SupportedExtensions.RAR.value}:
            print("Extracting pictures from CBR/RAR file...")
            with rarfile.RarFile(archive_path) as rar_file:
                rar_file.extractall(extract_to)
        else:
            print(f"Unsupported file format: {archive_path.suffix}")
            return False

        return True

    except (zipfile.BadZipFile, rarfile.Error, OSError) as e:
        print(f"Error extracting {archive_path.name}: {e}")
        return False


def convert_images_to_pdf(image_files: list[Path], output_path: Path) -> bool:
    """Convert list of image files to a single PDF."""
    if not image_files:
        print("No image files found to convert")
        return False

    converted_images = []
    total_files = len(image_files)

    print("Converting images...")
    for index, image_path in enumerate(image_files, 1):
        try:
            print(f"Processing: {index}/{total_files} ({index/total_files*100:.0f}%)", end="\r")

            with Image.open(image_path) as img:
                # Convert RGBA to RGB for PDF compatibility
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                converted_images.append(img.copy())

        except (OSError, IOError) as e:
            print(f"\nError processing {image_path.name}: {e}")
            continue

    if not converted_images:
        print("No images could be processed")
        return False

    try:
        print(f"\nSaving PDF: {output_path.name}")
        first_image = converted_images[0]
        remaining_images = converted_images[1:] if len(converted_images) > 1 else []

        first_image.save(output_path, "PDF", save_all=True, append_images=remaining_images, resolution=100.0)
        print(f"\x1b[1;32m✓ Successfully converted: {output_path.name}\x1b[0m")
        return True

    except (OSError, IOError) as e:
        print(f"Error saving PDF: {e}")
        return False


def convert_comic_to_pdf(file_path: Path) -> bool:
    """Convert a single comic file to PDF."""
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"Unsupported file: {file_path.name}")
        return False

    temp_dir = Path(tempfile.mkdtemp(prefix="comics2pdf_"))

    try:
        if not extract_archive(file_path, temp_dir):
            return False

        image_files = collect_image_files(temp_dir)
        if not image_files:
            print(f"No images found in {file_path.name}")
            return False

        output_path = file_path.with_suffix(".pdf")

        convert_images_to_pdf(image_files, output_path)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def process_directory(directory_path: Path) -> None:
    """Process all comic files in a directory."""
    if not directory_path.is_dir():
        print(f"Directory not found: {directory_path}")
        return

    comic_files = [f for f in directory_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not comic_files:
        print(f"No comic files found in {directory_path}")
        return

    print(f"Found {len(comic_files)} comic file(s) to convert")

    for comic_file in sorted(comic_files):
        convert_comic_to_pdf(comic_file)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  -d <directory>  Convert all comic files in directory\n"
            "  -f <file>       Convert a single comic file"
        )
        return

    mode = sys.argv[1]
    target_path = Path(sys.argv[2])

    if mode == "-d":
        process_directory(target_path)
    elif mode == "-f":
        if not target_path.is_file():
            print(f"File not found: {target_path}")
            return
        convert_comic_to_pdf(target_path)
    else:
        print(f"Invalid mode: {mode}. Use -d for directory or -f for file")


if __name__ == "__main__":
    main()
