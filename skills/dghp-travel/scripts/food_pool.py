#!/usr/bin/env python3
"""DGHP 美食候選池覆蓋檢核 v0.1.0-CANDIDATE

依據：DGHP_TRAVEL_RULES.md §4（實體→品質→順路）、FOOD 承接規則（先建候選池→逐店核實→最後才排名；
      正餐／小吃／甜點／飲品／伴手禮分組；半徑為硬範圍；評論分 0–30／31–90／91–180 日；合格不足不湊數）。
輸入：候選池 CSV（欄位見 CSV_FIELDS）。不連網、不爬蝦皮或 Google；欄位由查詢者填入。
用法：python3 food_pool.py 候選.csv --radius-km 3 [--top 3] [--out 輸出資料夾]
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

VERSION = "0.1.1-CANDIDATE"
CATEGORIES = ["正餐", "小吃", "甜點", "飲品", "伴手禮"]
CSV_FIELDS = ["name", "branch", "category", "road_km", "entity_status", "business_status",
              "open_at_target", "quality_score", "review_window", "signature", "price", "source_date", "search_angle"]
WINDOW_RANK = {"0-30": 0, "31-90": 1, "91-180": 2}


def _truthy(v):
    v = (v or "").strip().upper()
    return True if v in ("TRUE", "Y", "1", "是") else False if v in ("FALSE", "N", "0", "否") else None


def classify(row: dict, radius_km: float) -> tuple[str, str]:
    """回傳 (狀態, 原因)。狀態：QUALIFIED／PENDING／EXCLUDED。"""
    cat = (row.get("category") or "").strip()
    if cat not in CATEGORIES:
        return "EXCLUDED", f"餐型 {cat or '空白'} 不在五類內，不混組"
    try:
        km = float(row.get("road_km") or "")
    except ValueError:
        return "PENDING", "道路距離未知（直線距離不代道路距離）"
    if not math.isfinite(km) or km < 0:
        return "EXCLUDED", f"道路距離 {row.get('road_km')} 不是有效數值"
    if km > radius_km:
        return "EXCLUDED", f"道路距離 {km} km 超出硬半徑 {radius_km} km"
    if (row.get("entity_status") or "").strip() != "GOOGLE_ENTITY_VERIFIED":
        return "PENDING", "實體未核實（NOT_VERIFIED）"
    bs = (row.get("business_status") or "").strip().upper()
    if bs in ("CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"):
        return "EXCLUDED", f"營業狀態 {bs}"
    if bs != "OPERATIONAL":
        return "PENDING", "營業狀態未知"
    oat = _truthy(row.get("open_at_target"))
    if oat is False:
        return "EXCLUDED", "目標時段未營業"
    if oat is None:
        return "PENDING", "未核目標時段營業（OPEN_NOW ≠ OPEN_AT_TARGET_ARRIVAL）"
    if (row.get("review_window") or "").strip() not in WINDOW_RANK:
        return "PENDING", "無 180 日內評論，品質不宣稱通過"
    try:
        q = float(row.get("quality_score") or "")
    except ValueError:
        return "PENDING", "品質分數未評"
    if not math.isfinite(q) or not 0 <= q <= 100:
        return "EXCLUDED", f"品質分數 {row.get('quality_score')} 不在 0–100 有效範圍"
    return "QUALIFIED", "實體、營業、目標時段、近期評論皆已核"


def rank(rows: list[dict], radius_km: float, top: int) -> dict:
    out = {c: {"ranked": [], "pending": [], "excluded": []} for c in CATEGORIES}
    out["_other"] = {"ranked": [], "pending": [], "excluded": []}
    seen = set()
    for r in rows:
        key = ((r.get("name") or "").strip(), (r.get("branch") or "").strip())
        if key in seen:
            st, why = "EXCLUDED", "重複店家（同名同分店）"
        else:
            seen.add(key)
            st, why = classify(r, radius_km)
        r = dict(r, _status=st, _reason=why)
        bucket = out.get((r.get("category") or "").strip(), out["_other"])
        bucket["ranked" if st == "QUALIFIED" else st.lower()].append(r)
    for c in CATEGORIES:
        q = out[c]["ranked"]
        q.sort(key=lambda r: (-float(r["quality_score"]), WINDOW_RANK[r["review_window"].strip()],
                              float(r["road_km"])))
        out[c]["ranked"] = q[:top]  # 不足 top 不湊數
    return out


def to_markdown(res: dict, radius_km: float, top: int, title: str) -> str:
    L = [f"# 美食候選：{title}", "", f"硬半徑 {radius_km} km（道路距離）｜每類最多 {top} 家，合格不足不補", ""]
    for c in CATEGORIES:
        b = res[c]
        if not (b["ranked"] or b["pending"] or b["excluded"]):
            continue
        L.append(f"## {c}（目前核實到的候選 {len(b['ranked'])} 家）")
        if b["ranked"]:
            L += ["", "| 名次 | 店名 | 分店 | 招牌 | 價格 | 道路 km | 評論區間 | 來源日期 |", "|---|---|---|---|---|---|---|---|"]
            for i, r in enumerate(b["ranked"], 1):
                L.append(f"| {i} | {r['name']} | {r.get('branch', '')} | {r.get('signature', '')} | {r.get('price', '')} | "
                         f"{r['road_km']} | {r['review_window']} 日 | {r.get('source_date', '')} |")
        if b["pending"]:
            L += ["", "待核（不排名）：" + "；".join(f"{r['name']}（{r['_reason']}）" for r in b["pending"])]
        if b["excluded"]:
            L += ["", "已排除：" + "；".join(f"{r['name']}（{r['_reason']}）" for r in b["excluded"])]
        L.append("")
    if res["_other"]["excluded"]:
        L.append("其他排除：" + "；".join(f"{r.get('name')}（{r['_reason']}）" for r in res["_other"]["excluded"]))
    L += ["", f"> food_pool {VERSION}。用語為「目前核實到的候選」，不宣稱客觀前幾名或沒有漏店。"]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="DGHP 美食候選池覆蓋檢核")
    ap.add_argument("pool")
    ap.add_argument("--radius-km", type=float, required=True)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    with open(a.pool, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    res = rank(rows, a.radius_km, a.top)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.pool).stem
    (out / f"{stem}_候選.md").write_text(to_markdown(res, a.radius_km, a.top, stem), encoding="utf-8")
    with (out / f"{stem}_判定.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "name", "branch", "status", "reason"])
        for c in CATEGORIES + ["_other"]:
            for k in ("ranked", "pending", "excluded"):
                for r in res[c][k]:
                    w.writerow([c, r.get("name"), r.get("branch"), r["_status"], r["_reason"]])
    n = sum(len(res[c]["ranked"]) for c in CATEGORIES)
    print(f"QUALIFIED_RANKED={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
