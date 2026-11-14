#!/usr/bin/env python3
"""Audit packet builder (minimal viable): build / verify.

Layout (per UCP 附錄 A):
  audit-packet/MANIFEST.sha256, packet-meta.yaml, artifact/, ac/, contract/, diff/, checks/
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

TPE = timezone(timedelta(hours=8))
ALLOWED = ("MANIFEST.sha256", "packet-meta.yaml", "artifact", "ac", "contract", "diff", "checks")


def now():
    return datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S+08:00")


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def version_of(cand: Path):
    v = cand / "VERSION"
    if v.exists():
        return v.read_text().splitlines()[0].strip()
    t = (cand / "ucp-spec.md").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*(\S+)", t, re.M)
    return m.group(1) if m else "UNKNOWN"


def strip_diff(p: Path) -> str:
    """Remove commit-message/annotation lines that could leak author reasoning."""
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("Subject:", "From:", "Date:", "# ")):
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def build(cand: Path, out: Path, task: str, diffdir: Path | None, checks: list[Path]):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "artifact").mkdir()
    (out / "ac").mkdir()
    (out / "contract").mkdir()
    (out / "diff").mkdir()
    (out / "checks").mkdir()

    for f in ("ucp-spec.md", "uac-spec.md", "usc-spec.md", "ledger-spec.md", "modules-spec.md"):
        if (cand / f).exists():
            shutil.copy(cand / f, out / "artifact" / f)
    if (cand / "acceptance-matrix.md").exists():
        shutil.copy(cand / "acceptance-matrix.md", out / "ac" / "ac-table.md")
    for f in ("uac-spec.md", "usc-spec.md"):
        if (cand / f).exists():
            shutil.copy(cand / f, out / "contract" / f)
    if diffdir and diffdir.exists():
        for p in sorted(diffdir.glob("*.patch")):
            (out / "diff" / p.name).write_text(strip_diff(p), encoding="utf-8")
    for c in checks:
        if c.exists():
            shutil.copy(c, out / "checks" / c.name)

    files = sorted(p for p in out.rglob("*") if p.is_file())
    lines = [f"{sha(p)}  {p.relative_to(out)}" for p in files]
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta = {
        "schema": "miko-audit-packet/1",
        "packet_version": f"pkt-{datetime.now(TPE).strftime('%Y%m%dT%H%M%S%z')}-v{version_of(cand)}",
        "task_id": task,
        "packed_by": "R-EVD",
        "packed_at": now(),
        "artifact_version": version_of(cand),
        "contract_version": version_of(cand),
        "file_count": len(files),
        "excluded": ["作者辯解", "自我驗收結論", "實作思路", "對話紀錄"],
    }
    (out / "packet-meta.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    # meta must not be inside manifest (it declares file_count) -> recompute including meta
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
    lines = [f"{sha(p)}  {p.relative_to(out)}" for p in files]
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return meta


def verify(out: Path):
    r = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256"], cwd=out, capture_output=True, text=True)
    extra = [p.name for p in out.iterdir() if p.name not in ALLOWED]
    bad = [l for l in r.stdout.splitlines() if "OK" not in l]
    res = {"manifest_check": "PASS" if r.returncode == 0 else "FAIL",
           "files": len([l for l in r.stdout.splitlines() if "OK" in l]),
           "failed": bad, "unexpected": extra}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "verify"])
    ap.add_argument("--cand", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="uga-candidate")
    ap.add_argument("--diffdir")
    ap.add_argument("--checks", nargs="*", default=[])
    a = ap.parse_args()
    cand = Path(a.cand)
    out = Path(a.out)
    if a.cmd == "build":
        meta = build(cand, out, a.task, Path(a.diffdir) if a.diffdir else None, [Path(c) for c in a.checks])
        print(json.dumps(meta, ensure_ascii=False))
        print(json.dumps(verify(out), ensure_ascii=False))
    else:
        res = verify(out)
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res["manifest_check"] == "PASS" and not res["unexpected"] else 1


if __name__ == "__main__":
    sys.exit(main())
