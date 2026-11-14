#!/usr/bin/env python3
"""TSV-VERSION: every VERSION file and md front matter must equal root VERSION."""
import json
import re
import sys
from pathlib import Path

import yaml


def main(root: Path):
    issues = []
    rv = root / "VERSION"
    if not rv.exists():
        print(json.dumps({"checker": "TSV-VERSION", "status": "FAIL", "items": ["根目錄缺 VERSION"]}, ensure_ascii=False))
        return 1
    root_ver = rv.read_text().splitlines()[0].strip()
    for p in sorted(root.rglob("VERSION")):
        if p == rv:
            continue
        v = p.read_text().splitlines()[0].strip() if p.read_text().strip() else ""
        if v != root_ver:
            issues.append(f"{p.relative_to(root)}: {v} != {root_ver}")
    for p in sorted(root.rglob("*.md")):
        m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            issues.append(f"{p.relative_to(root)}: front matter 無法解析")
            continue
        v = str(fm.get("version", ""))
        if v and v != root_ver:
            issues.append(f"{p.relative_to(root)}: front matter {v} != {root_ver}")
    res = {"checker": "TSV-VERSION", "root_version": root_ver,
           "status": "PASS" if not issues else "FAIL", "items": issues}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
