# check_repo.py｜MIKO 正本自動檢查（只用標準函式庫）｜用法：在 repo 根目錄執行 python3 tests/check_repo.py
# 私人關鍵字不寫進本檔：要加測時，用環境變數 MIKO_PRIVATE_WORDS（以逗號分隔）傳入。
import json, os, re, subprocess, sys, pathlib, hashlib
R = pathlib.Path(__file__).resolve().parents[1]
res = []
NR = []   # NOT_RUN 項（1.2.44）：只列名稱與原因，不算 PASS 也不算 FAIL
def ok(name, cond, note=''):
    res.append((name, bool(cond), note))

# C11 Skill 保真：改過的 skills/*/SKILL.md 與上一版（HEAD）比，子句保留率要 ≥ 90%；刪除要在正文「## 刪除清單」逐條列出理由
# 1.2.41（P-I1、P-I2）：只認行首「## 刪除清單」標題；保留率 < 90% 時刪除清單節要比上一版多出新條目；訊息寫實際保留率；
# 沒逐字保留的子句即使 PASS 也逐條列出（只顯示不擋）；可單獨執行：python3 tests/check_repo.py --only C11
# 1.2.43：新舊兩邊都把同目錄 references/*.md 併進來比（搬到附檔不算遺失）；references/MOVED.md 提到的附檔要存在
def _seg(t): return [x.strip(' -`') for x in re.split(r'[，；。\n：]', t) if len(x.strip(' -`')) >= 6]
def _dl(t):   # 所有行首「## 刪除清單」節的條目行（到下一個 ## 標題或檔尾）；條目＝以「- 」開頭且含「：」或「理由」；只驗形式，內容由 make-skill S5 與稽核看
    out = set()
    for m in re.finditer(r'^## 刪除清單[^\n]*\n(.*?)(?=^## |\Z)', t, re.M | re.S):
        out |= {x.strip() for x in m.group(1).splitlines() if x.strip().startswith('- ') and ('：' in x or '理由' in x)}
    return out
c11_lost = []
def _refs_old(base, d):   # 上一版同目錄 references/*.md 全文（1.2.43：搬到附檔的句子算保留）
    ls = subprocess.run(['git', '-C', str(R), 'ls-tree', '-r', '--name-only', base, f'{d}/references/'], capture_output=True, text=True)
    out = ''
    for n in sorted(x for x in ls.stdout.splitlines() if x.endswith('.md') and not x.endswith('/MOVED.md')):
        out += '\n' + subprocess.run(['git', '-C', str(R), 'show', f'{base}:{n}'], capture_output=True, text=True).stdout
    return out
def _refs_new(f):
    return ''.join('\n' + x.read_text(encoding='utf-8') for x in sorted((f.parent / 'references').glob('*.md')) if x.name != 'MOVED.md')   # MOVED.md 是對照表，不算保留
