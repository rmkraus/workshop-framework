"""Workshop file synchronization functionality."""

import grp
import os
from pathlib import Path
from typing import List

import yaml
from dotenv import dotenv_values

from devx.models import BrevWorkspace, Port, Project

DEVX_DIR = Path('.devx')
TARGET_BRANCH = 'main'
TARGET_LAUNCHABLE_FILE = DEVX_DIR / 'compose.yaml'
TARGET_LOCAL_FILE = DEVX_DIR / 'compose.local.yaml'
USER_COMPOSE_PATHS = [Path('compose.yaml'), Path('compose.yml')]
USER_COMPOSE_PATH = next((path for path in USER_COMPOSE_PATHS if path.exists()), USER_COMPOSE_PATHS[0])
LOCAL_JUPYTER_PORT = 8888
LOCAL_ENV_FILE = Path('variables.env')
ENV_INJECTION_VARS = {"NGC_API_KEY": "${NGC_API_KEY}", "COMPOSE_PROJECT_NAME": "${COMPOSE_PROJECT_NAME:-devx}"}


def _get_docker_gid() -> int:
    """Get the group ID of the docker group.

    Returns:
        The group ID of the docker group.

    Raises:
        KeyError: If the docker group doesn't exist.
    """
    try:
        docker_group = grp.getgrnam('docker')
        return docker_group.gr_gid
    except KeyError:
        return 999


def _parse_env_file(env_file_path: Path) -> dict:
    """Parse environment variables from a .env file.

    Args:
        env_file_path: Path to the .env file.

    Returns:
        Dictionary of environment variables with their values from the file.
    """
    env_vars = ENV_INJECTION_VARS.copy()

    if not env_file_path.exists():
        return env_vars

    env_vars.update(dotenv_values(env_file_path))

    return env_vars


def _read_compose_file(compose_path: Path) -> dict:
    """Read and parse a docker compose file.

    Args:
        compose_path: Path to the docker compose file.

    Returns:
        Dictionary containing the compose file contents.
    """
    try:
        with open(compose_path, 'r', encoding='utf-8') as f:
            compose = yaml.load(f.read(), Loader=yaml.SafeLoader) or {}
    except FileNotFoundError:
        compose = {}

    compose['services'] = compose.get('services', {})
    compose['services']['devx'] = compose['services'].get('devx', {})
    compose['volumes'] = compose.get('volumes', {})
    compose['networks'] = compose.get('networks', {})

    return compose


def compile_local_compose(compose_path: Path, ports: List[Port], jupyter_port: int) -> str:
    """Get the docker compose file content.

    Args:
        compose_path: Path to the docker compose file.
        ports: List of ports to expose.
        jupyter_port: Port to use for Jupyter.

    Returns:
        The docker compose file content.
    """
    compose = _read_compose_file(compose_path)

    # Add devx service
    compose['services']['devx'] = {
        "ports": [f"{jupyter_port}:8888"],
        "ipc": "host",
        "volumes": [
            "../:/project:cached",
            "/var/run/docker.sock:/var/run/docker.sock",
            "devx_home:/home/nvidia"
        ],
        "environment": _parse_env_file(Path('variables.env')),
        "networks": ["devx"],
        "build": {
            "context": "../",
            "dockerfile": "Dockerfile",
            "args": {
                "USER_UID": str(os.getuid()),
                "USER_GID": str(os.getgid()),
                "DOCKER_GID": str(_get_docker_gid()),
            }
        }
    }

    compose['volumes']['devx_home'] = None
    compose['networks']['devx'] = {"driver": "bridge"}

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
    compose = _read_compose_file(compose_path)

    # Add devx service
    repo_name = image_url.split('/')[-1]
    compose['services']['devx'] = {
        "image": image_url + f"/devx:{TARGET_BRANCH}",
        "ports": ["8888:8888"],
        "ipc": "host",
        "volumes": [
            f"../{repo_name}:/project:cached",
            "/var/run/docker.sock:/var/run/docker.sock",
            "devx_home:/home/nvidia"
        ],
        "environment": _parse_env_file(Path('variables.env')),
        "networks": ["devx"],
    }

    compose['volumes']['devx_home'] = None
    compose['networks']['devx'] = {"driver": "bridge"}

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


def sync(workspace: BrevWorkspace, project: Project, force: bool = False) -> None:
    """Synchronize the cached workshop files.

    Args:
        workspace: Brev workspace configuration.
        project: Project configuration.
        force: Whether to force update regardless of timestamps.
    """
    print("🔄 Synchronizing cached workshop files...")

    update_launchable_compse = (
        force or
        needs_update(USER_COMPOSE_PATH, TARGET_LAUNCHABLE_FILE) or
        needs_update(LOCAL_ENV_FILE, TARGET_LAUNCHABLE_FILE)
    )

    if update_launchable_compse:
        compose = compile_launchable_compose(USER_COMPOSE_PATH, project.image_url, workspace.ports)
        with open(TARGET_LAUNCHABLE_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LAUNCHABLE_FILE}")

    update_local_compse = (
        force or
        needs_update(USER_COMPOSE_PATH, TARGET_LOCAL_FILE) or
        needs_update(LOCAL_ENV_FILE, TARGET_LOCAL_FILE)
    )

    if update_local_compse:
        compose = compile_local_compose(USER_COMPOSE_PATH, workspace.ports, LOCAL_JUPYTER_PORT)
        with open(TARGET_LOCAL_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LOCAL_FILE}")
