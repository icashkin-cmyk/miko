# build_company.py v0.3｜依「材料自主檢查照片」範例版面（tools/template_company.xlsx）產出公司格式
# 用法：python3 build_company.py entries.json 輸出.xlsx [照片紀錄.xlsx]
#   v0.3：給照片紀錄.xlsx 時，把工作資料（原文、基準、分項工程、已確認詞彙）存進輸出檔的隱藏工作表，下次 log_photo.py restore 可接續。
# entries.json：[{"sec":分項工程名稱,"item":檢查項目,"design":[行...],"measured":[行...],
#                "shot":"115年10月8日","loc":"工區內","bldg":"","photo":"照片路徑或空"}]
# 版面：每頁 46 列；3 個區塊，每塊 14 列（A:E 照片、F:I 資訊）；A46 頁碼。全部複製自範例，不另設計。
import json, sys, os, copy
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XI
from openpyxl.styles import Alignment
from openpyxl.worksheet.pagebreak import Break
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.spreadsheet_drawing import TwoCellAnchor, AnchorMarker

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "材料自主檢查照片_範本.xlsx")
TPL_SHEET = "範本"
PAGE_ROWS, BLOCK_TOP, PHOTO_BOX = 46, [4, 18, 32], (340, 290)

def copy_page(tpl_ws, wb_ws, offset):
    # 先合併，再套樣式（openpyxl 合併會重置被合併格的樣式，順序不可對調）
    for rng in tpl_ws.merged_cells.ranges:
        if rng.max_row <= PAGE_ROWS:
            wb_ws.merge_cells(start_row=rng.min_row + offset, start_column=rng.min_col,
                              end_row=rng.max_row + offset, end_column=rng.max_col)
    for r in range(1, PAGE_ROWS + 1):
        h = tpl_ws.row_dimensions[r].height
        if h: wb_ws.row_dimensions[r + offset].height = h
    for r in range(1, PAGE_ROWS + 1):
        for c in range(1, 10):
            s = tpl_ws.cell(r, c); t = wb_ws.cell(r + offset, c)
            t.font = copy.copy(s.font); t.border = copy.copy(s.border)
            t.alignment = copy.copy(s.alignment); t.number_format = s.number_format
            if not isinstance(t, MergedCell): t.value = s.value  # 沿用範本的標籤（標題、設計/標準值、實測值…）；合併格非錨點不寫

def put(ws, row, col, text, size=10, align_top=True):
    # 只寫值，沿用範本格的字型與對齊（與範例一致）
    ws.cell(row, col).value = text
    return ws.cell(row, col)

def build(entries, out, record=None):
    tpl = load_workbook(TPL)[TPL_SHEET]
    wb = Workbook(); ws = wb.active; ws.title = "材料自主檢查照片"; raw = []
    for col, dim in tpl.column_dimensions.items():
        if dim.width: ws.column_dimensions[col].width = dim.width
    pages = max(1, -(-len(entries) // 3))
    for p in range(pages):
        off = p * PAGE_ROWS
        copy_page(tpl, ws, off)
        ws.cell(off + 1, 1).value = "材料自主檢查照片"
        ws.cell(off + PAGE_ROWS, 1).value = p + 1
        ws.row_breaks.append(Break(id=off + PAGE_ROWS))
        for b in range(3):
            top = off + BLOCK_TOP[b]
            for col, row_off in ((6, 0), (6, 4), (8, 4), (6, 11), (6, 12), (6, 13)):
                cell = ws.cell(top + row_off, col)
                if not isinstance(cell, MergedCell): cell.value = None  # 清除範本的範例內容，之後只寫入實際資料
        for b in range(3):
            i = p * 3 + b
            if i >= len(entries): break
            e = entries[i]; top = off + BLOCK_TOP[b]
            if e.get('_sheet') and e.get('_row'): raw.append((e['_sheet'], e['_row'], ws.title, top))
            put(ws, top, 6, f"分項工程名稱：{e.get('sec') or '【待確認】'}\n檢查項目：{e.get('item') or '【待確認】'}")
            put(ws, top + 4, 6, "\n".join(e.get("design") or ["【待確認】"]))
            put(ws, top + 4, 8, "\n".join(e.get("measured") or ["【待填】"]))
            put(ws, top + 11, 6, f"拍攝時間：{e.get('shot') or '【待確認】'}")
            put(ws, top + 12, 6, f"拍攝位置：{e.get('loc') or '工區內'}")
            put(ws, top + 13, 6, f"棟別/層別/空間編號/空間位置：{e.get('bldg') or '【待填】'}")
            if e.get("photo") and os.path.exists(e["photo"]):
                # 照片錨定在 A:E × 本區 14 列（與範例相同：兩格錨點，填滿照片格）
                img = XI(e["photo"])
                img.anchor = TwoCellAnchor(_from=AnchorMarker(col=0, row=top - 1),
                                           to=AnchorMarker(col=5, row=top + 13))
                ws.add_image(img)
    ws.print_area = f"A1:I{pages * PAGE_ROWS}"
    tm = load_workbook(TPL)[TPL_SHEET].page_margins
    ws.page_margins = copy.copy(tm)  # 邊界與範本相同（不用 openpyxl 預設值，否則每頁會被切成兩頁）
    ws.print_options.horizontalCentered = False
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    if record:
        sys.path.insert(0, HERE); import log_photo as lp
        rec = lp.load(record)
        rows = [[d, r, s, t, rec[d].cell(r, 2).value] for d, r, s, t in raw if d in rec.sheetnames]
        lp.keep(rec, wb, rows)
    wb.save(out)
    return len(entries), pages

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    n, pg = build(data, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(f"寫入 {n} 筆，{pg} 頁 → {sys.argv[2]}")
