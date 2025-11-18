-- Add NotebookLM integration fields to projects table
-- Phase 9: NotebookLM MCP Integration

-- Add NotebookLM notebook URLs (typed by purpose)
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS notebooklm_notebooks JSONB DEFAULT '{}';

-- Add NotebookLM configuration
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS notebooklm_config JSONB DEFAULT '{"enabled": false}';

-- Add comments for clarity
COMMENT ON COLUMN projects.notebooklm_notebooks IS
  'NotebookLM notebook URLs by type (character_research, world_building, themes). Example: {"character_research": "https://notebooklm.google.com/notebook/abc123", "world_building": "https://notebooklm.google.com/notebook/def456"}';

COMMENT ON COLUMN projects.notebooklm_config IS
  'NotebookLM configuration settings. Example: {"enabled": true, "auto_query_on_copilot": true, "configured_at": "2025-01-18T12:00:00Z"}';

-- Create index for fast lookups of enabled projects
CREATE INDEX IF NOT EXISTS idx_projects_notebooklm_enabled
ON projects ((notebooklm_config->>'enabled'))
WHERE (notebooklm_config->>'enabled')::boolean = true;

-- Create index for querying projects with specific notebook types
CREATE INDEX IF NOT EXISTS idx_projects_notebooklm_notebooks
ON projects USING GIN (notebooklm_notebooks);
