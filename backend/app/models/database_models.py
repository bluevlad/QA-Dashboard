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
    # ── Fix Results: Auto-Tobe-Agent 수정 결과 ──
    """
    CREATE TABLE IF NOT EXISTS qa_fix_results (
        id                BIGSERIAL PRIMARY KEY,
        issue_number      INTEGER NOT NULL,
        project_name      VARCHAR NOT NULL,
        source_run_id     VARCHAR,
        priority          VARCHAR(2) NOT NULL,
        category          VARCHAR NOT NULL,
        strategy          VARCHAR NOT NULL,
        status            VARCHAR NOT NULL,
        branch_name       VARCHAR,
        commit_hash       VARCHAR,
        pr_url            TEXT,
        pr_number         INTEGER,
        modified_files    JSONB DEFAULT '[]'::jsonb,
        verifications     JSONB DEFAULT '[]'::jsonb,
        compliance_score  VARCHAR,
        error             TEXT,
        retry_count       INTEGER DEFAULT 0,
        duration_ms       INTEGER,
        engine_type       VARCHAR,
        engine_model      VARCHAR,
        engine_inference_ms INTEGER,
        engine_metadata   JSONB DEFAULT '{}'::jsonb,
        started_at        TIMESTAMPTZ NOT NULL,
        completed_at      TIMESTAMPTZ,
        created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    # Engine 컬럼 마이그레이션 (기존 DB 호환)
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS engine_type VARCHAR",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS engine_model VARCHAR",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS engine_inference_ms INTEGER",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS engine_metadata JSONB DEFAULT '{}'::jsonb",
    # Fix source / discovery 컬럼 (standards/qa/FIX_RESULT_REGISTRATION.md §3)
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS fix_source VARCHAR(16) NOT NULL DEFAULT 'agent'",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS discovery_method VARCHAR(32)",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS actor VARCHAR(128)",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS prevention_rule TEXT",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS recurrence VARCHAR(32)",
    "ALTER TABLE qa_fix_results ADD COLUMN IF NOT EXISTS affected_layer VARCHAR(64)",
    # developer fix 는 issue_number 없을 수 있음 → NOT NULL 해제 (이미 적용됐으면 no-op)
    "ALTER TABLE qa_fix_results ALTER COLUMN issue_number DROP NOT NULL",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_engine ON qa_fix_results(engine_type)",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_project ON qa_fix_results(project_name)",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_issue ON qa_fix_results(issue_number)",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_status ON qa_fix_results(status)",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_source ON qa_fix_results(fix_source)",
    "CREATE INDEX IF NOT EXISTS idx_fix_results_layer ON qa_fix_results(affected_layer)",
    # UNIQUE: agent(issue_number 있음) / developer(issue_number NULL → commit_hash) 두 경로를 분리
    "DROP INDEX IF EXISTS idx_fix_results_proj_issue",
    """
    CREATE UNIQUE INDEX IF NOT EXISTS ux_fix_results_issue
        ON qa_fix_results(project_name, issue_number)
        WHERE issue_number IS NOT NULL
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS ux_fix_results_commit
        ON qa_fix_results(project_name, commit_hash)
        WHERE issue_number IS NULL AND commit_hash IS NOT NULL
    """,
    # ── Lifecycle Tracking: 점검 → 수정 → 확인 추적 ──
    """
    CREATE TABLE IF NOT EXISTS qa_lifecycle_tracking (
        id                    BIGSERIAL PRIMARY KEY,
        issue_number          INTEGER NOT NULL,
        project_name          VARCHAR NOT NULL,
        detected_run_id       VARCHAR,
        detected_at           TIMESTAMPTZ,
        detection_type        VARCHAR,
        fix_result_id         BIGINT REFERENCES qa_fix_results(id) ON DELETE SET NULL,
        fix_started_at        TIMESTAMPTZ,
        fix_completed_at      TIMESTAMPTZ,
        fix_status            VARCHAR,
        verification_run_id   VARCHAR,
        verified_at           TIMESTAMPTZ,
        verification_passed   BOOLEAN,
        lifecycle_status      VARCHAR NOT NULL DEFAULT 'detected',
        resolved_at           TIMESTAMPTZ,
        created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(project_name, issue_number)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_lifecycle_status ON qa_lifecycle_tracking(lifecycle_status)",
    "CREATE INDEX IF NOT EXISTS idx_lifecycle_project ON qa_lifecycle_tracking(project_name)",
]