def c11():
    low, info = [], []
    try:
        for f in sorted((R / 'skills').glob('*/SKILL.md')):
            rel = f.relative_to(R).as_posix()
            base = os.environ.get('MIKO_BASE', 'HEAD')   # CI 用 MIKO_BASE=推送前的 commit，比對本次推送
            old = subprocess.run(['git', '-C', str(R), 'show', f'{base}:{rel}'], capture_output=True, text=True)
            if old.returncode != 0: continue
            skill_new = f.read_text(encoding='utf-8')
            new = skill_new + _refs_new(f); oldt = old.stdout + _refs_old(base, f.parent.relative_to(R).as_posix())
            mv = f.parent / 'references' / 'MOVED.md'   # 搬移對照：每列提到的 references/檔名 要存在
            if mv.exists():
                gone = sorted({x for x in re.findall(r'references/([\w.-]+\.md)', mv.read_text(encoding='utf-8')) if not (f.parent / 'references' / x).exists()})
                if gone: low.append(f'{rel} 的 references/MOVED.md 指到不存在的附檔：{gone}')
            unref = [x.name for x in sorted((f.parent / 'references').glob('*.md')) if x.name != 'MOVED.md' and f'references/{x.name}' not in skill_new]
            if unref: low.append(f'{rel} 的附檔沒有在 SKILL.md 正文提到（references/檔名）：{unref}')   # 1.2.43 稽核：防止刪掉正文句子塞進沒有指回的附檔
            if new == oldt: continue
            so = _seg(oldt); miss = [x for x in so if x not in new]; kept = len(so) - len(miss); rate = kept / len(so) if so else 1
            added = _dl(skill_new) - _dl(old.stdout)
            if miss: c11_lost.append((rel, miss))
            msg = f'{rel}（含 references/）保留 {kept}/{len(so)}={rate:.3f}'
            if rate < 0.9 and not added: low.append(msg + '，行首「## 刪除清單」節本次沒有新增條目（條目以「- 」開頭且含「：」或「理由」，只驗形式）')
            else: info.append(msg + (f'，刪除清單新增 {len(added)} 行' if rate < 0.9 else ''))
        ok('C11 Skill 改版不得大量精簡（子句保留 ≥ 90%，否則行首「## 刪除清單」本次要有新增條目）', not low, '；'.join(low + info) or '無改動')
    except Exception as ex:
        ok('C11 Skill 改版不得大量精簡（子句保留 ≥ 90%，否則行首「## 刪除清單」本次要有新增條目）', False, f'執行失敗：{ex}')

def report():
    for n, c, note in res:
        print(('PASS' if c else 'FAIL'), n, ('｜' + note) if note else '')
    for rel, miss in c11_lost:
        print(f'C11 遺失子句（只顯示不擋，逐條要有處置：改寫到哪、搬到哪或進刪除清單）{rel} 共 {len(miss)} 條：')
        for x in miss: print('  - ' + x)
    for n in NR:
        print('NOT_RUN', n, '｜回測 PAUSED_BY_USER，不執行 bt_min.py，不算 PASS')
    tail = f'；NOT_RUN {len(NR)} 項（{"、".join(n.split()[0] for n in NR)}，PAUSED_BY_USER，不算 PASS）' if NR else ''
    print(f'合計：{sum(c for _, c, _ in res)}/{len(res)} PASS' + tail)
    if NR and os.environ.get('GITHUB_ACTIONS') == 'true':   # CI 頁面的警示與摘要也寫 NOT_RUN，不寫成 PASS
        print(f'::warning title=check_repo NOT_RUN::{"、".join(n.split()[0] for n in NR)} NOT_RUN（PAUSED_BY_USER），不算 PASS')
        sp = os.environ.get('GITHUB_STEP_SUMMARY')
        if sp:
            with open(sp, 'a', encoding='utf-8') as fh:
                fh.write(f'## check_repo\n\n- {"、".join(n.split()[0] for n in NR)} NOT_RUN（PAUSED_BY_USER），不算 PASS\n- 合計：{sum(c for _, c, _ in res)}/{len(res)} PASS\n' + ''.join(f'- FAIL {n}\n' for n, c, _ in res if not c) + ''.join(f'- NOT_RUN {n}（PAUSED_BY_USER，不算 PASS）\n' for n in NR))
    sys.exit(0 if all(c for _, c, _ in res) else 1)

ONLY = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv and sys.argv.index('--only') + 1 < len(sys.argv) else None
if '--only' in sys.argv and ONLY != 'C11':
    print(f'--only 目前只支援 C11，收到：{ONLY}'); sys.exit(2)
if ONLY == 'C11':
    c11(); report()

# 1.2.44（ADR-067）：--skip-backtest 略過 C6、C9（兩項會執行回測引擎 bt_min.py）；回測 PAUSED_BY_USER 期間 CI 與本機都帶這個參數；MIKO 明說恢復回測後從 check.yml 拿掉
SKIP_BT = '--skip-backtest' in sys.argv


