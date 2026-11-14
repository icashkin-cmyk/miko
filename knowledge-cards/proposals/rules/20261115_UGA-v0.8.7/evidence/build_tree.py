#!/usr/bin/env python3
"""Build the proposed GitHub folder skeleton from the candidate docs."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

CAND = Path(sys.argv[1])
OUT = Path(sys.argv[2])
DATE = "2026-11-14"
VER = "0.2.1"

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

MODULES = {
    "governance": ("治理層", "Governance Layer", "A0 硬邊界、W1～W7、A3 狀態字典"),
    "universal-creation-process": ("通用製作流程", "Universal Creation Process", "A00～A13 製作主幹與閉環"),
    "universal-artifact-contract": ("通用產物契約", "Universal Artifact Contract", "規格類十六章與必要欄位"),
    "universal-skill-contract": ("通用 Skill 契約", "Universal Skill Contract", "九契約、四節、P/C/J 七欄"),
    "routing-and-selection": ("路由與選擇", "Routing and Selection", "產物類型 → 契約 → 驗收器"),
    "lifecycle-and-versioning": ("生命週期與版本", "Lifecycle and Versioning", "版本、快照、退役、熱插拔"),
    "testing-and-validation": ("測試與驗證", "Testing and Validation", "11 個檢查器與回歸"),
    "skills": ("Skills", "Skills", "符合 USC 的 Skill"),
    "adapters": ("Adapters", "Adapters", "執行環境介面（全部 PLACEHOLDER／UNKNOWN）"),
    "tests": ("Tests", "Tests", "檢查器與測資"),
    "archive": ("Archive", "Archive", "快照、退役、ADR"),
}


def readme(zh, en, purpose):
    return f"""# {zh}（{en}）
狀態：PROPOSED｜版本：{VER}｜日期：{DATE}｜Runtime：UNKNOWN

## 目的
{purpose}。本模組只負責此一範圍，其餘責任依 matrix.md 分派。

## 範圍與非範圍
範圍見本模組規格檔；非範圍一律交由其他模組，並在引用時註明版本。

## 檔案
| 檔名 | 用途 | 版本 |
|---|---|---|
| VERSION | 版本檔 | {VER} |

## 與其他模組的關係
依賴方向以 deps.yaml 為準；本 README 不另行宣告依賴。

## 使用方式
依 UCP A00～A13 製作與驗收；採用前須 AUDIT_PASS。

## 驗收方式
TSV 檢查器與本模組 AC；未合格不得交付。

## 失敗與回復
見 ucp-spec.md §7 與 modules-spec.md §LCV。

## 維護者與變更紀錄
| 版本 | 日期 | commit | SHA-256 | 變更 |
|---|---|---|---|---|
| {VER} | {DATE} | NOT_COMMITTED | 見 MANIFEST | 初始候選 |

