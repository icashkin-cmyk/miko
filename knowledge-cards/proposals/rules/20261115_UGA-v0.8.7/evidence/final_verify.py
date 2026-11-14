import json, sys, time
from pathlib import Path
import anthropic
cand = Path(sys.argv[1]); model = sys.argv[2]
items = [
 ("F-07/N-02","R-04 命中兩條路由時必須判 CONFLICT 交 R-CONV，且裁決理由必須有固定記錄位置（route_decision_reason、decided_by）"),
 ("N-01","contract.yaml 第 1 章 required 必須與 uac-spec.md 第 1 章必要欄位完全一致（含 目的、範圍（含）、非範圍（不含）、適用對象）"),
]
files = ["modules-spec.md","uac-spec.md","contract.yaml"]
body = "".join(f"\n\n===== FILE: {n} =====\n" + (cand/n).read_text() for n in files)
flist = "\n".join(f"- {i}: {d}" for i,d in items)
prompt = f"""請驗證以下兩項修正是否已落實。只依文件內容判定。

待驗證項目：
{flist}

輸出單一 JSON：
{{"summary":"繁中 <=80字","verification":[{{"id":"...","status":"FIXED|PARTIAL|NOT_FIXED","evidence":"引用文字","note":"剩餘問題或 NONE"}}],"new_findings":[{{"id":"N-xx","severity":"P0|P1|P2","problem":"..."}}],"verdict":"PASS|PASS_WITH_FIXES|FAIL"}}

文件內容：{body}"""
client = anthropic.Anthropic(max_retries=4)
msg=None
for a in range(1,4):
    try:
        msg = client.messages.create(model=model, max_tokens=4000, system="你是 MIKO 獨立稽核者，只輸出 JSON。", messages=[{"role":"user","content":prompt}])
        break
    except Exception as e:
        print("attempt",a,type(e).__name__,flush=True); time.sleep(5*a)
text = "".join(b.text for b in msg.content if getattr(b,"type","")=="text").strip()
if text.startswith("```"):
    text = text.split("```")[1]; text = text[text.find("{"):]
data=json.loads(text); data["_meta"]={"model":model,"usage":{"input":msg.usage.input_tokens,"output":msg.usage.output_tokens}}
Path("review/round4_final.json").write_text(json.dumps(data,ensure_ascii=False,indent=2))
print("verdict",data["verdict"])
for v in data["verification"]: print(v["id"],v["status"],v["note"][:60])
for n in data.get("new_findings",[]): print("NEW",n["id"],n["severity"],n["problem"][:80])
