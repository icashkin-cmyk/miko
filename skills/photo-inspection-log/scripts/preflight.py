# preflight.py v0.1｜防呆：每個對話開工前與交檔前執行；任一項 FAIL 就停止，不得交檔
# 用法：
#   python3 scripts/preflight.py start                     開工檢查（整包是否齊全、範本是否正確）
#   python3 scripts/preflight.py deliver 材料自主檢查照片.xlsx entries.json   交檔前檢查（版面、筆數、頁數、照片數）
import sys, os, json, csv, math
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ["log_photo.py", "build_company.py", "make_entries.py", "forms.csv", "材料自主檢查照片_範本.xlsx"]
MATERIAL_SHEETS = ["電線電纜", "鋁製電纜線架", "不銹鋼保溫管", "PVC管", "EMT管", "消防管", "變壓器", "配電盤", "泵浦", "閥類"]
results = []

def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"｜{detail}" if detail else ""))

def start():
    for f in REQUIRED:
        check(f"整包檔案 {f}", os.path.exists(os.path.join(HERE, f)))
    tpl = os.path.join(HERE, "材料自主檢查照片_範本.xlsx")
    if os.path.exists(tpl):
        wb = load_workbook(tpl)
        check("範本分頁「範本」存在", "範本" in wb.sheetnames)
        missing = [s for s in MATERIAL_SHEETS if s not in wb.sheetnames]
        check("材料表 10 個分頁齊全", not missing, f"缺：{missing}" if missing else "")
        if "範本" in wb.sheetnames:
            ws = wb["範本"]
            check("範本版面 A1 標題", ws["A1"].value == "材料自主檢查照片")
            formulas = [c.coordinate for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
            check("範本無公式殘留（防止區塊互相連動）", not formulas, f"殘留：{formulas}" if formulas else "")
            check("範本 F4 分項欄有標示", str(ws.cell(4, 6).value or "").startswith("分項工程名稱"))
            check("範本頁碼列 A46", str(ws["A46"].value) == "1")
    fc = os.path.join(HERE, "forms.csv")
    if os.path.exists(fc):
        rows = list(csv.reader(open(fc, encoding="utf-8")))
        check("forms.csv 名詞列數 ≥ 130", len(rows) - 1 >= 130, f"{len(rows) - 1} 列")
    lp = os.path.join(HERE, "log_photo.py")
    if os.path.exists(lp):
        check("log_photo.py 舊 export 已停用", "export 已停用" in open(lp, encoding="utf-8").read())
    print("開工結果：" + ("全部 PASS，可以開始" if all(results) else "有 FAIL，停止並請使用者上傳整包 zip"))

def deliver(xlsx, entries_path):
    entries = json.load(open(entries_path, encoding="utf-8"))
    n = len(entries)
    wb = load_workbook(xlsx); ws = wb.active
    pages = math.ceil(n / 3)
    check("只有一個分頁", len(wb.sheetnames) == 1, str(wb.sheetnames))
    check("頁數 = ceil(筆數/3)", ws.max_row >= pages * 46 - 1 and ws.max_row <= pages * 46 + 1, f"筆數 {n}、頁數 {pages}、列數 {ws.max_row}")
    check("照片數 = 有圖的筆數", len(ws._images) == sum(1 for e in entries if e.get("photo") and os.path.exists(e["photo"])), f"圖 {len(ws._images)}")
    for p in range(pages):
        check(f"第 {p + 1} 頁頁碼", str(ws.cell(p * 46 + 46, 1).value) == str(p + 1))
    unresolved = [e for e in entries if "【待確認】" in str(e.get("sec", "")) or not e.get("sec")]
    print(f"待確認分項：{len(unresolved)} 筆（交檔時須在回覆列出）")
    print("交檔結果：" + ("全部 PASS，可以交檔" if all(results) else "有 FAIL，不得交檔"))

if __name__ == "__main__":
    if sys.argv[1] == "start": start()
    elif sys.argv[1] == "deliver": deliver(sys.argv[2], sys.argv[3])
