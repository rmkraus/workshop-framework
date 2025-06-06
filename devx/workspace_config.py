"""
Module for managing workspace-specific config containers in compose.yaml files.

This module provides config service configurations that need to be injected into
compose.yaml files based on the current workspace group.
"""

from pathlib import Path
from typing import Dict

from devx.models import WorkspaceGroupConfig

# Dictionary to store workspace group configurations
WORKSPACE_CONFIG_CONFIGS: Dict[str, WorkspaceGroupConfig] = {
    "crusoe-brev-wg": WorkspaceGroupConfig(
        name="crusoe-brev-wg",
        data_dir=Path("/ephemeral")
    )
}
