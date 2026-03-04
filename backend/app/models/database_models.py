TABLES_DDL = [
    """
    CREATE TABLE IF NOT EXISTS scheduler_runs (
        id              SERIAL PRIMARY KEY,
        run_id          VARCHAR(20) NOT NULL UNIQUE,
        started_at      TIMESTAMPTZ NOT NULL,
        finished_at     TIMESTAMPTZ NOT NULL,
        duration_ms     INTEGER NOT NULL,
        total_projects  INTEGER NOT NULL DEFAULT 0,
        healthy_projects INTEGER NOT NULL DEFAULT 0,
        tested_projects INTEGER NOT NULL DEFAULT 0,
        total_tests     INTEGER NOT NULL DEFAULT 0,
        total_passed    INTEGER NOT NULL DEFAULT 0,
        total_failed    INTEGER NOT NULL DEFAULT 0,
        total_skipped   INTEGER NOT NULL DEFAULT 0,
        log_filename    VARCHAR(255) NOT NULL UNIQUE,
        imported_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_runs_started_at ON scheduler_runs(started_at)",
    """
    CREATE TABLE IF NOT EXISTS health_check_results (
        id              SERIAL PRIMARY KEY,
        run_id          INTEGER NOT NULL REFERENCES scheduler_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR(100) NOT NULL,
        healthy         BOOLEAN NOT NULL,
        checked_at      TIMESTAMPTZ NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_health_run_id ON health_check_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_health_project ON health_check_results(project_name)",
    """
    CREATE TABLE IF NOT EXISTS endpoint_check_results (
        id                  SERIAL PRIMARY KEY,
        health_check_id     INTEGER NOT NULL REFERENCES health_check_results(id) ON DELETE CASCADE,
        url                 TEXT NOT NULL,
        label               VARCHAR(200) NOT NULL,
        healthy             BOOLEAN NOT NULL,
        status_code         INTEGER,
        response_time_ms    REAL NOT NULL,
        error               TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_endpoint_health_id ON endpoint_check_results(health_check_id)",
    """
    CREATE TABLE IF NOT EXISTS test_run_results (
        id              SERIAL PRIMARY KEY,
        run_id          INTEGER NOT NULL REFERENCES scheduler_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR(100) NOT NULL,
        executed        BOOLEAN NOT NULL,
        skipped_reason  TEXT,
        passed          INTEGER NOT NULL DEFAULT 0,
        failed          INTEGER NOT NULL DEFAULT 0,
        skipped         INTEGER NOT NULL DEFAULT 0,
        total           INTEGER NOT NULL DEFAULT 0,
        exit_code       INTEGER NOT NULL DEFAULT 0,
        duration_ms     INTEGER NOT NULL DEFAULT 0,
        failures        JSONB DEFAULT '[]'::jsonb
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_test_run_id ON test_run_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_test_project ON test_run_results(project_name)",
    """
    CREATE TABLE IF NOT EXISTS issue_report_results (
        id              SERIAL PRIMARY KEY,
        run_id          INTEGER NOT NULL REFERENCES scheduler_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR(100) NOT NULL,
        action          VARCHAR(20) NOT NULL,
        issue_url       TEXT,
        issue_number    INTEGER,
        error           TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_issue_run_id ON issue_report_results(run_id)",
]
