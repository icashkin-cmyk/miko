---
name: tw-backtest-workflow
description: 臺股策略、月配息 ETF 或下跌預警的回測與改進時使用：把想法拆成可程式化規則、讀本機 FinMind 資料（雲端改用證交所官方日線）、用內附 bt_min.py 實算成本與統計、找虧損模式、樣本外驗證。先載入 miko-core，再依本 Skill 四段執行。一般投資問答、即時報價、台指期不使用。
---

# 臺股回測工作流 v1.4｜2026-10-30 可執行版（對齊 DGHP 規則）
載入順序：先 miko-core（四視角主流程、品質閘門），再本 Skill；§1 問問題、§2～§3 解決、§4 後設、§6 檢查，對應 miko-core §2.4。v1.3 依 2026-10-26 實跑結果加入資料取得路徑、執行步驟與附錄 A 引擎（ADR-015）。

## 0. 作用域與權威（v1.1 新增）
來源：臺股專案指令原件 V1.2-REFERENCE-CANDIDATE、ADR-001、ADR-004、四視角引擎 v3.1 §7.2（RC2 作用域 PROJECT_RC2_PROFILE_ONLY、不適用月配息）、MIKO 帳號偏好（三檔 2330／2454／2317 共同規則、OOS 與全局最優用語、策略比較 Markdown）；v1.2 增補來自 H-03、H-04（ADR-015）。
- DGHP_TW_STOCK_REBUILD（含 2330、2454、2317 三檔共同策略）：適用 RC2（PROJECT_RC2_PROFILE_ONLY，從屬 RC1）與臺股專案指令。Universe 只限 TWSE＋TPEx 可交易普通股，排除興櫃、創櫃、ETF、ETN、REIT、TDR、特別股、權證、可轉債、槓桿反向商品。
- 月配息專案（MONTHLY_INCOME_DASHBOARD）：標的是 ETF，屬另一個領域，RC2 與上面的普通股限制不適用。
- 權責：Claude 是總召（ADR-001），負責驗證、探索、審查與放行；Codex 負責工程執行；送審與結論由 MIKO 轉貼。STOP_FOR_GPT_REVIEW 等門檻只由總召以正式審查紀錄放行，不自審解鎖。
- 台指期維持停止；下單、交易、Broker、LIVE 一律不做。

原則：AI 做繁瑣驗證與篩選，進場／停損／正式採用由 MIKO 決定。回測結果不是未來保證，也不是交易訊號。

## 1. 問問題：規則化（動手前）
- 必問（缺了才問）：標的、區間、進出場規則。預設（沒說就用並寫出）：資金 50,000 元、零股整股數、手續費 0.1425%（最低 1 元）、證交稅 0.3%、滑價 0、隔日開盤成交、比較基準為同區間買進持有。
- 把模糊詞（轉強、穩定配息、風險高）拆成可計算條件：趨勢、量、突破位置、族群、停損／停利、持有期。
- 寫清：目標、不可改項、完成條件（指標門檻）。有影響結果的歧義一次問完。
- 一輪只改一個變數；改條件＝新版本，舊版結果保留對照。
- 外部績效（社群、平台、課程截圖）只當假說：先查區間、標的、成本、樣本數是否寫明；用本機資料、同成本、PIT 重現後，才可和自家結果比較。

## 2. 解決：資料
- 先用本機已驗證的 FinMind 資料夾（路徑由使用者設定）（每批有 manifest：request、rows、SHA-256、downloaded_at）。
  - TaiwanStockPrice：全市場日線 2025-01-02～2026-01-30（含 0056、00878、00919、00929、00939、00940、00713）。
  - TaiwanStockPriceAdj：還原日線 2024-05～2026-01。TaiwanStockDividend：2025 年、稀疏。
  - 以上為 2026-10-13 盤點快照；使用前重新核對範圍。缺的區間用 FinMind 補抓，先落地 CSV 再回測。
