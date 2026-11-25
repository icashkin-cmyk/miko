"""build_company.py 照片不得變形（2026-11-22，13 張驗收獨立稽核：直式照片被拉成 4:3 照片格，嚴重變形）。
照片格固定 2875930×2156190 EMU（範例 A 的錨點）；照片要等比縮放、置中，空白處補白。"""
import io, json, os, subprocess, sys, tempfile, unittest, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = 2875930 / 2156190


class BuildCompanyPhotoAspect(unittest.TestCase):
    def test_portrait_photo_not_stretched(self):
        with tempfile.TemporaryDirectory() as d:
            ph = os.path.join(d, "p.jpg"); Image.new("RGB", (300, 600), (200, 0, 0)).save(ph)
            ent = [{"sec": "", "item": "〈項目〉", "design": ["〈字〉"], "measured": ["〈字〉"], "shot": "", "loc": "工區內", "bldg": "", "photo": ph}]
            ej = os.path.join(d, "e.json"); json.dump(ent, open(ej, "w", encoding="utf-8"), ensure_ascii=False)
            out = os.path.join(d, "o.xlsx")
            cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "build_company.py"), ej, out], capture_output=True, text=True, cwd=d)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            with zipfile.ZipFile(out) as z:
                media = [n for n in z.namelist() if n.startswith("xl/media/")]
                self.assertEqual(len(media), 1)
                im = Image.open(io.BytesIO(z.read(media[0]))).convert("RGB")
        # 放進照片格的圖片比例要等於照片格比例（等比縮放後補白），而不是原照片 1:2 被拉成 4:3
        self.assertAlmostEqual(im.width / im.height, BOX, delta=0.02)
        # 原照片內容（紅色）等比放在中間：紅色區域寬高比仍是 1:2
        px = im.load(); red = [(x, y) for x in range(0, im.width, 2) for y in range(0, im.height, 2) if px[x, y][0] > 150 and px[x, y][1] < 80]
        xs = [x for x, _ in red]; ys = [y for _, y in red]
        self.assertAlmostEqual((max(xs) - min(xs)) / (max(ys) - min(ys)), 0.5, delta=0.05)
        self.assertLess(abs((min(xs) + max(xs)) / 2 - im.width / 2), im.width * 0.03)



class BuildCompanyAnchor(unittest.TestCase):
    """照片顯示範圍也不得變形（2026-11-22 第二輪稽核 AC7）：未加高區塊用兩格錨點，照片被拉成錨點範圍（PDF 比例 1.82，原 1.334）。
    每張照片都要用固定尺寸（OneCellAnchor）且寬高比等於圖片比例；加高區塊也要置中，不靠左上。"""

    def test_anchor_keeps_ratio(self):
        from openpyxl import load_workbook
        from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor
        with tempfile.TemporaryDirectory() as d:
            ph = os.path.join(d, "p.jpg"); Image.new("RGB", (400, 300), "gray").save(ph)
            short = {"sec": "", "item": "〈項目〉", "design": ["〈字〉"], "measured": ["〈字〉"], "shot": "", "loc": "工區內", "bldg": "", "photo": ph}
            long = dict(short, design=[f"〈第{i}行〉" for i in range(30)])
            ej = os.path.join(d, "e.json"); json.dump([short, long, short], open(ej, "w", encoding="utf-8"), ensure_ascii=False)
            out = os.path.join(d, "o.xlsx")
            cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "build_company.py"), ej, out], capture_output=True, text=True, cwd=d)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            ws = load_workbook(out).active
            self.assertEqual(len(ws._images), 3)
            for im in ws._images:
                a = im.anchor
                self.assertIsInstance(a, OneCellAnchor)
                self.assertEqual((a.ext.width, a.ext.height), (2875930, 2156190))   # 第四輪稽核：大小一致、等於範例 A
                self.assertEqual((a._from.col, a._from.colOff), (0, 95250))
            # 加高區塊（第 2 筆）的照片要往下置中，不能貼在區塊頂端
            tops = sorted(im.anchor._from.row for im in ws._images)
            self.assertGreater(tops[1], 3 + 14)


class BuildCompanyWorkSheets(unittest.TestCase):
    """AC-3：交付檔有隱藏工作表「原文」「基準」「已確認詞彙」；沒有確認過的詞彙時「已確認詞彙」也要在（只有表頭）。
    重現（2026-11-22，13 張驗收獨立稽核問題 7）：照片紀錄沒有已確認詞彙分頁時，交付檔少了這張隱藏表。"""

    def test_vocab_sheet_always_present(self):
        from openpyxl import Workbook, load_workbook
        with tempfile.TemporaryDirectory() as d:
            ph = os.path.join(d, "p.jpg"); Image.new("RGB", (400, 300), "gray").save(ph)
            rec = Workbook(); ws = rec.active; ws.title = "2026-10-27"; ws["B2"] = "查驗項目：〈項目〉"
            b = rec.create_sheet("基準"); b.append(["欄位", "值"]); b.append(["工程名稱", "〈工程名稱〉"])
            rp = os.path.join(d, "照片紀錄.xlsx"); rec.save(rp)
            ent = [{"sec": "", "item": "〈項目〉", "design": ["〈字〉"], "measured": ["〈字〉"], "shot": "", "loc": "工區內", "bldg": "",
                    "photo": ph, "_sheet": "2026-10-27", "_row": 2}]
            ej = os.path.join(d, "e.json"); json.dump(ent, open(ej, "w", encoding="utf-8"), ensure_ascii=False)
            out = os.path.join(d, "o.xlsx")
            cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "build_company.py"), ej, out, rp], capture_output=True, text=True, cwd=d)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            wb = load_workbook(out)
            for name in ("原文", "基準", "已確認詞彙"):
                self.assertIn(name, wb.sheetnames)
                self.assertEqual(wb[name].sheet_state, "hidden")



class BuildCompanyPageFit(unittest.TestCase):
    """內容很長、區塊加高時，每一頁（3 個區塊）仍要印在一張 A4 上，不能把區塊切到下一頁。
    重現（2026-11-22，13 張驗收）：加高後 fitToHeight=0、縮放比例沒算（max_h 算了沒用），LibreOffice PDF 由 4 頁變 8 頁。"""

    def test_grown_page_scaled_to_a4(self):
        from openpyxl import load_workbook
        with tempfile.TemporaryDirectory() as d:
            ph = os.path.join(d, "p.jpg"); Image.new("RGB", (400, 300), "gray").save(ph)
            long = [f"〈第{i}行〉" for i in range(40)]
            ent = [{"sec": "", "item": "〈項目〉", "design": long, "measured": long, "shot": "", "loc": "工區內", "bldg": "", "photo": ph}] * 3
            ej = os.path.join(d, "e.json"); json.dump(ent, open(ej, "w", encoding="utf-8"), ensure_ascii=False)
            out = os.path.join(d, "o.xlsx")
            cp = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "build_company.py"), ej, out], capture_output=True, text=True, cwd=d)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            ws = load_workbook(out).active
            m = ws.page_margins
            avail = 841.89 - (m.top + m.bottom) * 72
            dflt = ws.sheet_format.defaultRowHeight or 16.2
            page_h = sum((ws.row_dimensions[r].height or dflt) for r in range(1, 47))
            self.assertGreater(page_h, avail)                     # 確實加高超過一頁
            self.assertFalse(ws.sheet_properties.pageSetUpPr.fitToPage)
            self.assertIsNotNone(ws.page_setup.scale)
            self.assertLessEqual(page_h * int(ws.page_setup.scale) / 100, avail)


if __name__ == "__main__":
    unittest.main()
