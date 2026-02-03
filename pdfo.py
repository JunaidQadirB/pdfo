#!/usr/bin/env python3
"""Fast PDF compression CLI tool."""

import click
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from PIL import Image
import io
import sys
import subprocess
import tempfile


def compress_with_ghostscript(input_path: Path, output_path: Path, quality: int = 2) -> tuple[int, int]:
    """Compress PDF using Ghostscript (much better compression)."""
    # Quality presets
    quality_settings = {
        1: "printer",      # High quality (300 DPI)
        2: "ebook",        # Medium quality (150 DPI)
        3: "screen",       # Lower quality (72 DPI)
        4: "screen",       # Lowest quality (72 DPI)
    }
    
    preset = quality_settings.get(quality, "ebook")
    
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{preset}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dColorImageResolution=150" if quality >= 3 else "-dColorImageResolution=200",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Ghostscript failed: {result.stderr}")
    
    input_size = input_path.stat().st_size
    output_size = output_path.stat().st_size
    
    return input_size, output_size


def compress_with_pypdf(input_path: Path, output_path: Path, quality: int = 2) -> tuple[int, int]:
    """Compress PDF using pypdf (fallback method)."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    for page in writer.pages:
        page.compress_content_streams()
    
    writer.add_metadata({})
    writer.compress_identical_objects(remove_identicals=True)
    
    with open(output_path, "wb") as f:
        writer.write(f)
    
    input_size = input_path.stat().st_size
    output_size = output_path.stat().st_size
    
    return input_size, output_size


def has_ghostscript() -> bool:
    """Check if Ghostscript is available."""
    try:
        subprocess.run(["gs", "--version"], capture_output=True, check=True)
        return True
    except:
        return False


@click.command(no_args_is_help=True)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output file (default: input_compressed.pdf)")
@click.option("-q", "--quality", type=int, default=2, help="Quality: 1=high(300dpi) 2=medium(150dpi) 3/4=low(72dpi)")
@click.option("-f", "--force", is_flag=True, help="Overwrite output file if exists")
@click.option("--no-gs", is_flag=True, help="Don't use Ghostscript (use pypdf instead)")
def main(input_file: Path, output: Path, quality: int, force: bool, no_gs: bool):
    """Compress PDF files to reduce file size dramatically.
    
    \b
    Examples:
      pdfo document.pdf                    # Auto compress (creates document_compressed.pdf)
      pdfo doc.pdf -o small.pdf            # Specify output file
      pdfo large.pdf -q 3                  # Max compression (72 DPI)
      pdfo doc.pdf -q 1                    # High quality (300 DPI)
      pdfo scan.pdf -f                     # Overwrite existing output
    
    \b
    Quality levels (using Ghostscript):
      1 = High quality   (300 DPI) - Best for printing
      2 = Medium quality (150 DPI) - Default, good balance
      3 = Low quality    (72 DPI)  - Smallest size, screen only
      4 = Lowest quality (72 DPI)  - Maximum compression
    
    Tip: Most scanned documents work great with -q 2 or -q 3
    """
    if not input_file.suffix.lower() == ".pdf":
        click.echo("Error: Input must be a PDF file", err=True)
        sys.exit(1)
    
    if output is None:
        output = input_file.parent / f"{input_file.stem}_compressed{input_file.suffix}"
    
    if output.exists() and not force:
        click.echo(f"Error: Output file '{output}' already exists. Use -f to overwrite.", err=True)
        sys.exit(1)
    
    use_gs = has_ghostscript() and not no_gs
    
    click.echo(f"🔄 Compressing: {input_file.name}")
    if use_gs:
        click.echo(f"   Method: Ghostscript (quality={quality})")
    else:
        click.echo(f"   Method: pypdf")
    
    input_size = input_file.stat().st_size
    click.echo(f"   Before: {input_size:,} bytes ({input_size / 1024 / 1024:.2f} MB)")
    
    try:
        if use_gs:
            input_size_check, output_size = compress_with_ghostscript(input_file, output, quality)
        else:
            input_size_check, output_size = compress_with_pypdf(input_file, output, quality)
        
        reduction = ((input_size - output_size) / input_size) * 100
        
        click.echo(f"✅ Success!")
        click.echo(f"   After:  {output_size:,} bytes ({output_size / 1024 / 1024:.2f} MB)")
        click.echo(f"   Saved:  {reduction:.1f}% reduction")
        click.echo(f"   File:   {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
