# PDFO - PDF Optimizer 🗜️

Lightning-fast CLI tool to compress and optimize PDF files, reducing file size by up to 99%!

## Features

- ⚡ **Blazing fast** compression using Ghostscript
- 🎯 **Massive savings** - reduce 9MB PDFs to 60KB
- 🔧 **Quality control** - 4 quality levels (300/150/72 DPI)
- 📦 **Fallback mode** - works without Ghostscript (pypdf)
- 🚀 **Easy to use** - simple CLI interface

## Installation

```bash
# With uv (recommended)
uv tool install -e .

# Or install in venv
uv pip install -e .
source .venv/bin/activate
```

## Usage

```bash
# Quick compress (creates input_compressed.pdf)
pdfo document.pdf

# Specify output file
pdfo document.pdf -o small.pdf

# Max compression (smallest file)
pdfo large.pdf -q 3

# High quality (best for printing)
pdfo document.pdf -q 1

# Overwrite existing output
pdfo document.pdf -f
```

## Quality Levels

- **`-q 1`** High quality (300 DPI) - Best for printing
- **`-q 2`** Medium quality (150 DPI) - Default, great balance
- **`-q 3`** Low quality (72 DPI) - Smallest size, screen viewing
- **`-q 4`** Lowest quality (72 DPI) - Maximum compression

## Example Results

```
Input:  9,370,382 bytes (8.94 MB)
Output: 67,215 bytes (0.06 MB)
Saved:  99.3% reduction ✨
```

## Requirements

- Python 3.12+
- **Ghostscript** (optional but highly recommended for best compression)
  ```bash
  # macOS
  brew install ghostscript
  
  # Ubuntu/Debian
  sudo apt install ghostscript
  
  # Windows (via chocolatey)
  choco install ghostscript
  ```

## How It Works

Uses Ghostscript to:
1. Downsample images to target DPI
2. Compress image data with JPEG
3. Remove duplicate embedded objects
4. Optimize fonts and metadata
5. Rewrite PDF structure efficiently

Falls back to pypdf if Ghostscript is not available.

## Releases

Use the GitHub Actions "Release" workflow and choose `patch`, `minor`, or `major`. It bumps `pyproject.toml`, tags `vX.Y.Z`, creates a GitHub Release, and updates the Homebrew tap formula.
