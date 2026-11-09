# terms_check.py｜MIKO 核心詞彙與行為定義表檢查（1.2.53，ADR-076；只用標準函式庫）
# 用法：python3 -I -B terms_check.py <skills/miko-core/references/term-definitions.md> [要檢查的檔 ...]
# 檢查 1（定義表）：每個「## 短名」都有十一節（正式名稱、類型、定義、觸發條件、執行動作、輸出格式、完成判準、失敗處理、不適用情況、相關名詞、條文），
#   每節有內容（至少 2 個字，不能只寫「見…」）；類型五選一（【流程】【輸出】【檢核】【限制】【處置】）；短名與正式名稱都不重複
# 檢查 2（受檢檔）：先去掉 frontmatter、``` 程式碼區塊與第一個 H1；每個短名第一次出現的那一行，要有緊鄰的「短名（正式名稱：正式名稱」；
#   找短名時先把該行各個「（正式名稱：…）」括號內文字拿掉，避免正式名稱裡的字被當成另一個短名（例：「出口」的正式名稱含「困難卡」）
#   正式名稱後要接「）」或「；」（不得多字）；在名詞行裡還要緊接該名詞的類型標籤（1.2.53 稽核第二輪）
# 檢查 3（受檢檔）：檔內有用到任何短名時，H1 下第一個非空行要是「> 名詞」開頭的名詞行
# 已知限制：不在定義表裡的新造短名詞檢查不到，靠 miko-core §4「名詞寫法」與稽核（README §8 T52）
# 結束碼：0 全過；1 有不合格；2 參數錯或讀不到檔
import re, sys, pathlib
TAGS = ['【流程】', '【輸出】', '【檢核】', '【限制】', '【處置】']
SECS = ['正式名稱', '類型', '定義', '觸發條件', '執行動作', '輸出格式', '完成判準', '失敗處理', '不適用情況', '相關名詞', '條文']
PAREN = re.compile(r'（正式名稱：[^）]*）')

def parse(text):
    terms, bad = [], []
    for b in re.split(r'^(?=## )', text, flags=re.M):
        if not b.startswith('## '):
            continue
        name = b.splitlines()[0][3:].strip()
        secs = {}
        for m in re.finditer(r'^### (.+?)\s*\n(.*?)(?=^### |\Z)', b, re.M | re.S):
            secs[m.group(1).strip()] = m.group(2).strip()
        miss = [k for k in SECS if k not in secs]
        thin = [k for k in SECS if k in secs and (len(secs[k]) < 2 or re.fullmatch(r'見[^。；]*', secs[k]))]
        if miss: bad.append(f'{name} 缺節：{"、".join(miss)}')
        if thin: bad.append(f'{name} 節內容空白或只指回：{"、".join(thin)}')
        if secs.get('類型') not in TAGS: bad.append(f'{name} 類型不在五選一：{secs.get("類型")}')
        terms.append((name, secs.get('正式名稱', '')))
    for i, label in ((0, '短名'), (1, '正式名稱')):
        vals = [t[i] for t in terms]
        dup = sorted({v for v in vals if v and vals.count(v) > 1})
        if dup: bad.append(f'{label}重複：{dup}')
    if not terms: bad.append('定義表沒有任何名詞（找不到「## 短名」）')
    return terms, bad

def body(text):
    fm = re.match(r'^---\n.*?\n---\n', text, re.S)
    lines, out, fence, h1 = (text[fm.end():] if fm else text).split('\n'), [], False, None
    for l in lines:
        if l.lstrip().startswith('```'):
            fence = not fence; out.append(''); continue
        if fence: out.append(''); continue
        if h1 is None and l.startswith('# '):
            h1 = len(out); continue
        out.append(l)
    return out, h1

def tag_map(text):
    tags = {}
    for b in re.split(r'^(?=## )', text, flags=re.M):
        if not b.startswith('## '):
            continue
        m = re.search(r'^### 類型\s*\n(.*?)(?=^### |\Z)', b, re.M | re.S)
        tags[b.splitlines()[0][3:].strip()] = m.group(1).strip() if m else ''
    return tags

def check_file(text, terms, tags=None):
    bad = []
    ls, h1 = body(text)
    start = next((i for i in range((h1 or 0), len(ls)) if ls[i].strip()), None)
    block = set()
    if start is not None and ls[start].startswith('> 名詞'):
        i = start
        while i < len(ls) and ls[i].startswith('>'):
            block.add(i); i += 1
    used = False
    for s, formal in terms:
        for i, l in enumerate(ls):
            if s in PAREN.sub('', l):
                used = True
                if not re.search(re.escape(f'{s}（正式名稱：{formal}') + '[）；]', l):
                    bad.append(f'「{s}」第一次出現的那一行沒有「{s}（正式名稱：{formal}）」：{l.strip()[:50]}')
                elif tags is not None and i in block and f'{s}（正式名稱：{formal}）{tags.get(s, "")}' not in l:
                    bad.append(f'「{s}」在名詞行沒有緊接類型標籤 {tags.get(s, "（定義表沒有類型）")}：{l.strip()[:50]}')
                break
    if used and start is None or used and not ls[start].startswith('> 名詞'):
        bad.append('H1 下第一個非空行不是「> 名詞」名詞行')
    return bad

def main(argv):
    if len(argv) < 2:
        print('用法：python3 -I -B terms_check.py <term-definitions.md> [要檢查的檔 ...]'); return 2
    try:
        defs = pathlib.Path(argv[1]).read_text(encoding='utf-8')
        others = [(f, pathlib.Path(f).read_text(encoding='utf-8')) for f in argv[2:]]
    except OSError as ex:
        print(f'讀不到檔：{ex}'); return 2
    terms, bad = parse(defs)
    fails = [f'定義表：{x}' for x in bad]
    for f, t in others:
        fails += [f'{f}：{x}' for x in check_file(t, terms, tag_map(defs))]
    print(f'名詞 {len(terms)} 個；檢查檔 {len(others)} 個；不合格 {len(fails)} 項')
    for x in fails: print('  - ' + x)
    print('PASS' if not fails else 'FAIL')
    return 0 if not fails else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
