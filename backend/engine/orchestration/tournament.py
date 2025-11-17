"""
Multi-Agent Scene Tournament System

Orchestrates the proven workflow:
1. Generate 5 scene variations from different AI agents (parallel)
2. Score each variation automatically (7 criteria)
3. Run cross-agent critique
4. Synthesize hybrid scene from best elements
5. Output structured results (JSON + markdown)

Usage:
    python3 framework/orchestration/tournament.py \\
        --scene "Mickey confronts Vance about optimization mathematics" \\
        --chapter 2.3.6 \\
        --context-requirements "Mickey Bardot, Vance, bi-location strain" \\
        --output output/2.3.6-tournament-results.json \\
        --synthesize
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gemini_file_search import ExplantsKnowledgeGraph, GeminiFileSearchConfig
from google_store import GoogleStoreConfig, GoogleStoreQuerier  # Keep for backward compatibility

# Cognee Knowledge Graph (alternative to Gemini File Search)
try:
    from cognee_knowledge_graph import CogneeKnowledgeGraph, CogneeConfig
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    CogneeKnowledgeGraph = None
    CogneeConfig = None

from agents import (
    ClaudeAgent, GeminiAgent, ChatGPTAgent, GrokAgent
)
from utils.scoring import SceneScorer, format_score_summary
from utils.validation import validate_scene


class TournamentOrchestrator:
    """Orchestrates multi-agent scene tournament."""

    # Agent configurations
    AGENT_CONFIGS = {
        'claude-sonnet-4-5': {
            'class': ClaudeAgent,
            'model': 'claude-sonnet-4-5-20250929',
            'config_key': 'claude',
            'description': 'Primary agent - best at voice authenticity and emotional impact'
        },
        'gemini-1-5-pro': {
            'class': GeminiAgent,
            'model': 'gemini-1.5-pro',
            'config_key': 'google',
            'description': 'Best at philosophical arguments and structure'
        },
        'gpt-4o': {
            'class': ChatGPTAgent,
            'model': 'gpt-4o',
            'config_key': 'openai',
            'description': 'Best at dialogue and character consistency'
        },
        'grok-2': {
            'class': GrokAgent,
            'model': 'grok-2',
            'config_key': 'xai',
            'description': 'Best at worldbuilding integration'
        },
        'claude-haiku': {
            'class': ClaudeAgent,
            'model': 'claude-3-haiku-20240307',
            'config_key': 'claude',
            'description': 'Budget option for simple scenes'
        }
    }

    def __init__(self, project_name: str = "The-Explants",
                 config: Optional[GoogleStoreConfig] = None,
                 synthesis_threshold: float = 7.0,
                 use_gemini_search: bool = True,
                 use_cognee: bool = False):
        """
        Initialize tournament orchestrator.

        Args:
            project_name: Writing project name
            config: GoogleStoreConfig instance (for backward compatibility)
            synthesis_threshold: Minimum score for inclusion in hybrid (default 7.0)
            use_gemini_search: Use Gemini File Search (cloud-based semantic search)
            use_cognee: Use Cognee Knowledge Graph (self-hosted, true graph with entities/relationships)
        """
        self.project_name = project_name
        self.config = config or self._load_config()
        self.synthesis_threshold = synthesis_threshold
        self.knowledge_graph = None
        self.cognee_graph = None
        self.querier = None  # Legacy Google Cloud Storage querier
        self.kg_type = None  # Track which knowledge graph is in use

        # Try Cognee first if requested (self-hosted, true knowledge graph)
        if use_cognee and COGNEE_AVAILABLE:
            try:
                print("Initializing Cognee Knowledge Graph...")
                cognee_config = CogneeConfig()
                self.cognee_graph = CogneeKnowledgeGraph(config=cognee_config)
                # Initialize must be called asynchronously, so we'll do it lazily
                self.kg_type = "cognee"
                print("✓ Cognee Knowledge Graph will be initialized on first use")
            except Exception as e:
                print(f"Warning: Cognee not available: {e}")
                use_cognee = False

        # Try to initialize Gemini File Search if not using Cognee
        if not use_cognee and use_gemini_search:
            try:
                gemini_config = GeminiFileSearchConfig()
                self.knowledge_graph = ExplantsKnowledgeGraph(config=gemini_config)
                self.kg_type = "gemini"
                print("✓ Gemini File Search knowledge graph initialized")
            except Exception as e:
                print(f"Warning: Gemini File Search not available: {e}")
                print("Falling back to legacy Google Cloud Storage...")
                use_gemini_search = False

        # Fallback to legacy Google Cloud Storage
        if not use_cognee and (not use_gemini_search or self.knowledge_graph is None):
            try:
                self.querier = GoogleStoreQuerier(project_name, self.config)
                self.kg_type = "gcs"
                print("✓ Google Cloud Storage querier initialized")
            except Exception as e:
                print(f"Warning: Google Cloud Storage not available: {e}")
                print("Continuing with minimal context...")
                self.kg_type = "minimal"

        # Initialize agents cache
        self.agents_cache = {}

        # Cost tracking
        self.total_cost = 0.0
        self.total_tokens = 0

    def _load_config(self) -> GoogleStoreConfig:
        """Load configuration from credentials.json or environment."""
        config = GoogleStoreConfig()

        if not config.config:
            print("Warning: No credentials.json found. Checking environment variables...")
            # Could add environment variable fallback here

        return config

    def run_tournament(self,
                      scene_outline: str,
                      chapter: Optional[str] = None,
                      context_requirements: Optional[List[str]] = None,
                      previous_scenes: Optional[List[str]] = None,
                      custom_instructions: Optional[str] = None,
                      agents: Optional[List[str]] = None,
                      synthesize: bool = True,
                      max_tokens: int = 4000) -> Dict:
        """
        Run complete tournament for a scene.

        Args:
            scene_outline: Scene description/outline
            chapter: Chapter identifier (e.g., "2.3.6")
            context_requirements: Required context (characters, worldbuilding topics)
            previous_scenes: Previous scene IDs for context
            custom_instructions: Additional writing instructions
            agents: List of agent names to use (defaults to all 5)
            synthesize: Whether to synthesize hybrid scene
            max_tokens: Max tokens per generation

        Returns:
            Complete tournament results dictionary
        """
        print("=" * 80)
        print("MULTI-AGENT SCENE TOURNAMENT")
        print("=" * 80)
        print(f"Project: {self.project_name}")
        print(f"Scene: {scene_outline}")
        if chapter:
            print(f"Chapter: {chapter}")
        print(f"Synthesis threshold: {self.synthesis_threshold}")
        print()

        start_time = time.time()

        # Default agents: all 5
        if agents is None:
            agents = [
                'claude-sonnet-4-5',
                'gemini-1-5-pro',
                'gpt-4o',
                'grok-2',
                'claude-haiku'
            ]

        # Step 1: Build context
        print("Step 1: Building context...")
        context_text = self._build_context(
            scene_outline, chapter, context_requirements, previous_scenes
        )
        print(f"Context: {len(context_text)} characters")
        print()

        # Step 2: Generate variations (parallel)
        print("Step 2: Generating scene variations from agents...")
        print()
        variations = self._generate_variations(
            scene_outline, context_text, agents, custom_instructions, max_tokens
        )
        print(f"Generated {len(variations)} variations")
        print()

        # Step 3: Score variations
        print("Step 3: Scoring variations...")
        print()
        scored_variations = self._score_variations(variations)
        self._print_score_summary(scored_variations)
        print()

        # Step 4: Run cross-agent critique
        print("Step 4: Running cross-agent critique...")
        print()
        critiques = self._run_critiques(scored_variations)
        print()

        # Step 5: Synthesize hybrid (if requested)
        hybrid_result = None
        if synthesize:
            print("Step 5: Synthesizing hybrid scene...")
            print()
            hybrid_result = self._synthesize_hybrid(
                scored_variations, critiques, scene_outline, context_text
            )
            print()

        # Compile results
        elapsed_time = time.time() - start_time
        results = self._compile_results(
            scene_outline=scene_outline,
            chapter=chapter,
            context_requirements=context_requirements,
            variations=scored_variations,
            critiques=critiques,
            hybrid=hybrid_result,
            elapsed_time=elapsed_time
        )

        print("=" * 80)
        print("TOURNAMENT COMPLETE")
        print(f"Elapsed time: {elapsed_time:.1f}s")
        print(f"Total cost: ${self.total_cost:.4f}")
        print(f"Total tokens: {self.total_tokens:,}")
        print("=" * 80)

        return results

    def _extract_story_phase(self, chapter: Optional[str]) -> Optional[int]:
        """
        Extract story phase from chapter identifier.

        Phase 1: Volume 1, Chapters 1-10
        Phase 2: Volume 1, Chapters 11-28
        Phase 3: Volume 2
        Phase 4: Volume 3
        """
        if not chapter:
            return None

        try:
            parts = chapter.split('.')
            if len(parts) >= 2:
                volume = int(parts[0])
                chapter_num = int(parts[1]) if len(parts) > 1 else None

                if volume == 1:
                    return 1 if (chapter_num and chapter_num <= 10) else 2
                elif volume == 2:
                    return 3
                elif volume == 3:
                    return 4
        except (ValueError, IndexError):
            pass

        return None

    def _build_context(self, scene_outline: str,
                      chapter: Optional[str],
                      context_requirements: Optional[List[str]],
                      previous_scenes: Optional[List[str]]) -> str:
        """
        Build context using available knowledge graph system.

        Priority order:
        1. Cognee (self-hosted, true graph with entities/relationships)
        2. Gemini File Search (cloud-based semantic search)
        3. Google Cloud Storage (legacy file retrieval)
        4. Minimal context (fallback)
        """
        # Extract story phase from chapter
        story_phase = self._extract_story_phase(chapter)

        # Extract character names and worldbuilding from context_requirements
        characters = []
        worldbuilding = []

        if context_requirements:
            for req in context_requirements:
                # Simple heuristic: capitalized name = character, lowercase = worldbuilding
                if req[0].isupper() and (' ' in req or req in ['Mickey', 'Noni', 'Vance', 'Jillian']):
                    characters.append(req)
                else:
                    worldbuilding.append(req)

        # Try Cognee first (true knowledge graph with entity/relationship extraction)
        if self.cognee_graph:
            try:
                import asyncio

                print("Building context from Cognee Knowledge Graph...")

                # Ensure Cognee is initialized (lazy initialization)
                async def build_cognee_context():
                    if not self.cognee_graph.initialized:
                        await self.cognee_graph.initialize()

                    # Build comprehensive context package with semantic queries + graph traversal
                    context_package = await self.cognee_graph.build_scene_context(
                        scene_outline=scene_outline,
                        characters=characters if characters else ['Mickey'],  # Default to Mickey
                        worldbuilding_topics=worldbuilding if worldbuilding else ['bi-location'],
                        story_phase=story_phase,
                        previous_scenes=previous_scenes
                    )

                    # Format for agent consumption
                    return self.cognee_graph.format_context_for_agent(context_package)

                # Run async function
                formatted_context = asyncio.run(build_cognee_context())

                print(f"✓ Context built from Cognee: {len(formatted_context):,} characters (entity graph + semantic search)")
                return formatted_context

            except Exception as e:
                print(f"Warning: Could not fetch Cognee context: {e}")
                import traceback
                traceback.print_exc()
                print("Falling back to other methods...")

        # Try Gemini File Search (semantic knowledge graph)
        if self.knowledge_graph:
            try:
                print("Building context from Gemini File Search knowledge graph...")

                # Build comprehensive context package with semantic queries
                context_package = self.knowledge_graph.build_scene_context(
                    scene_outline=scene_outline,
                    characters=characters if characters else ['Mickey'],  # Default to Mickey
                    worldbuilding_topics=worldbuilding if worldbuilding else ['bi-location'],
                    story_phase=story_phase,
                    include_related_scenes=True
                )

                # Format for agent consumption
                formatted_context = self.knowledge_graph.format_context_for_agent(context_package)

                print(f"✓ Context built from Gemini: {len(formatted_context):,} characters from semantic queries")
                return formatted_context

            except Exception as e:
                print(f"Warning: Could not fetch Gemini File Search context: {e}")
                print("Falling back to Google Cloud Storage...")

        # Fallback to legacy Google Cloud Storage
        if self.querier:
            try:
                # Extract character names and worldbuilding from context_requirements
                characters = []
                worldbuilding = []

                if context_requirements:
                    for req in context_requirements:
                        # Simple heuristic: capitalized = character, lowercase = worldbuilding
                        if req[0].isupper() and ' ' in req:
                            characters.append(req)
                        else:
                            worldbuilding.append(req)

                context_package = self.querier.build_context_package(
                    scene_outline=scene_outline,
                    character_names=characters if characters else None,
                    worldbuilding_topics=worldbuilding if worldbuilding else None,
                    include_recent_chapters=3
                )

                return context_package.to_prompt_context()
            except Exception as e:
                print(f"Warning: Could not fetch Google Cloud Storage context: {e}")
                print("Using minimal fallback context...")

        # Final fallback: minimal context
        print("Using minimal fallback context (no cloud context available)")
        context_parts = [
            f"SCENE OUTLINE: {scene_outline}",
            "",
            "PROJECT: The Explants - Science fiction novel trilogy",
            "VOICE: Enhanced Mickey Bardot (compressed phrasing, direct metaphors, present-tense urgency)",
            ""
        ]

        if context_requirements:
            context_parts.append("CONTEXT REQUIREMENTS:")
            context_parts.extend([f"- {req}" for req in context_requirements])
            context_parts.append("")

        if story_phase:
            context_parts.append(f"STORY PHASE: {story_phase}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _generate_variations(self, scene_outline: str, context: str,
                            agents: List[str], custom_instructions: Optional[str],
                            max_tokens: int) -> List[Dict]:
        """Generate scene variations from agents in parallel."""
        variations = []

        # Build writing prompt
        writing_prompt = self._build_writing_prompt(scene_outline, custom_instructions)

        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all generation tasks
            future_to_agent = {}
            for agent_name in agents:
                if agent_name not in self.AGENT_CONFIGS:
                    print(f"Warning: Unknown agent '{agent_name}', skipping")
                    continue

                future = executor.submit(
                    self._generate_single_variation,
                    agent_name, writing_prompt, context, max_tokens
                )
                future_to_agent[future] = agent_name

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    variation = future.get(timeout=120)  # 2 minute timeout per agent
                    if variation:
                        variations.append(variation)
                        print(f"✓ {agent_name}: {variation['word_count']} words, "
                              f"${variation['cost']:.4f}")
                except Exception as e:
                    print(f"✗ {agent_name}: Failed - {str(e)[:100]}")

        return variations

    def _generate_single_variation(self, agent_name: str, prompt: str,
                                   context: str, max_tokens: int) -> Optional[Dict]:
        """Generate a single variation with retry logic."""
        agent_config = self.AGENT_CONFIGS[agent_name]

        # Create agent with retry
        agent = self._create_agent_with_retry(agent_name)
        if not agent:
            return None

        # Generate with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = agent.generate(
                    prompt=prompt,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=0.8  # Higher temperature for creativity
                )

                # Track cost
                self.total_cost += response.cost or 0
                self.total_tokens += response.tokens_used or 0

                return {
                    'agent': agent_name,
                    'content': response.content,
                    'word_count': len(response.content.split()),
                    'tokens_used': response.tokens_used,
                    'cost': response.cost,
                    'metadata': response.metadata,
                    'timestamp': response.timestamp
                }

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"  Retry {attempt + 1}/{max_retries} for {agent_name} "
                          f"after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  Failed after {max_retries} attempts: {e}")
                    return None

    def _create_agent_with_retry(self, agent_name: str, max_retries: int = 2):
        """Create agent instance with error handling."""
        # Check cache first
        if agent_name in self.agents_cache:
            return self.agents_cache[agent_name]

        agent_config = self.AGENT_CONFIGS[agent_name]
        config_key = agent_config['config_key']

        try:
            # Get API key
            api_key = self.config.get_ai_api_key(config_key)
            if not api_key:
                # Try alternate key names
                if config_key == 'claude':
                    api_key = self.config.get_ai_api_key('anthropic')

                if not api_key:
                    print(f"Warning: No API key for {config_key}")
                    return None

            # Create agent
            agent_class = agent_config['class']
            agent = agent_class(
                agent_name=agent_name,
                api_key=api_key,
                model=agent_config['model']
            )

            # Cache it
            self.agents_cache[agent_name] = agent
            return agent

        except Exception as e:
            print(f"Error creating agent {agent_name}: {e}")
            return None

    def _build_writing_prompt(self, scene_outline: str,
                              custom_instructions: Optional[str]) -> str:
        """Build comprehensive writing prompt."""
        prompt_parts = [
            "Write a complete scene for The Explants novel based on this outline:",
            "",
            scene_outline,
            "",
            "VOICE REQUIREMENTS (CRITICAL):",
            "- Write in Enhanced Mickey Bardot voice:",
            "  * Compressed phrasing (e.g., 'geometried themselves', 'refused to stay')",
            "  * Direct metaphors from con artist/gambling realm",
            "  * Present-tense urgency, embedded personality",
            "- Use Mickey's terms: 'The Line', 'The Tether', 'The Shared Vein'",
            "- NEVER use: 'quantum link', 'bi-location mode', 'split consciousness'",
            "",
            "BI-LOCATION MECHANICS:",
            "- Show through physical strain (temples pulsing, shadow splitting, voice desync)",
            "- Do NOT announce with technical language",
            "- Noni actively interprets with morphic resonance (NOT passive receiver)",
            "",
            "SCENE REQUIREMENTS:",
            "- 400-600 words optimal length",
            "- Strong opening hook",
            "- Authentic character dialogue",
            "- Visceral physical descriptions",
            "- Advance consciousness war themes naturally",
            "- Maintain consistency with established characters/worldbuilding",
            ""
        ]

        if custom_instructions:
            prompt_parts.extend([
                "ADDITIONAL INSTRUCTIONS:",
                custom_instructions,
                ""
            ])

        prompt_parts.append("Write the complete scene now:")

        return "\n".join(prompt_parts)

    def _score_variations(self, variations: List[Dict]) -> List[Dict]:
        """Score all variations."""
        # Create scorer agent (Claude Sonnet 4.5)
        scorer_agent = self._create_agent_with_retry('claude-sonnet-4-5')
        if not scorer_agent:
            print("Error: Could not create scorer agent")
            return variations

        scorer = SceneScorer(scorer_agent)

        for i, variation in enumerate(variations):
            print(f"Scoring {variation['agent']}...")
            try:
                score_result = scorer.score_scene(
                    variation['content'],
                    variation['agent']
                )

                # Track scoring cost
                if 'cost' in score_result:
                    self.total_cost += score_result.get('cost', 0)
                if 'tokens_used' in score_result:
                    self.total_tokens += score_result.get('tokens_used', 0)

                # Add scores to variation
                variation['scores'] = score_result['scores']
                variation['validation'] = score_result['validation']

            except Exception as e:
                print(f"  Error scoring: {e}")
                # Add default scores
                variation['scores'] = {
                    'total': 0,
                    'note': 'Scoring failed'
                }

        # Sort by total score (descending)
        variations.sort(key=lambda v: v.get('scores', {}).get('total', 0), reverse=True)

        return variations

    def _print_score_summary(self, variations: List[Dict]):
        """Print score summary table."""
        print(f"{'Agent':<20} {'Total':<8} {'Voice':<7} {'Char':<7} {'World':<7} "
              f"{'Pace':<7} {'Dial':<7} {'Emot':<7} {'CW':<7}")
        print("-" * 90)

        for var in variations:
            scores = var.get('scores', {})
            agent = var['agent'][:18]
            print(f"{agent:<20} "
                  f"{scores.get('total', 0):>6.1f}  "
                  f"{scores.get('voice_authenticity', 0):>5.1f}  "
                  f"{scores.get('character_consistency', 0):>5.1f}  "
                  f"{scores.get('worldbuilding', 0):>5.1f}  "
                  f"{scores.get('pacing', 0):>5.1f}  "
                  f"{scores.get('dialogue', 0):>5.1f}  "
                  f"{scores.get('emotional_impact', 0):>5.1f}  "
                  f"{scores.get('consciousness_war', 0):>5.1f}")

        print()

        # Show validation issues
        for var in variations:
            validation = var.get('validation', {})
            bi_location = validation.get('bi_location', {})

            if bi_location.get('issues'):
                print(f"{var['agent']}: {len(bi_location['issues'])} issues")
                for issue in bi_location['issues'][:2]:
                    print(f"  - {issue}")

    def _run_critiques(self, variations: List[Dict]) -> Dict[str, Dict]:
        """Run cross-agent critique (Claude only for now to save costs)."""
        critiques = {}

        # Use Claude Sonnet 4.5 for critique (best at analysis)
        critic_agent = self._create_agent_with_retry('claude-sonnet-4-5')
        if not critic_agent:
            print("Warning: Could not create critic agent, skipping critiques")
            return critiques

        # Build critique prompt
        critique_prompt = self._build_critique_prompt(variations)

        try:
            response = critic_agent.generate(
                prompt=critique_prompt,
                system_prompt="You are an expert editor analyzing scene variations for a novel.",
                max_tokens=3000,
                temperature=0.5
            )

            self.total_cost += response.cost or 0
            self.total_tokens += response.tokens_used or 0

            # Parse critique (store as single analysis for now)
            critiques['claude-critic'] = {
                'analysis': response.content,
                'timestamp': response.timestamp
            }

            print(f"✓ Critique complete")

        except Exception as e:
            print(f"Error running critique: {e}")

        return critiques

    def _build_critique_prompt(self, variations: List[Dict]) -> str:
        """Build prompt for cross-agent critique."""
        prompt_parts = [
            "Analyze these scene variations and identify the best elements from each.",
            "",
            "Your task:",
            "1. Identify the best STRUCTURAL CHASSIS (overall flow, pacing, scene architecture)",
            "2. Extract the best PHILOSOPHICAL KILL-SHOTS (most impactful moments/lines)",
            "3. Note elements to AVOID",
            "4. Provide synthesis recommendations",
            "",
            "VARIATIONS:",
            ""
        ]

        # Add each variation
        for i, var in enumerate(variations, 1):
            scores = var.get('scores', {})
            prompt_parts.extend([
                f"=== VARIATION {i}: {var['agent'].upper()} ===",
                f"Total Score: {scores.get('total', 0):.1f}/70",
                f"Word Count: {var['word_count']}",
                "",
                var['content'],
                "",
                ""
            ])

        prompt_parts.extend([
            "ANALYSIS REQUIRED:",
            "",
            "1. **Best Structural Chassis**: Which variation has the best overall flow and pacing?",
            "",
            "2. **Best Philosophical Moments**: Quote 3-5 specific lines/moments that pack the most punch",
            "",
            "3. **Elements to Avoid**: What should NOT be included in the final version?",
            "",
            "4. **Synthesis Strategy**: How should these be combined for maximum impact?",
            "",
            "Provide your analysis now:"
        ])

        return "\n".join(prompt_parts)

    def _synthesize_hybrid(self, variations: List[Dict], critiques: Dict,
                          scene_outline: str, context: str) -> Optional[Dict]:
        """Synthesize hybrid scene from best elements."""
        # Filter variations by threshold
        qualified_variations = [
            v for v in variations
            if v.get('scores', {}).get('total', 0) >= self.synthesis_threshold * 10
        ]

        if not qualified_variations:
            print(f"Warning: No variations scored above threshold "
                  f"({self.synthesis_threshold * 10:.1f}/70)")
            print("Using top 2 variations anyway...")
            qualified_variations = variations[:2]

        print(f"Synthesizing from {len(qualified_variations)} qualified variations")

        # Use Claude Sonnet 4.5 for synthesis
        synthesis_agent = self._create_agent_with_retry('claude-sonnet-4-5')
        if not synthesis_agent:
            print("Error: Could not create synthesis agent")
            return None

        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(
            qualified_variations, critiques, scene_outline
        )

        try:
            response = synthesis_agent.generate(
                prompt=synthesis_prompt,
                context=context,
                max_tokens=5000,
                temperature=0.7
            )

            self.total_cost += response.cost or 0
            self.total_tokens += response.tokens_used or 0

            # Score the hybrid
            scorer = SceneScorer(synthesis_agent)
            hybrid_scores = scorer.score_scene(response.content, "hybrid")

            result = {
                'content': response.content,
                'word_count': len(response.content.split()),
                'sources': [v['agent'] for v in qualified_variations],
                'scores': hybrid_scores['scores'],
                'validation': hybrid_scores['validation'],
                'tokens_used': response.tokens_used,
                'cost': response.cost,
                'timestamp': response.timestamp
            }

            print(f"✓ Hybrid synthesized: {result['word_count']} words, "
                  f"score: {result['scores'].get('total', 0):.1f}/70")

            return result

        except Exception as e:
            print(f"Error synthesizing hybrid: {e}")
            traceback.print_exc()
            return None

    def _build_synthesis_prompt(self, variations: List[Dict], critiques: Dict,
                                scene_outline: str) -> str:
        """Build prompt for hybrid synthesis."""
        prompt_parts = [
            "Create a HYBRID scene that combines the best elements from these variations.",
            "",
            f"SCENE OUTLINE: {scene_outline}",
            "",
            "SYNTHESIS STRATEGY:",
            "- Take the best STRUCTURAL CHASSIS (flow and pacing)",
            "- Extract the best PHILOSOPHICAL KILL-SHOTS (impactful moments)",
            "- Maintain Enhanced Mickey voice throughout",
            "- Avoid weak elements identified in critiques",
            "- 400-600 words optimal",
            "",
            "QUALIFIED VARIATIONS TO SYNTHESIZE:",
            ""
        ]

        # Add qualified variations
        for i, var in enumerate(variations, 1):
            scores = var.get('scores', {})
            prompt_parts.extend([
                f"=== VARIATION {i}: {var['agent'].upper()} "
                f"(Score: {scores.get('total', 0):.1f}) ===",
                var['content'],
                "",
                ""
            ])

        # Add critique guidance
        if critiques:
            prompt_parts.extend([
                "CRITIQUE GUIDANCE:",
                critiques.get('claude-critic', {}).get('analysis', 'No critique available'),
                "",
                ""
            ])

        prompt_parts.extend([
            "Now create the HYBRID scene that combines the best elements.",
            "Requirements:",
            "- Use Enhanced Mickey voice (compressed phrasing, direct metaphors)",
            "- Use Mickey's terms (The Line/Tether/Shared Vein, NOT 'quantum link')",
            "- Show bi-location through physical strain",
            "- Take best structural flow from top-scoring variation",
            "- Integrate best philosophical moments from all variations",
            "",
            "Write the hybrid scene now:"
        ])

        return "\n".join(prompt_parts)

    def _compile_results(self, scene_outline: str, chapter: Optional[str],
                        context_requirements: Optional[List[str]],
                        variations: List[Dict], critiques: Dict,
                        hybrid: Optional[Dict], elapsed_time: float) -> Dict:
        """Compile complete tournament results."""
        return {
            'tournament_metadata': {
                'project': self.project_name,
                'scene_outline': scene_outline,
                'chapter': chapter,
                'context_requirements': context_requirements,
                'timestamp': datetime.now().isoformat(),
                'elapsed_time_seconds': round(elapsed_time, 2),
                'synthesis_threshold': self.synthesis_threshold
            },
            'variations': variations,
            'critiques': critiques,
            'hybrid_synthesis': hybrid,
            'summary': {
                'num_variations': len(variations),
                'agents_used': [v['agent'] for v in variations],
                'total_tokens': self.total_tokens,
                'total_cost': round(self.total_cost, 4),
                'highest_scoring': variations[0]['agent'] if variations else None,
                'highest_score': variations[0].get('scores', {}).get('total', 0) if variations else 0,
                'hybrid_score': hybrid.get('scores', {}).get('total', 0) if hybrid else None
            }
        }

    def save_results(self, results: Dict, output_path: str):
        """Save tournament results to files."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved: {json_path}")

        # Save hybrid as markdown
        if results.get('hybrid_synthesis'):
            hybrid = results['hybrid_synthesis']
            md_path = output_path.with_name(
                output_path.stem + '-hybrid.md'
            )
            with open(md_path, 'w') as f:
                f.write(f"# Hybrid Scene: {results['tournament_metadata']['scene_outline']}\n\n")
                f.write(f"**Score:** {hybrid['scores'].get('total', 0):.1f}/70\n")
                f.write(f"**Word Count:** {hybrid['word_count']}\n")
                f.write(f"**Sources:** {', '.join(hybrid['sources'])}\n\n")
                f.write("---\n\n")
                f.write(hybrid['content'])
            print(f"✓ Hybrid saved: {md_path}")

        # Save summary
        summary_path = output_path.with_name(output_path.stem + '-summary.md')
        with open(summary_path, 'w') as f:
            self._write_summary_markdown(f, results)
        print(f"✓ Summary saved: {summary_path}")

    def _write_summary_markdown(self, f, results: Dict):
        """Write summary markdown file."""
        meta = results['tournament_metadata']
        summary = results['summary']

        f.write(f"# Tournament Summary: {meta['scene_outline']}\n\n")
        f.write(f"**Project:** {meta['project']}\n")
        if meta.get('chapter'):
            f.write(f"**Chapter:** {meta['chapter']}\n")
        f.write(f"**Date:** {meta['timestamp'][:10]}\n")
        f.write(f"**Duration:** {meta['elapsed_time_seconds']:.1f}s\n")
        f.write(f"**Total Cost:** ${summary['total_cost']:.4f}\n\n")

        f.write("## Score Rankings\n\n")
        f.write(f"{'Rank':<6} {'Agent':<20} {'Total':<10} {'Voice':<8} {'Char':<8} "
                f"{'World':<8} {'Pace':<8} {'Dial':<8} {'Emot':<8} {'CW':<8}\n")
        f.write("-" * 100 + "\n")

        for i, var in enumerate(results['variations'], 1):
            scores = var.get('scores', {})
            f.write(f"{i:<6} {var['agent']:<20} "
                   f"{scores.get('total', 0):>8.1f}  "
                   f"{scores.get('voice_authenticity', 0):>6.1f}  "
                   f"{scores.get('character_consistency', 0):>6.1f}  "
                   f"{scores.get('worldbuilding', 0):>6.1f}  "
                   f"{scores.get('pacing', 0):>6.1f}  "
                   f"{scores.get('dialogue', 0):>6.1f}  "
                   f"{scores.get('emotional_impact', 0):>6.1f}  "
                   f"{scores.get('consciousness_war', 0):>6.1f}\n")

        if results.get('hybrid_synthesis'):
            f.write("\n## Hybrid Results\n\n")
            hybrid = results['hybrid_synthesis']
            scores = hybrid['scores']
            f.write(f"**Total Score:** {scores.get('total', 0):.1f}/70\n")
            f.write(f"**Word Count:** {hybrid['word_count']}\n")
            f.write(f"**Sources:** {', '.join(hybrid['sources'])}\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Run multi-agent scene tournament",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--scene', required=True,
                       help="Scene outline/description")
    parser.add_argument('--chapter', help="Chapter identifier (e.g., 2.3.6)")
    parser.add_argument('--context-requirements', nargs='+',
                       help="Context requirements (characters, worldbuilding topics)")
    parser.add_argument('--previous-scenes', nargs='+',
                       help="Previous scene IDs for context")
    parser.add_argument('--instructions', help="Custom writing instructions")
    parser.add_argument('--agents', nargs='+',
                       choices=['claude-sonnet-4-5', 'gemini-1-5-pro', 'gpt-4o',
                               'grok-2', 'claude-haiku'],
                       help="Agents to use (default: all 5)")
    parser.add_argument('--output', required=True,
                       help="Output file path (JSON)")
    parser.add_argument('--synthesize', action='store_true',
                       help="Synthesize hybrid scene from best elements")
    parser.add_argument('--synthesis-threshold', type=float, default=7.0,
                       help="Minimum score for hybrid synthesis (default: 7.0)")
    parser.add_argument('--max-tokens', type=int, default=4000,
                       help="Maximum tokens per generation (default: 4000)")
    parser.add_argument('--project', default="The-Explants",
                       help="Project name (default: The-Explants)")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = TournamentOrchestrator(
        project_name=args.project,
        synthesis_threshold=args.synthesis_threshold
    )

    # Run tournament
    try:
        results = orchestrator.run_tournament(
            scene_outline=args.scene,
            chapter=args.chapter,
            context_requirements=args.context_requirements,
            previous_scenes=args.previous_scenes,
            custom_instructions=args.instructions,
            agents=args.agents,
            synthesize=args.synthesize,
            max_tokens=args.max_tokens
        )

        # Save results
        orchestrator.save_results(results, args.output)

    except KeyboardInterrupt:
        print("\n\nTournament interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tournament: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