- 輸出 CSV 記來源、抓取日、區間、欄位、SHA-256；回測只讀該 CSV。
- PIT：公告日、除息日、發放日、首次可得日分開。T 日訊號只用 T 日收盤前可得資料，T+1 成交。禁 Look-ahead、注意存活者偏誤（下市／暫停表已在資料夾）。
- 歷史 Universe 必須 Point-in-Time，保留上市、下市、停牌、處置、全額交割狀態。
- RAW 不覆寫，修正另存新版並保留來源鏈；RAW 價格、還原價格、調整因子、除權息、公司事件分開存。Adjusted 與 Raw 的鍵不一致時不得靜默合併。
- Token 與帳密不寫進 Log、CSV、Manifest 或對話。
- 取得路徑（依序；2026-10-26 實測）：
  A. 本機正本：讀 MIKO 的 Mac 上列資料夾（需 MIKO 授權連接該資料夾，或由 Codex 在本機執行）。雲端工作區直接連 FinMind API 不通。
  B. 證交所官方日線（雲端可用）：`https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=YYYYMM01&stockNo=代號`，用網頁讀取工具要求逐列輸出 CSV（日期、開高低收、漲跌、成交股數），一個月一次；連續抓約 5 個月後被網站擋（實測），分批抓並保留已抓部分。殼層直連被代理擋（實測）。上櫃股的櫃買中心頁本版未實測（UNKNOWN）。
  C. MIKO 上傳 CSV。
- 落地後先跑資料檢查：日期升冪、OHLC 合理、價格不為 0、收盤差等於官方漲跌欄（漲跌欄以 X 開頭是除權息日，跳過核對）；不符就停，不回測。官方日線是未還原價，跨除權息的報酬要另計股利或改用還原價，並在報告寫明。

## 3. 解決：回測計算（用程式，不心算）
- 執行步驟：①把附錄 A 的 bt_min.py 寫成檔案，只改 signal() 實作使用者的規則（引擎只把當日以前的資料交給 signal()，讀到未來就停止），P 參數改資金、成本、移動停損；②執行 `python3 bt_min.py 資料.csv --expect-sha <manifest 的 SHA-256> [--events 事件.csv 或 --adjusted] [--etf]`（雜湊不符、原始價格跨公司事件、ETF 沒有事件檔也沒有還原價格，都會停止），保存 JSON 輸出（輸入 SHA-256、無 look-ahead 檢查、指標、逐筆交易、未平倉）；③同區間跑買進持有當基準；④依 §6 範本出比較表，交易次數不足就標樣本不足。引擎預設：期末未平倉以收盤價計未實現、不含股利。
- 成本：手續費 0.1425%（可設折扣）、證交稅股票 0.3%／ETF 0.1%、滑價參數化；稅費率使用前查證現行值。
- 成交規則：訊號隔日開盤成交；當日成交量為 0 不成交、順延到下一個有量的交易日；買進股數預留最低手續費，現金不得為負；漲跌停鎖死無法成交尚未模擬，遇到時標「未模擬」，不當成可成交。公司事件：沒有事件檔時輸出 corporate_events=NOT_CHECKED 並註明報酬不含股利；月配息 ETF 與含息報酬一律要事件檔或還原價格，否則 BLOCKED，不能只附一句提醒。
- 必報：淨利、報酬率、MDD、勝率、PF、交易次數、盈虧比、最大連敗。月配息加：含息總報酬、每月現金流、填息天數、溫度比較（領息 vs 再投入）。
- 問「最多會輸多少」優先於「最多賺多少」。
- DGHP 正式回測有實際結果時，依臺股專案底本 §6 逐欄提供全部 28 欄與適用性；底本全文 Claude 端 NOT_READ。欄名未取得前，標「28 欄未對齊（底本 NOT_READ）」，不得用自訂縮表冒充 28 欄（原件：不另縮表）；上列指標只能當補充摘要。缺值寫 UNKNOWN 或 NOT_AVAILABLE＋原因，不當 0。
- 資料足夠判定（下結論前）：交易次數、換股期數、回測月數、因缺資料跳過的比例未達門檻，標「樣本不足」，不下優劣結論；門檻由 MIKO 定（外部參考：換股 6 期以上、平均持股 5 檔以上、回測 24 個月以上、跳過的換股日不超過 50%）。選股策略另與隨機選股（同檔數、同換股日）比較，前段與後段各比一次。

## 4. 後設：改進迴圈與常見錯誤
- 常見錯誤（實跑整理）：把未實現損益當已實現；忘了除權息日造成價差跳空；把官方網頁限流當成沒有資料；只看報酬不看買進持有基準。
找方法→驗證→分析→改進→記錄→再驗證。
- 虧損模式：按行情、月份、個股、進場條件分組，找拖累期望值的因素；檢視最近 50 筆交易的執行偏差。
- 比較新舊版必須同資料、同成本；合計改善但個股劇烈退步，不自動取代主策略。
- 樣本內調參、樣本外（或 walk-forward）驗證；參數在鄰近值也要穩定，只在單點最佳視為過度擬合。
- 結論前反方檢查：假設結論錯，列最強反例、另類解釋、缺的證據。
- 失效條件：每個候選策略寫明停用重檢的條件（例：實測或樣本外回撤超過回測 MDD、連敗超過回測最大連敗），門檻由回測結果決定，不寫死。
- 共同規則：三檔共用同一套規則，不為個股設特例。歷史已測過的資料不改稱新的樣本外；已測最高不稱全局最優。
- 盤後訊號＋T+1 只是 Candidate，策略規格凍結前不是 Canonical。
- 施工依底本七層測試，從 LEVEL_0 STATIC_CHECK 到 LEVEL_6 FULL_RUN；中間層名以底本為準。任何 FAIL、BLOCKED 或關鍵 UNKNOWN 就停止擴大，只暫停受影響部分；Smoke 沒過不得 Full Run。

