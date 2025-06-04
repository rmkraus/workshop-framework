"""Workshop manager cli."""

import argparse
import os
from pathlib import Path

from devx.create import create
from devx.init import init
from devx.models import BrevWorkspace, Project
from devx.run import build, restart, start, status, stop
from devx.sync import sync


def go_to_project_root() -> Path:
    """Go to the nearest directory containing a pyproject.toml file.

    Returns:
        Path to the project root directory.

    Raises:
        FileNotFoundError: If no pyproject.toml is found in the current directory or any parent.
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            os.chdir(current)
            return current
        current = current.parent
    print("No pyproject.toml found in current directory or any parent directory")
    return None


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Workshop configuration and settings management.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # Code management commands
    init_parser = subparsers.add_parser("init", help="Initialize a workshop repository")
    init_parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
    init_parser.add_argument(
        "-t", "--template",
        default="simple",
        help="Name of the template to use"
    )

    # Locally running workshop commands
    start_parser = subparsers.add_parser("start", help="Start the workshop locally")
    start_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open the browser automatically"
    )
    subparsers.add_parser("stop", help="Stop the workshop")
    subparsers.add_parser("build", help="Build the workshop container")
    subparsers.add_parser("restart", help="Restart the workshop")
    subparsers.add_parser("status", help="Check the status of the workshop containers")

    # Brev configuration commands
    create_parser = subparsers.add_parser("create", help="Create a launchable workshop on Brev")
    create_parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    create_parser.add_argument(
        "--dry-run", action="store_true", help="Show API request details without making the request")

    # Utility commands
    subparsers.add_parser("sync", help="Only synchronize the cached workshop files and quit.")

    return parser.parse_args()


def main() -> None:
    """Create a Brev launchable workspace."""
    args = parse_args()

    # Handle init command
    if args.command == "init":
        init(args)
        return

    # Find project root and change to it
    if not go_to_project_root():
        return

    # Create project instance
    project = Project()

    # Ensure files are synced
    workspace = BrevWorkspace()
    if args.command == "sync":
        sync(workspace, project, force=True)
        return
    sync(workspace, project)

    # Handle other commands
    if args.command == "start":
        start(args.no_browser)
    elif args.command == "stop":
        stop()
    elif args.command == "build":
        build()
    elif args.command == "restart":
        restart()
    elif args.command == "status":
        status()
    elif args.command == "create":
        create(workspace, project, args.yes, args.dry_run)


if __name__ == "__main__":
    main()
