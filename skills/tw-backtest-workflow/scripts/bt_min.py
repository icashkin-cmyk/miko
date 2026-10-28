# bt_min.py｜tw-backtest-workflow 最小回測引擎｜用法：python3 bt_min.py 資料.csv
# CSV 欄位：date,open,high,low,close,volume（日期 YYYY-MM-DD 升冪）。改策略只改 signal()。
import csv, sys, json, hashlib, random
P = dict(capital=50000, fee=0.001425, fee_min=1, tax=0.003, slip=0.0, trail=0.12)

def load(p):
    d = [{k: (v if k == 'date' else float(v)) for k, v in r.items()} for r in csv.DictReader(open(p, encoding='utf-8'))]
    assert all(a['date'] < b['date'] for a, b in zip(d, d[1:])), '日期未升冪或重複'
    assert all(r['low'] <= min(r['open'], r['close']) <= max(r['open'], r['close']) <= r['high'] and r['low'] > 0 for r in d), 'OHLC 異常或價格為 0'
    return d

def sma(x, n, i):
    return sum(x[i - n + 1:i + 1]) / n if i >= n - 1 else None

def signal(d, i):  # 只能用第 i 日收盤前已知的資料：1 進場、-1 出場、0 不動
    c = [r['close'] for r in d[:i + 1]]
    f0, s0, f1, s1 = sma(c, 5, i - 1), sma(c, 20, i - 1), sma(c, 5, i), sma(c, 20, i)
    if None in (f0, s0, f1, s1):
        return 0
    return 1 if f0 <= s0 and f1 > s1 else -1 if f0 >= s0 and f1 < s1 else 0

def run(d):
    cash, sh, peak, ent, pend, trades, eq = P['capital'], 0, 0, None, 0, [], []
    for i, r in enumerate(d):
        if pend:  # 訊號隔日開盤成交（T+1）
            px = r['open'] * (1 + P['slip'] * pend)
            if pend == 1 and sh == 0:
                n = int(cash / (px * (1 + P['fee'])))  # 整股數（零股）
                if n > 0:
                    fee = max(P['fee_min'], px * n * P['fee'])
                    cash -= px * n + fee; sh = n; peak = px; ent = dict(date=r['date'], px=px, cost=px * n + fee)
            elif pend == -1 and sh > 0:
                fee = max(P['fee_min'], px * sh * P['fee']); tax = px * sh * P['tax']
                cash += px * sh - fee - tax
                trades.append(dict(entry=ent['date'], exit=r['date'], shares=sh, pnl=round(px * sh - fee - tax - ent['cost'], 1))); sh = 0
            pend = 0
        if sh:
            peak = max(peak, r['close'])
        s = signal(d, i)
        if sh == 0 and s == 1:
            pend = 1
        elif sh and (s == -1 or r['close'] <= peak * (1 - P['trail'])):
            pend = -1
        eq.append(cash + sh * r['close'])
    open_pos = dict(entry=ent['date'], shares=sh, unrealized=round(sh * d[-1]['close'] - ent['cost'], 1)) if sh else None
    return trades, eq, open_pos

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

def check_no_lookahead(d, n=30):  # 固定檢查：竄改未來資料，訊號不得改變
    rnd = random.Random(0)
    for _ in range(n):
        i = rnd.randrange(len(d) - 1); fake = [dict(r) for r in d]
        for r in fake[i + 1:]:
            r['close'] *= rnd.uniform(0.5, 1.5)
        if signal(fake, i) != signal(d, i):
            return False
    return True

if __name__ == '__main__':
    p = sys.argv[1]; d = load(p); t, e, op = run(d)
    print(json.dumps(dict(input=p, sha256=hashlib.sha256(open(p, 'rb').read()).hexdigest(), rows=len(d), range=[d[0]['date'], d[-1]['date']],
                          params=P, no_lookahead=check_no_lookahead(d), stats=stats(t, e), trades=t, open_position=op), ensure_ascii=False, indent=1))
