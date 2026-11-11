# flowlock_check.py｜流程鎖（正式名稱：回覆結尾的證據標籤計數檢核）三數與行內標籤數的程式核算（1.2.64，ADR-087；只用標準函式庫）
# 起因：1.2.63 冷啟動 T59／T60 六份作答中五份流程鎖三數與可數行內標籤不符（判分方手數；總召專案檔判分_T59_T60_1263.md），
#   同類錯誤重複出現，依 miko-core §4「重複錯誤回到規則」（P-19a）先試程式檢查。
# 用法：python3 -I -B flowlock_check.py <回覆檔.md> [...]；判分、稽核、冷啟動回歸時用，對話中的回覆不在 repo 裡，check_repo 攔不到（只能靠本工具與測題）。
# 不要用本工具的回覆（先由人判斷，再決定要不要跑；工具不自己判「不適用」，1.2.64 稽核第三輪起）：
#   停止回覆（§5 第 5 點不寫流程鎖）；領域 Skill 另定不寫流程鎖的回覆（§5 第 7 點，例如 photo-inspection-log）；
#   標籤照 §5 第 5 點寫在交付檔時，改對交付檔跑。對這些回覆跑本工具會判 FAIL「沒有流程鎖行」或計數不符，不代表違規。
# 算法（miko-core §5 第 1、2、5、8 點）：
#   1. 最後一個非空行要以「流程鎖：」開頭（前後的 ** 粗體記號先去掉）；解析「通過 N 項／降級 N 項／UNKNOWN N 項」。沒有就 FAIL。
#   2. 結尾段＝流程鎖行往上、到第一個空行為止的連續非空行。結尾段裡，以「降級」或「UNKNOWN」開頭（前面可有 -、*、>、編號）的行是
#      重述清單的標題行；標題行之後、同在結尾段內、以 -、*、編號開頭的子項目行也算重述；以「任務四態」開頭的行略過。
#      重述行與流程鎖行（括號內）的標籤不計數（§5 第 5 點允許降級與 UNKNOWN 寫在括號裡或流程鎖之前；第 8 點任務四態寫在流程鎖之前）。
#   3. 其餘行去掉 ``` 程式碼區塊後計數：通過＝【來源：…】【工具：…】【使用者…】【常識…】；降級＝【推論…】【未查證…】；UNKNOWN＝【UNKNOWN…】；
#      【流程】【輸出】【檢核】【限制】【處置】是規則類型標籤，不計數。標籤後可帶補充（例：【推論，只加句不刪】），照前綴分類。
#      ``` 沒有閉合就 FAIL（不猜後面算不算程式碼）。
#   4. 三數各自相符才 PASS（不只比總數）。
# 已知限制（判 FAIL 或 PASS 都要人再看的情形）：只核計數與位置，不核「來源真的支持這句」（§5 第 5 點另查三件）；一個檔只當一則回覆；
#   結尾段裡以「降級：」「UNKNOWN：」開頭的真實主張也會被當成重述、不計數（可能假 PASS；這種寫法本身易混，判分時人工看結尾段）；
#   正文引述規則時提到的標籤名（例：「要標【推論】」）、行內程式碼（`…`）裡的標籤都會被計數；
#   流程鎖行同一行括號外續寫的內容與標籤不計數；
#   標籤寫法不照 §5 第 2 點（例：【使用者提供】【工具 wc】）不計數；
#   流程鎖行前有「>」「- 」「## 」、用半形冒號或半形斜線、括號跨行都判 FAIL（偏嚴，改人工核）。
# 結束碼：0 全部相符；1 有不符、沒有流程鎖行或程式碼區塊沒閉合；2 參數錯或讀不到檔
import re, sys, pathlib
LOCK = re.compile(r'^流程鎖：通過\s*(\d+)\s*項／降級\s*(\d+)\s*項／UNKNOWN\s*(\d+)\s*項')
TAG = re.compile(r'【(來源|工具)[：:][^】]*】|【(使用者|常識|推論|未查證|UNKNOWN)(?:[，,：:、（(][^】]*)?】')
KIND = {'來源': 0, '工具': 0, '使用者': 0, '常識': 0, '推論': 1, '未查證': 1, 'UNKNOWN': 2}
HEAD = re.compile(r'^[\s>*\-]*(?:\d+[.、)）]\s*)?(降級|UNKNOWN)')
SUB = re.compile(r'^\s*(?:[-*]|\d+[.、)）])\s')
STATE = re.compile(r'^[\s>*\-]*任務四態')

def check(text):
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return False, '空檔'
    last = lines[-1].strip().strip('*').strip()
    m = LOCK.match(last)
    if not m:
        anywhere = [i + 1 for i, l in enumerate(lines) if l.strip().strip('*').strip().startswith('流程鎖：')]
        return False, (f'流程鎖不在最後一行（出現在第 {anywhere} 行）' if anywhere else '沒有流程鎖行')
    said = tuple(int(x) for x in m.groups())
    k = len(lines) - 1
    while k > 0 and lines[k - 1].strip():
        k -= 1
    skip, in_list = set(), False
    for i in range(k, len(lines) - 1):
        l = lines[i]
        if HEAD.match(l):
            skip.add(i); in_list = True
        elif in_list and SUB.match(l):
            skip.add(i)
        elif STATE.match(l):
            in_list = False
        else:
            in_list = False
    body, fence = [], False
    for i, l in enumerate(lines[:-1]):
        if l.strip().startswith('```'):
            fence = not fence
            continue
        if not fence and i not in skip:
            body.append(l)
    if fence:
        return False, '``` 程式碼區塊沒閉合'
    got = [0, 0, 0]
    for t in TAG.finditer('\n'.join(body)):
        got[KIND[t.group(1) or t.group(2)]] += 1
    got = tuple(got)
    note = f'宣告 通過 {said[0]}／降級 {said[1]}／UNKNOWN {said[2]}；可數 通過 {got[0]}／降級 {got[1]}／UNKNOWN {got[2]}'
    return said == got, note

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法：python3 -I -B flowlock_check.py <回覆檔.md> [...]'); sys.exit(2)
    bad = 0
    for a in sys.argv[1:]:
        try:
            txt = pathlib.Path(a).read_text(encoding='utf-8')
        except OSError as e:
            print(f'讀不到 {a}：{e}'); sys.exit(2)
        good, note = check(txt)
        bad += not good
        print(('PASS' if good else 'FAIL'), a, '｜' + note)
    sys.exit(1 if bad else 0)
