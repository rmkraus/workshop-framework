"""Workshop running functionality."""

import subprocess
import webbrowser
from pathlib import Path
from typing import List

from devx.sync import LOCAL_JUPYTER_PORT, TARGET_LOCAL_FILE


def _run(cmd: List[str]) -> None:
    """Run a command and handle errors."""
    if not TARGET_LOCAL_FILE.exists():
        print("⚠️  No workshop configuration found")
        return

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        pass

def start(no_browser: bool = False) -> None:
    """Start the workshop locally.

    Args:
        args: Command line arguments.
    """
    print("🚀 Starting workshop...")

    # run docker compose
    cmd = ['docker', 'compose', '-f', TARGET_LOCAL_FILE, 'up', '--build', '-d']
    if Path('workshop.env').exists():
        cmd.extend(['--env-file', 'workshop.env'])
    _run(cmd)

    # open browser
    if not no_browser:
        webbrowser.open(f"http://localhost:{LOCAL_JUPYTER_PORT}")


def stop() -> None:
    """Stop the workshop's Docker containers."""
    print("🛑 Stopping workshop...")
    _run(['docker', 'compose', '-f', TARGET_LOCAL_FILE, 'down'])


def build() -> None:
    """Build the workshop's Docker container."""
    print("🔨 Building workshop container...")
    _run(['docker', 'compose', '-f', TARGET_LOCAL_FILE, 'build'])


def restart() -> None:
    """Restart the workshop's Docker containers."""
    print("🔄 Restarting workshop...")
    _run(['docker', 'compose', '-f', TARGET_LOCAL_FILE, 'restart'])


def status() -> None:
    """Check the status of the workshop's Docker containers."""
    print("📊 Checking workshop status...")
    _run(['docker', 'compose', '-f', TARGET_LOCAL_FILE, 'ps'])