readme = (R / 'README.md').read_text(encoding='utf-8')
ver = (R / 'VERSION').read_text(encoding='utf-8').split('\n')[0].strip()
chg = (R / 'CHANGELOG.md').read_text(encoding='utf-8')
adp = (R / 'adapters' / 'README.md').read_text(encoding='utf-8')
core = (R / 'skills' / 'miko-core' / 'SKILL.md').read_text(encoding='utf-8')
m = re.search(r'對應正本：([0-9.]+)', core)
ok('C1 版本一致', f'v{ver}｜' in readme and f'- {ver}（' in chg and f'VERSION 的 {ver}' in adp and f'正本 v{ver}」' in adp and m and m.group(1) == ver,
   f'VERSION={ver} miko-core 對應正本={m.group(1) if m else None}')

bad, nover = [], []
for p in sorted((R / 'skills').glob('*/SKILL.md')):
    t = p.read_text(encoding='utf-8')
    fm = re.match(r'^---\n(.*?)\n---\n', t, re.S)
    h1 = re.search(r'^# (.*)$', t[fm.end():] if fm else t, re.M)   # 1.2.41（P-I3）：frontmatter 後第一個 # 標題要含 v數字；caveman、grilling、dghp-work-handoff 補完前只提示不擋
    if not (h1 and re.search(r'v\d', h1.group(1))): nover.append(p.parent.name)
    name = re.search(r'^name:\s*"?([^"\n]+)"?\s*$', fm.group(1), re.M) if fm else None
    desc = re.search(r'^description:[ \t]*\S', fm.group(1), re.M) if fm else None   # 1.2.43 稽核：同一行要有內容，不跨行吃到下一個欄位（刻意比 YAML 嚴：description 第一行必須有字）
    if not (fm and name and desc and name.group(1).strip() == p.parent.name):
        bad.append(p.parent.name); continue
    nm = name.group(1).strip()   # 1.2.43（R1，Agent Skills 規格）：name 只能小寫英數與單一連字號、≤ 64 字；description ≤ 1024 字
    dm = re.search(r'^description:[ \t]*(.*)\n?((?:(?:[ \t]+.*)?\n)*)', fm.group(1) + '\n', re.M)   # 1.2.43 稽核：YAML 區塊純量（> 或 |）與縮排續行併起來量
    dv = (dm.group(1).strip().lstrip('>|-').strip() + ' ' + ' '.join(x.strip() for x in dm.group(2).splitlines())).strip().strip('"').strip("'")
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', nm) or len(nm) > 64: bad.append(f'{p.parent.name}（name 格式或長度）')
    if len(dv) > 1024: bad.append(f'{p.parent.name}（description {len(dv)} 字 > 1024）')
ok('C2 Skill 開頭格式（name 與資料夾同名、小寫連字號 ≤ 64 字、description ≤ 1024 字）', not bad, f'不合格：{bad}；提示（不擋）標題沒有版號：{nover}')

words = [w for w in os.environ.get('MIKO_PRIVATE_WORDS', '').split(',') if w]
pat = re.compile(r'[\w.+-]+@[\w-]+\.(com|tw|net|org)|/home/|/Users/|~/[A-Z]' + ''.join('|' + re.escape(w) for w in words))
hits = []
if (R / '.git').exists():
    files = [R / f for f in subprocess.run(['git', 'ls-files'], cwd=R, capture_output=True, text=True).stdout.splitlines()]
