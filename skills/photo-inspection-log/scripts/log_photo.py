# log_photo.py v0.14｜施工查驗照片登記（支援一次上百張）：每天一個分頁；A 欄照片（固定在格子裡）、B 欄照片文字，一張一列；自動整理詞庫
# 視覺：待確認處自動編號〔?1〕〔?2〕並標紅字，和提問、放大圖同號；分頁標籤黃色＝有待確認；表頭顯示張數與待確認列數；清單可點擊跳到該列
# 分頁：依 B 欄「查驗時間」的日期（YYYY-MM-DD）分頁；查驗時間讀不到用照片日期；都沒有放「日期未知」。不同天不會接在同一頁。
# 位置寫法：「分頁:列號」，例 2026-10-15:3；分頁可只寫月日（10-15:3）；只有一個分頁時可只寫列號。
# 用法：
#   python3 log_photo.py prep      來源資料夾或.zip 紀錄.xlsx          去重（SHA-256）、讀 EXIF 日期、轉正、縮圖、格線圖、抄寫範本 text/NNN.tpl，產生 manifest.csv
#   python3 log_photo.py addmany   紀錄.xlsx [manifest.csv]           已有 text/NNN.txt 的照片一次寫入，各自放進該日分頁（只存檔一次）
#   python3 log_photo.py add       紀錄.xlsx 照片.jpg 文字.txt [--fixed 固定欄位.txt] [--sha 雜湊] [--name 原檔名]
#   python3 log_photo.py fix       紀錄.xlsx 位置 "原文字" "確認後文字" [--source 來源]   改到日期時自動搬到正確分頁
#   python3 log_photo.py vocab     紀錄.xlsx "白板寫法" "確認後" 來源    型錄等外部來源確認的寫法也記進已確認詞彙
#   python3 log_photo.py set       紀錄.xlsx 位置 文字.txt               整格改寫（格式調整或自己抄錯），不記進已確認詞彙
#   python3 log_photo.py check     紀錄.xlsx
#   python3 log_photo.py questions 紀錄.xlsx                           依回覆樣板列出所有含〔?〕的行
#   python3 log_photo.py glossary  紀錄.xlsx [--import 詞庫.csv]       重建並列出詞庫（查驗項目、人名、廠牌、品名用語、型號、位置），另存 詞庫.csv；抄寫前先看
#   python3 log_photo.py grid      照片.jpg 輸出.jpg                    疊座標格線（每 100 像素），框選讀不清的位置前先看
#   python3 log_photo.py crops     照片.jpg 輸出.png [編號:]x0,y0,x1,y1 ...    放大、編號（編號對應〔?N〕），左原圖右增強
#   python3 log_photo.py export    紀錄.xlsx 材料自主檢查照片.xlsx       輸出公司格式（A4 直式、每頁 3 張、標楷體），每天一個分頁
#   python3 log_photo.py sub       紀錄.xlsx "查驗項目" "分項工程名稱"  記下分項工程名稱，export 時填入
#   python3 log_photo.py terms     [自主檢查名詞.csv]                  列出 forms.csv 的材料自主檢查表名詞
#   python3 log_photo.py restore   材料自主檢查照片.xlsx 紀錄.xlsx       新對話接續：從公司格式檔的隱藏工作表還原工作檔（原文、照片、詞彙、基準、分項工程）
# 交付：只交「材料自主檢查照片.xlsx」（公司格式）；工作資料藏在它的隱藏工作表，下次上傳這一個檔就能接續。
# 結束碼：0 成功；2 固定欄位與基準不同；3 fix 找不到或不只一處；4 前兩行不是「查驗時間：」「照片日期：」；5 照片重複；6 位置寫法不對或找不到分頁（以上都未寫入）
import sys, os, re, csv, hashlib, zipfile, datetime
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.drawing.spreadsheet_drawing import TwoCellAnchor, AnchorMarker
from openpyxl.utils.units import pixels_to_EMU, EMU_to_pixels
from openpyxl.worksheet.hyperlink import Hyperlink
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageOps, ImageFilter
try:
    import pillow_heif; pillow_heif.register_heif_opener()   # iPhone HEIC
except ImportError:
    pass

IMG_W, IMG_H_MAX = 400, 480                     # Excel 內顯示寬度與高度上限（像素）；v0.11 放大，白板字較好讀
COL_A = 59                                      # A 欄寬（約 410 像素，放得下照片加邊距）
READ_MAX, XL_MAX, XL_Q = 2000, 1200, 78         # 判讀用長邊、放進 Excel 的長邊與 JPEG 品質
EXTS = ('.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp')
LINE = Side(style='thin', color='999999')
BOX = Border(left=LINE, right=LINE, top=LINE, bottom=LINE)
F, FB = Font(name='Arial', size=11), Font(name='Arial', size=11, bold=True)
PENDING, NOFILL = PatternFill('solid', fgColor='FFF2CC'), PatternFill(fill_type=None)
HEADFILL = PatternFill('solid', fgColor='D9D9D9')
LEGACY, BASE, VOCAB, INDEX, Q = '照片紀錄', '基準', '已確認詞彙', '清單', '〔?〕'   # LEGACY：v0.9 以前所有日期放同一頁，載入時自動拆成每日分頁
UNK = '日期未知'
HEAD = ('查驗時間：', '照片日期：')            # B 欄固定前兩行
MF = ['nnn', '原檔名', 'sha256', 'exif時間', '照片日期', '狀態', '列號']
GLOSS, CATS = '詞庫', ['查驗項目', '人名', '廠牌', '品名用語', '型號', '位置']
TAIL = [INDEX, BASE, '分項工程', VOCAB, GLOSS]              # 每日分頁之後的工作表順序
MODEL = re.compile(r'(?<![A-Za-z0-9])[A-Z]{1,3}\d{3,5}[A-Z]{0,2}\d?(?![A-Za-z0-9])')      # 例：LF1124P、EF4005、V2700
NAME = re.compile(r'[一-鿿][一-鿿0-9°A-Za-z ]*[一-鿿]')            # 一行裡第一段中文品名或用語
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
PAD = 4                                         # 照片離格線的邊距（像素）
QRE = re.compile(r'〔\?(\d*)〕')                 # 待確認標記：〔?〕寫入時自動編號成〔?1〕〔?2〕
WARN = re.compile(r'〔\?\d*〕|（≠查驗時間）')       # 紅字顯示的部分
RED, LINK = 'C00000', '0563C1'
TAB_PEND, TAB_UNK = 'FFC000', 'A6A6A6'          # 分頁標籤：黃＝有待確認；灰＝日期未知

class Stop(Exception):
    def __init__(self, code, msg): self.code, self.msg = code, msg

# ---------- 共用 ----------
def field(text, key):
    for ln in str(text or '').split('\n'):
        if ln.startswith(key + '：'): return ln.split('：', 1)[1]
    return ''

def qcount(text):                               # 待確認處數
    return len(QRE.findall(str(text or '')))

def number_q(text):                             # 沒編號的〔?〕依序編號，接在本格已有的最大號之後（確認過的號不重排）
    n = max([int(x) for x in QRE.findall(text) if x] + [0])
    def rep(m):
        nonlocal n
        if m.group(1): return m.group(0)
        n += 1; return f'〔?{n}〕'
    return QRE.sub(rep, text)

def day_of(text):                               # 這張照片屬於哪一天的分頁
    for key in ('查驗時間', '照片日期'):
        d = field(text, key)[:10]
        if DATE.fullmatch(d): return d
    return UNK

def is_day(name):
    return name == UNK or bool(DATE.fullmatch(name))

def day_sheets(wb):
    return [ws for ws in wb.worksheets if is_day(ws.title)]

def order_sheets(wb):                           # 每日分頁依日期排（日期未知最後），再接清單、基準、已確認詞彙、詞庫
    def key(ws):
        if is_day(ws.title): return (0, ws.title if ws.title != UNK else '9999')
        return (1, TAIL.index(ws.title) if ws.title in TAIL else 99, ws.title)
    wb._sheets.sort(key=key)
    days = [ws for ws in day_sheets(wb) if ws.title != UNK] or day_sheets(wb)
    act = days[-1] if days else wb.worksheets[0]  # 開檔時停在最新一天
    wb.active = wb.worksheets.index(act)
    for ws in wb.worksheets: ws.sheet_view.tabSelected = ws is act   # 只選一頁，避免 Excel 把多頁群組在一起

