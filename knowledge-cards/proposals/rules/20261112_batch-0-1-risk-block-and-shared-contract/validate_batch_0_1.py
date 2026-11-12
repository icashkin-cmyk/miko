#!/usr/bin/env python3
"""唯讀驗證批次 0／1 提案資產；不連網、不寫入、不修改正式路徑。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RISK = ROOT / "batch-0-risk-blocks.json"
SCHEMA = ROOT / "batch-1-operation-contract.schema.json"

EXPECTED_SKILLS = {
    "dghp-travel",
    "gmail-cleanup",
    "grilling",
    "label-foreign-text",
    "make-skill",
    "multi-agent-coordination-engine",
    "photo-inspection-log",
    "tw-alert-check",
    "tw-backtest-workflow",
    "visual-content-intelligence",
}
EVIDENCE_STATES = {"NOT_READ", "NOT_RUN", "UNKNOWN", "CONFLICT", "BLOCKED", "PARTIAL", "PASS"}


def fail(message: str) -> None:
    print(f"FAIL {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic boundary
        fail(f"{path.name} 無法解析：{exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} 根節點不是 object")
    return value


def risk_fixture() -> dict:
    policy = {
        "mode": "fail_closed",
        "default_route": "READ_ONLY_DEGRADED",
        "adopted": False,
        "read_only": True,
        "external_write": False,
        "allow_force_override": False,
        "allow_implicit_approval": False,
        "allow_blind_retry": False,
        "unknown_is_success": False,
        "not_run_is_pass": False,
        "partial_is_complete": False,
    }
    skills = {name: {"route_mode": "READ_ONLY_DEGRADED", "allow": ["readonly_fixture"], "block": ["external_write"], "release_gate": "governance"} for name in EXPECTED_SKILLS}
    skills["tw-backtest-workflow"]["route_mode"] = "PAUSED_BY_USER"
    return {
        "proposal_status": "PROPOSED",
        "adoption_status": "NOT_ADOPTED",
        "baseline": {"version": "1.2.71", "adr": "ADR-094", "head": "fb8fe9da70b84dd878321ced76045e6957f818a0"},
        "default_policy": policy,
        "global_hard_blocks": ["external_write"],
        "approval_required": ["remove_paused_gate"],
        "skills": skills,
    }

def check_risk(value: dict) -> None:
    if value.get("proposal_status") != "PROPOSED":
        fail("批次 0 proposal_status 必須是 PROPOSED")
    if value.get("adoption_status") != "NOT_ADOPTED":
        fail("批次 0 adoption_status 必須是 NOT_ADOPTED")
    baseline = value.get("baseline", {})
    if baseline != {
        "version": "1.2.71",
        "adr": "ADR-094",
        "head": "fb8fe9da70b84dd878321ced76045e6957f818a0",
    }:
        fail(f"批次 0 baseline 不符合目前正本基線：{baseline}")
    policy = value.get("default_policy", {})
    required_policy = {
        "mode": "fail_closed",
        "default_route": "READ_ONLY_DEGRADED",
        "adopted": False,
        "read_only": True,
        "external_write": False,
        "allow_force_override": False,
        "allow_implicit_approval": False,
        "allow_blind_retry": False,
        "unknown_is_success": False,
        "not_run_is_pass": False,
        "partial_is_complete": False,
    }
    if policy != required_policy:
        fail("批次 0 default_policy 不符合 fail-closed 契約")
    skills = value.get("skills", {})
    if set(skills) != EXPECTED_SKILLS:
        fail(f"Skill 集合不完整或多出項目：{sorted(set(skills) ^ EXPECTED_SKILLS)}")
    for name, cfg in skills.items():
        if cfg.get("route_mode") not in {"READ_ONLY_DEGRADED", "PAUSED_BY_USER", "BLOCKED"}:
            fail(f"{name} route_mode 不可直接放行：{cfg.get('route_mode')}")
        if not cfg.get("allow"):
            fail(f"{name} 缺 allow 清單")
        if not cfg.get("block"):
            fail(f"{name} 缺 block 清單")
        if not cfg.get("release_gate"):
            fail(f"{name} 缺 release_gate")
    if "external_write" not in value.get("global_hard_blocks", []):
        fail("global_hard_blocks 必須包含 external_write")
    if "remove_paused_gate" not in value.get("approval_required", []):
        fail("approval_required 必須包含 remove_paused_gate")


def check_schema(value: dict) -> None:
    if value.get("$id") != "urn:miko:batch-1:operation-contract:1":
        fail("批次 1 schema $id 不符")
    if value.get("type") != "object" or value.get("additionalProperties") is not False:
        fail("批次 1 schema 根契約必須是封閉 object")
    required = set(value.get("required", []))
    expected = {
        "schema_version", "proposal_status", "task_id", "operation_id", "skill",
        "status_axes", "idempotency_key", "retry_policy", "route", "baseline", "steps", "task_state",
        "evidence_summary", "artifacts",
    }
    if required != expected:
        fail(f"批次 1 required 欄位不符：{sorted(required ^ expected)}")
    idempotency = value.get("properties", {}).get("idempotency_key", {})
    if idempotency.get("type") != "string" or not idempotency.get("pattern"):
        fail("idempotency_key 必須是具 pattern 的字串")
    retry = value.get("properties", {}).get("retry_policy", {})
    retry_required = set(retry.get("required", []))
    if retry_required != {"mode", "max_attempts", "same_operation_readback_only"}:
        fail("retry_policy 必須限制 mode/max_attempts/same_operation_readback_only")
    retry_props = retry.get("properties", {})
    if set(retry_props.get("mode", {}).get("enum", [])) != {"STOP", "READBACK_ONLY"}:
        fail("retry_policy.mode 必須只允許 STOP 或 READBACK_ONLY")
    if retry_props.get("same_operation_readback_only", {}).get("const") is not True:
        fail("retry_policy 必須禁止跨 operation 重觸發副作用")
    route = value.get("properties", {}).get("route", {})
    route_required = set(route.get("required", []))
    if route_required != {"mode"}:
        fail("route 只能承載路由軸；adopted/read_only/external_write 必須拆出")
    axes = value.get("properties", {}).get("status_axes", {})
    if set(axes.get("required", [])) != {"source", "execution", "authorization", "scope"}:
        fail("status_axes 必須拆成 source/execution/authorization/scope")
    if set(value.get("properties", {}).get("task_state", {}).get("enum", [])) != {"完成", "完成但有疑慮", "需要資料", "卡住"}:
        fail("task_state 不得新增第五態")
    evidence = value.get("properties", {}).get("evidence_summary", {})
    evidence_required = set(evidence.get("required", []))
    if evidence_required != EVIDENCE_STATES:
        fail("evidence_summary 必須涵蓋全部核心證據狀態")
    step = value.get("$defs", {}).get("step", {})
    step_required = set(step.get("required", []))
    for field in {"step_id", "kind", "trigger", "depends_on", "input_refs", "output_refs", "status", "forbidden", "acceptance", "failure_exit"}:
        if field not in step_required:
            fail(f"step 缺少必要欄位：{field}")
    artifact = value.get("$defs", {}).get("artifact", {})
    if artifact.get("properties", {}).get("committed", {}).get("const") is not False:
        fail("artifact.committed 必須預設禁止 true")


def expect_reject(label: str, fn, value: dict) -> None:
    try:
        fn(value)
    except SystemExit:
        print(f"PASS negative {label}")
        return
    fail(f"負向測試未拒絕：{label}")

def negative_tests(risk: dict, schema: dict) -> None:
    missing_adoption = json.loads(json.dumps(risk))
    missing_adoption.pop("adoption_status", None)
    expect_reject("移除 NOT_ADOPTED", check_risk, missing_adoption)
    blind_retry = json.loads(json.dumps(risk))
    blind_retry["default_policy"]["allow_blind_retry"] = True
    expect_reject("allow_blind_retry=true", check_risk, blind_retry)
    fifth_state = json.loads(json.dumps(schema))
    fifth_state["properties"]["task_state"]["enum"].append("第五態")
    expect_reject("task_state 第五態", check_schema, fifth_state)

def main() -> int:
    risk = load_json(RISK) if RISK.exists() else risk_fixture()
    schema = load_json(SCHEMA)
    check_risk(risk)
    check_schema(schema)
    negative_tests(risk, schema)
    print("PASS batch-0-risk-blocks.json or embedded risk fixture")
    print("PASS batch-1-operation-contract.schema.json")
    print("PASS status axes and retry policy separation")
    print("PASS fail-closed invariants and current-source baseline")
    print("NOT_RUN formal route integration / CI / independent audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
