#!/usr/bin/env python3
"""
Deploy the Central Market Micro-Grant Multi-Agent System to Vertex AI Agent Runtime.
Usage:
  python3 scripts/deploy_agent_runtime.py --project YOUR_PROJECT_ID --region us-central1
"""

import argparse
import os
import pickle
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure working directory and sys.path are rooted at the repository root
# so extra_packages archive with relative paths (e.g., `agents/...`, `server/...`).
REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.runtime_app import CentralMarketReliefAgentRuntime


def clean_pycache_dirs(dirs):
    """Remove local __pycache__ directories so Python 3.14 .pyc files aren't tarred."""
    for d in dirs:
        p = REPO_ROOT / d
        if p.is_dir():
            for cache_dir in p.rglob("__pycache__"):
                shutil.rmtree(cache_dir, ignore_errors=True)


def get_credentials():
    """
    Attempts google.auth.default(), and falls back to gcloud auth print-access-token.
    """
    import google.auth
    import google.oauth2.credentials

    try:
        creds, _ = google.auth.default()
        return creds
    except Exception:
        pass

    gcloud_bin = shutil.which("gcloud") or "/Users/gauravrai/Downloads/google-cloud-sdk/bin/gcloud"
    if os.path.exists(gcloud_bin):
        try:
            token = subprocess.check_output([gcloud_bin, "auth", "print-access-token"], text=True).strip()
            return google.oauth2.credentials.Credentials(token)
        except Exception as e:
            print(f"[Warning] Failed to get token from gcloud: {e}")

    return None


def main():
    parser = argparse.ArgumentParser(description="Deploy to Google Agent Runtime")
    parser.add_argument(
        "--project",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
    )
    parser.add_argument("--region", default=os.environ.get("REGION", "us-central1"))
    parser.add_argument("--display-name", default="central-market-relief-orchestrator")
    args = parser.parse_args()

    if not args.project:
        print("Error: Specify --project or export GOOGLE_CLOUD_PROJECT")
        sys.exit(1)

    staging_bucket = f"gs://{args.project}-agent-runtime-staging"

    print("=" * 60)
    print(f" Deploying to Vertex AI Agent Runtime (Reasoning Engine)")
    print(f" Project        : {args.project}")
    print(f" Region         : {args.region}")
    print(f" Staging Bucket : {staging_bucket}")
    print("=" * 60)

    try:
        import cloudpickle
        import vertexai
        from vertexai.preview import reasoning_engines
    except ImportError:
        print("Error: vertexai SDK not found. Install with: python3 -m pip install 'google-cloud-aiplatform>=1.60.0'")
        sys.exit(1)

    # Use protocol 4 for cross-version pickle compatibility (Python 3.14 -> 3.12)
    cloudpickle.DEFAULT_PROTOCOL = 4
    pickle.DEFAULT_PROTOCOL = 4

    creds = get_credentials()

    vertexai.init(
        project=args.project,
        location=args.region,
        staging_bucket=staging_bucket,
        credentials=creds
    )

    # Instantiate from `server.runtime_app` (not `__main__`) so cloudpickle
    # serializes by module reference instead of embedding Python 3.14 bytecode.
    app = CentralMarketReliefAgentRuntime(project_id=args.project)

    # Relative paths from REPO_ROOT so tarfile extracts directly into the remote workdir
    extra_packages = [
        "server",
        "agents",
        "tools",
        "ADK",
        "adk_context_loader.py",
    ]
    clean_pycache_dirs(["server", "agents", "tools", "ADK"])

    print("\nRegistering and packaging agent artifacts with Vertex AI...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        app,
        requirements=[
            "cloudpickle>=3.0.0",
            "google-cloud-bigquery>=3.20.0",
            "google-cloud-aiplatform>=1.60.0",
            "pydantic>=2.0.0",
        ],
        extra_packages=extra_packages,
        display_name=args.display_name,
        description="Central Market Small Business Relief Multi-Agent Orchestrator",
        sys_version="3.12"
    )

    print("\n Deployment Successful!")
    print(f" Resource Name: {remote_agent.resource_name}")
    resource_file = REPO_ROOT / "server" / ".agent_runtime_resource"
    resource_file.write_text(remote_agent.resource_name + "\n")
    print("\nNext: Connect Cloud Run to this Agent Runtime by running:")
    print("  bash scripts/deploy.sh")


if __name__ == "__main__":
    main()