def style_head(ws):
    for c in ws[1][:2]:
        c.font = FB; c.fill = HEADFILL; c.border = BOX
        c.alignment = Alignment(horizontal='center', vertical='center')

def setup_page(ws):
    ws.page_setup.orientation = 'landscape'
    ws.print_title_rows = '1:1'; ws.print_options.horizontalCentered = True   # 每頁都印表頭、置中
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0

def day_sheet(wb, day):                         # 取得該日分頁，沒有就新開一頁（不接在前一天後面）
    if day in wb.sheetnames: return wb[day]
    ws = wb.create_sheet(day)
    ws['A1'], ws['B1'] = '照片', '照片文字'
    ws.column_dimensions['A'].width, ws.column_dimensions['B'].width = COL_A, 60
    ws.freeze_panes = 'A2'; style_head(ws); setup_page(ws)
    for s in list(wb.worksheets):               # 新建活頁簿的預設空白頁拿掉
        if s.title == 'Sheet' and s.max_row == 1 and s['A1'].value is None: wb.remove(s)
    order_sheets(wb)
    return ws

def in_cell(img, row, w, h):                    # 照片放進 A 欄該列的格子裡，設成「隨儲存格移動及調整大小」
    img.anchor = TwoCellAnchor(editAs='twoCell',
        _from=AnchorMarker(col=0, colOff=pixels_to_EMU(PAD), row=row - 1, rowOff=pixels_to_EMU(PAD)),
        to=AnchorMarker(col=0, colOff=pixels_to_EMU(PAD + w), row=row - 1, rowOff=pixels_to_EMU(PAD + h)))

def img_size(img):
    a = img.anchor
    if isinstance(a, TwoCellAnchor):
        return EMU_to_pixels(a.to.colOff - a._from.colOff), EMU_to_pixels(a.to.rowOff - a._from.rowOff)
    return EMU_to_pixels(a.ext.width), EMU_to_pixels(a.ext.height)

def lock_images(ws):                            # 舊檔浮動的照片也改成固定在格子裡
    for img in ws._images:
        a = img.anchor
        if isinstance(a, TwoCellAnchor) or a._from.col != 0: continue
        w, h = img_size(img); in_cell(img, a._from.row + 1, w, h)

def copy_row(src, r, dst, nr):                  # 整列（照片＋文字＋格式＋列高）搬到另一頁的 nr 列
    s, d = src[f'B{r}'], dst[f'B{nr}']
    d.value = s.value; d.font = FB; d.border = BOX
    d.alignment = Alignment(wrap_text=True, vertical='top'); dst[f'A{nr}'].border = BOX
    dst.row_dimensions[nr].height = src.row_dimensions[r].height
    for img in [i for i in src._images if i.anchor._from.row == r - 1]:
        w, h = img_size(img); src._images.remove(img); in_cell(img, nr, w, h); dst._images.append(img)

def index_sheet(wb):
    return sheet(wb, INDEX, ['列號', '原檔名', 'SHA-256', '查驗時間', '照片日期', '查驗項目', '待確認', '分頁', '前往'], [6, 18, 12, 22, 12, 26, 8, 12, 20])

def move_index(wb, s, r, ns, nr):               # 清單上的位置跟著搬
    ix = index_sheet(wb)
    for i in range(2, ix.max_row + 1):
        if ix.cell(i, 1).value == r and (ix.cell(i, 8).value or LEGACY) == s:
            ix.cell(i, 1, nr); ix.cell(i, 8, ns); return

def migrate(wb):                                # v0.9 以前的單一「照片紀錄」頁拆成每日分頁
    if LEGACY not in wb.sheetnames: return
    old = wb[LEGACY]; lock_images(old)
    for r in range(2, old.max_row + 1):
        if old[f'B{r}'].value is None: continue
        ws = day_sheet(wb, day_of(old[f'B{r}'].value)); nr = ws.max_row + 1
        copy_row(old, r, ws, nr); move_index(wb, LEGACY, r, ws.title, nr)
    wb.remove(old); order_sheets(wb)

def load(xlsx):
    wb = load_workbook(xlsx, rich_text=True)    # 保留粗體
    migrate(wb)
    for ws in day_sheets(wb): lock_images(ws)
    return wb

def locate(wb, spec):                           # 「2026-10-15:3」「10-15:3」或只有一個分頁時「3」
    s, _, r = str(spec).rpartition(':')
    days = [ws.title for ws in day_sheets(wb)]
    if not s:
        if len(days) != 1: raise Stop(6, f'有 {len(days)} 個分頁，位置請寫「分頁:列號」，例 {days[-1] if days else "2026-10-15"}:3')
        s = days[0]
    hit = [d for d in days if d == s or d.endswith(s)]
    if len(hit) != 1 or not r.isdigit(): raise Stop(6, f'找不到分頁「{s}」或列號「{r}」；現有分頁：{"、".join(days)}')
    ws = wb[hit[0]]; r = int(r)
    if not (2 <= r <= ws.max_row): raise Stop(6, f'{ws.title} 沒有第 {r} 列（共 {ws.max_row - 1} 列）')
    return ws, r

def relocate(wb, ws, r):                        # 日期改了：整列搬到正確的分頁，原分頁下面的列往上補
    day = day_of(ws[f'B{r}'].value)
    if day == ws.title: return ws, r
    dst = day_sheet(wb, day); nr = dst.max_row + 1
    copy_row(ws, r, dst, nr); move_index(wb, ws.title, r, '__moving__', 0)
    last = ws.max_row
    heights = {i: ws.row_dimensions[i].height for i in range(r + 1, last + 1)}
    ws.delete_rows(r)
    for i, h in heights.items(): ws.row_dimensions[i - 1].height = h
    ws.row_dimensions[last].height = None
    for img in ws._images:
        if img.anchor._from.row > r - 1: img.anchor._from.row -= 1; img.anchor.to.row -= 1
    ix = index_sheet(wb)
    for i in range(2, ix.max_row + 1):
        if (ix.cell(i, 8).value or LEGACY) == ws.title and (ix.cell(i, 1).value or 0) > r: ix.cell(i, 1, ix.cell(i, 1).value - 1)
    move_index(wb, '__moving__', 0, dst.title, nr)
    if ws.max_row == 1 and not ws._images: wb.remove(ws)
    order_sheets(wb)
    return dst, nr

def flag_dates(text):                           # 照片日期和查驗時間不同時，自動在照片日期行尾加「（≠查驗時間）」
    ls = text.split('\n')
    if len(ls) > 1 and ls[0].startswith(HEAD[0]) and ls[1].startswith(HEAD[1]):
        ls[1] = ls[1].replace('（≠查驗時間）', '')       # 先拿掉舊標註，改日期後重新判斷
        a, b = ls[0].split('：', 1)[1][:10], ls[1].split('：', 1)[1][:10]
        if DATE.fullmatch(a) and DATE.fullmatch(b) and a != b and '≠' not in ls[1]:   # 兩邊都是完整日期才比
            ls[1] += '（≠查驗時間）'
    return '\n'.join(ls)

