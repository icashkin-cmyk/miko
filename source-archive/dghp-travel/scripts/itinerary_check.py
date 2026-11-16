#!/usr/bin/env python3
"""DGHP 旅遊行程檢核器 v0.1.0-CANDIDATE

依據：DGHP_TRAVEL_RULES.md（2026-10-19 / 0.1.0-CANDIDATE，6567 bytes）§2–§7。
用途：把一份行程 JSON 做硬檢查，輸出「順向流程表」Markdown 與檢查結果 CSV。
限制：本程式只檢查使用者／查詢者已填入的欄位，不連網、不替你查班次或營業時間；
      欄位沒填就是 UNKNOWN，UNKNOWN ≠ PASS。
用法：python3 itinerary_check.py 行程.json [--out 輸出資料夾]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

VERSION = "0.1.1-CANDIDATE"
RULE_SOURCE = "DGHP_TRAVEL_RULES.md 0.1.0-CANDIDATE (2026-10-19)"

PASS, RISK, UNKNOWN, FAIL = "PASS", "RISK", "UNKNOWN", "FAIL"
DEFAULT_MODES = ["walk", "transit", "ebike", "micro_e2w"]  # 步行、大眾運輸、電輔車、微型電動二輪
DRIVER_MODES = {"car", "scooter"}  # 汽車、機車：僅明確合法駕駛者可用（§3）
MODE_ZH = {"walk": "步行", "transit": "大眾運輸", "ebike": "電輔車", "micro_e2w": "微型電動二輪",
           "car": "汽車", "scooter": "機車", "taxi": "計程車"}
OFFICIAL_DOMAINS = ("railway.gov.tw", "thsrc.com.tw", "gov.tw", "ntbus.com.tw", "taiwantrip.com.tw")
DEFAULT_ACCESS_MIN = 10  # 進站／步行／購票／候車的預設下限（候選參數）
FOOD_ORDER = ["entity_status", "food_review", "route_fit"]  # §4 必守順序（最後一步是排入行程）
WEEKDAY_ZH = "一二三四五六日"

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?:\s*\+(\d))?$")


def parse_time(s: str) -> int:
    """'HH:MM'、'HH:MM +1'（隔日）、'24:30'（=隔日 00:30）→ 由行程日 00:00 起算的分鐘數。"""
    m = _TIME_RE.match(str(s).strip())
    if not m:
        raise ValueError(f"時間格式錯誤：{s!r}（應為 HH:MM 或 HH:MM +1）")
    h, mi, plus = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if mi > 59 or h > 47:
        raise ValueError(f"時間超出範圍：{s!r}")
    return (h + 24 * plus) * 60 + mi


def fmt_time(trip_date: date, minutes: int) -> str:
    d = trip_date + timedelta(days=minutes // 1440)
    hm = minutes % 1440
    tag = "" if d == trip_date else f"（{d.month}/{d.day} 週{WEEKDAY_ZH[d.weekday()]}）"
    return f"{hm // 60:02d}:{hm % 60:02d}{tag}"


def evidence_status(s: dict, official=OFFICIAL_DOMAINS) -> tuple[str, str]:
    """班次證據：date_specific_verified=True 還必須附官方來源網址與查核日期，否則不算 PASS。"""
    if s.get("date_specific_verified") is not True:
        return UNKNOWN, "未核官方指定日期班次（一般班表不代表當日開行）"
    ev = s.get("evidence") or {}
    url, when = str(ev.get("source_url", "")).strip(), str(ev.get("checked_at", "")).strip()
    if not url.startswith("https://") or not when:
        return UNKNOWN, "宣稱已核，但缺官方來源網址或查核日期（evidence.source_url／checked_at）"
    host = url.split("/")[2].split(":")[0].lower()
    if not any(host == d or host.endswith("." + d) for d in official):
        return UNKNOWN, f"來源 {host} 不在官方網域清單內"
    return PASS, f"已核指定日期班次（{host}，{when}）"


@dataclass
class Check:
    rule: str
    step: str
    status: str
    detail: str


@dataclass
class Result:
    checks: list[Check] = field(default_factory=list)

    def add(self, rule, step, status, detail):
        self.checks.append(Check(rule, step, status, detail))

    @property
    def overall(self) -> str:
        st = {c.status for c in self.checks}
        if FAIL in st:
            return "NOT_EXECUTABLE"
        if UNKNOWN in st:
            return "INCOMPLETE_UNVERIFIED"
        if RISK in st:
            return "EXECUTABLE_WITH_RISK"
        return "EXECUTABLE"


def check(plan: dict) -> Result:
    r = Result()
    trip = plan.get("trip", {})
    steps = plan.get("steps", [])
    allowed = set(trip.get("modes_allowed") or DEFAULT_MODES)
    licensed = trip.get("licensed_driver") is True
    buffer_min = int(trip.get("min_transfer_buffer_min", 15))
    default_access = int(trip.get("default_access_min", DEFAULT_ACCESS_MIN))
    official = tuple(trip.get("official_domains") or OFFICIAL_DOMAINS)
    home = (trip.get("home") or trip.get("origin") or "").strip()
    excluded = [k for k in trip.get("exclude_keywords", []) if k]

    # §3 必要輸入
    for key in ("date", "origin", "home_deadline"):
        if not trip.get(key):
            r.add("T00 必要輸入", "trip", UNKNOWN, f"缺 {key}")
    if not steps:
        r.add("T00 必要輸入", "trip", FAIL, "沒有任何行程步驟")
        return r

    # 時間解析與 §5 跨日正規化（時間倒退且未標 +1 → 跨日歧義）
    prev_end, prev_id = None, None
    for s in steps:
        sid = s.get("id", "?")
        try:
            s["_start"] = parse_time(s["start"])
            s["_end"] = parse_time(s["end"])
        except (KeyError, ValueError) as e:
            r.add("D01 時間格式", sid, FAIL, str(e))
            s["_start"] = s["_end"] = None
            continue
        if s["_end"] < s["_start"]:
            r.add("D01 跨日正規化", sid, FAIL,
                  f"結束 {s['end']} 早於開始 {s['start']}；跨午夜請寫成 '00:30 +1' 或 '24:30'")
        if prev_end is not None and s["_start"] < prev_end:
            r.add("T04 時序連續", sid, FAIL,
                  f"開始時間早於前一步 {prev_id} 的結束；若為隔日請標 +1")
        prev_end, prev_id = s["_end"], sid

    # §3 交通方式
    for s in steps:
        if s.get("type") != "transport":
            continue
        sid, mode = s.get("id", "?"), s.get("mode")
        if mode in DRIVER_MODES and not licensed:
            r.add("T01 交通方式", sid, FAIL, f"{MODE_ZH.get(mode, mode)}需明確合法駕駛者；預設不可用")
        elif mode not in allowed and mode not in DRIVER_MODES:
            r.add("T01 交通方式", sid, FAIL, f"{MODE_ZH.get(mode, mode)} 不在可用交通方式內")
        # §3 一般班表 ≠ 指定日期開行
        if mode == "transit":
            st, why = evidence_status(s, official)
            r.add("T06 指定日期班次", sid, st, why)

    # §5 轉乘緩衝：上車前需留「進站／步行／購票／候車」(access_min)，交通接交通再加轉乘緩衝
    for a, b in zip(steps, steps[1:]):
        if b.get("type") != "transport" or b.get("mode") == "walk":
            continue
        if a.get("_end") is None or b.get("_start") is None:
            continue
        gap = b["_start"] - a["_end"]
        acc = b.get("access_min")
        need = int(acc if acc is not None else default_access)
        if a.get("type") == "transport":
            need += buffer_min
        if gap < need:
            src = "" if acc is not None else f"（未填 access_min，採預設 {default_access}）"
            r.add("T05 轉乘緩衝", b.get("id", "?"), RISK,
                  f"上車前只有 {gap} 分鐘，需 {need} 分鐘{src}；不得當作穩健方案")

    # §5／§7 回程優先
    returns = [s for s in steps if s.get("type") == "transport" and s.get("is_return")]
    if not returns:
        r.add("T02 回程閉環", "trip", FAIL, "沒有回程交通；沒有可靠回程不貿然出發")
    else:
        last = [s for s in steps if s.get("type") == "transport"][-1]  # 實際最後一段交通
        dest = (last.get("to") or "").strip()
        if not dest:
            r.add("T02 回程閉環", last.get("id", "?"), UNKNOWN, f"最後一段交通未填抵達地（to），無法確認回到 {home or '家'}")
        elif home and dest != home:
            r.add("T02 回程閉環", last.get("id", "?"), FAIL, f"最後一段只到「{dest}」，未回到「{home}」")
        elif last.get("mode") == "transit" and evidence_status(last, official)[0] != PASS:
            r.add("T02 回程閉環", last.get("id", "?"), UNKNOWN, "回到家的最後一段班次未有官方證據")
        else:
            r.add("T02 回程閉環", last.get("id", "?"), PASS, f"最後一段抵達 {dest}")
        if trip.get("home_deadline") and last.get("_end") is not None:
            dl = parse_time(trip["home_deadline"])
            if last["_end"] > dl:
                r.add("T03 回家截止", last.get("id", "?"), FAIL,
                      f"到家 {last['end']} 晚於截止 {trip['home_deadline']}")
            else:
                r.add("T03 回家截止", last.get("id", "?"), PASS, "在截止前到家")

    # §4 餐飲節點
    for i, s in enumerate(steps):
        if s.get("type") != "food":
            continue
        sid = s.get("id", "?")
        done = [s.get(k) in ("GOOGLE_ENTITY_VERIFIED", "DONE") for k in FOOD_ORDER]
        if not done[0]:
            r.add("F01 實體核實", sid, FAIL if s.get("primary", True) else UNKNOWN,
                  "未 GOOGLE_ENTITY_VERIFIED → 標 NOT_VERIFIED，不得列正式主選")
        else:
            # 順序：後一步完成而前一步未完成 = 跳步
            for j in range(1, len(done)):
                if done[j] and not all(done[:j]):
                    r.add("F01 核實順序", sid, FAIL, f"{FOOD_ORDER[j]} 先於前置步驟完成")
            if all(done):
                r.add("F01 實體→品質→順路", sid, PASS, "三步完成")
            else:
                miss = [k for k, d in zip(FOOD_ORDER, done) if not d]
                r.add("F01 實體→品質→順路", sid, UNKNOWN, f"未完成：{', '.join(miss)}")
        oa = s.get("open_at_arrival")
        if oa is True:
            r.add("F02 抵達時營業", sid, PASS, "已核抵達時段營業")
        elif oa is False:
            r.add("F02 抵達時營業", sid, FAIL, "抵達時未營業")
        else:
            r.add("F02 抵達時營業", sid, UNKNOWN, "未核抵達時營業（OPEN_NOW ≠ OPEN_AT_TARGET_ARRIVAL）")
        # §5 ARRIVAL_FEASIBLE ≠ NODE_COMPLETION_FEASIBLE
        if s.get("_start") is not None:
            wait, dine = s.get("wait_min"), s.get("dine_min")
            if wait is None or dine is None:
                r.add("F03 節點完成可行", sid, UNKNOWN, "缺候位或用餐時長")
            else:
                need_end = s["_start"] + int(wait) + int(dine)
                hard = s["_end"]
                nxt = steps[i + 1] if i + 1 < len(steps) else None
                if nxt and nxt.get("_start") is not None:
                    hard = min(hard, nxt["_start"])
                if need_end > hard:
                    r.add("F03 節點完成可行", sid, FAIL,
                          f"到店後需 {int(wait) + int(dine)} 分鐘，超過下一硬出發；到店可行 ≠ 吃得完")
                else:
                    r.add("F03 節點完成可行", sid, PASS, "候位＋用餐在下一步前完成")
            lo = s.get("last_order")
            if lo and wait is not None:
                if s["_start"] + int(wait) > parse_time(lo):
                    r.add("F03 最後點餐", sid, FAIL, f"候位後已超過 L.O. {lo}")
            elif not lo:
                r.add("F03 最後點餐", sid, UNKNOWN, "未填 L.O.")
        miss = [k for k in ("signature", "price", "source_date") if not s.get(k)]
        if miss:
            r.add("F04 店家資訊", sid, RISK, f"缺 {', '.join(miss)}（避免只有店名）")

    # §6 使用者排除項（例：夜市）
    for s in steps:
        name = f"{s.get('name', '')}{s.get('note', '')}"
        for k in excluded:
            if k in name:
                r.add("X01 排除項", s.get("id", "?"), FAIL, f"含使用者已排除的「{k}」")
    return r


def to_markdown(plan: dict, res: Result) -> str:
    trip = plan.get("trip", {})
    try:
        d0 = date.fromisoformat(trip["date"])
    except (KeyError, ValueError):
        d0 = date(1970, 1, 1)
    worst = {}
    order = {PASS: 0, RISK: 1, UNKNOWN: 2, FAIL: 3}
    for c in res.checks:
        if order[c.status] >= order.get(worst.get(c.step, PASS), 0):
            worst[c.step] = c.status
    L = [f"# 行程：{trip.get('title', '未命名')}",
         "",
         f"日期 {trip.get('date', 'UNKNOWN')}｜起點 {trip.get('origin', 'UNKNOWN')}｜回家截止 {trip.get('home_deadline', 'UNKNOWN')}｜整體 **{res.overall}**",
         "",
         "## 順向流程表",
         "",
         "| 時間 | 項目 | 交通／類別 | 預算 | 重點 | 驗證 |",
         "|---|---|---|---|---|---|"]
    for s in plan.get("steps", []):
        t = (f"{fmt_time(d0, s['_start'])}–{fmt_time(d0, s['_end'])}"
             if s.get("_start") is not None else f"{s.get('start')}–{s.get('end')}")
        kind = MODE_ZH.get(s.get("mode"), s.get("mode")) if s.get("type") == "transport" else s.get("category") or {"spot": "景點", "food": "餐飲", "stay": "住宿"}.get(s.get("type"), s.get("type", ""))
        note = " ".join(x for x in (s.get("service"), s.get("signature"), s.get("note")) if x)
        L.append(f"| {t} | {s.get('name', s.get('id'))} | {kind or ''} | {s.get('budget', '')} | {note} | {worst.get(s.get('id'), '—')} |")
    L += ["", "## 檢查結果", "", "| 規則 | 步驟 | 狀態 | 說明 |", "|---|---|---|---|"]
    for c in res.checks:
        L.append(f"| {c.rule} | {c.step} | {c.status} | {c.detail} |")
    backups = plan.get("backups") or []
    if backups:
        L += ["", "## 備案"]
        for b in backups:
            L.append(f"- **{b.get('id')}**：觸發＝{b.get('trigger')}；改為＝{b.get('action')}；回程＝{b.get('return')}")
    L += ["", f"> 規則來源：{RULE_SOURCE}；檢核器 {VERSION}。UNKNOWN ≠ PASS；本表不代表已即時查證班次或營業。"]
    return "\n".join(L) + "\n"


def write_csv(res: Result, path: Path):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rule", "step", "status", "detail"])
        for c in res.checks:
            w.writerow([c.rule, c.step, c.status, c.detail])


def main(argv=None):
    ap = argparse.ArgumentParser(description="DGHP 旅遊行程檢核器")
    ap.add_argument("plan")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    res = check(plan)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.plan).stem
    (out / f"{stem}_行程表.md").write_text(to_markdown(plan, res), encoding="utf-8")
    write_csv(res, out / f"{stem}_檢查.csv")
    print(res.overall)
    return 0 if res.overall in ("EXECUTABLE", "EXECUTABLE_WITH_RISK") else 2


if __name__ == "__main__":
    sys.exit(main())
