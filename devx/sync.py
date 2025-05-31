"""Workshop file synchronization functionality."""

from pathlib import Path
from typing import List

import yaml

from devx.models import BrevWorkspace, Port, Project

DEVX_DIR = Path('.devx')
COMPOSE_PATH = './docker-compose.yaml'
TARGET_BRANCH = 'main'


def get_docker_compose(compose_path: str, image_url: str, ports: List[Port]) -> str:
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

    # Add devx service
    repo_name = image_url.split('/')[-1]
    compose['services']['devx'] = {
        "image": image_url + f"/devx:{TARGET_BRANCH}",
        "ports": [f"{port.port}:{port.port}" for port in ports],
        "volumes": [f"../{repo_name}:/project:cached"]
    }

    return yaml.dump(compose)


def sync(workspace: BrevWorkspace, project: Project) -> None:
    """Synchronize the cached workshop files.

    Args:
        args: Command line arguments.
        workspace: Brev workspace configuration.
        project: Project configuration.
    """
    print("🔄 Synchronizing cached workshop files...")

    # get docker compose
    compose = get_docker_compose(COMPOSE_PATH, project.image_url, workspace.ports)

    # write to file
    with open(DEVX_DIR / COMPOSE_PATH, 'w', encoding='utf-8') as f:
        f.write(compose)

    print(f"✅ Docker compose file written to {DEVX_DIR / COMPOSE_PATH}")
