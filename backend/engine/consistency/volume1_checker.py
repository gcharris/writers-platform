#!/usr/bin/env python3
"""
Volume 1 Consistency Checker

Automated consistency verification for Volume 1 of The Explants trilogy.

Checks:
- Character state evolution (Mickey's addiction, Noni's abilities)
- Relationship progression (Mickey/Noni, Mickey/Sadie, etc.)
- Worldbuilding mechanics (bi-location rules, implant behavior)
- Timeline coherence (story phase progression)
- Backstory consistency (cross-reference NotebookLM)

Integrates with NotebookLM for canonical reference verification.
"""

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import ClaudeAgent
from consistency.models import (
    ConsistencyIssue,
    ConsistencyReport,
    VolumeConsistencyReport,
    CharacterState,
    RelationshipState,
    IssueSeverity,
    IssueCategory
)
from consistency.character_tracker import CharacterStateTracker
from utils.validation import BiLocationValidator, VoiceValidator


class NotebookLMInterface:
    """Interface to NotebookLM for canonical reference queries."""

    def __init__(self, query_script_path: str = "utilities/explants_nlm_query.sh"):
        """
        Initialize NotebookLM interface.

        Args:
            query_script_path: Path to NotebookLM query script
        """
        self.query_script = Path(query_script_path)

        if not self.query_script.exists():
            raise FileNotFoundError(
                f"NotebookLM query script not found: {query_script_path}\n"
                "Please ensure utilities/explants_nlm_query.sh exists."
            )

    def query(self, question: str) -> str:
        """
        Query NotebookLM for canonical information.

        Args:
            question: Natural language question

        Returns:
            Answer from NotebookLM
        """
        try:
            result = subprocess.run(
                [str(self.query_script), question],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise RuntimeError(f"NotebookLM query failed: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("NotebookLM query timed out after 60 seconds")
        except Exception as e:
            raise RuntimeError(f"NotebookLM query error: {e}")


class Volume1ConsistencyChecker:
    """
    Automated consistency checker for Volume 1.

    Checks character states, relationships, worldbuilding, timeline, and backstories
    against established canon from NotebookLM.
    """

    # Volume 1 structure
    VOLUME_1_ACTS = [
        "A FRONT_MATTER",
        "ACT 1",         # Chapters 1.1-1.10 (Phase 1)
        "ACT 2A",        # Chapters 1.11-1.20 (Phase 2)
        "ACT 2B",        # Chapters 1.21-1.28 (Phase 2)
        "BACK_MATTER"
    ]

    # Story phase mapping
    STORY_PHASES = {
        "ACT 1": 1,      # Setup
        "ACT 2A": 2,     # Development
        "ACT 2B": 2      # Development continues
    }

    def __init__(self,
                 nlm_interface: Optional[NotebookLMInterface] = None,
                 agent: Optional[ClaudeAgent] = None,
                 verbose: bool = False):
        """
        Initialize consistency checker.

        Args:
            nlm_interface: NotebookLM query interface (optional)
            agent: Claude Sonnet 4.5 for analysis (optional, will create if None)
            verbose: Enable verbose logging
        """
        self.nlm = nlm_interface
        self.verbose = verbose

        # Initialize agent for analysis
        if agent is None:
            self.agent = ClaudeAgent(model="claude-sonnet-4-5-20250929")
        else:
            self.agent = agent

        # Initialize validators
        self.bilocation_validator = BiLocationValidator()
        self.voice_validator = VoiceValidator()

        # Initialize character tracker
        self.tracker = CharacterStateTracker()

        # Cache canonical references from NotebookLM
        self.canonical_cache: Dict[str, str] = {}

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def query_canonical(self, question: str) -> Optional[str]:
        """
        Query NotebookLM for canonical reference (with caching).

        Args:
            question: Question to ask

        Returns:
            Answer from NotebookLM, or None if NLM unavailable
        """
        if self.nlm is None:
            self.log("NotebookLM not available, skipping canonical query", "WARNING")
            return None

        # Check cache first
        if question in self.canonical_cache:
            self.log(f"Using cached canonical reference for: {question[:50]}...")
            return self.canonical_cache[question]

        # Query NotebookLM
        try:
            self.log(f"Querying NotebookLM: {question[:50]}...")
            answer = self.nlm.query(question)
            self.canonical_cache[question] = answer
            return answer

        except Exception as e:
            self.log(f"NotebookLM query failed: {e}", "ERROR")
            return None

    def parse_scene_id(self, filename: str) -> Optional[str]:
        """
        Extract scene ID from filename.

        Examples:
            "1.3.2 blackjack scene.md" → "1.3.2"
            "Chapter_3/1.3.5 confrontation.md" → "1.3.5"
        """
        # Match pattern: X.Y.Z at start of filename
        match = re.search(r'(\d+\.\d+\.\d+)', filename)
        if match:
            return match.group(1)

        return None

    def extract_story_phase(self, scene_path: Path) -> int:
        """
        Extract story phase from scene path.

        Args:
            scene_path: Path to scene file

        Returns:
            Story phase (1 or 2)
        """
        path_str = str(scene_path)

        for act, phase in self.STORY_PHASES.items():
            if act in path_str:
                return phase

        # Default to phase 1 if can't determine
        return 1

    def check_scene(self, scene_path: Path,
                   scene_number: Optional[str] = None,
                   story_phase: Optional[int] = None) -> ConsistencyReport:
        """
        Check single scene for consistency issues.

        Args:
            scene_path: Path to scene file
            scene_number: Scene ID (e.g., "1.3.2"), will parse from filename if None
            story_phase: Story phase (1-2), will extract from path if None

        Returns:
            ConsistencyReport with all issues found
        """
        self.log(f"Checking scene: {scene_path.name}")

        # Parse scene ID if not provided
        if scene_number is None:
            scene_number = self.parse_scene_id(scene_path.name)
            if scene_number is None:
                scene_number = scene_path.stem  # Fallback to filename

        # Extract story phase if not provided
        if story_phase is None:
            story_phase = self.extract_story_phase(scene_path)

        # Read scene content
        try:
            with open(scene_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.log(f"Error reading scene: {e}", "ERROR")
            return ConsistencyReport(
                scene_id=scene_number,
                scene_path=str(scene_path),
                story_phase=story_phase,
                issues=[
                    ConsistencyIssue(
                        category=IssueCategory.TIMELINE,
                        severity=IssueSeverity.CRITICAL,
                        description=f"Unable to read scene file",
                        scenes_affected=[scene_number],
                        problem_details=str(e),
                        recommendation="Check file permissions and encoding"
                    )
                ]
            )

        # Initialize report
        report = ConsistencyReport(
            scene_id=scene_number,
            scene_path=str(scene_path),
            story_phase=story_phase
        )

        # Run all consistency checks
        report.issues.extend(self._check_worldbuilding_mechanics(content, scene_number))
        report.issues.extend(self._check_voice_violations(content, scene_number))
        report.issues.extend(self._check_character_consistency(content, scene_number, story_phase))
        report.issues.extend(self._check_backstory_consistency(content, scene_number))

        # Extract character and relationship states for timeline tracking
        self._extract_character_states(content, scene_number, story_phase, report)
        self._extract_relationship_states(content, scene_number, story_phase, report)

        self.log(f"Found {len(report.issues)} issues in {scene_number}")

        return report

    def _check_worldbuilding_mechanics(self, content: str, scene_id: str) -> List[ConsistencyIssue]:
        """Check worldbuilding mechanics consistency (bi-location, implants, etc.)."""
        issues = []

        # Check bi-location mechanics
        bilocation_result = self.bilocation_validator.validate(content)

        if not bilocation_result['valid']:
            # Forbidden jargon found
            for violation in bilocation_result.get('violations', []):
                issues.append(ConsistencyIssue(
                    category=IssueCategory.WORLDBUILDING,
                    severity=IssueSeverity.CRITICAL,
                    description="Forbidden Bi-location Jargon",
                    scenes_affected=[scene_id],
                    problem_details=f"Forbidden term found: {violation.get('term', 'unknown')}",
                    recommendation=f"Replace with correct terminology: {violation.get('correct_term', 'The Line, The Tether, The Shared Vein')}"
                ))

        # Check for correct bi-location terms being used
        correct_terms = ["The Line", "The Tether", "The Shared Vein"]
        has_bilocation_content = any(term.lower() in content.lower() for term in ["bi-location", "bilocation"])

        if has_bilocation_content:
            uses_correct_terms = any(term in content for term in correct_terms)

            if not uses_correct_terms:
                issues.append(ConsistencyIssue(
                    category=IssueCategory.WORLDBUILDING,
                    severity=IssueSeverity.MODERATE,
                    description="Missing Correct Bi-location Terminology",
                    scenes_affected=[scene_id],
                    problem_details="Scene discusses bi-location but doesn't use correct terms",
                    recommendation=f"Use established terms: {', '.join(correct_terms)}"
                ))

        return issues

    def _check_voice_violations(self, content: str, scene_id: str) -> List[ConsistencyIssue]:
        """Check for voice violations (forbidden phrases, incorrect style)."""
        issues = []

        # Use voice validator
        voice_result = self.voice_validator.validate(content)

        if not voice_result['valid']:
            for violation in voice_result.get('violations', []):
                issues.append(ConsistencyIssue(
                    category=IssueCategory.VOICE,
                    severity=IssueSeverity.MODERATE,
                    description="Voice Violation",
                    scenes_affected=[scene_id],
                    problem_details=violation.get('message', 'Voice violation detected'),
                    recommendation="Rewrite using Enhanced Mickey voice: compressed phrasing, direct metaphors, present-tense urgency"
                ))

        return issues

    def _check_character_consistency(self, content: str, scene_id: str, story_phase: int) -> List[ConsistencyIssue]:
        """Check character consistency using Claude analysis."""
        issues = []

        # Use Claude to analyze character consistency
        analysis_prompt = f"""Analyze this scene from The Explants Volume 1 for character consistency issues.

Scene ID: {scene_id}
Story Phase: {story_phase}

Content:
{content[:3000]}  # First 3000 chars

Check for:
1. Character behavior matching established personality
2. Capabilities consistent with story phase
3. Psychological state coherence
4. Relationships matching established dynamics

Report any CRITICAL inconsistencies (character doing something completely out of character or impossible for them).

Format your response as:
CONSISTENT: [Yes/No]
ISSUES:
- [Issue description if any]

Be strict but reasonable. Only flag clear inconsistencies."""

        try:
            response = self.agent.generate(analysis_prompt, max_tokens=500)

            # Parse response
            if "CONSISTENT: No" in response or "ISSUES:" in response:
                # Extract issues
                issue_match = re.search(r'ISSUES:\s*\n(.+)', response, re.DOTALL)
                if issue_match:
                    issue_text = issue_match.group(1).strip()

                    if issue_text and issue_text != "-" and "None" not in issue_text:
                        issues.append(ConsistencyIssue(
                            category=IssueCategory.CHARACTER_STATE,
                            severity=IssueSeverity.MODERATE,
                            description="Character Behavior Inconsistency",
                            scenes_affected=[scene_id],
                            problem_details=issue_text,
                            recommendation="Review character state and capabilities for this scene"
                        ))

        except Exception as e:
            self.log(f"Error in character consistency check: {e}", "ERROR")

        return issues

    def _check_backstory_consistency(self, content: str, scene_id: str) -> List[ConsistencyIssue]:
        """Check backstory consistency against NotebookLM canonical references."""
        issues = []

        # Check for character backstory mentions
        characters = ["Sadie", "Mickey", "Noni", "Dr. Webb"]

        for character in characters:
            if character.lower() in content.lower():
                # Check for backstory keywords
                backstory_keywords = ["history", "past", "before", "used to", "remember when", "years ago"]

                has_backstory = any(keyword in content.lower() for keyword in backstory_keywords)

                if has_backstory and self.nlm:
                    # Query NotebookLM for canonical backstory
                    canonical = self.query_canonical(f"What is {character}'s canonical backstory in Volume 1?")

                    if canonical:
                        # Use Claude to compare
                        comparison_prompt = f"""Compare this scene's portrayal of {character} against the canonical backstory.

Canonical backstory:
{canonical[:1000]}

Scene content:
{content[:2000]}

Is there any DIRECT CONTRADICTION between the scene and canonical backstory?

Format:
CONTRADICTS: [Yes/No]
DETAILS: [Specific contradiction if Yes]
"""

                        try:
                            response = self.agent.generate(comparison_prompt, max_tokens=300)

                            if "CONTRADICTS: Yes" in response:
                                details_match = re.search(r'DETAILS:\s*(.+)', response, re.DOTALL)
                                details = details_match.group(1).strip() if details_match else "Backstory contradiction detected"

                                issues.append(ConsistencyIssue(
                                    category=IssueCategory.BACKSTORY,
                                    severity=IssueSeverity.CRITICAL,
                                    description=f"{character} Backstory Contradiction",
                                    scenes_affected=[scene_id],
                                    problem_details=details,
                                    canonical_reference=canonical[:200] + "...",
                                    recommendation=f"Update scene to match canonical backstory from NotebookLM"
                                ))

                        except Exception as e:
                            self.log(f"Error checking backstory: {e}", "ERROR")

        return issues

    def _extract_character_states(self, content: str, scene_id: str, story_phase: int,
                                  report: ConsistencyReport):
        """Extract character states from scene for timeline tracking."""
        # This is simplified - in production, would use more sophisticated NLP/Claude analysis

        # Mickey Bardot state extraction
        if "mickey" in content.lower():
            state = CharacterState(
                character_name="Mickey Bardot",
                scene_id=scene_id,
                story_phase=story_phase
            )

            # Look for addiction markers
            if "sober" in content.lower() or "sobriety" in content.lower():
                # Try to extract sobriety count
                sober_match = re.search(r'(\d+)\s+days?\s+sober', content.lower())
                if sober_match:
                    state.attributes['sobriety_days'] = int(sober_match.group(1))

            # Look for quantum hindsight usage
            if "quantum hindsight" in content.lower() or "implant" in content.lower():
                state.abilities.append("quantum_hindsight")

            report.character_states["Mickey Bardot"] = state
            self.tracker.add_character_state(state)

        # Noni state extraction
        if "noni" in content.lower():
            state = CharacterState(
                character_name="Noni",
                scene_id=scene_id,
                story_phase=story_phase
            )

            # Look for morphic resonance
            if "morphic resonance" in content.lower():
                state.abilities.append("morphic_resonance")

                # Try to determine range
                if "touch" in content.lower() and "resonance" in content.lower():
                    state.attributes['morphic_resonance_range'] = "touch"
                elif "far" in content.lower() or "distance" in content.lower():
                    state.attributes['morphic_resonance_range'] = "far"

            report.character_states["Noni"] = state
            self.tracker.add_character_state(state)

    def _extract_relationship_states(self, content: str, scene_id: str, story_phase: int,
                                    report: ConsistencyReport):
        """Extract relationship states from scene for timeline tracking."""
        # This is simplified - would use more sophisticated analysis in production

        # Mickey/Noni relationship
        if "mickey" in content.lower() and "noni" in content.lower():
            state = RelationshipState(
                character_a="Mickey Bardot",
                character_b="Noni",
                scene_id=scene_id,
                story_phase=story_phase,
                relationship_type="professional/romantic",
                dynamic="Complex, evolving",
                trust_level="medium"  # Default, would extract from content
            )

            # Look for trust indicators
            if "trust" in content.lower():
                if "trust" in content.lower() and ("high" in content.lower() or "complete" in content.lower()):
                    state.trust_level = "high"
                elif "distrust" in content.lower() or "don't trust" in content.lower():
                    state.trust_level = "low"

            report.relationship_states["Mickey Bardot ↔ Noni"] = state
            self.tracker.add_relationship_state(state)

    def check_volume(self, volume_path: Path, output_path: Optional[Path] = None) -> VolumeConsistencyReport:
        """
        Check entire Volume 1 for consistency.

        Args:
            volume_path: Path to Volume 1 directory
            output_path: Optional path to save report

        Returns:
            VolumeConsistencyReport with all issues found
        """
        self.log(f"Checking Volume 1: {volume_path}")

        volume_report = VolumeConsistencyReport(
            volume_name="Volume 1",
            volume_path=str(volume_path)
        )

        # Scan all acts
        for act in self.VOLUME_1_ACTS:
            if act in ["A FRONT_MATTER", "BACK_MATTER"]:
                continue  # Skip front/back matter

            act_path = volume_path / act
            if not act_path.exists():
                self.log(f"Act directory not found: {act_path}", "WARNING")
                continue

            self.log(f"Scanning {act}...")

            # Find all scene files
            scene_files = []
            for pattern in ["**/*.md", "**/*.markdown"]:
                scene_files.extend(act_path.glob(pattern))

            # Filter out Archive directories
            scene_files = [f for f in scene_files if "Archive" not in str(f) and "archive" not in str(f)]

            self.log(f"Found {len(scene_files)} scenes in {act}")

            # Check each scene
            for scene_file in sorted(scene_files):
                try:
                    report = self.check_scene(scene_file)
                    volume_report.scene_reports.append(report)
                    volume_report.scenes_checked += 1

                    # Collect issues by severity
                    volume_report.critical_issues.extend(report.critical_issues)
                    volume_report.moderate_issues.extend(report.moderate_issues)
                    volume_report.minor_issues.extend(report.minor_issues)

                except Exception as e:
                    self.log(f"Error checking scene {scene_file}: {e}", "ERROR")

        # Run cross-scene consistency checks using tracker
        self.log("Running cross-scene consistency checks...")
        self._check_timeline_consistency(volume_report)

        # Generate character timelines
        for character in self.tracker.known_characters:
            timeline = self.tracker.get_character_timeline(character)
            if timeline:
                volume_report.character_timelines[character] = timeline

        # Generate relationship timelines
        relationships = [
            ("Mickey Bardot", "Noni"),
            ("Mickey Bardot", "Sadie"),
            ("Mickey Bardot", "Dr. Webb")
        ]

        for char_a, char_b in relationships:
            timeline = self.tracker.get_relationship_timeline(char_a, char_b)
            if timeline:
                key = f"{char_a} ↔ {char_b}"
                volume_report.relationship_timelines[key] = timeline

        # Save report if output path provided
        if output_path:
            self._save_report(volume_report, output_path)

        self.log(f"Volume check complete: {volume_report.total_issues} issues found")

        return volume_report

    def _check_timeline_consistency(self, volume_report: VolumeConsistencyReport):
        """Run timeline consistency checks across all scenes."""
        # Check character timelines
        for character in self.tracker.known_characters:
            issues = self.tracker.check_character_consistency(character)
            volume_report.moderate_issues.extend(issues)

        # Check relationship timelines
        relationships = [
            ("Mickey Bardot", "Noni"),
            ("Mickey Bardot", "Sadie")
        ]

        for char_a, char_b in relationships:
            issues = self.tracker.check_relationship_consistency(char_a, char_b)
            volume_report.moderate_issues.extend(issues)

    def _save_report(self, report: VolumeConsistencyReport, output_path: Path):
        """Save consistency report to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save markdown report
        if output_path.suffix == '.md':
            with open(output_path, 'w') as f:
                f.write(report.to_markdown())

            self.log(f"Saved markdown report: {output_path}")

            # Also save JSON version
            json_path = output_path.with_suffix('.json')
            with open(json_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)

            self.log(f"Saved JSON report: {json_path}")

        # Save JSON report
        elif output_path.suffix == '.json':
            with open(output_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)

            self.log(f"Saved JSON report: {output_path}")

        else:
            # Default to markdown
            with open(output_path, 'w') as f:
                f.write(report.to_markdown())

            self.log(f"Saved report: {output_path}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Volume 1 Consistency Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single scene
  python3 framework/consistency/volume1_checker.py \\
      --scene "The Explants Series/Volume 1/ACT 1/1.3.2 blackjack.md" \\
      --scene-number "1.3.2" \\
      --phase 1

  # Check entire volume
  python3 framework/consistency/volume1_checker.py \\
      --volume "The Explants Series/Volume 1" \\
      --output reports/volume1_consistency_report.md

  # Check specific category only
  python3 framework/consistency/volume1_checker.py \\
      --volume "The Explants Series/Volume 1" \\
      --check-only characters

  # Without NotebookLM (faster, but skips canonical checks)
  python3 framework/consistency/volume1_checker.py \\
      --volume "The Explants Series/Volume 1" \\
      --no-nlm
        """
    )

    parser.add_argument('--scene', help="Check single scene file")
    parser.add_argument('--scene-number', help="Scene ID (e.g., '1.3.2')")
    parser.add_argument('--phase', type=int, help="Story phase (1 or 2)")

    parser.add_argument('--volume', help="Check entire volume directory")
    parser.add_argument('--output', help="Output report path (.md or .json)")

    parser.add_argument('--check-only', choices=['characters', 'relationships', 'worldbuilding', 'timeline'],
                       help="Check only specific category")

    parser.add_argument('--no-nlm', action='store_true',
                       help="Skip NotebookLM queries (faster, but less thorough)")

    parser.add_argument('--verbose', action='store_true',
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Validate arguments
    if not args.scene and not args.volume:
        parser.error("Must specify either --scene or --volume")

    # Initialize NotebookLM interface
    nlm = None
    if not args.no_nlm:
        try:
            nlm = NotebookLMInterface()
            print("✓ NotebookLM interface initialized")
        except Exception as e:
            print(f"⚠️  NotebookLM not available: {e}")
            print("Continuing without canonical reference checks...")

    # Initialize checker
    checker = Volume1ConsistencyChecker(nlm_interface=nlm, verbose=args.verbose)

    # Check single scene
    if args.scene:
        scene_path = Path(args.scene)

        if not scene_path.exists():
            print(f"❌ Scene file not found: {scene_path}")
            return 1

        report = checker.check_scene(
            scene_path,
            scene_number=args.scene_number,
            story_phase=args.phase
        )

        print("\n" + "=" * 80)
        print(f"SCENE CONSISTENCY REPORT: {report.scene_id}")
        print("=" * 80)
        print(f"Consistency Score: {report.consistency_score}/100")
        print(f"Issues Found: {len(report.issues)}")
        print(f"  - Critical: {len(report.critical_issues)}")
        print(f"  - Moderate: {len(report.moderate_issues)}")
        print(f"  - Minor: {len(report.minor_issues)}")
        print()

        if report.issues:
            for i, issue in enumerate(report.issues, 1):
                print(f"{i}. [{issue.severity.value.upper()}] {issue.description}")
                print(f"   {issue.problem_details}")
                print(f"   Recommendation: {issue.recommendation}")
                print()

        return 0 if not report.critical_issues else 1

    # Check entire volume
    elif args.volume:
        volume_path = Path(args.volume)

        if not volume_path.exists():
            print(f"❌ Volume directory not found: {volume_path}")
            return 1

        output_path = Path(args.output) if args.output else None

        report = checker.check_volume(volume_path, output_path)

        print("\n" + "=" * 80)
        print(f"VOLUME 1 CONSISTENCY REPORT")
        print("=" * 80)
        print(f"Scenes Checked: {report.scenes_checked}")
        print(f"Consistency Grade: {report.grade} ({report.consistency_score}/100)")
        print(f"Total Issues: {report.total_issues}")
        print(f"  - Critical: {len(report.critical_issues)}")
        print(f"  - Moderate: {len(report.moderate_issues)}")
        print(f"  - Minor: {len(report.minor_issues)}")
        print()

        if report.critical_issues:
            print("CRITICAL ISSUES (Must Fix):")
            for i, issue in enumerate(report.critical_issues[:5], 1):
                print(f"{i}. {issue.description}")
                print(f"   Scenes: {', '.join(issue.scenes_affected)}")
                print(f"   {issue.problem_details}")
                print()

            if len(report.critical_issues) > 5:
                print(f"... and {len(report.critical_issues) - 5} more critical issues")
                print()

        if output_path:
            print(f"✓ Full report saved to: {output_path}")
        else:
            print("⚠️  No output path specified, report not saved")

        print()

        return 0 if not report.critical_issues else 1


if __name__ == "__main__":
    sys.exit(main())
