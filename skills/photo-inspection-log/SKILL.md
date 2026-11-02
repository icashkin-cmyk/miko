---
name: "photo-inspection-log"
description: "施工查驗照片登記成 Excel：使用者上傳查驗白板照片、或回覆待確認的字要更新紀錄時使用。照片放左欄，右欄前兩行固定查驗時間、照片日期，再寫查驗項目、位置、檢查人員、查驗說明；簡體轉繁體，讀不清附放大圖問使用者。先載入 miko-core。"
---

# photo-inspection-log v0.7｜施工查驗照片登記｜2026-10-31

- 負責：把查驗照片逐張登記進 Excel，一張一列：A 欄照片、B 欄照片文字；使用者確認讀不清的字後更新該列。
- 資料：使用者本輪上傳的照片；使用者上傳的既有紀錄檔（.xlsx）。
- 連接器：無。排程：無。
- 交回：更新後的 .xlsx（SendUserFile）；有讀不清的字時，另交放大對照圖與提問清單。
- 先問使用者：讀不清或無法辨識的字（集中一次問）；固定欄位與基準不同時。
- Excel：使用者指定此流程用 Excel，屬本流程的例外，不擴及其他任務。

## 活頁簿結構
- 「照片紀錄」：A 照片、B 照片文字。表頭粗體灰底。B 欄前兩行固定是查驗時間、照片日期（整行粗體，不加顏色）；其餘每一行冒號前（含冒號，例：查驗項目：、（旁註：）粗體，冒號後一般字。B 欄含〔?〕的列自動標淺黃底，確認完自動清除。
- 「基準」：固定欄位（工程名稱、監造單位、承造單位）。第一次出現的值成為基準，之後每張比對，不同就停下問。
- 「已確認詞彙」：使用者確認過的寫法（白板原文、確認後、來源列、日期）。抄新照片前先查這張表，同樣的字形與詞直接沿用，不再問。

## 回覆格式（使用者指定，2026-10-31，固定不變）
每次回覆都照這個樣板，查驗時間與照片日期固定在最上面：
```
**第 3 列**｜已將「無」填入。
**查驗時間**：2026-10-27（115.10.27）
**照片日期**：2026-10-27
**請確認**：
1. 面盆型號：L331／L334？
2. 排水器最後一字：器／部？
```
- 標題（列號、查驗時間、照片日期、請確認）用粗體。
- 第一行：新增時「第 N 列｜已新增。」；使用者回覆後「第 N 列｜已將「X」填入。」；只提問時「第 N 列」。
- 第二、三行：照抄 B 欄前兩行。
- 「請確認：」之後條列，一題一行，附候選字；沒有待確認就省略這段。
- 提醒（固定欄位不符等）放在最後一行。
- 多列同時有待確認：每列一個區塊，依列號排序。
- 不解釋判斷過程，不另起四段或流程鎖。
- 回覆對應不到哪一題時，只問一行：「「X」是第幾題？」

## B 欄欄位（固定順序，一行一欄位）
```
查驗時間：2026-10-27（115.10.27）
照片日期：2026-10-27
查驗項目：（白板寫「檢查項目」也放這欄）
位置：
檢查人員：
查驗說明：（白板有「品名 型號 數量」欄就照寫在冒號前）
（白板內容逐行照抄，保留原分行、品名、型號、數量；旁註寫成「（旁註：…）」）
```
值的寫法：
- 前兩行固定順序與格式，一目了然：
  - 查驗時間：白板的查驗日期換成西元 YYYY-MM-DD，括號附白板原樣（民國）。
  - 照片日期：浮水印或 EXIF 的日期 YYYY-MM-DD；和查驗時間不同時，行尾加「（≠查驗時間）」。
  - 讀不到只寫 UNKNOWN，不加原因；原因、日期來源寫在回覆。
