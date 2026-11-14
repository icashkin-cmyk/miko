#!/usr/bin/env python3
"""MIKO correction ledger: init / load / write / snapshot / verify.

Canonical store: ledger/entries.json
Rendered:        ledger/err.md, rej.md, chg.md, index.yaml
Dedupe:          sha256 of (type|dedupe_key) -> one entry, updates keep history.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

TPE = timezone(timedelta(hours=8))
TYPES = {"err": "錯誤帳", "rej": "否決帳", "chg": "變更帳"}
FILES = {"err": "err.md", "rej": "rej.md", "chg": "chg.md"}


def now():
    return datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S+08:00")


def store(root: Path) -> Path:
    return root / "ledger" / "entries.json"


def load_entries(root: Path):
    p = store(root)
    if not p.exists():
        return {"version": "1.0.0", "entries": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save(root: Path, data):
    p = store(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def dedupe(type_, key):
    return hashlib.sha256(f"{type_}|{key}".encode()).hexdigest()[:16]


def render(root: Path, data):
    d = root / "ledger"
    d.mkdir(parents=True, exist_ok=True)
    for t, label in TYPES.items():
        rows = [e for e in data["entries"] if e["type"] == t]
        out = [f"# {label}（{len(rows)} 筆）", ""]
        out.append("| 編號 | 去重鍵 | 專案 | 標題 | 狀態 | 更新時間 |")
        out.append("|---|---|---|---|---|---|")
        for e in rows:
            out.append(f"| {e['id']} | `{e['dedupe_key']}` | {e['project_id']} | {e['title']} | {e['status']} | {e['updated_at']} |")
        out.append("")
        for e in rows:
            out.append(f"## {e['id']}　{e['title']}")
            out.append("")
            out.append(e["body"].strip())
            out.append("")
            out.append(f"狀態：{e['status']}｜專案：{e['project_id']}｜建立：{e['created_at']}｜更新：{e['updated_at']}｜修訂：{e['rev']}")
            if e.get("history"):
                out.append("")
                out.append("歷史（就地更新保留前一版）：")
                for h in e["history"]:
                    out.append(f"- {h['at']}｜{h['rev']}｜{h['note']}")
            out.append("")
        (d / FILES[t]).write_text("\n".join(out), encoding="utf-8")
    counts = {t: sum(1 for e in data["entries"] if e["type"] == t) for t in TYPES}
    index = {"schema": "miko-ledger-index/1", "version": data["version"], "counts": counts,
             "rendered_at": now(), "entries_sha256": hashlib.sha256(
                 json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    (d / "index.yaml").write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return index


def cmd_init(a):
    root = Path(a.root)
    if store(root).exists() and not a.force:
        print("ledger 已存在，未覆寫（--force 可重建）")
        return 0
    save(root, {"version": "1.0.0", "entries": []})
    idx = render(root, load_entries(root))
    print(f"init ok: {idx['counts']}")
    return 0


def cmd_load(a):
    root = Path(a.root)
    try:
        data = load_entries(root)
        idx = render(root, data)
        res = {"status": "PASS", "loaded_at": now(), "path": str(store(root)),
               "counts": idx["counts"], "sha256": idx["entries_sha256"]}
    except Exception as e:
        res = {"status": "NOT_READ", "loaded_at": now(), "error": f"{type(e).__name__}: {e}"}
    out = Path(a.out) if a.out else root / "evidence" / "ledger-load.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res["status"] == "PASS" else 1


def cmd_write(a):
    root = Path(a.root)
    if a.type not in TYPES:
        print("type 必須是 err / rej / chg")
        return 2
    data = load_entries(root)
    key = dedupe(a.type, a.key)
    hit = next((e for e in data["entries"] if e["dedupe_key"] == key), None)
    if hit:
        hit["history"].append({"at": hit["updated_at"], "rev": hit["rev"], "note": hit["body"][:120]})
        hit["body"] = a.body
        hit["title"] = a.title or hit["title"]
        hit["status"] = a.status
        hit["rev"] += 1
        hit["updated_at"] = now()
        action = "updated"
        entry = hit
    else:
        n = sum(1 for e in data["entries"] if e["type"] == a.type) + 1
        entry = {"id": f"{a.type.upper()}-{n:03d}", "type": a.type, "dedupe_key": key,
                 "project_id": a.project, "title": a.title, "body": a.body, "status": a.status,
                 "created_at": now(), "updated_at": now(), "rev": 1, "history": []}
        data["entries"].append(entry)
        action = "created"
    save(root, data)
    render(root, data)
    print(json.dumps({"action": action, "id": entry["id"], "rev": entry["rev"], "dedupe_key": key}, ensure_ascii=False))
    return 0


def cmd_snapshot(a):
    root = Path(a.root)
    d = root / "ledger" / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TPE).strftime("%Y%m%dT%H%M%S%z")
    name = f"ledger__{stamp}__v1.json"
    shutil.copy(store(root), d / name)
    print(f"snapshot {d / name}")
    return 0


def cmd_verify(a):
    root = Path(a.root)
    data = load_entries(root)
    idx = yaml.safe_load((root / "ledger" / "index.yaml").read_text(encoding="utf-8"))
    ok = idx["entries_sha256"] == hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["init", "load", "write", "snapshot", "verify"])
    p.add_argument("--root", default=".")
    p.add_argument("--out")
    p.add_argument("--force", action="store_true")
    p.add_argument("--type")
    p.add_argument("--key", default="")
    p.add_argument("--title", default="")
    p.add_argument("--body", default="")
    p.add_argument("--project", default="MIKO-UGA")
    p.add_argument("--status", default="OPEN")
    a = p.parse_args()
    return {"init": cmd_init, "load": cmd_load, "write": cmd_write,
            "snapshot": cmd_snapshot, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
