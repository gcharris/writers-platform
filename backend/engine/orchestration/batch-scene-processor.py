#!/usr/bin/env python3
"""
Batch Scene Processing System

Processes 20-30 scene outlines overnight using the tournament framework.
Queue scenes before bed, wake up to 60-150 variations ready for scoring.

Usage:
    python3 framework/orchestration/batch-scene-processor.py \\
        --config batch-configs/volume-2-chapter-4.json \\
        --output output/batch-v2-ch4

Features:
    - Processes multiple scenes sequentially
    - Uses Gemini File Search for rich context
    - Scores with unified 100-point rubric
    - Resume capability if interrupted
    - Real-time progress monitoring
    - Cost and time tracking
    - Comprehensive summary reports

Cost: $50-100 for 20-30 scenes
Time: ~20 minutes with rate limiting
Output: 60-150 variations ready for morning scoring
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.tournament import TournamentOrchestrator
from utils.scoring import format_score_summary


class BatchSceneProcessor:
    """Processes multiple scenes in a batch overnight."""

    SUPPORTED_AGENTS = [
        'claude-sonnet-4-5',
        'gemini-1-5-pro',
        'gemini-2.0-flash-exp',
        'gpt-4o',
        'grok-2',
        'grok-2-latest',
        'claude-haiku'
    ]

    def __init__(self, config_path: str, output_dir: str,
                 resume: bool = False, verbose: bool = False):
        """
        Initialize batch processor.

        Args:
            config_path: Path to batch configuration JSON
            output_dir: Output directory for batch results
            resume: Resume from last completed scene
            verbose: Enable verbose logging
        """
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.resume = resume
        self.verbose = verbose

        self.config = None
        self.state = None
        self.state_file = self.output_dir / '.batch-state.json'
        self.log_file = self.output_dir / 'batch-log.txt'

        # Statistics
        self.start_time = None
        self.completed_scenes = []
        self.failed_scenes = []
        self.total_cost = 0.0
        self.total_variations = 0
        self.total_words = 0

    def load_config(self) -> Dict:
        """Load and validate batch configuration."""
        self.log("Loading configuration...")

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        # Validate required fields
        if 'batch_name' not in config:
            raise ValueError("Config missing 'batch_name'")

        if 'scenes' not in config or not config['scenes']:
            raise ValueError("Config missing 'scenes' array or array is empty")

        # Validate default settings
        defaults = config.get('default_settings', {})
        if 'agents' in defaults:
            for agent in defaults['agents']:
                if agent not in self.SUPPORTED_AGENTS:
                    raise ValueError(f"Unsupported agent in defaults: {agent}")

        # Validate each scene
        scene_ids = set()
        for i, scene in enumerate(config['scenes']):
            # Required fields
            required = ['id', 'outline', 'characters']
            for field in required:
                if field not in scene:
                    raise ValueError(f"Scene {i} missing required field: {field}")

            # Unique IDs
            if scene['id'] in scene_ids:
                raise ValueError(f"Duplicate scene ID: {scene['id']}")
            scene_ids.add(scene['id'])

            # Validate agents if specified
            if 'agents' in scene:
                for agent in scene['agents']:
                    if agent not in self.SUPPORTED_AGENTS:
                        raise ValueError(f"Unsupported agent in scene {scene['id']}: {agent}")

            # Validate word target
            if 'word_target' in scene:
                target = scene['word_target']
                if not (300 <= target <= 1500):
                    self.log(f"Warning: Scene {scene['id']} word_target {target} outside recommended range (300-1500)")

        self.log(f"✓ Configuration valid: {len(config['scenes'])} scenes")
        self.config = config
        return config

    def load_state(self) -> Optional[Dict]:
        """Load saved state for resume capability."""
        if not self.resume:
            return None

        if not self.state_file.exists():
            self.log("No saved state found, starting fresh")
            return None

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.log(f"✓ Loaded state: {len(state.get('completed_scenes', []))} scenes completed")
            self.completed_scenes = state.get('completed_scenes', [])
            self.total_cost = state.get('total_cost', 0.0)
            self.total_variations = state.get('total_variations', 0)
            self.total_words = state.get('total_words', 0)

            return state
        except Exception as e:
            self.log(f"Warning: Could not load state: {e}")
            return None

    def save_state(self, current_scene_id: str, current_scene_index: int):
        """Save current state for resume capability."""
        state = {
            'batch_name': self.config['batch_name'],
            'config_path': str(self.config_path),
            'started_at': self.start_time.isoformat(),
            'last_updated': datetime.now().isoformat(),
            'last_completed_scene': current_scene_id,
            'last_completed_index': current_scene_index,
            'total_scenes': len(self.config['scenes']),
            'completed_scenes': self.completed_scenes,
            'failed_scenes': self.failed_scenes,
            'total_cost': self.total_cost,
            'total_variations': self.total_variations,
            'total_words': self.total_words
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        self.state = state

    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"

        # Console output
        print(log_line)

        # File output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_line + '\n')

    def should_skip_scene(self, scene_id: str) -> bool:
        """Check if scene should be skipped (already completed)."""
        if not self.resume:
            return False

        # Check if scene directory exists with variations
        scene_dir = self.output_dir / self._sanitize_filename(scene_id)
        if scene_dir.exists():
            variations = list(scene_dir.glob('variation-*.md'))
            if variations:
                self.log(f"Skipping {scene_id} (already exists with {len(variations)} variations)")
                return True

        return False

    def _sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename."""
        import re
        # Replace invalid characters
        safe = re.sub(r'[^\w\s-]', '', text.lower())
        safe = re.sub(r'[-\s]+', '-', safe)
        return safe.strip('-')

    def process_scene(self, scene: Dict, scene_index: int, total_scenes: int) -> Dict:
        """
        Process a single scene through tournament.

        Args:
            scene: Scene configuration
            scene_index: Scene index (0-based)
            total_scenes: Total number of scenes

        Returns:
            Results dictionary with variations, scores, cost, time
        """
        scene_id = scene['id']
        scene_title = scene.get('title', scene_id)

        self.log("")
        self.log("=" * 80)
        self.log(f"SCENE {scene_index + 1}/{total_scenes}: {scene_id} \"{scene_title}\"")
        self.log("=" * 80)

        scene_start = time.time()

        # Skip if already completed
        if self.should_skip_scene(scene_id):
            return {'skipped': True, 'scene_id': scene_id}

        # Determine agents (per-scene override or defaults)
        agents = scene.get('agents')
        if not agents:
            agents = self.config.get('default_settings', {}).get('agents', ['claude-sonnet-4-5'])

        # Determine max tokens
        max_tokens = scene.get('max_tokens')
        if not max_tokens:
            word_target = scene.get('word_target', 600)
            max_tokens = int(word_target * 1.8)  # ~1.8 tokens per word

        # Build context requirements
        context_requirements = []
        context_requirements.extend(scene.get('characters', []))
        context_requirements.extend(scene.get('world_elements', []))

        # Custom instructions
        custom_instructions = []
        if 'voice_requirements' in scene:
            custom_instructions.append(f"Voice requirements: {scene['voice_requirements']}")
        if 'word_target' in scene:
            custom_instructions.append(f"Target length: ~{scene['word_target']} words")

        custom_instructions_str = '\n'.join(custom_instructions) if custom_instructions else None

        # Extract chapter from scene ID (e.g., "2.4.1" → "2.4")
        chapter = scene_id.rsplit('.', 1)[0] if '.' in scene_id else None

        # Initialize tournament
        try:
            orchestrator = TournamentOrchestrator(
                project_name="The-Explants",
                use_gemini_search=self.config.get('default_settings', {}).get('use_gemini_search', True)
            )

            # Run tournament
            self.log(f"Running tournament with {len(agents)} agents...")
            results = orchestrator.run_tournament(
                scene_outline=scene['outline'],
                chapter=chapter,
                context_requirements=context_requirements,
                custom_instructions=custom_instructions_str,
                agents=agents,
                synthesize=False,  # Don't synthesize in batch (do later)
                max_tokens=max_tokens
            )

            # Save results
            scene_dir = self.output_dir / self._sanitize_filename(scene_id)
            scene_dir.mkdir(parents=True, exist_ok=True)

            # Save variations
            variations_saved = 0
            total_words_scene = 0

            for i, var in enumerate(results.get('variations', []), 1):
                agent_name = var['agent']
                content = var['content']
                word_count = len(content.split())
                total_words_scene += word_count

                # Save variation
                var_filename = f"variation-{i}-{agent_name}.md"
                var_path = scene_dir / var_filename

                with open(var_path, 'w') as f:
                    f.write(f"# {scene_title}\n")
                    f.write(f"**Scene ID:** {scene_id}\n")
                    f.write(f"**Agent:** {agent_name}\n")
                    f.write(f"**Word Count:** {word_count}\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n---\n\n")
                    f.write(content)

                variations_saved += 1
                self.log(f"  Saved variation {i}: {agent_name} ({word_count} words)")

            # Save scores
            scores_path = scene_dir / 'scores.json'
            with open(scores_path, 'w') as f:
                json.dump(results.get('scores', {}), f, indent=2)

            # Save metadata
            metadata = {
                'scene_id': scene_id,
                'title': scene_title,
                'outline': scene['outline'],
                'characters': scene.get('characters', []),
                'world_elements': scene.get('world_elements', []),
                'agents': agents,
                'word_target': scene.get('word_target'),
                'variations_generated': variations_saved,
                'total_words': total_words_scene,
                'processing_time_seconds': time.time() - scene_start,
                'cost': results.get('cost_tracking', {}).get('total_cost', 0.0),
                'generated_at': datetime.now().isoformat()
            }

            metadata_path = scene_dir / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Update statistics
            scene_cost = results.get('cost_tracking', {}).get('total_cost', 0.0)
            self.total_cost += scene_cost
            self.total_variations += variations_saved
            self.total_words += total_words_scene

            scene_time = time.time() - scene_start

            self.log("")
            self.log(f"✓ Scene complete:")
            self.log(f"  Variations: {variations_saved}")
            self.log(f"  Words: {total_words_scene:,}")
            self.log(f"  Cost: ${scene_cost:.2f}")
            self.log(f"  Time: {scene_time:.1f}s")
            self.log(f"  Progress: {((scene_index + 1) / total_scenes * 100):.1f}%")

            self.completed_scenes.append(scene_id)

            # Save state
            self.save_state(scene_id, scene_index)

            return {
                'success': True,
                'scene_id': scene_id,
                'variations': variations_saved,
                'words': total_words_scene,
                'cost': scene_cost,
                'time': scene_time
            }

        except Exception as e:
            self.log(f"✗ Error processing scene {scene_id}: {e}", "ERROR")
            if self.verbose:
                self.log(traceback.format_exc(), "ERROR")

            self.failed_scenes.append({
                'scene_id': scene_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

            return {
                'success': False,
                'scene_id': scene_id,
                'error': str(e)
            }

    def apply_rate_limit(self):
        """Apply rate limit delay between scenes."""
        delay = self.config.get('default_settings', {}).get('rate_limit_delay', 3)
        if delay > 0:
            self.log(f"Rate limit delay: {delay}s...")
            time.sleep(delay)

    def generate_summary_reports(self):
        """Generate batch summary reports (JSON + Markdown)."""
        self.log("")
        self.log("=" * 80)
        self.log("GENERATING SUMMARY REPORTS")
        self.log("=" * 80)

        batch_name = self.config['batch_name']
        total_time = time.time() - self.start_time.timestamp()
        total_scenes = len(self.config['scenes'])
        successful_scenes = len(self.completed_scenes)
        failed_count = len(self.failed_scenes)

        # JSON Summary
        summary = {
            'batch_name': batch_name,
            'completed_at': datetime.now().isoformat(),
            'duration_seconds': total_time,
            'duration_formatted': f"{int(total_time // 60)}m {int(total_time % 60)}s",
            'status': 'complete' if failed_count == 0 else 'partial',
            'statistics': {
                'total_scenes': total_scenes,
                'successful_scenes': successful_scenes,
                'failed_scenes': failed_count,
                'total_variations': self.total_variations,
                'total_words': self.total_words,
                'total_cost': round(self.total_cost, 2),
                'avg_cost_per_scene': round(self.total_cost / successful_scenes, 2) if successful_scenes > 0 else 0,
                'avg_time_per_scene': round(total_time / successful_scenes, 1) if successful_scenes > 0 else 0
            },
            'completed_scenes': self.completed_scenes,
            'failed_scenes': self.failed_scenes
        }

        summary_json_path = self.output_dir / 'batch-summary.json'
        with open(summary_json_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.log(f"✓ Saved JSON summary: {summary_json_path}")

        # Markdown Summary
        md_lines = [
            f"# Batch Processing Summary: {batch_name}",
            "",
            f"**Completed:** {datetime.now().strftime('%Y-%m-%d %I:%M %p')}",
            f"**Duration:** {int(total_time // 60)} minutes {int(total_time % 60)} seconds",
            f"**Status:** {'✅ ' + str(successful_scenes) + '/' + str(total_scenes) + ' scenes successful' if failed_count == 0 else '⚠️ ' + str(successful_scenes) + '/' + str(total_scenes) + ' scenes successful, ' + str(failed_count) + ' failed'}",
            "",
            "## Statistics",
            "",
            f"- **Scenes processed:** {successful_scenes}/{total_scenes}",
            f"- **Variations generated:** {self.total_variations} (avg {self.total_variations / successful_scenes:.1f} per scene)" if successful_scenes > 0 else "- **Variations generated:** 0",
            f"- **Total words generated:** {self.total_words:,}",
            f"- **Total cost:** ${self.total_cost:.2f}",
            f"- **Average cost per scene:** ${self.total_cost / successful_scenes:.2f}" if successful_scenes > 0 else "- **Average cost per scene:** $0.00",
            f"- **Average time per scene:** {total_time / successful_scenes:.1f} seconds" if successful_scenes > 0 else "- **Average time per scene:** 0s",
            ""
        ]

        # Failed scenes section
        if self.failed_scenes:
            md_lines.extend([
                "## ⚠️ Failed Scenes",
                ""
            ])
            for failure in self.failed_scenes:
                md_lines.append(f"- **{failure['scene_id']}**: {failure['error']}")
            md_lines.append("")

        # Next steps
        md_lines.extend([
            "## Next Steps",
            "",
            "### Morning Workflow:",
            "",
            "1. **Quick review of variations**",
            f"   - {successful_scenes} scenes with {self.total_variations} total variations ready",
            "   - Located in individual scene directories",
            "",
            "2. **Use skill for detailed analysis:**",
            "   ```bash",
            "   # Invoke: explants-scene-analyzer-scorer skill",
            "   # Analyze: Load any scene for MODE 1 (Detailed Analysis)",
            "   ```",
            "",
            "3. **Select best variations:**",
            "   - Review scores.json in each scene directory",
            "   - Check for voice authenticity and bi-location mechanics",
            "   - Flag any scenes needing enhancement",
            "",
            "4. **Run enhancement pass on selected variations**",
            "   - Use explants-scene-enhancement skill",
            "   - Focus on voice markers and physical details",
            "",
            "5. **Final validation with skill before publication**",
            "",
            "## Files Ready For Skill Scoring",
            "",
            f"All variations saved in `{self.output_dir}/` with individual scene folders.",
            "Each folder contains:",
            "- variation-N-agent-name.md files",
            "- scores.json (unified 100-point rubric)",
            "- metadata.json (scene details)",
            "",
            f"**Estimated time to complete scoring + selection:** 2-3 hours",
            f"**Estimated time saved by batch processing:** {successful_scenes}+ hours",
            ""
        ])

        summary_md_path = self.output_dir / 'batch-summary.md'
        with open(summary_md_path, 'w') as f:
            f.write('\n'.join(md_lines))

        self.log(f"✓ Saved Markdown summary: {summary_md_path}")

        # Next steps file
        next_steps_path = self.output_dir / 'next-steps.md'
        with open(next_steps_path, 'w') as f:
            f.write('\n'.join(md_lines[md_lines.index("## Next Steps"):]))

        self.log(f"✓ Saved next steps: {next_steps_path}")

    def run(self):
        """Run the batch processing workflow."""
        self.start_time = datetime.now()

        try:
            # Load configuration
            self.load_config()

            # Load state if resuming
            self.load_state()

            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Print batch header
            batch_name = self.config['batch_name']
            total_scenes = len(self.config['scenes'])

            self.log("")
            self.log("=" * 80)
            self.log(f"BATCH PROCESSING: {batch_name}")
            self.log("=" * 80)
            self.log(f"Total scenes: {total_scenes}")
            self.log(f"Output directory: {self.output_dir}")
            self.log(f"Resume mode: {'enabled' if self.resume else 'disabled'}")
            self.log("")

            # Process each scene
            for i, scene in enumerate(self.config['scenes']):
                try:
                    result = self.process_scene(scene, i, total_scenes)

                    # Apply rate limit (except after last scene)
                    if i < total_scenes - 1 and not result.get('skipped'):
                        self.apply_rate_limit()

                except KeyboardInterrupt:
                    self.log("\n\nBatch processing interrupted by user", "WARNING")
                    self.log("State saved. Use --resume to continue.")
                    return False

                except Exception as e:
                    self.log(f"Unexpected error processing scene: {e}", "ERROR")
                    if self.verbose:
                        self.log(traceback.format_exc(), "ERROR")
                    # Continue with next scene

            # Generate summary reports
            self.generate_summary_reports()

            # Final summary
            self.log("")
            self.log("=" * 80)
            self.log("BATCH COMPLETE")
            self.log("=" * 80)
            self.log(f"✓ Scenes processed: {len(self.completed_scenes)}/{total_scenes}")
            self.log(f"✓ Variations generated: {self.total_variations}")
            self.log(f"✓ Total cost: ${self.total_cost:.2f}")
            self.log(f"✓ Total time: {int((time.time() - self.start_time.timestamp()) // 60)}m {int((time.time() - self.start_time.timestamp()) % 60)}s")
            self.log(f"✓ Output: {self.output_dir}/")
            self.log("")
            self.log("See batch-summary.md for detailed report and next steps.")
            self.log("")

            return True

        except Exception as e:
            self.log(f"Fatal error: {e}", "ERROR")
            if self.verbose:
                self.log(traceback.format_exc(), "ERROR")
            return False


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Batch Scene Processing System - Process 20-30 scenes overnight",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 framework/orchestration/batch-scene-processor.py \\
      --config batch-configs/volume-2-chapter-4.json \\
      --output output/batch-v2-ch4

  # Resume interrupted batch
  python3 framework/orchestration/batch-scene-processor.py \\
      --config batch-configs/volume-2-chapter-4.json \\
      --output output/batch-v2-ch4 \\
      --resume

  # Dry run (validate config only)
  python3 framework/orchestration/batch-scene-processor.py \\
      --config batch-configs/test-batch.json \\
      --dry-run

  # Verbose logging
  python3 framework/orchestration/batch-scene-processor.py \\
      --config batch-configs/volume-2-chapter-4.json \\
      --output output/batch-v2-ch4 \\
      --verbose
        """
    )

    parser.add_argument('--config', required=True,
                       help="Path to batch configuration JSON file")
    parser.add_argument('--output', required=True,
                       help="Output directory for batch results")
    parser.add_argument('--resume', action='store_true',
                       help="Resume from last completed scene")
    parser.add_argument('--dry-run', action='store_true',
                       help="Validate configuration without processing")
    parser.add_argument('--verbose', action='store_true',
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Create processor
    processor = BatchSceneProcessor(
        config_path=args.config,
        output_dir=args.output,
        resume=args.resume,
        verbose=args.verbose
    )

    # Dry run mode
    if args.dry_run:
        print("=" * 80)
        print("DRY RUN MODE - Configuration Validation")
        print("=" * 80)
        print()

        try:
            config = processor.load_config()
            print(f"✓ Configuration valid")
            print(f"  Batch name: {config['batch_name']}")
            print(f"  Total scenes: {len(config['scenes'])}")
            print(f"  Default agents: {config.get('default_settings', {}).get('agents', [])}")
            print()

            # Scene summary
            for i, scene in enumerate(config['scenes'][:5], 1):  # Show first 5
                print(f"  {i}. {scene['id']}: {scene.get('title', 'Untitled')}")
            if len(config['scenes']) > 5:
                print(f"  ... and {len(config['scenes']) - 5} more scenes")

            print()
            print("Configuration is valid. Ready to process.")
            print("Remove --dry-run flag to start processing.")
            return 0

        except Exception as e:
            print(f"✗ Configuration error: {e}")
            return 1

    # Run batch processing
    try:
        success = processor.run()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
