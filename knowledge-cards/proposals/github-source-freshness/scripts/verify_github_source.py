#!/usr/bin/env python3
"""Verify GitHub VERSION metadata, main-HEAD fixed-commit contents, freshness headers, and README SHA."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "miko-github-source-freshness",
}
RAW_HEADERS = {
    "Accept": "application/vnd.github.raw+json",
    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "miko-github-source-freshness",
}


def now_taipei() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=8))).strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )


def get(url: str, headers: dict[str, str]) -> bytes:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def raw_url(repo: str, ref: str, path: str) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}?cachebust={stamp}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result: dict[str, object] = {
        "checked_at_taipei": now_taipei(),
        "repo": args.repo,
        "status": "PASS",
        "errors": [],
        "files": {},
    }
    errors: list[str] = result["errors"]  # type: ignore[assignment]

    try:
        api_url = f"https://api.github.com/repos/{args.repo}/contents/VERSION?ref=main"
        metadata = json.loads(get(api_url, API_HEADERS))
        if metadata.get("type") != "file" or metadata.get("encoding") != "base64":
            raise ValueError("VERSION API response is not a base64 file")
        version_api = base64.b64decode(metadata["content"]).decode("utf-8")
        result["version_api_sha"] = metadata.get("sha")
    except Exception as exc:  # noqa: BLE001 - report exact external failure
        errors.append(f"VERSION API NOT_READ: {type(exc).__name__}: {exc}")
        result["status"] = "NOT_READ"
        return write_result(result, args.output)

    try:
        commits_url = f"https://api.github.com/repos/{args.repo}/commits?path=VERSION&per_page=5"
        commits = json.loads(get(commits_url, API_HEADERS))
        commit = commits[0]["sha"]
        result["version_commit"] = commit
        result["version_commit_short"] = commit[:7]
        result["version_commit_message"] = commits[0].get("commit", {}).get("message", "")
        head_url = f"https://api.github.com/repos/{args.repo}/commits?sha=main&per_page=1"
        head = json.loads(get(head_url, API_HEADERS))[0]["sha"]
        result["main_head_commit"] = head
        result["main_head_commit_short"] = head[:7]
    except Exception as exc:  # noqa: BLE001
        errors.append(f"VERSION commit UNKNOWN: {type(exc).__name__}: {exc}")
        result["status"] = "UNKNOWN"
        return write_result(result, args.output)

    try:
        version_fixed = get(raw_url(args.repo, head, "VERSION"), RAW_HEADERS).decode("utf-8")
        if version_api != version_fixed:
            errors.append("CONFLICT: API VERSION differs from fixed-commit VERSION")
            result["status"] = "CONFLICT"
    except Exception as exc:  # noqa: BLE001
        errors.append(f"fixed VERSION NOT_READ: {type(exc).__name__}: {exc}")
        result["status"] = "NOT_READ"
        return write_result(result, args.output)

    version_lines = version_fixed.rstrip("\n").splitlines()
    if len(version_lines) < 4:
        errors.append("FAIL: VERSION has fewer than four lines")
        result["status"] = "FAIL"
    else:
        result["version"] = version_lines[0]
        result["version_date"] = version_lines[1]
        result["adr"] = version_lines[2]
        result["readme_sha_expected"] = version_lines[3]

    for path in args.paths:
        try:
            content = get(raw_url(args.repo, head, path), RAW_HEADERS)
            digest = hashlib.sha256(content).hexdigest()
            result["files"][path] = {"status": "PASS", "sha256": digest, "bytes": len(content)}  # type: ignore[index]
        except urllib.error.HTTPError as exc:
            result["files"][path] = {"status": "NOT_READ", "error": f"HTTP {exc.code}"}  # type: ignore[index]
            errors.append(f"{path} NOT_READ: HTTP {exc.code}")
            result["status"] = "NOT_READ"
        except Exception as exc:  # noqa: BLE001
            result["files"][path] = {"status": "NOT_READ", "error": str(exc)}  # type: ignore[index]
            errors.append(f"{path} NOT_READ: {type(exc).__name__}: {exc}")
            result["status"] = "NOT_READ"

    if "README.md" in args.paths and len(version_lines) >= 4 and result["files"].get("README.md", {}).get("status") == "PASS":  # type: ignore[union-attr]
        actual = result["files"]["README.md"]["sha256"]  # type: ignore[index]
        if actual != version_lines[3]:
            errors.append(f"CONFLICT: README SHA expected {version_lines[3]}, got {actual}")
            result["status"] = "CONFLICT"

    try:
        head_after = json.loads(get(head_url, API_HEADERS))[0]["sha"]
        if head_after != head:
            errors.append(f"STALE: main moved during read ({head[:7]} -> {head_after[:7]}); rerun")
            if result["status"] == "PASS":
                result["status"] = "STALE"
    except Exception as exc:  # noqa: BLE001
        errors.append(f"main HEAD recheck UNKNOWN: {type(exc).__name__}: {exc}")
        if result["status"] == "PASS":
            result["status"] = "UNKNOWN"

    return write_result(result, args.output)


def write_result(result: dict[str, object], output: Path | None) -> int:
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