else:
    files = [p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
for p in files:
    if p.is_file() and p.name != 'check_repo.py':  # 含 .csv 與二進位檔（以位元組解碼掃字串）
        t = p.read_bytes().decode('utf-8', 'ignore')
        for mm in pat.finditer(t):
            hits.append(f'{p.relative_to(R)}:{mm.group(0)}')
pyc = [str(f.relative_to(R)) for f in files if f.suffix == '.pyc' or '__pycache__' in f.parts]
hits += pyc
ok('C3 公開檔（含 .csv、二進位、快取檔）無 email、本機路徑與私人關鍵字', not hits, f'命中：{hits[:5]}；私人關鍵字 {len(words)} 個')

miss = [t for t in [f'T{i}' for i in range(1, 48)] + ['T15B', 'T15C', 'T15D', 'T15E', 'T29B'] if f'| {t} |' not in readme]
ok('C4 回歸測試 T1～T47、T15B～T15E 與 T29B 都在正本 §8', not miss, f'缺：{miss}')

log = (R / 'sync' / 'LOG.md').read_text(encoding='utf-8') if (R / 'sync' / 'LOG.md').exists() else ''
ok('C5 sync 檔存在且 LOG 有表頭', (R / 'sync' / 'CLAUDE_STATUS.md').exists() and '| 時間（台北） | 提出方 | 內容 | 決定 | 負責方 | 狀態 |' in log)

sd = R / 'skills' / 'tw-backtest-workflow' / 'scripts'
if SKIP_BT:   # 1.2.44（ADR-067）：回測 PAUSED_BY_USER 期間不執行 bt_min.py，標 NOT_RUN，不算 PASS
    NR.append('C6 bt_min.py 實跑結果與預期一致（含除息日樣本：給事件檔就停止）')
else:
    exp = json.loads((R / 'tests' / 'expected_bt_min.json').read_text(encoding='utf-8'))
    out = subprocess.run([sys.executable, '-I', '-B', 'bt_min.py', '2330_202501_202505.csv', '--ignore-events'], cwd=sd, capture_output=True, text=True)
    blk = subprocess.run([sys.executable, '-I', '-B', 'bt_min.py', '2330_202501_202505.csv', '--events', 'ev_2330.csv'], cwd=sd, capture_output=True, text=True).returncode != 0
    try:
        got = json.loads(out.stdout)
        same = (got['sha256'] == exp['csv_sha256'] and got['rows'] == exp['rows'] and got['range'] == exp['range']
                and got['no_lookahead'] == exp['no_lookahead'] and got['stats'] == exp['stats']
                and got['open_position'] == exp['open_position'] and len(got['trades']) == exp['closed_trades']
                and got['corporate_events'] == 'IGNORED_BY_USER' and blk)
        ok('C6 bt_min.py 實跑結果與預期一致（含除息日樣本：給事件檔就停止）', same, f"報酬率={got['stats'].get('報酬率')} MDD={got['stats'].get('MDD')} 事件擋下={blk}")
    except Exception as e:
        ok('C6 bt_min.py 實跑結果與預期一致', False, f'執行失敗：{e} {out.stderr[:200]}')

bp = R / 'projects' / 'beauty'
need = ['README.md', 'INSTRUCTIONS.md', 'INVENTORY_TEMPLATE.md', 'TESTS.md']
miss7 = [f for f in need if not (bp / f).exists()]
note7 = f'缺檔：{miss7}'
cond7 = not miss7
if cond7:
    ins, inv, tst, rd = [(bp / f).read_text(encoding='utf-8') for f in ('INSTRUCTIONS.md', 'INVENTORY_TEMPLATE.md', 'TESTS.md', 'README.md')]
    pv = re.search(r'beauty-project v([0-9.]+)', ins)
    iv = re.search(r'對應 dghp-beauty v([0-9.]+)', ins)
    skp = R / 'skills' / 'dghp-beauty' / 'SKILL.md'
    sv = re.search(r'^# dghp-beauty v([0-9.]+)', skp.read_text(encoding='utf-8'), re.M) if skp.exists() else None
    filled, hdr = [], False
    for line in inv.split('\n'):
        if not line.startswith('|'):
            hdr = False
            continue
        if not hdr:
            hdr = True
            continue
        if set(line) <= set('|-: '):
            continue
        if any(c.strip() for c in line.strip().strip('|').split('|')):
            filled.append(line[:40])
    sec = inv.split('## 膚況設定', 1)[1].split('\n## ', 1)[0] if '## 膚況設定' in inv else ''
    for line in sec.split('\n'):
        if line.startswith('- ') and '：' in line and line.split('：', 1)[1].strip():
            filled.append(line[:40])
    tmiss = [f'P{i}' for i in range(1, 9) if f'| P{i} |' not in tst]
    cond7 = bool(pv and iv and sv and iv.group(1) == sv.group(1) and f'beauty-project v{pv.group(1)}' in rd
                 and f'beauty-project v{pv.group(1)}' in tst and '美妝_現有產品.md' in ins and not filled and not tmiss)
    note7 = (f"專案包 v{pv.group(1) if pv else None}／對應 dghp-beauty v{iv.group(1) if iv else None}／Skill v{sv.group(1) if sv else None}"
             f"；範本已填列 {len(filled)}；缺驗收題 {tmiss}")
ok('C7 美妝專案包完整、版本對應、範本表格與膚況欄位未填', cond7, note7)

pf = [str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and '.git' not in p.parts
      and (p.name.startswith('美妝_現有產品') or re.search(r'_個人資料.*\.md$', p.name))]
gi = (R / '.gitignore').read_text(encoding='utf-8') if (R / '.gitignore').exists() else ''
ok('C8 repo 沒有個人清單檔，.gitignore 已排除', not pf and '美妝_現有產品' in gi and '_個人資料' in gi, f'命中：{pf}')

if SKIP_BT:
    NR.append('C9 回測帳本（獨立常數＋固定值）、偷看未來與全樣本統計、公司事件、雜湊、順延取消、ETF 稅率')
else:
    import importlib.util, tempfile
    sys.dont_write_bytecode = True
    note9, cond9 = '', False
    try:
        spec = importlib.util.spec_from_file_location('bt', sd / 'bt_min.py'); bt = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt)
        syn = R / 'tests' / 'synthetic_cycle.csv'; dd = bt.load(str(syn)); tt, ee, oo, sk = bt.run(dd)
        rows = {r['date']: r for r in dd}; fee = lambda v: max(1, v * 0.001425)  # 獨立常數，不讀引擎參數
        led = all(abs(round(rows[x['exit']]['open'] * x['shares'] - fee(rows[x['exit']]['open'] * x['shares']) - rows[x['exit']]['open'] * x['shares'] * 0.003
                            - rows[x['entry']]['open'] * x['shares'] - fee(rows[x['entry']]['open'] * x['shares']), 1) - x['pnl']) < 0.11
                  and rows[x['entry']]['volume'] > 0 and rows[x['exit']]['volume'] > 0 for x in tt)
        st9 = bt.stats(tt, ee)
        statok = (st9['淨利（含未實現）'], st9['PF'], st9['交易次數（已平倉）'], st9['最大連敗'], st9['MDD']) == (1479, 1.42, 7, 2, '-14.60%') and len(sk) >= 1
        orig = bt.signal; caught = []
        for bad in (lambda d, i: 1 if d[i + 1]['open'] > d[i]['close'] else 0, lambda d, i: 1 if d[i + 1]['volume'] > d[i]['volume'] else 0):
            bt.signal = bad
            try:
                bt.run(dd); ran = False
            except SystemExit:
                ran = True
            caught.append(bt.check_no_lookahead(dd) is False and ran)
        bt.signal = lambda d, i: (1 if d[i + 1]['open'] > d[i]['close'] else -1) if i + 1 < len(d) else 0  # 不在最後一天出錯的偷看
        caught.append(len(bt.run(dd)[0]) == 0 and bt.run(dd)[2] is None and bt.check_no_lookahead(dd) is False)  # 證明只傳歷史
        z = [dict(r) for r in dd]; z[6]['volume'] = 0
        bt.signal = lambda d, i: 1 if i == 5 else -1 if i == 6 else 0
        cancel = bt.run(z)[0] == [] and bt.run(z)[2] is None
        bt.signal = orig
        tmpd = pathlib.Path(tempfile.mkdtemp())
        ev = tmpd / 'ev.csv'; ev.write_text('date,type\n' + dd[50]['date'] + ',除權息\n', encoding='utf-8')
        ev0 = tmpd / 'ev0.csv'; ev0.write_text('date,type\n', encoding='utf-8')
        gsrc = re.sub(r"def signal\(d, i\):.*?\n\ndef safe_signal", "_A = [float(r['close']) for r in csv.DictReader(open(sys.argv[1], encoding='utf-8'))]\n_M = sum(_A) / len(_A)\n"
                      "def signal(d, i):\n    return 1 if d[i]['close'] < _M * 0.97 else -1 if d[i]['close'] > _M * 1.03 else 0\n\ndef safe_signal",
                      (sd / 'bt_min.py').read_text(encoding='utf-8'), flags=re.S)
        (tmpd / 'g.py').write_text(gsrc, encoding='utf-8')
        run_ = lambda f, *a: subprocess.run([sys.executable, '-I', '-B', str(f), str(syn), *a], capture_output=True, text=True)
        cli = lambda *a: run_(sd / 'bt_min.py', *a).returncode
        sha9 = hashlib.sha256(syn.read_bytes()).hexdigest()
        ok_m = json.loads(run_(sd / 'bt_min.py', '--ignore-events', '--expect-sha', sha9).stdout)['manifest_check'] == 'MATCH'
        etf_tax = json.loads(run_(sd / 'bt_min.py', '--etf', '--adjusted').stdout)['params']['tax'] == 0.001
        stops = [cli() != 0, cli('--events', str(ev)) != 0, cli('--events', str(ev0)) != 0, cli('--etf', '--ignore-events') != 0,
                 cli('--ignore-events', '--expect-sha', '0' * 64) != 0, cli('--events', str(ev), '--adjusted') == 0,
                 run_(tmpd / 'g.py', '--ignore-events').returncode != 0, ok_m, etf_tax, bt.buy_shares(773.91, 24.9) == 31, bt.buy_shares(100.5, 10) == 9,
                 (bt.P['fee'], bt.P['fee_min'], bt.P['tax']) == (0.001425, 1, 0.003), cancel]
        cond9 = led and statok and all(caught) and all(stops)
        note9 = f'已平倉 {st9["交易次數（已平倉）"]} 筆、淨利 {st9["淨利（含未實現）"]}、PF {st9["PF"]}、最大連敗 {st9["最大連敗"]}；帳本 {led}、固定值 {statok}、偷看未來被擋 {caught}、停止與規格 {stops}'
    except Exception as ex:
        note9 = f'執行失敗：{ex}'
    ok('C9 回測帳本（獨立常數＋固定值）、偷看未來與全樣本統計、公司事件、雜湊、順延取消、ETF 稅率', cond9, note9)

