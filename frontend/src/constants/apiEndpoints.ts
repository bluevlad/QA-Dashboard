import type { ApiEndpoint } from '../types/api';

const BASE = 'http://localhost:9095';

export const API_CATEGORIES = [
  'Health',
  'Dashboard',
  'Runs',
  'Projects',
  'Trends',
  'Import',
] as const;

export const API_ENDPOINTS: ApiEndpoint[] = [
  // --- Health ---
  {
    id: 'health',
    method: 'GET',
    path: '/api/health',
    category: 'Health',
    description: 'Check if the API server is running and return the current version.',
    responseSchema: `{
  "status": "ok",
  "version": "1.0.0"
}`,
    curlExample: `curl ${BASE}/api/health`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/health")
print(resp.json())`,
    jsExample: `const resp = await fetch("${BASE}/api/health");
const data = await resp.json();
console.log(data);`,
  },

  // --- Dashboard ---
  {
    id: 'summary',
    method: 'GET',
    path: '/api/summary',
    category: 'Dashboard',
    description: 'Get the full dashboard summary: total runs, latest run, all projects, pass-rate trend, and recent runs.',
    responseSchema: `{
  "total_runs": 42,
  "latest_run": { "id": 1, "run_id": "run-20250303-0100", ... },
  "projects": [ { "project_name": "MyApp", "healthy": true, ... } ],
  "pass_rate_trend": [ { "date": "2025-03-01", "pass_rate": 98.5, ... } ],
  "recent_runs": [ ... ]
}`,
    curlExample: `curl ${BASE}/api/summary`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/summary")
data = resp.json()
print(f"Total runs: {data['total_runs']}")`,
    jsExample: `const resp = await fetch("${BASE}/api/summary");
const data = await resp.json();
console.log("Total runs:", data.total_runs);`,
  },

  // --- Runs ---
  {
    id: 'runs-list',
    method: 'GET',
    path: '/api/runs',
    category: 'Runs',
    description: 'List scheduler runs with pagination.',
    params: [
      { name: 'page', type: 'integer', required: false, description: 'Page number', defaultValue: '1' },
      { name: 'size', type: 'integer', required: false, description: 'Page size', defaultValue: '20' },
    ],
    responseSchema: `{
  "items": [ { "id": 1, "run_id": "run-20250303-0100", ... } ],
  "total": 42,
  "page": 1,
  "size": 20,
  "pages": 3
}`,
    curlExample: `curl "${BASE}/api/runs?page=1&size=10"`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/runs", params={"page": 1, "size": 10})
data = resp.json()
for run in data["items"]:
    print(run["run_id"], run["total_passed"], run["total_failed"])`,
    jsExample: `const resp = await fetch("${BASE}/api/runs?page=1&size=10");
const data = await resp.json();
data.items.forEach(run => console.log(run.run_id));`,
  },
  {
    id: 'runs-detail',
    method: 'GET',
    path: '/api/runs/{run_id}',
    category: 'Runs',
    description: 'Get detailed information for a specific run, including health checks, test results, and issue reports.',
    params: [
      { name: 'run_id', type: 'string', required: true, description: 'The run ID (e.g. "run-20250303-0100")' },
    ],
    responseSchema: `{
  "id": 1,
  "run_id": "run-20250303-0100",
  "started_at": "2025-03-03T01:00:00Z",
  "health_checks": [ ... ],
  "test_results": [ ... ],
  "issue_reports": [ ... ]
}`,
    curlExample: `curl ${BASE}/api/runs/run-20250303-0100`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/runs/run-20250303-0100")
run = resp.json()
print(f"Run {run['run_id']}: {run['total_passed']} passed, {run['total_failed']} failed")`,
    jsExample: `const resp = await fetch("${BASE}/api/runs/run-20250303-0100");
const run = await resp.json();
console.log(run);`,
  },

  // --- Projects ---
  {
    id: 'projects-list',
    method: 'GET',
    path: '/api/projects',
    category: 'Projects',
    description: 'List all projects with their latest status.',
    responseSchema: `[
  {
    "project_name": "MyApp",
    "last_run_id": "run-20250303-0100",
    "last_run_at": "2025-03-03T01:00:00Z",
    "healthy": true,
    "last_passed": 50,
    "last_failed": 0,
    "last_total": 50,
    "last_duration_ms": 12000
  }
]`,
    curlExample: `curl ${BASE}/api/projects`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/projects")
for project in resp.json():
    status = "Healthy" if project["healthy"] else "Unhealthy"
    print(f"{project['project_name']}: {status}")`,
    jsExample: `const resp = await fetch("${BASE}/api/projects");
const projects = await resp.json();
projects.forEach(p => console.log(p.project_name, p.healthy));`,
  },
  {
    id: 'projects-history',
    method: 'GET',
    path: '/api/projects/{name}/history',
    category: 'Projects',
    description: 'Get the run history for a specific project.',
    params: [
      { name: 'name', type: 'string', required: true, description: 'Project name' },
      { name: 'limit', type: 'integer', required: false, description: 'Max number of history items', defaultValue: '30' },
    ],
    responseSchema: `[
  {
    "run_id": "run-20250303-0100",
    "started_at": "2025-03-03T01:00:00Z",
    "healthy": true,
    "passed": 50,
    "failed": 0,
    "total": 50,
    "duration_ms": 12000
  }
]`,
    curlExample: `curl "${BASE}/api/projects/MyApp/history?limit=10"`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/projects/MyApp/history", params={"limit": 10})
for item in resp.json():
    print(item["run_id"], item["passed"], item["failed"])`,
    jsExample: `const resp = await fetch("${BASE}/api/projects/MyApp/history?limit=10");
const history = await resp.json();
console.log(history);`,
  },

  // --- Trends ---
  {
    id: 'trends-pass-rate',
    method: 'GET',
    path: '/api/trends/pass-rate',
    category: 'Trends',
    description: 'Get the daily test pass-rate trend.',
    params: [
      { name: 'days', type: 'integer', required: false, description: 'Number of days to look back', defaultValue: '30' },
    ],
    responseSchema: `[
  {
    "date": "2025-03-01",
    "pass_rate": 98.5,
    "total_tests": 200,
    "total_passed": 197,
    "total_failed": 3
  }
]`,
    curlExample: `curl "${BASE}/api/trends/pass-rate?days=14"`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/trends/pass-rate", params={"days": 14})
for point in resp.json():
    print(f"{point['date']}: {point['pass_rate']}%")`,
    jsExample: `const resp = await fetch("${BASE}/api/trends/pass-rate?days=14");
const trend = await resp.json();
trend.forEach(p => console.log(p.date, p.pass_rate));`,
  },
  {
    id: 'trends-duration',
    method: 'GET',
    path: '/api/trends/duration',
    category: 'Trends',
    description: 'Get the daily test duration trend.',
    params: [
      { name: 'days', type: 'integer', required: false, description: 'Number of days to look back', defaultValue: '30' },
    ],
    responseSchema: `[
  {
    "date": "2025-03-01",
    "avg_duration_ms": 15000,
    "min_duration_ms": 8000,
    "max_duration_ms": 25000
  }
]`,
    curlExample: `curl "${BASE}/api/trends/duration?days=14"`,
    pythonExample: `import requests

resp = requests.get("${BASE}/api/trends/duration", params={"days": 14})
for point in resp.json():
    print(f"{point['date']}: avg {point['avg_duration_ms']}ms")`,
    jsExample: `const resp = await fetch("${BASE}/api/trends/duration?days=14");
const trend = await resp.json();
trend.forEach(p => console.log(p.date, p.avg_duration_ms));`,
  },

  // --- Import ---
  {
    id: 'import-run',
    method: 'POST',
    path: '/api/import/run',
    category: 'Import',
    description: 'Import a single scheduler run into the database. Returns 201 on success, 409 if the run already exists.',
    requestSchema: `{
  "runId": "run-20250303-0100",
  "startedAt": "2025-03-03T01:00:00Z",
  "finishedAt": "2025-03-03T01:05:00Z",
  "durationMs": 300000,
  "summary": {
    "totalProjects": 3,
    "healthyProjects": 3,
    "testedProjects": 3,
    "totalTests": 150,
    "totalPassed": 148,
    "totalFailed": 2,
    "totalSkipped": 0
  },
  "healthChecks": [
    {
      "projectName": "MyApp",
      "healthy": true,
      "checkedAt": "2025-03-03T01:00:10Z",
      "endpoints": [
        {
          "url": "https://myapp.example.com/health",
          "label": "Health endpoint",
          "healthy": true,
          "statusCode": 200,
          "responseTimeMs": 45.3,
          "error": null
        }
      ]
    }
  ],
  "testResults": [
    {
      "projectName": "MyApp",
      "executed": true,
      "skippedReason": null,
      "passed": 50,
      "failed": 1,
      "skipped": 0,
      "total": 51,
      "exitCode": 1,
      "durationMs": 12000,
      "failures": [
        { "testName": "test_login", "error": "AssertionError: expected 200" }
      ]
    }
  ],
  "issueReports": [
    {
      "projectName": "MyApp",
      "action": "created",
      "issueUrl": "https://github.com/org/repo/issues/42",
      "issueNumber": 42,
      "error": null
    }
  ]
}`,
    responseSchema: `{
  "success": true,
  "runId": "run-20250303-0100",
  "message": "Run imported successfully"
}`,
    curlExample: `curl -X POST ${BASE}/api/import/run \\
  -H "Content-Type: application/json" \\
  -d '{
    "runId": "run-20250303-0100",
    "startedAt": "2025-03-03T01:00:00Z",
    "finishedAt": "2025-03-03T01:05:00Z",
    "durationMs": 300000,
    "summary": {
      "totalProjects": 1,
      "healthyProjects": 1,
      "testedProjects": 1,
      "totalTests": 10,
      "totalPassed": 10,
      "totalFailed": 0,
      "totalSkipped": 0
    },
    "healthChecks": [],
    "testResults": [],
    "issueReports": []
  }'`,
    pythonExample: `import requests

payload = {
    "runId": "run-20250303-0100",
    "startedAt": "2025-03-03T01:00:00Z",
    "finishedAt": "2025-03-03T01:05:00Z",
    "durationMs": 300000,
    "summary": {
        "totalProjects": 1,
        "healthyProjects": 1,
        "testedProjects": 1,
        "totalTests": 10,
        "totalPassed": 10,
        "totalFailed": 0,
        "totalSkipped": 0
    },
    "healthChecks": [],
    "testResults": [],
    "issueReports": []
}
resp = requests.post("${BASE}/api/import/run", json=payload)
print(resp.status_code, resp.json())`,
    jsExample: `const payload = {
  runId: "run-20250303-0100",
  startedAt: "2025-03-03T01:00:00Z",
  finishedAt: "2025-03-03T01:05:00Z",
  durationMs: 300000,
  summary: {
    totalProjects: 1, healthyProjects: 1, testedProjects: 1,
    totalTests: 10, totalPassed: 10, totalFailed: 0, totalSkipped: 0
  },
  healthChecks: [], testResults: [], issueReports: []
};
const resp = await fetch("${BASE}/api/import/run", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});
console.log(resp.status, await resp.json());`,
  },
  {
    id: 'import-bulk',
    method: 'POST',
    path: '/api/import/bulk',
    category: 'Import',
    description: 'Import multiple runs at once. Supports partial success — each run is imported independently.',
    requestSchema: `{
  "runs": [
    { "runId": "run-001", "startedAt": "...", "finishedAt": "...", "durationMs": 1000, ... },
    { "runId": "run-002", "startedAt": "...", "finishedAt": "...", "durationMs": 2000, ... }
  ]
}`,
    responseSchema: `{
  "total": 2,
  "succeeded": 1,
  "failed": 1,
  "results": [
    { "success": true, "runId": "run-001", "message": "Imported successfully" },
    { "success": false, "runId": "run-002", "message": "Duplicate run_id 'run-002'" }
  ]
}`,
    curlExample: `curl -X POST ${BASE}/api/import/bulk \\
  -H "Content-Type: application/json" \\
  -d '{ "runs": [ { "runId": "run-001", ... }, { "runId": "run-002", ... } ] }'`,
    pythonExample: `import requests

payload = {
    "runs": [
        {
            "runId": "run-001",
            "startedAt": "2025-03-03T01:00:00Z",
            "finishedAt": "2025-03-03T01:05:00Z",
            "durationMs": 300000,
            "summary": { "totalProjects": 1, "totalTests": 10, "totalPassed": 10,
                         "totalFailed": 0, "totalSkipped": 0,
                         "healthyProjects": 1, "testedProjects": 1 }
        }
    ]
}
resp = requests.post("${BASE}/api/import/bulk", json=payload)
result = resp.json()
print(f"Succeeded: {result['succeeded']}, Failed: {result['failed']}")`,
    jsExample: `const resp = await fetch("${BASE}/api/import/bulk", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ runs: [/* ... */] })
});
const result = await resp.json();
console.log("Succeeded:", result.succeeded, "Failed:", result.failed);`,
  },
  {
    id: 'delete-run',
    method: 'DELETE',
    path: '/api/runs/{run_id}',
    category: 'Import',
    description: 'Delete a run and all related data (health checks, test results, issue reports) via cascade.',
    params: [
      { name: 'run_id', type: 'string', required: true, description: 'The run ID to delete' },
    ],
    responseSchema: `{
  "success": true,
  "runId": "run-20250303-0100",
  "message": "Run and related data deleted successfully"
}`,
    curlExample: `curl -X DELETE ${BASE}/api/runs/run-20250303-0100`,
    pythonExample: `import requests

resp = requests.delete("${BASE}/api/runs/run-20250303-0100")
print(resp.json())`,
    jsExample: `const resp = await fetch("${BASE}/api/runs/run-20250303-0100", {
  method: "DELETE"
});
console.log(await resp.json());`,
  },
];