def rich(text):                                 # 前兩行整行粗體；其餘每行冒號前粗體
    lines = text.split('\n')
    if len(lines) < 2 or not (lines[0].startswith(HEAD[0]) and lines[1].startswith(HEAD[1])):
        raise Stop(4, f'前兩行必須是「{HEAD[0]}」「{HEAD[1]}」')
    TOP = InlineFont(rFont='Arial', sz=11, b=True)   # 不加顏色：部分手機預覽會吃掉帶顏色的粗體
    TXT = InlineFont(rFont='Arial', sz=11)
    RT, RX = InlineFont(rFont='Arial', sz=11, b=True, color=RED), InlineFont(rFont='Arial', sz=11, color=RED)   # 〔?N〕、（≠查驗時間）紅字
    segs = []
    for i, ln in enumerate(lines):
        nl = '\n' if i else ''
        if i < 2:
            segs.append((TOP, nl + ln))
        elif '：' in ln:
            k, v = ln.split('：', 1); segs += [(TOP, nl + k + '：'), (TXT, v)]
        else:
            segs.append((TXT, nl + ln))
    red = []                                    # 待確認與日期不符的字切出來標紅
    for f, t in segs:
        i = 0
        for m in WARN.finditer(t):
            red += [(f, t[i:m.start()]), (RT if f is TOP else RX, m.group(0))]; i = m.end()
        red.append((f, t[i:]))
    out = []
    for f, t in red:
        if not t: continue
        if out and out[-1][0] is f: out[-1] = (f, out[-1][1] + t)
        else: out.append((f, t))
    return CellRichText([TextBlock(f, t) for f, t in out])

def sheet(wb, name, head, widths):
    if name in wb.sheetnames:
        ws = wb[name]
        for i, h in enumerate(head, 1):         # 舊版表頭缺欄就補上
            if ws.cell(1, i).value is None: ws.cell(1, i, h).font = FB
        return ws
    ws = wb.create_sheet(name); ws.append(head)
    for c in ws[1]: c.font = FB
    for col, w in zip('ABCDEFGHI', widths): ws.column_dimensions[col].width = w
    return ws

def mark(ws):                                   # 含〔?〕的列淺黃底，確認完自動清除
    for r in range(2, ws.max_row + 1):
        c = ws[f'B{r}']
        c.fill = PENDING if qcount(c.value) else NOFILL

def fit(ws, r, text, img_h=0):                  # 中文行高約 17 點
    need = max(img_h * 0.75 + 6, (text.count('\n') + 1) * 17 + 8)
    ws.row_dimensions[r].height = max(need, ws.row_dimensions[r].height or 0)

def finish(wb, xlsx):                           # 存檔前：每頁格式、詞庫、分頁順序
    for ws in day_sheets(wb): restyle(ws); setup_page(ws); mark(ws); style_head(ws); day_head(ws)
    build_glossary(wb); build_index(wb); order_sheets(wb); wb.save(xlsx)

def restyle(ws):                                # 舊列也套新版：〔?〕補編號、紅字、照片放大
    ws.column_dimensions['A'].width = max(ws.column_dimensions['A'].width or 0, COL_A)
    for r in range(2, ws.max_row + 1):
        c = ws[f'B{r}']
        if c.value is None: continue
        t = number_q(str(c.value))
        try: c.value = rich(t); c.font = FB
        except Stop: pass
    for img in ws._images:
        if img.anchor._from.col != 0: continue
        r = img.anchor._from.row + 1; w, h = img_size(img); s = min(IMG_W / w, IMG_H_MAX / h)
        if abs(s - 1) > 0.02: w, h = round(w * s), round(h * s); in_cell(img, r, w, h)
        fit(ws, r, str(ws[f'B{r}'].value or ''), h + 2 * PAD)

def day_head(ws):                               # 表頭顯示本日張數與待確認列數；有待確認的分頁標籤標黃
    n = ws.max_row - 1; p = sum(1 for r in range(2, ws.max_row + 1) if qcount(ws[f'B{r}'].value))
    ws['B1'] = f'照片文字（{n} 張｜待確認 {p} 列）'
    ws.sheet_properties.tabColor = TAB_PEND if p else (TAB_UNK if ws.title == UNK else None)

def build_index(wb):                            # 清單：依分頁、列號排序；待確認的列黃底；「前往」可點擊跳到該列
    ix = index_sheet(wb)
    rows = [list(r) + [None] * (8 - len(r)) for r in ix.iter_rows(min_row=2, max_col=8, values_only=True) if any(v is not None for v in r)]
    for r in rows:                              # 以分頁上的實際內容為準
        if r[7] in wb.sheetnames and isinstance(r[0], int):
            v = str(wb[r[7]][f'B{r[0]}'].value or '')
            r[3], r[4], r[5], r[6] = field(v, '查驗時間'), field(v, '照片日期'), field(v, '查驗項目'), qcount(v)
    rows.sort(key=lambda r: ('9999' if r[7] in (UNK, None) else str(r[7]), r[0] if isinstance(r[0], int) else 0))
    if ix.max_row > 1: ix.delete_rows(2, ix.max_row)
    head = ['列號', '原檔名', 'SHA-256', '查驗時間', '照片日期', '查驗項目', '待確認', '分頁', '前往']
    for i, h in enumerate(head, 1):
        c = ix.cell(1, i, h); c.font = FB; c.fill = HEADFILL; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center')
    for col, w in zip('ABCDEFGHI', [6, 18, 12, 22, 12, 26, 8, 12, 20]): ix.column_dimensions[col].width = w
    for i, r in enumerate(rows, 2):
        for j, v in enumerate(r[:8], 1): ix.cell(i, j, v).border = BOX
        c = ix.cell(i, 9)
        if r[7] in wb.sheetnames and isinstance(r[0], int):
            c.value = f'{r[7]} 第 {r[0]} 列 →'; c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{r[7]}'!A{r[0]}")
            c.font = Font(name='Arial', size=11, color=LINK, underline='single')
        c.border = BOX
        for j in range(1, 10): ix.cell(i, j).fill = PENDING if r[6] else NOFILL
    ix.freeze_panes = 'A2'; ix.auto_filter.ref = f'A1:I{max(ix.max_row, 2)}'

def parse(path):
    out = {}
    for ln in open(path, encoding='utf-8'):
        if '：' in ln:
            k, v = ln.split('：', 1); out[k.strip()] = v.strip()
    return out

def update_index(wb, s, row, text, sha=None, name=None):   # 清單：一列一張照片，方便百張時快速瀏覽與去重
    ix = index_sheet(wb)
    vals = [row, name, sha, field(text, '查驗時間'), field(text, '照片日期'), field(text, '查驗項目'), qcount(text), s]
    for r in range(2, ix.max_row + 1):
        if ix.cell(r, 1).value == row and (ix.cell(r, 8).value or LEGACY) == s:
            for i, v in enumerate(vals, 1):
                if v is not None: ix.cell(r, i, v)
            return
    ix.append(vals)

def known_hashes(xlsx):
    if not os.path.exists(xlsx): return {}
    wb = load_workbook(xlsx, read_only=True)
    if INDEX not in wb.sheetnames: return {}
    return {r[2]: r[0] for r in wb[INDEX].iter_rows(min_row=2, values_only=True) if r and r[2]}

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def exif_time(im):
    ex = im.getexif()
    v = ex.get_ifd(0x8769).get(36867) or ex.get(306)
    try:
        return datetime.datetime.strptime(str(v).strip(), '%Y:%m:%d %H:%M:%S') if v else None
    except ValueError:
        return None

def shrink(im, longest):
    s = longest / max(im.size)
    return im.resize((round(im.width * s), round(im.height * s)), PILImage.LANCZOS) if s < 1 else im

