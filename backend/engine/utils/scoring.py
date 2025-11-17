"""
Scene Scoring System

Implements hybrid scoring approach:
1. Rule-based validation (forbidden jargon, voice markers)
2. LLM-based quality scoring (7 criteria)

Scores scenes on:
- Enhanced Mickey voice authenticity (0-10)
- Character consistency (0-10)
- Worldbuilding integration (0-10)
- Pacing (0-10)
- Dialogue naturalness (0-10)
- Emotional impact (0-10)
- Consciousness war argument progression (0-10)
"""

import json
import re
from typing import Dict, Optional
from dataclasses import dataclass, asdict

from .validation import validate_scene


@dataclass
class SceneScores:
    """Scene quality scores."""
    voice_authenticity: float
    character_consistency: float
    worldbuilding: float
    pacing: float
    dialogue: float
    emotional_impact: float
    consciousness_war: float
    total: float
    reasoning: Dict[str, str]


class SceneScorer:
    """Scores scenes using hybrid approach: rule-based + LLM."""

    SCORING_PROMPT_TEMPLATE = """Score this scene on 7 criteria using a 0-10 scale. Be strict but fair.

SCENE:
---
{scene_content}
---

SCORING CRITERIA:

1. **voice_authenticity** (0-10): Enhanced Mickey Bardot voice
   - Compressed phrasing (e.g., "geometried themselves", "refused to stay")
   - Direct metaphors (e.g., "deeper than quantum transformation reached")
   - Present-tense urgency
   - Embedded personality (con artist, gambling metaphors)
   - NO academic/technical language
   - Uses "The Line", "The Tether", "The Shared Vein" (NOT "quantum link")

2. **character_consistency** (0-10): Characters behave true to established profiles
   - Mickey: Con artist, cynical, dual consciousness strain, addiction themes
   - Noni: Morphic resonance, pattern reader, spiritual practitioner perspective
   - Other characters: Match established personalities and motivations

3. **worldbuilding_integration** (0-10): Seamless incorporation of universe elements
   - Q5 chip mechanics (computer-brain interface)
   - Bi-location shown through physical strain (NOT technical announcements)
   - Corporate control, consciousness war themes
   - Dystopian future elements
   - No exposition dumps

4. **pacing** (0-10): Scene rhythm and momentum
   - Strong opening hook
   - Varied sentence lengths
   - Tension builds appropriately
   - No dragging sections
   - Satisfying beats/moments

5. **dialogue_naturalness** (0-10): Authentic character dialogue
   - Character-specific voices
   - Natural flow, not stilted
   - Advances plot/character
   - Shows emotion/conflict
   - Avoids on-the-nose exposition

6. **emotional_impact** (0-10): Reader engagement and emotional resonance
   - Visceral physical descriptions
   - Emotional authenticity
   - Stakes feel real
   - Creates reader investment
   - Memorable moments

7. **consciousness_war_argument** (0-10): Advances philosophical thesis
   - Explores human vs. AI consciousness
   - Addresses identity, control, autonomy themes
   - Not preachy or on-the-nose
   - Integrated into action/character
   - Adds depth without stopping narrative

CRITICAL VOICE REQUIREMENTS:
- FORBIDDEN JARGON: "quantum link", "bi-location mode", "split consciousness", "entering bi-location"
- REQUIRED TERMS: "The Line" (Mickey/Noni connection), "The Tether" (quantum binding), "The Shared Vein" (toxic connection)
- BI-LOCATION SHOWING: Physical strain (temples pulsing, shadow splitting, voice desync), NOT technical announcements
- NONI'S ROLE: Active interpreter with morphic resonance, NOT passive receiver

OUTPUT FORMAT (valid JSON only, no additional text):
{{
  "voice_authenticity": 8.5,
  "character_consistency": 9.0,
  "worldbuilding": 8.0,
  "pacing": 7.5,
  "dialogue": 8.5,
  "emotional_impact": 9.0,
  "consciousness_war": 8.0,
  "reasoning": {{
    "voice_authenticity": "Brief explanation",
    "character_consistency": "Brief explanation",
    "worldbuilding": "Brief explanation",
    "pacing": "Brief explanation",
    "dialogue": "Brief explanation",
    "emotional_impact": "Brief explanation",
    "consciousness_war": "Brief explanation"
  }}
}}

Score the scene now. Output ONLY the JSON, no additional commentary:"""

    def __init__(self, agent):
        """
        Initialize scorer with an AI agent for LLM scoring.

        Args:
            agent: BaseAgent instance (typically Claude Sonnet 4.5)
        """
        self.agent = agent

    def score_scene(self, scene_content: str, agent_name: str = "unknown") -> Dict:
        """
        Score a scene using hybrid approach.

        Args:
            scene_content: Scene text to score
            agent_name: Name of agent that generated the scene

        Returns:
            Dictionary with scores and validation results
        """
        # Step 1: Rule-based validation
        validation_results = validate_scene(scene_content)

        # Step 2: LLM-based scoring
        llm_scores = self._score_with_llm(scene_content)

        # Step 3: Adjust LLM scores based on validation
        adjusted_scores = self._adjust_scores_with_validation(
            llm_scores, validation_results
        )

        # Step 4: Calculate word count
        word_count = len(scene_content.split())

        return {
            'agent': agent_name,
            'word_count': word_count,
            'scores': adjusted_scores,
            'validation': validation_results,
            'raw_llm_scores': llm_scores
        }

    def _score_with_llm(self, scene_content: str) -> Dict:
        """
        Score scene using LLM (Claude Sonnet 4.5).

        Args:
            scene_content: Scene text

        Returns:
            Dictionary with scores and reasoning
        """
        # Truncate scene if too long (keep first 3000 words for scoring)
        words = scene_content.split()
        if len(words) > 3000:
            scene_content = ' '.join(words[:3000]) + "\n\n[... scene truncated for scoring ...]"

        prompt = self.SCORING_PROMPT_TEMPLATE.format(scene_content=scene_content)

        try:
            response = self.agent.generate(
                prompt=prompt,
                system_prompt="You are an expert editor for science fiction novels, specializing in character voice and narrative craft. Provide precise, structured scores.",
                max_tokens=2000,
                temperature=0.3  # Lower temperature for consistent scoring
            )

            # Extract JSON from response
            scores_dict = self._extract_json_scores(response.content)

            # Calculate total
            if scores_dict and 'reasoning' in scores_dict:
                total = sum([
                    scores_dict.get('voice_authenticity', 0),
                    scores_dict.get('character_consistency', 0),
                    scores_dict.get('worldbuilding', 0),
                    scores_dict.get('pacing', 0),
                    scores_dict.get('dialogue', 0),
                    scores_dict.get('emotional_impact', 0),
                    scores_dict.get('consciousness_war', 0)
                ])
                scores_dict['total'] = round(total, 1)

                return scores_dict

        except Exception as e:
            print(f"Error during LLM scoring: {e}")

        # Fallback: return default scores
        return self._get_default_scores()

    def _extract_json_scores(self, response_text: str) -> Optional[Dict]:
        """
        Extract JSON scores from LLM response.

        Args:
            response_text: LLM response text

        Returns:
            Dictionary with scores or None if parsing fails
        """
        try:
            # Try direct JSON parse first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in text (between curly braces)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _adjust_scores_with_validation(self, llm_scores: Dict,
                                      validation_results: Dict) -> Dict:
        """
        Adjust LLM scores based on rule-based validation.

        Args:
            llm_scores: Scores from LLM
            validation_results: Rule-based validation results

        Returns:
            Adjusted scores
        """
        adjusted = llm_scores.copy()

        bi_location = validation_results.get('bi_location', {})
        voice = validation_results.get('voice', {})

        # Penalty for forbidden jargon
        forbidden_count = len(bi_location.get('forbidden_jargon_found', []))
        if forbidden_count > 0:
            penalty = min(forbidden_count * 1.5, 5.0)  # Max -5 points
            adjusted['voice_authenticity'] = max(0, adjusted.get('voice_authenticity', 5) - penalty)

        # Bonus for correct terms
        correct_terms = len(bi_location.get('correct_terms_used', []))
        if correct_terms >= 2:
            bonus = min(correct_terms * 0.5, 2.0)  # Max +2 points
            adjusted['voice_authenticity'] = min(10, adjusted.get('voice_authenticity', 5) + bonus)

        # Penalty for anti-patterns
        if voice.get('has_anti_patterns'):
            adjusted['voice_authenticity'] = max(0, adjusted.get('voice_authenticity', 5) - 1.0)

        # Bonus for bi-location shown properly
        if bi_location.get('bi_location_shown_properly'):
            adjusted['worldbuilding'] = min(10, adjusted.get('worldbuilding', 5) + 1.0)

        # Recalculate total
        adjusted['total'] = round(sum([
            adjusted.get('voice_authenticity', 0),
            adjusted.get('character_consistency', 0),
            adjusted.get('worldbuilding', 0),
            adjusted.get('pacing', 0),
            adjusted.get('dialogue', 0),
            adjusted.get('emotional_impact', 0),
            adjusted.get('consciousness_war', 0)
        ]), 1)

        return adjusted

    def _get_default_scores(self) -> Dict:
        """Get default scores if LLM scoring fails."""
        return {
            'voice_authenticity': 5.0,
            'character_consistency': 5.0,
            'worldbuilding': 5.0,
            'pacing': 5.0,
            'dialogue': 5.0,
            'emotional_impact': 5.0,
            'consciousness_war': 5.0,
            'total': 35.0,
            'reasoning': {
                'note': 'Default scores - LLM scoring failed'
            }
        }