- 一律繁體字。手寫簡體轉繁體（自动→自動、龙头→龍頭、缝→縫）。
- 讀不清的字：儲存格在該字位置標〔?〕，回覆中集中一次問。不猜字、不補型號。
- 白板整張入鏡但沒有該欄：「—（白板無此欄）」。
- 其他欄位白板被裁切或沒拍到：「UNKNOWN（原因）」。

## ① 問問題
- 必問：無，照片本身就是輸入。
- 預設值：
  - 使用者上傳了既有 .xlsx → 接在它後面（複製一份處理，不改原檔）。
  - 沒上傳 → 本對話已有工作檔就接續；沒有就新建「照片紀錄.xlsx」。
  - 一次多張 → 依上傳順序各一列。
  - 使用者只回一個名字或詞（例：「某某某」「無」）→ 對應到字形與候選最吻合的那一處〔?〕更新，回覆照「回覆格式」樣板。

## ② 解決
1. 檔案：照片複製到工作目錄 photos/NNN.jpg；既有 .xlsx 複製到工作目錄；log_photo.py 寫到工作目錄（全文在下方）。
2. 照片日期：PIL 讀 EXIF DateTimeOriginal → 裁四邊放大找浮水印 → 都沒有標 UNKNOWN。
3. 抄白板：
   - 分區裁切放大：上方欄位、左右兩欄內容、底列人員與日期、旁註。
   - 逐行抄成繁體。能和照片裡包裝盒的印刷型號對照就對照；先查「已確認詞彙」。
   - 查驗時間：民國年加 1911 換西元，用程式算。
4. 讀不清的字，標〔?〕之前先做兩件事：
   - 用 `crops` 放大單獨看那個字（左原圖、右增強：紅色通道＋自動對比＋銳化，藍筆在灰白板上會變成清楚的黑字），依下方「簡體偏旁表」換成繁體偏旁再認。
   - 用工地與建材常用詞對照（例：拖布盆、排水器、龍頭、面盆）。
   - 還是不確定才標〔?〕。
5. 漏字檢查：小字與旁註抄完後，數白板該行的字數和抄寫的字數，對不上就重看。
6. 簡體檢查：用 OpenCC（`pip install --break-system-packages opencc-python-reimplemented`，s2t）掃一遍抄寫結果，只當偵測器，命中的字逐一判斷。
7. 寫入：B 欄文字存 text/NNN.txt，固定欄位存 fixed/NNN.txt（每行「欄位：值」）。
   - 執行 `python3 log_photo.py add 照片紀錄.xlsx photos/NNN.jpg text/NNN.txt --fixed fixed/NNN.txt`。
   - 結束碼 2：固定欄位與基準不同，未寫入，把差異給使用者確認。
   - 結束碼 4：前兩行不是「查驗時間：」「照片日期：」，未寫入，改好 text/NNN.txt 再執行。
8. 提問：
   - 用 `python3 log_photo.py crops photos/NNN.jpg 待確認_照片N.png x0,y0,x1,y1 ...` 把每處讀不清的位置放大、編號（左原圖、右增強），拼成一張圖，用 SendUserFile 交給使用者。
   - 問題照「回覆格式」條列，編號和圖上編號一致，每題一行附候選字（最多 3 個）。
9. 使用者回覆後：
   - 執行 `python3 log_photo.py fix 照片紀錄.xlsx 列號 "原文字（含〔?〕）" "確認後文字"`，同時記進「已確認詞彙」。
   - 結束碼 3：找不到或不只一處，未寫入，改用更長的原文字重試。
   - 同步更新 text/NNN.txt。
   - 自己發現抄錯（不是使用者確認的）：改 text/NNN.txt 後執行 `python3 log_photo.py set 照片紀錄.xlsx 列號 text/NNN.txt`，不記進「已確認詞彙」，並在回覆說明。
