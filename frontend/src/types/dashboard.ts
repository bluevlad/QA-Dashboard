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

export interface LifecycleSummaryData {
  total: number;
  detected: number;
  fixing: number;
  fixed: number;
  verifying: number;
  resolved: number;
  regression: number;
  failed: number;
  by_project: Record<string, Record<string, number>>;
}

export interface DashboardSummary {
  total_runs: number;
  latest_run: RunListItem | null;
  projects: ProjectStatus[];
  pass_rate_trend: TrendPoint[];
  recent_runs: RunListItem[];
  lifecycle_summary: LifecycleSummaryData | null;
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
  fixResults: FixResult[];
  lifecycleItems: LifecycleItem[];
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
  lifecycle_status: string | null;
  fix_status: string | null;
  fix_pr_url: string | null;
  fix_pr_number: number | null;
}

export interface ModifiedFile {
  path: string;
  changeType: string;
  linesAdded: number;
  linesDeleted: number;
}

export interface Verification {
  type: string;
  passed: boolean;
  command: string;
  output: string | null;
  error: string | null;
  durationMs: number;
}

export interface FixResult {
  id: number;
  issue_number: number;
  project_name: string;
  source_run_id: string | null;
  priority: string;
  category: string;
  strategy: string;
  status: string;
  branch_name: string | null;
  commit_hash: string | null;
  pr_url: string | null;
  pr_number: number | null;
  modified_files: ModifiedFile[];
  verifications: Verification[];
  compliance_score: string | null;
  error: string | null;
  retry_count: number;
  duration_ms: number | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

export interface LifecycleItem {
  id: number;
  issue_number: number;
  project_name: string;
  detected_run_id: string | null;
  detected_at: string | null;
  detection_type: string | null;
  fix_result_id: number | null;
  fix_started_at: string | null;
  fix_completed_at: string | null;
  fix_status: string | null;
  verification_run_id: string | null;
  verified_at: string | null;
  verification_passed: boolean | null;
  lifecycle_status: string;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  fix_pr_url: string | null;
  fix_pr_number: number | null;
  fix_compliance_score: string | null;
  fix_detail_status: string | null;
}