vl = (R / 'VERSION').read_text(encoding='utf-8').split('\n')
rsha = hashlib.sha256((R / 'README.md').read_bytes()).hexdigest()
ok('C10 VERSION 第 4 行等於 README 的 SHA-256', len(vl) > 3 and vl[3].strip() == rsha, f'README={rsha[:12]}')

# C11 定義在檔頭（可用 --only C11 單獨執行）
c11()

# C12 私密字也掃 skills/ 下的 xlsx 與 csv 內容（C8 只掃文字檔；2026-11-04 範本曾夾帶工程名稱）
try:
    from openpyxl import load_workbook
    words = [w for w in os.environ.get('MIKO_PRIVATE_WORDS', '').split(',') if w]
    hit = []
    for f in list((R / 'skills').rglob('*.xlsx')) + list((R / 'skills').rglob('*.csv')):
        if f.suffix == '.xlsx':
            txt = ' '.join(str(c.value) for ws in load_workbook(f, read_only=True).worksheets for r in ws.iter_rows() for c in r if c.value is not None)
        else:
            txt = f.read_text(encoding='utf-8-sig', errors='ignore')
        hit += [f'{f.name}:{w}' for w in words if w in txt]
    ok('C12 xlsx／csv 內容無私密字', not hit, f'掃描字數 {len(words)}；命中：{hit}')
