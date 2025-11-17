-- Writers Factory Core - Database Schema
-- SQLite database for session tracking, results, and analytics

-- ============================================================================
-- SESSIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    context_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_workflow ON sessions(workflow_name);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started ON sessions(started_at);

-- ============================================================================
-- RESULTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS results (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    prompt TEXT NOT NULL,
    output TEXT NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    cost REAL NOT NULL,
    response_time_ms INTEGER NOT NULL,
    model_version TEXT,
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX idx_results_session ON results(session_id);
CREATE INDEX idx_results_agent ON results(agent_name);
CREATE INDEX idx_results_created ON results(created_at);

-- ============================================================================
-- SCORES
-- ============================================================================

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    score INTEGER NOT NULL,
    notes TEXT,
    scored_by TEXT NOT NULL,
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES results(id)
);

CREATE INDEX idx_scores_result ON scores(result_id);
CREATE INDEX idx_scores_dimension ON scores(dimension);

-- ============================================================================
-- WINNERS
-- ============================================================================

CREATE TABLE IF NOT EXISTS winners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    result_id TEXT NOT NULL,
    reason TEXT,
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (result_id) REFERENCES results(id)
);

CREATE INDEX idx_winners_session ON winners(session_id);
CREATE INDEX idx_winners_result ON winners(result_id);

-- ============================================================================
-- AGENT_STATS
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_stats (
    agent_name TEXT PRIMARY KEY,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost REAL DEFAULT 0.0,
    total_response_time_ms INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COST_TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS cost_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    cost REAL NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX idx_cost_session ON cost_tracking(session_id);
CREATE INDEX idx_cost_agent ON cost_tracking(agent_name);
CREATE INDEX idx_cost_created ON cost_tracking(created_at);

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- Agent performance summary
CREATE VIEW IF NOT EXISTS v_agent_performance AS
SELECT
    agent_name,
    COUNT(*) as total_generations,
    AVG(cost) as avg_cost,
    AVG(tokens_input + tokens_output) as avg_tokens,
    AVG(response_time_ms) as avg_response_time_ms,
    MIN(created_at) as first_used,
    MAX(created_at) as last_used
FROM results
GROUP BY agent_name;

-- Session cost summary
CREATE VIEW IF NOT EXISTS v_session_costs AS
SELECT
    s.id,
    s.workflow_name,
    s.started_at,
    COUNT(r.id) as num_results,
    SUM(r.cost) as total_cost,
    SUM(r.tokens_input + r.tokens_output) as total_tokens,
    AVG(r.response_time_ms) as avg_response_time_ms
FROM sessions s
LEFT JOIN results r ON s.id = r.session_id
GROUP BY s.id;

-- Agent win rates
CREATE VIEW IF NOT EXISTS v_agent_win_rates AS
SELECT
    r.agent_name,
    COUNT(DISTINCT r.session_id) as total_sessions,
    COUNT(DISTINCT w.session_id) as wins,
    CAST(COUNT(DISTINCT w.session_id) AS REAL) / COUNT(DISTINCT r.session_id) as win_rate
FROM results r
LEFT JOIN winners w ON r.id = w.result_id
GROUP BY r.agent_name;

-- Daily cost summary
CREATE VIEW IF NOT EXISTS v_daily_costs AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as num_requests,
    SUM(cost) as total_cost,
    SUM(tokens_input + tokens_output) as total_tokens,
    AVG(cost) as avg_cost_per_request
FROM results
GROUP BY DATE(created_at)
ORDER BY date DESC;
