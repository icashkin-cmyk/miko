# bt_min.py｜tw-backtest-workflow 最小回測引擎 v1.4｜用法：python3 bt_min.py 資料.csv [--expect-sha HEX] [--events 事件.csv] [--adjusted] [--etf]
# CSV 欄位：date,open,high,low,close,volume（日期 YYYY-MM-DD 升冪）。改策略只改 signal()；引擎只把第 i 日以前（含）的資料交給 signal()。
# 事件 CSV（選用）：date,type（除權息、除息、拆股、減資等）。原始價格跨事件就停止；已用還原價格時加 --adjusted。--etf 沒有事件檔也沒有 --adjusted 就停止。
import csv, sys, json, hashlib, random
P = dict(capital=50000, fee=0.001425, fee_min=1, tax=0.003, slip=0.0, trail=0.12)

def stop(msg):
    raise SystemExit('停止：' + msg)

def load(p):
    d = [{k: (v if k == 'date' else float(v)) for k, v in r.items()} for r in csv.DictReader(open(p, encoding='utf-8'))]
    assert all(a['date'] < b['date'] for a, b in zip(d, d[1:])), '日期未升冪或重複'
    assert all(r['low'] <= min(r['open'], r['close']) <= max(r['open'], r['close']) <= r['high'] and r['low'] > 0 and r['volume'] >= 0 for r in d), 'OHLC 異常、價格為 0 或成交量為負'
    return d

def sma(x, n, i):
    return sum(x[i - n + 1:i + 1]) / n if i >= n - 1 else None

def signal(d, i):  # d 只含第 i 日以前（含）的資料：1 進場、-1 出場、0 不動
    c = [r['close'] for r in d[:i + 1]]
    f0, s0, f1, s1 = sma(c, 5, i - 1), sma(c, 20, i - 1), sma(c, 5, i), sma(c, 20, i)
    if None in (f0, s0, f1, s1):
        return 0
    return 1 if f0 <= s0 and f1 > s1 else -1 if f0 >= s0 and f1 < s1 else 0

def safe_signal(d, i):  # 結構防護：只傳歷史；讀到第 i+1 日就停止
    try:
        return signal(d[:i + 1], i)
    except IndexError:
        stop('signal() 讀取第 i 日之後的資料（未來資料洩漏）')

def buy_shares(cash, px):  # 預留最低手續費，買進後現金不得為負
    n = int(max(cash - P['fee_min'], 0) / (px * (1 + P['fee'])))
    while n > 0 and px * n + max(P['fee_min'], px * n * P['fee']) > cash:
        n -= 1
    return n

def run(d):
    cash, sh, peak, ent, pend, trades, eq, skipped = P['capital'], 0, 0, None, 0, [], [], []
    for i, r in enumerate(d):
        if pend and r['volume'] <= 0:  # 零成交量不成交，委託順延到下一個有量的交易日
            skipped.append(r['date'])
        elif pend:  # 訊號隔日開盤成交（T+1）
            px = r['open'] * (1 + P['slip'] * pend)
            if pend == 1 and sh == 0:
                n = buy_shares(cash, px)
                if n > 0:
                    fee = max(P['fee_min'], px * n * P['fee'])
                    cash -= px * n + fee; sh = n; peak = px; ent = dict(date=r['date'], px=px, cost=px * n + fee)
            elif pend == -1 and sh > 0:
                fee = max(P['fee_min'], px * sh * P['fee']); tax = px * sh * P['tax']
                cash += px * sh - fee - tax
                trades.append(dict(entry=ent['date'], exit=r['date'], shares=sh, pnl=round(px * sh - fee - tax - ent['cost'], 1))); sh = 0
            pend = 0
        if cash < -1e-9:
            stop(f"{r['date']} 現金為負")
        if sh:
            peak = max(peak, r['close'])
        s = safe_signal(d, i)
        if sh == 0 and s == 1:
            pend = 1
        elif sh and (s == -1 or r['close'] <= peak * (1 - P['trail'])):
            pend = -1
        eq.append(cash + sh * r['close'])
    open_pos = dict(entry=ent['date'], shares=sh, unrealized=round(sh * d[-1]['close'] - ent['cost'], 1)) if sh else None
    return trades, eq, open_pos, skipped

def stats(trades, eq):
    p = [t['pnl'] for t in trades]; w = [x for x in p if x > 0]; l = [-x for x in p if x <= 0]
    mdd, pk = 0, eq[0]
    for v in eq:
        pk = max(pk, v); mdd = min(mdd, v / pk - 1)
    run_l = best = 0
    for x in p:
        run_l = run_l + 1 if x <= 0 else 0; best = max(best, run_l)
    return {'淨利（含未實現）': round(eq[-1] - P['capital']), '報酬率': f"{eq[-1] / P['capital'] - 1:.2%}", 'MDD': f"{mdd:.2%}",
            '勝率': f"{len(w) / len(p):.0%}" if p else 'NA', 'PF': round(sum(w) / sum(l), 2) if l and sum(l) > 0 else 'NA',
            '交易次數（已平倉）': len(p), '盈虧比': round((sum(w) / len(w)) / (sum(l) / len(l)), 2) if w and l and sum(l) > 0 else 'NA', '最大連敗': best}

def check_no_lookahead(d, n=30):  # 故障測試：竄改未來各欄（開高低收量），用完整資料呼叫 signal()，訊號不得改變
    rnd = random.Random(0)
    for _ in range(n):
        i = rnd.randrange(len(d) - 1); fake = [dict(r) for r in d]
        for r in fake[i + 1:]:
            k = rnd.uniform(0.5, 1.5)
            for f in ('open', 'high', 'low', 'close', 'volume'):
                r[f] *= k
        try:
            if signal(fake, i) != signal(d, i):
                return False
        except IndexError:
            return False
    return True

def corporate(d, events, adjusted, etf):
    if adjusted:
        return 'ADJUSTED_DECLARED'
    if events:
        hit = [r for r in csv.DictReader(open(events, encoding='utf-8')) if d[0]['date'] < r['date'] <= d[-1]['date']]
        if hit:
            stop(f"原始價格區間含公司事件 {[(h['date'], h.get('type', '')) for h in hit]}；請改用還原價格（--adjusted）或切開區間")
        return 'CHECKED_NONE_IN_RANGE'
    if etf:
        stop('ETF 回測需要事件檔（--events）或還原價格（--adjusted），否則不含股利且除息跳空會失真')
    return 'NOT_CHECKED'

if __name__ == '__main__':
    a = sys.argv[1:]; p = a[0]
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if opt('--expect-sha') and opt('--expect-sha') != sha:
        stop(f'輸入 CSV 的 SHA-256 與 manifest 不符（實際 {sha}）')
    d = load(p); ce = corporate(d, opt('--events'), '--adjusted' in a, '--etf' in a); t, e, op, sk = run(d)
    out = dict(engine='bt_min v1.4', input=p, sha256=sha, rows=len(d), range=[d[0]['date'], d[-1]['date']], params=P,
               no_lookahead=check_no_lookahead(d), corporate_events=ce, skipped_zero_volume=sk, stats=stats(t, e), trades=t, open_position=op)
    if ce == 'NOT_CHECKED':
        out['note'] = '未檢查公司事件：報酬不含股利，跨除權息或拆股日的價差可能失真'
    print(json.dumps(out, ensure_ascii=False, indent=1))
