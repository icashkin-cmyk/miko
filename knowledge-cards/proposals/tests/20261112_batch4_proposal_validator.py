#!/usr/bin/env python3
"""批次 4 提案層驗證器：只讀檔案，不連網、不修改正式路徑。"""
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[3]
PROPOSALS = ROOT / 'knowledge-cards' / 'proposals' / 'skills' / '20261112_batch4'
HANDOFF = ROOT / 'knowledge-cards' / 'proposals' / 'handoff' / '20261112_batch4-out-of-scope'
EXPECTED = [
    'dghp-travel', 'gmail-cleanup', 'grilling', 'label-foreign-text',
    'make-skill', 'multi-agent-coordination-engine', 'tw-alert-check',
    'visual-content-intelligence',
]
TRANSFERRED = ['07-photo-inspection-log', '09-tw-backtest-workflow']
REQUIRED_MARKERS = ['PROPOSED', 'NOT_ADOPTED', 'HISTORICAL_NOT_RUNTIME']
FORBIDDEN_ADOPTION = [
    'adoption_status: ADOPTED', 'proposal_status: ADOPTED',
    'status: EFFECTIVE', 'adoption_status: EFFECTIVE',
]
VALID_TASK_STATES = {'完成', '完成但有疑慮', '需要資料', '卡住'}


def fail(message):
    print('FAIL', message)
    raise SystemExit(1)


def text_errors(text):
    errors = []
    if not text.startswith('未驗收提案'):
        errors.append('第一行不是未驗收提案')
    errors.extend(f'缺少 {marker}' for marker in REQUIRED_MARKERS if marker not in text)
    errors.extend(f'出現正式採用狀態：{marker}' for marker in FORBIDDEN_ADOPTION if marker in text)
    if 'allow_blind_retry: true' in text or 'allow_blind_retry=true' in text:
        errors.append('allow_blind_retry 不得為 true')
    return errors


def validate_task_states(states):
    """驗證候選任務態只能沿用 miko-core 四態，拒絕第五態。"""
    return set(states).issubset(VALID_TASK_STATES) and bool(set(states))


def run_negative_tests():
    sample = '未驗收提案\nPROPOSED\nNOT_ADOPTED\nHISTORICAL_NOT_RUNTIME\n'
    if not text_errors(sample.replace('NOT_ADOPTED', '')):
        fail('負向測試失敗：移除 NOT_ADOPTED 應 FAIL')
    if not text_errors(sample + 'allow_blind_retry: true\n'):
        fail('負向測試失敗：allow_blind_retry=true 應 FAIL')
    if validate_task_states(VALID_TASK_STATES | {'第五態'}):
        fail('負向測試失敗：第五種任務態應 FAIL')
    print('PASS negative_test=missing_marker_rejected')
    print('PASS negative_test=blind_retry_rejected')
    print('PASS negative_test=fifth_task_state_rejected')


def main():
    if not PROPOSALS.is_dir():
        fail(f'候選提案目錄不存在: {PROPOSALS}')
    found = []
    for name in EXPECTED:
        matches = sorted(PROPOSALS.glob(f'*-{name}/SKILL.md'))
        if len(matches) != 1:
            fail(f'缺少候選 {name}/SKILL.md')
        path = matches[0]
        text = path.read_text(encoding='utf-8')
        errors = text_errors(text)
        if errors:
            fail(f'{path}: {"；".join(errors)}')
        found.append((path, hashlib.sha256(text.encode()).hexdigest(), len(text)))

    for name in TRANSFERRED:
        candidate_path = PROPOSALS / name
        handoff_path = HANDOFF / name / 'SKILL.md'
        if candidate_path.exists():
            fail(f'{name} 不得留在本輪候選目錄')
        if not handoff_path.is_file():
            fail(f'{name} 缺少責任轉交檔：{handoff_path}')

    # 這裡必須檢查 repo 正式路徑，而不是 ROOT.glob('skills/...') 的錯誤相對路徑。
    formal_candidate = ROOT / 'skills' / '20261112_batch4'
    if formal_candidate.exists():
        fail(f'候選內容意外進入正式路徑：{formal_candidate}')

    run_negative_tests()
    print(f'PASS candidate_proposal_count={len(found)}')
    for path, digest, size in found:
        print(f'PASS {path.relative_to(ROOT)} bytes={size} sha256={digest}')
    print('PASS transferred_out_of_scope=07-photo-inspection-log,09-tw-backtest-workflow')
    print('PASS proposal_status=PROPOSED_NOT_ADOPTED')
    print('PASS route_boundary=knowledge-cards/proposals-only')
    print('NOT_RUN Gemini consensus / independent audit / Runtime integration / CI')
    return 0


if __name__ == '__main__':
    sys.exit(main())
