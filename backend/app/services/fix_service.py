import json
import logging
from datetime import datetime, timezone

from app.core.database import get_pool

logger = logging.getLogger(__name__)


async def upsert_fix_result(data: dict) -> int:
    """수정 결과를 저장하거나 업데이트합니다 (project_name + issue_number 기준 upsert)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO qa_fix_results (
                issue_number, project_name, source_run_id,
                priority, category, strategy, status,
                branch_name, commit_hash, pr_url, pr_number,
                modified_files, verifications, compliance_score,
                error, retry_count, duration_ms,
                started_at, completed_at
            ) VALUES (
                $1, $2, $3,
                $4, $5, $6, $7,
                $8, $9, $10, $11,
                $12::jsonb, $13::jsonb, $14,
                $15, $16, $17,
                $18, $19
            )
            ON CONFLICT (project_name, issue_number) DO UPDATE SET
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
                error             = EXCLUDED.error,
                retry_count       = EXCLUDED.retry_count,
                duration_ms       = EXCLUDED.duration_ms,
                started_at        = EXCLUDED.started_at,
                completed_at      = EXCLUDED.completed_at
            RETURNING id
            """,
            data["issueNumber"],
            data["projectName"],
            data.get("sourceRunId"),
            data["priority"],
            data["category"],
            data["strategy"],
            data["status"],
            data.get("branchName"),
            data.get("commitHash"),
            data.get("prUrl"),
            data.get("prNumber"),
            json.dumps([f for f in data.get("modifiedFiles", [])]),
            json.dumps([v for v in data.get("verifications", [])]),
            data.get("complianceScore"),
            data.get("error"),
            data.get("retryCount", 0),
            data.get("durationMs"),
            data["startedAt"],
            data.get("completedAt"),
        )
        fix_id = row["id"]

        # lifecycle_tracking 자동 업데이트
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
        data["startedAt"],
        data.get("completedAt"),
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
