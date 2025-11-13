#!/usr/bin/env python3
"""
PNG to PDF Converter
Converts PNG images to PDF with configurable padding and background color.
Maintains the frame size consistency with card generators.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image


class PNGtoPDFConverter:
    """Converts PNG images to PDF with configurable options."""

    def __init__(self, config_path: str = "png_to_pdf_config.json"):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.base_dir = Path(__file__).parent

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def _validate_image(self, image_path: str) -> bool:
        """Validate that image exists and is readable."""
        if not os.path.exists(image_path):
            print(f"Error: Image not found: {image_path}")
            return False

        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            print(f"Error: Invalid image file {image_path}: {e}")
            return False

    def _get_image_dimensions(self, image_path: str) -> tuple:
        """Get image dimensions."""
        with Image.open(image_path) as img:
            return img.size

    def convert_png_to_pdf(self, png_path: str, output_path: Optional[str] = None) -> bool:
        """
        Convert a PNG image to PDF.

        Args:
            png_path: Path to the PNG image
            output_path: Optional output path for PDF. If not provided, will use same name with .pdf extension

        Returns:
            True if successful, False otherwise
        """
        png_path = Path(png_path)

        # Validate input
        if not self._validate_image(str(png_path)):
            return False

        # Determine output path
        if output_path is None:
            output_suffix = self.config.get('output_suffix', '_pdf')
            output_name = png_path.stem + output_suffix + '.pdf'
            output_dir = self.base_dir / self.config.get('output_directory', 'output')
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / output_name
        else:
            output_path = Path(output_path)

        cfg = self.config

        print(f"Converting: {png_path.name}")
        print(f"  Output: {output_path}")

        try:
            # Page dimensions
            page_width = cfg['page_width_pt']
            page_height = cfg['page_height_pt']

            # Padding
            top_pad = cfg.get('top_padding_pt', 0)
            bottom_pad = cfg.get('bottom_padding_pt', 0)
            left_pad = cfg.get('left_padding_pt', 0)
            right_pad = cfg.get('right_padding_pt', 0)

            # Available space for image
            available_width = page_width - left_pad - right_pad
            available_height = page_height - top_pad - bottom_pad

            print(f"  Page: {page_width}pt × {page_height}pt")
            print(f"  Padding: T:{top_pad}pt B:{bottom_pad}pt L:{left_pad}pt R:{right_pad}pt")
            print(f"  Available: {available_width}pt × {available_height}pt")

            # Get image dimensions
            img_width_px, img_height_px = self._get_image_dimensions(str(png_path))

            # Calculate scaling to fit image in available space
            # Assuming 72 DPI for conversion (standard PDF points)
            # But if the PNG is high-res (e.g., 4x scale = 288 DPI), we need to account for that
            # For now, let's calculate based on maintaining aspect ratio to fit available space

            if cfg.get('fit_to_page', True):
                # Scale to fit within available space while maintaining aspect ratio
                scale_w = available_width / img_width_px
                scale_h = available_height / img_height_px
                scale = min(scale_w, scale_h)

                img_width_pt = img_width_px * scale
                img_height_pt = img_height_px * scale
            else:
                # Use image at its native size (assuming pixels = points)
                img_width_pt = min(img_width_px, available_width)
                img_height_pt = min(img_height_px, available_height)

            # Calculate position
            if cfg.get('center_image', True):
                # Center the image in available space
                x = left_pad + (available_width - img_width_pt) / 2
                y = bottom_pad + (available_height - img_height_pt) / 2
            else:
                # Align to bottom-left of available space
                x = left_pad
                y = bottom_pad

            print(f"  Image: {img_width_pt:.1f}pt × {img_height_pt:.1f}pt at ({x:.1f}, {y:.1f})")

            # Create PDF
            c = canvas.Canvas(str(output_path), pagesize=(page_width, page_height))

            # Fill background if color is specified
            bg_color = cfg.get('background_color', '')
            if bg_color and bg_color.strip():
                c.setFillColor(HexColor(bg_color))
                c.rect(0, 0, page_width, page_height, fill=1, stroke=0)
                print(f"  Background: {bg_color}")

            # Draw the PNG image
            c.drawImage(
                str(png_path),
                x, y,
                width=img_width_pt,
                height=img_height_pt,
                preserveAspectRatio=True,
                mask='auto'
            )

            # Save PDF
            c.save()
            print(f"  ✓ Successfully created: {output_path}\n")
            return True

        except Exception as e:
            print(f"  ✗ Error creating PDF: {e}\n")
            import traceback
            traceback.print_exc()
            return False

    def convert_directory(self, directory_path: str, pattern: str = "*.png") -> None:
        """
        Convert all PNG files in a directory to PDF.

        Args:
            directory_path: Path to directory containing PNG files
            pattern: Glob pattern for matching files (default: "*.png")
        """
        dir_path = Path(directory_path)

        if not dir_path.exists() or not dir_path.is_dir():
            print(f"Error: Directory not found: {directory_path}")
            return

        png_files = list(dir_path.glob(pattern))

        if not png_files:
            print(f"No PNG files found in {directory_path}")
            return

        print(f"Found {len(png_files)} PNG files to convert\n")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        for png_file in png_files:
            if self.convert_png_to_pdf(str(png_file)):
                success_count += 1
            else:
                fail_count += 1

        # Summary
        print("=" * 60)
        print(f"CONVERSION COMPLETE")
        print(f"  Total: {len(png_files)}")
        print(f"  Success: {success_count}")
        print(f"  Failed: {fail_count}")
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert PNG images to PDF with configurable padding and background',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single PNG file
  python convert_png_to_pdf.py image.png

  # Convert single PNG with output path
  python convert_png_to_pdf.py image.png -o output.pdf

  # Convert all PNGs in a directory
  python convert_png_to_pdf.py -d output/

  # Use custom config
  python convert_png_to_pdf.py image.png -c my_config.json
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input PNG file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (optional)'
    )
    parser.add_argument(
        '-d', '--directory',
        help='Convert all PNG files in directory'
    )
    parser.add_argument(
        '-c', '--config',
        default='png_to_pdf_config.json',
        help='Configuration file (default: png_to_pdf_config.json)'
    )
    parser.add_argument(
        '-p', '--pattern',
        default='*.png',
        help='File pattern for directory mode (default: *.png)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.input and not args.directory:
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print("PNG TO PDF CONVERTER")
    print("=" * 60)
    print(f"Configuration: {args.config}\n")

    # Create converter
    converter = PNGtoPDFConverter(args.config)

    # Convert
    if args.directory:
        converter.convert_directory(args.directory, args.pattern)
    elif args.input:
        converter.convert_png_to_pdf(args.input, args.output)


if __name__ == "__main__":
    main()
