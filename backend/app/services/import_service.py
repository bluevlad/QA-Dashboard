import json
import logging

from app.core.database import get_pool
from app.models.schemas import RunImportRequest

logger = logging.getLogger(__name__)


async def import_run(data: RunImportRequest, log_filename: str | None = None) -> int:
    """Import a single run into the database. Returns the DB id of the inserted run."""
    if log_filename is None:
        log_filename = f"http-import-{data.runId}"

    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert scheduler_runs
            s = data.summary
            run_db_id = await conn.fetchval(
                """
                INSERT INTO scheduler_runs
                    (run_id, started_at, finished_at, duration_ms,
                     total_projects, healthy_projects, tested_projects,
                     total_tests, total_passed, total_failed, total_skipped,
                     log_filename)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
                """,
                data.runId,
                data.startedAt,
                data.finishedAt,
                data.durationMs,
                s.totalProjects,
                s.healthyProjects,
                s.testedProjects,
                s.totalTests,
                s.totalPassed,
                s.totalFailed,
                s.totalSkipped,
                log_filename,
            )

            # Insert health_check_results + endpoint_check_results
            for hc in data.healthChecks:
                hc_id = await conn.fetchval(
                    """
                    INSERT INTO health_check_results
                        (run_id, project_name, healthy, checked_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    run_db_id,
                    hc.projectName,
                    hc.healthy,
                    hc.checkedAt,
                )

                for ep in hc.endpoints:
                    await conn.execute(
                        """
                        INSERT INTO endpoint_check_results
                            (health_check_id, url, label, healthy, status_code, response_time_ms, error)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        hc_id,
                        ep.url,
                        ep.label,
                        ep.healthy,
                        ep.statusCode,
                        ep.responseTimeMs,
                        ep.error,
                    )

            # Insert test_run_results
            for tr in data.testResults:
                failures_json = json.dumps(
                    [f.model_dump() for f in tr.failures]
                )
                await conn.execute(
                    """
                    INSERT INTO test_run_results
                        (run_id, project_name, executed, skipped_reason,
                         passed, failed, skipped, total, exit_code, duration_ms, failures)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb)
                    """,
                    run_db_id,
                    tr.projectName,
                    tr.executed,
                    tr.skippedReason,
                    tr.passed,
                    tr.failed,
                    tr.skipped,
                    tr.total,
                    tr.exitCode,
                    tr.durationMs,
                    failures_json,
                )

            # Insert issue_report_results
            for ir in data.issueReports:
                await conn.execute(
                    """
                    INSERT INTO issue_report_results
                        (run_id, project_name, action, issue_url, issue_number, error)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    run_db_id,
                    ir.projectName,
                    ir.action,
                    ir.issueUrl,
                    ir.issueNumber,
                    ir.error,
                )

    return run_db_id


async def delete_run(run_id: str) -> bool:
    """Delete a run by run_id (string). Returns True if a row was deleted."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM scheduler_runs WHERE run_id = $1", run_id
        )
        # result is like 'DELETE 1' or 'DELETE 0'
        return result == "DELETE 1"
