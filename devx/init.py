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
    "requirements.txt",
    "docker-compose.yaml",
]

TEMPLATE_REPO = ("https://github.com/rmkraus/workshop-framework/archive/refs/heads/main.zip", "templates")


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

        # Download the zip file
        print(f"📥 Downloading template from {TEMPLATE_REPO[0]}...")
        urllib.request.urlretrieve(TEMPLATE_REPO[0], zip_path)

        # Extract the zip file
        print("📦 Extracting template...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)

        # Find the extracted directory (it will be named workshop-framework-main)
        extracted_dir = next(temp_path.glob("*"))
        template_dir = extracted_dir / TEMPLATE_REPO[1] / args.template

        if not template_dir.exists():
            print(f"❌ Template not found: {args.template}")
            sys.exit(1)

        # Copy directories from template
        for dir_name in TEMPLATE_DIRS:
            template_dir_path = template_dir / dir_name
            if not template_dir_path.exists():
                print(f"❌ Template does not contain a {dir_name} directory: {template_dir}")
                sys.exit(1)

            if Path(dir_name).exists() and not args.force:
                print(f"⚠️  {dir_name} already exists. Use --force to overwrite.")
                sys.exit(1)

            print(f"📝 Copying {template_dir_path} to {dir_name}...")
            shutil.copytree(template_dir_path, dir_name, dirs_exist_ok=args.force)

        # Copy additional files from template
        for file_name in TEMPLATE_FILES:
            src_file = template_dir / file_name
            if src_file.exists():
                if Path(file_name).exists() and not args.force:
                    print(f"⚠️  {file_name} already exists. Use --force to overwrite.")
                else:
                    print(f"📝 Copying {file_name}...")
                    shutil.copy2(src_file, file_name)

    print("\n✅ Workshop repository initialized!")
