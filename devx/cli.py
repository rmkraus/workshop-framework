"""Workshop manager cli."""

import argparse
import os

from devx.create import create
from devx.init import init
from devx.models import BrevWorkspace, Project
from devx.run import build, restart, start, status, stop
from devx.sync import sync


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
    _ = subparsers.add_parser("sync", help="Only synchronize the cached workshop files and quit.")

    return parser.parse_args()


def main() -> None:
    """Create a Brev launchable workspace."""
    args = parse_args()

    # Handle init command
    if args.command == "init":
        init(args)
        return

    # Create project instance and change to project directory
    project = Project()
    os.chdir(project.project_dir)

    # Ensure files are synced
    workspace = BrevWorkspace()
    sync(workspace, project)
    if args.command == "sync":
        return

    # Handle other commands
    if args.command == "start":
        start(args)
    elif args.command == "stop":
        stop()
    elif args.command == "build":
        build()
    elif args.command == "restart":
        restart()
    elif args.command == "status":
        status()
    elif args.command == "create":
        create(args, workspace, project)


if __name__ == "__main__":
    main()
