#!/usr/bin/env python3
# read_ledger.py｜來源讀取紀錄：把一份文字來源切成固定行數的區塊，逐塊取得並記帳，最後由程式算覆蓋率（只用標準函式庫）
# 用途：miko-core references/source-read-log.md 的 R2「連續讀取」P 步。覆蓋率、缺塊、重複、來源是否被改過都由程式算，模型不得手算。
# 用法：
#   python3 -I -B read_ledger.py plan   <來源檔> [--lines 300] [--bytes 24000]  → 印出 JSON：檔案 SHA-256、總行數、區塊清單（每塊起訖行；不印區塊 SHA）
#   python3 -I -B read_ledger.py show   <來源檔> <第幾塊> [--lines 300] [--bytes 24000] → 印出該塊表頭、全文，最後一行 END 才印該塊 SHA-256；模型照 END 行的 SHA 記進讀取帳
#   python3 -I -B read_ledger.py verify <來源檔> <讀取帳.json> [--lines 300] [--bytes 24000] → 印出 JSON 結果
# 分塊（稽核 r9、r10）：每塊最多 --lines 行、且最多 --bytes 個 UTF-8 位元組（預設與上限 24000，低於本環境工具輸出約 30 KB 就存檔只顯示預覽的門檻；
#   r9 原用字元數，中文 12000 字約 36 KB 會超過，r10 改算 bytes）；單一行超過上限時自成一塊；--bytes 大於 24000 一律拒絕（結束碼 2）。
#   區塊 SHA 只印在正文之後的 END 行，輸出被截斷、只看到預覽就拿不到 SHA，verify 也就不會過。
# 讀取帳格式：{"file_sha256": "<plan 給的值>", "lines_per_chunk": 300, "bytes_per_chunk": 24000, "chunks_read": [{"k": 1, "sha256": "<show END 行的值>"}, ...]}
# 結束碼：0＝全文已讀；1＝PARTIAL_READ（有缺塊或區塊 SHA 不符）；3＝CONFLICT（來源檔 SHA 和讀取帳不同，讀完之後來源被改過）；2＝用法錯誤或讀不到檔（NOT_READ）
# 區塊 SHA＝sha256("chunk:<k>:<起>-<訖>\n"＋該塊內容)，永遠不等於檔案 SHA；讀取帳填 file_sha256 當區塊 SHA 一律算不符。
# 限制：區塊 SHA 只由 show 印出（和該塊全文一起），所以照抄 plan 不能過 verify；但能自行對檔案切塊算雜湊的人仍可偽造，
#       故驗收另看工具紀錄裡逐塊的 show 呼叫。本程式也不證明模型理解正確；理解要靠固定測題（references R5）。
import hashlib, json, os, sys


def _load(path):
    try:
        b = open(path, 'rb').read()
    except OSError as ex:
        print(json.dumps({'read_status': 'NOT_READ', 'reason': str(ex)}, ensure_ascii=False)); sys.exit(2)
    try:
        t = b.decode('utf-8')
    except UnicodeDecodeError:
        print(json.dumps({'read_status': 'NOT_READ', 'reason': '不是 UTF-8 文字檔'}, ensure_ascii=False)); sys.exit(2)
    return b, t.splitlines(keepends=True)


def _bounds(lines, n, c):
    # 依行數與字元數上限切塊，回傳 [(起, 訖)]（1 起算，含訖）；空檔回傳一塊 (1, 0)
    if not lines: return [(1, 0)]
    out, st, size = [], 0, 0
    for i, l in enumerate(lines):
        b = len(l.encode('utf-8'))
        if i > st and (i - st >= n or size + b > c):
            out.append((st + 1, i)); st, size = i, 0
        size += b
    out.append((st + 1, len(lines)))
    return out


def _chunks(lines, n, c=24000):
    out = []
    for st, en in _bounds(lines, n, c):
        part = ''.join(lines[st - 1:en])
        k = len(out) + 1
        # 區塊 SHA 帶區塊身分再算（稽核 r3：只有一塊時，純內容 SHA 會等於檔案 SHA，照抄 plan 的 file_sha256 就能過）
        out.append({'k': k, 'start': st, 'end': en,
                    'sha256': hashlib.sha256(f'chunk:{k}:{st}-{en}\n'.encode('utf-8') + part.encode('utf-8')).hexdigest()})
    return out


