import json
import logging
from datetime import datetime, timezone

from app.core.database import get_pool

logger = logging.getLogger(__name__)


def _parse_dt(value) -> datetime | None:
    """문자열 또는 datetime을 datetime 객체로 변환합니다."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        s = str(value)
        # 'Z' suffix를 '+00:00'으로 변환
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


async def upsert_fix_result(data: dict) -> int:
    """수정 결과를 저장하거나 업데이트합니다.

    - agent 경로 (issueNumber 있음): (project_name, issue_number) upsert
    - developer 경로 (issueNumber 없음): (project_name, commit_hash) upsert
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Engine 메타데이터 추출
        engine = data.get("engine") or {}
        engine_type = engine.get("engineType")
        engine_model = engine.get("modelName")
        engine_inference_ms = engine.get("inferenceMs")
        engine_metadata = json.dumps(engine) if engine else "{}"

        issue_number = data.get("issueNumber")
        commit_hash = data.get("commitHash")
        fix_source = data.get("fixSource", "agent")

        # developer 경로 가드: issueNumber 가 없으면 commitHash 가 있어야 dedup 가능
        if issue_number is None and not commit_hash:
            raise ValueError("issueNumber 또는 commitHash 중 하나는 반드시 있어야 합니다")

        # started_at NOT NULL 보존: developer 경로처럼 startedAt 미전달 시 completedAt 또는 now() 사용
        started_at = _parse_dt(data.get("startedAt")) or _parse_dt(data.get("completedAt")) or datetime.now(timezone.utc)
        completed_at = _parse_dt(data.get("completedAt"))

        conflict_target = (
            "(project_name, issue_number) WHERE issue_number IS NOT NULL"
            if issue_number is not None
            else "(project_name, commit_hash) WHERE issue_number IS NULL AND commit_hash IS NOT NULL"
        )

        row = await conn.fetchrow(
            f"""
            INSERT INTO qa_fix_results (
                issue_number, project_name, source_run_id,
                priority, category, strategy, status,
                branch_name, commit_hash, pr_url, pr_number,
                modified_files, verifications, compliance_score,
                engine_type, engine_model, engine_inference_ms, engine_metadata,
                error, retry_count, duration_ms,
                started_at, completed_at,
                fix_source, discovery_method, actor, prevention_rule, recurrence
            ) VALUES (
                $1, $2, $3,
                $4, $5, $6, $7,
                $8, $9, $10, $11,
                $12::jsonb, $13::jsonb, $14,
                $15, $16, $17, $18::jsonb,
                $19, $20, $21,
                $22, $23,
                $24, $25, $26, $27, $28
            )
            ON CONFLICT {conflict_target} DO UPDATE SET
                source_run_id     = EXCLUDED.source_run_id,
                priority          = EXCLUDED.priority,
                category          = EXCLUDED.category,
                strategy          = EXCLUDED.strategy,
                status            = EXCLUDED.status,
                branch_name       = EXCLUDED.branch_name,
                commit_hash       = EXCLUDED.commit_hash,
                pr_url            = EXCLUDED.pr_url,
                pr_number         = EXCLUDED.pr_number,
                modified_files    = EXCLUDED.modified_files,
                verifications     = EXCLUDED.verifications,
                compliance_score  = EXCLUDED.compliance_score,
                engine_type       = EXCLUDED.engine_type,
                engine_model      = EXCLUDED.engine_model,
                engine_inference_ms = EXCLUDED.engine_inference_ms,
                engine_metadata   = EXCLUDED.engine_metadata,
                error             = EXCLUDED.error,
                retry_count       = EXCLUDED.retry_count,
                duration_ms       = EXCLUDED.duration_ms,
                started_at        = EXCLUDED.started_at,
                completed_at      = EXCLUDED.completed_at,
                fix_source        = EXCLUDED.fix_source,
                discovery_method  = EXCLUDED.discovery_method,
                actor             = EXCLUDED.actor,
                prevention_rule   = EXCLUDED.prevention_rule,
                recurrence        = EXCLUDED.recurrence
            RETURNING id
            """,
            issue_number,
            data["projectName"],
            data.get("sourceRunId"),
            data["priority"],
            data["category"],
            data["strategy"],
            data["status"],
            data.get("branchName"),
            commit_hash,
            data.get("prUrl"),
            data.get("prNumber"),
            json.dumps([f for f in data.get("modifiedFiles", [])]),
            json.dumps([v for v in data.get("verifications", [])]),
            data.get("complianceScore"),
            engine_type,
            engine_model,
            engine_inference_ms,
            engine_metadata,
            data.get("error"),
            data.get("retryCount", 0),
            data.get("durationMs"),
            started_at,
            completed_at,
            fix_source,
            data.get("discoveryMethod"),
            data.get("actor"),
            data.get("preventionRule"),
            data.get("recurrence"),
        )
        fix_id = row["id"]

        # lifecycle_tracking: issue_number 있는 agent 경로에서만 갱신 (developer fix 는 detection 이벤트 페어 없음)
        if issue_number is not None:
            await _update_lifecycle(conn, data, fix_id)

        return fix_id


