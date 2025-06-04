"""Brev workspace creation functionality."""

import argparse
import json
import subprocess
import sys
from typing import Optional

import requests

from devx.models import BrevWorkspace, Project

TARGET_BRANCH = "main"


def run_brev_org():
    """Run `brev org` to display current organization info."""
    print("🔍 Running `brev org` to display current organization info...")
    try:
        subprocess.run(["brev", "org"], check=True)
    except FileNotFoundError as e:
        raise RuntimeError("❌ `brev` CLI not found. Make sure it's installed and in your PATH.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ `brev org` failed with exit code {e.returncode}") from e


def create_launchable(workspace: BrevWorkspace, project: Project, dry_run: bool = False) -> Optional[str]:
    """Create a Brev launchable workspace.

    Args:
        workspace: The workspace configuration.
        project: The project configuration.
        dry_run: If True, only show the API request payload without making the request.

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
                "fileUrl": (
                    f"{project.repo_url}/raw/{TARGET_BRANCH}/{workspace.relative_to_root}/"
                    ".devx/compose.yaml"
                ),
                "jupyterInstall": False,
                "registries": []
            }
        },
        "file": {
            "url": project.repo_url,
            "path": "./"
        }
    }

    if dry_run:
        print("\n📦 API Request Details:")
        print(f"URL: {url}")
        print("\nPayload:")
        print(json.dumps(payload, indent=2))
        return None

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.json()


def create(args: argparse.Namespace, workspace: BrevWorkspace, project: Project) -> None:
    """Create a launchable workshop on Brev.

    Args:
        args: Command line arguments.
        workspace: Brev workspace configuration.
        project: Project configuration.
    """
    run_brev_org()

    print("\n⚠️  About to create launchable with the following configuration:")
    print(f"  - Name: {project.description}")
    print(f"  - Instance Type: {workspace.instance_type}")
    print(f"  - Workspace Group: {workspace.workspace_group_id}")
    print(f"  - Storage: {workspace.storage or 'None'}")
    print(f"  - Ports: {[port.model_dump() for port in workspace.ports]}")
    print(f"  - Repository: {project.repo_url}")
    print(f"  - Image: {project.image_url}/devx:{TARGET_BRANCH}")

    if not args.yes and input("\nContinue? [y/N] ").lower() != 'y':
        print("❌ Aborted.")
        sys.exit(1)

    print("\n📦 Creating launchable...")
    api_response = create_launchable(workspace, project, dry_run=args.dry_run)
    if not api_response or not api_response.get("id"):
        if not args.dry_run:
            print("❌ Failed to create launchable.")
            print(f"Server response: {api_response}")
            sys.exit(1)
        return

    if not args.dry_run:
        print(f"\n✅ Launchable created with ID: {api_response.get('id')}")
        print(f"  ✨ https://brev.nvidia.com/launchable/deploy/now?launchableID={api_response.get('id')}")
