#!/usr/bin/env python3
"""Fix-verification round: confirm each round-2 finding is resolved in v0.2.1."""
import json
import sys
import time
from pathlib import Path

import anthropic

FILES = ["ucp-spec.md", "uac-spec.md", "usc-spec.md", "modules-spec.md", "structure.md", "matrix.md", "deps.yaml", "contract.yaml"]
findings = json.loads(Path("review/round2.json").read_text())["findings"]
flist = "\n".join(
    f"- {f['id']} [{f['severity']}] {f['location']}: {f['problem']} / 修正要求: {f['required_fix']}" for f in findings
)
cand = Path(sys.argv[1])
model = sys.argv[2]
body = "".join(f"\n\n===== FILE: {n} =====\n" + (cand / n).read_text() for n in FILES)
prompt = f"""上一輪審查提出以下問題，製作者已提交修正版。請逐項驗證修正是否落實，並檢查修正是否造成新問題（回歸）。只依文件內容判定，不得假設未提供的內容存在。

待驗證問題：
{flist}

輸出單一 JSON：
{{"summary":"整體判定（繁中 <=100字）",
  "verification":[{{"id":"F-01","status":"FIXED|PARTIAL|NOT_FIXED","evidence":"文件中對應文字","note":"剩餘問題或 NONE"}}],
  "new_findings":[{{"id":"N-01","severity":"P0|P1|P2","location":"檔案:章節","problem":"...","required_fix":"..."}}],
  "verdict":"PASS|PASS_WITH_FIXES|FAIL"}}

文件內容：{body}"""
client = anthropic.Anthropic(max_retries=4)
msg = None
for attempt in range(1, 4):
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=8000,
            system="你是 MIKO 專案的獨立架構稽核者。只輸出 JSON。",
            messages=[{"role": "user", "content": prompt}],
        )
        break
    except Exception as e:
        print("attempt", attempt, type(e).__name__, flush=True)
        time.sleep(5 * attempt)
if msg is None:
    raise SystemExit("failed")
text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
if text.startswith("```"):
    text = text.split("```")[1]
    text = text[text.find("{"):]
data = json.loads(text)
data["_meta"] = {"model": model, "usage": {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens}}
Path("review/round3_verify.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
print("verdict", data["verdict"])
for v in data["verification"]:
    print(v["id"], v["status"], v["note"][:70])
for n in data.get("new_findings", []):
    print("NEW", n["id"], n["severity"], n["problem"][:90])
