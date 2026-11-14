import json,sys,time
from pathlib import Path
import anthropic
cand=Path(sys.argv[1]); model=sys.argv[2]
t=(cand/"ucp-spec.md").read_text()
seg=t[t.index("### 2.1 獨立性等級判定表"):t.index("## 3. 三層分層")]
a12=t[t.index("### A12"):t.index("### A13")]
app=t[t.index("## 附錄 A"):t.index("## 12. 未決事項")]
prompt=f"""以下是 MIKO 通用製作流程 A12 獨立驗收的修訂內容。請檢查：等級判定是否可執行且無矛盾、驗收包規格是否足以防止自我驗收冒充、是否仍有循環或無法結束、是否與「不得由製作者驗收」一致。只依內容判定，不要假設未提供者存在。

輸出 JSON：{{"summary":"繁中<=100字","findings":[{{"id":"A-01","severity":"P0|P1|P2","location":"...","problem":"...","required_fix":"..."}}],"verdict":"PASS|PASS_WITH_FIXES|FAIL"}}

[2.1 等級]\n{seg}\n\n[A12]\n{a12}\n\n[附錄A]\n{app}"""
c=anthropic.Anthropic(max_retries=4)
m=None
for a in range(1,4):
    try:
        m=c.messages.create(model=model,max_tokens=6000,system="你是 MIKO 獨立稽核者，只輸出 JSON。",messages=[{"role":"user","content":prompt}]); break
    except Exception as e:
        print("attempt",a,type(e).__name__,flush=True); time.sleep(5*a)
tx="".join(b.text for b in m.content if getattr(b,"type","")=="text").strip()
if tx.startswith("```"):
    tx=tx.split("```")[1]; tx=tx[tx.find("{"):]
d=json.loads(tx); d["_meta"]={"model":model,"usage":{"input":m.usage.input_tokens,"output":m.usage.output_tokens}}
Path("review/round5_a12.json").write_text(json.dumps(d,ensure_ascii=False,indent=2))
print("verdict",d["verdict"]); [print(f["id"],f["severity"],f["problem"][:100]) for f in d.get("findings",[])]