# ---------- 批次準備 ----------
def prep(src, xlsx, mpath='manifest.csv'):
    files = []
    if src.lower().endswith('.zip'):            # 解壓到獨立資料夾，只取圖片檔名，不照壓縮檔裡的路徑
        dest = os.path.join('incoming', os.path.splitext(os.path.basename(src))[0]); os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                b = os.path.basename(n)
                if b and b.lower().endswith(EXTS) and not b.startswith('._'):
                    p = os.path.join(dest, b)
                    with z.open(n) as fi, open(p, 'wb') as fo: fo.write(fi.read())
                    files.append(p)
    else:
        files = [os.path.join(src, n) for n in sorted(os.listdir(src)) if n.lower().endswith(EXTS)]
    rows = list(csv.DictReader(open(mpath, encoding='utf-8'))) if os.path.exists(mpath) else []
    seen = known_hashes(xlsx); seen.update({r['sha256']: r['nnn'] for r in rows})
    os.makedirs('photos', exist_ok=True)
    nxt = max([int(r['nnn']) for r in rows] + [int(n[:3]) for n in os.listdir('photos') if n[:3].isdigit()] + [0]) + 1
    new, dup, bad = [], [], []
    for p in files:
        h = sha256(p)
        if h in seen: dup.append(os.path.basename(p)); continue
        try:
            im = PILImage.open(p); t = exif_time(im); im = ImageOps.exif_transpose(im).convert('RGB')
        except Exception as e:
            bad.append(f'{os.path.basename(p)}（{e.__class__.__name__}）'); continue
        seen[h] = 'new'; new.append((t or datetime.datetime.max, os.path.basename(p), h, t, im))
    new.sort(key=lambda x: (x[0], x[1]))       # 依拍攝時間排序，沒有 EXIF 的排最後
    for _, name, h, t, im in new:
        nnn = f'{nxt:03d}'; nxt += 1
        shrink(im, READ_MAX).save(f'photos/{nnn}.jpg', quality=90)
        shrink(im, XL_MAX).save(f'photos/{nnn}_xl.jpg', quality=XL_Q, optimize=True)
        grid(f'photos/{nnn}.jpg', f'photos/{nnn}_grid.jpg')
        os.makedirs('text', exist_ok=True)              # 抄寫範本：照片日期已填，其餘待填
        open(f'text/{nnn}.tpl', 'w', encoding='utf-8').write(
            f"查驗時間：\n照片日期：{t.strftime('%Y-%m-%d') if t else 'UNKNOWN'}\n查驗項目：\n位置：\n檢查人員：\n查驗說明：\n")
        rows.append(dict(nnn=nnn, 原檔名=name, sha256=h, exif時間=t.isoformat(' ') if t else '',
                         照片日期=t.strftime('%Y-%m-%d') if t else 'UNKNOWN', 狀態='todo', 列號=''))
    with open(mpath, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=MF); w.writeheader(); w.writerows(rows)
    noexif = sum(1 for *_, t, _ in new if t is None)
    print(f'OK 新增 {len(new)} 張（無 EXIF 日期 {noexif}）｜重複略過 {len(dup)}｜無法開啟 {len(bad)}｜待抄寫 {sum(r["狀態"]=="todo" for r in rows)}')
    if dup: print('重複：' + '、'.join(dup))
    if bad: print('無法開啟：' + '、'.join(bad))

# ---------- 寫入 ----------
def open_book(xlsx):
    if os.path.exists(xlsx): return load(xlsx)
    return Workbook()                           # 預設空白頁在開第一個日分頁時拿掉

def add_one(wb, img_path, text, fixed=None, sha=None, name=None):
    if sha:
        ix = index_sheet(wb)
        for r in ix.iter_rows(min_row=2, values_only=True):
            if r[2] == sha: raise Stop(5, f'照片重複（已在 {r[7] if len(r) > 7 and r[7] else LEGACY} 第 {r[0]} 列）')
    text = number_q(flag_dates(text)); value = rich(text) # 先檢查格式，失敗就不動檔案
    if fixed:
        base = sheet(wb, BASE, ['欄位', '值'], [12, 50])
        known = {r[0]: r[1] for r in base.iter_rows(min_row=2, values_only=True) if r[0]}
        diff = [f'{k}：基準「{known[k]}」／本張「{v}」' for k, v in fixed.items() if k in known and known[k] != v]
        if diff: raise Stop(2, '固定欄位與基準不同：' + '；'.join(diff))
        for k, v in fixed.items():
            if k not in known: base.append([k, v])
    ws = day_sheet(wb, day_of(text)); row = ws.max_row + 1
    w, h = PILImage.open(img_path).size
    s = min(IMG_W / w, IMG_H_MAX / h)
    img = XLImage(img_path); img.width, img.height = round(w * s), round(h * s)
    in_cell(img, row, img.width, img.height); ws.add_image(img)
    c = ws[f'B{row}']; c.value = value; c.font = FB; c.border = BOX   # 儲存格字型設粗體：預覽忽略第一段格式時第一行仍是粗體
    c.alignment = Alignment(wrap_text=True, vertical='top'); ws[f'A{row}'].border = BOX
    fit(ws, row, text, img.height + 2 * PAD)
    update_index(wb, ws.title, row, text, sha, name)
    return ws.title, row

def add(xlsx, img_path, txt_path, fixed_path=None, sha=None, name=None):
    wb = open_book(xlsx)
    text = open(txt_path, encoding='utf-8').read().strip()
    try:
        s, row = add_one(wb, img_path, text, parse(fixed_path) if fixed_path else None, sha, name)
    except Stop as e:
        print(f'STOP {e.msg}，未寫入'); sys.exit(e.code)
    finish(wb, xlsx)
    print(f'OK {s} 第 {row} 列：{os.path.basename(img_path)}；待確認 {qcount(text)} 處')

def addmany(xlsx, mpath='manifest.csv'):        # 百張批次：一次載入、一次存檔
    rows = list(csv.DictReader(open(mpath, encoding='utf-8')))
    wb = open_book(xlsx)
    done, skip, waiting = [], [], 0
    for r in rows:
        if r['狀態'] != 'todo': continue
        t = f"text/{r['nnn']}.txt"
        if not os.path.exists(t): waiting += 1; continue
        fx = f"fixed/{r['nnn']}.txt"
        text = open(t, encoding='utf-8').read().strip()
        try:
            s, n = add_one(wb, f"photos/{r['nnn']}_xl.jpg", text, parse(fx) if os.path.exists(fx) else None, r['sha256'], r['原檔名'])
            r['狀態'], r['列號'] = 'done', f'{s}:{n}'; done.append((s, n, qcount(text)))
        except Stop as e:
            r['狀態'] = f'stop{e.code}'; skip.append(f"{r['nnn']}（{e.msg}）")
    if wb.sheetnames: finish(wb, xlsx)
    with open(mpath, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=MF); w.writeheader(); w.writerows(rows)
    per = {}
    for s, n, _ in done: per.setdefault(s, []).append(n)
    rng = '、'.join(f'{s} 第 {min(v)}～{max(v)} 列' if len(v) > 1 else f'{s} 第 {v[0]} 列' for s, v in sorted(per.items())) or '無'
    print(f'OK 寫入 {len(done)} 張（{rng}，含待確認 {sum(1 for *_, q in done if q)} 列）｜未寫入 {len(skip)}｜尚未抄寫 {waiting}')
    for s in skip: print('未寫入：' + s)

def fix(xlsx, spec, old, new, source='使用者'):
    wb = load(xlsx)
    try: ws, row = locate(wb, spec)
    except Stop as e: print(f'STOP {e.msg}，未寫入'); sys.exit(e.code)
    c = ws[f'B{row}']; v = str(c.value or '')
    n = v.count(old)
    if n != 1:
        print(f'STOP {ws.title} 第 {row} 列找到 {n} 處「{old}」，未寫入'); sys.exit(3)
    t = number_q(flag_dates(v.replace(old, new)))
    try: c.value = rich(t)
    except Stop as e: print(f'STOP {e.msg}，未寫入'); sys.exit(e.code)
    c.font = FB; fit(ws, row, t); update_index(wb, ws.title, row, t)
    vocab_sheet(wb).append([old, new, f'{ws.title}:{row}', datetime.date.today().isoformat(), source])
    was = f'{ws.title} 第 {row} 列'; ws, row = relocate(wb, ws, row)
    finish(wb, xlsx)
    moved = '' if was == f'{ws.title} 第 {row} 列' else f'（日期改了，已從 {was} 搬到這裡）'
    print(f'OK {ws.title} 第 {row} 列已更新{moved}；本列還有 {qcount(t)} 處待確認')

def vocab_sheet(wb):
    return sheet(wb, VOCAB, ['白板原文（待確認）', '確認後', '來源位置', '確認日期', '來源'], [32, 32, 14, 12, 30])

def vocab(xlsx, raw, ok, source):
    wb = load(xlsx); vocab_sheet(wb).append([raw, ok, None, datetime.date.today().isoformat(), source]); finish(wb, xlsx)
    print(f'OK 已記錄：{raw}→{ok}（{source}）')

