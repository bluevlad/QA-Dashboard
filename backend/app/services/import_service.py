import json
import logging
from datetime import datetime

from app.core.database import get_pool
from app.models.schemas import IngestRequest

logger = logging.getLogger(__name__)


async def ingest_run(data: IngestRequest) -> int:
    """Ingest a single run into the database. Returns the DB id."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            s = data.summary

            # 1. qa_runs (upsert)
            run_row = await conn.fetchrow(
                """
                INSERT INTO qa_runs (
                    run_id, started_at, finished_at, duration_ms,
                    total_projects, healthy_projects, tested_projects,
                    total_tests, total_passed, total_failed, total_skipped,
                    raw_json
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (run_id) DO UPDATE SET
                    finished_at = EXCLUDED.finished_at,
                    duration_ms = EXCLUDED.duration_ms,
                    total_projects = EXCLUDED.total_projects,
                    healthy_projects = EXCLUDED.healthy_projects,
                    tested_projects = EXCLUDED.tested_projects,
                    total_tests = EXCLUDED.total_tests,
                    total_passed = EXCLUDED.total_passed,
                    total_failed = EXCLUDED.total_failed,
                    total_skipped = EXCLUDED.total_skipped,
                    raw_json = EXCLUDED.raw_json
                RETURNING id
                """,
                data.runId,
                datetime.fromisoformat(data.startedAt),
                datetime.fromisoformat(data.finishedAt),
                data.durationMs,
                s.totalProjects,
                s.healthyProjects,
                s.testedProjects,
                s.totalTests,
                s.totalPassed,
                s.totalFailed,
                s.totalSkipped,
                json.dumps(data.model_dump(), default=str),
            )
            run_pk = run_row["id"]

            # Clear child tables on upsert
            await conn.execute("DELETE FROM qa_health_results WHERE run_id = $1", run_pk)
            await conn.execute("DELETE FROM qa_test_results WHERE run_id = $1", run_pk)
            await conn.execute("DELETE FROM qa_suggestions WHERE run_id = $1", run_pk)
            await conn.execute("DELETE FROM qa_issue_results WHERE run_id = $1", run_pk)

            # 2. qa_health_results + qa_endpoint_results
            for hr in data.healthResults:
                hr_row = await conn.fetchrow(
                    """
                    INSERT INTO qa_health_results (run_id, project_name, healthy, checked_at, endpoints)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                    """,
                    run_pk,
                    hr.projectName,
                    hr.healthy,
                    datetime.fromisoformat(hr.checkedAt),
                    json.dumps([e.model_dump() for e in hr.endpoints], default=str),
                )
                hr_pk = hr_row["id"]

                for ep in hr.endpoints:
                    await conn.execute(
                        """
                        INSERT INTO qa_endpoint_results (
                            health_result_id, url, label, healthy,
                            status_code, response_time_ms, error
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        hr_pk,
                        ep.url,
                        ep.label,
                        ep.healthy,
                        ep.statusCode,
                        ep.responseTimeMs,
                        ep.error,
                    )

            # 3. qa_test_results + qa_failure_details
            for tr in data.testResults:
                tr_row = await conn.fetchrow(
                    """
                    INSERT INTO qa_test_results (
                        run_id, project_name, executed, skipped_reason,
                        passed, failed, skipped, total, exit_code, duration_ms, failures
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    RETURNING id
                    """,
                    run_pk,
                    tr.projectName,
                    tr.executed,
                    tr.skippedReason,
                    tr.passed,
                    tr.failed,
                    tr.skipped,
                    tr.total,
                    tr.exitCode,
                    tr.durationMs,
                    tr.failures,
                )
                tr_pk = tr_row["id"]

                if data.failureDetails:
                    for fd in data.failureDetails:
                        belongs = False
                        if fd.filePath and tr.projectName.lower() in fd.filePath.lower():
                            belongs = True
                        elif fd.suiteName and tr.projectName.lower() in fd.suiteName.lower():
                            belongs = True
                        elif not fd.filePath and not fd.suiteName:
                            belongs = True

                        if belongs:
                            await conn.execute(
                                """
                                INSERT INTO qa_failure_details (
                                    test_result_id, test_name, suite_name, file_path,
                                    error_message, category
                                ) VALUES ($1, $2, $3, $4, $5, $6)
                                """,
                                tr_pk,
                                fd.testName,
                                fd.suiteName,
                                fd.filePath,
                                fd.errorMessage,
                                fd.category,
                            )

            # 4. qa_suggestions
            if data.suggestions:
                for sg in data.suggestions:
                    await conn.execute(
                        """
                        INSERT INTO qa_suggestions (run_id, rule_id, severity, title, description, project_name)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        run_pk,
                        sg.ruleId,
                        sg.severity,
                        sg.title,
                        sg.description,
                        sg.projectName,
                    )

            # 5. qa_issue_results
            if data.issueResults:
                for ir in data.issueResults:
                    await conn.execute(
                        """
                        INSERT INTO qa_issue_results (
                            run_id, project_name, action, issue_url, issue_number, error
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        run_pk,
                        ir.projectName,
                        ir.action,
                        ir.issueUrl,
                        ir.issueNumber,
                        ir.error,
                    )

    return run_pk


async def delete_run(run_id: str) -> bool:
    """Delete a run by run_id. Returns True if deleted."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM qa_runs WHERE run_id = $1", run_id
        )
        return result == "DELETE 1"