10. 讀回：
    - `python3 log_photo.py check 照片紀錄.xlsx`：每列照片、查驗時間／照片日期、待確認數、UNKNOWN 數。
    - 新增列時，再用 LibreOffice 轉 PDF，看新列文字沒被截斷。
11. 交檔：SendUserFile，回覆照「回覆格式」。新對話第一次登記時，加一行提醒：要接續請上傳上次的 .xlsx（已確認詞彙存在檔裡，跟著檔案走）。

簡體偏旁表（手寫常見）：
| 簡體 | 繁體 | 例 |
|---|---|---|
| 纟 | 糸 | 缝→縫 |
| 钅 | 金 | 镀→鍍、铜→銅 |
| 讠 | 言 | 说→說 |
| 门 | 門 | 闸→閘 |
| 贝 | 貝 | 质→質 |
| 车 | 車 | 软→軟 |
| 页 | 頁 | 头→頭 |
| 马 | 馬 | 码→碼 |
| 鱼 | 魚 | 鲜→鮮 |
| 饣 | 食 | 饮→飲 |
| 见 | 見 | 观→觀 |
| 风 | 風 | 风管→風管 |

log_photo.py v0.6（每個新對話先寫到工作目錄）：
```python
# log_photo.py v0.6｜施工查驗照片登記：A 欄照片、B 欄照片文字，一張一列；B 欄前兩行固定為查驗時間、照片日期（整行粗體），其餘每行冒號前粗體
# 用法：
#   python3 log_photo.py add   紀錄.xlsx 照片.jpg 文字.txt [--fixed 固定欄位.txt]
#   python3 log_photo.py fix   紀錄.xlsx 列號 "原文字" "確認後文字"
#   python3 log_photo.py set   紀錄.xlsx 列號 文字.txt   （整格改寫，不記進已確認詞彙）
#   python3 log_photo.py check 紀錄.xlsx
#   python3 log_photo.py crops 照片.jpg 輸出.png x0,y0,x1,y1 [x0,y0,x1,y1 ...]   （左原圖、右增強，編號）
# 結束碼：0 成功；2 固定欄位與基準不同；3 fix 找不到或不只一處；4 前兩行不是「查驗時間：」「照片日期：」（以上都未寫入）
import sys, os, datetime
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageOps, ImageFilter

IMG_W, IMG_H_MAX = 320, 400                     # 照片顯示寬度與高度上限（像素）
LINE = Side(style='thin', color='999999')
BOX = Border(left=LINE, right=LINE, top=LINE, bottom=LINE)
F, FB = Font(name='Arial', size=11), Font(name='Arial', size=11, bold=True)
PENDING, NOFILL = PatternFill('solid', fgColor='FFF2CC'), PatternFill(fill_type=None)
MAIN, BASE, VOCAB, Q = '照片紀錄', '基準', '已確認詞彙', '〔?〕'
HEAD = ('查驗時間：', '照片日期：')            # B 欄固定前兩行
HEADFILL = PatternFill('solid', fgColor='D9D9D9')

def load(xlsx):
    return load_workbook(xlsx, rich_text=True)  # 保留粗體

def rich(text):                                 # 前兩行粗體，其餘一般
    lines = text.split('\n')
    if len(lines) < 2 or not (lines[0].startswith(HEAD[0]) and lines[1].startswith(HEAD[1])):
        print(f'STOP 前兩行必須是「{HEAD[0]}」「{HEAD[1]}」，未寫入'); sys.exit(4)
    TOP = InlineFont(rFont='Arial', sz=11, b=True)                   # 前兩行：整行粗體（不加顏色，部分手機預覽會吃掉帶顏色的粗體）
    LAB = InlineFont(rFont='Arial', sz=11, b=True)                   # 冒號前：粗體
    TXT = InlineFont(rFont='Arial', sz=11)
    segs = []
    for i, ln in enumerate(lines):
        nl = '\n' if i else ''
        if i < 2:
            segs.append((TOP, nl + ln))
        elif '：' in ln:                        # 任何一行冒號前（含冒號）粗體
            k, v = ln.split('：', 1); segs += [(LAB, nl + k + '：'), (TXT, v)]
        else:
            segs.append((TXT, nl + ln))
    out = []                                    # 相鄰同字型合併
    for f, t in segs:
        if not t: continue
        if out and out[-1][0] is f: out[-1] = (f, out[-1][1] + t)
        else: out.append((f, t))
    return CellRichText([TextBlock(f, t) for f, t in out])

def style_head(ws):                             # 表頭：粗體、灰底、置中
    for c in ws[1][:2]:
        c.font = FB; c.fill = HEADFILL; c.border = BOX
        c.alignment = Alignment(horizontal='center', vertical='center')

def sheet(wb, name, head, widths):
    if name in wb.sheetnames:
        return wb[name]
    ws = wb.create_sheet(name); ws.append(head)
    for c in ws[1]: c.font = FB
    for col, w in zip('ABCD', widths): ws.column_dimensions[col].width = w
    return ws

def mark(ws):                                   # B 欄含〔?〕標淺黃底，確認完自動清除
    for r in range(2, ws.max_row + 1):
        c = ws[f'B{r}']
        c.fill = PENDING if Q in str(c.value or '') else NOFILL

def fit(ws, r, text, img_h=0):                  # 中文行高約 17 點
    need = max(img_h * 0.75 + 6, (text.count('\n') + 1) * 17 + 8)
    ws.row_dimensions[r].height = max(need, ws.row_dimensions[r].height or 0)

def parse(path):
    out = {}
    for ln in open(path, encoding='utf-8'):
        if '：' in ln:
            k, v = ln.split('：', 1); out[k.strip()] = v.strip()
    return out

def add(xlsx, img_path, txt_path, fixed_path=None):
    if os.path.exists(xlsx):
        wb = load(xlsx); ws = wb[MAIN] if MAIN in wb.sheetnames else wb.worksheets[0]
        row = ws.max_row + 1
    else:
        wb = Workbook(); ws = wb.active; ws.title = MAIN
        ws['A1'], ws['B1'] = '照片', '照片文字'
        ws.column_dimensions['A'].width, ws.column_dimensions['B'].width = 47, 60
        ws.freeze_panes = 'A2'; row = 2
    if fixed_path:                              # 固定欄位：第一次出現的值成為基準，之後不同就停
        fixed = parse(fixed_path)
        base = sheet(wb, BASE, ['欄位', '值'], [12, 50])
        known = {r[0]: r[1] for r in base.iter_rows(min_row=2, values_only=True) if r[0]}
        diff = [f'{k}：基準「{known[k]}」／本張「{v}」' for k, v in fixed.items() if k in known and known[k] != v]
        if diff:
            print('STOP 固定欄位與基準不同，未寫入：\n' + '\n'.join(diff)); sys.exit(2)
        for k, v in fixed.items():
            if k not in known: base.append([k, v])
    ws.page_setup.orientation = 'landscape'
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    w, h = PILImage.open(img_path).size
    s = min(IMG_W / w, IMG_H_MAX / h)
    img = XLImage(img_path); img.width, img.height = round(w * s), round(h * s)
    ws.add_image(img, f'A{row}')
    text = open(txt_path, encoding='utf-8').read().strip()
    value = rich(text)
    c = ws[f'B{row}']; c.value = value; c.font = FB; c.border = BOX   # 儲存格字型也設粗體：預覽忽略第一段格式時，第一行仍是粗體
    c.alignment = Alignment(wrap_text=True, vertical='top')
    ws[f'A{row}'].border = BOX
    fit(ws, row, text, img.height); mark(ws); style_head(ws); wb.save(xlsx)
    print(f'OK 第 {row} 列：{os.path.basename(img_path)}；待確認 {text.count(Q)} 處')

def fix(xlsx, row, old, new):                   # 使用者確認後更新，並記進已確認詞彙
    row = int(row)
    wb = load(xlsx); ws = wb[MAIN]
    c = ws[f'B{row}']; v = str(c.value or '')
    n = v.count(old)
    if n != 1:
        print(f'STOP 第 {row} 列找到 {n} 處「{old}」，未寫入'); sys.exit(3)
    t = v.replace(old, new); c.value = rich(t); c.font = FB
    fit(ws, row, t)
    sheet(wb, VOCAB, ['白板原文（待確認）', '確認後', '來源列', '確認日期'], [32, 32, 8, 12]).append(
        [old, new, row, datetime.date.today().isoformat()])
    mark(ws); style_head(ws); wb.save(xlsx)
    print(f'OK 第 {row} 列已更新；本列還有 {t.count(Q)} 處待確認')

def set_text(xlsx, row, txt_path):              # 整格改寫（格式調整或自己抄錯），不記進已確認詞彙
    row = int(row); t = open(txt_path, encoding='utf-8').read().strip()
    wb = load(xlsx); ws = wb[MAIN]; c = ws[f'B{row}']; c.value = rich(t); c.font = FB
    fit(ws, row, t); mark(ws); style_head(ws); wb.save(xlsx)
    print(f'OK 第 {row} 列已改寫；待確認 {t.count(Q)} 處')

def check(xlsx):                                # 唯讀：每列照片、待確認、UNKNOWN 數
    wb = load(xlsx); ws = wb[MAIN]
    imgs = sorted(i.anchor._from.row + 1 for i in ws._images)
    print(f'資料列 {ws.max_row - 1}；照片所在列 {imgs}')
    for r in range(2, ws.max_row + 1):
        v = str(ws[f'B{r}'].value or '')
        top = '／'.join(v.split('\n')[:2])
        print(f'第 {r} 列：照片{"有" if r in imgs else "無"}｜{top}｜待確認 {v.count(Q)}｜UNKNOWN {v.count("UNKNOWN")}')
    if VOCAB in wb.sheetnames:
        print('已確認詞彙：' + '；'.join(f'{a}→{b}' for a, b, *_ in wb[VOCAB].iter_rows(min_row=2, values_only=True)))

def enhance(c):                                 # 白板藍黑筆：取紅色通道（筆跡最暗）＋自動對比＋銳化
    r = c.split()[0]
    return ImageOps.autocontrast(r, cutoff=2).filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=2)).convert('RGB')

def crops(img_path, out, boxes):                # 讀不清的位置放大、編號，左原圖右增強，拼成一張
    im = PILImage.open(img_path).convert('RGB'); font = ImageFont.load_default(size=36); tiles = []
    for i, b in enumerate(boxes, 1):
        x0, y0, x1, y1 = map(int, b.split(','))
        c = im.crop((x0, y0, x1, y1)); s = min(560 / c.width, 180 / c.height)
        c = c.resize((round(c.width * s), round(c.height * s)), PILImage.LANCZOS)
        t = PILImage.new('RGB', (c.width * 2 + 90, c.height + 16), 'white')
        t.paste(c, (60, 8)); t.paste(enhance(c), (c.width + 80, 8))
        ImageDraw.Draw(t).text((12, 8), str(i), fill='red', font=font); tiles.append(t)
    W = max(t.width for t in tiles); H = sum(t.height for t in tiles)
    canvas = PILImage.new('RGB', (W, H), 'white'); y = 0
    for t in tiles: canvas.paste(t, (0, y)); y += t.height
    canvas.save(out); print(f'OK {len(tiles)} 處放大圖：{out}')

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'add':
        add(a[1], a[2], a[3], a[a.index('--fixed') + 1] if '--fixed' in a else None)
    elif a[0] == 'fix':
        fix(*a[1:5])
    elif a[0] == 'set':
        set_text(*a[1:4])
    elif a[0] == 'check':
        check(a[1])
    elif a[0] == 'crops':
        crops(a[1], a[2], a[3:])
```

