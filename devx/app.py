"""CLI application for workshop configuration and settings management."""

import argparse

from init import init
from models import BrevWorkspace, Project
from publish import publish
from sync import sync


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

    # Publish subcommand
    publish_parser = subparsers.add_parser("publish", help="Publish a workshop to Brev")
    publish_parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    publish_parser.add_argument("--dry-run", action="store_true", help="Show API request details without making the request")

    # Sync subcommand
    _ = subparsers.add_parser("sync", help="Synchronize the cached workshop files.")

    args = parser.parse_args()
    workspace = BrevWorkspace()
    project = Project()

    match args.command:
        case "init":
            init(args)
        case "publish":
            publish(args, workspace, project)
        case "sync":
            sync(args, workspace, project)


if __name__ == "__main__":
    main()