def set_text(xlsx, spec, txt_path):
    t = number_q(flag_dates(open(txt_path, encoding='utf-8').read().strip()))
    wb = load(xlsx)
    try: ws, row = locate(wb, spec); val = rich(t)
    except Stop as e: print(f'STOP {e.msg}，未寫入'); sys.exit(e.code)
    c = ws[f'B{row}']; c.value = val
    c.font = FB; fit(ws, row, t); update_index(wb, ws.title, row, t)
    was = f'{ws.title} 第 {row} 列'; ws, row = relocate(wb, ws, row)
    finish(wb, xlsx)
    moved = '' if was == f'{ws.title} 第 {row} 列' else f'（日期改了，已從 {was} 搬到這裡）'
    print(f'OK {ws.title} 第 {row} 列已改寫{moved}；待確認 {qcount(t)} 處')

ROWS = {}                                       # 每個詞出現在哪些位置（同一張白板上的兩個詞一定是不同物件）
def build_glossary(wb, imported=()):            # 詞庫：從所有分頁自動整理，已寫入的字就是下次抄寫的對照
    terms = {}; ROWS.clear()
    def put(cat, w, pos):
        w = w.strip(' 　、，,）)')
        if not w or QRE.search(w) or w.startswith(('UNKNOWN', '—')): return
        ROWS.setdefault((cat, w), set()).add(pos)
        if (cat, w) in terms: terms[(cat, w)][1] += 1
        else: terms[(cat, w)] = [pos, 1]
    for ws in day_sheets(wb):
        for r in range(2, ws.max_row + 1):
            pos = f'{ws.title}:{r}'
            for ln in str(ws[f'B{r}'].value or '').split('\n'):
                if ln.startswith(HEAD) or ln.startswith('查驗說明'): continue
                if ln.startswith('查驗項目：'): put('查驗項目', ln.split('：', 1)[1], pos); continue
                if ln.startswith('位置：'): put('位置', ln.split('：', 1)[1], pos); continue
                if ln.startswith('檢查人員：'):
                    for w in re.split(r'[、，,\s]+', ln.split('：', 1)[1]):
                        w = re.sub(r'\d+/\d+', '', w)
                        if re.fullmatch(r'[一-鿿]{2,4}', w): put('人名', w, pos)
                    continue
                for m in MODEL.findall(ln): put('型號', m, pos)
                if '：' in ln:
                    k, v = ln.split('：', 1)
                    if k.strip('（(') in ('廠牌', '品牌'): put('廠牌', v, pos)
                    continue
                m = NAME.search(ln)
                if m and not ln.startswith('（'): put('品名用語', m.group(0), pos)
    conf = []                                   # 使用者或型錄確認過的寫法
    if VOCAB in wb.sheetnames:
        for row in wb[VOCAB].iter_rows(min_row=2, values_only=True):
            if row and row[1]: conf.append((str(row[1]), str(row[4] or '使用者')))
    def source(w):
        for txt, src in reversed(conf):
            if w in txt: return '型錄' if src.startswith('http') else '使用者確認'
        return '白板判讀'
    keep = {}
    if GLOSS in wb.sheetnames:                  # 舊詞庫：使用者確認、型錄、匯入的詞保留；白板判讀但已不在任何列的詞丟掉（避免留下讀錯的字）
        for row in wb[GLOSS].iter_rows(min_row=2, values_only=True):
            if row and row[0] in CATS and row[1] and (len(row) > 4 and row[4] in ('使用者確認', '型錄', '匯入')):
                keep[(row[0], str(row[1]))] = row[4]
    for c, w in imported: keep.setdefault((c, w), '匯入')
    out = {k: [p, n, source(k[1])] for k, (p, n) in terms.items()}
    for k, src in keep.items():                 # 已確認的來源不因再次出現而降級
        if k not in out: out[k] = ['', 0, src]
        elif out[k][2] == '白板判讀': out[k][2] = src
    gs = wb[GLOSS] if GLOSS in wb.sheetnames else wb.create_sheet(GLOSS)
    gs.delete_rows(1, gs.max_row + 1); gs.append(['類別', '詞', '首次位置', '出現次數', '來源'])
    for c in gs[1]: c.font = FB
    for col, w in zip('ABCDE', [10, 34, 14, 10, 12]): gs.column_dimensions[col].width = w
    for (c, w), (p, n, src) in sorted(out.items(), key=lambda x: (CATS.index(x[0][0]), x[1][0] or '~', x[0][1])):
        gs.append([c, w, p, n, src])
    return out

def glossary(xlsx, imp=None):                   # 重建詞庫、另存 詞庫.csv；--import 可匯入舊詞庫.csv（換新檔時沿用）
    imported = []
    if imp:
        for row in csv.DictReader(open(imp, encoding='utf-8-sig')):
            if row.get('類別') in CATS and row.get('詞'): imported.append((row['類別'], row['詞']))
    wb = load(xlsx); out = build_glossary(wb, imported); finish(wb, xlsx)
    with open('詞庫.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['類別', '詞', '首次位置', '出現次數', '來源'])
        for (c, t), (p, n, src) in sorted(out.items(), key=lambda x: (CATS.index(x[0][0]), x[1][0] or '~')): w.writerow([c, t, p, n, src])
    for c in CATS:
        ws_ = [t + ('＊' if out[(k, t)][2] != '白板判讀' else '') for (k, t) in out if k == c]
        if ws_: print(f'{c}（{len(ws_)}）：' + '、'.join(ws_))
    print('＊＝使用者確認／型錄／匯入；已存 詞庫.csv')
    import difflib                              # 公共工程同物件重複多：同類別寫法只差一兩字的，列出來核對是否同一物
    sim = []
    for c in ('型號', '品名用語', '人名', '查驗項目', '位置'):
        ws_ = sorted({t for (k, t) in out if k == c})
        for i, x in enumerate(ws_):
            for y in ws_[i + 1:]:
                if ROWS.get((c, x), set()) & ROWS.get((c, y), set()): continue   # 同一張白板並列＝不同物件
                one = len(x) == len(y) >= 3 and sum(p != q for p, q in zip(x, y)) == 1     # 只差一個字（王小明／王小名、V2700／V2701）
                if x != y and abs(len(x) - len(y)) <= 1 and (one or difflib.SequenceMatcher(None, x, y).ratio() >= 0.8) \
                   and not (c == '型號' and re.sub(r'\d', '', x) == re.sub(r'\d', '', y) and len(x) == len(y) and sum(a != b for a, b in zip(x, y)) > 1):
                    sim.append(f'{c}：{x}／{y}')
    print('疑似同物不同寫法：' + ('、'.join(sim) if sim else '無'))

# ---------- 讀回與提問 ----------
def check(xlsx):                                # 讀檔案原狀，不先轉換
    wb = load_workbook(xlsx, rich_text=True)
    if LEGACY in wb.sheetnames: print(f'舊版單頁「{LEGACY}」尚未拆成每日分頁（任何寫入指令或 glossary 會自動拆）')
    days = day_sheets(wb); total = 0
    print(f'分頁 {len(days)} 個：' + '、'.join(ws.title for ws in days) + f'｜檔案 {os.path.getsize(xlsx)/1e6:.1f} MB')
    for ws in days:
        rows = range(2, ws.max_row + 1); total += len(rows)
        imgs = sorted(i.anchor._from.row + 1 for i in ws._images)
        miss = [r for r in rows if r not in imgs]
        loose = [i.anchor._from.row + 1 for i in ws._images if not (isinstance(i.anchor, TwoCellAnchor) and i.anchor.to.row == i.anchor._from.row and i.anchor._from.col == 0)]
        wrong = [r for r in rows if day_of(ws[f'B{r}'].value) != ws.title]
        pend = [r for r in rows if qcount(ws[f'B{r}'].value)]
        print(f'【{ws.title}】資料列 {len(rows)}｜照片 {len(imgs)}｜缺照片列 {miss or "無"}｜未固定在格子裡 {loose or "無"}｜放錯分頁 {wrong or "無"}｜待確認列 {pend or "無"}')
        for r in rows:
            v = str(ws[f'B{r}'].value or '')
            print(f'  第 {r} 列｜{"／".join(v.split(chr(10))[:2])}｜{field(v, "查驗項目")}｜待確認 {qcount(v)}｜UNKNOWN {v.count("UNKNOWN")}')
    n_ix = (wb[INDEX].max_row - 1) if INDEX in wb.sheetnames else 0
    print(f'合計 {total} 列｜清單 {n_ix} 筆' + ('' if n_ix == total else '（不一致）'))

def questions(xlsx):                            # 依回覆樣板輸出，再由 Claude 改寫成一題一行附候選字
    wb = load(xlsx)
    for ws in day_sheets(wb):
        for r in range(2, ws.max_row + 1):
            v = str(ws[f'B{r}'].value or '')
            if not qcount(v): continue
            ls = v.split('\n')
            print(f'**{ws.title}｜第 {r} 列**\n**查驗時間**：{ls[0].split("：",1)[1]}\n**照片日期**：{ls[1].split("：",1)[1]}\n**請確認**：')
            for ln in ls:                       # 題號＝格子裡的〔?N〕號，和放大圖編號一致
                for k in QRE.findall(ln): print(f'{k}. {ln}')
            print()

def grid(img_path, out, step=100):              # 座標格線（判讀用原圖座標），縮成 1200 寬給 Claude 看（省 token）
    im = PILImage.open(img_path).convert('RGB'); d = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=max(14, im.width // 70))
    for x in range(0, im.width, step):
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if x % 500 == 0 else (255, 160, 160), width=1)
        d.text((x + 2, 2), str(x), fill='red', font=font)
    for y in range(0, im.height, step):
        d.line([(0, y), (im.width, y)], fill=(255, 0, 0) if y % 500 == 0 else (255, 160, 160), width=1)
        d.text((2, y + 2), str(y), fill='red', font=font)
    shrink(im, 1200).save(out, quality=85)

def enhance(c):                                 # 白板藍黑筆：紅色通道＋自動對比＋銳化
    return ImageOps.autocontrast(c.split()[0], cutoff=2).filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=2)).convert('RGB')

