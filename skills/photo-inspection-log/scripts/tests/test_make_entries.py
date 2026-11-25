"""photo-inspection-log 照片專案自己的測試：make_entries.py 不得截掉查驗說明（SKILL.md「內容不截行、不精簡」）。
重現（2026-11-22，13 張驗收照片）：白板查驗說明 15 行，entries.json 的 design 只剩前 12 行。"""
import json, os, subprocess, sys, tempfile, unittest
from openpyxl import Workbook

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MakeEntriesNoTruncate(unittest.TestCase):
    def test_design_keeps_all_lines(self):
        lines = [f"〈品名{i}〉 〈型號{i}〉｜{i}" for i in range(1, 16)]   # 15 行，超過舊上限 12
        text = "查驗時間：2026-10-27（115.10.27）\n照片日期：2026-10-27\n查驗項目：〈項目〉材料進場\n位置：\n檢查人員：\n查驗說明：\n" + "\n".join(lines)
        with tempfile.TemporaryDirectory() as d:
            wb = Workbook(); ws = wb.active; ws.title = "2026-10-27"
            ws["B2"] = text
            src = os.path.join(d, "照片紀錄.xlsx"); out = os.path.join(d, "entries.json"); wb.save(src)
            cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "make_entries.py"), src, out, os.path.join(d, "photos_out")],
                                capture_output=True, text=True)
            # 這列沒有照片，make_entries 依規定 STOP（結束碼 8），但 entries.json 已先寫出
            self.assertEqual(cp.returncode, 8, cp.stdout + cp.stderr)
            design = json.load(open(out, encoding="utf-8"))[0]["design"]
        self.assertEqual(design, lines)


def run_one(text):
    """寫一列照片紀錄（沒有照片，make_entries 依規定結束碼 8，但 entries.json 已寫出），回傳第一筆 entry。"""
    with tempfile.TemporaryDirectory() as d:
        wb = Workbook(); ws = wb.active; ws.title = "2026-10-27"
        ws["B2"] = text
        src = os.path.join(d, "照片紀錄.xlsx"); out = os.path.join(d, "entries.json"); wb.save(src)
        cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "make_entries.py"), src, out, os.path.join(d, "photos_out")],
                            capture_output=True, text=True, cwd=d)
        assert cp.returncode == 8, cp.stdout + cp.stderr
        return json.load(open(out, encoding="utf-8"))[0]


def board(item, head, lines):
    return ("查驗時間：2026-10-27（115.10.27）\n照片日期：2026-10-27\n查驗項目：" + item + "\n位置：\n檢查人員：\n"
            + "查驗說明" + (f"（{head}）" if head else "") + "：\n" + "\n".join(lines))


class MakeEntriesCompanyExample(unittest.TestCase):
    """v0.5（2026-11-22，13 張驗收稽核 AC3／AC6／AC7）：照公司範例 A 的填法（範例A對照與修改方案_20261108.md 第 2、4、6 節）。"""

    def test_form_match_uses_company_wording(self):
        # 範例 A：檢查項目＝材料/設備名稱；設計/標準值第 1 行＝材料表工作表名稱，之後是品質管理標準；相符時實測值同寫
        e = run_one(board("EMT管 材料進場", "品名 規格｜實測｜數量", ["永銳堅 E19｜E19｜10"]))
        self.assertEqual(e["item"], "EMT導線管")
        self.assertEqual(e["design"], ["EMT管", "廠牌:永銳堅", "稱呼:E19", "符合CNS2606"])
        self.assertEqual(e["measured"], e["design"])

    def test_alias_item_when_spec_not_in_form(self):
        # 規格對不到材料表：檢查項目仍用材料表名稱（EMT管→EMT導線管），設計/實測照白板兩欄拆開，不把實測併進設計
        e = run_one(board("EMT管 材料進場", "品名 規格｜實測｜數量", ["〈廠牌〉 E51｜〈實測〉m｜30"]))
        self.assertEqual(e["item"], "EMT導線管")
        self.assertEqual(e["design"], ["〈廠牌〉 E51（30）"])
        self.assertEqual(e["measured"], ["〈實測〉m（30）"])
        self.assertFalse(any("｜" in x for x in e["design"]))

    def test_label_word_not_prefixed_to_measured(self):
        # 第二輪稽核 AC3：設計欄開頭是標籤字「廠牌」時，實測值前面不得加「廠牌」（看起來像 廠牌＝實測值）
        e = run_one(board("EMT管 材料進場", "品名 規格｜實測｜數量", ["廠牌（E51）〈規格〉｜〈實測〉m｜30"]))
        self.assertEqual(e["measured"], ["〈實測〉m（30）"])

    def test_scene_kept_in_design_only(self):
        e = run_one(board("〈項目〉", "", ["〈字一〉", "（意象：〈描述〉）"]))
        self.assertIn("（意象：〈描述〉）", e["design"])
        self.assertNotIn("（意象：〈描述〉）", e["measured"])

    def test_reading_goes_to_measured_only(self):
        e = run_one(board("〈項目〉", "", ["〈字一〉", "（量測讀數：捲尺讀數：〔?〕（刻度看不清））"]))
        self.assertNotIn("（量測讀數：捲尺讀數：〔?〕（刻度看不清））", e["design"])
        self.assertIn("捲尺讀數：〔?〕（刻度看不清）", e["measured"])   # 讀數本身的括號要留著


if __name__ == "__main__":
    unittest.main()
