# make_entries.py v0.5｜把 照片紀錄.xlsx（log_photo.py 產生）轉成 entries.json，供 build_company.py 產出公司格式
# 用法：python3 make_entries.py 照片紀錄.xlsx entries.json 照片目錄
# 〔v0.5 起已取代，見下方 v0.5 說明〕只做機械轉換：時間、位置、白板文字原樣放入。分項工程名稱、設計/標準值（材料表對照）、實測值、棟別一律留空，由 Claude 依範本與材料表填入，填不出的保持【待確認】。
# v0.3（2026-11-08，MIKO 決定卡「留空白」）：日期讀不到時 shot 為空字串（v0.2 為【待確認】），Excel 只留「拍攝時間：」標籤。
# v0.4（2026-11-22，13 張驗收照片發現）：design 不再只取前 12 行（舊寫法 [s for s in d["說明"] if s][:12]，15 行的白板最後 3 行沒進 Excel，
#        違反 SKILL.md「內容不截行、不精簡」）；超出的高度由 build_company.py 加高區塊處理。重現測試：scripts/tests/test_make_entries.py。
# v0.5（2026-11-22，13 張驗收獨立稽核 AC3／AC6／AC7 不合格；MIKO「按照公司範例處理」）：照公司範例 A 填（範例A對照與修改方案_20261108.md）：
#        對到材料表（forms.csv，本檔同目錄）時 item＝材料/設備名稱，design＝［工作表名稱］＋品質管理標準（只用 B 欄），白板實測都對得上規格時 measured 同寫；
#        對不到表時檢查項目仍換成材料表名稱（ALIAS，例 EMT管→EMT導線管），設計/實測照白板的「實測」欄拆開（log_photo.split_dm），白板沒有實測欄照白板內容（SKILL.md 公司規則）；
#        同名多張表：先比白板規格字樣重疊最多，平手時選多餘規格最少的那張（範例 A 的 E19→表 10），仍平手不套表；
#        「（意象：…）」只進 design，「（量測讀數：…）」只進 measured（量測照寫自己的讀數，白板實測一併保留，不一致兩個都寫）。
#        分項工程名稱（sub）也可用換過的材料表名稱查（網頁第 3 步依 item 記錄）。
#        v0.4 以前「設計/標準值、實測值一律留空由 Claude 填」的機械轉換說明由本版取代；分項工程名稱、棟別仍不自動推定。
import sys, re, io, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import log_photo as lp
lp.FORMS = lp.load_forms(os.path.join(HERE, 'forms.csv'))   # log_photo 預設讀工作目錄的 forms.csv，在工作目錄外跑會讀不到
from openpyxl import load_workbook
from PIL import Image as PI

def parse(text):
    d = {"時間": "", "日期": "", "項目": "", "位置": "", "說明": []}; sp = False
    for line in (text or "").splitlines():
        s = line.strip()
        if not s: continue
        if s.startswith("查驗時間："): d["時間"] = s.split("：", 1)[1]
        elif s.startswith("照片日期："): d["日期"] = s.split("：", 1)[1]
        elif s.startswith("查驗項目："): d["項目"] = s.split("：", 1)[1]; sp = False
        elif s.startswith("位置："): d["位置"] = s.split("：", 1)[1]; sp = False
        elif s.startswith("檢查人員："): sp = False
        elif s.startswith("查驗說明"): sp = True
        elif sp: d["說明"].append(s)
    return d

def roc(iso):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
    return f"{int(m.group(1)) - 1911}年{int(m.group(2))}月{int(m.group(3))}日" if m else ""

TOK = re.compile(r'[A-Za-z0-9.]{2,}')

