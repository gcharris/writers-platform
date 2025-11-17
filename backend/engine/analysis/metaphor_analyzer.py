"""
Metaphor Domain Analyzer for Enhanced Mickey Voice

Analyzes text to detect and count metaphor usage by domain.
Ensures metaphor rotation discipline (casino ≤25%, appropriate distribution).
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class MetaphorAnalysis:
    """Analysis of metaphor usage in text."""

    domain_counts: Dict[str, int]
    domain_percentages: Dict[str, float]
    total_metaphors: int
    violations: List[str]
    score: int  # 0-25 points

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'domain_counts': self.domain_counts,
            'domain_percentages': self.domain_percentages,
            'total_metaphors': self.total_metaphors,
            'violations': self.violations,
            'score': self.score
        }


class MetaphorAnalyzer:
    """
    Analyzes metaphor domain usage in Enhanced Mickey voice.

    Detects metaphors from domains:
    - Casino/gambling (target ≤25%)
    - Addiction/recovery
    - Martial arts/combat
    - Music/performance
    - Architecture/space
    - Food/cuisine
    - Weather/nature
    - Technology (forbidden for psychology)
    - Other
    """

    # Metaphor domain keywords/patterns
    DOMAIN_PATTERNS = {
        'casino': [
            r'\b(bet|gamble|odds|stake|chip|deck|deal|hand|fold|bluff|call|raise|pot|table|dealer|house|casino|roulette|blackjack|poker|cards|shuffle|ante|jackpot|double down|all in|high roller)\b',
            r'\bstack(ed|ing)? the deck\b',
            r'\bplay(ed|ing)? (his|her|the) cards\b',
            r'\b(good|bad|poor) hand\b',
            r'\braise the stakes\b',
        ],
        'addiction': [
            r'\b(craving|withdrawal|relapse|sober|sobriety|habit|fix|dose|hit|rush|high|dependency|addiction|addict|clean|using|user|needle|substance)\b',
            r'\b(jones|jonesing|monkey on.*back)\b',
            r'\b(chasing|chase) the (dragon|high)\b',
            r'\b(need|needed|needing) a (fix|hit)\b',
        ],
        'martial_arts': [
            r'\b(stance|strike|block|parry|defense|offense|kata|dojo|sensei|belt|sparring|grapple|throw|hold|lock|submission|tap out|counter|feint|combination)\b',
            r'\b(punch|kick|jab|hook|uppercut|roundhouse)\b',
            r'\btelegraph(ed|ing)? (the|a) (move|strike)\b',
            r'\b(guard|guarded) (up|down)\b',
            r'\bread (the|his|her) (move|attack|stance)\b',
        ],
        'music': [
            r'\b(rhythm|beat|tempo|melody|harmony|chord|note|pitch|tone|symphony|orchestra|composer|conductor|performance|improvisation|riff|solo|ensemble)\b',
            r'\b(play|played|playing) (by|off) ear\b',
            r'\b(in|out of) tune\b',
            r'\bhit the (right|wrong) note\b',
        ],
        'architecture': [
            r'\b(foundation|structure|framework|scaffolding|blueprint|design|floor plan|construct|build|edifice|facade|cornerstone|pillar|beam|arch|vault)\b',
            r'\b(room|space|territory|boundary|threshold|entrance|exit)\b',
            r'\blaid the (groundwork|foundation)\b',
        ],
        'food': [
            r'\b(taste|flavor|recipe|ingredient|cook|bake|simmer|boil|blend|mix|spice|seasoning|dish|meal|course|appetite|hunger|craving|palate)\b',
            r'\b(bitter|sweet|sour|salty|savory) (taste|flavor)\b',
            r'\bdigest(ed|ing)?\b',
            r'\b(half|well)-baked\b',
        ],
        'weather': [
            r'\b(storm|thunder|lightning|rain|wind|cloud|fog|mist|snow|ice|heat|cold|temperature|climate|pressure|front|system)\b',
            r'\b(weather|weathered|weathering) (the|a) storm\b',
            r'\bcalm before the storm\b',
            r'\bperfect storm\b',
        ],
        'technology': [
            # Computer/tech metaphors (forbidden for psychology)
            r'\b(process|processing|compute|algorithm|program|code|debug|boot|reboot|install|download|upload|cache|buffer|bandwidth|circuit|wire|hardware|software|interface|database|server|client)\b',
            r'\b(neural|brain) (circuit|wiring|programming)\b',
            r'\b(re)?program(med|ming)?\b',
        ]
    }

    def __init__(self):
        """Initialize analyzer."""
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            self.compiled_patterns[domain] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]

    def analyze(self, text: str, expected_distribution: Dict[str, int] = None) -> MetaphorAnalysis:
        """
        Analyze metaphor domain usage in text.

        Args:
            text: Text to analyze
            expected_distribution: Expected percentages by domain (optional)

        Returns:
            MetaphorAnalysis with counts, percentages, and score
        """
        # Count metaphors by domain
        domain_counts = defaultdict(int)

        for domain, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                domain_counts[domain] += len(matches)

        total_metaphors = sum(domain_counts.values())

        if total_metaphors == 0:
            # No metaphors found
            return MetaphorAnalysis(
                domain_counts=dict(domain_counts),
                domain_percentages={},
                total_metaphors=0,
                violations=["No metaphors detected - voice may be too flat"],
                score=10  # Poor score for no metaphors
            )

        # Calculate percentages
        domain_percentages = {
            domain: (count / total_metaphors * 100)
            for domain, count in domain_counts.items()
        }

        # Check violations
        violations = []
        score = 25  # Start with perfect score

        # Casino overload (should be ≤25%)
        casino_pct = domain_percentages.get('casino', 0)
        if casino_pct > 25:
            violations.append(
                f"Casino metaphor overload: {casino_pct:.1f}% (target ≤25%)"
            )
            score -= min(10, int((casino_pct - 25) / 2))  # -1 point per 2% over

        # Technology metaphors for psychology (forbidden)
        tech_count = domain_counts.get('technology', 0)
        if tech_count > 0:
            violations.append(
                f"Forbidden computer metaphors for psychology: {tech_count} instances"
            )
            score -= tech_count * 2  # -2 points per instance

        # Check expected distribution if provided
        if expected_distribution:
            for domain, expected_pct in expected_distribution.items():
                actual_pct = domain_percentages.get(domain, 0)
                diff = abs(actual_pct - expected_pct)

                # Allow 10% tolerance
                if diff > 10:
                    violations.append(
                        f"{domain.title()} metaphors: {actual_pct:.1f}% "
                        f"(expected ~{expected_pct}%, diff: {diff:.1f}%)"
                    )
                    score -= min(3, int(diff / 5))  # -1 point per 5% deviation

        # Check for domain diversity (at least 3 domains)
        domains_used = len([d for d, c in domain_counts.items() if c > 0 and d != 'technology'])
        if domains_used < 3:
            violations.append(
                f"Poor domain diversity: only {domains_used} domains used (target ≥3)"
            )
            score -= (3 - domains_used) * 2

        # Ensure score stays in 0-25 range
        score = max(0, min(25, score))

        return MetaphorAnalysis(
            domain_counts=dict(domain_counts),
            domain_percentages=domain_percentages,
            total_metaphors=total_metaphors,
            violations=violations,
            score=score
        )

    def format_report(self, analysis: MetaphorAnalysis) -> str:
        """Format analysis as readable report."""
        lines = [
            "## Metaphor Domain Analysis",
            "",
            f"**Total Metaphors:** {analysis.total_metaphors}",
            f"**Score:** {analysis.score}/25",
            ""
        ]

        if analysis.domain_percentages:
            lines.extend([
                "**Domain Distribution:**",
                ""
            ])

            # Sort by percentage descending
            sorted_domains = sorted(
                analysis.domain_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for domain, percentage in sorted_domains:
                count = analysis.domain_counts[domain]
                flag = ""

                if domain == 'casino' and percentage > 25:
                    flag = " ⚠️ OVERLOAD"
                elif domain == 'technology' and count > 0:
                    flag = " ❌ FORBIDDEN"

                lines.append(f"  - **{domain.title()}**: {percentage:.1f}% ({count} instances){flag}")

            lines.append("")

        if analysis.violations:
            lines.extend([
                "**Violations:**",
                ""
            ])
            for violation in analysis.violations:
                lines.append(f"  - {violation}")
            lines.append("")
        else:
            lines.append("✓ **No violations** - excellent metaphor discipline!")
            lines.append("")

        return '\n'.join(lines)


# Example usage and testing
if __name__ == "__main__":
    analyzer = MetaphorAnalyzer()

    # Test text with mixed metaphors
    test_text = """
    Mickey read Ken's play—three moves ahead, the setup obvious as a stacked deck.
    The sobriety itch crawled up his spine, old familiar craving he'd learned to block.
    He shifted his stance, waiting for Ken to telegraph the real move.
    The room's architecture told the story: exits controlled, pressure points mapped.
    """

    expected = {
        'casino': 20,
        'addiction': 30,
        'martial_arts': 25,
        'architecture': 25
    }

    analysis = analyzer.analyze(test_text, expected)

    print("=" * 60)
    print("METAPHOR ANALYSIS TEST")
    print("=" * 60)
    print()
    print(analyzer.format_report(analysis))
    print()
    print("Raw data:")
    print(f"  Domain counts: {analysis.domain_counts}")
    print(f"  Domain percentages: {analysis.domain_percentages}")
    print(f"  Score: {analysis.score}/25")
