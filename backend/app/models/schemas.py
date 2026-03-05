from datetime import datetime

from pydantic import BaseModel, Field


# --- Ingest Request (QA Agent -> Dashboard) ---


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
    checkedAt: str
    endpoints: list[EndpointCheckIn] = []


class TestFailureIn(BaseModel):
    testName: str
    suiteName: str | None = None
    filePath: str | None = None
    errorMessage: str | None = None
    category: str | None = None


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
    failures: list[str] = []


class IssueReportIn(BaseModel):
    projectName: str
    action: str
    issueUrl: str | None = None
    issueNumber: int | None = None
    error: str | None = None


class SuggestionIn(BaseModel):
    ruleId: str
    severity: str = "info"
    title: str
    description: str | None = None
    projectName: str | None = None


class RunSummaryIn(BaseModel):
    totalProjects: int = 0
    healthyProjects: int = 0
    testedProjects: int = 0
    totalTests: int = 0
    totalPassed: int = 0
    totalFailed: int = 0
    totalSkipped: int = 0


class IngestRequest(BaseModel):
    runId: str
    startedAt: str
    finishedAt: str
    durationMs: int
    healthResults: list[HealthCheckIn] = []
    testResults: list[TestResultIn] = []
    issueResults: list[IssueReportIn] | None = None
    failureDetails: list[TestFailureIn] | None = None
    suggestions: list[SuggestionIn] | None = None
    summary: RunSummaryIn = RunSummaryIn()


# --- API Response models ---


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str = "unknown"


class RunListItem(BaseModel):
    id: int
    run_id: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    total_projects: int
    healthy_projects: int
    tested_projects: int = 0
    total_tests: int
    total_passed: int
    total_failed: int
    total_skipped: int = 0


class PaginatedRuns(BaseModel):
    items: list[RunListItem]
    total: int
    page: int
    size: int
    pages: int


class ProjectStatus(BaseModel):
    project_name: str
    last_checked_at: datetime | None = None
    last_healthy: bool | None = None
    total_runs: int = 0
    avg_pass_rate: float | None = None
    recent_failures: int = 0


class ProjectHistoryItem(BaseModel):
    date: str
    healthy: bool
    passed: int = 0
    failed: int = 0
    total: int = 0
    responseTimeMs: float | None = None


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
    latest_run: RunListItem | None
    projects: list[ProjectStatus]
    pass_rate_trend: list[TrendPoint]
    recent_runs: list[RunListItem]


class ImportLogItem(BaseModel):
    id: int
    run_id: str
    source: str
    client_ip: str | None
    received_at: datetime
    status: str
    error_message: str | None
    request_size: int
    completed_at: datetime | None
