"""CLI application for workshop configuration and settings management."""

import argparse
from pathlib import Path

from .models import BrevWorkspace, Project
from .publish import publish
from .sync import sync

DEVX_DIR = Path('.devx')
COMPOSE_PATH = './docker-compose.yaml'


def main() -> None:
    """Create a Brev launchable workspace."""
    parser = argparse.ArgumentParser(description="Workshop configuration and settings management.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # Publish subcommand
    publish_parser = subparsers.add_parser("publish", help="Publish a workshop to Brev")
    publish_parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")

    # Sync subcommand
    _ = subparsers.add_parser("sync", help="Synchronize the cached workshop files.")

    args = parser.parse_args()
    workspace = BrevWorkspace()
    project = Project()

    match args.command:
        case "publish":
            publish(args, workspace, project)
        case "sync":
            sync(args, workspace, project)


if __name__ == "__main__":
    main()
