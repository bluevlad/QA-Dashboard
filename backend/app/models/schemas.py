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


# --- Fix Results (Auto-Tobe-Agent -> Dashboard) ---


class ModifiedFileIn(BaseModel):
    path: str
    changeType: str  # modified, added, deleted
    linesAdded: int = 0
    linesDeleted: int = 0


class VerificationIn(BaseModel):
    type: str  # build, test, lint
    passed: bool
    command: str
    output: str | None = None
    error: str | None = None
    durationMs: int = 0


class EngineMetadataIn(BaseModel):
    engineType: str  # "claude-code-cli" or "local-llm"
    modelName: str  # e.g. "claude-opus-4-6", "qwen2.5-coder:32b"
    inferenceMs: int = 0
    totalTokens: int | None = None
    toolCallCount: int | None = None
    fallbackUsed: bool = False
    fallbackReason: str | None = None


class FixResultIn(BaseModel):
    # agent 경로는 issueNumber 필수, developer 경로(GitHub Actions footer 파싱)는 commitHash 로 dedup
    issueNumber: int | None = None
    projectName: str
    sourceRunId: str | None = None
    priority: str
    category: str
    strategy: str
    status: str
    branchName: str | None = None
    commitHash: str | None = None
    prUrl: str | None = None
    prNumber: int | None = None
    modifiedFiles: list[ModifiedFileIn] = []
    verifications: list[VerificationIn] = []
    complianceScore: str | None = None
    engine: EngineMetadataIn | None = None
    error: str | None = None
    retryCount: int = 0
    durationMs: int | None = None
    startedAt: str | None = None
    completedAt: str | None = None
    # standards/qa/FIX_RESULT_REGISTRATION.md §3.1
    fixSource: str = Field(default="agent", pattern="^(agent|developer)$")
    discoveryMethod: str | None = None
    actor: str | None = None
    preventionRule: str | None = None
    recurrence: str | None = None


class FixResultItem(BaseModel):
    id: int
    issue_number: int
    project_name: str
    source_run_id: str | None
    priority: str
    category: str
    strategy: str
    status: str
    branch_name: str | None
    commit_hash: str | None
    pr_url: str | None
    pr_number: int | None
    modified_files: list[dict] = []
    verifications: list[dict] = []
    compliance_score: str | None
    engine_type: str | None = None
    engine_model: str | None = None
    engine_inference_ms: int | None = None
    engine_fallback_used: bool | None = None
    error: str | None
    retry_count: int
    duration_ms: int | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime


class LifecycleItem(BaseModel):
    id: int
    issue_number: int
    project_name: str
    detected_run_id: str | None
    detected_at: datetime | None
    detection_type: str | None
    fix_result_id: int | None
    fix_started_at: datetime | None
    fix_completed_at: datetime | None
    fix_status: str | None
    verification_run_id: str | None
    verified_at: datetime | None
    verification_passed: bool | None
    lifecycle_status: str
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class LifecycleSummary(BaseModel):
    total: int
    detected: int
    fixing: int
    fixed: int
    verifying: int
    resolved: int
    regression: int
    failed: int
    by_project: dict[str, dict[str, int]]
