"""Workshop manager cli."""

import os
from pathlib import Path

import click

from devx.create import create
from devx.init import init
from devx.models import BrevWorkspace, Project
from devx.run import build, restart, start, status, stop
from devx.sync import sync


def find_project_root() -> Path:
    """Find and change to the project root directory.

    Returns:
        Path to the project root directory.

    Raises:
        click.ClickException: If no pyproject.toml is found.
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            os.chdir(current)
            return current
        current = current.parent

    raise click.ClickException("No pyproject.toml found in current directory or any parent directory")


def load_project_context() -> tuple[Project, BrevWorkspace]:
    """Load project and workspace configuration.

    Returns:
        Tuple of (project, workspace)

    Raises:
        click.ClickException: If loading fails.
    """
    try:
        project = Project()
        workspace = BrevWorkspace()
        return project, workspace
    except Exception as e:
        raise click.ClickException(f"Failed to load configuration: {e}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
def cli():
    """Workshop configuration and settings management."""
    pass


# Project Management Commands
@cli.group(context_settings={"help_option_names": ["-h", "--help"]})
def project():
    """Project and repository management commands."""
    pass


@project.command("init")
@click.option("-f", "--force", is_flag=True, help="Overwrite existing files")
@click.option("-t", "--template", default="simple", help="Name of the template to use")
def init_cmd(force: bool, template: str):
    """Initialize a workshop repository."""
    # Create a mock args object for backward compatibility
    class Args:
        def __init__(self, force, template):
            self.force = force
            self.template = template

    init(Args(force, template))


@project.command("sync")
def sync_cmd():
    """Force sync of runtime config."""
    find_project_root()
    project, workspace = load_project_context()
    sync(workspace, project, force=True)


# Workshop Commands
@cli.group(context_settings={"help_option_names": ["-h", "--help"]})
def workshop():
    """Workshop management and testing commands."""
    pass


@workshop.command("start")
@click.option("--no-browser", is_flag=True, help="Don't open the browser automatically")
def start_cmd(no_browser: bool):
    """Start the workshop locally."""
    find_project_root()
    project, workspace = load_project_context()
    sync(workspace, project)
    start(no_browser)


@workshop.command("stop")
def stop_cmd():
    """Stop the workshop."""
    find_project_root()
    stop()


@workshop.command("build")
def build_cmd():
    """Build the workshop container."""
    find_project_root()
    project, workspace = load_project_context()
    sync(workspace, project)
    build()


@workshop.command("restart")
def restart_cmd():
    """Restart the workshop."""
    find_project_root()
    restart()


@workshop.command("status")
def status_cmd():
    """Check the status of the workshop containers."""
    find_project_root()
    status()


# Deployment Commands
@cli.group(context_settings={"help_option_names": ["-h", "--help"]})
def deploy():
    """Deployment and publishing commands."""
    pass


@deploy.command("brev")
@click.option("-y", "--yes", is_flag=True, help="Automatically answer yes to prompts")
@click.option("--dry-run", is_flag=True, help="Show API request details without making the request")
def brev_cmd(yes: bool, dry_run: bool):
    """Create a launchable workshop on Brev."""
    find_project_root()
    project, workspace = load_project_context()
    sync(workspace, project, force=True)
    create(workspace, project, yes, dry_run)





def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
