"""Workshop repository initialization functionality."""

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# Directories to copy from template
TEMPLATE_DIRS = [
    ".devx",
    ".github",
]

# Files to copy from template
TEMPLATE_FILES = [
    ".gitignore",
    "README.md",
    "Dockerfile",
    "pyproject.toml",
    "compose.yaml",
    "variables.env",
]

TEMPLATE_REPO = ("https://github.com/rmkraus/workshop-framework/archive/refs/heads/main.zip", "templates")


def download_template(url: str, dest: Path) -> None:
    """Download the template zip file.

    Args:
        url: URL of the template zip file.
        dest: Path to save the zip file to.
    """
    print(f"📥 Downloading template from {url}...")
    urllib.request.urlretrieve(url, dest)


def extract_template(zip_path: Path, dest: Path) -> None:
    """Extract the template zip file.

    Args:
        zip_path: Path to the zip file.
        dest: Path to extract to.
    """
    print("📦 Extracting template...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest)


def find_template_dir(extracted_dir: Path, template_name: str) -> Path:
    """Find the template directory in the extracted files.

    Args:
        extracted_dir: Path to the extracted directory.
        template_name: Name of the template to find.

    Returns:
        Path to the template directory.

    Raises:
        SystemExit: If template directory is not found.
    """
    template_dir = next(extracted_dir.glob("*/")) / TEMPLATE_REPO[1] / template_name
    if not template_dir.exists():
        print(f"❌ Template not found: {template_name}")
        sys.exit(1)
    return template_dir


def copy_directory(src: Path, dest: Path, force: bool) -> None:
    """Copy a directory from source to destination.

    Args:
        src: Source directory path.
        dest: Destination directory path.
        force: Whether to force overwrite if destination exists.

    Raises:
        SystemExit: If source directory doesn't exist or destination exists without force.
    """
    if not src.exists():
        print(f"❌ Directory not found: {src}")
        sys.exit(1)

    if dest.exists() and not force:
        print(f"⚠️  {dest} already exists. Use --force to overwrite.")
        sys.exit(1)

    print(f"📝 Copying {dest}...")
    shutil.copytree(src, dest, dirs_exist_ok=force)


def copy_file(src: Path, dest: Path, force: bool) -> None:
    """Copy a file from source to destination.

    Args:
        src: Source file path.
        dest: Destination file path.
        force: Whether to force overwrite if destination exists.
    """
    if src.exists():
        if dest.exists() and not force:
            print(f"⚠️  {dest} already exists. Use --force to overwrite.")
        else:
            print(f"📝 Copying {dest}...")
            shutil.copy2(src, dest)


def init(args) -> None:
    """Initialize a workshop repository.

    Args:
        args: Command line arguments.
    """
    print("🚀 Initializing workshop repository...")

    # Create temporary directory for downloading and extracting
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "template.zip"

        # Download and extract template
        download_template(TEMPLATE_REPO[0], zip_path)
        extract_template(zip_path, temp_path)

        # Find and validate template directory
        template_dir = find_template_dir(temp_path, args.template)

        # Copy directories from template
        for dir_name in TEMPLATE_DIRS:
            copy_directory(template_dir / dir_name, Path(dir_name), args.force)

        # Copy additional files from template
        for file_name in TEMPLATE_FILES:
            copy_file(template_dir / file_name, Path(file_name), args.force)

    print("\n✅ Workshop repository initialized!")