## 未決事項
| ID | 描述 | 狀態 |
|---|---|---|
| OPEN-01 | 待總召裁決 | PENDING_DECISION |
"""


def split_modules(text: str):
    parts = {}
    for key, pat in (("rsl", r"## RSL："), ("lcv", r"## LCV："), ("tsv", r"## TSV：")):
        m = re.search(pat, text)
        if not m:
            continue
        start = m.start()
        nxt = re.search(r"\n## (?!RSL：|LCV：|TSV：)", text[m.end():])
        end = m.end() + nxt.start() if nxt else len(text)
        parts[key] = text[start:end].strip()
    return parts


def main():
    contract = yaml.safe_load((CAND / "contract.yaml").read_text())
    (OUT / "VERSION").write_text(f"{VER}\n")
    (OUT / "README.md").write_text(
        f"# MIKO Universal Governance Architecture\n狀態：PROPOSED｜版本：{VER}｜日期：{DATE}｜Runtime：UNKNOWN\n\n"
        "本倉庫為候選架構，尚未寫入 GitHub、尚未正式採用、尚未 Runtime 生效。\n"
        "入口文件：universal-creation-process/ucp-spec.md。\n")

    for mod, (zh, en, purpose) in MODULES.items():
        d = OUT / mod
        d.mkdir()
        (d / "README.md").write_text(readme(zh, en, purpose))
        if mod not in ("skills", "tests"):
            (d / "VERSION").write_text(f"{VER}\n")
        if mod not in ("skills", "tests", "archive"):
            (d / "snapshots").mkdir()

    shutil.copy(CAND / "ucp-spec.md", OUT / "universal-creation-process/ucp-spec.md")
    (OUT / "universal-creation-process/ucp-steps.yaml").write_text(
        yaml.safe_dump({"schema": "miko-ucp-steps/1", "version": VER, **contract["ucp"]},
                       allow_unicode=True, sort_keys=False))
    shutil.copy(CAND / "uac-spec.md", OUT / "universal-artifact-contract/uac-spec.md")
    (OUT / "universal-artifact-contract/uac-chapters.yaml").write_text(
        yaml.safe_dump({"schema": "miko-uac-chapters/1", "version": VER, "chapters": contract["uac"]["chapters"]},
                       allow_unicode=True, sort_keys=False))
    shutil.copy(CAND / "usc-spec.md", OUT / "universal-skill-contract/usc-spec.md")
    (OUT / "universal-skill-contract/usc-contracts.yaml").write_text(
        yaml.safe_dump({"schema": "miko-usc/1", "version": VER, **contract["usc"]},
                       allow_unicode=True, sort_keys=False))

    mods = split_modules((CAND / "modules-spec.md").read_text())
    (OUT / "routing-and-selection/rsl-spec.md").write_text(
        f"---\ndoc_id: rsl-spec\nname_zh: 路由與選擇\nversion: {VER}\ndate: {DATE}\nstatus: PROPOSED\n---\n\n" + mods["rsl"] + "\n")
    (OUT / "routing-and-selection/rsl-routes.yaml").write_text(
        yaml.safe_dump({"schema": "miko-routes/1", "version": VER, "routes": contract["routes"]},
                       allow_unicode=True, sort_keys=False))
    (OUT / "lifecycle-and-versioning/lcv-spec.md").write_text(
        f"---\ndoc_id: lcv-spec\nname_zh: 生命週期與版本\nversion: {VER}\ndate: {DATE}\nstatus: PROPOSED\n---\n\n" + mods["lcv"] + "\n")
    (OUT / "testing-and-validation/tsv-spec.md").write_text(
        f"---\ndoc_id: tsv-spec\nname_zh: 測試與驗證\nversion: {VER}\ndate: {DATE}\nstatus: PROPOSED\n---\n\n" + mods["tsv"] + "\n")
    shutil.copy(CAND / "acceptance-matrix.md", OUT / "testing-and-validation/tsv-matrix.md")
    shutil.copy(CAND / "deps.yaml", OUT / "lifecycle-and-versioning/deps.yaml")
    shutil.copy(CAND / "matrix.md", OUT / "governance/matrix.md")
    shutil.copy(CAND / "structure.md", OUT / "governance/structure.md")
    shutil.copy(CAND / "readme-templates.md", OUT / "governance/readme-templates.md")

    for sub in ("claude-code", "manus", "github", "generic"):
        d = OUT / "adapters" / sub
        d.mkdir()
        (d / "README.md").write_text(
            f"# {sub} adapter\n狀態：PLACEHOLDER｜Runtime：UNKNOWN\n\n"
            "只有介面約定，沒有任何 Runtime 實測證據。不得宣稱已支援熱插拔；升格需 LCV H-04 三項證據。\n")
    for sub in ("unit", "contract", "integration", "regression", "fixtures"):
        (OUT / "tests" / sub).mkdir()
    (OUT / "tests/README.md").write_text(
        "# Tests（Tests）\n狀態：PROPOSED｜版本：0.2.1｜日期：2026-11-14｜Runtime：UNKNOWN\n\n"
        "放置 tsv_check.py、regression.py 與測資；結果寫入 results/。\n")
    for sub in ("snapshots", "retired", "decisions"):
        (OUT / "archive" / sub).mkdir()
    (OUT / "archive/README.md").write_text(
        "# Archive（Archive）\n狀態：PROPOSED｜版本：0.2.1｜日期：2026-11-14｜Runtime：UNKNOWN\n\n"
        "只新增不改寫。快照命名依 N-05；退役依 RT-01～RT-05。\n")

    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
    lines = []
    for p in files:
        h = subprocess.run(["sha256sum", str(p)], capture_output=True, text=True).stdout.split()[0]
        lines.append(f"{h}  {p.relative_to(OUT)}")
    (OUT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print(f"built {OUT} files={len(files)}")


if __name__ == "__main__":
    main()
