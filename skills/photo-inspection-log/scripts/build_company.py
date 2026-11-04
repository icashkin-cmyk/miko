# build_company.py v0.2｜依「材料自主檢查照片」範例版面（tools/template_company.xlsx）產出公司格式
# 用法：python3 build_company.py entries.json 輸出.xlsx
# entries.json：[{"sec":分項工程名稱,"item":檢查項目,"design":[行...],"measured":[行...],
#                "shot":"115年10月8日","loc":"工區內","bldg":"","photo":"照片路徑或空"}]
# 版面：每頁 46 列；3 個區塊，每塊 14 列（A:E 照片、F:I 資訊）；A46 頁碼。全部複製自範例，不另設計。
import json, sys, os, copy
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XI
from openpyxl.styles import Alignment
from openpyxl.worksheet.pagebreak import Break
from openpyxl.drawing.spreadsheet_drawing import TwoCellAnchor, AnchorMarker

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "材料自主檢查照片_範本.xlsx")
TPL_SHEET = "範本"
PAGE_ROWS, BLOCK_TOP, PHOTO_BOX = 46, [4, 18, 32], (340, 290)

def copy_page(tpl_ws, wb_ws, offset):
    for r in range(1, PAGE_ROWS + 1):
        for c in range(1, 10):
            s = tpl_ws.cell(r, c); t = wb_ws.cell(r + offset, c)
            if s.has_style:
                t.font = copy.copy(s.font); t.border = copy.copy(s.border)
                t.alignment = copy.copy(s.alignment); t.number_format = s.number_format
            if s.value is not None and r == 1:
                t.value = s.value  # 只有標題列沿用範本文字
    for rng in tpl_ws.merged_cells.ranges:
        if rng.max_row <= PAGE_ROWS:
            wb_ws.merge_cells(start_row=rng.min_row + offset, start_column=rng.min_col,
                              end_row=rng.max_row + offset, end_column=rng.max_col)
    for r in range(1, PAGE_ROWS + 1):
        h = tpl_ws.row_dimensions[r].height
        if h: wb_ws.row_dimensions[r + offset].height = h

def put(ws, row, col, text, size=10, align_top=True):
    c = ws.cell(row, col, text)
    c.font = copy.copy(ws.cell(row, col).font)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True) if align_top else Alignment(horizontal="center", vertical="center")
    return c

def build(entries, out):
    tpl = load_workbook(TPL)[TPL_SHEET]
    wb = Workbook(); ws = wb.active; ws.title = "材料自主檢查照片"
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
            i = p * 3 + b
            if i >= len(entries): break
            e = entries[i]; top = off + BLOCK_TOP[b]
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
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    wb.save(out)
    return len(entries), pages

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    n, pg = build(data, sys.argv[2])
    print(f"寫入 {n} 筆，{pg} 頁 → {sys.argv[2]}")
