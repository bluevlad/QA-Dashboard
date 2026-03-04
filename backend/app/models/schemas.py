from datetime import datetime

from pydantic import BaseModel, Field


# --- Request (Input) models ---


class EndpointCheckIn(BaseModel):
    url: str
    label: str
    healthy: bool
    statusCode: int | None = None
    responseTimeMs: float = 0
    error: str | None = None


class HealthCheckIn(BaseModel):
    projectName: str
    healthy: bool
    checkedAt: datetime
    endpoints: list[EndpointCheckIn] = []


class TestFailureIn(BaseModel):
    testName: str
    error: str


class TestResultIn(BaseModel):
    projectName: str
    executed: bool
    skippedReason: str | None = None
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    exitCode: int = 0
    durationMs: int = 0
    failures: list[TestFailureIn] = []


class IssueReportIn(BaseModel):
    projectName: str
    action: str
    issueUrl: str | None = None
    issueNumber: int | None = None
    error: str | None = None


class RunSummaryIn(BaseModel):
    totalProjects: int = 0
    healthyProjects: int = 0
    testedProjects: int = 0
    totalTests: int = 0
    totalPassed: int = 0
    totalFailed: int = 0
    totalSkipped: int = 0


class RunImportRequest(BaseModel):
    runId: str = Field(..., max_length=20)
    startedAt: datetime
    finishedAt: datetime
    durationMs: int
    summary: RunSummaryIn = RunSummaryIn()
    healthChecks: list[HealthCheckIn] = []
    testResults: list[TestResultIn] = []
    issueReports: list[IssueReportIn] = []


class BulkImportRequest(BaseModel):
    runs: list[RunImportRequest]


class ImportResult(BaseModel):
    success: bool
    runId: str
    message: str


class BulkImportResult(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[ImportResult]


class DeleteResult(BaseModel):
    success: bool
    runId: str
    message: str


# --- Response models ---

class HealthResponse(BaseModel):
    status: str
    version: str


class EndpointCheckOut(BaseModel):
    url: str
    label: str
    healthy: bool
    status_code: int | None
    response_time_ms: float
    error: str | None


class HealthCheckOut(BaseModel):
    project_name: str
    healthy: bool
    checked_at: datetime
    endpoints: list[EndpointCheckOut] = []


class TestFailure(BaseModel):
    testName: str
    error: str


class TestRunOut(BaseModel):
    project_name: str
    executed: bool
    skipped_reason: str | None
    passed: int
    failed: int
    skipped: int
    total: int
    exit_code: int
    duration_ms: int
    failures: list[TestFailure] = []


class IssueReportOut(BaseModel):
    project_name: str
    action: str
    issue_url: str | None
    issue_number: int | None
    error: str | None


class RunSummary(BaseModel):
    id: int
    run_id: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    total_projects: int
    healthy_projects: int
    tested_projects: int
    total_tests: int
    total_passed: int
    total_failed: int
    total_skipped: int


class RunDetail(RunSummary):
    health_checks: list[HealthCheckOut] = []
    test_results: list[TestRunOut] = []
    issue_reports: list[IssueReportOut] = []


class PaginatedRuns(BaseModel):
    items: list[RunSummary]
    total: int
    page: int
    size: int
    pages: int


class ProjectStatus(BaseModel):
    project_name: str
    last_run_id: str
    last_run_at: datetime
    healthy: bool
    last_passed: int
    last_failed: int
    last_total: int
    last_duration_ms: int


class ProjectHistoryItem(BaseModel):
    run_id: str
    started_at: datetime
    healthy: bool
    passed: int
    failed: int
    total: int
    duration_ms: int


class TrendPoint(BaseModel):
    date: str
    pass_rate: float
    total_tests: int
    total_passed: int
    total_failed: int


class DurationTrendPoint(BaseModel):
    date: str
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float


class DashboardSummary(BaseModel):
    total_runs: int
    latest_run: RunSummary | None
    projects: list[ProjectStatus]
    pass_rate_trend: list[TrendPoint]
    recent_runs: list[RunSummary]
