# build_company.py v0.6｜依「材料自主檢查照片」範例版面（scripts/材料自主檢查照片_範本.xlsx 的「範本」分頁；v0.3 檔頭寫 tools/template_company.xlsx 為舊路徑）產出公司格式
# 用法：python3 build_company.py entries.json 輸出.xlsx [照片紀錄.xlsx]
#   v0.3：給照片紀錄.xlsx 時，把工作資料（原文、基準、分項工程、已確認詞彙）存進輸出檔的隱藏工作表，下次 log_photo.py restore 可接續。
#   v0.4（2026-11-07，補記 c12d817～963caf7 的改動並升版）：字型固定標楷體、內容固定 10pt、不縮字不截行；內容超出時加高該區塊內容列（grow_block），
#         設計超出且實測未填時合併 F:I 並加一行「實測值：【待填】」（決議第 7 項）；棟別未填只留標籤（同範例，決議第 8 項）；
#         PDF 一頁寬（fitToWidth=1）；照片未加高區塊用兩格錨點、加高區塊固定尺寸對齊左上；「超出格子」訊息改為說明已加高（舊訊息誤寫「已截行」）。
#   v0.5（2026-11-08，MIKO 決定卡「留空白」）：照片與材料表都沒有的資訊只留標籤、冒號後空白，不再寫【待確認】【待填】（取代決議第 7 項的【待填】）；合併區塊最後一行改為「實測值：」。
#   v0.6（2026-11-22，13 張驗收獨立稽核：直式照片被拉成 4:3 照片格而變形）：照片先等比縮放、置中補白成照片格比例（2875930×2156190 EMU）再放入（錨點改法見本段後半）；
#         先依 EXIF 轉正；照片紀錄沒有「已確認詞彙」時交付檔仍建一張只有表頭的隱藏表（AC-3）；加高超過 A4 時整張依最高一頁算縮放比例（不用 fitToHeight），區塊不被切到下一頁；照片一律用固定尺寸錨點（起點同範例 A，尺寸沿用 v0.4 加高區塊的固定尺寸 2875930×2156190 EMU），加高區塊上下置中（place）；左右不依欄寬計算（欄寬像素隨字型而變）。重現測試 scripts/tests/test_build_company_photo.py。
#   待 MIKO 決定：加高列與整張縮放是否接受；電腦版 Excel 看不到照片（A／B／C 測試檔待回報；v0.6 改了錨點寫法，舊測試檔不再適用，需用 v0.6 產出的檔重測，見 SKILL.md）。
# entries.json：[{"sec":分項工程名稱,"item":檢查項目,"design":[行...],"measured":[行...],
#                "shot":"115年10月8日","loc":"工區內","bldg":"","photo":"照片路徑或空"}]
# 版面：每頁 46 列；3 個區塊，每塊 14 列（A:E 照片、F:I 資訊）；A46 頁碼。全部複製自範例，不另設計。
import json, sys, os, copy
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XI
from openpyxl.styles import Alignment
from openpyxl.worksheet.pagebreak import Break
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker   # v0.6 起不再用 TwoCellAnchor

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
    return (n + 1) * size * 1.35 + 4  # 多留一行安全餘量，避免末行被裁切

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

BOX_EMU = (2875930, 2156190)                    # 照片格（範例 A 錨點）

