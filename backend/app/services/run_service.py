import json
import math

from app.core.database import get_pool
from app.models.schemas import (
    EndpointCheckOut,
    HealthCheckOut,
    IssueReportOut,
    PaginatedRuns,
    RunDetail,
    RunSummary,
    TestRunOut,
)


async def get_runs(page: int = 1, size: int = 20) -> PaginatedRuns:
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM scheduler_runs")
        rows = await conn.fetch(
            """
            SELECT id, run_id, started_at, finished_at, duration_ms,
                   total_projects, healthy_projects, tested_projects,
                   total_tests, total_passed, total_failed, total_skipped
            FROM scheduler_runs
            ORDER BY started_at DESC
            LIMIT $1 OFFSET $2
            """,
            size,
            (page - 1) * size,
        )

    items = [RunSummary(**dict(r)) for r in rows]
    return PaginatedRuns(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


async def get_run_detail(run_id: str) -> RunDetail | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        run_row = await conn.fetchrow(
            """
            SELECT id, run_id, started_at, finished_at, duration_ms,
                   total_projects, healthy_projects, tested_projects,
                   total_tests, total_passed, total_failed, total_skipped
            FROM scheduler_runs WHERE run_id = $1
            """,
            run_id,
        )
        if not run_row:
            return None

        db_id = run_row["id"]

        # Health checks with endpoints
        hc_rows = await conn.fetch(
            "SELECT id, project_name, healthy, checked_at FROM health_check_results WHERE run_id = $1",
            db_id,
        )
        health_checks = []
        for hc in hc_rows:
            ep_rows = await conn.fetch(
                """
                SELECT url, label, healthy, status_code, response_time_ms, error
                FROM endpoint_check_results WHERE health_check_id = $1
                """,
                hc["id"],
            )
            endpoints = [EndpointCheckOut(**dict(ep)) for ep in ep_rows]
            health_checks.append(HealthCheckOut(
                project_name=hc["project_name"],
                healthy=hc["healthy"],
                checked_at=hc["checked_at"],
                endpoints=endpoints,
            ))

        # Test results
        tr_rows = await conn.fetch(
            """
            SELECT project_name, executed, skipped_reason, passed, failed, skipped,
                   total, exit_code, duration_ms, failures
            FROM test_run_results WHERE run_id = $1
            """,
            db_id,
        )
        test_results = []
        for tr in tr_rows:
            d = dict(tr)
            failures_raw = d.pop("failures", [])
            if isinstance(failures_raw, str):
                failures_raw = json.loads(failures_raw)
            test_results.append(TestRunOut(**d, failures=failures_raw))

        # Issue reports
        ir_rows = await conn.fetch(
            """
            SELECT project_name, action, issue_url, issue_number, error
            FROM issue_report_results WHERE run_id = $1
            """,
            db_id,
        )
        issue_reports = [IssueReportOut(**dict(ir)) for ir in ir_rows]

        return RunDetail(
            **dict(run_row),
            health_checks=health_checks,
            test_results=test_results,
            issue_reports=issue_reports,
        )
