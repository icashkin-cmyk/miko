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


import math
OVERFLOW = []  # 內容放不進格子（縮到最小字級仍超出）的紀錄，交檔時須列在回覆

def compact(line):
    # 只去掉無資訊的「—」占位與完全相同的重複片段；其餘資訊一律保留
    parts = []
    for seg in line.split("｜"):
        seg = seg.strip()
        if seg in ("", "—", "-", "－"): continue
        if parts and parts[-1] == seg: continue
        parts.append(seg)
    return "｜".join(parts) if parts else line

def pack_lines(lines, width_pt, size=10):
    # 合併寬格時，把相鄰的短行併成同一行（以「 ｜ 」連接），不改動文字內容，只減少行數
    def w(t): return sum(size * (1.0 if ord(ch) > 127 else 0.55) for ch in t)
    out = []
    for line in lines:
        if out and w(out[-1] + " ｜ " + line) <= width_pt: out[-1] = out[-1] + " ｜ " + line
        else: out.append(line)
    return out

def need_pt(lines, width_pt, size=10):
    # 完整顯示所需高度（點）：行數 × 行高（10pt × 1.35）
    def w(t): return sum(size * (1.0 if ord(ch) > 127 else 0.55) for ch in t)
    n = 0
    for line in lines:
        n += max(1, math.ceil(w(line) / width_pt))
    return n * size * 1.35 + 4

def grow_block(ws, top, need):
    # 內容列 top+4..top+10 的總高度至少為 need；僅超出時才加高（不影響未超出的區塊）
    rows = list(range(top + 4, top + 11))
    cur = sum((ws.row_dimensions[r].height or 16.2) for r in rows)
    if need <= cur: return False
    each = round(need / len(rows) + 0.05, 2)
    for r in rows: ws.row_dimensions[r].height = max(each, 16.2)
    ws._grown = True
    return True

def merge_design_wide(ws, top):
    # 區塊內 設計/實測 欄改為 F:I 合併（僅用於設計超出且實測未填的區塊）
    h, r0, r1 = top + 3, top + 4, top + 10
    for rng in (f"F{h}:G{h}", f"H{h}:I{h}", f"F{r0}:G{r1}", f"H{r0}:I{r1}"):
        ws.unmerge_cells(rng)
    for r in range(h, r1 + 1):
        for col in (8, 9):
            cell = ws.cell(r, col)
            if not isinstance(cell, MergedCell): cell.value = None
    ws.merge_cells(f"F{h}:I{h}"); ws.merge_cells(f"F{r0}:I{r1}")

FONT_NAME = "標楷體"  # 範例全部使用標楷體
def fit_lines(lines, size=10, width_pt=88, height_pt=108):
    # 字型與字級固定（與範例相同：內容 10pt），不縮字；放不下時自尾端截行，加註「…另 N 行見原文分頁」
    def need(ls):
        n = 0
        for line in ls:
            w = sum(size * (1.0 if ord(ch) > 127 else 0.55) for ch in line)
            n += max(1, math.ceil(w / width_pt))
        return n
    if need(lines) * size * 1.35 <= height_pt: return lines, False
    return lines, True  # 不截行：內容完整保留，由列高擴充處理（見 grow_block）
    keep = list(lines)
    while len(keep) > 1:
        keep.pop()
        shown = keep + [f"…另 {len(lines) - len(keep)} 行見原文分頁"]
        if need(shown) * size * 1.35 <= height_pt: return shown, True
    return lines, True

def set_font(cell, size=None):
    f = copy.copy(cell.font)
    f.name = FONT_NAME
    if size: f.sz = size
    cell.font = f

def put(ws, row, col, text, size=10, align_top=True):
    # 只寫值，沿用範本格的字型與對齊（與範例一致）
    c = ws.cell(row, col); c.value = text
    if not isinstance(c, MergedCell): set_font(c)  # 字型固定為標楷體，字級沿用範本
    return c