def fit_box(path, long_px=1200):                # v0.6：等比縮放、置中補白成照片格比例，避免 Excel 把照片拉變形
    import io
    from PIL import Image as PI, ImageOps
    im = ImageOps.exif_transpose(PI.open(path)).convert("RGB")
    bw, bh = long_px, round(long_px * BOX_EMU[1] / BOX_EMU[0])
    s = min(bw / im.width, bh / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), PI.LANCZOS)
    canvas = PI.new("RGB", (bw, bh), "white"); canvas.paste(im, ((bw - im.width) // 2, (bh - im.height) // 2))
    buf = io.BytesIO(); canvas.save(buf, "JPEG", quality=85); buf.seek(0)
    return buf

def place(ws, top):                             # v0.6：固定尺寸錨點（不拉伸）；起點與尺寸照範例 A（2875930×2156190 EMU；電腦版 Excel 實際位置待 MIKO 實機確認），加高區塊上下置中
    # 欄寬換算像素取決於預設字型（新細明體）的字寬，各軟體不同（雲端 LibreOffice 沒有新細明體、改用替代字型，欄會變寬），
    # 所以左右不依欄寬計算，只用範例 A 的位置與尺寸；列高以點為單位、各軟體相同，可以上下置中。
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor
    from openpyxl.drawing.xdr import XDRPositiveSize2D
    dflt = ws.sheet_format.defaultRowHeight or 16.2
    rh = lambda r: int((ws.row_dimensions[r + 1].height or dflt) * 12700)    # r：0 起算的列
    y0, y1 = 148590, sum(rh(r) for r in range(top, top + 11)) + 10445
    w, h = BOX_EMU                              # 一律範例 A 的尺寸（範例 A 本身就比 11 列的範圍高約 2.5pt），同一檔照片大小一致
    oy, row = y0 + max(0, (y1 - y0 - h) // 2), top
    while oy >= rh(row): oy -= rh(row); row += 1
    return OneCellAnchor(_from=AnchorMarker(col=0, colOff=95250, row=row, rowOff=oy), ext=XDRPositiveSize2D(cx=w, cy=h))

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
            e = entries[i]; top = off + BLOCK_TOP[b]; grew = False
            if e.get('_sheet') and e.get('_row'): raw.append((e['_sheet'], e['_row'], ws.title, top))
            # v0.5：沒有資訊留空白（v0.4 寫【待確認】／【待填】）
            put(ws, top, 6, f"分項工程名稱：{e.get('sec') or ''}\n檢查項目：{e.get('item') or ''}")
            dl = [compact(x) for x in (e.get("design") or [])]; ml = [compact(x) for x in (e.get("measured") or [])]
            dl, dtr = fit_lines(dl); ml, mtr = fit_lines(ml)
            if dtr and not ml:
                # 設計內容超出、實測尚未填：合併 F:I 為一格，讓設計內容完整顯示（不縮字）
                merge_design_wide(ws, top)
                dl = pack_lines([compact(x) for x in (e.get("design") or [])], 176)
                dl = dl + ["實測值："]  # 合併後實測欄消失，保留標籤（v0.4 為「實測值：【待填】」，v0.5 依 MIKO 決定留空白）
                grew = grow_block(ws, top, need_pt(dl, 176)); dtr = False
                c = put(ws, top + 4, 6, "\n".join(dl)); set_font(c, 10)
                c = put(ws, top + 3, 6, "設計/標準值"); set_font(c, 11)
                if dtr: OVERFLOW.append((i + 1, "設計/標準值", e.get("item")))
                ml = None
            else:
                grew = grow_block(ws, top, max(need_pt(dl, 88), need_pt(ml, 88)))
                c = put(ws, top + 4, 6, "\n".join(dl) or None); set_font(c, 10)
                c = put(ws, top + 4, 8, "\n".join(ml) or None); set_font(c, 10)
            if dtr and ml is not None: OVERFLOW.append((i + 1, "設計/標準值", e.get("item")))
            if mtr: OVERFLOW.append((i + 1, "實測值", e.get("item")))
            put(ws, top + 11, 6, f"拍攝時間：{e.get('shot') or ''}")
            put(ws, top + 12, 6, f"拍攝位置：{e.get('loc') or '工區內'}")
            bl = e.get('bldg')
            put(ws, top + 13, 6, f"棟別/層別/空間編號/空間位置：{bl}" if bl else "棟別/層別/空間編號/空間位置")
            if e.get("photo") and os.path.exists(e["photo"]):
                # v0.6：固定尺寸錨點（place），不再用兩格錨點拉伸；舊寫法：未加高兩格錨點填滿 A:E × 12 列、加高時固定尺寸靠左上
                img = XI(fit_box(e["photo"]))
                img.anchor = place(ws, top)
                ws.add_image(img)
    # 加高列後若單頁高度超過未加高時的高度，整張工作表等比縮小到同一頁高（未加高時維持 100%，與範例相同）
    dflt = ws.sheet_format.defaultRowHeight or 16.2
    max_h = max(sum((ws.row_dimensions[r].height or dflt) for r in range(off + 1, off + PAGE_ROWS + 1)) for off in range(0, pages * PAGE_ROWS, PAGE_ROWS))
    # 列印寬度固定為一頁寬（A:I 全部放進同一頁寬，避免 H:I 被拆到另一頁）；高度由分頁符號控制
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    if getattr(ws, "_grown", False):
        ws.page_setup.scale = None  # 有加高列時由 fitToWidth 控制比例
    ws.print_area = f"A1:I{pages * PAGE_ROWS}"
    tm = load_workbook(TPL)[TPL_SHEET].page_margins
    ws.page_margins = copy.copy(tm)  # 邊界與範本相同（不用 openpyxl 預設值，否則每頁會被切成兩頁）
    ws.page_margins.header = ws.page_margins.footer = 0.31496062992125984  # 與範例逐位相同
    if getattr(ws, "_grown", False):            # v0.6：加高後照 max_h 算縮放比例，讓每頁 3 個區塊印在同一張 A4（v0.5 算了 max_h 沒用，PDF 區塊被切到下一頁）
        avail = 841.89 - (ws.page_margins.top + ws.page_margins.bottom) * 72
        if max_h > avail:
            ws.sheet_properties.pageSetUpPr.fitToPage = False
            ws.page_setup.scale = max(10, min(100, int(100 * avail / max_h)))
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
        if lp.VOCAB not in wb.sheetnames:       # v0.6：沒有確認過的詞彙也留空表（AC-3；13 張稽核問題 7）
            v = wb.create_sheet(lp.VOCAB); v.append(['白板原文（待確認）', '確認後', '來源位置', '確認日期', '來源']); v.sheet_state = 'hidden'
    wb.save(out)
    return len(entries), pages

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    n, pg = build(data, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(f"寫入 {n} 筆，{pg} 頁 → {sys.argv[2]}")
    for no, col, item in OVERFLOW:
        # v0.3 舊訊息寫「已截行（10pt 仍放不下）」，但 v0.4 起 fit_lines 不截行、由 grow_block 加高列高完整顯示，舊訊息與實際不符
        print(f"【超出格子】第 {no} 筆（{item}）{col}：內容超出範本格高，已加高該區塊列高完整顯示（未截行、未縮字），請在回覆列出，並用 PDF 抽看該頁")
