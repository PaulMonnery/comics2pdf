#!/usr/bin/env python3

import sys
import shutil
import tempfile
import asyncio
import argparse
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import zipfile

import rarfile
from PIL.ImageFile import ImageFile
from PIL.Image import Image, open as ImageOpen


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


class ComicConverter:
    """Comic archive to PDF converter with configurable options."""

    def __init__(
        self,
        verbose: bool = True,
        output_dir: Path | None = None,
        temp_prefix: str = "comics2pdf_",
        use_async: bool = True,
        progress_callback=None,
    ):
        """
        Initialize the converter.

        Args:
            verbose: Enable detailed logging
            output_dir: Directory for output PDFs (default: same as input)
            temp_prefix: Prefix for temporary directories
            use_async: Use async processing for directories
            progress_callback: Function to call with progress updates (total_files, completed_files, current_file)
        """
        self.verbose = verbose
        self.output_dir = output_dir
        self.temp_prefix = temp_prefix
        self.use_async = use_async
        self.progress_callback = progress_callback
        self.total_files = 0
        self.completed_files = 0

    def collect_image_files(self, directory: Path) -> list[Path]:
        """Recursively collect all image files from directory."""
        image_files = []

        for item in directory.rglob("*"):
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(item)

        return sorted(image_files)

    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract archive to specified directory. Returns True on success."""
        try:
            extract_to.mkdir(parents=True, exist_ok=True)

            ext = archive_path.suffix.lower()
            if ext in {SupportedExtensions.CBZ.value, SupportedExtensions.ZIP.value}:
                if self.verbose:
                    print(f"Extracting pictures from CBZ/ZIP file: {archive_path.name}")
                with zipfile.ZipFile(archive_path, "r") as zip_file:
                    zip_file.extractall(extract_to)

            elif ext in {SupportedExtensions.CBR.value, SupportedExtensions.RAR.value}:
                if self.verbose:
                    print(f"Extracting pictures from CBR/RAR file: {archive_path.name}")
                with rarfile.RarFile(archive_path) as rar_file:
                    rar_file.extractall(extract_to)
            else:
                print(f"Unsupported file format: {archive_path.suffix}")
                return False

            return True

        except (zipfile.BadZipFile, rarfile.BadRarFile, OSError) as e:
            print(f"Error extracting {archive_path.name}: {e}")
            return False

    def convert_images_to_pdf(self, image_files: list[Path], output_path: Path) -> bool:
        """Convert list of image files to a single PDF."""

        if not image_files:
            if self.verbose:
                print("No image files found to convert")
            return False

        converted_images: list[ImageFile | Image] = []
        total_files = len(image_files)

        if self.verbose:
            print("Converting images...")

        for index, image_path in enumerate(image_files, 1):
            try:
                if self.verbose:
                    print(
                        f"Processing: {index}/{total_files} ({index/total_files*100:.0f}%)",
                        end="\r",
                    )

                with ImageOpen(image_path) as img:
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
            if self.verbose:
                print(f"\nSaving PDF: {output_path.name}")
            first_image = converted_images[0]
            remaining_images = converted_images[1:] if len(converted_images) > 1 else []

            first_image.save(
                output_path,
                "PDF",
                save_all=True,
                append_images=remaining_images,
                resolution=100,
            )
            print(f"\x1b[1;32m✓ Successfully converted: {output_path.name}\x1b[0m")
            return True

        except (OSError, IOError) as e:
            print(f"Error saving PDF: {e}")
            return False

    def convert_comic_to_pdf(self, file_path: Path) -> bool:
        """Convert a single comic file to PDF."""
        if self.progress_callback:
            self.progress_callback(self.total_files, self.completed_files, file_path.name)

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"Unsupported file: {file_path.name}")
            return False

        temp_dir = Path(tempfile.mkdtemp(prefix=self.temp_prefix))

        try:
            if not self.extract_archive(file_path, temp_dir):
                return False

            image_files = self.collect_image_files(temp_dir)
            if not image_files:
                print(f"No images found in {file_path.name}")
                return False

            output_path = self._get_output_path(file_path)
            success = self.convert_images_to_pdf(image_files, output_path)

            if success:
                self.completed_files += 1
                if self.progress_callback:
                    self.progress_callback(self.total_files, self.completed_files, f"✓ {file_path.name}")

            return success

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _get_output_path(self, input_path: Path) -> Path:
        """Generate output path for PDF file."""
        if self.output_dir:
            return self.output_dir / f"{input_path.stem}.pdf"
        return input_path.with_suffix(".pdf")

    def process_single_file(self, file_path: Path) -> bool:
        """Process a single comic file."""
        if not file_path.is_file():
            print(f"File not found: {file_path}")
            return False

        self.total_files = 1
        self.completed_files = 0
        return self.convert_comic_to_pdf(file_path)

    def process_directory_sync(self, directory_path: Path) -> None:
        """Process all comic files in a directory synchronously."""
        if not directory_path.is_dir():
            print(f"Directory not found: {directory_path}")
            return

        comic_files = [f for f in directory_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

        if not comic_files:
            print(f"No comic files found in {directory_path}")
            return

        self.total_files = len(comic_files)
        self.completed_files = 0

        print(f"Found {len(comic_files)} comic file(s) to convert")

        for comic_file in sorted(comic_files):
            self.convert_comic_to_pdf(comic_file)

    async def process_directory_async(self, directory_path: Path) -> None:
        """Process all comic files in a directory concurrently using thread pool."""
        if not directory_path.is_dir():
            print(f"Directory not found: {directory_path}")
            return

        comic_files = [f for f in directory_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

        if not comic_files:
            print(f"No comic files found in {directory_path}")
            return

        self.total_files = len(comic_files)
        self.completed_files = 0

        print(f"Found {len(comic_files)} comic file(s) to convert (async mode)")

        # Use current instance with reduced verbosity for async
        original_verbose = self.verbose
        self.verbose = False

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            tasks = [
                loop.run_in_executor(executor, self.convert_comic_to_pdf, comic_file)
                for comic_file in sorted(comic_files)
            ]
            await asyncio.gather(*tasks)

        # Restore original verbosity
        self.verbose = original_verbose

    def process_directory(self, directory_path: Path) -> None:
        """Process directory with async/sync based on instance configuration."""
        if self.use_async:
            asyncio.run(self.process_directory_async(directory_path))
        else:
            self.process_directory_sync(directory_path)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Convert comic archives (CBZ/CBR) to PDF files")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-d", type=Path, metavar="DIR", help="Convert all comic files in directory")
    mode_group.add_argument("-f", type=Path, metavar="FILE", help="Convert a single comic file")

    parser.add_argument(
        "--sync", action="store_true", help="Force synchronous processing (default is async for directories)"
    )
    parser.add_argument("--output-dir", type=Path, help="Output directory for PDF files")
    parser.add_argument("--quality", type=float, default=100.0, help="Individual image quality")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    converter = ComicConverter(
        verbose=not args.quiet,
        output_dir=args.output_dir,
        use_async=not args.sync,
    )

    if args.d:
        converter.process_directory(args.d)
    elif args.f:
        converter.process_single_file(args.f)


if __name__ == "__main__":
    main()
