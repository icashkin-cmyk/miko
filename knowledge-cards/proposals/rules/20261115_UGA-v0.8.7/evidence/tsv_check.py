#!/usr/bin/env python3
"""TSV background checkers for MIKO UGA candidate.

Usage: tsv_check.py <candidate_dir> <out_json>
Exit code 0 only if every checker is PASS.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ALIASES = {
    "sha256": ["sha256", "sha-256"],
    "UCP 步驟 ID": ["ucp 步驟 id", "ucp"],
}

VAGUE = ["完整", "正確", "良好", "盡量", "大概", "適當"]


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def front_matter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def parse_ucp_steps(text: str):
    steps = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^### (A\d{2})\s", line)
        if m:
            cur = m.group(1)
            steps[cur] = {}
            continue
        if line.startswith("### ") or line.startswith("## "):
            if not re.match(r"^### (A\d{2})\s", line):
                cur = None
        if cur:
            fm = re.match(r"^- \*\*(.+?)\*\*：(.+)$", line)
            if fm:
                steps[cur][fm.group(1).strip()] = fm.group(2).strip()
    return steps


def parse_uac_chapters(text: str):
    chapters = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^## (\d{1,2})\. ", line)
        if m:
            cur = int(m.group(1))
            chapters[cur] = []
            continue
        if line.startswith("## ") and not m:
            cur = None
        if cur is not None:
            chapters[cur].append(line)
    return {k: "\n".join(v) for k, v in chapters.items()}


def parse_matrix(text: str):
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8 or cells[0] in ("責任", "---") or set(cells[0]) <= {"-"}:
            continue
        rows.append(cells)
    return rows


def field_present(chapter_text: str, field: str) -> bool:
    low = chapter_text.lower()
    names = ALIASES.get(field, [field])
    return any(n.lower() in low for n in names)


def result(cid, status, items, summary):
    return {"checker": cid, "status": status, "items": items, "summary": summary}


def check_fmt(d):
    issues = []
    for f in sorted(d.glob("*.md")):
        t = read(f)
        fm = front_matter(t)
        if not fm:
            issues.append(f"{f.name}: front matter 缺失或無法解析")
        dt = str(fm.get("date", ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt):
            issues.append(f"{f.name}: date 格式不符 YYYY-MM-DD ({dt})")
        if "\t" in t:
            issues.append(f"{f.name}: 含 tab 字元")
        for i, line in enumerate(t.splitlines(), 1):
            m = re.match(r"^(#{1,6}) ", line)
            if m and len(m.group(1)) > 4:
                issues.append(f"{f.name}:{i}: 標題層級超過 ####")
        for i, line in enumerate(t.splitlines(), 1):
            if "Acceptance Criteria" in line:
                for w in VAGUE:
                    if w in line:
                        issues.append(f"{f.name}:{i}: AC 含無判準詞「{w}」")
    return result("TSV-FMT", "PASS" if not issues else "FAIL", issues, f"檢查 {len(list(d.glob('*.md')))} 份文件")


def check_struct(d, contract):
    issues = []
    ucp = read(d / "ucp-spec.md")
    steps = parse_ucp_steps(ucp)
    want_steps = contract["ucp"]["steps"]
    want_fields = contract["ucp"]["required_fields"]
    for s in want_steps:
        if s not in steps:
            issues.append(f"ucp-spec: 缺少步驟 {s}")
            continue
        for fld in want_fields:
            if fld not in steps[s]:
                issues.append(f"ucp-spec: {s} 缺少欄位「{fld}」")
            elif not steps[s][fld]:
                issues.append(f"ucp-spec: {s} 欄位「{fld}」為空")
    uac = read(d / "uac-spec.md")
    chs = parse_uac_chapters(uac)
    for n in range(1, 17):
        if n not in chs:
            issues.append(f"uac-spec: 缺少第 {n} 章")
    usc = read(d / "usc-spec.md")
    for c in contract["usc"]["contracts"]:
        if f"USC-{c}" not in usc:
            issues.append(f"usc-spec: 缺少契約 {c}")
    for s in contract["usc"]["sections"]:
        if not re.search(rf"\|\s*{s}\s*\|", usc):
            issues.append(f"usc-spec: 缺少四節 {s}")
    for col in contract["usc"]["step_columns"]:
        if f"| {col} |" not in usc:
            issues.append(f"usc-spec: 七欄缺「{col}」")
    return result("TSV-STRUCT", "PASS" if not issues else "FAIL", issues,
                  f"步驟 {len(steps)}/{len(want_steps)}、章節 {len([n for n in range(1,17) if n in chs])}/16")


def check_contract(d, contract):
    issues = []
    uac = read(d / "uac-spec.md")
    chs = parse_uac_chapters(uac)
    for ch in contract["uac"]["chapters"]:
        n = ch["chapter"]
        if n not in chs:
            issues.append(f"第 {n} 章缺失")
            continue
        body = chs[n]
        missing = [f for f in ch["required"] if not field_present(body, f)]
        if missing:
            issues.append(f"第 {n} 章 {ch['title']} 缺欄位: {', '.join(missing)}")
    return result("TSV-CONTRACT", "PASS" if not issues else "FAIL", issues, "十六章必要欄位逐一比對")


def check_skill(d, contract):
    issues = []
    usc = read(d / "usc-spec.md")
    ids = re.findall(r"USC-(C\d)\b", usc)
    if len(set(ids)) != 9:
        issues.append(f"USC 契約數 {len(set(ids))} != 9")
    for n in range(1, 10):
        if not re.search(rf"USC-C{n}\b", usc):
            issues.append(f"USC 契約 USC-C{n} 不存在（需精確 ID）")
    for s in contract["usc"]["sections"]:
        if not re.search(rf"\| {s} \|", usc):
            issues.append(f"四節缺 {s}")
    for col in contract["usc"]["step_columns"]:
        if f"| {col} |" not in usc:
            issues.append(f"七欄缺 {col}")
    if "expected" not in usc or "forbidden" not in usc:
        issues.append("缺少 expected／forbidden 規則")
    return result("TSV-SKILL", "PASS" if not issues else "FAIL", issues, "九契約／四節／七欄")


def check_overlap(d, contract):
    issues = []
    rows = parse_matrix(read(d / "matrix.md"))
    for cells in rows:
        owns = [i for i, c in enumerate(cells[1:], 1) if c == "擁有"]
        if len(owns) != 1:
            issues.append(f"責任「{cells[0]}」擁有者數 {len(owns)} != 1")
    names = [c[0] for c in rows]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        issues.append(f"責任列重複: {dup}")
    resp = contract["responsibility"]["rows"]
    owners = {}
    for r in resp:
        owners.setdefault(r["owner"], []).append(r["name"])
    return result("TSV-OVERLAP", "PASS" if not issues else "FAIL", issues,
                  f"矩陣 {len(rows)} 列，契約責任 {len(resp)} 項")


def check_route(d, contract):
    issues = []
    routes = contract["routes"]
    ids = [r["route_id"] for r in routes]
    if len(ids) != len(set(ids)):
        issues.append("route_id 重複")
    artifacts = {r["artifact"] for r in routes}
    need = {"skill", "skill-spec", "architecture", "process-design", "governance-rule", "router-doc", "test-spec", "integration-upgrade"}
    miss = need - artifacts
    if miss:
        issues.append(f"缺少路由: {miss}")
    valid_contracts = {"UAC", "USC"}
    for r in routes:
        if r["contract"] not in valid_contracts:
            issues.append(f"{r['route_id']} 契約 {r['contract']} 不存在")
        if not r.get("checker"):
            issues.append(f"{r['route_id']} 無驗收器")
    mods = read(d / "modules-spec.md")
    for r in routes:
        if r["route_id"] not in mods:
            issues.append(f"modules-spec 未列出 {r['route_id']}")
    return result("TSV-ROUTE", "PASS" if not issues else "FAIL", issues, f"路由 {len(routes)} 條")


def _cycle(nodes, edges):
    g = {n: [] for n in nodes}
    for e in edges:
        g.setdefault(e["from"], []).append(e["to"])
    color = {}

    def dfs(u, stack):
        color[u] = 1
        for v in g.get(u, []):
            if color.get(v) == 1:
                return stack + [u, v]
            if color.get(v, 0) == 0:
                r = dfs(v, stack + [u])
                if r:
                    return r
        color[u] = 2
        return None

    for n in nodes:
        if color.get(n, 0) == 0:
            c = dfs(n, [])
            if c:
                return c
    return None


def check_dag(d):
    issues = []
    data = yaml.safe_load(read(d / "deps.yaml"))
    nodes = [n["id"] for n in data["nodes"]]
    layer = {n["id"]: n["layer"] for n in data["nodes"]}
    edges = data["edges"]
    c = _cycle(nodes, edges)
    if c:
        issues.append(f"依賴循環: {' -> '.join(c)}")
    for kind in ("build-time", "run-time"):
        sub = [e for e in edges if e["kind"] == kind]
        c = _cycle(nodes, sub)
        if c:
            issues.append(f"{kind} 圖循環: {' -> '.join(c)}")
    for e in edges:
        if e["from"] not in nodes or e["to"] not in nodes:
            issues.append(f"邊指向未定義節點: {e}")
        elif e["from"] == e["to"]:
            issues.append(f"自我依賴: {e}")
    return result("TSV-DAG", "PASS" if not issues else "FAIL", issues,
                  f"節點 {len(nodes)}、邊 {len(edges)}（build {sum(1 for e in edges if e['kind']=='build-time')}）")


def check_exit(d, contract):
    issues = []
    ucp = read(d / "ucp-spec.md")
    steps = parse_ucp_steps(ucp)
    for s, fields in steps.items():
        for fld in ("Failure Handling", "Recovery", "閉環條件"):
            if not fields.get(fld):
                issues.append(f"{s} 缺 {fld}")
    for bad in ("無上限重試", "無限重試", "永不停止"):
        if bad in ucp and "不得" not in ucp.split(bad)[0][-20:]:
            issues.append(f"出現無界語句: {bad}")
    budget = contract["ucp"]["budget"]
    for k, v in budget.items():
        if not isinstance(v, int) or v <= 0:
            issues.append(f"預算 {k} 非有限正整數: {v}")
    if not re.search(r"retest_round`?\s*≤\s*3", ucp):
        issues.append("缺少 retest_round ≤ 3 明示")
    m = re.search(r"\|\s*`retest_round`\s*\|[^|]*\|\s*(\d+)\s*\|", ucp)
    if not m:
        issues.append("預算表缺 retest_round 數值")
    elif int(m.group(1)) > budget["retest_round_max"]:
        issues.append(f"預算表 retest_round={m.group(1)} 超過契約上限 {budget['retest_round_max']}")
    m = re.search(r"\|\s*`audit_round`\s*\|[^|]*\|\s*(\d+)\s*\|", ucp)
    if not m:
        issues.append("預算表缺 audit_round 數值")
    elif int(m.group(1)) > budget["audit_round_max"]:
        issues.append(f"預算表 audit_round={m.group(1)} 超過契約上限 {budget['audit_round_max']}")
    if "audit_round" not in ucp or "上限 2" not in ucp:
        issues.append("缺少 audit_round 上限 2 明示")
    if "終止性" not in ucp:
        issues.append("缺少終止性說明")
    targets = set(re.findall(r"回 A\d{2}", ucp))
    for t in targets:
        if t.split(" ")[1] not in steps:
            issues.append(f"Recovery 指向不存在步驟: {t}")
    return result("TSV-EXIT", "PASS" if not issues else "FAIL", issues,
                  f"檢查 {len(steps)} 步失敗出口")


def check_reg(d):
    issues = []
    for f in sorted(d.glob("*.md")):
        fm = front_matter(read(f))
        for k in ("version", "date", "status"):
            if k not in fm:
                issues.append(f"{f.name} front matter 缺 {k}")
    mods = read(d / "modules-spec.md")
    for i in range(1, 6):
        if f"RT-0{i}" not in mods:
            issues.append(f"LCV 缺退役規則 RT-0{i}")
    for i in range(0, 6):
        if f"H-0{i}" not in mods:
            issues.append(f"LCV 缺熱插拔規則 H-0{i}")
    for st in ("PROPOSED", "ADOPTED", "EFFECTIVE", "DEPRECATED", "RETIRED"):
        if st not in mods:
            issues.append(f"LCV 缺狀態 {st}")
    st = read(d / "structure.md")
    for rule in ("N-05", "N-06", "N-07", "MANIFEST.sha256"):
        if rule not in st:
            issues.append(f"structure 缺命名／維護規則 {rule}")
    return result("TSV-REG", "PASS" if not issues else "FAIL", issues, "版本／退役／命名規則")


def check_runtime(d):
    issues = []
    st = read(d / "structure.md")
    if "PLACEHOLDER" not in st or "UNKNOWN" not in st:
        issues.append("adapters 未標示 PLACEHOLDER／UNKNOWN")
    ucp = read(d / "ucp-spec.md")
    if "EFFECTIVE（需 Runtime 證據）" not in ucp:
        issues.append("UCP 未要求 EFFECTIVE 需 Runtime 證據")
    bad_patterns = [r"已支援熱插拔", r"Claude Code 已(整合|支援)", r"Manus 已(整合|支援)", r"GitHub 已(整合|支援)"]
    for f in d.glob("*.md"):
        for i, line in enumerate(read(f).splitlines(), 1):
            for bp in bad_patterns:
                if re.search(bp, line) and not any(k in line for k in ("不得", "未", "UNKNOWN", "非")):
                    issues.append(f"{f.name}:{i}: 無證據 Runtime 宣稱「{bp}」")
    mods = read(d / "modules-spec.md")
    if "H-04" not in mods or "三項證據" not in mods:
        issues.append("LCV 缺熱插拔三項證據要求")
    return result("TSV-RUNTIME", "PASS" if not issues else "FAIL", issues, "Runtime 聲明掃描")


def run_all(d: Path):
    contract = yaml.safe_load(read(d / "contract.yaml"))
    out = [
        check_fmt(d),
        check_struct(d, contract),
        check_contract(d, contract),
        check_skill(d, contract),
        check_overlap(d, contract),
        check_route(d, contract),
        check_dag(d),
        check_exit(d, contract),
        check_reg(d),
        check_runtime(d),
    ]
    return out


def main():
    d = Path(sys.argv[1])
    out = Path(sys.argv[2])
    res = run_all(d)
    overall = "PASS" if all(r["status"] == "PASS" for r in res) else "FAIL"
    payload = {"candidate": str(d), "overall": overall, "results": res}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    for r in res:
        print(f"{r['checker']:<14} {r['status']:<5} {r['summary']}")
        for i in r["items"][:20]:
            print(f"    - {i}")
    print("OVERALL", overall)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
