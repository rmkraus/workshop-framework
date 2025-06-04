"""Workshop running functionality."""

import argparse
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import List

import yaml

from devx.models import BrevWorkspace, Port

DEVX_DIR = Path('.devx')
COMPOSE_PATHS = ['compose.yaml', 'compose.yml']
COMPOSE_PATH = next((path for path in COMPOSE_PATHS if Path(path).exists()), COMPOSE_PATHS[0])
LOCAL_COMPOSE_PATH = DEVX_DIR / 'compose.local.yaml'

def get_docker_compose(compose_path: str, ports: List[Port], jupyter_port: int) -> str:
    """Get the docker compose file content.

    Args:
        compose_path: Path to the docker compose file.
        image_url: URL of the docker image.
        ports: List of ports to expose.

    Returns:
        The docker compose file content.
    """
    try:
        with open(compose_path, 'r', encoding='utf-8') as f:
            compose = yaml.load(f.read(), Loader=yaml.SafeLoader) or {}
    except FileNotFoundError:
        compose = {}
    compose['services'] = compose.get('services', {})
    compose['services']['devx'] = compose['services'].get('devx', {})


    # Add ports
    port_list = []
    for port in ports:
        host_port = port.port
        if port.name == "jupyter":
            host_port = jupyter_port
        port_list.append(f"{host_port}:{port.port}")

    # Add devx service
    compose['services']['devx']['build'] = {
        "context": "../",
        "dockerfile": "Dockerfile",
        "args": {
            "USER_UID": str(os.getuid()),
            "USER_GID": str(os.getgid()),
        }
    }
    compose['services']['devx']['ports'] = [f"{port.port}:{port.port}" for port in ports]
    compose['services']['devx']['volumes'] = ["../:/project:cached"]

    # Add environment variables
    compose['services']['devx']['environment'] = {
        "NGC_API_KEY": "${NGC_API_KEY}"
    }

    return yaml.dump(compose)


def start(args: argparse.Namespace, workspace: BrevWorkspace) -> None:
    """Start the workshop locally.

    Args:
        args: Command line arguments.
        workspace: Brev workspace configuration.
    """
    print("🚀 Starting workshop...")

    # get docker compose
    compose = get_docker_compose(COMPOSE_PATH, workspace.ports, args.port)

    # write to file
    with open(LOCAL_COMPOSE_PATH, 'w', encoding='utf-8') as f:
        f.write(compose)

    # run docker compose
    cmd = ['docker', 'compose', '-f', LOCAL_COMPOSE_PATH, 'up', '--build', '-d']
    if Path('workshop.env').exists():
        cmd.extend(['--env-file', 'workshop.env'])
    subprocess.run(cmd, check=True)

    # open browser
    if not args.no_browser:
        webbrowser.open(f"http://localhost:{args.port}")


def stop() -> None:
    """Stop the workshop's Docker containers."""
    print("🛑 Stopping workshop...")

    if not LOCAL_COMPOSE_PATH.exists():
        print("⚠️  No running workshop found")
        return

    try:
        subprocess.run(['docker', 'compose', '-f', LOCAL_COMPOSE_PATH, 'down'], check=True)
        LOCAL_COMPOSE_PATH.unlink()
        print("✅ Workshop stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop workshop: {e}")
    except FileNotFoundError:
        print("✅ Workshop stopped")
