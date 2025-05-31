"""Brev workspace management functionality."""

import subprocess
from typing import Optional

import requests

from devx.models import BrevWorkspace, Project


def run_brev_org():
    """Run `brev org` to display current organization info."""
    print("🔍 Running `brev org` to display current organization info...")
    try:
        subprocess.run(["brev", "org"], check=True)
    except FileNotFoundError as e:
        raise RuntimeError("❌ `brev` CLI not found. Make sure it's installed and in your PATH.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ `brev org` failed with exit code {e.returncode}") from e


def create_launchable(workspace: BrevWorkspace, project: Project) -> Optional[str]:
    """Create a Brev launchable workspace.

    Args:
        workspace: The workspace configuration.
        project: The project configuration.

    Returns:
        The launchable ID if successful, None otherwise.
    """
    url = (
        "https://brevapi2.us-west-2-prod.control-plane.brev.dev/api/"
        f"organizations/{workspace.org_id}/v2/launchables?utm_source=devx-cli"
    )

    headers = {
        "Authorization": f"Bearer {workspace.access_token}",
        "Content-Type": "application/json",
        "User-Agent": "devx-cli"
    }

    payload = {
        "name": project.description,
        "createWorkspaceRequest": {
            "instanceType": workspace.instance_type,
            "workspaceGroupId": workspace.workspace_group_id,
            "storage": workspace.storage or "",
            "firewallRules": []
        },
        "buildRequest": {
            "ports": [port.model_dump() for port in workspace.ports],
            "dockerCompose": {
                "fileUrl": f"{project.repo_url}/blob/main/.devx/docker-compose.yaml",
                "jupyterInstall": False,
                "registries": []
            }
        },
        "file": {
            "url": project.repo_url,
            "path": "./project"
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    launchable_id = response.json().get("id")
    if launchable_id:
        return launchable_id
    return None
