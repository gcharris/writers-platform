"""
Multi-Agent Scene Writer

Coordinates multiple AI agents to write scene variations with full context
from Google File Store. This is the core workflow for generating scenes.
"""

import argparse
import json
from pathlib import Path
from typing import List, Optional, Dict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google_store import GoogleStoreConfig, GoogleStoreQuerier, ContextPackage
from agents import (
    create_claude_agent, create_chatgpt_agent,
    create_gemini_agent, create_grok_agent
)


class SceneWriter:
    """Orchestrate multiple agents to write scene variations."""

    AGENT_FACTORIES = {
        'claude': create_claude_agent,
        'chatgpt': create_chatgpt_agent,
        'gemini': create_gemini_agent,
        'grok': create_grok_agent
    }

    def __init__(self, project_name: str, config: Optional[GoogleStoreConfig] = None):
        """
        Initialize scene writer.

        Args:
            project_name: Name of the writing project
            config: GoogleStoreConfig instance
        """
        self.project_name = project_name
        self.config = config or GoogleStoreConfig()
        self.querier = GoogleStoreQuerier(project_name, self.config)

    def write_scene(self,
                   scene_outline: str,
                   agents: List[str],
                   character_names: Optional[List[str]] = None,
                   worldbuilding_topics: Optional[List[str]] = None,
                   include_recent_chapters: int = 3,
                   custom_instructions: Optional[str] = None,
                   max_tokens: int = 4000) -> Dict:
        """
        Generate scene variations using multiple agents.

        Args:
            scene_outline: Brief description of the scene
            agents: List of agent platforms to use (e.g., ['claude', 'gemini'])
            character_names: Characters involved in the scene
            worldbuilding_topics: Relevant worldbuilding topics
            include_recent_chapters: Number of recent chapters to include as context
            custom_instructions: Optional custom instructions for the agents
            max_tokens: Maximum tokens per generation

        Returns:
            Dictionary with variations and metadata
        """
        print("=" * 80)
        print("MULTI-AGENT SCENE WRITER")
        print("=" * 80)
        print(f"Project: {self.project_name}")
        print(f"Scene: {scene_outline}")
        print(f"Agents: {', '.join(agents)}")
        print()

        # Step 1: Build context package from Google File Store
        print("Step 1: Querying Google File Store for context...")
        context_package = self.querier.build_context_package(
            scene_outline=scene_outline,
            character_names=character_names,
            worldbuilding_topics=worldbuilding_topics,
            include_recent_chapters=include_recent_chapters
        )

        # Convert context to prompt format
        context_text = context_package.to_prompt_context()
        print(f"Context built: {len(context_text)} characters")
        print()

        # Step 2: Build the writing prompt
        writing_prompt = self._build_writing_prompt(
            scene_outline,
            custom_instructions
        )

        # Step 3: Generate variations from each agent
        print("Step 2: Generating scene variations from agents...")
        print()

        variations = []
        total_cost = 0.0
        total_tokens = 0

        for agent_name in agents:
            if agent_name not in self.AGENT_FACTORIES:
                print(f"Warning: Unknown agent '{agent_name}', skipping")
                continue

            print(f"--- {agent_name.upper()} ---")

            try:
                # Create agent
                agent_factory = self.AGENT_FACTORIES[agent_name]
                agent = agent_factory(self.config)

                # Generate content
                response = agent.generate(
                    prompt=writing_prompt,
                    context=context_text,
                    max_tokens=max_tokens,
                    temperature=0.8  # Higher temperature for creativity
                )

                variations.append({
                    'agent': agent_name,
                    'content': response.content,
                    'metadata': response.metadata,
                    'tokens_used': response.tokens_used,
                    'cost': response.cost
                })

                total_cost += response.cost or 0
                total_tokens += response.tokens_used or 0

                print(f"Generated {len(response.content)} characters")
                print(f"Tokens: {response.tokens_used}, Cost: ${response.cost:.4f}")
                print()

            except Exception as e:
                print(f"Error with {agent_name}: {e}")
                print()

        # Step 4: Compile results
        results = {
            'project': self.project_name,
            'scene_outline': scene_outline,
            'context_package': context_package.to_dict(),
            'writing_prompt': writing_prompt,
            'variations': variations,
            'summary': {
                'num_variations': len(variations),
                'total_tokens': total_tokens,
                'total_cost': total_cost,
                'agents_used': [v['agent'] for v in variations]
            }
        }

        print("=" * 80)
        print("GENERATION COMPLETE")
        print(f"Generated {len(variations)} variations")
        print(f"Total cost: ${total_cost:.4f}")
        print("=" * 80)

        return results

    def _build_writing_prompt(self, scene_outline: str,
                             custom_instructions: Optional[str] = None) -> str:
        """
        Build the writing prompt for agents.

        Args:
            scene_outline: Scene outline
            custom_instructions: Optional custom instructions

        Returns:
            Complete writing prompt
        """
        prompt = f"""Write a complete scene based on this outline:

{scene_outline}

INSTRUCTIONS:
- Use the context provided above to ensure consistency with characters, worldbuilding, and story events
- Write in a vivid, engaging style appropriate for the genre
- Include authentic dialogue and character interactions
- Show character development and emotional depth
- Maintain consistency with established voice and tone
"""

        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

        prompt += "\n\nWrite the complete scene now:"

        return prompt

    def save_results(self, results: Dict, output_path: str):
        """
        Save results to a file.

        Args:
            results: Results dictionary
            output_path: Path to output file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.suffix == '.json':
            # Save as JSON
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            # Save as markdown
            self._save_as_markdown(results, output_path)

        print(f"\nResults saved to: {output_path}")

    def _save_as_markdown(self, results: Dict, output_path: Path):
        """Save results as formatted markdown."""
        with open(output_path, 'w') as f:
            f.write(f"# Scene Variations: {results['scene_outline']}\n\n")
            f.write(f"**Project:** {results['project']}\n\n")
            f.write(f"**Generated:** {results['summary']['num_variations']} variations\n")
            f.write(f"**Total Cost:** ${results['summary']['total_cost']:.4f}\n\n")

            f.write("---\n\n")

            for i, variation in enumerate(results['variations'], 1):
                f.write(f"## Variation {i}: {variation['agent'].upper()}\n\n")
                f.write(f"**Tokens:** {variation['tokens_used']} | ")
                f.write(f"**Cost:** ${variation['cost']:.4f}\n\n")
                f.write(variation['content'])
                f.write("\n\n---\n\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate scene variations using multiple AI agents"
    )
    parser.add_argument('--project', required=True, help="Project name")
    parser.add_argument('--scene', required=True, help="Scene outline/description")
    parser.add_argument('--agents', nargs='+', required=True,
                       help="Agents to use (claude, chatgpt, gemini, grok)")
    parser.add_argument('--characters', nargs='+', help="Character names")
    parser.add_argument('--worldbuilding', nargs='+', help="Worldbuilding topics")
    parser.add_argument('--chapters', type=int, default=3,
                       help="Number of recent chapters to include")
    parser.add_argument('--instructions', help="Custom writing instructions")
    parser.add_argument('--output', required=True, help="Output file path")
    parser.add_argument('--max-tokens', type=int, default=4000,
                       help="Maximum tokens per generation")

    args = parser.parse_args()

    # Initialize writer
    writer = SceneWriter(args.project)

    # Generate variations
    results = writer.write_scene(
        scene_outline=args.scene,
        agents=args.agents,
        character_names=args.characters,
        worldbuilding_topics=args.worldbuilding,
        include_recent_chapters=args.chapters,
        custom_instructions=args.instructions,
        max_tokens=args.max_tokens
    )

    # Save results
    writer.save_results(results, args.output)


if __name__ == "__main__":
    main()
