-- Community Badges and Factory Integration Migration
-- Phase 2: Community Platform Migration
-- Creates badges table and adds Factory linking to works

-- ============================================================================
-- Badges Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_id UUID NOT NULL REFERENCES works(id) ON DELETE CASCADE,

    -- Badge type
    badge_type VARCHAR(50) NOT NULL,
    -- Options: ai_analyzed, human_verified, human_self, community_upload

    -- Verification status
    verified BOOLEAN DEFAULT FALSE,

    -- Additional metadata (scores, confidence, etc.)
    metadata_json JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for badges
CREATE INDEX IF NOT EXISTS idx_badges_work_id ON badges(work_id);
CREATE INDEX IF NOT EXISTS idx_badges_type ON badges(badge_type);
CREATE INDEX IF NOT EXISTS idx_badges_verified ON badges(verified);

-- GIN index for fast JSONB queries
CREATE INDEX IF NOT EXISTS idx_badges_metadata_gin ON badges USING GIN (metadata_json);

-- Comments
COMMENT ON TABLE badges IS 'Authenticity and analysis badges for published works';
COMMENT ON COLUMN badges.badge_type IS 'Badge type: ai_analyzed (Factory), human_verified (AI detection), human_self (self-certified), community_upload (no verification)';
COMMENT ON COLUMN badges.verified IS 'Whether badge has been validated';
COMMENT ON COLUMN badges.metadata_json IS 'Stores scores, confidence, Factory project ID, etc.';

-- ============================================================================
-- Works Table - Add Factory Integration
-- ============================================================================

-- Add Factory linking columns
ALTER TABLE works
ADD COLUMN IF NOT EXISTS factory_project_id UUID REFERENCES projects(id),
ADD COLUMN IF NOT EXISTS factory_scores JSONB;

-- Indexes for Factory fields
CREATE INDEX IF NOT EXISTS idx_works_factory_project ON works(factory_project_id);

-- Comments
COMMENT ON COLUMN works.factory_project_id IS 'Link to Factory project if work was published from Factory';
COMMENT ON COLUMN works.factory_scores IS 'Stores Factory analysis scores: {best_score, hybrid_score, total_cost}';

-- ============================================================================
-- Data Migration (if needed)
-- ============================================================================

-- No existing data to migrate for new tables
-- Future: If we want to retroactively assign badges to existing works, add logic here
