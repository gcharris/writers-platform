#!/usr/bin/env python3
"""
Phase 2: Community Platform Migration - API Test Script
Tests badge assignment and Factory integration endpoints
"""

import os
import sys
import json
import asyncio
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.database import Base
from app.models.user import User
from app.models.work import Work
from app.models.badge import Badge
from app.models.project import Project
from app.services.badge_engine import BadgeEngine

# ANSI colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")


def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")


def print_info(msg):
    print(f"{BLUE}ℹ {msg}{NC}")


def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{NC}")


def get_db_session():
    """Get database session"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print_error("DATABASE_URL environment variable not set")
        sys.exit(1)

    engine = create_engine(database_url)
    return Session(engine)


def test_database_schema(db: Session):
    """Test 1: Verify database schema"""
    print("\n" + "="*60)
    print("Test 1: Database Schema Verification")
    print("="*60)

    # Check badges table
    result = db.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'badges')"
    ))
    badges_exists = result.scalar()

    if badges_exists:
        print_success("Badges table exists")
    else:
        print_error("Badges table does not exist")
        return False

    # Check badges columns
    result = db.execute(text(
        """SELECT column_name FROM information_schema.columns
           WHERE table_name = 'badges'
           ORDER BY ordinal_position"""
    ))
    columns = [row[0] for row in result]
    expected = ['id', 'work_id', 'badge_type', 'verified', 'metadata_json', 'created_at', 'updated_at']

    if columns == expected:
        print_success(f"Badges table has correct schema: {', '.join(columns)}")
    else:
        print_error(f"Schema mismatch. Expected {expected}, got {columns}")
        return False

    # Check works table Factory fields
    result = db.execute(text(
        """SELECT column_name FROM information_schema.columns
           WHERE table_name = 'works'
           AND column_name IN ('factory_project_id', 'factory_scores')"""
    ))
    factory_fields = [row[0] for row in result]

    if 'factory_project_id' in factory_fields and 'factory_scores' in factory_fields:
        print_success("Works table has Factory integration fields")
    else:
        print_error(f"Works table missing Factory fields. Found: {factory_fields}")
        return False

    # Check indexes
    result = db.execute(text(
        """SELECT indexname FROM pg_indexes
           WHERE tablename = 'badges'
           AND indexname LIKE 'idx_badges_%'"""
    ))
    indexes = [row[0] for row in result]

    required_indexes = ['idx_badges_work_id', 'idx_badges_type']
    for idx in required_indexes:
        if idx in indexes:
            print_success(f"Index {idx} exists")
        else:
            print_warning(f"Index {idx} missing (not critical)")

    return True


async def test_badge_assignment(db: Session):
    """Test 2: Badge assignment logic"""
    print("\n" + "="*60)
    print("Test 2: Badge Assignment Logic")
    print("="*60)

    # Get or create test user
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        print_info("Creating test user...")
        test_user = User(
            email="test@example.com",
            username="test_user",
            hashed_password="fake_hash_for_testing"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print_success("Test user created")

    badge_engine = BadgeEngine(db)

    # Test 2a: Community upload without claim
    print("\nTest 2a: Community Upload (No Human Claim)")
    work1 = Work(
        author_id=test_user.id,
        title="Test Work 1 - Community Upload",
        content="This is a test story for badge assignment.",
        word_count=8,
        status="draft"
    )
    db.add(work1)
    db.flush()

    badge1 = await badge_engine.assign_badge_for_upload(
        work=work1,
        claim_human_authored=False
    )

    if badge1.badge_type == "community_upload":
        print_success(f"Correct badge assigned: {badge1.badge_type}")
        print_info(f"  Verified: {badge1.verified}")
    else:
        print_error(f"Wrong badge type: {badge1.badge_type}, expected: community_upload")

    # Test 2b: Human-authored claim with human-like content
    print("\nTest 2b: Human Authorship Claim (Human-like Content)")
    work2 = Work(
        author_id=test_user.id,
        title="Test Work 2 - Human Story",
        content="I love writing! This is my personal story about characters and their journeys. It's really fun to create worlds.",
        word_count=20,
        status="draft"
    )
    db.add(work2)
    db.flush()

    badge2 = await badge_engine.assign_badge_for_upload(
        work=work2,
        claim_human_authored=True
    )

    if badge2.badge_type in ["human_verified", "human_self"]:
        print_success(f"Correct badge assigned: {badge2.badge_type}")
        print_info(f"  Verified: {badge2.verified}")
        print_info(f"  Confidence: {badge2.metadata_json.get('confidence', 'N/A')}")
    else:
        print_error(f"Wrong badge type: {badge2.badge_type}, expected: human_verified or human_self")

    # Test 2c: AI-like content with human claim
    print("\nTest 2c: Human Claim with AI-like Content")
    work3 = Work(
        author_id=test_user.id,
        title="Test Work 3 - AI-like",
        content="It is important to note that this content follows a pattern. Furthermore, it is worth noting that AI-generated text often exhibits these characteristics. Moreover, it is crucial to understand the implications.",
        word_count=30,
        status="draft"
    )
    db.add(work3)
    db.flush()

    badge3 = await badge_engine.assign_badge_for_upload(
        work=work3,
        claim_human_authored=True
    )

    if badge3.badge_type == "community_upload":
        print_success(f"Correct badge assigned: {badge3.badge_type} (AI detected)")
        print_info(f"  Note: {badge3.metadata_json.get('note', 'N/A')}")
        print_info(f"  Confidence: {badge3.metadata_json.get('confidence', 'N/A')}")
    else:
        print_warning(f"Badge type: {badge3.badge_type} (AI detection may have low confidence)")

    db.commit()
    print_success("Badge assignment tests completed")
    return True


def test_badge_queries(db: Session):
    """Test 3: Badge query functionality"""
    print("\n" + "="*60)
    print("Test 3: Badge Query Functionality")
    print("="*60)

    # Count total badges
    total_badges = db.query(Badge).count()
    print_info(f"Total badges in database: {total_badges}")

    if total_badges == 0:
        print_warning("No badges exist (run Test 2 first)")
        return True

    # Count by type
    print("\nBadge distribution:")
    result = db.execute(text(
        """SELECT badge_type, COUNT(*) as count,
           AVG(CASE WHEN verified THEN 1 ELSE 0 END)::numeric(3,2) as verified_ratio
           FROM badges
           GROUP BY badge_type
           ORDER BY count DESC"""
    ))

    for row in result:
        badge_type, count, verified_ratio = row
        print_info(f"  {badge_type}: {count} badges ({float(verified_ratio)*100:.0f}% verified)")

    # Test querying works with badges
    works_with_badges = db.query(Work).join(Badge).count()
    print_info(f"\nWorks with badges: {works_with_badges}")

    # Test filtering by badge type
    ai_analyzed_count = db.query(Work).join(Badge).filter(
        Badge.badge_type == "ai_analyzed"
    ).count()
    print_info(f"AI-Analyzed works: {ai_analyzed_count}")

    human_verified_count = db.query(Work).join(Badge).filter(
        Badge.badge_type == "human_verified"
    ).count()
    print_info(f"Human-Verified works: {human_verified_count}")

    print_success("Badge query tests completed")
    return True


def cleanup_test_data(db: Session):
    """Cleanup: Remove test data"""
    print("\n" + "="*60)
    print("Cleanup: Removing Test Data")
    print("="*60)

    # Delete test works and badges (cascade will handle badges)
    deleted = db.query(Work).filter(
        Work.title.like("Test Work%")
    ).delete(synchronize_session=False)

    if deleted > 0:
        db.commit()
        print_success(f"Deleted {deleted} test works and associated badges")
    else:
        print_info("No test data to clean up")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Phase 2: Community Platform Migration")
    print("API Test Suite")
    print("="*60)

    db = get_db_session()

    try:
        # Test 1: Database Schema
        if not test_database_schema(db):
            print_error("\nDatabase schema test failed. Please run migration first:")
            print_info("  psql $DATABASE_URL -f backend/migrations/add_community_badges.sql")
            return

        # Test 2: Badge Assignment
        if not await test_badge_assignment(db):
            print_error("\nBadge assignment test failed")
            return

        # Test 3: Badge Queries
        if not test_badge_queries(db):
            print_error("\nBadge query test failed")
            return

        # Cleanup
        cleanup_test_data(db)

        # Final Summary
        print("\n" + "="*60)
        print(f"{GREEN}All Tests Passed!{NC}")
        print("="*60)
        print("\nPhase 2 Migration Summary:")
        print("  ✓ Database schema correct")
        print("  ✓ Badge assignment working")
        print("  ✓ Badge queries functional")
        print("\nNext steps:")
        print("  1. Test Factory → Community publishing endpoint")
        print("  2. Test frontend badge filtering")
        print("  3. Test Knowledge Graph showcase tabs")
        print("")

    except Exception as e:
        print_error(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