def _opt(args, name, default):
    if name in args:
        i = args.index(name)
        try:
            v = int(args[i + 1]); del args[i:i + 2]; return v
        except (IndexError, ValueError):
            print(f'{name} 後面要接正整數'); sys.exit(2)
    return default


def main(argv):
    args = list(argv)
    n = _opt(args, '--lines', 300)
    cmax = _opt(args, '--bytes', 24000)
    if cmax > 24000:
        print('--bytes 上限 24000（再大就會超過工具輸出存檔門檻，只看到預覽）'); sys.exit(2)
    if n <= 0 or cmax <= 0 or len(args) < 2 or args[0] not in ('plan', 'show', 'verify'):
        print(__doc__ or '用法見檔頭註解'); sys.exit(2)
    cmd, src = args[0], args[1]
    b, lines = _load(src)
    fsha = hashlib.sha256(b).hexdigest()
    ch = _chunks(lines, n, cmax)
    if cmd == 'plan':
        print(json.dumps({'file': os.path.basename(src), 'file_sha256': fsha, 'bytes': len(b), 'lines': len(lines),
                          'lines_per_chunk': n, 'bytes_per_chunk': cmax, 'chunks_total': len(ch),
                          'chunks': [{'k': c['k'], 'start': c['start'], 'end': c['end']} for c in ch]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == 'show':
        if len(args) < 3 or not args[2].isdigit() or not 1 <= int(args[2]) <= len(ch):
            print(f'第幾塊要是 1～{len(ch)}'); sys.exit(2)
        c = ch[int(args[2]) - 1]
        print(f'=== CHUNK {c["k"]}/{len(ch)} lines {c["start"]}-{c["end"]} file_sha256={fsha}（區塊 SHA 在最後的 END 行）===')
        sys.stdout.write(''.join(lines[c['start'] - 1:c['end']]))
        print(f'\n=== END CHUNK {c["k"]}/{len(ch)} chunk_sha256={c["sha256"]} ===')
        return 0
    # verify
    if len(args) < 3:
        print('verify 要給讀取帳 JSON'); sys.exit(2)
    try:
        led = json.load(open(args[2], encoding='utf-8'))
    except (OSError, ValueError) as ex:
        print(json.dumps({'read_status': 'NOT_READ', 'reason': f'讀取帳讀不到或不是 JSON：{ex}'}, ensure_ascii=False)); sys.exit(2)
    if isinstance(led, dict) and led.get('lines_per_chunk', n) != n:
        print(f'讀取帳的 lines_per_chunk={led.get("lines_per_chunk")} 和本次 --lines {n} 不同'); sys.exit(2)
    if isinstance(led, dict) and led.get('bytes_per_chunk', cmax) != cmax:
        print(f'讀取帳的 bytes_per_chunk={led.get("bytes_per_chunk")} 和本次 --bytes {cmax} 不同'); sys.exit(2)
    if not isinstance(led, dict) or not isinstance(led.get('chunks_read', []), list) or \
            not all(isinstance(e, dict) and type(e.get('k')) is int for e in led.get('chunks_read', [])):
        print(json.dumps({'read_status': 'NOT_READ', 'reason': '讀取帳格式不對（chunks_read 要是 [{"k": 整數, "sha256": …}]）'}, ensure_ascii=False)); sys.exit(2)
    want = {c['k']: c['sha256'] for c in ch}
    got, dup, bad = {}, [], []
    for e in led.get('chunks_read', []):
        k = e.get('k')
        if k in got: dup.append(k)
        if k not in want or e.get('sha256') != want[k] or e.get('sha256') == fsha: bad.append(k)
        else: got[k] = True
    missing = [k for k in want if k not in got]
    res = {'file': os.path.basename(src), 'file_sha256': fsha, 'ledger_file_sha256': led.get('file_sha256'),
           'chunks_total': len(ch), 'chunks_verified': len(got), 'coverage': f'{len(got)}/{len(ch)}',
           'missing': missing, 'mismatched': sorted(set(bad), key=str), 'duplicated': sorted(set(dup), key=str)}
    if led.get('file_sha256') != fsha:
        res['read_status'] = 'CONFLICT'; res['reason'] = '來源檔現在的 SHA-256 和讀取帳記的不同（讀完後被改過或讀錯檔）'; code = 3
    elif missing or bad:
        res['read_status'] = 'PARTIAL_READ'; code = 1
    else:
        res['read_status'] = '全文已讀'; code = 0
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
