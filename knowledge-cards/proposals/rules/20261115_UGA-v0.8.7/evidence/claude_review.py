#!/usr/bin/env python3
"""MIKO UGA candidate review via Claude API.

Usage: claude_review.py <candidate_dir> <round_label> <model>
Writes review/<round_label>.json and .md
"""
import json
import sys
from pathlib import Path

import anthropic

FILES = ["ucp-spec.md", "uac-spec.md", "usc-spec.md", "modules-spec.md", "structure.md", "matrix.md", "deps.yaml", "contract.yaml"]

SYSTEM = (
    "你是 MIKO 專案的獨立架構稽核者。只根據提供的候選規格做靜態審查，"
    "不得假設未提供的內容存在，不得捏造。輸出必須是單一 JSON 物件，不要加任何說明文字。"
)

PROMPT_TMPL = """以下是 MIKO Universal Governance Architecture 候選規格（v{ver}）。請執行嚴格稽核，找出真實存在的問題，不要為了湊數而回報。

必查項目：
1. 架構邏輯衝突（層級、依賴方向、狀態機、責任歸屬互相矛盾）。
2. A（UCP）與 Universal Artifact Contract（UAC）責任是否重疊。
3. A（UCP）與 Universal Skill Contract（USC）責任是否重疊。
4. 十六章是否缺少必要欄位（逐章檢查，列出缺哪個欄位）。
5. 路由、版本、熱插拔、權限、失敗處理、回復是否有邊界缺口。
6. 是否存在自我驗收冒充獨立驗收的問題。
7. 是否有無限重試、循環依賴、無法結束的流程。
8. 是否把文件完整性誤寫成 Runtime 已支援（例如熱插拔、GitHub、Claude Code、Manus）。

輸出 JSON schema：
{{"summary": "整體判定（繁體中文，<=120字）",
  "findings": [
    {{"id": "F-01",
      "category": "ARCH_CONFLICT|A_UAC_OVERLAP|A_USC_OVERLAP|UAC_MISSING_FIELD|BOUNDARY_GAP|SELF_VS_INDEPENDENT|LOOP_RISK|RUNTIME_CLAIM|OTHER",
      "severity": "P0|P1|P2",
      "location": "檔案:章節",
      "problem": "問題（繁體中文）",
      "evidence": "候選文件中的依據（引用文字或欄位）",
      "required_fix": "必須如何修正（可執行）",
      "ac_impact": "影響哪條 AC 或哪個檢查器"}}],
  "uac_missing": [{{"chapter": 1, "missing_fields": ["..."]}}],
  "must_fix_before_delivery": ["F-01", "F-02"],
  "verdict": "PASS|PASS_WITH_FIXES|FAIL"}}

候選文件內容如下：
"""


def main() -> int:
    cand = Path(sys.argv[1])
    label = sys.argv[2]
    model = sys.argv[3]
    ver = json.loads((Path("review/state.json").read_text()))["version"] if Path("review/state.json").exists() else "0.1.0"
    body = []
    for name in FILES:
        p = cand / name
        body.append(f"\n\n===== FILE: {name} =====\n" + p.read_text())
    prompt = PROMPT_TMPL.format(ver=ver) + "".join(body)

    import time
    client = anthropic.Anthropic(max_retries=4)
    msg = None
    last = None
    for attempt in range(1, 4):
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=16000,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # transient network/5xx
            last = e
            print(f"attempt {attempt} failed: {type(e).__name__}")
            time.sleep(5 * attempt)
    if msg is None:
        raise SystemExit(f"review failed after 3 attempts: {last}")
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text[text.find("{"):]
    data = json.loads(text)
    data["_meta"] = {
        "model": model,
        "round": label,
        "usage": {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens},
        "stop_reason": msg.stop_reason,
    }
    out = Path("review") / f"{label}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"verdict={data.get('verdict')} findings={len(data.get('findings', []))} -> {out}")
    for f in data.get("findings", []):
        print(f"{f['id']} {f['severity']} {f['category']} {f['location']}: {f['problem'][:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
