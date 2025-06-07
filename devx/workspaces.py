"""
Module for managing workspace-specific config containers in compose.yaml files.

This module provides config service configurations that need to be injected into
compose.yaml files based on the current workspace group.
"""

from pathlib import Path
from typing import Dict, List

from devx.models import WorkspaceGroupConfig

# List to store workspace group configurations
_KNOWN_WORKSPACES: List[WorkspaceGroupConfig] = [
    WorkspaceGroupConfig(
        name="crusoe-brev-wg",
        data_dir=Path("/ephemeral"),
        provider="crusoe",
        flexible_storage=False,
        nvidia_driver_version=570
    ),
    WorkspaceGroupConfig(
        name="GCP",
        provider="gcp",
        nvidia_driver_version=550
    ),
    WorkspaceGroupConfig(
        name="devplane-brev-1",
        provider="aws",
        nvidia_driver_version=570,
        docker_gid=998
    )
]


class WorkspaceCollection():
    """
    A collection of workspace group configurations.

    This class provides a dictionary-like interface for accessing workspace group configurations.
    It supports both string-based indexing (by name) and integer-based indexing (by position).

    """

    def query_name(self, name: str) -> WorkspaceGroupConfig | None:
        """Query a workspace group by name."""
        return next((group for group in _KNOWN_WORKSPACES if group.name == name), None)

    def query_provider(self, provider: str) -> WorkspaceGroupConfig | None:
        """Query a workspace group by provider."""
        return next((group for group in _KNOWN_WORKSPACES if group.provider == provider), None)

    def __len__(self) -> int:
        """Get the number of workspace groups."""
        return len(_KNOWN_WORKSPACES)

WORKSPACES = WorkspaceCollection()
