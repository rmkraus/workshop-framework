"""Workshop configuration and settings management."""

import argparse

from devx.init import init
from devx.models import BrevWorkspace, Project
from devx.publish import publish
from devx.run import start, stop
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

    # Publish subcommand
    publish_parser = subparsers.add_parser("publish", help="Publish a workshop to Brev")
    publish_parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    publish_parser.add_argument(
        "--dry-run", action="store_true", help="Show API request details without making the request")

    # Sync subcommand
    _ = subparsers.add_parser("sync", help="Synchronize the cached workshop files.")

    args = parser.parse_args()

    if args.command == "init":
        init(args)
    elif args.command == "start":
        start(args, BrevWorkspace())
    elif args.command == "stop":
        stop()
    elif args.command == "publish":
        publish(args, BrevWorkspace(), Project())
    elif args.command == "sync":
        sync(BrevWorkspace(), Project())


if __name__ == "__main__":
    main()
