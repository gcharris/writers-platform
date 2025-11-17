"""
Comparison framework for Cognee vs. Gemini File Search.

This script runs parallel tests on both systems to compare:
- Query response quality
- Context building capabilities
- Entity and relationship extraction
- Performance metrics
- Cost estimates
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    from factory.core.cognee_knowledge_graph import CogneeKnowledgeGraph, CogneeConfig
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False

try:
    from factory.core.gemini_file_search import ExplantsKnowledgeGraph, GeminiFileSearchConfig
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class QueryComparison:
    """Comparison results for a single query."""
    query: str
    cognee_answer: str
    gemini_answer: str
    cognee_time: float
    gemini_time: float
    cognee_sources: List[str]
    gemini_sources: List[str]
    cognee_context_size: int
    gemini_context_size: int


@dataclass
class SystemComparison:
    """Overall comparison between systems."""
    total_queries: int
    cognee_avg_time: float
    gemini_avg_time: float
    cognee_avg_context_size: int
    gemini_avg_context_size: int
    queries: List[QueryComparison]
    winner: str
    summary: str


class KnowledgeGraphComparator:
    """
    Compare Cognee and Gemini File Search systems.

    Runs parallel queries on both systems and produces detailed
    comparison reports.
    """

    def __init__(self):
        """Initialize both knowledge graph systems."""
        self.cognee_kg = None
        self.gemini_kg = None

        if COGNEE_AVAILABLE:
            try:
                config = CogneeConfig()
                self.cognee_kg = CogneeKnowledgeGraph(config)
                print("✓ Cognee Knowledge Graph loaded")
            except Exception as e:
                print(f"✗ Could not load Cognee: {e}")

        if GEMINI_AVAILABLE:
            try:
                config = GeminiFileSearchConfig()
                self.gemini_kg = ExplantsKnowledgeGraph(config)
                print("✓ Gemini File Search loaded")
            except Exception as e:
                print(f"✗ Could not load Gemini File Search: {e}")

    async def initialize(self):
        """Initialize both systems."""
        if self.cognee_kg:
            await self.cognee_kg.initialize()
            print("✓ Cognee initialized")

        if self.gemini_kg:
            # Gemini is already initialized in constructor
            print("✓ Gemini initialized")

    async def compare_query(
        self,
        query: str,
        story_phase: Optional[int] = None,
    ) -> QueryComparison:
        """
        Compare a single query across both systems.

        Args:
            query: Natural language query
            story_phase: Optional story phase filter

        Returns:
            QueryComparison with results from both systems
        """
        # Query Cognee
        cognee_answer = ""
        cognee_time = 0.0
        cognee_sources = []
        cognee_context_size = 0

        if self.cognee_kg:
            try:
                start = time.time()
                result = await self.cognee_kg.query(query, story_phase=story_phase)
                cognee_time = time.time() - start

                cognee_answer = result.answer
                cognee_sources = result.source_documents
                cognee_context_size = len(result.answer)
            except Exception as e:
                cognee_answer = f"ERROR: {e}"

        # Query Gemini
        gemini_answer = ""
        gemini_time = 0.0
        gemini_sources = []
        gemini_context_size = 0

        if self.gemini_kg:
            try:
                start = time.time()
                result = self.gemini_kg.query(query, story_phase=story_phase)
                gemini_time = time.time() - start

                gemini_answer = result.get('answer', '')
                gemini_sources = result.get('citations', [])
                gemini_context_size = len(gemini_answer)
            except Exception as e:
                gemini_answer = f"ERROR: {e}"

        return QueryComparison(
            query=query,
            cognee_answer=cognee_answer,
            gemini_answer=gemini_answer,
            cognee_time=cognee_time,
            gemini_time=gemini_time,
            cognee_sources=cognee_sources,
            gemini_sources=gemini_sources,
            cognee_context_size=cognee_context_size,
            gemini_context_size=gemini_context_size,
        )

    async def compare_context_building(
        self,
        scene_outline: str,
        characters: List[str],
        worldbuilding: List[str],
        story_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compare context building capabilities for scene writing.

        Args:
            scene_outline: Scene description
            characters: Character names
            worldbuilding: Worldbuilding topics
            story_phase: Story phase

        Returns:
            Dictionary with comparison results
        """
        results = {
            'scene_outline': scene_outline,
            'cognee': {},
            'gemini': {},
        }

        # Build context with Cognee
        if self.cognee_kg:
            try:
                start = time.time()
                context = await self.cognee_kg.build_scene_context(
                    scene_outline=scene_outline,
                    characters=characters,
                    worldbuilding_topics=worldbuilding,
                    story_phase=story_phase,
                )
                formatted = self.cognee_kg.format_context_for_agent(context)
                elapsed = time.time() - start

                results['cognee'] = {
                    'time': elapsed,
                    'context_size': len(formatted),
                    'character_count': len(context.get('characters', {})),
                    'worldbuilding_count': len(context.get('worldbuilding', {})),
                    'has_related_scenes': bool(context.get('related_scenes', '')),
                    'sample': formatted[:500] + "..." if len(formatted) > 500 else formatted,
                }
            except Exception as e:
                results['cognee'] = {'error': str(e)}

        # Build context with Gemini
        if self.gemini_kg:
            try:
                start = time.time()
                context = self.gemini_kg.build_scene_context(
                    scene_outline=scene_outline,
                    characters=characters,
                    worldbuilding_topics=worldbuilding,
                    story_phase=story_phase,
                    include_related_scenes=True,
                )
                formatted = self.gemini_kg.format_context_for_agent(context)
                elapsed = time.time() - start

                results['gemini'] = {
                    'time': elapsed,
                    'context_size': len(formatted),
                    'character_count': len(context.get('characters', [])),
                    'worldbuilding_count': len(context.get('worldbuilding', [])),
                    'has_related_scenes': bool(context.get('related_scenes', [])),
                    'sample': formatted[:500] + "..." if len(formatted) > 500 else formatted,
                }
            except Exception as e:
                results['gemini'] = {'error': str(e)}

        return results

    async def run_comparison_suite(
        self,
        test_queries: Optional[List[Dict[str, Any]]] = None,
    ) -> SystemComparison:
        """
        Run a full comparison suite.

        Args:
            test_queries: List of query dictionaries with 'query' and optional 'story_phase'

        Returns:
            SystemComparison with detailed results
        """
        if test_queries is None:
            test_queries = self._get_default_test_queries()

        print(f"\nRunning comparison suite with {len(test_queries)} queries...\n")

        query_results = []
        cognee_times = []
        gemini_times = []
        cognee_context_sizes = []
        gemini_context_sizes = []

        for i, test_query in enumerate(test_queries, 1):
            query = test_query['query']
            story_phase = test_query.get('story_phase')

            print(f"[{i}/{len(test_queries)}] Testing: {query[:60]}...")

            comparison = await self.compare_query(query, story_phase)
            query_results.append(comparison)

            if comparison.cognee_time > 0:
                cognee_times.append(comparison.cognee_time)
                cognee_context_sizes.append(comparison.cognee_context_size)

            if comparison.gemini_time > 0:
                gemini_times.append(comparison.gemini_time)
                gemini_context_sizes.append(comparison.gemini_context_size)

        # Calculate averages
        cognee_avg_time = sum(cognee_times) / len(cognee_times) if cognee_times else 0
        gemini_avg_time = sum(gemini_times) / len(gemini_times) if gemini_times else 0
        cognee_avg_size = sum(cognee_context_sizes) / len(cognee_context_sizes) if cognee_context_sizes else 0
        gemini_avg_size = sum(gemini_context_sizes) / len(gemini_context_sizes) if gemini_context_sizes else 0

        # Determine winner
        winner = "tie"
        if cognee_avg_size > gemini_avg_size * 1.2 and cognee_avg_time < gemini_avg_time * 2:
            winner = "cognee"
        elif gemini_avg_size > cognee_avg_size * 1.2 and gemini_avg_time < cognee_avg_time * 2:
            winner = "gemini"

        # Generate summary
        summary = self._generate_summary(
            cognee_avg_time, gemini_avg_time,
            cognee_avg_size, gemini_avg_size,
            winner
        )

        return SystemComparison(
            total_queries=len(test_queries),
            cognee_avg_time=cognee_avg_time,
            gemini_avg_time=gemini_avg_time,
            cognee_avg_context_size=int(cognee_avg_size),
            gemini_avg_context_size=int(gemini_avg_size),
            queries=query_results,
            winner=winner,
            summary=summary,
        )

    def _get_default_test_queries(self) -> List[Dict[str, Any]]:
        """Get default test queries for comparison."""
        return [
            {'query': "What is Mickey Bardot's psychological state in Phase 1?", 'story_phase': 1},
            {'query': "Describe the relationship between Mickey and Noni", 'story_phase': 1},
            {'query': "Explain how bi-location works", 'story_phase': None},
            {'query': "What are the rules of The Line?", 'story_phase': None},
            {'query': "Describe Mickey's addiction arc", 'story_phase': None},
            {'query': "Who is Vance and what is his role?", 'story_phase': 2},
            {'query': "What are the key themes in Volume 1?", 'story_phase': None},
            {'query': "How does quantum consciousness work in the story?", 'story_phase': None},
        ]

    def _generate_summary(
        self,
        cognee_time: float,
        gemini_time: float,
        cognee_size: float,
        gemini_size: float,
        winner: str,
    ) -> str:
        """Generate comparison summary."""
        summary = []

        summary.append("## Comparison Summary\n")

        # Speed
        if cognee_time < gemini_time:
            speed_diff = ((gemini_time - cognee_time) / gemini_time) * 100
            summary.append(f"**Speed**: Cognee is {speed_diff:.1f}% faster")
        else:
            speed_diff = ((cognee_time - gemini_time) / cognee_time) * 100
            summary.append(f"**Speed**: Gemini is {speed_diff:.1f}% faster")

        # Context size
        if cognee_size > gemini_size:
            size_diff = ((cognee_size - gemini_size) / gemini_size) * 100
            summary.append(f"**Context Size**: Cognee provides {size_diff:.1f}% more context")
        else:
            size_diff = ((gemini_size - cognee_size) / cognee_size) * 100
            summary.append(f"**Context Size**: Gemini provides {size_diff:.1f}% more context")

        # Winner
        if winner == "cognee":
            summary.append("\n**Winner**: Cognee (better context with acceptable speed)")
        elif winner == "gemini":
            summary.append("\n**Winner**: Gemini (better context with acceptable speed)")
        else:
            summary.append("\n**Result**: Tie (both systems perform similarly)")

        return "\n".join(summary)

    def print_results(self, comparison: SystemComparison):
        """Print comparison results to console."""
        print("\n" + "="*80)
        print("KNOWLEDGE GRAPH COMPARISON RESULTS")
        print("="*80)

        print(f"\nTotal queries: {comparison.total_queries}")
        print(f"\nCognee avg time: {comparison.cognee_avg_time:.2f}s")
        print(f"Gemini avg time: {comparison.gemini_avg_time:.2f}s")
        print(f"\nCognee avg context size: {comparison.cognee_avg_context_size:,} chars")
        print(f"Gemini avg context size: {comparison.gemini_avg_context_size:,} chars")

        print(f"\n{comparison.summary}")

        print("\n" + "="*80)
        print("DETAILED QUERY RESULTS")
        print("="*80)

        for i, query in enumerate(comparison.queries, 1):
            print(f"\n[{i}] {query.query}")
            print(f"    Cognee: {query.cognee_time:.2f}s, {query.cognee_context_size:,} chars")
            print(f"    Gemini: {query.gemini_time:.2f}s, {query.gemini_context_size:,} chars")

        print("\n" + "="*80)

    def save_results(self, comparison: SystemComparison, output_path: Path):
        """Save comparison results to JSON file."""
        results_dict = asdict(comparison)

        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"\n✓ Results saved to: {output_path}")


async def main():
    """Run comparison suite."""
    comparator = KnowledgeGraphComparator()

    # Initialize systems
    await comparator.initialize()

    # Run comparison suite
    results = await comparator.run_comparison_suite()

    # Print results
    comparator.print_results(results)

    # Save results
    output_path = Path(__file__).parent.parent.parent / "cognee_vs_gemini_comparison.json"
    comparator.save_results(results, output_path)


if __name__ == "__main__":
    asyncio.run(main())
