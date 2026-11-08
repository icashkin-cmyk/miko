# make_entries.py v0.3｜把 照片紀錄.xlsx（log_photo.py 產生）轉成 entries.json，供 build_company.py 產出公司格式
# 用法：python3 make_entries.py 照片紀錄.xlsx entries.json 照片目錄
# 只做機械轉換：時間、位置、白板文字原樣放入。分項工程名稱、設計/標準值（材料表對照）、實測值、棟別一律留空，由 Claude 依範本與材料表填入，填不出的保持【待確認】。
# v0.3（2026-11-08，MIKO 決定卡「留空白」）：日期讀不到時 shot 為空字串（v0.2 為【待確認】），Excel 只留「拍攝時間：」標籤。
import sys, re, io, os, json
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
            entries.append({"sec": subs.get(d["項目"], "") or subs.get(d["項目"].replace("材料進場", "").strip(), ""), "item": d["項目"].replace("材料進場", "").strip(),
                            "design": [s for s in d["說明"] if s][:12], "measured": [],
                            "shot": roc(d["日期"]) if d["日期"] and "UNKNOWN" not in d["日期"] else "",
                            "loc": "工區內", "bldg": "", "photo": p,
                            "_sheet": ws.title, "_row": r})
    json.dump(entries, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if miss: print('STOP 缺照片：' + '、'.join(miss) + '（照片紀錄該列沒有照片，不得交檔）'); sys.exit(8)
    return len(entries)

if __name__ == "__main__":
    print(f"寫入 {main(sys.argv[1], sys.argv[2], sys.argv[3])} 筆 → {sys.argv[2]}")
