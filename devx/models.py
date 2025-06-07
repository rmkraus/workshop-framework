"""Data models for the workshop configuration."""

import json
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class Provider(str, Enum):
    """Enum for supported cloud providers."""
    CRUSOE = "crusoe"
    GCP = "gcp"
    AWS = "aws"
    AZURE = "azure"
    LAMBDA = "lambda"


def _relative_to_root() -> str:
    """Find the .git directory and nearest pyproject.toml, return dirs between them.

    Returns:
        Relative path between .git and pyproject.toml (exclusive).

    Raises:
        RuntimeError: If either .git or pyproject.toml cannot be found.
        ValueError: If pyproject.toml is not under .git directory.
    """
    current = Path.cwd()
    git_dir = None
    pyproject_dir = None

    # Search up the directory tree
    while current.parent != current:
        if (current / '.git').is_dir() and not git_dir:
            git_dir = current
        if (current / 'pyproject.toml').is_file() and not pyproject_dir:
            pyproject_dir = current
        if git_dir and pyproject_dir:
            break
        current = current.parent

    if not git_dir:
        raise RuntimeError("Could not find .git directory")
    if not pyproject_dir:
        raise RuntimeError("Could not find pyproject.toml")

    # Get relative path between the two
    try:
        return str(pyproject_dir.relative_to(git_dir))
    except ValueError as exc:
        raise ValueError("pyproject is not under git dir") from exc


def _infer_repo_url() -> str:
    """Infer the HTTPS URL of the repository from the git remote.

    Returns:
        The HTTPS URL of the repository.

    Raises:
        ValueError: If the remote URL format is not supported.
    """
    remote_url = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], text=True
    ).strip()

    if remote_url.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+)\.git", remote_url)
        if match:
            domain, path = match.groups()
            return f"https://{domain}/{path}"
    elif remote_url.startswith("https://"):
        return remote_url.removesuffix(".git")

    raise ValueError(f"Unsupported remote URL format: {remote_url}")


def _infer_image_url() -> str:
    """Infer the container image URL from the git remote.

    Returns:
        The container image URL.

    Raises:
        ValueError: If the remote URL format is not supported.
    """
    remote_url = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], text=True
    ).strip()

    if remote_url.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+)\.git", remote_url)
        if match:
            _, path = match.groups()
            return f"ghcr.io/{path}"
    elif remote_url.startswith("https://"):
        url = remote_url.removesuffix(".git")
        if "github.com" in url:
            path = url.split("github.com/")[1]
            return f"ghcr.io/{path}"

    raise ValueError(f"Unsupported remote URL format: {remote_url}")


class Port(BaseModel):
    """Represents a port mapping for a container.

    Attributes:
        name: The name of the port.
        port: The port number.
    """
    name: str
    port: str | int

    def model_dump(self) -> dict:  # pylint: disable=arguments-differ
        """Dump the port mapping to a dictionary.

        Returns:
            A dictionary representation of the port mapping.
        """
        return {"name": self.name, "port": str(self.port)}


class WorkspaceGroupConfig(BaseModel):
    """Represents a workspace group configuration.

    Attributes:
        name: The name of the workspace group.
        data_dir: The data directory path for the workspace group.
        provider: The cloud provider for the workspace group.
        flexible_storage: Whether the workspace supports flexible storage.
        nvidia_driver_version: The NVIDIA driver major version number.
        docker_gid: The Docker group ID for this workspace.
    """
    name: str
    data_dir: Optional[Path] = None
    provider: Optional[str] = None
    flexible_storage: bool = True
    nvidia_driver_version: Optional[int] = None
    docker_gid: int = 999


class Project(BaseSettings):
    """Represents a project configuration from pyproject.toml.

    Attributes:
        name: The name of the project.
        description: The description of the project.
        repo_url: The HTTPS URL of the repository.
        image_url: The container image URL.
        project_dir: Path to the current directory.
    """
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=('project',), extra='allow'
    )

    name: str
    description: str
    repo_url: str = Field(default_factory=_infer_repo_url)
    image_url: str = Field(default_factory=_infer_image_url)

    @classmethod
    # pylint: disable-next=arguments-differ,too-many-arguments,too-many-positional-arguments
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


class BrevWorkspace(BaseSettings):
    """Represents a brev workspace configuration.

    Attributes:
        instance_type: The type of instance to use for the workspace.
        workspace_group_id: The ID of the workspace group to use.
        storage: The storage configuration for the workspace.
        ports: The port mappings for the brev workspace.
        relative_to_root: Whether the workspace is relative to the root.
        valid_driver_versions: List of valid NVIDIA driver versions for this workspace.
        cloud: The cloud provider for this workspace.
    """
    model_config = SettingsConfigDict(pyproject_toml_table_header=('tool', 'brev'))

    instance_type: str
    cloud: str
    storage: Optional[int] = None
    ports: list[Port]
    relative_to_root: str = Field(default_factory=_relative_to_root)
    valid_driver_versions: Optional[list[int]] = None

    @field_validator('cloud')
    @classmethod
    def validate_cloud_provider(cls, v: str, info) -> str:
        """Validate that a workspace exists for the specified cloud provider and driver compatibility."""
        # Convert to lowercase for consistency
        v = v.lower()

        # Import here to avoid circular imports
        from devx.workspaces import WORKSPACES

        workspace = WORKSPACES.query_provider(v)
        if workspace is None:
            available_providers = [ws.provider for ws in WORKSPACES._KNOWN_WORKSPACES if ws.provider]
            raise ValueError(f"No workspace found for cloud provider '{v}'. Available providers: {available_providers}")

        # Check driver version compatibility if valid_driver_versions is also specified
        if hasattr(info, 'data') and 'valid_driver_versions' in info.data:
            valid_driver_versions = info.data['valid_driver_versions']
            if valid_driver_versions is not None and workspace.nvidia_driver_version is not None:
                if workspace.nvidia_driver_version not in valid_driver_versions:
                    raise ValueError(
                        f"Cloud provider '{v}' has NVIDIA driver version {workspace.nvidia_driver_version}, "
                        f"but valid versions are: {valid_driver_versions}"
                    )

        return v

    @property
    def workspace_group_id(self) -> str:
        """Get the workspace group ID by looking up the cloud provider."""
        # Import here to avoid circular imports
        from devx.workspaces import WORKSPACES

        workspace = WORKSPACES.query_provider(self.cloud)
        if workspace:
            return workspace.name

        # Raise error if no matching workspace found
        available_providers = [ws.provider for ws in WORKSPACES._KNOWN_WORKSPACES if ws.provider]
        raise ValueError(f"No workspace found for cloud provider '{self.cloud}'. Available providers: {available_providers}")

    @property
    def access_token(self) -> str:
        """Get the Brev access token from credentials file."""
        cred_path = Path.home() / ".brev" / "credentials.json"
        with open(cred_path, encoding='utf-8') as f:
            return json.load(f)["access_token"]

    @property
    def org_id(self) -> str:
        """Get the Brev organization ID from active org file."""
        org_path = Path.home() / ".brev" / "active_org.json"
        with open(org_path, encoding='utf-8') as f:
            return json.load(f)["id"]

    @classmethod
    # pylint: disable-next=arguments-differ,too-many-arguments,too-many-positional-arguments
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)