## 5. 下跌預警（需要時）
- 六因子（各 0–100 標準化）：趨勢破壞、動能衰竭、量價異常、波動與尾端、市場與籌碼、流動性與事件。總分 R=Σw·F（Σw=1），大盤系統風險另計避免重複。
- 五級：0–19 低、20–39 留意、40–59 警戒、60–79 高、80–100 極高；輸出附觸發原因。
- 評估不只看準確率：Precision、Recall、PR-AUC、Brier、平均提前天數、最大回撤改善、警報頻率。權重由回測決定，不寫死。

## 6. 檢查：交付與驗收
可執行程式、輸出 CSV、摘要，分列已驗證／未驗證。逐項對照原需求標完成／未完成與依據。
- 策略比較用獨立 Markdown，列出範圍、版本、淨利、獲利因子、回撤與交易證據。範本（每次比較都用）：
  | 版本 | 規則變動 | 標的 | 區間（樣本內／外） | 輸入 CSV SHA-256 | 成本設定 | 淨利 | 報酬率 | MDD | 勝率 | PF | 交易次數 | 盈虧比 | 最大連敗 | 樣本足夠 | 結論 |
  表下逐列附交易明細檔名。已測最高只寫「本輪已測最高」，不寫全局最優；歷史已測資料不稱新 OOS。DGHP 正式結果仍依 §3 的 28 欄。
- 固定檢查寫成自動測試（無 look-ahead、成本已計、輸入 CSV 的 SHA-256 與 manifest 一致，不符就停止：--expect-sha），每次改版必跑，不靠提示詞提醒。
- 流程表一律用 6 欄：步驟／交付物、負責人、前置依賴、驗收條件、證據位置、狀態與下一步（ADR-004）；交給 Codex 時用 19 欄 FINAL_HANDOFF。
- DGHP 正式工程由 Codex 執行、Claude 總召審查（ADR-001，經 MIKO 轉貼）；Claude 也直接做驗證、探索與月配息專案。（v1.0 原句「Codex 執行、GPT 審查」已由 ADR-001 取代。）
- 驗收：AC-S1 資料落地 CSV，附來源、區間、SHA-256；AC-S2 資料檢查 0 異常；AC-S3 no_lookahead 為 true，且 signal() 只收到歷史（引擎結構防護；用全域變數讀全樣本的寫法擋不住，審查時另看）；AC-S4 指標由程式輸出且含成本；AC-S5 有買進持有基準與樣本足夠判定；AC-S6 第一筆訊號與成交用獨立程式手算相符；AC-S7 公司事件已檢查或宣告還原價格（ETF 必須）；AC-S8 改引擎後 tests/check_repo.py 的 C9（買賣帳本獨立重算、偷看隔日開盤與量能的故障測試、公司事件與雜湊停止條件）全過。
- 實跑題：「2330，2025-01～05，MA5／MA20 黃金交叉進場、死亡交叉或 12% 移動停損出場，5 萬元」。2026-10-26 實跑：證交所官方日線 95 列，資料檢查 0 異常；4/29 黃金交叉、4/30 開盤 901 元買 55 股；期末未平倉，含未實現 +3,559 元（7.12%），MDD −3.38%；同期買進持有 −4,808 元（−9.62%），MDD −30.42%；已平倉 0 筆，標樣本不足、不下優劣結論；第一筆訊號與成交手算相符。AC-S1～S6 全過。
- 實跑紀錄（2026-10-30）：引擎 v1.4 重跑 2330 固定樣本，指標與未平倉完全相同；另用合成資料 tests/synthetic_cycle.csv 驗證賣出帳本 7 筆（勝 3、敗 4、最大連敗 2、零量順延 1 次），每筆損益由獨立公式重算相符。

## 附錄 A：bt_min.py（最小回測引擎；寫成檔案後執行）
```python
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
```
