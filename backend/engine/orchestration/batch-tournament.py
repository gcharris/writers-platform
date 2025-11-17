"""
Batch Tournament Processor

Processes multiple scenes through the tournament system with rate limiting.

Input JSON format:
{
  "chapter": "2.4",
  "scenes": [
    {
      "scene_id": "2.4.1",
      "title": "The Seduction Deepens",
      "outline": "Vance makes his offer explicit...",
      "context_requirements": ["Mickey", "Vance", "Ken surveillance"],
      "previous_scenes": ["2.3.3", "2.3.4", "2.3.5"]
    },
    ...
  ]
}

Usage:
    python3 framework/orchestration/batch-tournament.py \\
        --input chapter-2-4-outline.json \\
        --output output/chapter-2-4-tournament/ \\
        --parallel 3 \\
        --synthesize
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.tournament import TournamentOrchestrator


class BatchTournamentProcessor:
    """Process multiple scenes through tournament system."""

    def __init__(self, project_name: str = "The-Explants",
                 synthesis_threshold: float = 7.0,
                 parallel_scenes: int = 1):
        """
        Initialize batch processor.

        Args:
            project_name: Writing project name
            synthesis_threshold: Minimum score for hybrid synthesis
            parallel_scenes: Number of scenes to process in parallel
        """
        self.project_name = project_name
        self.synthesis_threshold = synthesis_threshold
        self.parallel_scenes = parallel_scenes

        # Rate limiting (per-platform API limits)
        self.rate_limits = {
            'anthropic': 50,  # requests per minute
            'openai': 500,
            'google': 60,
            'xai': 60
        }

        # Tracking
        self.total_scenes_processed = 0
        self.total_cost = 0.0
        self.failed_scenes = []
        self.start_time = None

    def process_batch(self, input_file: str, output_dir: str,
                     synthesize: bool = True,
                     agents: List[str] = None,
                     max_tokens: int = 4000) -> Dict:
        """
        Process batch of scenes from input file.

        Args:
            input_file: Path to input JSON file
            output_dir: Directory for output files
            synthesize: Whether to synthesize hybrid scenes
            agents: List of agents to use (None = all 5)
            max_tokens: Max tokens per generation

        Returns:
            Batch processing summary
        """
        self.start_time = time.time()

        print("=" * 80)
        print("BATCH TOURNAMENT PROCESSOR")
        print("=" * 80)
        print(f"Input: {input_file}")
        print(f"Output: {output_dir}")
        print(f"Parallel scenes: {self.parallel_scenes}")
        print(f"Synthesis: {synthesize}")
        print()

        # Load input
        with open(input_file, 'r') as f:
            batch_config = json.load(f)

        chapter = batch_config.get('chapter', 'unknown')
        scenes = batch_config.get('scenes', [])

        print(f"Chapter: {chapter}")
        print(f"Scenes to process: {len(scenes)}")
        print()

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Process scenes
        if self.parallel_scenes == 1:
            # Sequential processing
            results = self._process_sequential(
                scenes, output_path, synthesize, agents, max_tokens
            )
        else:
            # Parallel processing
            results = self._process_parallel(
                scenes, output_path, synthesize, agents, max_tokens
            )

        # Generate batch summary
        summary = self._generate_summary(chapter, scenes, results)

        # Save batch summary
        summary_path = output_path / 'batch-summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print()
        print("=" * 80)
        print("BATCH PROCESSING COMPLETE")
        print(f"Processed: {self.total_scenes_processed}/{len(scenes)} scenes")
        print(f"Failed: {len(self.failed_scenes)} scenes")
        print(f"Total cost: ${self.total_cost:.4f}")
        print(f"Elapsed time: {time.time() - self.start_time:.1f}s")
        print(f"Summary saved: {summary_path}")
        print("=" * 80)

        return summary

    def _process_sequential(self, scenes: List[Dict], output_path: Path,
                           synthesize: bool, agents: List[str],
                           max_tokens: int) -> List[Dict]:
        """Process scenes sequentially."""
        results = []

        for i, scene_config in enumerate(scenes, 1):
            print(f"\n{'=' * 80}")
            print(f"SCENE {i}/{len(scenes)}: {scene_config.get('scene_id', 'unknown')}")
            print(f"{'=' * 80}\n")

            result = self._process_single_scene(
                scene_config, output_path, synthesize, agents, max_tokens
            )
            results.append(result)

            # Rate limiting delay between scenes (conservative)
            if i < len(scenes):
                print(f"\nWaiting 5s before next scene (rate limiting)...")
                time.sleep(5)

        return results

    def _process_parallel(self, scenes: List[Dict], output_path: Path,
                         synthesize: bool, agents: List[str],
                         max_tokens: int) -> List[Dict]:
        """Process scenes in parallel (with caution)."""
        results = []

        with ThreadPoolExecutor(max_workers=self.parallel_scenes) as executor:
            future_to_scene = {}

            for scene_config in scenes:
                future = executor.submit(
                    self._process_single_scene,
                    scene_config, output_path, synthesize, agents, max_tokens
                )
                future_to_scene[future] = scene_config.get('scene_id', 'unknown')

            for future in as_completed(future_to_scene):
                scene_id = future_to_scene[future]
                try:
                    result = future.get()
                    results.append(result)
                    print(f"\n✓ Completed: {scene_id}")
                except Exception as e:
                    print(f"\n✗ Failed: {scene_id} - {e}")
                    results.append({
                        'scene_id': scene_id,
                        'success': False,
                        'error': str(e)
                    })

        return results

    def _process_single_scene(self, scene_config: Dict, output_path: Path,
                             synthesize: bool, agents: List[str],
                             max_tokens: int) -> Dict:
        """Process a single scene through tournament."""
        scene_id = scene_config.get('scene_id', 'unknown')

        try:
            # Create orchestrator for this scene
            orchestrator = TournamentOrchestrator(
                project_name=self.project_name,
                synthesis_threshold=self.synthesis_threshold
            )

            # Run tournament
            result = orchestrator.run_tournament(
                scene_outline=scene_config.get('outline', ''),
                chapter=scene_id,
                context_requirements=scene_config.get('context_requirements'),
                previous_scenes=scene_config.get('previous_scenes'),
                custom_instructions=scene_config.get('custom_instructions'),
                agents=agents,
                synthesize=synthesize,
                max_tokens=max_tokens
            )

            # Save results
            output_file = output_path / f"{scene_id}-tournament.json"
            orchestrator.save_results(result, str(output_file))

            # Track metrics
            self.total_scenes_processed += 1
            self.total_cost += result['summary']['total_cost']

            return {
                'scene_id': scene_id,
                'success': True,
                'cost': result['summary']['total_cost'],
                'highest_score': result['summary']['highest_score'],
                'hybrid_score': result['summary'].get('hybrid_score'),
                'output_file': str(output_file)
            }

        except Exception as e:
            print(f"Error processing scene {scene_id}: {e}")
            self.failed_scenes.append({
                'scene_id': scene_id,
                'error': str(e)
            })
            return {
                'scene_id': scene_id,
                'success': False,
                'error': str(e)
            }

    def _generate_summary(self, chapter: str, scenes: List[Dict],
                         results: List[Dict]) -> Dict:
        """Generate batch processing summary."""
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]

        summary = {
            'batch_metadata': {
                'chapter': chapter,
                'total_scenes': len(scenes),
                'processed': len(successful),
                'failed': len(failed),
                'timestamp': datetime.now().isoformat(),
                'elapsed_time_seconds': round(time.time() - self.start_time, 2)
            },
            'cost_summary': {
                'total_cost': round(self.total_cost, 4),
                'average_cost_per_scene': round(self.total_cost / len(successful), 4) if successful else 0,
                'cost_breakdown': [
                    {
                        'scene_id': r['scene_id'],
                        'cost': r.get('cost', 0)
                    }
                    for r in successful
                ]
            },
            'quality_summary': {
                'average_highest_score': round(
                    sum(r.get('highest_score', 0) for r in successful) / len(successful), 2
                ) if successful else 0,
                'average_hybrid_score': round(
                    sum(r.get('hybrid_score', 0) for r in successful if r.get('hybrid_score')) /
                    len([r for r in successful if r.get('hybrid_score')]), 2
                ) if any(r.get('hybrid_score') for r in successful) else None,
                'score_details': [
                    {
                        'scene_id': r['scene_id'],
                        'highest_score': r.get('highest_score'),
                        'hybrid_score': r.get('hybrid_score')
                    }
                    for r in successful
                ]
            },
            'failed_scenes': failed,
            'output_files': [r.get('output_file') for r in successful if r.get('output_file')]
        }

        return summary


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Batch process multiple scenes through tournament system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', required=True,
                       help="Input JSON file with scene configurations")
    parser.add_argument('--output', required=True,
                       help="Output directory for tournament results")
    parser.add_argument('--parallel', type=int, default=1,
                       help="Number of scenes to process in parallel (default: 1)")
    parser.add_argument('--synthesize', action='store_true',
                       help="Synthesize hybrid scenes from best elements")
    parser.add_argument('--synthesis-threshold', type=float, default=7.0,
                       help="Minimum score for hybrid synthesis (default: 7.0)")
    parser.add_argument('--agents', nargs='+',
                       choices=['claude-sonnet-4-5', 'gemini-1-5-pro', 'gpt-4o',
                               'grok-2', 'claude-haiku'],
                       help="Agents to use (default: all 5)")
    parser.add_argument('--max-tokens', type=int, default=4000,
                       help="Maximum tokens per generation (default: 4000)")
    parser.add_argument('--project', default="The-Explants",
                       help="Project name (default: The-Explants)")

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Initialize batch processor
    processor = BatchTournamentProcessor(
        project_name=args.project,
        synthesis_threshold=args.synthesis_threshold,
        parallel_scenes=args.parallel
    )

    # Process batch
    try:
        summary = processor.process_batch(
            input_file=args.input,
            output_dir=args.output,
            synthesize=args.synthesize,
            agents=args.agents,
            max_tokens=args.max_tokens
        )

        # Exit with error code if any scenes failed
        if summary['batch_metadata']['failed'] > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nBatch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError in batch processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
