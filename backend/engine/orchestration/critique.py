"""
Multi-Agent Critique System

Compare and critique scene variations using multiple AI agents.
Agents provide feedback on each other's work, helping identify strengths.
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from google_store import GoogleStoreConfig
from agents import create_claude_agent


class SceneCritique:
    """Orchestrate critique and comparison of scene variations."""

    DEFAULT_CRITERIA = [
        'narrative-voice',
        'character-consistency',
        'dialogue-authenticity',
        'pacing',
        'emotional-impact',
        'worldbuilding-integration',
        'prose-quality'
    ]

    def __init__(self, config: Optional[GoogleStoreConfig] = None):
        """
        Initialize critique system.

        Args:
            config: GoogleStoreConfig instance
        """
        self.config = config or GoogleStoreConfig()

    def load_variations(self, input_path: str) -> Dict:
        """
        Load scene variations from JSON file.

        Args:
            input_path: Path to scene-writer output

        Returns:
            Variations data
        """
        with open(input_path, 'r') as f:
            return json.load(f)

    def critique_variations(self,
                          variations_data: Dict,
                          criteria: Optional[List[str]] = None,
                          critique_agent: str = 'claude') -> Dict:
        """
        Critique all variations using specified criteria.

        Args:
            variations_data: Output from scene-writer
            criteria: Criteria to evaluate
            critique_agent: Agent to use for critique (default: claude)

        Returns:
            Critique results
        """
        criteria = criteria or self.DEFAULT_CRITERIA

        print("=" * 80)
        print("MULTI-AGENT SCENE CRITIQUE")
        print("=" * 80)
        print(f"Scene: {variations_data['scene_outline']}")
        print(f"Variations: {len(variations_data['variations'])}")
        print(f"Criteria: {', '.join(criteria)}")
        print()

        # Create critique agent
        if critique_agent == 'claude':
            agent = create_claude_agent(self.config)
        else:
            print(f"Warning: Only Claude supported for critique currently")
            agent = create_claude_agent(self.config)

        critiques = []
        total_cost = 0.0

        # Critique each variation
        for i, variation in enumerate(variations_data['variations'], 1):
            print(f"--- Critiquing Variation {i} ({variation['agent'].upper()}) ---")

            try:
                response = agent.critique(
                    content=variation['content'],
                    criteria=criteria
                )

                critique_data = {
                    'variation_index': i,
                    'variation_agent': variation['agent'],
                    'critique_content': response.content,
                    'tokens_used': response.tokens_used,
                    'cost': response.cost
                }

                critiques.append(critique_data)
                total_cost += response.cost or 0

                print(f"Critique complete. Cost: ${response.cost:.4f}")
                print()

            except Exception as e:
                print(f"Error critiquing variation {i}: {e}")
                print()

        # Generate comparative analysis
        print("--- Generating Comparative Analysis ---")

        comparison = self._generate_comparison(
            variations_data['variations'],
            critiques,
            agent,
            criteria
        )

        total_cost += comparison.get('cost', 0)

        print(f"Analysis complete. Cost: ${comparison.get('cost', 0):.4f}")
        print()

        results = {
            'scene_outline': variations_data['scene_outline'],
            'project': variations_data.get('project'),
            'criteria': criteria,
            'individual_critiques': critiques,
            'comparative_analysis': comparison['content'],
            'summary': {
                'num_variations': len(variations_data['variations']),
                'total_cost': total_cost
            }
        }

        print("=" * 80)
        print("CRITIQUE COMPLETE")
        print(f"Total cost: ${total_cost:.4f}")
        print("=" * 80)

        return results

    def _generate_comparison(self,
                           variations: List[Dict],
                           critiques: List[Dict],
                           agent,
                           criteria: List[str]) -> Dict:
        """
        Generate comparative analysis of all variations.

        Args:
            variations: List of scene variations
            critiques: Individual critiques
            agent: Agent to use for comparison
            criteria: Evaluation criteria

        Returns:
            Comparison results
        """
        # Build comparison prompt
        comparison_text = "# SCENE VARIATIONS FOR COMPARISON\n\n"

        for i, (variation, critique) in enumerate(zip(variations, critiques), 1):
            comparison_text += f"## Variation {i} (by {variation['agent'].upper()})\n\n"
            comparison_text += f"### Content\n{variation['content']}\n\n"
            comparison_text += f"### Individual Critique\n{critique['critique_content']}\n\n"
            comparison_text += "---\n\n"

        criteria_text = "\n".join([f"- {c}" for c in criteria])

        comparison_prompt = f"""You have {len(variations)} variations of the same scene written by different AI agents.
Each has been individually critiqued.

Now, provide a COMPARATIVE ANALYSIS:

1. **Overall Ranking**: Rank the variations from strongest to weakest overall

2. **Criterion-by-Criterion Analysis**: For each criterion, identify which variation excels:
{criteria_text}

3. **Unique Strengths**: What does each variation do uniquely well?

4. **Synthesis Recommendation**: Which specific elements from each variation should be combined to create the strongest final version?

5. **Key Improvements**: What are the 2-3 most important improvements the author should focus on?

Provide your analysis in a structured, actionable format."""

        try:
            response = agent.generate(
                prompt=comparison_prompt,
                context=comparison_text,
                system_prompt="You are an expert at comparative analysis of creative writing."
            )

            return {
                'content': response.content,
                'tokens_used': response.tokens_used,
                'cost': response.cost
            }

        except Exception as e:
            print(f"Error generating comparison: {e}")
            return {
                'content': f"Error: {str(e)}",
                'tokens_used': 0,
                'cost': 0.0
            }

    def save_critique(self, results: Dict, output_path: str):
        """
        Save critique results.

        Args:
            results: Critique results
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.suffix == '.json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            self._save_as_markdown(results, output_path)

        print(f"\nCritique saved to: {output_path}")

    def _save_as_markdown(self, results: Dict, output_path: Path):
        """Save critique as formatted markdown."""
        with open(output_path, 'w') as f:
            f.write(f"# Scene Critique: {results['scene_outline']}\n\n")
            f.write(f"**Criteria:** {', '.join(results['criteria'])}\n\n")
            f.write("---\n\n")

            f.write("## Individual Critiques\n\n")
            for critique in results['individual_critiques']:
                f.write(f"### Variation {critique['variation_index']}: ")
                f.write(f"{critique['variation_agent'].upper()}\n\n")
                f.write(critique['critique_content'])
                f.write("\n\n---\n\n")

            f.write("## Comparative Analysis\n\n")
            f.write(results['comparative_analysis'])
            f.write("\n\n---\n\n")

            f.write(f"**Total Cost:** ${results['summary']['total_cost']:.4f}\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Critique and compare scene variations"
    )
    parser.add_argument('--input', required=True,
                       help="Input file (JSON from scene-writer)")
    parser.add_argument('--criteria', nargs='+',
                       help="Criteria to evaluate")
    parser.add_argument('--output', required=True,
                       help="Output file path")

    args = parser.parse_args()

    # Initialize critique system
    critique_system = SceneCritique()

    # Load variations
    variations_data = critique_system.load_variations(args.input)

    # Run critique
    results = critique_system.critique_variations(
        variations_data=variations_data,
        criteria=args.criteria
    )

    # Save results
    critique_system.save_critique(results, args.output)


if __name__ == "__main__":
    main()
