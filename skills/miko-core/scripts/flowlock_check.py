# flowlock_check.py｜流程鎖（正式名稱：回覆結尾的證據標籤計數檢核）三數與行內標籤數的程式核算（1.2.64，ADR-087；只用標準函式庫）
# 起因：1.2.63 冷啟動 T59／T60 六份作答中五份流程鎖三數與可數行內標籤不符（判分方手數；總召專案檔判分_T59_T60_1263.md），
#   同類錯誤重複出現，依 miko-core §4「重複錯誤回到規則」（P-19a）先試程式檢查。
# 用法：python3 -I -B flowlock_check.py <回覆檔.md> [...]；判分、稽核、冷啟動回歸時用，對話中的回覆不在 repo 裡，check_repo 攔不到（只能靠本工具與測題）。
# 算法（miko-core §5 第 1、2、5 點）：
#   1. 最後一個非空行要以「流程鎖：」開頭（§5 第 5 點：流程鎖之後不再寫任何內容）；解析「通過 N 項／降級 N 項／UNKNOWN N 項」。
#   2. 計數範圍：去掉 ``` 程式碼區塊與流程鎖那一行（括號內逐條列出的降級、UNKNOWN 標籤是重述，不重複計數）。
#   3. 通過＝【來源：…】【工具：…】【使用者…】【常識…】；降級＝【推論…】【未查證…】；UNKNOWN＝【UNKNOWN…】；
#      【流程】【輸出】【檢核】【限制】【處置】是規則類型標籤，不計數。標籤後可帶補充（例：【推論，只加句不刪】），照前綴分類。
#   4. 三數各自相符才 PASS（不只比總數）。
# 已知限制：只核計數與位置，不核「來源真的支持這句」（§5 第 5 點另查三件，仍靠人或稽核）；一個檔只當一則回覆。
# 結束碼：0 全部相符；1 有不符或沒有流程鎖行；2 參數錯或讀不到檔
import re, sys, pathlib
LOCK = re.compile(r'^流程鎖：通過\s*(\d+)\s*項／降級\s*(\d+)\s*項／UNKNOWN\s*(\d+)\s*項')
TAG = re.compile(r'【(來源|工具)[：:][^】]*】|【(使用者|常識|推論|未查證|UNKNOWN)(?:[，,：:、（(][^】]*)?】')
KIND = {'來源': 0, '工具': 0, '使用者': 0, '常識': 0, '推論': 1, '未查證': 1, 'UNKNOWN': 2}

def check(text):
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return False, '空檔'
    m = LOCK.match(lines[-1].strip())
    if not m:
        anywhere = [i + 1 for i, l in enumerate(lines) if l.strip().startswith('流程鎖：')]
        return False, (f'流程鎖不在最後一行（出現在第 {anywhere} 行）' if anywhere else '沒有流程鎖行')
    said = tuple(int(x) for x in m.groups())
    body, fence = [], False
    for l in lines[:-1]:
        if l.strip().startswith('```'):
            fence = not fence
            continue
        if not fence:
            body.append(l)
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