def crops(img_path, out, boxes):
    im = PILImage.open(img_path).convert('RGB'); font = ImageFont.load_default(size=36); tiles = []
    for i, b in enumerate(boxes, 1):
        lab, _, xy = b.rpartition(':'); lab = lab or str(i)   # 「2:x0,y0,x1,y1」＝圖上標 2，對應〔?2〕
        x0, y0, x1, y1 = map(int, xy.split(','))
        c = im.crop((x0, y0, x1, y1)); s = min(560 / c.width, 180 / c.height)
        c = c.resize((round(c.width * s), round(c.height * s)), PILImage.LANCZOS)
        t = PILImage.new('RGB', (c.width * 2 + 90, c.height + 16), 'white')
        t.paste(c, (60, 8)); t.paste(enhance(c), (c.width + 80, 8))
        ImageDraw.Draw(t).text((12, 8), lab, fill='red', font=font); tiles.append(t)
    W = max(t.width for t in tiles); H = sum(t.height for t in tiles)
    canvas = PILImage.new('RGB', (W, H), 'white'); y = 0
    for t in tiles: canvas.paste(t, (0, y)); y += t.height
    canvas.save(out); print(f'OK {len(tiles)} 處放大圖：{out}')

def load_forms(path='forms.csv'):              # 公司「材料自主檢查表」名詞：放在工作目錄 forms.csv（表號,工作表,材料/設備名稱,項目,品質管理標準）；沒有就不套用
    if not os.path.exists(path): return []
    out = {}
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        k = (r['表號'], r['工作表'], r['材料/設備名稱'])
        out.setdefault(k, []).append((r['項目'], r['品質管理標準']))
    return [(k[1], k[2], v) for k, v in sorted(out.items(), key=lambda x: int(x[0][0]) if x[0][0].isdigit() else 0)]
FORMS = load_forms()

# ---------- 公司格式：材料自主檢查照片（export）----------
# 版面照公司範例：A4 直式，每頁標題「材料自主檢查照片」＋ 3 張照片＋頁碼；每張 14 列：左 A:E 照片；右 F:I 依序
# 分項工程名稱／檢查項目、設計/標準值｜實測值、拍攝時間（民國）、拍攝位置、棟別/層別/空間編號/空間位置。字型標楷體。
# 設計/標準值：查驗項目對得到公司「材料自主檢查表」(FORMS) 就用表上的品質管理標準；對不到用白板的規格欄。實測值：白板的實測欄；白板沒有實測欄就照白板內容。
CO_TITLE, CO_FONT = '材料自主檢查照片', '標楷體'
CO_COLW, CO_ROWH = 9.5, 15.3                    # 9 欄欄寬、列高（點）：一頁 46 列＝標題 3＋照片 14×3＋頁碼 1，A4 放得下
CO_PAGE = 732                                   # 每頁高度上限（點）：A4 841.9 減上下邊界 0.748 吋；46 列×15.3＝703.8，加高的列用剩下的空間
CO_IMG = 900                                    # 匯出照片長邊（像素）
SUB = '分項工程'                                # 照片紀錄.xlsx 裡「查驗項目 → 分項工程名稱」對照（sub 指令填）
ALIAS = {'線槽': '鋁製電纜線架', 'EMT管': 'EMT導線管'}   # 白板寫法 → 自主檢查表的材料/設備名稱；使用者確認後再加
NAMEMAP = {'鋁梯型直式': '直式電纜線架', '水平90°彎頭': '水平90°彎接頭', '水平90°T型': '水平T型彎接頭',   # 白板品名 → 自主檢查表品名（輸出時統一用公司寫法）
           '垂直90°上彎': '90°垂直上升彎接頭', '垂直90°下彎': '90°垂直下降彎接頭'}
LABELED = ('廠牌', '型號', '名稱', '項目名稱', '廠牌/型號', '標稱壓力', '尺寸', '材質', '長度', '數量', '音壓位準等級', '型式認可', '產品規範')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
TOPLEFT = Alignment(horizontal='left', vertical='top', wrap_text=True)

def co_px(pt): return pt * 96 / 72
COLPX = int(CO_COLW * 7 + 5)                    # 欄寬換像素（預設字型 Calibri 11）

def roc(d):                                     # 2026-09-30 → 115年9月30日
    if not DATE.fullmatch(d or ''): return ''
    y, m, dd = map(int, d.split('-')); return f'{y - 1911}年{m}月{dd}日'

def co_item(text):                              # 檢查項目：查驗項目去掉「材料進場」
    it = field(text, '查驗項目').strip()
    for suf in ('材料進場', '進場'):
        if it.endswith(suf) and len(it) > len(suf): return it[:-len(suf)]
    return it

def co_form(item, text):                        # 對到哪一張自主檢查表；同名多張時用白板上的型號、規格數字比對，比不出來就不套
    key = ALIAS.get(item, item)
    cand = [f for f in FORMS if f[1] == key or (len(key) >= 2 and (key in f[1] or f[1] in key))]
    if len(cand) <= 1: return cand[0] if cand else None
    toks = set(re.findall(r'[A-Za-z0-9.]{2,}', text))
    sc = [(len(toks & set(re.findall(r'[A-Za-z0-9.]{2,}', ' '.join(v for _, v in f[2])))), f) for f in cand]
    best = max(s for s, _ in sc); top = [f for s, f in sc if s == best]
    return top[0] if best and len(top) == 1 else None

def form_lines(f):                              # 自主檢查表 → 設計/標準值文字（公司寫法：廠牌:XX、規格只寫值）
    return [f'{k}:{v}'.replace('\n', ' ') if k in LABELED else v.replace('\n', ' ') for k, v in f[2]]

def body(text):                                 # 查驗說明的表頭與內容行
    ls = str(text).split('\n')
    for i, ln in enumerate(ls):
        if ln.startswith('查驗說明'):
            return ln.split('：', 1)[0][4:].strip('（）() '), [l for l in ls[i + 1:] if l.strip()]
    return '', []

