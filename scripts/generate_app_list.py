#!/usr/bin/env python3
"""
generate_app_list.py
Scans the apps/ directory and generates app-list.json at the repo root.
Each app directory must contain a manifest.json file.
Git metadata (last commit SHA, date, author) is added automatically.
"""

import json
import os
import subprocess
from datetime import datetime, timezone

REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR   = os.path.join(REPO_ROOT, "apps")
OUTPUT     = os.path.join(REPO_ROOT, "app-list.json")


def git_log_for(path: str) -> dict:
    """Return last-commit metadata for *path* relative to REPO_ROOT."""
    try:
        result = subprocess.run(
            ["git", "-C", REPO_ROOT, "log", "-1",
             "--format=%H|%aI|%an", "--", path],
            capture_output=True, text=True, check=True,
        )
        parts = result.stdout.strip().split("|")
        if len(parts) == 3 and parts[0]:
            return {
                "last_commit_sha": parts[0],
                "last_updated":    parts[1],
                "last_updated_by": parts[2],
            }
    except (subprocess.CalledProcessError, OSError):
        pass
    return {
        "last_commit_sha": "",
        "last_updated":    datetime.now(timezone.utc).isoformat(),
        "last_updated_by": "",
    }


def load_apps() -> list:
    apps = []
    if not os.path.isdir(APPS_DIR):
        return apps

    for entry in sorted(os.listdir(APPS_DIR)):
        app_dir = os.path.join(APPS_DIR, entry)
        if not os.path.isdir(app_dir):
            continue

        manifest_path = os.path.join(app_dir, "manifest.json")
        if not os.path.isfile(manifest_path):
            print(f"  WARNING: skipping '{entry}' – no manifest.json found")
            continue

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"  ERROR: skipping '{entry}' – invalid manifest.json: {exc}")
            continue

        required_fields = ("id", "name", "entry")
        missing = [k for k in required_fields if k not in manifest]
        if missing:
            print(f"  ERROR: skipping '{entry}' – missing fields: {missing}")
            continue

        git_meta = git_log_for(os.path.join("apps", entry))

        app_record = {
            "id":          manifest["id"],
            "name":        manifest["name"],
            "description": manifest.get("description", ""),
            "author":      manifest.get("author", ""),
            "version":     manifest.get("version", ""),
            "entry":       manifest["entry"],
            "category":    manifest.get("category", ""),
            "last_updated":    git_meta["last_updated"],
            "last_updated_by": git_meta["last_updated_by"],
            "last_commit_sha": git_meta["last_commit_sha"],
        }
        apps.append(app_record)
        print(f"  + {app_record['id']} v{app_record['version']} ({app_record['author']})")

    return apps


def main():
    print("Generating app-list.json …")
    apps = load_apps()

    output = {
        "version":      "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "app_count":    len(apps),
        "apps":         apps,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Done – {len(apps)} app(s) written to {OUTPUT}")


if __name__ == "__main__":
    main()