except Exception as ex:
    ok('C12 xlsx／csv 內容無私密字', False, f'執行失敗：{ex}')

# C13 不得提交本機設定、環境變數、憑證檔與金鑰樣式（1.2.41；金鑰外洩防護串 2026-11-08 提案）
# 命中只印「檔名：類型」，不印字串；本檔自身含樣式定義，不掃
import fnmatch
BAN13 = ['.env', '.env.*', '*.key', '*.pem', '*.p12', '*.pfx', '.netrc', 'secrets.toml']
KEYPAT = {
    'anthropic': r'sk-ant-[A-Za-z0-9_\-]{20,}', 'openai': r'sk-(proj-)?[A-Za-z0-9]{20,}',
    'github': r'(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}',
    'google': r'AIza[0-9A-Za-z_\-]{35}|GOCSPX-[A-Za-z0-9_\-]{20,}', 'aws': r'AKIA[0-9A-Z]{16}',
    'slack': r'xox[baprs]-[A-Za-z0-9\-]{10,}', 'private_key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'assign': r'(?i)(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*["\']?[A-Za-z0-9_\-\.]{24,}',
}
bad13 = []
try:
    for f in files:
        rel = f.relative_to(R).as_posix(); name = f.name
        if name != '.env.example' and (('/.claude/' in '/' + rel and name.endswith('.local.json')) or any(fnmatch.fnmatch(name, b) for b in BAN13)):
            bad13.append(f'{rel}：禁止提交的檔')
        if f.is_file() and name != 'check_repo.py':
            tx = f.read_bytes().decode('utf-8', 'ignore')
            bad13 += [f'{rel}：{k}' for k, pt in KEYPAT.items() if re.search(pt, tx)]
    ok('C13 不得提交本機設定、環境變數、憑證檔與金鑰樣式', not bad13, f'共 {len(bad13)} 筆；命中（只列檔名與類型）：{bad13[:8]}')
except Exception as ex:
    ok('C13 不得提交本機設定、環境變數、憑證檔與金鑰樣式', False, f'執行失敗：{ex}')

# C14 skill_lint 不倒退（1.2.43，R2）：tests/lint_ratchet.txt 列的是已過升級站的 Skill，這些 Skill 的 skill_lint 不得 FAIL；清單每過一站由升級串加一行
try:
    lr = [x.split('#')[0].strip() for x in (R / 'tests' / 'lint_ratchet.txt').read_text(encoding='utf-8').splitlines()]
    lr = [x for x in lr if x]; bad14 = []
    for sk in lr:
        f = R / 'skills' / sk / 'SKILL.md'
        out = subprocess.run([sys.executable, '-I', '-B', str(R / 'skills' / 'make-skill' / 'scripts' / 'skill_lint.py'), str(f)], capture_output=True, text=True)
        if out.returncode != 0: bad14.append(sk)
    ok('C14 已過升級站的 Skill，skill_lint 不得退回 FAIL', lr and not bad14, f'清單 {len(lr)} 個：{lr}；FAIL：{bad14}')
except Exception as ex:
    ok('C14 已過升級站的 Skill，skill_lint 不得退回 FAIL', False, f'執行失敗：{ex}')

# C15 出處編號提示（1.2.43，R3；只提示不擋）：skills/ 正文引用的 ADR 編號要在 CHANGELOG 或 README 找得到；已知記在別處的列 tests/c15_exceptions.txt
try:
    ex15 = {x.split()[0] for x in (R / 'tests' / 'c15_exceptions.txt').read_text(encoding='utf-8').splitlines() if x.strip() and not x.startswith('#')}
    src15 = chg + readme
    refs15 = set()
    for f in sorted((R / 'skills').rglob('*.md')):
        refs15 |= set(re.findall(r'ADR-\d{3}', f.read_text(encoding='utf-8')))
    miss15 = sorted(x for x in refs15 if x not in src15 and x not in ex15)
    ok('C15 出處編號提示（只提示不擋）：正文引用的 ADR 在 CHANGELOG 或 README 有出處', True,
       f'引用 {len(refs15)} 個；例外 {len(ex15 & refs15)} 個（出處未核實，見 tests/c15_exceptions.txt）；找不到出處：{miss15 or "無"}')
except Exception as ex:
    ok('C15 出處編號提示（只提示不擋）：正文引用的 ADR 在 CHANGELOG 或 README 有出處', True, f'提示項執行失敗（不擋）：{ex}')

report()
