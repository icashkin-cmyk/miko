"""驗收測試：每條規則至少一正一反。執行：python3 -m unittest discover -s tests -v"""
import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import food_pool as fp  # noqa: E402
import itinerary_check as ic  # noqa: E402

BASE = json.loads((ROOT / "examples" / "範例_一日遊.json").read_text(encoding="utf-8"))


def run(mutate=None):
    plan = copy.deepcopy(BASE)
    if mutate:
        mutate(plan)
    return ic.check(plan)


def statuses(res, rule_prefix):
    return [c.status for c in res.checks if c.rule.startswith(rule_prefix)]


def step(plan, sid):
    return next(s for s in plan["steps"] if s["id"] == sid)


class TravelRules(unittest.TestCase):
    def test_base_executable(self):
        self.assertEqual(run().overall, "EXECUTABLE")

    def test_T00_missing_input_unknown(self):
        r = run(lambda p: p["trip"].pop("home_deadline"))
        self.assertIn("UNKNOWN", statuses(r, "T00"))
        self.assertNotEqual(r.overall, "EXECUTABLE")

    def test_T01_car_without_license_fail(self):
        r = run(lambda p: step(p, "S1").update(mode="car"))
        self.assertIn("FAIL", statuses(r, "T01"))

    def test_T01_car_with_license_ok(self):
        def m(p):
            step(p, "S1").update(mode="car")
            p["trip"]["licensed_driver"] = True
        self.assertNotIn("FAIL", statuses(run(m), "T01"))

    def test_T01_micro_e2w_and_ebike_distinct_allowed(self):
        def m(p):
            step(p, "S1").update(mode="micro_e2w")
            step(p, "S4").update(mode="ebike")
        self.assertEqual(statuses(run(m), "T01"), [])
        self.assertNotEqual(ic.MODE_ZH["ebike"], ic.MODE_ZH["micro_e2w"])

    def test_T01_mode_not_allowed(self):
        def m(p):
            p["trip"]["modes_allowed"] = ["walk", "transit"]
            step(p, "S1").update(mode="ebike")
        self.assertIn("FAIL", statuses(run(m), "T01"))

    def test_T02_no_return_fail(self):
        r = run(lambda p: step(p, "S4").pop("is_return"))
        self.assertIn("FAIL", statuses(r, "T02"))
        self.assertEqual(r.overall, "NOT_EXECUTABLE")

    def test_T02_return_unverified_unknown(self):
        r = run(lambda p: step(p, "S4").update(date_specific_verified=False))
        self.assertIn("UNKNOWN", statuses(r, "T02"))
        self.assertEqual(r.overall, "INCOMPLETE_UNVERIFIED")

    def test_T03_home_deadline(self):
        self.assertIn("FAIL", statuses(run(lambda p: p["trip"].update(home_deadline="14:00")), "T03"))
        self.assertEqual(statuses(run(), "T03"), ["PASS"])

    def test_T04_time_order(self):
        self.assertIn("FAIL", statuses(run(lambda p: step(p, "S2").update(start="08:30")), "T04"))

    def test_T05_short_transfer_risk(self):
        def m(p):
            p["steps"].insert(1, {"id": "S1b", "type": "transport", "mode": "transit", "name": "轉乘",
                                  "start": "09:10", "end": "09:15", "date_specific_verified": True,
                                  "evidence": {"source_url": "https://www.railway.gov.tw/x", "checked_at": "2026-10-19"}})
        r = run(m)
        self.assertIn("RISK", statuses(r, "T05"))
        self.assertEqual(r.overall, "EXECUTABLE_WITH_RISK")

    def test_T06_general_timetable_unknown(self):
        r = run(lambda p: step(p, "S1").pop("date_specific_verified"))
        self.assertIn("UNKNOWN", statuses(r, "T06"))

    def test_D01_cross_midnight(self):
        # 週六 23:50 開始、00:30 結束卻未標 +1 → FAIL；標 +1 → 正規化為隔日
        bad = run(lambda p: step(p, "S4").update(start="23:50", end="00:30"))
        self.assertIn("FAIL", statuses(bad, "D01"))

        def good(p):
            step(p, "S4").update(start="23:50", end="00:30 +1")
            p["trip"]["home_deadline"] = "01:00 +1"
        g = run(good)
        self.assertEqual(statuses(g, "D01"), [])
        self.assertEqual(ic.parse_time("00:30 +1"), ic.parse_time("24:30"))
        from datetime import date
        self.assertIn("10/25", ic.fmt_time(date(2026, 10, 24), ic.parse_time("00:30 +1")))

    def test_F01_entity_not_verified_fail(self):
        r = run(lambda p: step(p, "S3").update(entity_status="NOT_VERIFIED"))
        self.assertIn("FAIL", statuses(r, "F01"))

    def test_F01_order_skip_fail(self):
        def m(p):
            step(p, "S3").update(food_review=None)  # 品質未做，順路卻已做
        self.assertIn("FAIL", statuses(run(m), "F01 核實順序"))

    def test_F02_open_now_is_not_open_at_arrival(self):
        r = run(lambda p: step(p, "S3").pop("open_at_arrival"))
        self.assertIn("UNKNOWN", statuses(r, "F02"))
        self.assertIn("FAIL", statuses(run(lambda p: step(p, "S3").update(open_at_arrival=False)), "F02"))

    def test_F03_arrival_ok_but_cannot_finish(self):
        # 19:00 到店、19:15 硬出發 型態
        def m(p):
            step(p, "S3").update(start="12:00", end="12:15", wait_min=10, dine_min=30)
        self.assertIn("FAIL", statuses(run(m), "F03 節點完成可行"))

    def test_F03_last_order(self):
        self.assertIn("FAIL", statuses(run(lambda p: step(p, "S3").update(last_order="12:10")), "F03 最後點餐"))

    def test_F04_name_only_risk(self):
        self.assertIn("RISK", statuses(run(lambda p: step(p, "S3").pop("signature")), "F04"))

    def test_X01_excluded_keyword(self):
        self.assertIn("FAIL", statuses(run(lambda p: step(p, "S2").update(name="範例夜市")), "X01"))

    def test_markdown_and_csv_written(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "p.json"
            src.write_text(json.dumps(BASE, ensure_ascii=False), encoding="utf-8")
            code = ic.main([str(src), "--out", d])
            self.assertEqual(code, 0)
            md = (Path(d) / "p_行程表.md").read_text(encoding="utf-8")
            self.assertIn("順向流程表", md)
            self.assertIn("UNKNOWN ≠ PASS", md)
            with (Path(d) / "p_檢查.csv").open(encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(rows)


def load_pool():
    with (ROOT / "examples" / "範例_候選池.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


class FoodRules(unittest.TestCase):
    def test_radius_is_hard(self):
        res = fp.rank(load_pool(), 3, 3)
        names = [r["name"] for r in res["小吃"]["ranked"]]
        self.assertNotIn("範例遠店", names)  # 分數最高但超出半徑
        self.assertIn("範例遠店", [r["name"] for r in res["小吃"]["excluded"]])

    def test_unverified_entity_not_ranked(self):
        res = fp.rank(load_pool(), 3, 3)
        self.assertEqual(res["飲品"]["ranked"], [])
        self.assertEqual(res["飲品"]["pending"][0]["name"], "範例茶行")

    def test_closed_excluded(self):
        res = fp.rank(load_pool(), 3, 3)
        self.assertEqual(res["正餐"]["ranked"], [])
        self.assertEqual(res["正餐"]["excluded"][0]["name"], "範例休店")

    def test_no_padding(self):
        res = fp.rank(load_pool(), 3, 3)
        self.assertEqual(len(res["小吃"]["ranked"]), 1)  # 只有 1 家合格就只列 1 家

    def test_categories_separate(self):
        res = fp.rank(load_pool(), 3, 3)
        self.assertEqual([r["name"] for r in res["甜點"]["ranked"]], ["範例冰室"])

    def test_open_now_not_target(self):
        rows = load_pool()
        rows[0]["open_at_target"] = ""
        self.assertEqual(fp.classify(rows[0], 3)[0], "PENDING")

    def test_stale_review_not_qualified(self):
        rows = load_pool()
        rows[0]["review_window"] = ">180"
        self.assertEqual(fp.classify(rows[0], 3)[0], "PENDING")

    def test_unknown_road_distance_pending(self):
        rows = load_pool()
        rows[0]["road_km"] = ""
        self.assertEqual(fp.classify(rows[0], 3)[0], "PENDING")

    def test_bad_category_excluded(self):
        rows = load_pool()
        rows[0]["category"] = "宵夜"
        self.assertEqual(fp.classify(rows[0], 3)[0], "EXCLUDED")

    def test_duplicate_store(self):
        rows = load_pool()
        rows.append(dict(rows[0]))
        res = fp.rank(rows, 3, 3)
        self.assertEqual(len(res["小吃"]["ranked"]), 1)
        self.assertTrue(any("重複" in r["_reason"] for r in res["小吃"]["excluded"]))

    def test_ranking_order(self):
        rows = load_pool()
        extra = dict(rows[0], name="範例麵店二", quality_score="90")
        res = fp.rank(rows + [extra], 3, 3)
        self.assertEqual([r["name"] for r in res["小吃"]["ranked"]], ["範例麵店二", "範例麵店"])
        res1 = fp.rank(rows + [extra], 3, 1)
        self.assertEqual(len(res1["小吃"]["ranked"]), 1)

    def test_cli_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            fp.main([str(ROOT / "examples" / "範例_候選池.csv"), "--radius-km", "3", "--out", d])
            md = next(Path(d).glob("*_候選.md")).read_text(encoding="utf-8")
            self.assertIn("目前核實到的候選", md)
            self.assertIn("不宣稱客觀前幾名", md)



EV = {"source_url": "https://www.thsrc.com.tw/示範", "checked_at": "2026-10-19"}


def taichung_case():
    """偵錯報告案例的結構：甲地→高鐵甲站→高鐵台中→台中市區→原路回甲地（時刻為合成值，非真實班次）。"""
    def tr(i, frm, to, st, en, mode="transit", ret=False, acc=10):
        return {"id": i, "type": "transport", "mode": mode, "from": frm, "to": to, "start": st, "end": en,
                "date_specific_verified": mode == "transit", "evidence": EV if mode == "transit" else None,
                "access_min": acc, "is_return": ret}
    return {"trip": {"date": "2026-10-27", "origin": "甲地", "home": "甲地", "home_deadline": "22:00"},
            "steps": [tr("A1", "甲地", "高鐵甲站", "07:00", "07:30", mode="ebike", acc=0),
                      tr("A2", "高鐵甲站", "高鐵台中站", "08:00", "08:45", acc=15),
                      tr("A3", "高鐵台中站", "台中市區", "09:15", "09:55", acc=15),
                      {"id": "P1", "type": "spot", "name": "市區景點", "start": "10:00", "end": "16:00"},
                      tr("B1", "台中市區", "高鐵台中站", "16:30", "17:10", acc=15),
                      tr("B2", "高鐵台中站", "高鐵甲站", "17:40", "18:25", acc=15, ret=True),
                      tr("B3", "高鐵甲站", "甲地", "18:50", "19:20", mode="ebike", ret=True, acc=10)]}


class RepairP0P1(unittest.TestCase):
    def test_taichung_full_loop_executable(self):
        self.assertEqual(ic.check(taichung_case()).overall, "EXECUTABLE")

    def test_P0_return_stops_at_hsr_station_fail(self):
        p = taichung_case(); p["steps"].pop()  # 最後只回到高鐵甲站
        r = ic.check(p)
        self.assertIn("FAIL", statuses(r, "T02"))
        self.assertEqual(r.overall, "NOT_EXECUTABLE")

    def test_P0_last_leg_without_destination_unknown(self):
        p = taichung_case(); p["steps"][-1].pop("to")
        self.assertIn("UNKNOWN", statuses(ic.check(p), "T02"))

    def test_P0_verified_flag_without_evidence_not_pass(self):
        p = taichung_case(); p["steps"][1]["evidence"] = None
        r = ic.check(p)
        self.assertIn("UNKNOWN", statuses(r, "T06"))
        self.assertNotEqual(r.overall, "EXECUTABLE")

    def test_P0_non_official_source_not_pass(self):
        p = taichung_case(); p["steps"][1]["evidence"] = {"source_url": "https://blog.example.com/x", "checked_at": "2026-10-19"}
        self.assertIn("UNKNOWN", statuses(ic.check(p), "T06"))

    def test_P0_lookalike_domain_rejected(self):
        p = taichung_case(); p["steps"][1]["evidence"] = {"source_url": "https://thsrc.com.tw.evil.io/x", "checked_at": "2026-10-19"}
        self.assertIn("UNKNOWN", statuses(ic.check(p), "T06"))

    def test_P1_access_time_spot_to_transit(self):
        p = taichung_case(); p["steps"][4]["start"] = "16:05"; p["steps"][4]["end"] = "16:45"  # 景點 16:00 結束，需 15 分進站
        self.assertIn("RISK", statuses(ic.check(p), "T05"))

    def test_P1_access_default_applied(self):
        p = taichung_case(); p["steps"][2].pop("access_min"); p["steps"][2]["start"] = "08:50"; p["steps"][2]["end"] = "09:30"
        r = ic.check(p)  # 08:35 到站，08:50 上車：15 分 < 預設 10 + 轉乘 15
        self.assertTrue(any("採預設" in c.detail for c in r.checks if c.rule.startswith("T05")))


class RepairFood(unittest.TestCase):
    def row(self, **kw):
        r = load_pool()[0]; r.update(kw); return r

    def test_negative_distance(self):
        self.assertEqual(fp.classify(self.row(road_km="-1"), 3)[0], "EXCLUDED")

    def test_nan_distance(self):
        self.assertEqual(fp.classify(self.row(road_km="nan"), 3)[0], "EXCLUDED")

    def test_nan_score(self):
        self.assertEqual(fp.classify(self.row(quality_score="nan"), 3)[0], "EXCLUDED")

    def test_score_out_of_range(self):
        self.assertEqual(fp.classify(self.row(quality_score="150"), 3)[0], "EXCLUDED")
        self.assertEqual(fp.classify(self.row(quality_score="inf"), 3)[0], "EXCLUDED")

if __name__ == "__main__":
    unittest.main()
