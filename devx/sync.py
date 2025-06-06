"""Workshop file synchronization functionality."""

import grp
import os
from pathlib import Path

import yaml
from dotenv import dotenv_values

from devx.models import BrevWorkspace, Project
from devx.workspace_config import WORKSPACE_CONFIG_CONFIGS

DEVX_DIR = Path('.devx')
TARGET_BRANCH = 'main'
TARGET_LAUNCHABLE_FILE = DEVX_DIR / 'compose.yaml'
TARGET_LOCAL_FILE = DEVX_DIR / 'compose.local.yaml'
USER_COMPOSE_PATHS = [Path('compose.yaml'), Path('compose.yml')]
USER_COMPOSE_PATH = next((path for path in USER_COMPOSE_PATHS if path.exists()), USER_COMPOSE_PATHS[0])
LOCAL_JUPYTER_PORT = 8888
LOCAL_ENV_FILE = Path('variables.env')
PYPROJECT_FILE = Path('pyproject.toml')
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


def _create_data_dir_watcher(compose: dict, workspace_group_id: str) -> dict:
    """Add a data watcher service that monitors and fixes permissions on new directories.

    Args:
        compose: The docker compose configuration dictionary.
        workspace_group_id: The workspace group ID to get configuration for.

    Returns:
        The compose configuration with data watcher service added.
    """
    if workspace_group_id not in WORKSPACE_CONFIG_CONFIGS:
        return compose

    workspace_config = WORKSPACE_CONFIG_CONFIGS[workspace_group_id]

    # Skip if no data directory configured
    if workspace_config.data_dir is None:
        return compose

    data_dir = str(workspace_config.data_dir)

    # Add data watcher service
    compose['services']['data-watcher'] = {
        "image": "alpine",
        "command": [
            "sh", "-c",
            f"""echo "Starting directory permission watcher for {data_dir}..." &&
while true; do
  find "{data_dir}" -type d ! -perm 777 -exec chmod 777 {{}} \\; -print 2>/dev/null || true
  sleep 10
done"""
        ],
        "environment": [f"DATA_DIR={data_dir}"],
        "volumes": [f"{data_dir}:{data_dir}"],
        "restart": "always"
    }

    return compose


def compile_local_compose(compose_path: Path, jupyter_port: int) -> str:
    """Get the docker compose file content.

    Args:
        compose_path: Path to the docker compose file.
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
        "restart": "always",
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


def compile_launchable_compose(compose_path: Path, image_url: str, workspace_group_id: str) -> str:
    """Get the docker compose file content.

    Args:
        compose_path: Path to the docker compose file.
        image_url: URL of the docker image.
        workspace_group_id: The workspace group ID to check for init services.

    Returns:
        The docker compose file content.
    """
    compose = _read_compose_file(compose_path)

    # Get environment variables and add data directory if configured
    environment = _parse_env_file(Path('variables.env'))

    # Add data directory to environment if workspace config exists
    if workspace_group_id in WORKSPACE_CONFIG_CONFIGS:
        workspace_config = WORKSPACE_CONFIG_CONFIGS[workspace_group_id]
        if workspace_config.data_dir is not None:
            environment["DATA_DIR"] = str(workspace_config.data_dir)

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
        "environment": environment,
        "networks": ["devx"],
        "restart": "always",
    }

    compose['volumes']['devx_home'] = None
    compose['networks']['devx'] = {"driver": "bridge"}

    compose = _create_data_dir_watcher(compose, workspace_group_id)

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
        needs_update(LOCAL_ENV_FILE, TARGET_LAUNCHABLE_FILE) or
        needs_update(PYPROJECT_FILE, TARGET_LAUNCHABLE_FILE)
    )

    if update_launchable_compse:
        compose = compile_launchable_compose(USER_COMPOSE_PATH, project.image_url, workspace.workspace_group_id)
        with open(TARGET_LAUNCHABLE_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LAUNCHABLE_FILE}")

    update_local_compse = (
        force or
        needs_update(USER_COMPOSE_PATH, TARGET_LOCAL_FILE) or
        needs_update(LOCAL_ENV_FILE, TARGET_LOCAL_FILE) or
        needs_update(PYPROJECT_FILE, TARGET_LOCAL_FILE)
    )

    if update_local_compse:
        compose = compile_local_compose(USER_COMPOSE_PATH, LOCAL_JUPYTER_PORT)
        with open(TARGET_LOCAL_FILE, 'w', encoding='utf-8') as f:
            f.write(compose)
        print(f"✅ Docker compose file written to {TARGET_LOCAL_FILE}")