def format_score_summary(score_result: Dict) -> str:
    """
    Format score results as readable text.

    Args:
        score_result: Score dictionary from score_scene()

    Returns:
        Formatted string
    """
    scores = score_result.get('scores', {})
    validation = score_result.get('validation', {})
    bi_location = validation.get('bi_location', {})

    lines = [
        f"Agent: {score_result.get('agent', 'unknown')}",
        f"Word Count: {score_result.get('word_count', 0)}",
        f"",
        "SCORES:",
        f"  Voice Authenticity:    {scores.get('voice_authenticity', 0):.1f}/10",
        f"  Character Consistency: {scores.get('character_consistency', 0):.1f}/10",
        f"  Worldbuilding:         {scores.get('worldbuilding', 0):.1f}/10",
        f"  Pacing:                {scores.get('pacing', 0):.1f}/10",
        f"  Dialogue:              {scores.get('dialogue', 0):.1f}/10",
        f"  Emotional Impact:      {scores.get('emotional_impact', 0):.1f}/10",
        f"  Consciousness War:     {scores.get('consciousness_war', 0):.1f}/10",
        f"  ---",
        f"  TOTAL:                 {scores.get('total', 0):.1f}/70",
        f"",
        "VALIDATION:",
    ]

    if bi_location.get('forbidden_jargon_found'):
        lines.append(f"  ⚠️  Forbidden jargon: {', '.join(bi_location['forbidden_jargon_found'])}")

    if bi_location.get('correct_terms_used'):
        lines.append(f"  ✓ Correct terms: {', '.join(bi_location['correct_terms_used'])}")

    if bi_location.get('bi_location_shown_properly'):
        lines.append("  ✓ Bi-location shown through physical strain")

    if bi_location.get('issues'):
        lines.append("  Issues:")
        for issue in bi_location['issues']:
            lines.append(f"    - {issue}")

    return '\n'.join(lines)
