import json
import requests
import subprocess
import re
from pathlib import Path

def run_brev_org():
    print("🔍 Running `brev org` to display current organization info...")
    try:
        subprocess.run(["brev", "org"], check=True)
    except FileNotFoundError:
        raise RuntimeError("❌ `brev` CLI not found. Make sure it's installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ `brev org` failed with exit code {e.returncode}")

def get_access_token():
    cred_path = Path.home() / ".brev" / "credentials.json"
    with open(cred_path) as f:
        return json.load(f)["access_token"]

def get_org_id():
    org_path = Path.home() / ".brev" / "active_org.json"
    with open(org_path) as f:
        return json.load(f)["id"]

def get_repo_https_url():
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

def create_launchable():
    run_brev_org()
    token = get_access_token()
    org_id = get_org_id()
    repo_url = get_repo_https_url()

    url = f"https://brevapi2.us-west-2-prod.control-plane.brev.dev/api/organizations/{org_id}/v2/launchables?utm_source=devx-cli"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "devx-cli"
    }

    payload = {
        "name": "Workshop Launchable Template",
        "createWorkspaceRequest": {
            "instanceType": "l40s-48gb.1x",
            "workspaceGroupId": "crusoe-brev-wg",
            "storage": "",
            "firewallRules": []
        },
        "buildRequest": {
            "ports": [
                {"name": "Jupyter", "port": "8888"}
            ],
            "dockerCompose": {
                "fileUrl": f"{repo_url}/raw/main/docker-compose.yaml",
                "jupyterInstall": False,
                "registries": []
            }
        },
        "file": {
            "url": repo_url,
            "path": "./"
        }
    }

    print("\n📦 Creating launchable...")
    response = requests.post(url, headers=headers, json=payload)

    # Print full HTTP response
    print(f"\n✅ HTTP {response.status_code} {response.reason}")
    print("🔁 Response Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")

    print("\n📦 Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(response.text)

if __name__ == "__main__":
    create_launchable()