def build(entries, out, record=None):
    # 以範本活頁簿為底（預設字型 新細明體 12 與範例相同），只保留輸出分頁
    wb = load_workbook(TPL); tpl = wb[TPL_SHEET]
    ws = wb.create_sheet("材料自主檢查照片", 0); raw = []
    ws.sheet_format = copy.copy(tpl.sheet_format)  # 預設列高 16.2、基準欄寬 8（與範例相同）
    for name in list(wb.sheetnames):
        if name != ws.title: del wb[name]
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
            if i >= len(entries):
                # 空白區塊：與範例末頁空白區相同，只保留「拍攝位置：工區內」與棟別標籤
                top = off + BLOCK_TOP[b]
                put(ws, top + 12, 6, "拍攝位置：工區內")
                put(ws, top + 13, 6, "棟別/層別/空間編號/空間位置")
                continue
            e = entries[i]; top = off + BLOCK_TOP[b]
            if e.get('_sheet') and e.get('_row'): raw.append((e['_sheet'], e['_row'], ws.title, top))
            put(ws, top, 6, f"分項工程名稱：{e.get('sec') or '【待確認】'}\n檢查項目：{e.get('item') or '【待確認】'}")
            dl = [compact(x) for x in (e.get("design") or ["【待確認】"])]; ml = [compact(x) for x in (e.get("measured") or ["【待填】"])]
            dl, dtr = fit_lines(dl); ml, mtr = fit_lines(ml)
            if dtr and all(x == "【待填】" for x in ml):
                # 設計內容超出、實測尚未填：合併 F:I 為一格，讓設計內容完整顯示（不縮字）
                merge_design_wide(ws, top)
                dl = pack_lines([compact(x) for x in (e.get("design") or ["【待確認】"])], 176)
                grow_block(ws, top, need_pt(dl, 176)); dtr = False
                c = put(ws, top + 4, 6, "\n".join(dl)); set_font(c, 10)
                c = put(ws, top + 3, 6, "設計/標準值"); set_font(c, 11)
                if dtr: OVERFLOW.append((i + 1, "設計/標準值", e.get("item")))
                ml = None
            else:
                grow_block(ws, top, max(need_pt(dl, 88), need_pt(ml, 88)))
                c = put(ws, top + 4, 6, "\n".join(dl)); set_font(c, 10)
                c = put(ws, top + 4, 8, "\n".join(ml)); set_font(c, 10)
            if dtr and ml is not None: OVERFLOW.append((i + 1, "設計/標準值", e.get("item")))
            if mtr: OVERFLOW.append((i + 1, "實測值", e.get("item")))
            put(ws, top + 11, 6, f"拍攝時間：{e.get('shot') or '【待確認】'}")
            put(ws, top + 12, 6, f"拍攝位置：{e.get('loc') or '工區內'}")
            bl = e.get('bldg')
            put(ws, top + 13, 6, f"棟別/層別/空間編號/空間位置：{bl}" if bl else "棟別/層別/空間編號/空間位置")
            if e.get("photo") and os.path.exists(e["photo"]):
                # 照片錨定在 A:E × 本區 14 列（與範例相同：兩格錨點，填滿照片格）
                img = XI(e["photo"])
                img.width, img.height = 302, 226  # 與範例的圖片 xfrm 相同（2875930×2156190 EMU）
                # 與範例相同：起點 A 欄 +95250 EMU、列 +148590 EMU；終點 E 欄 +532780 EMU、列 +10445 EMU（區塊 12 列）
                img.anchor = TwoCellAnchor(_from=AnchorMarker(col=0, colOff=95250, row=top, rowOff=148590),
                                           to=AnchorMarker(col=4, colOff=532780, row=top + 11, rowOff=10445 if b == 0 else 10446))
                ws.add_image(img)
    # 加高列後若單頁高度超過未加高時的高度，整張工作表等比縮小到同一頁高（未加高時維持 100%，與範例相同）
    dflt = ws.sheet_format.defaultRowHeight or 16.2
    max_h = max(sum((ws.row_dimensions[r].height or dflt) for r in range(off + 1, off + PAGE_ROWS + 1)) for off in range(0, pages * PAGE_ROWS, PAGE_ROWS))
    if getattr(ws, "_grown", False):
        ws.page_setup.scale = min(100, int(PAGE_ROWS * 16.2 / max_h * 100))  # 有加高列時才縮放，以未加高的單頁高度為準
    ws.print_area = f"A1:I{pages * PAGE_ROWS}"
    tm = load_workbook(TPL)[TPL_SHEET].page_margins
    ws.page_margins = copy.copy(tm)  # 邊界與範本相同（不用 openpyxl 預設值，否則每頁會被切成兩頁）
    ws.page_margins.header = ws.page_margins.footer = 0.31496062992125984  # 與範例逐位相同
    ws.print_options.horizontalCentered = True   # 與範例相同
    ws.print_options.verticalCentered = True
    ws.sheet_view.zoomScale = 160               # 與範例相同
    ws.sheet_view.view = "pageBreakPreview"; ws.sheet_view.zoomScaleSheetLayoutView = 160; ws.sheet_view.tabSelected = True  # 與範例相同
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
    for no, col, item in OVERFLOW:
        print(f"【超出格子】第 {no} 筆（{item}）{col}：設計/實測內容已截行（10pt 仍放不下），完整內容保留在 entries.json 與原文分頁，請在回覆列出並確認")