## ③ 後設（常見錯誤）
- 藍筆在灰白板、反光或陰影下對比低：一律先看增強圖再判斷（例：L33? 的尾字在增強圖才看出像 4）。
- 簡體偏旁寫得潦草時最難認（例：纟寫成一筆鋸齒，沒認出「縫」）：先放大、查偏旁表，還是不確定才問。
- 小字與旁註容易漏字（例：漏抄「塞」）：抄完逐行數字數。
- 手寫型號容易混淆的字：1／7、0／D、5／S、2／Z、V／1/。要和照片裡包裝盒上的印刷型號對得上才算確定，否則標〔?〕。
- 數量和型號尾碼黏在一起（例：LF6450N 6）：看同欄其他數量的對齊位置，仍不確定就問。
- 照常用詞自動補字（例：把像「部」的字寫成「器」）：字形和常用詞不一致時標〔?〕問，不自己補。
- 浮水印時間是相機設定的時間，不保證正確；和查驗時間不同時兩個都寫（照片日期行加「（≠查驗時間）」），不自行判斷哪個對。
- 聊天上傳常去掉 EXIF；讀不到不代表照片沒有拍攝時間。
- OpenCC 會誤報：斗→鬥、台→臺；冲要看上下文，是沖水的「沖」還是衝擊的「衝」。只當偵測器，不自動替換。
- 新對話時工作檔不在：沒上傳上次的 .xlsx 就會新建一份，已確認詞彙也會跟著遺失。
- 日期格式不一（標籤不同、括號附註過長）：前兩行只放日期，附註寫在回覆。
- 帶顏色的粗體在部分手機預覽不顯示（2026-11-01 查驗時間行看不到粗體）：前兩行只用粗體不加顏色，儲存格字型也設粗體。
- 部分手機預覽不顯示同一格內的部分粗體：使用者說看不到粗體時，先問用哪個 App 開檔，再決定是否改版面。
- 回覆太長或格式不固定：一律照樣板（列號行、查驗時間、照片日期、題目），不解釋怎麼判斷、不重述已知事項。

