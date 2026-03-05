TABLES_DDL = [
    """
    CREATE TABLE IF NOT EXISTS qa_runs (
        id              BIGSERIAL PRIMARY KEY,
        run_id          VARCHAR NOT NULL UNIQUE,
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
        raw_json        JSONB,
        search_vector   TSVECTOR,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_runs_started_at ON qa_runs(started_at)",
    """
    CREATE TABLE IF NOT EXISTS qa_health_results (
        id              BIGSERIAL PRIMARY KEY,
        run_id          BIGINT NOT NULL REFERENCES qa_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR NOT NULL,
        healthy         BOOLEAN NOT NULL,
        checked_at      TIMESTAMPTZ NOT NULL,
        endpoints       JSONB NOT NULL DEFAULT '[]'::jsonb,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_health_run_id ON qa_health_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_qa_health_project ON qa_health_results(project_name)",
    """
    CREATE TABLE IF NOT EXISTS qa_endpoint_results (
        id                  BIGSERIAL PRIMARY KEY,
        health_result_id    BIGINT NOT NULL REFERENCES qa_health_results(id) ON DELETE CASCADE,
        url                 TEXT NOT NULL,
        label               VARCHAR,
        healthy             BOOLEAN NOT NULL,
        status_code         INTEGER,
        response_time_ms    DOUBLE PRECISION NOT NULL,
        error               TEXT,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_endpoint_health_id ON qa_endpoint_results(health_result_id)",
    """
    CREATE TABLE IF NOT EXISTS qa_test_results (
        id              BIGSERIAL PRIMARY KEY,
        run_id          BIGINT NOT NULL REFERENCES qa_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR NOT NULL,
        executed        BOOLEAN NOT NULL DEFAULT false,
        skipped_reason  TEXT,
        passed          INTEGER NOT NULL DEFAULT 0,
        failed          INTEGER NOT NULL DEFAULT 0,
        skipped         INTEGER NOT NULL DEFAULT 0,
        total           INTEGER NOT NULL DEFAULT 0,
        exit_code       INTEGER NOT NULL DEFAULT 0,
        duration_ms     INTEGER NOT NULL DEFAULT 0,
        failures        TEXT[] DEFAULT '{}'::text[],
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_test_run_id ON qa_test_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_qa_test_project ON qa_test_results(project_name)",
    """
    CREATE TABLE IF NOT EXISTS qa_failure_details (
        id              BIGSERIAL PRIMARY KEY,
        test_result_id  BIGINT NOT NULL REFERENCES qa_test_results(id) ON DELETE CASCADE,
        test_name       TEXT NOT NULL,
        suite_name      TEXT,
        file_path       TEXT,
        error_message   TEXT,
        category        VARCHAR,
        search_vector   TSVECTOR,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_failure_test_id ON qa_failure_details(test_result_id)",
    """
    CREATE TABLE IF NOT EXISTS qa_suggestions (
        id              BIGSERIAL PRIMARY KEY,
        run_id          BIGINT NOT NULL REFERENCES qa_runs(id) ON DELETE CASCADE,
        rule_id         VARCHAR NOT NULL,
        severity        VARCHAR NOT NULL DEFAULT 'info',
        title           TEXT NOT NULL,
        description     TEXT,
        project_name    VARCHAR,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_suggestions_run_id ON qa_suggestions(run_id)",
    """
    CREATE TABLE IF NOT EXISTS qa_issue_results (
        id              BIGSERIAL PRIMARY KEY,
        run_id          BIGINT NOT NULL REFERENCES qa_runs(id) ON DELETE CASCADE,
        project_name    VARCHAR NOT NULL,
        action          VARCHAR NOT NULL,
        issue_url       TEXT,
        issue_number    INTEGER,
        error           TEXT,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_qa_issue_run_id ON qa_issue_results(run_id)",
    """
    CREATE TABLE IF NOT EXISTS import_request_log (
        id              BIGSERIAL PRIMARY KEY,
        run_id          VARCHAR NOT NULL,
        source          VARCHAR(20) NOT NULL,
        client_ip       VARCHAR(45),
        received_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        status          VARCHAR(10) NOT NULL DEFAULT 'received',
        error_message   TEXT,
        request_size    INTEGER DEFAULT 0,
        completed_at    TIMESTAMPTZ
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_import_log_run_id ON import_request_log(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_import_log_received_at ON import_request_log(received_at)",
    "CREATE INDEX IF NOT EXISTS idx_import_log_status ON import_request_log(status)",
]
