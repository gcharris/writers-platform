"""
Agent Analytics System

Analyzes tournament results to identify agent strengths and weaknesses.
Builds agent performance profiles and recommends optimal agent combinations.

Usage:
    python3 framework/orchestration/agent-analytics.py \\
        --input "output/chapter-*-tournament.json" \\
        --output output/agent-analytics.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from glob import glob


class AgentAnalyzer:
    """Analyze agent performance across multiple tournaments."""

    CRITERIA = [
        'voice_authenticity',
        'character_consistency',
        'worldbuilding',
        'pacing',
        'dialogue',
        'emotional_impact',
        'consciousness_war'
    ]

    def __init__(self):
        """Initialize analyzer."""
        self.tournaments = []
        self.agent_stats = defaultdict(lambda: {
            'total_scenes': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'scores_by_criteria': defaultdict(list),
            'total_scores': [],
            'wins': 0,  # Times agent had highest score
            'hybrid_contributions': 0  # Times included in hybrid
        })

    def load_tournaments(self, tournament_files: List[str]):
        """
        Load tournament results from files.

        Args:
            tournament_files: List of paths to tournament JSON files
        """
        print(f"Loading {len(tournament_files)} tournament files...")

        for file_path in tournament_files:
            try:
                with open(file_path, 'r') as f:
                    tournament = json.load(f)
                    self.tournaments.append(tournament)
                    self._process_tournament(tournament)
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")

        print(f"Loaded {len(self.tournaments)} tournaments")
        print()

    def _process_tournament(self, tournament: Dict):
        """Process a single tournament's results."""
        variations = tournament.get('variations', [])
        hybrid = tournament.get('hybrid_synthesis')

        if not variations:
            return

        # Find winner (highest scoring agent)
        winner = max(variations, key=lambda v: v.get('scores', {}).get('total', 0))

        for variation in variations:
            agent_name = variation['agent']
            scores = variation.get('scores', {})
            cost = variation.get('cost', 0)
            tokens = variation.get('tokens_used', 0)

            # Update stats
            self.agent_stats[agent_name]['total_scenes'] += 1
            self.agent_stats[agent_name]['total_cost'] += cost
            self.agent_stats[agent_name]['total_tokens'] += tokens
            self.agent_stats[agent_name]['total_scores'].append(scores.get('total', 0))

            # Record scores by criteria
            for criterion in self.CRITERIA:
                if criterion in scores:
                    self.agent_stats[agent_name]['scores_by_criteria'][criterion].append(
                        scores[criterion]
                    )

            # Check if winner
            if agent_name == winner['agent']:
                self.agent_stats[agent_name]['wins'] += 1

            # Check if in hybrid
            if hybrid and agent_name in hybrid.get('sources', []):
                self.agent_stats[agent_name]['hybrid_contributions'] += 1

    def generate_profiles(self) -> Dict:
        """
        Generate agent performance profiles.

        Returns:
            Dictionary with agent profiles and recommendations
        """
        print("Generating agent profiles...")

        agent_profiles = {}

        for agent_name, stats in self.agent_stats.items():
            if stats['total_scenes'] == 0:
                continue

            # Calculate averages
            avg_scores = {}
            for criterion in self.CRITERIA:
                scores = stats['scores_by_criteria'][criterion]
                avg_scores[criterion] = round(sum(scores) / len(scores), 2) if scores else 0.0

            avg_total = round(
                sum(stats['total_scores']) / len(stats['total_scores']), 2
            ) if stats['total_scores'] else 0.0

            avg_cost = round(stats['total_cost'] / stats['total_scenes'], 4)

            # Identify strengths (top 3 criteria)
            criteria_sorted = sorted(
                avg_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            strengths = [c[0] for c in criteria_sorted[:3]]

            # Identify weaknesses (bottom 2 criteria)
            weaknesses = [c[0] for c in criteria_sorted[-2:]]

            # Calculate win rate
            win_rate = round(
                (stats['wins'] / stats['total_scenes']) * 100, 1
            )

            # Calculate hybrid contribution rate
            hybrid_rate = round(
                (stats['hybrid_contributions'] / stats['total_scenes']) * 100, 1
            )

            agent_profiles[agent_name] = {
                'stats': {
                    'total_scenes': stats['total_scenes'],
                    'wins': stats['wins'],
                    'win_rate_percent': win_rate,
                    'hybrid_contributions': stats['hybrid_contributions'],
                    'hybrid_contribution_rate_percent': hybrid_rate,
                    'avg_cost_per_scene': avg_cost,
                    'avg_total_tokens': round(stats['total_tokens'] / stats['total_scenes'])
                },
                'performance': {
                    'average_total_score': avg_total,
                    'average_scores_by_criteria': avg_scores,
                    'strengths': strengths,
                    'weaknesses': weaknesses
                },
                'cost_efficiency': {
                    'cost_per_point': round(avg_cost / avg_total, 6) if avg_total > 0 else 0,
                    'ranking': None  # Will be filled later
                }
            }

        # Rank agents by cost efficiency
        ranked = sorted(
            agent_profiles.items(),
            key=lambda x: x[1]['cost_efficiency']['cost_per_point']
        )
        for i, (agent_name, _) in enumerate(ranked, 1):
            agent_profiles[agent_name]['cost_efficiency']['ranking'] = i

        # Generate recommendations
        recommendations = self._generate_recommendations(agent_profiles)

        return {
            'agent_profiles': agent_profiles,
            'recommendations': recommendations,
            'summary': {
                'total_tournaments_analyzed': len(self.tournaments),
                'total_agents_evaluated': len(agent_profiles)
            }
        }

    def _generate_recommendations(self, profiles: Dict) -> Dict:
        """Generate scene-type recommendations based on agent strengths."""
        # Find best agents for each criterion
        best_by_criteria = {}

        for criterion in self.CRITERIA:
            ranked = sorted(
                profiles.items(),
                key=lambda x: x[1]['performance']['average_scores_by_criteria'].get(criterion, 0),
                reverse=True
            )
            best_by_criteria[criterion] = [agent_name for agent_name, _ in ranked[:2]]

        # Generate scene type recommendations
        scene_type_recommendations = {
            'high_emotion': best_by_criteria.get('emotional_impact', [])[:2],
            'philosophical_argument': best_by_criteria.get('consciousness_war', [])[:2],
            'dialogue_heavy': best_by_criteria.get('dialogue', [])[:2],
            'worldbuilding': best_by_criteria.get('worldbuilding', [])[:2],
            'character_development': best_by_criteria.get('character_consistency', [])[:2],
            'voice_critical': best_by_criteria.get('voice_authenticity', [])[:2],
            'action_pacing': best_by_criteria.get('pacing', [])[:2]
        }

        # Find most cost-efficient overall
        cost_efficient = sorted(
            profiles.items(),
            key=lambda x: x[1]['cost_efficiency']['cost_per_point']
        )
        best_value = cost_efficient[0][0] if cost_efficient else None

        # Find highest quality overall
        highest_quality = sorted(
            profiles.items(),
            key=lambda x: x[1]['performance']['average_total_score'],
            reverse=True
        )
        best_quality = highest_quality[0][0] if highest_quality else None

        # Find most reliable (highest hybrid contribution rate)
        most_reliable = sorted(
            profiles.items(),
            key=lambda x: x[1]['stats']['hybrid_contribution_rate_percent'],
            reverse=True
        )
        most_consistent = most_reliable[0][0] if most_reliable else None

        return {
            'scene_type_recommendations': scene_type_recommendations,
            'best_by_criteria': best_by_criteria,
            'overall_recommendations': {
                'best_quality': best_quality,
                'best_value': best_value,
                'most_consistent': most_consistent
            },
            'optimal_tournament_lineup': self._recommend_optimal_lineup(profiles)
        }

    def _recommend_optimal_lineup(self, profiles: Dict) -> List[str]:
        """Recommend optimal 5-agent lineup based on complementary strengths."""
        # Strategy: Pick agents that cover different strengths

        # Always include best quality agent
        by_quality = sorted(
            profiles.items(),
            key=lambda x: x[1]['performance']['average_total_score'],
            reverse=True
        )

        lineup = []
        covered_strengths = set()

        for agent_name, profile in by_quality:
            strengths = profile['performance']['strengths']

            # Check if this agent adds new strengths
            new_strengths = set(strengths) - covered_strengths
            if new_strengths or len(lineup) == 0:
                lineup.append(agent_name)
                covered_strengths.update(strengths)

            if len(lineup) >= 5:
                break

        return lineup

    def print_report(self, analysis: Dict):
        """Print analysis report to console."""
        print("=" * 80)
        print("AGENT ANALYTICS REPORT")
        print("=" * 80)
        print()

        print(f"Tournaments analyzed: {analysis['summary']['total_tournaments_analyzed']}")
        print(f"Agents evaluated: {analysis['summary']['total_agents_evaluated']}")
        print()

        # Agent profiles
        print("AGENT PERFORMANCE PROFILES:")
        print()

        profiles = analysis['agent_profiles']
        sorted_agents = sorted(
            profiles.items(),
            key=lambda x: x[1]['performance']['average_total_score'],
            reverse=True
        )

        for agent_name, profile in sorted_agents:
            stats = profile['stats']
            perf = profile['performance']
            cost_eff = profile['cost_efficiency']

            print(f"--- {agent_name.upper()} ---")
            print(f"  Scenes: {stats['total_scenes']} | "
                  f"Wins: {stats['wins']} ({stats['win_rate_percent']}%) | "
                  f"Hybrid: {stats['hybrid_contributions']} ({stats['hybrid_contribution_rate_percent']}%)")
            print(f"  Avg Score: {perf['average_total_score']:.1f}/70 | "
                  f"Avg Cost: ${stats['avg_cost_per_scene']:.4f}")
            print(f"  Strengths: {', '.join(perf['strengths'])}")
            print(f"  Cost Efficiency Rank: #{cost_eff['ranking']} "
                  f"(${cost_eff['cost_per_point']:.6f} per point)")
            print()

        # Recommendations
        print("RECOMMENDATIONS:")
        print()

        recs = analysis['recommendations']
        overall = recs['overall_recommendations']

        print(f"Best Quality:     {overall['best_quality']}")
        print(f"Best Value:       {overall['best_value']}")
        print(f"Most Consistent:  {overall['most_consistent']}")
        print()

        print("Optimal Tournament Lineup:")
        for i, agent in enumerate(recs['optimal_tournament_lineup'], 1):
            print(f"  {i}. {agent}")
        print()

        print("Scene Type Recommendations:")
        for scene_type, agents in recs['scene_type_recommendations'].items():
            print(f"  {scene_type.replace('_', ' ').title()}: {', '.join(agents)}")
        print()

        print("=" * 80)

    def save_report(self, analysis: Dict, output_path: str):
        """Save analysis to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Analysis saved to: {output_path}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze agent performance across tournaments",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', required=True,
                       help='Tournament files (glob pattern, e.g., "output/*-tournament.json")')
    parser.add_argument('--output', required=True,
                       help="Output file path for analytics report (JSON)")

    args = parser.parse_args()

    # Find tournament files
    tournament_files = glob(args.input)
    if not tournament_files:
        print(f"Error: No tournament files found matching: {args.input}")
        sys.exit(1)

    print(f"Found {len(tournament_files)} tournament files")
    print()

    # Initialize analyzer
    analyzer = AgentAnalyzer()

    # Load and analyze
    analyzer.load_tournaments(tournament_files)
    analysis = analyzer.generate_profiles()

    # Print report
    analyzer.print_report(analysis)

    # Save report
    analyzer.save_report(analysis, args.output)


if __name__ == "__main__":
    main()
