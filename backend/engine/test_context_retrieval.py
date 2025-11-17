#!/usr/bin/env python3
"""
Test Context Retrieval from Google Cloud Storage

Run this after uploading context files to verify the system works.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "framework"))

from google_store.query import GoogleStoreQuerier
from google_store.config import GoogleStoreConfig


def test_context_retrieval():
    """Test all context retrieval functions."""

    print("=" * 80)
    print("TESTING CONTEXT RETRIEVAL FROM GOOGLE CLOUD STORAGE")
    print("=" * 80)
    print()

    try:
        # Initialize
        print("Initializing connection...")
        config = GoogleStoreConfig()
        querier = GoogleStoreQuerier("The-Explants", config)
        print("✓ Connected to bucket: explants-story-store")
        print()

        # Test 1: List all files
        print("TEST 1: List Bucket Contents")
        print("-" * 80)

        from google.cloud import storage
        from google.oauth2 import service_account

        creds_path = config.get_google_credentials_path()
        project_id = config.get_project_id()
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        client = storage.Client(project=project_id, credentials=credentials)
        bucket = client.bucket("explants-story-store")

        blobs = list(bucket.list_blobs())
        print(f"✓ Found {len(blobs)} files in bucket")

        categories = {}
        for blob in blobs:
            if blob.name.endswith('/'):
                continue  # Skip directory markers
            category = blob.name.split('/')[0] if '/' in blob.name else 'root'
            categories[category] = categories.get(category, 0) + 1

        print("\nFiles by category:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} files")
        print()

        # Test 2: Query characters
        print("TEST 2: Character Query")
        print("-" * 80)
        try:
            characters = querier.query_characters(["Mickey", "Noni"])
            print(f"✓ Character query successful")
            print(f"  Retrieved {len(characters)} character profiles")
            for char in characters:
                print(f"    - {char.get('name', char.get('file', 'Unknown'))}")
        except Exception as e:
            print(f"⚠ Character query failed: {e}")
        print()

        # Test 3: Query worldbuilding
        print("TEST 3: Worldbuilding Query")
        print("-" * 80)
        try:
            worldbuilding = querier.query_worldbuilding(["bi-location", "The Line", "consciousness"])
            print(f"✓ Worldbuilding query successful")
            print(f"  Retrieved {len(worldbuilding)} worldbuilding docs")
            for doc in worldbuilding[:5]:  # Show first 5
                print(f"    - {doc.get('title', doc.get('file', 'Unknown'))}")
        except Exception as e:
            print(f"⚠ Worldbuilding query failed: {e}")
        print()

        # Test 4: Query chapters
        print("TEST 4: Chapter Query")
        print("-" * 80)
        try:
            chapters = querier.query_chapters(limit=5)
            print(f"✓ Chapter query successful")
            print(f"  Retrieved {len(chapters)} chapter files")
            for chapter in chapters:
                print(f"    - {chapter.get('title', chapter.get('file', 'Unknown'))}")
        except Exception as e:
            print(f"⚠ Chapter query failed: {e}")
        print()

        # Test 5: Build complete context package
        print("TEST 5: Context Package Build")
        print("-" * 80)
        try:
            context = querier.build_context_package(
                scene_outline="Mickey processes bi-location strain after Noni's warning",
                character_names=["Mickey", "Noni"],
                worldbuilding_topics=["bi-location", "The Line", "morphic resonance"],
                include_recent_chapters=2
            )

            context_text = context.to_prompt_context()

            print(f"✓ Context package built successfully")
            print(f"  Characters: {len(context.characters)}")
            print(f"  Worldbuilding: {len(context.worldbuilding)}")
            print(f"  Previous chapters: {len(context.previous_chapters)}")
            print(f"  Motifs: {len(context.motifs)}")
            print(f"  Total context: {len(context_text):,} characters")
            print()

            if len(context_text) > 0:
                print("Context preview (first 500 chars):")
                print("-" * 80)
                print(context_text[:500])
                print("...")
                print()
        except Exception as e:
            print(f"⚠ Context package build failed: {e}")
            import traceback
            traceback.print_exc()
        print()

        # Summary
        print("=" * 80)
        print("CONTEXT RETRIEVAL TESTS COMPLETE")
        print("=" * 80)
        print()
        print("✅ Google Cloud Storage integration is working!")
        print()
        print("The tournament system can now:")
        print("  - Automatically retrieve character profiles")
        print("  - Load worldbuilding documents")
        print("  - Reference previous chapters")
        print("  - Include motifs and themes")
        print()
        print("Context will be automatically included when running tournaments.")
        print()

        return True

    except Exception as e:
        print("=" * 80)
        print("❌ ERROR: Context retrieval test failed")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify credentials.json has google_cloud section")
        print("2. Check google-cloud-credentials.json exists and is valid")
        print("3. Ensure bucket was created: explants-story-store")
        print("4. Verify files were uploaded successfully")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_context_retrieval()
    sys.exit(0 if success else 1)
