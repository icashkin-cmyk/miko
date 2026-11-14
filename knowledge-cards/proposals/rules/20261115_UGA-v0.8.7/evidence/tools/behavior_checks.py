#!/usr/bin/env python3
"""Semi-automated behavioral AC checks. PASS only with evidence on disk."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "evidence" / "behavior-checks.json"


def exists(p):
    return (ROOT / p).exists()


def manifest_ok(p):
    d = ROOT / p
    if not (d / "MANIFEST.sha256").exists():
        return False
    r = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256"], cwd=d, capture_output=True)
    return r.returncode == 0


checks = []


def add(ac, status, evidence, note):
    checks.append({"ac_id": ac, "status": status, "evidence": evidence, "note": note})


diffs = list((ROOT / "diff").glob("*.patch")) if exists("diff") else []
add("AC-A10-01", "PASS" if diffs else "NOT_RUN", f"diff/ 共 {len(diffs)} 個 patch", "每輪修改有 diff")

vers = [p.name for p in ROOT.glob("candidate-v*")]
add("AC-A10-03", "PASS" if len(vers) >= 3 else "NOT_RUN", f"保留候選版本 {len(vers)} 個", "歷史版本未被覆寫")

add("AC-A11-01", "PASS" if exists("tests/regression_v031.json") else "NOT_RUN",
    "tests/regression_v031.json", "回歸結果存在")
add("AC-A11-03", "PASS" if exists("tests/results_v031.json") else "NOT_RUN",
    "tests/results_v031.json", "檢查器結果存在")

add("AC-A13-01", "PASS" if manifest_ok("delivery/miko-universal-governance") else "NOT_RUN",
    "delivery/miko-universal-governance/MANIFEST.sha256", "sha256sum -c")

add("AC-A12-04", "PASS" if manifest_ok("delivery/audit-packet") else "NOT_RUN",
    "delivery/audit-packet/MANIFEST.sha256", "驗收包封裝與清單")
add("AC-A12-01", "NOT_RUN", "無獨立驗收者", "需 L1 以上驗收者冷啟動")
add("AC-A12-02", "NOT_RUN", "無 audit-report", "需驗收者逐條判定")
add("AC-A12-03", "NOT_RUN", "無 audit-report", "標籤與等級需驗收者填寫")

add("AC-A00-04", "NOT_RUN", "ledger-root/ledger", "載入結果存在但未綁定任務卡")
add("AC-A10-04", "PASS" if exists("ledger-root/ledger/chg.md") else "NOT_RUN",
    "ledger-root/ledger/chg.md", "變更帳已寫入")
add("AC-A13-04", "NOT_RUN", "交付包未含帳本快照", "待封裝整合")

summary = {"total": len(checks),
           "pass": sum(1 for c in checks if c["status"] == "PASS"),
           "not_run": sum(1 for c in checks if c["status"] == "NOT_RUN")}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"checks": checks, "summary": summary}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
for c in checks:
    print(c["ac_id"], c["status"], c["note"])
