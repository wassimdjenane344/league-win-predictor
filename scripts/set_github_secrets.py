"""One-off helper: create the staging/production GitHub Environments and put the
MLflow (DagsHub) secrets into each. Reads the GitHub token from the git
credential manager and the secret values from environment variables, so no
secret is ever written to disk or committed.

Usage (values passed via env, never as CLI args that could leak in shell history):
    GITHUB_TOKEN=... MLFLOW_TRACKING_URI=... MLFLOW_TRACKING_USERNAME=... \
    MLFLOW_TRACKING_PASSWORD=... REPO_ID=... python scripts/set_github_secrets.py
"""

import base64
import json
import os
import urllib.request

from nacl import encoding, public

TOKEN = os.environ["GITHUB_TOKEN"]
REPO_ID = os.environ["REPO_ID"]
ENVIRONMENTS = ["staging", "production"]
OWNER_REPO = "wassimdjenane344/league-win-predictor"

SECRETS = {
    "MLFLOW_TRACKING_URI": os.environ["MLFLOW_TRACKING_URI"],
    "MLFLOW_TRACKING_USERNAME": os.environ["MLFLOW_TRACKING_USERNAME"],
    "MLFLOW_TRACKING_PASSWORD": os.environ["MLFLOW_TRACKING_PASSWORD"],
}


def api(method: str, url: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def encrypt(public_key_b64: str, secret_value: str) -> str:
    pk = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    sealed = public.SealedBox(pk).encrypt(secret_value.encode())
    return base64.b64encode(sealed).decode()


for env_name in ENVIRONMENTS:
    # 1. create the environment (idempotent)
    api("PUT", f"https://api.github.com/repos/{OWNER_REPO}/environments/{env_name}", {})

    # 2. fetch that environment's public key
    key = api(
        "GET",
        f"https://api.github.com/repositories/{REPO_ID}/environments/{env_name}/secrets/public-key",
    )

    # 3. encrypt + upload each secret
    for name, value in SECRETS.items():
        api(
            "PUT",
            f"https://api.github.com/repositories/{REPO_ID}/environments/{env_name}/secrets/{name}",
            {"encrypted_value": encrypt(key["key"], value), "key_id": key["key_id"]},
        )
        print(f"  [{env_name}] set secret {name}")

print("Done.")