def pick_form(item, text):                      # 對到哪一張材料表；回傳 (工作表, 材料/設備名稱, [(項目, 品質管理標準)]) 或 None
    key = lp.ALIAS.get(item, item)
    cand = [f for f in lp.FORMS if f[1] == key or (len(key) >= 2 and (key in f[1] or f[1] in key))]
    if len(cand) <= 1: return cand[0] if cand else None
    toks = set(TOK.findall(text))
    sc = [(len(toks & set(TOK.findall(' '.join(v for _, v in f[2])))), f) for f in cand]
    best = max(x for x, _ in sc)
    if not best: return None
    top = [f for x, f in sc if x == best]
    extra = lambda f: len(set(TOK.findall(' '.join(v for _, v in f[2]))) - toks)
    few = min(extra(f) for f in top); top = [f for f in top if extra(f) == few]
    return top[0] if len(top) == 1 else None

def form_name(item):                            # 材料表上的材料/設備名稱（唯一一個時才換）
    key = lp.ALIAS.get(item, item)
    names = {f[1] for f in lp.FORMS if f[1] == key}
    return names.pop() if len(names) == 1 else item

def fill(text):                                 # 回傳 item, design, measured
    lines = str(text).split('\n')
    scene = [l.strip() for l in lines if l.strip().startswith('（意象：')]
    reads = [l.strip()[len('（量測讀數：'):].removesuffix('）') for l in lines if l.strip().startswith('（量測讀數：')]   # 只去掉外層一個括號
    rest = '\n'.join(l for l in lines if not l.strip().startswith(('（意象：', '（量測讀數：')))
    item = lp.co_item(rest).strip()
    head, body = lp.body(rest); d, m = lp.split_dm(head, body)
    f = pick_form(item, rest)
    if f:
        nums = lambda x: set(re.findall(r'\d+(?:\.\d+)?', x))
        spec = set().union(*[nums(x) for x in d]) if d else set()
        same = bool(m) and all(nums(x) <= spec for x in m)
        d = [f[0]] + lp.form_lines(f); item = f[1]
        if same: m = list(d)
    else:
        item = form_name(item)
    return item, d + scene, m + reads

def main(src, out, photo_dir):
    os.makedirs(photo_dir, exist_ok=True)
    wb = load_workbook(src); entries = []; k = 0; miss = []
    import re as _re
    subs = {r[0]: r[1] for r in wb['分項工程'].iter_rows(min_row=2, values_only=True) if r and r[0]} if '分項工程' in wb.sheetnames else {}
    for ws in wb.worksheets:
        if not (ws.title == '日期未知' or _re.fullmatch(r'\d{4}-\d{2}-\d{2}', ws.title)): continue   # v0.2：只讀每日分頁（v0.1 會把「分項工程」當成照片列）
        imgs = {im.anchor._from.row + 1: im for im in ws._images}
        for r in range(2, ws.max_row + 1):
            t = ws.cell(r, 2).value
            if not t: continue
            d = parse(t); im = imgs.get(r); k += 1; p = ""
            if im is not None:
                p = os.path.join(photo_dir, f"{k:03d}.jpg")
                PI.open(io.BytesIO(im._data())).convert("RGB").save(p, quality=85)
            if not p: miss.append(f'{ws.title} 第 {r} 列')
            item, design, measured = fill(t)
            entries.append({"sec": subs.get(d["項目"], "") or subs.get(d["項目"].replace("材料進場", "").strip(), "") or subs.get(item, ""), "item": item,
                            "design": [s for s in design if s], "measured": [s for s in measured if s],
                            "shot": roc(d["日期"]) if d["日期"] and "UNKNOWN" not in d["日期"] else "",
                            "loc": "工區內", "bldg": "", "photo": p,
                            "_sheet": ws.title, "_row": r})
    json.dump(entries, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if miss: print('STOP 缺照片：' + '、'.join(miss) + '（照片紀錄該列沒有照片，不得交檔）'); sys.exit(8)
    return len(entries)

if __name__ == "__main__":
    print(f"寫入 {main(sys.argv[1], sys.argv[2], sys.argv[3])} 筆 → {sys.argv[2]}")
