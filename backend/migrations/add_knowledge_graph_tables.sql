-- Knowledge Graph Tables Migration
-- Creates tables for storing knowledge graphs and extraction jobs

-- Main graph storage table
CREATE TABLE IF NOT EXISTS project_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Serialized graph data (NetworkX JSON format)
    graph_data JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_extracted_scene UUID,

    -- Statistics
    entity_count INTEGER DEFAULT 0,
    relationship_count INTEGER DEFAULT 0,
    scene_count INTEGER DEFAULT 0,

    -- Extraction tracking
    total_extractions INTEGER DEFAULT 0,
    successful_extractions INTEGER DEFAULT 0,
    failed_extractions INTEGER DEFAULT 0,

    -- One graph per project
    CONSTRAINT unique_graph_per_project UNIQUE (project_id)
);

CREATE INDEX idx_project_graphs_project_id ON project_graphs(project_id);
CREATE INDEX idx_project_graphs_last_updated ON project_graphs(last_updated DESC);

-- GIN index for fast JSONB queries on graph data (CRITICAL for performance)
CREATE INDEX idx_project_graphs_graph_data_gin ON project_graphs USING GIN (graph_data);

-- Extraction jobs tracking
CREATE TABLE IF NOT EXISTS extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scene_id UUID NOT NULL REFERENCES manuscript_scenes(id) ON DELETE CASCADE,

    -- Job details
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    extractor_type VARCHAR(20) NOT NULL CHECK (extractor_type IN ('llm', 'ner', 'hybrid')),
    model_name VARCHAR(50),

    -- Results
    entities_extracted INTEGER DEFAULT 0,
    relationships_extracted INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds FLOAT,

    -- Error tracking
    error_message TEXT,

    -- Cost tracking
    tokens_used INTEGER,
    cost FLOAT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_extraction_jobs_project_id ON extraction_jobs(project_id);
CREATE INDEX idx_extraction_jobs_scene_id ON extraction_jobs(scene_id);
CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
CREATE INDEX idx_extraction_jobs_created_at ON extraction_jobs(created_at DESC);

-- Comments
COMMENT ON TABLE project_graphs IS 'Stores knowledge graphs (NetworkX format) for each project';
COMMENT ON TABLE extraction_jobs IS 'Tracks entity/relationship extraction jobs with timing and cost data';

COMMENT ON COLUMN project_graphs.graph_data IS 'Serialized NetworkX graph in node-link JSON format';
COMMENT ON COLUMN extraction_jobs.extractor_type IS 'Type of extractor used: llm (Claude/GPT), ner (spaCy), or hybrid';
