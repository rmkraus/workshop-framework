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


def _parse_env_file(env_file_path: Path) -> dict:
    """Parse environment variables from a .env file.

    Args:
        env_file_path: Path to the .env file.

    Returns:
        Dictionary of environment variables with shell substitution format.
    """
    env_vars = {"NGC_API_KEY": "${NGC_API_KEY}"}  # Start with default NGC_API_KEY

    if not env_file_path.exists():
        return env_vars

    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            var_name = line.split('=', 1)[0].strip()
            if var_name:
                env_vars[var_name] = f"${{{var_name}}}"

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

    return compose


def _project_port_list(ports: List[Port], jupyter_port: None | int = None) -> List[str]:
    """Get the list of ports to expose.

    Args:
        ports: List of ports to expose.
        jupyter_port: Port to use for Jupyter.

    Returns:
        List of ports to expose.
    """
    port_list = []
    for port in ports:
        host_port = port.port
        if jupyter_port and port.name == "jupyter":
            host_port = jupyter_port
        port_list.append(f"{host_port}:{port.port}")
    return port_list


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
        "ports": _project_port_list(ports, jupyter_port),
        "volumes": ["../:/project:cached", "/var/run/docker.sock:/var/run/docker.sock"],
        "environment": _parse_env_file(Path('variables.env')),
        "build": {
            "context": "../",
            "dockerfile": "Dockerfile",
            "args": {
                "USER_UID": str(os.getuid()),
                "USER_GID": str(os.getgid()),
            }
        }
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
    compose = _read_compose_file(compose_path)

    # Add devx service
    repo_name = image_url.split('/')[-1]
    compose['services']['devx'] = {
        "image": image_url + f"/devx:{TARGET_BRANCH}",
        "ports": _project_port_list(ports),
        "volumes": [f"../{repo_name}:/project:cached", "/var/run/docker.sock:/var/run/docker.sock"],
        "environment": _parse_env_file(Path('variables.env')),
    }

    return yaml.dump(compose)


def needs_update(source_file: Path, target_file: Path, force: bool = False) -> bool:
    """Check if the target file needs to be updated based on source file.

    Args:
        source_file: Path to the source file.
        target_file: Path to the target file.
        force: Whether to force update regardless of timestamps.

    Returns:
        True if the target file needs to be updated, False otherwise.
    """
    if force:
        return True

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

    if needs_update(USER_COMPOSE_PATH, TARGET_LAUNCHABLE_FILE, force):
        compose = compile_launchable_compose(USER_COMPOSE_PATH, project.image_url, workspace.ports)
        with open(TARGET_LAUNCHABLE_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LAUNCHABLE_FILE}")

    if needs_update(USER_COMPOSE_PATH, TARGET_LOCAL_FILE, force):
        compose = compile_local_compose(USER_COMPOSE_PATH, workspace.ports, LOCAL_JUPYTER_PORT)
        with open(TARGET_LOCAL_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LOCAL_FILE}")
