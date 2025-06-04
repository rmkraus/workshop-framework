"""Workshop manager cli."""

import argparse
import os

from devx.create import create
from devx.init import init
from devx.models import BrevWorkspace, Project
from devx.run import build, restart, start, stop
from devx.sync import sync


def main() -> None:
    """Create a Brev launchable workspace."""
    parser = argparse.ArgumentParser(description="Workshop configuration and settings management.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # Init subcommand
    init_parser = subparsers.add_parser("init", help="Initialize a workshop repository")
    init_parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
    init_parser.add_argument(
        "-t", "--template",
        default="simple",
        help="Name of the template to use"
    )

    # Start subcommand
    start_parser = subparsers.add_parser("start", help="Start the workshop locally")
    start_parser.add_argument(
        "-p", "--port",
        type=int,
        default=8888,
        help="Port to run the workshop on (default: 8888)"
    )
    start_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open the browser automatically"
    )

    # Stop subcommand
    subparsers.add_parser("stop", help="Stop the workshop")

    # Build subcommand
    subparsers.add_parser("build", help="Build the workshop container")

    # Restart subcommand
    subparsers.add_parser("restart", help="Restart the workshop")

    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a launchable workshop on Brev")
    create_parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    create_parser.add_argument(
        "--dry-run", action="store_true", help="Show API request details without making the request")

    # Sync subcommand
    _ = subparsers.add_parser("sync", help="Synchronize the cached workshop files.")

    args = parser.parse_args()

    # Handle init command
    if args.command == "init":
        init(args)
        return

    # Create project instance and change to project directory
    project = Project()
    os.chdir(project.project_dir)

    # Handle other commands
    if args.command == "start":
        start(args, BrevWorkspace())
    elif args.command == "stop":
        stop()
    elif args.command == "build":
        build()
    elif args.command == "restart":
        restart()
    elif args.command == "create":
        create(args, BrevWorkspace(), project)
    elif args.command == "sync":
        sync(BrevWorkspace(), project)


if __name__ == "__main__":
    main()