## ④ 檢查
- AC-1：新列 A 欄有照片，B 欄依固定順序 6 個欄位齊全（沒有值也有標記）；前兩行是查驗時間、照片日期，整行粗體，日期為 YYYY-MM-DD 或 UNKNOWN；其餘每行冒號前粗體；表頭粗體灰底。
- AC-2：check 讀回，既有列的照片數與文字不變。
- AC-3：民國換西元用程式算；照片日期和查驗時間不同時，照片日期行尾有「（≠查驗時間）」。
- AC-4：B 欄全為繁體（OpenCC 命中逐字判過）；每個〔?〕都有附放大圖的提問；含〔?〕的列是黃底，沒有〔?〕的列不是。
- AC-5：fix 只改一處，並記進已確認詞彙；找不到時結束碼 3、檔案不變；固定欄位不符時結束碼 2、前兩行格式不符時結束碼 4，檔案都不變（SHA-256 前後相同）。
- AC-6：使用者上傳的原檔沒被覆寫；PDF 預覽新列文字沒被截斷。
- AC-7：每次回覆照樣板：第一行列號，第二、三行查驗時間與照片日期，再條列題目（一題一行），標題粗體；不解釋判斷過程。
- 實跑題：上傳一張有浮水印日期、民國查驗日期、整張入鏡的白板照，再回覆一個待確認字。通過條件：AC-1～AC-7 全過，回覆的字更新到正確那一處，並出現在已確認詞彙。（2026-10-31 以衛生設備材料進場照片、回覆「某某某」「無」「6是數量」實跑通過；v0.5 格式與增強圖同日實跑；v0.6 冒號前粗體 2026-11-01 實跑；v0.7 拿掉顏色後使用者確認粗體可見）