# check_repo.py｜MIKO 正本自動檢查（只用標準函式庫）｜用法：在 repo 根目錄執行 python3 tests/check_repo.py
# 私人關鍵字不寫進本檔：要加測時，用環境變數 MIKO_PRIVATE_WORDS（以逗號分隔）傳入。
import json, os, re, subprocess, sys, pathlib, hashlib
R = pathlib.Path(__file__).resolve().parents[1]
res = []
def ok(name, cond, note=''):
    res.append((name, bool(cond), note))

readme = (R / 'README.md').read_text(encoding='utf-8')
ver = (R / 'VERSION').read_text(encoding='utf-8').split('\n')[0].strip()
chg = (R / 'CHANGELOG.md').read_text(encoding='utf-8')
adp = (R / 'adapters' / 'README.md').read_text(encoding='utf-8')
core = (R / 'skills' / 'miko-core' / 'SKILL.md').read_text(encoding='utf-8')
m = re.search(r'對應正本：([0-9.]+)', core)
ok('C1 版本一致', f'v{ver}｜' in readme and f'- {ver}（' in chg and f'VERSION 的 {ver}' in adp and m and m.group(1) == ver,
   f'VERSION={ver} miko-core 對應正本={m.group(1) if m else None}')

bad = []
for p in sorted((R / 'skills').glob('*/SKILL.md')):
    t = p.read_text(encoding='utf-8')
    fm = re.match(r'^---\n(.*?)\n---\n', t, re.S)
    name = re.search(r'^name:\s*"?([^"\n]+)"?\s*$', fm.group(1), re.M) if fm else None
    desc = re.search(r'^description:\s*\S', fm.group(1), re.M) if fm else None
    if not (fm and name and desc and name.group(1).strip() == p.parent.name):
        bad.append(p.parent.name)
ok('C2 Skill 開頭格式（name 與資料夾同名、有 description）', not bad, f'不合格：{bad}')

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

miss = [f'T{i}' for i in list(range(1, 15)) if f'| T{i} |' not in readme]
ok('C4 回歸測試 T1～T14 都在正本 §8', not miss, f'缺：{miss}')

log = (R / 'sync' / 'LOG.md').read_text(encoding='utf-8') if (R / 'sync' / 'LOG.md').exists() else ''
ok('C5 sync 檔存在且 LOG 有表頭', (R / 'sync' / 'CLAUDE_STATUS.md').exists() and '| 時間（台北） | 提出方 | 內容 | 決定 | 負責方 | 狀態 |' in log)

sd = R / 'skills' / 'tw-backtest-workflow' / 'scripts'
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

for n, c, note in res:
    print(('PASS' if c else 'FAIL'), n, ('｜' + note) if note else '')
print(f'合計：{sum(c for _, c, _ in res)}/{len(res)} PASS')
sys.exit(0 if all(c for _, c, _ in res) else 1)
