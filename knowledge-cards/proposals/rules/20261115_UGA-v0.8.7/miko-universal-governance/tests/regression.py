#!/usr/bin/env python3
"""Negative regression tests: inject faults and verify the right checker fails."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tsv_check import run_all, FILE_ALIASES  # noqa: E402


def resolve(d: Path, fname: str) -> Path:
    p = d / fname
    if p.exists():
        return p
    for alt in FILE_ALIASES.get(Path(fname).name, ()):
        if (d / alt).exists():
            return d / alt
    return p


def mutate(d: Path, fname: str, old: str, new: str):
    p = resolve(d, fname)
    t = p.read_text(encoding="utf-8")
    assert old in t, f"mutation anchor not found in {fname}: {old[:40]}"
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


CASES = [
    ("R-01", "TSV-STRUCT", "ucp-spec.md", "- **Recovery**：修正後回 A08。", "- **Recovery2**：修正後回 A08。"),
    ("R-02", "TSV-STRUCT", "uac-spec.md", "## 11. 恢復與回復", "## 11x. 恢復與回復"),
    ("R-03", "TSV-DAG", "deps.yaml", "  - {from: TST, to: TSV, kind: run-time}", "  - {from: TST, to: TSV, kind: run-time}\n  - {from: UAC, to: UCP, kind: run-time}"),
    ("R-04", "TSV-OVERLAP", "matrix.md", "| 路由判定 | — | 消費 | — | — | 擁有 | — | 消費 |", "| 路由判定 | — | 擁有 | — | — | 擁有 | — | 消費 |"),
    ("R-05", "TSV-ROUTE", "contract.yaml", "  - {route_id: RSL-R07, artifact: test-spec, contract: UAC, checker: [TSV-CONTRACT, TSV-EXIT]}", ""),
    ("R-06", "TSV-RUNTIME", "structure.md", "## 6. 熱插拔與 Runtime 宣告", "已支援熱插拔。\n\n## 6. 熱插拔與 Runtime 宣告"),
    ("R-07", "TSV-EXIT", "ucp-spec.md", "`retest_round` | 對受影響 AC 全集完整重測一次 | 3 |", "`retest_round` | 對受影響 AC 全集完整重測一次 | 9999 |"),
    ("R-08", "TSV-SKILL", "usc-spec.md", "| 失敗與回復 | USC-C7 |", "| 失敗與回復X | USC-C7X |"),
    ("R-09", "TSV-REG", "structure.md", "MANIFEST.sha256", "MANIFEST.bak"),
    ("R-10", "TSV-FMT", "ucp-spec.md", "`AC-A08-02` 無空結果", "`AC-A08-02` 結果完整正確"),
    ("R-11", "TSV-AUDIT", "ucp-spec.md", "| L3 | 人類驗收者 |", "| LX | 人類驗收者 |"),
    ("R-12", "TSV-AUDIT", "ucp-spec.md", "├── MANIFEST.sha256", "├── MANIFEST.txt"),
    ("R-13", "TSV-AUDIT", "ucp-spec.md", "| `contact_with_author` |", "| `contact_flag` |"),
    ("R-14", "TSV-AUDIT", "ucp-spec.md", "`AC-A12-06` `AUDIT_PASS` 未經 R-CONV", "`AC-A12-99` `AUDIT_PASS` 未經 R-CONV"),
    ("R-15", "TSV-LEDGER", "ledger-spec.md", "`err.md`", "`error.md`"),
    ("R-16", "TSV-LEDGER", "ucp-spec.md", "`AC-A00-04` 治理、錯誤帳、否決帳皆有載入結果或未讀原因", "`AC-A00-99` 治理、錯誤帳、否決帳皆有載入結果或未讀原因"),
    ("R-17", "TSV-STRUCT", "ucp-spec.md", "- **Recovery**：修正後回 A08。", "- **RecoveryX**：修正後回 A08。"),
    ("R-18", "TSV-LEDGER", "ledger-spec.md", "已裁決為全域單一帳本", "已裁決為專案分檔"),
    ("R-19", "TSV-AUDIT", "ucp-spec.md", "最後一行是流程鎖，流程鎖的通過、降級、UNKNOWN 三數相加等於標籤數。", "最後一行是摘要。"),
    ("R-20", "TSV-AUDIT", "ucp-spec.md", "後設四項", "後設摘要"),
    ("R-21", "TSV-AUDIT", "ucp-spec.md", "最小受影響單元", "整體重跑"),
    ("R-22", "TSV-AUDIT", "uac-spec.md", "對應方向為單向", "對應方向為雙向"),
    ("R-23", "TSV-AUDIT", "uac-spec.md", "由 ARC-1～ARC-5 取代適用", "由 ARC 全面取代"),
    ("R-24", "TSV-AUDIT", "core-closure/core-rewrite-spec.md", "### C6 交付收工", "### C6 摘要"),
    ("R-25", "TSV-AUDIT", "closure/closure-report.md", "tools/behavior_stats.py", "手動統計"),
]


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    results = []
    for cid, checker, fname, old, new in CASES:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "cand"
            shutil.copytree(src, d)
            mutate(d, fname, old, new)
            res = run_all(d)
            got = {r["checker"]: r["status"] for r in res}
            ok = got.get(checker) == "FAIL"
            results.append({
                "case": cid, "expect_fail_checker": checker, "file": fname,
                "result": "PASS" if ok else "FAIL",
                "detail": f"{checker} status={got.get(checker)}",
                "other_fails": [k for k, v in got.items() if v == "FAIL" and k != checker],
            })
    overall = "PASS" if all(r["result"] == "PASS" for r in results) else "FAIL"
    out.write_text(json.dumps({"overall": overall, "cases": results}, ensure_ascii=False, indent=2))
    for r in results:
        print(f"{r['case']} {r['result']} expect={r['expect_fail_checker']} detail={r['detail']} other={r['other_fails']}")
    print("OVERALL", overall)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