def split_dm(head, lines):                      # 白板內容拆成 設計/標準值、實測值 兩欄
    def cols_of(h):
        cs = [c.strip() for c in h.split('｜')]
        return cs, next((i for i, c in enumerate(cs) if '實測' in c), None), next((i for i, c in enumerate(cs) if c == '數量'), None)
    cols, mi, qi = cols_of(head)
    d, m, top = [], [], []
    if mi is not None:                          # 表頭有尺寸代號（W H）就寫進欄頭，數字才看得懂
        dh = ' '.join(c for i, c in enumerate(cols) if i not in (mi, qi) and c != '無標題欄')
        mh = cols[mi].replace('實測', '').strip()
        if re.search(r'[A-Za-z]', dh): d.append(dh)
        if re.search(r'[A-Za-z]', mh): m.append(mh)
    for ln in lines:
        if ln.startswith('（') and '｜' in ln and '實測' in ln:      # 例「（右欄 實測｜數量）」：之後的行換表頭
            cols, mi, qi = cols_of(ln.strip('（）()').replace('右欄', '').strip()); continue
        if '｜' in ln and mi is not None:
            p = [x.strip() for x in ln.split('｜')]
            q = p[qi] if qi is not None and qi < len(p) else ''
            dv = ' '.join(x for i, x in enumerate(p) if i not in (mi, qi) and x)
            mv = p[mi] if mi < len(p) and p[mi] not in ('—', '') else ''
            nm = NAME.match(dv); nm = NAMEMAP.get(nm.group(0), nm.group(0)) if nm else ''
            if dv: d.append(dv + (f'（{q}）' if q else ''))
            ml = ' '.join(x for x in (nm, mv) if x) + (f'（{q}）' if q else '')
            m.append(ml or '—')
        elif '：' in ln and not ln.startswith('（'):
            top.append(ln.replace('：', ':', 1))                    # 例 廠牌：弘晟 → 廠牌:弘晟（兩欄都放最上面）
        else:
            d.append(ln)
            if mi is None: m.append(ln)
    return top + d, top + m

def cw(ch):                                     # 字寬（em）：全形與×°等寬字算 1，半形算 0.62
    import unicodedata
    return 1.0 if unicodedata.east_asian_width(ch) in 'WFA' else 0.62

def disp(s): return sum(cw(ch) for ch in s)

def wrap_n(s, cpl):                             # 模擬自動換行：英數字串不拆開，中文一字一單位
    n, cur = 1, 0.0
    for u in re.findall(r'[!-~]+|\s|.', s):
        uw = disp(u)
        if u.isspace() or cur + uw <= cpl: cur += uw; continue
        n += 1; cur = uw
        while cur > cpl: n += 1; cur -= cpl
    return n

def co_fit(lines, px_w, px_h):                  # 字級 10→7 自動縮到放得下；還放不下回傳需要的高度（像素）
    for sz in (10, 9, 8, 7):                    # 最小 7 點（維持每頁 3 張），再放不下才加高列
        em = sz * 96 / 72; cpl = max(1, (px_w - 10) / em)
        n = sum(wrap_n(l, cpl) for l in lines) or 1
        need = n * em * 1.4 + 10                 # 抓寬一點：Excel 與 LibreOffice 換行位置不同
        if need <= px_h: break
    return sz, need

def co_rich(text, sz):                          # 〔?N〕紅字
    if not WARN.search(text): return text
    a, b, out, i = InlineFont(rFont=CO_FONT, sz=sz), InlineFont(rFont=CO_FONT, sz=sz, color=RED), [], 0
    for mt in WARN.finditer(text):
        if mt.start() > i: out.append(TextBlock(a, text[i:mt.start()]))
        out.append(TextBlock(b, mt.group(0))); i = mt.end()
    if i < len(text): out.append(TextBlock(a, text[i:]))
    return CellRichText(out)

def co_one(text, cols):                         # 單列文字太長就縮字（10→7 點），不跑出格子
    for sz in (10, 9, 8, 7):
        if disp(text) * sz * 96 / 72 <= COLPX * cols - 6: return sz
    return 7

def co_cell(ws, rng, value, sz, align):        # 合併、寫字、整塊加框
    ws.merge_cells(rng); first = rng.split(':')[0]
    c = ws[first]; c.value = co_rich(value, sz) if isinstance(value, str) else value
    c.font = Font(name=CO_FONT, size=sz); c.alignment = align
    for row in ws[rng]:
        for x in row: x.border = BOX

def co_info(text, subs):
    item = co_item(text); f = co_form(item, text)
    head, lines = body(text); d, m = split_dm(head, lines)
    if f:
        nums = lambda x: set(re.findall(r'\d+(?:\.\d+)?', x))
        spec = set().union(*[nums(x) for x in d]) if d else set()
        same = bool(m) and all(nums(x) <= spec for x in m)   # 白板實測都對得上白板規格＝相符
        d = [f[1]] + form_lines(f); item = f[1]
        if same: m = list(d)                    # 公司規則：相符時實測值與設計/標準值同寫
    shot = field(text, '照片日期')[:10]
    if not DATE.fullmatch(shot): shot = field(text, '查驗時間')[:10]
    loc = field(text, '位置').strip()
    return dict(sub=subs.get(field(text, '查驗項目'), ''), item=item, d=d or ['—'], m=m or ['—'], shot=roc(shot),
                area=loc if loc and not loc.startswith(('—', 'UNKNOWN')) else '', form=f[0] + '／' + f[1] if f else '')

def co_heights(info):                           # 14 列的列高；設計/實測放不下就加高那 7 列
    base = co_px(CO_ROWH) * 7
    need = max(co_fit(info['d'], COLPX * 2, base)[1], co_fit(info['m'], COLPX * 2, base)[1], base)
    h = [CO_ROWH] * 14
    for i in range(4, 11): h[i] = max(CO_ROWH, round(need / 7 * 72 / 96, 1))
    return h

