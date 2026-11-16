# skill_lint.py v0.3｜make-skill S4～S6 的檢查程式：SKILL.md 是否符合可執行格式
# 用法：python3 -I -B skill_lint.py SKILL.md [SKILL.md ...]   全部 PASS 結束碼 0；任一 FAIL 結束碼 1；沒給檔案結束碼 2
# 只檢查格式與結構（L1～L9）。PASS 不代表可執行；「標 J／C 的步驟其實能用程式算」只印 WARN 提醒，最後由稽核判定。
# v0.3（2026-11-08，第二～四輪稽核）：七欄表頭之後，七欄以上的表列一律當步驟列檢（夾空行、註解、佔位列、第二張七欄表、範本表後續寫都照檢）；
# 少於七欄的別的表（範本表，有無分隔列皆可）與程式碼區塊內的範例表不檢；全「-」的格視同空白。
# v0.2（2026-11-08，冷啟動稽核問題 2、3、14）：L5 只有禁止事項可寫「無」；L7 命令要以可執行程式開頭、不得是〈佔位〉；
# L8 要寫明「相近反例」或「不該觸發」；新增 L9 ID 不重複；解決節不再把「執行」開頭的節當解決節；沒給檔案結束碼 2；檔案不存在印 FAIL。
import re, sys

SEC = {'問問題': r'問問題|模式|何時用', '解決': r'解決|流程|清理判定', '後設': r'後設|常見錯', '檢查': r'檢查|驗收'}
HEAD7 = ['ID', '類型', '觸發條件', '操作要求', '禁止事項', '驗收證據', '失敗處理']
CMD = re.compile(r'`\s*(python3?|bash|sh|curl|git|diff|sha256sum|gh|node|npm|pip3?|cd|mkdir|cp|unzip|libreoffice|soffice|grep)\b[^`]*`')
CALC = re.compile(r'換算|計算|算出|篩選條件|排序|加總|單價|日期差|截止日|查表|對照表比對')

def sections(text):
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r'^##\s+(.*)', ln)
        if m:
            cur = m.group(1); out[cur] = []
        elif cur is not None:
            out[cur].append(ln)
    return out

def cells(ln): return [c.strip() for c in re.split(r'(?<!\\)\|', ln.strip().strip('|'))]   # 表格內的 \| 是內容，不是欄界

def lint(path):
    with open(path, encoding='utf-8') as f: t = f.read(); r = []; warn = []
    fm = re.match(r'^---\n(.*?)\n---', t, re.S)
    r.append(('L1 frontmatter 有 name 與 description', bool(fm and re.search(r'^name:', fm.group(1), re.M) and re.search(r'^description:', fm.group(1), re.M))))
    r.append(('L2 標題有版本號（# 名稱 vX）', bool(re.search(r'^# .*\bv\d+(\.\d+)*', t, re.M))))
    sec = sections(t); found = {k: [h for h in sec if re.search(p, h)] for k, p in SEC.items()}
    r.append(('L3 四節齊（問問題／解決／後設／檢查）', all(found.values()), '缺：' + '、'.join(k for k, v in found.items() if not v)))
    body = '\n'.join(l for h in found['解決'] for l in sec[h])
    rows, head_ok, in_step, fence, prev = [], False, False, False, ''
    SEP = re.compile(r'^:?-{3,}:?$')
    for ln in body.splitlines():
        if ln.strip().startswith('```'): fence = not fence; prev = ''; continue   # 程式碼區塊內的範例表不檢
        if fence: continue
        if not ln.strip().startswith('|'):
            if ln.strip(): prev = ''       # 文字行結束表格；空行、註解不結束七欄表
            continue
        c = cells(ln); start = not prev.startswith('|'); prev_cells = prev
        prev = ln.strip()
        if c[:7] == HEAD7: head_ok = in_step = True; continue                    # 第二張七欄表也照檢
        if not start and all(SEP.match(x) for x in c) and cells(prev_cells)[:7] == HEAD7 or (not start and all(SEP.match(x) for x in c) and not in_step):
            continue                                                             # 表頭下的分隔列
        if start and len(c) < 7: in_step = False; continue                       # 別的表（範本表，少於七欄）：表頭與其列不是步驟列
        if not head_ok: continue
        if len(c) >= 7: in_step = True                                           # 七欄以上的列一律當步驟列（範本表後續寫也照檢）
        if in_step: rows.append(c)
    r.append(('L4 解決節有七欄表（ID、類型、觸發、操作、禁止、驗收證據、失敗處理）', head_ok and bool(rows)))
    bad = [c[0] for c in rows if len(c) < 7 or any((not x) or set(x) <= set('-—') or (x == '無' and i != 4) for i, x in enumerate(c[:7]))]
    r.append(('L5 七欄都有內容（只有禁止事項可寫「無」）', head_ok and not bad, '不合格：' + '、'.join(bad)))
    badt = [c[0] for c in rows if len(c) > 1 and c[1] not in ('P', 'C', 'J')]
    r.append(('L6 類型只有 P／C／J', head_ok and not badt, '不符：' + '、'.join(badt)))
    nocmd = [c[0] for c in rows if len(c) > 3 and c[1] == 'P' and not CMD.search(c[3])]
    r.append(('L7 P 步的操作要求寫出可執行命令（不是〈佔位〉）', head_ok and not nocmd, '沒命令：' + '、'.join(nocmd)))
    chk = '\n'.join(l for h in found['檢查'] for l in sec[h])
    r.append(('L8 檢查節有 expected、forbidden，且寫明相近反例或不該觸發的題', all(k in chk for k in ('expected', 'forbidden')) and bool(re.search(r'相近反例|不該觸發', chk))))
    ids = [re.split(r'\s', c[0])[0] for c in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    r.append(('L9 ID 不重複', head_ok and not dup, '重複：' + '、'.join(dup)))
    warn = [c[0] for c in rows if len(c) > 3 and c[1] in ('J', 'C') and CALC.search(c[3])]
    return r, warn

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法：python3 -I -B skill_lint.py SKILL.md [SKILL.md ...]'); sys.exit(2)
    allok = True
    for p in sys.argv[1:]:
        try:
            res, warn = lint(p)
        except OSError as e:
            print(f'== {p}：FAIL（讀不到檔案：{e.strerror}）'); allok = False; continue
        ok = all(x[1] for x in res); allok &= ok
        print(f'== {p}：{"PASS" if ok else "FAIL"}（{sum(x[1] for x in res)}/{len(res)}）')
        nt = not res[3][1]
        for i, x in enumerate(res):
            note = '｜沒有七欄表，無法逐列檢查' if nt and i in (4, 5, 6, 8) else (f'｜{x[2]}' if not x[1] and len(x) > 2 else '')
            print(f'  {"PASS" if x[1] else "FAIL"} {x[0]}' + note)
        for w in warn:
            print(f'  WARN 可能能算（標 J／C，操作要求含計算或比對字樣，請確認是否改標 P）：{w}')
    sys.exit(0 if allok else 1)
