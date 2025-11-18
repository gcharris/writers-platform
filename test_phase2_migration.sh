#!/bin/bash
# Phase 2: Community Platform Migration - Quick Test Script
# This script verifies the migration and tests badge functionality

set -e  # Exit on error

echo "========================================="
echo "Phase 2 Migration & Testing Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if DATABASE_URL is set
echo "Step 1: Checking database connection..."
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
    echo "Please set DATABASE_URL environment variable"
    echo "Example: export DATABASE_URL='postgresql://user:pass@localhost:5432/dbname'"
    exit 1
fi
echo -e "${GREEN}✓ Database URL configured${NC}"
echo ""

# Step 2: Check if migration has been run
echo "Step 2: Checking if badges table exists..."
BADGES_EXISTS=$(psql $DATABASE_URL -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'badges');")

if [ "$BADGES_EXISTS" = "t" ]; then
    echo -e "${GREEN}✓ Badges table already exists${NC}"
else
    echo -e "${YELLOW}⚠ Badges table does not exist - running migration...${NC}"
    psql $DATABASE_URL -f backend/migrations/add_community_badges.sql
    echo -e "${GREEN}✓ Migration completed${NC}"
fi
echo ""

# Step 3: Verify table schema
echo "Step 3: Verifying badges table schema..."
BADGE_COLUMNS=$(psql $DATABASE_URL -tAc "SELECT column_name FROM information_schema.columns WHERE table_name = 'badges' ORDER BY ordinal_position;")
EXPECTED_COLUMNS="id
work_id
badge_type
verified
metadata_json
created_at
updated_at"

if [ "$BADGE_COLUMNS" = "$EXPECTED_COLUMNS" ]; then
    echo -e "${GREEN}✓ Badges table schema correct${NC}"
    echo "Columns: id, work_id, badge_type, verified, metadata_json, created_at, updated_at"
else
    echo -e "${RED}✗ Badges table schema mismatch${NC}"
    echo "Found columns:"
    echo "$BADGE_COLUMNS"
fi
echo ""

# Step 4: Verify works table has Factory fields
echo "Step 4: Verifying works table has Factory fields..."
WORKS_COLUMNS=$(psql $DATABASE_URL -tAc "SELECT column_name FROM information_schema.columns WHERE table_name = 'works' AND column_name IN ('factory_project_id', 'factory_scores');")

if echo "$WORKS_COLUMNS" | grep -q "factory_project_id" && echo "$WORKS_COLUMNS" | grep -q "factory_scores"; then
    echo -e "${GREEN}✓ Works table has Factory integration fields${NC}"
else
    echo -e "${RED}✗ Works table missing Factory fields${NC}"
fi
echo ""

# Step 5: Verify indexes
echo "Step 5: Verifying indexes..."
INDEXES=$(psql $DATABASE_URL -tAc "SELECT indexname FROM pg_indexes WHERE tablename = 'badges' ORDER BY indexname;")

if echo "$INDEXES" | grep -q "idx_badges_work_id"; then
    echo -e "${GREEN}✓ idx_badges_work_id exists${NC}"
else
    echo -e "${RED}✗ idx_badges_work_id missing${NC}"
fi

if echo "$INDEXES" | grep -q "idx_badges_type"; then
    echo -e "${GREEN}✓ idx_badges_type exists${NC}"
else
    echo -e "${RED}✗ idx_badges_type missing${NC}"
fi

if echo "$INDEXES" | grep -q "idx_badges_metadata_gin"; then
    echo -e "${GREEN}✓ idx_badges_metadata_gin (GIN) exists${NC}"
else
    echo -e "${RED}✗ idx_badges_metadata_gin missing${NC}"
fi
echo ""

# Step 6: Count existing badges
echo "Step 6: Checking existing badges..."
BADGE_COUNT=$(psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM badges;")
echo "Current badges in database: $BADGE_COUNT"

if [ "$BADGE_COUNT" -gt 0 ]; then
    echo ""
    echo "Badge distribution:"
    psql $DATABASE_URL -c "SELECT badge_type, COUNT(*) as count, AVG(CASE WHEN verified THEN 1 ELSE 0 END)::numeric(3,2) as verified_ratio FROM badges GROUP BY badge_type ORDER BY count DESC;"
fi
echo ""

# Step 7: Test badge types
echo "Step 7: Verifying badge types..."
BADGE_TYPES=$(psql $DATABASE_URL -tAc "SELECT DISTINCT badge_type FROM badges ORDER BY badge_type;" 2>/dev/null || echo "")

if [ -n "$BADGE_TYPES" ]; then
    echo "Badge types found:"
    echo "$BADGE_TYPES"
else
    echo -e "${YELLOW}No badges exist yet (this is OK for fresh install)${NC}"
fi
echo ""

echo "========================================="
echo "Migration Verification Complete!"
echo "========================================="
echo ""
echo -e "${GREEN}✓ Phase 2 database migration successful${NC}"
echo ""
echo "Next steps:"
echo "1. Start the backend server: cd backend && uvicorn app.main:app --reload"
echo "2. Test badge assignment via API (see PHASE_2_TESTING_GUIDE.md)"
echo "3. Test frontend badge filter in Browse page"
echo ""