def co_block(ws, t, info, data, h):
    for i, v in enumerate(h): ws.row_dimensions[t + i].height = v
    co_cell(ws, f'A{t}:E{t + 13}', None, 11, CENTER)
    co_cell(ws, f'F{t}:I{t + 2}', f"分項工程名稱：{info['sub']}\n檢查項目：{info['item']}", 11, TOPLEFT)
    co_cell(ws, f'F{t + 3}:G{t + 3}', '設計/標準值', 11, CENTER); co_cell(ws, f'H{t + 3}:I{t + 3}', '實測值', 11, CENTER)
    px_h = sum(co_px(x) for x in h[4:11])
    co_cell(ws, f'F{t + 4}:G{t + 10}', '\n'.join(info['d']), co_fit(info['d'], COLPX * 2, px_h)[0], TOPLEFT)
    co_cell(ws, f'H{t + 4}:I{t + 10}', '\n'.join(info['m']), co_fit(info['m'], COLPX * 2, px_h)[0], TOPLEFT)
    for i, x in enumerate([f"拍攝時間：{info['shot']}", '拍攝位置：工區內', '棟別/層別/空間編號/空間位置' + (f"：{info['area']}" if info['area'] else '')]):
        co_cell(ws, f'F{t + 11 + i}:I{t + 11 + i}', x, co_one(x, 4), TOPLEFT)
    if not data: return
    import io
    im = shrink(ImageOps.exif_transpose(PILImage.open(io.BytesIO(data))).convert('RGB'), CO_IMG)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80); buf.seek(0)
    rows = [co_px(x) for x in h]; W, H = COLPX * 5, sum(rows)
    s = min((W - 16) / im.width, (H - 16) / im.height); w, hh = round(im.width * s), round(im.height * s)
    def at(x, y):                               # 區塊內像素位置 → (欄, 欄內位移, 列, 列內位移)
        c = min(int(x // COLPX), 4); r, acc = 0, 0
        while r < 13 and acc + rows[r] <= y: acc += rows[r]; r += 1
        return c, x - c * COLPX, r, y - acc
    x0, y0 = (W - w) / 2, (H - hh) / 2
    c0, ox0, r0, oy0 = at(x0, y0); c1, ox1, r1, oy1 = at(x0 + w, y0 + hh)
    img = XLImage(buf); img.width, img.height = w, hh
    img.anchor = TwoCellAnchor(editAs='twoCell',
        _from=AnchorMarker(col=c0, colOff=pixels_to_EMU(int(ox0)), row=t - 1 + r0, rowOff=pixels_to_EMU(int(oy0))),
        to=AnchorMarker(col=c1, colOff=pixels_to_EMU(int(ox1)), row=t - 1 + r1, rowOff=pixels_to_EMU(int(oy1))))
    ws.add_image(img)

def co_sheet(ws):
    for col in 'ABCDEFGHI': ws.column_dimensions[col].width = CO_COLW
    ws.page_setup.orientation, ws.page_setup.paperSize = 'portrait', 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.7086614173228347
    ws.page_margins.top = ws.page_margins.bottom = 0.7480314960629921

def export(xlsx, out):                          # 照片紀錄.xlsx → 材料自主檢查照片.xlsx（每天一個分頁，版面同公司範例）
    from openpyxl.worksheet.pagebreak import Break
    wb = load(xlsx); ob = Workbook(); ob.remove(ob.active)
    subs = {r[0]: r[1] for r in wb[SUB].iter_rows(min_row=2, values_only=True) if r[0]} if SUB in wb.sheetnames else {}
    report, raw = [], []
    for ds in day_sheets(wb):
        ws = ob.create_sheet(ds.title); co_sheet(ws)
        imgs = {i.anchor._from.row + 1: i for i in ds._images}
        r, page, used = 1, 0, None
        def title(r):
            for i in range(3): ws.row_dimensions[r + i].height = CO_ROWH
            co_cell(ws, f'A{r}:I{r + 2}', CO_TITLE, 14, CENTER); return r + 3
        def foot(r, page):
            ws.row_dimensions[r].height = CO_ROWH
            co_cell(ws, f'A{r}:I{r}', page, 12, CENTER); ws.row_breaks.append(Break(id=r)); return r + 1
        for row in range(2, ds.max_row + 1):
            text = str(ds[f'B{row}'].value or '')
            if not text.strip(): continue
            info = co_info(text, subs); h = co_heights(info)
            if used is None or used + sum(h) + CO_ROWH > CO_PAGE:
                if used is not None: r = foot(r, page)
                page += 1; r = title(r); used = 3 * CO_ROWH
            co_block(ws, r, info, imgs[row]._data() if row in imgs else None, h)
            if qcount(text): ws.sheet_properties.tabColor = TAB_PEND
            raw.append([ds.title, row, ws.title, r, text])
            report.append(f"{ds.title} 第 {row} 列 → {ws.title} 第 {page} 頁｜檢查項目：{info['item']}｜設計/標準值：{'自主檢查表 ' + info['form'] if info['form'] else '白板'}｜分項工程名稱：{info['sub'] or '未填'}｜拍攝時間：{info['shot'] or '未知'}" + ('' if row in imgs else '｜缺照片'))
            r += 14; used += sum(h)
        if used is not None: foot(r, page)
        ws.print_area = f'A1:I{r}'
    keep(wb, ob, raw)
    ob.save(out)
    print(f'OK 匯出 {len(report)} 張到 {out}（分頁：{"、".join(s for s in ob.sheetnames if ob[s].sheet_state == "visible")}）')
    for x in report: print('  ' + x)

RAW = '原文'                                     # 交付檔的隱藏工作表：每張照片的完整抄寫與區塊位置
def keep(wb, ob, raw):                          # 把工作資料存進交付檔（隱藏），下次 restore 用
    ix = {(r[7], r[0]): r for r in wb[INDEX].iter_rows(min_row=2, values_only=True)} if INDEX in wb.sheetnames else {}
    ws = ob.create_sheet(RAW); ws.append(['分頁', '列號', '原檔名', 'SHA-256', '輸出分頁', '區塊起始列', '照片文字'])
    for d, r, s, t, text in raw:
        x = ix.get((d, r)) or [None] * 8
        ws.append([d, r, x[1], x[2], s, t, text])
    for name in (BASE, SUB, VOCAB):
        if name not in wb.sheetnames: continue
        cp = ob.create_sheet(name)
        for row in wb[name].iter_rows(values_only=True): cp.append(list(row))
    for name in (RAW, BASE, SUB, VOCAB):
        if name in ob.sheetnames: ob[name].sheet_state = 'hidden'
    ob.active = 0

def restore(src, xlsx):                         # 公司格式檔 → 工作檔（照片取自各區塊，文字取自「原文」）
    import io
    ob = load_workbook(src, rich_text=True)
    if RAW not in ob.sheetnames: print(f'STOP {src} 沒有「{RAW}」工作表（不是本 Skill 輸出的檔），未還原'); sys.exit(6)
    wb = open_book(xlsx); os.makedirs('photos', exist_ok=True); n = miss = 0
    for name in (BASE, SUB, VOCAB):
        if name in ob.sheetnames:
            ws = sheet(wb, name, [c.value for c in ob[name][1]], [30] * 8)
            have = {tuple(r) for r in ws.iter_rows(min_row=2, values_only=True)}
            for r in ob[name].iter_rows(min_row=2, values_only=True):
                if tuple(r) not in have: ws.append(list(r))
    for d, r, name, sha, s, t, text in ob[RAW].iter_rows(min_row=2, values_only=True):
        if not text: continue
        img = next((i for i in ob[s]._images if t - 1 <= i.anchor._from.row <= t + 12), None) if s in ob.sheetnames else None
        if img is None: miss += 1; continue
        p = f'photos/r{n + miss + 1:03d}.jpg'; open(p, 'wb').write(img._data())
        try: add_one(wb, p, str(text), None, sha, name); n += 1
        except Stop as e: print(f'略過 {d} 第 {r} 列：{e.msg}')
    finish(wb, xlsx)
    print(f'OK 還原 {n} 張到 {xlsx}' + (f'｜缺照片 {miss} 張未還原' if miss else ''))

def sub(xlsx, item, name):                      # 記下「查驗項目 → 分項工程名稱」，export 時填進分項工程名稱
    wb = load(xlsx); ws = sheet(wb, SUB, ['查驗項目', '分項工程名稱'], [30, 30])
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == item: ws.cell(r, 2, name); break
    else: ws.append([item, name])
    finish(wb, xlsx); print(f'OK 分項工程：{item} → {name}')

def terms(out='自主檢查名詞.csv'):              # 列出 forms.csv 的名詞（抄寫、比對型號時對照）
    if not FORMS: print('沒有 forms.csv：公司名詞未載入，設計/標準值改用白板內容'); return
    for s, n, it in FORMS: print(f'{s}｜{n}：' + '、'.join(f'{k}:{v}'.replace('\n', ' ') for k, v in it))
    print(f'共 {len(FORMS)} 張表、{sum(len(i) for _, _, i in FORMS)} 項（來源 forms.csv）')

def opt(a, k):
    return a[a.index(k) + 1] if k in a else None

if __name__ == '__main__':
    a = sys.argv[1:]; cmd = a[0]
    if cmd == 'prep': prep(a[1], a[2])
    elif cmd == 'addmany': addmany(a[1], a[2] if len(a) > 2 else 'manifest.csv')
    elif cmd == 'add': add(a[1], a[2], a[3], opt(a, '--fixed'), opt(a, '--sha'), opt(a, '--name'))
    elif cmd == 'fix': fix(a[1], a[2], a[3], a[4], opt(a, '--source') or '使用者')
    elif cmd == 'vocab': vocab(a[1], a[2], a[3], a[4])
    elif cmd == 'set': set_text(a[1], a[2], a[3])
    elif cmd == 'check': check(a[1])
    elif cmd == 'questions': questions(a[1])
    elif cmd == 'glossary': glossary(a[1], opt(a, '--import'))
    elif cmd == 'grid': grid(a[1], a[2])
    elif cmd == 'crops': crops(a[1], a[2], a[3:])
    elif cmd == 'export':
        # v0.17 起交付一律走 make_entries.py → build_company.py（依範本版面）；本指令的舊版面不再交付
        sys.stderr.write('export 已停用：請改用 make_entries.py + build_company.py（見 SKILL.md 第二節）\n'); sys.exit(7)
    elif cmd == 'sub': sub(a[1], a[2], a[3])
    elif cmd == 'terms': terms(*a[1:2])
    elif cmd == 'restore': restore(a[1], a[2])
