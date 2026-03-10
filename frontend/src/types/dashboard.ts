export interface RunListItem {
  id: number;
  run_id: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  total_projects: number;
  healthy_projects: number;
  tested_projects: number;
  total_tests: number;
  total_passed: number;
  total_failed: number;
  total_skipped: number;
}

export interface ProjectStatus {
  project_name: string;
  last_checked_at: string | null;
  last_healthy: boolean | null;
  total_runs: number;
  avg_pass_rate: number | null;
  recent_failures: number;
}

export interface TrendPoint {
  date: string;
  pass_rate: number;
  total_tests: number;
  total_passed: number;
  total_failed: number;
}

export interface DurationTrendPoint {
  date: string;
  avg_duration_ms: number;
  min_duration_ms: number;
  max_duration_ms: number;
}

export interface DashboardSummary {
  total_runs: number;
  latest_run: RunListItem | null;
  projects: ProjectStatus[];
  pass_rate_trend: TrendPoint[];
  recent_runs: RunListItem[];
}

export interface RunDetail {
  id: number;
  runId: string;
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  summary: {
    totalProjects: number;
    healthyProjects: number;
    testedProjects: number;
    totalTests: number;
    totalPassed: number;
    totalFailed: number;
    totalSkipped: number;
  };
  healthResults: HealthResult[];
  testResults: TestResult[];
  failureDetails: FailureDetail[];
  suggestions: Suggestion[];
  issueResults: IssueResult[];
}

export interface HealthResult {
  id: number;
  project_name: string;
  healthy: boolean;
  checked_at: string;
  endpoints: EndpointResult[];
}

export interface EndpointResult {
  url: string;
  label: string;
  healthy: boolean;
  statusCode: number | null;
  responseTimeMs: number;
  error: string | null;
}

export interface TestResult {
  id: number;
  project_name: string;
  executed: boolean;
  skipped_reason: string | null;
  passed: number;
  failed: number;
  skipped: number;
  total: number;
  exit_code: number;
  duration_ms: number;
}

export interface FailureDetail {
  id: number;
  test_name: string;
  suite_name: string | null;
  file_path: string | null;
  error_message: string | null;
  category: string | null;
}

export interface Suggestion {
  id: number;
  rule_id: string;
  severity: string;
  title: string;
  description: string | null;
  project_name: string | null;
}

export interface IssueResult {
  id: number;
  project_name: string;
  action: string;
  issue_url: string | null;
  issue_number: number | null;
  error: string | null;
}
