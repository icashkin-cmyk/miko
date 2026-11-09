# terms_check.py｜名詞表與第一次出現檢查（1.2.53，ADR-076；只用標準函式庫）
# 用法：python3 -I -B terms_check.py <miko-core SKILL.md> [要檢查的檔 ...]
# 檢查 1：miko-core「## 名詞表」每個「### 短名（正式名稱：…）【類型】」都寫齊七項（定義、觸發條件、執行動作、輸出／證據、完成判準、失敗處理、條文），類型五選一，短名不重複
# 檢查 2：每個要檢查的檔，名詞表每個短名第一次出現的那一行（frontmatter 與第一個 H1 標題不算）要含該名詞的正式名稱；檔裡沒用到的短名不檢查
# 結束碼：0 全過；1 有不合格；2 參數錯或讀不到檔
import re, sys, pathlib
TAGS = '流程|輸出|檢核|限制|處置'
KEYS = ['定義', '觸發條件', '執行動作', '輸出／證據', '完成判準', '失敗處理', '條文']

def parse(text):
    m = re.search(r'^## 名詞表[^\n]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not m:
        return None, ['找不到「## 名詞表」節']
    terms, bad = [], []
    for b in re.split(r'^(?=### )', m.group(1), flags=re.M):
        if not b.startswith('### '):
            continue
        h = re.match(r'### (.+?)（正式名稱：(.+)）【(' + TAGS + r')】[ \t]*\n', b)
        if not h:
            bad.append(f'標題格式不符：{b.splitlines()[0][:60]}'); continue
        miss = [k for k in KEYS if not re.search(r'^- ' + re.escape(k) + r'：\s*\S', b, re.M)]
        if miss:
            bad.append(f'{h.group(1)} 缺欄：{"、".join(miss)}')
        terms.append((h.group(1), h.group(2)))
    names = [s for s, _ in terms]
    dup = sorted({s for s in names if names.count(s) > 1})
    if dup:
        bad.append(f'短名重複：{dup}')
    if not terms:
        bad.append('名詞表沒有任何名詞')
    return terms, bad

def body(text):
    fm = re.match(r'^---\n.*?\n---\n', text, re.S)
    lines = (text[fm.end():] if fm else text).split('\n')
    for i, l in enumerate(lines):
        if l.startswith('# '):
            return lines[:i] + lines[i + 1:]
    return lines

def first_bad(text, terms):
    bad = []
    ls = body(text)
    for s, formal in terms:
        for l in ls:
            if s in l:
                if formal not in l:
                    bad.append(f'「{s}」第一次出現的那一行沒有正式名稱「{formal}」：{l.strip()[:50]}')
                break
    return bad

def main(argv):
    if len(argv) < 2:
        print('用法：python3 -I -B terms_check.py <miko-core SKILL.md> [要檢查的檔 ...]'); return 2
    try:
        core = pathlib.Path(argv[1]).read_text(encoding='utf-8')
        others = [(f, pathlib.Path(f).read_text(encoding='utf-8')) for f in argv[2:]]
    except OSError as ex:
        print(f'讀不到檔：{ex}'); return 2
    terms, bad = parse(core)
    fails = [f'名詞表：{x}' for x in bad]
    for f, t in others:
        fails += [f'{f}：{x}' for x in first_bad(t, terms or [])]
    print(f'名詞 {len(terms or [])} 個；檢查檔 {len(others)} 個；不合格 {len(fails)} 項')
    for x in fails:
        print('  - ' + x)
    print('PASS' if not fails else 'FAIL')
    return 0 if not fails else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
