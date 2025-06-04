"""Workshop file synchronization functionality."""

import os
from pathlib import Path
from typing import List

import yaml

from devx.models import BrevWorkspace, Port, Project

DEVX_DIR = Path('.devx')
TARGET_BRANCH = 'main'
TARGET_LAUNCHABLE_FILE = DEVX_DIR / 'compose.yaml'
TARGET_LOCAL_FILE = DEVX_DIR / 'compose.local.yaml'
USER_COMPOSE_PATHS = [Path('compose.yaml'), Path('compose.yml')]
USER_COMPOSE_PATH = next((path for path in USER_COMPOSE_PATHS if path.exists()), USER_COMPOSE_PATHS[0])
LOCAL_JUPYTER_PORT = 8888


def compile_local_compose(compose_path: Path, ports: List[Port], jupyter_port: int) -> str:
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
    compose['services']['devx']['volumes'] = ["../:/project:cached", "/var/run/docker.sock:/var/run/docker.sock"]

    # Add environment variables
    compose['services']['devx']['environment'] = {
        "NGC_API_KEY": "${NGC_API_KEY}"
    }

    return yaml.dump(compose)


def compile_launchable_compose(compose_path: Path, image_url: str, ports: List[Port]) -> str:
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
        "volumes": [f"../{repo_name}:/project:cached", "/var/run/docker.sock:/var/run/docker.sock"],
        "environment": {
            "NGC_API_KEY": "${NGC_API_KEY}"
        }
    }

    # Add env_file if variables.env exists
    if Path('variables.env').exists():
        compose['services']['devx']['env_file'] = ['variables.env']

    return yaml.dump(compose)


def needs_update(source_file: Path, target_file: Path) -> bool:
    """Check if the target file needs to be updated based on source file.

    Args:
        source_file: Path to the source file.
        target_file: Path to the target file.

    Returns:
        True if the target file needs to be updated, False otherwise.
    """
    if not target_file.exists():
        return True

    if not source_file.exists():
        return False

    target_mtime = os.path.getmtime(target_file)
    source_mtime = os.path.getmtime(source_file)
    return target_mtime < source_mtime


def sync(workspace: BrevWorkspace, project: Project) -> None:
    """Synchronize the cached workshop files.

    Args:
        args: Command line arguments.
        workspace: Brev workspace configuration.
        project: Project configuration.
    """
    print("🔄 Synchronizing cached workshop files...")

    if needs_update(USER_COMPOSE_PATH, TARGET_LAUNCHABLE_FILE):
        compose = compile_launchable_compose(USER_COMPOSE_PATH, project.image_url, workspace.ports)
        with open(TARGET_LAUNCHABLE_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LAUNCHABLE_FILE}")

    if needs_update(USER_COMPOSE_PATH, TARGET_LOCAL_FILE):
        compose = compile_local_compose(USER_COMPOSE_PATH, workspace.ports, LOCAL_JUPYTER_PORT)
        with open(TARGET_LOCAL_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LOCAL_FILE}")
