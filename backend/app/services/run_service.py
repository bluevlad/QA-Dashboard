import json
import math

from app.core.database import get_pool
from app.models.schemas import PaginatedRuns, RunListItem


async def get_runs(page: int = 1, size: int = 20, date_from: str | None = None, date_to: str | None = None) -> PaginatedRuns:
    pool = await get_pool()

    conditions = []
    params: list = []
    idx = 1

    if date_from:
        conditions.append(f"started_at >= ${idx}::timestamptz")
        params.append(date_from)
        idx += 1
    if date_to:
        conditions.append(f"started_at <= ${idx}::timestamptz")
        params.append(date_to)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM qa_runs {where}", *params
        )
        rows = await conn.fetch(
            f"""
            SELECT id, run_id, started_at, finished_at, duration_ms,
                   total_projects, healthy_projects, tested_projects,
                   total_tests, total_passed, total_failed, total_skipped
            FROM qa_runs
            {where}
            ORDER BY started_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params,
            size,
            (page - 1) * size,
        )

    items = [RunListItem(**dict(r)) for r in rows]
    return PaginatedRuns(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


async def get_run_detail(run_id: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        run = await conn.fetchrow(
            "SELECT * FROM qa_runs WHERE run_id = $1", run_id
        )
        if not run:
            return None

        run_pk = run["id"]

        health_rows = await conn.fetch(
            "SELECT * FROM qa_health_results WHERE run_id = $1 ORDER BY project_name",
            run_pk,
        )
        test_rows = await conn.fetch(
            "SELECT * FROM qa_test_results WHERE run_id = $1 ORDER BY project_name",
            run_pk,
        )

        test_result_ids = [r["id"] for r in test_rows]
        failure_rows = []
        if test_result_ids:
            failure_rows = await conn.fetch(
                "SELECT * FROM qa_failure_details WHERE test_result_id = ANY($1::bigint[]) ORDER BY id",
                test_result_ids,
            )

        suggestion_rows = await conn.fetch(
            "SELECT * FROM qa_suggestions WHERE run_id = $1 ORDER BY id",
            run_pk,
        )

        issue_rows = await conn.fetch(
            "SELECT * FROM qa_issue_results WHERE run_id = $1 ORDER BY id",
            run_pk,
        )

    health_results = []
    for hr in health_rows:
        d = dict(hr)
        if isinstance(d.get("endpoints"), str):
            d["endpoints"] = json.loads(d["endpoints"])
        health_results.append(d)

    return {
        "id": run["id"],
        "runId": run["run_id"],
        "startedAt": run["started_at"].isoformat(),
        "finishedAt": run["finished_at"].isoformat(),
        "durationMs": run["duration_ms"],
        "summary": {
            "totalProjects": run["total_projects"],
            "healthyProjects": run["healthy_projects"],
            "testedProjects": run["tested_projects"],
            "totalTests": run["total_tests"],
            "totalPassed": run["total_passed"],
            "totalFailed": run["total_failed"],
            "totalSkipped": run["total_skipped"],
        },
        "healthResults": health_results,
        "testResults": [dict(r) for r in test_rows],
        "failureDetails": [dict(r) for r in failure_rows],
        "suggestions": [dict(r) for r in suggestion_rows],
        "issueResults": [dict(r) for r in issue_rows],
    }