async def _update_lifecycle(conn, data: dict, fix_id: int) -> None:
    """수정 결과에 따라 lifecycle_tracking을 자동 업데이트합니다."""
    now = datetime.now(timezone.utc)
    status = data["status"]

    # 수정 상태 → lifecycle 상태 매핑
    if status in ("failed",):
        lifecycle_status = "failed"
    elif status in ("pr_created", "test_verified", "build_verified", "fix_applied"):
        lifecycle_status = "fixed"
    elif status in ("in_progress", "pending"):
        lifecycle_status = "fixing"
    elif status in ("verification_requested", "verification_passed", "verification_failed"):
        lifecycle_status = "verifying"
    elif status in ("merged", "deployed"):
        lifecycle_status = "resolved"
    else:
        lifecycle_status = "detected"

    await conn.execute(
        """
        INSERT INTO qa_lifecycle_tracking (
            issue_number, project_name,
            detected_run_id, detected_at, detection_type,
            fix_result_id, fix_started_at, fix_completed_at, fix_status,
            lifecycle_status, updated_at
        ) VALUES (
            $1, $2,
            $3, $4, $5,
            $6, $7, $8, $9,
            $10, $11
        )
        ON CONFLICT (project_name, issue_number) DO UPDATE SET
            fix_result_id    = EXCLUDED.fix_result_id,
            fix_started_at   = COALESCE(qa_lifecycle_tracking.fix_started_at, EXCLUDED.fix_started_at),
            fix_completed_at = EXCLUDED.fix_completed_at,
            fix_status       = EXCLUDED.fix_status,
            lifecycle_status = EXCLUDED.lifecycle_status,
            resolved_at      = CASE
                WHEN EXCLUDED.lifecycle_status = 'resolved' THEN $11
                ELSE qa_lifecycle_tracking.resolved_at
            END,
            updated_at       = $11
        """,
        data["issueNumber"],
        data["projectName"],
        data.get("sourceRunId"),
        now,
        data.get("category"),
        fix_id,
        _parse_dt(data["startedAt"]),
        _parse_dt(data.get("completedAt")),
        status,
        lifecycle_status,
        now,
    )


async def get_fix_results(
    project_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[dict], int]:
    """수정 결과 목록을 조회합니다."""
    pool = await get_pool()

    conditions = []
    params: list = []
    idx = 1

    if project_name:
        conditions.append(f"project_name = ${idx}")
        params.append(project_name)
        idx += 1
    if status:
        conditions.append(f"status = ${idx}")
        params.append(status)
        idx += 1
    if priority:
        conditions.append(f"priority = ${idx}")
        params.append(priority)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM qa_fix_results {where}", *params
        )

        offset = (page - 1) * size
        rows = await conn.fetch(
            f"""
            SELECT * FROM qa_fix_results
            {where}
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params,
            size,
            offset,
        )

    return [dict(r) for r in rows], total


async def get_lifecycle_items(
    project_name: str | None = None,
    lifecycle_status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[dict], int]:
    """생명주기 추적 항목을 조회합니다."""
    pool = await get_pool()

    conditions = []
    params: list = []
    idx = 1

    if project_name:
        conditions.append(f"project_name = ${idx}")
        params.append(project_name)
        idx += 1
    if lifecycle_status:
        conditions.append(f"lifecycle_status = ${idx}")
        params.append(lifecycle_status)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM qa_lifecycle_tracking {where}", *params
        )

        offset = (page - 1) * size
        rows = await conn.fetch(
            f"""
            SELECT * FROM qa_lifecycle_tracking
            {where}
            ORDER BY updated_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params,
            size,
            offset,
        )

    return [dict(r) for r in rows], total


async def get_lifecycle_summary() -> dict:
    """전체 생명주기 요약 통계를 반환합니다."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT project_name, lifecycle_status, COUNT(*) as cnt
            FROM qa_lifecycle_tracking
            GROUP BY project_name, lifecycle_status
            """
        )

    # 전체 집계
    status_counts: dict[str, int] = {
        "detected": 0,
        "fixing": 0,
        "fixed": 0,
        "verifying": 0,
        "resolved": 0,
        "regression": 0,
        "failed": 0,
    }
    by_project: dict[str, dict[str, int]] = {}

    for row in rows:
        proj = row["project_name"]
        st = row["lifecycle_status"]
        cnt = row["cnt"]

        if st in status_counts:
            status_counts[st] += cnt

        if proj not in by_project:
            by_project[proj] = {
                "detected": 0, "fixing": 0, "fixed": 0,
                "verifying": 0, "resolved": 0, "regression": 0, "failed": 0,
            }
        if st in by_project[proj]:
            by_project[proj][st] += cnt

    total = sum(status_counts.values())

    return {
        "total": total,
        **status_counts,
        "by_project": by_project,
    }


async def update_lifecycle_verification(
    project_name: str,
    issue_number: int,
    verification_run_id: str,
    passed: bool,
) -> bool:
    """QA Agent 재점검 결과로 lifecycle을 업데이트합니다."""
    pool = await get_pool()
    now = datetime.now(timezone.utc)
    new_status = "resolved" if passed else "regression"

    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE qa_lifecycle_tracking SET
                verification_run_id = $1,
                verified_at         = $2,
                verification_passed = $3,
                lifecycle_status    = $4,
                resolved_at         = CASE WHEN $3 THEN $2 ELSE resolved_at END,
                updated_at          = $2
            WHERE project_name = $5 AND issue_number = $6
              AND lifecycle_status IN ('fixed', 'verifying')
            """,
            verification_run_id,
            now,
            passed,
            new_status,
            project_name,
            issue_number,
        )
        return result == "UPDATE 1"
