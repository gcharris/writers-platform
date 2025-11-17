"""Character dimensional depth analyzer.

Detects contradictions and complexity in character design based on
NotebookLM craft knowledge insights.

Key Principle: "Complexity is created by CONTRADICTION"
- Internal contradictions (guilt-ridden ambition)
- External contradictions (charming thief, lonely but smiling)
- Deep flaws driven by mistaken beliefs
- Supporting cast that reveals protagonist dimensions
"""

from typing import Dict, List, Any, Optional


def analyze_character_depth(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze character for dimensional depth through contradiction.

    Args:
        character_data: Character data dictionary with fields:
            - core_traits: List of internal traits
            - observable_traits: List of external traits
            - fatal_flaw: Character's fatal flaw
            - mistaken_belief: Underlying mistaken belief
            - role: Character role (protagonist/antagonist/supporting)

    Returns:
        Dictionary with:
            - depth_score (0-100)
            - flags (list of issues detected)
            - recommendations (list of fixes)
    """
    results = {
        "depth_score": 0,
        "flags": [],
        "recommendations": []
    }

    # 1. CHECK: External Contradiction (True Character vs Characterization)
    core_traits = character_data.get("core_traits", [])
    observable_traits = character_data.get("observable_traits", [])

    if not core_traits or not observable_traits:
        results["flags"].append({
            "severity": "HIGH",
            "type": "INCOMPLETE_CHARACTER_DEFINITION",
            "message": "Character lacks both True Character and Characterization data.",
            "recommendation": "Define core internal traits (True Character) and observable external traits (Characterization)"
        })
    elif are_traits_identical(core_traits, observable_traits):
        results["flags"].append({
            "severity": "HIGH",
            "type": "NO_EXTERNAL_CONTRADICTION",
            "message": "True Character directly mirrors Characterization. Character is predictable and flat.",
            "example": "If core is 'Courageous, Loyal' and actions are always 'Bold, Honorable', there's no mask or conflict.",
            "recommendation": "Create dissonance: e.g., 'loyal' internally but appears 'untrustworthy' externally (a charming thief)"
        })
    else:
        results["depth_score"] += 25

    # 2. CHECK: Internal Contradiction (Within True Character)
    internal_contradiction = detect_trait_polarity(core_traits)

    if not internal_contradiction:
        results["flags"].append({
            "severity": "CRITICAL",
            "type": "NO_INTERNAL_CONTRADICTION",
            "message": "Character has no internal contradictions detected.",
            "example": "Need opposing forces like 'guilt-ridden ambition' or 'compassionate yet cruel'",
            "recommendation": "Add contradictory core traits that create internal tension"
        })
    else:
        results["depth_score"] += 35
        results["recommendations"].append({
            "type": "STRENGTH",
            "message": f"Good internal contradiction detected: {internal_contradiction}"
        })

    # 3. CHECK: Fatal Flaw Depth
    flaw = character_data.get("fatal_flaw", "")
    mistaken_belief = character_data.get("mistaken_belief", "")

    if not flaw or len(flaw) < 10:
        results["flags"].append({
            "severity": "MEDIUM",
            "type": "MISSING_FLAW",
            "message": "Character lacks a defined fatal flaw.",
            "recommendation": "Define a flaw that will drive character transformation"
        })
    elif not mistaken_belief or len(mistaken_belief) < 20:
        results["flags"].append({
            "severity": "HIGH",
            "type": "SHALLOW_FLAW",
            "message": "Flaw description lacks clear mistaken belief or transformational potential.",
            "example": "'Impatient' (observation) vs 'Must control everything or will fail' (deep psychological conflict)",
            "recommendation": "Reframe flaw as a mistaken belief the character must overcome to transform"
        })
    else:
        results["depth_score"] += 20

    # 4. CHECK: Values and Fears (adds depth)
    values = character_data.get("values", [])
    fears = character_data.get("fears", [])

    if values and fears:
        results["depth_score"] += 10
        results["recommendations"].append({
            "type": "STRENGTH",
            "message": "Character has defined values and fears, adding psychological depth"
        })

    # 5. CHECK: Appearance and speech (adds dimensionality)
    appearance = character_data.get("appearance", "")
    speech_pattern = character_data.get("speech_pattern", "")

    if appearance and speech_pattern:
        results["depth_score"] += 10
        results["recommendations"].append({
            "type": "STRENGTH",
            "message": "Character has distinct appearance and speech patterns"
        })

    return results


def are_traits_identical(core_traits: List[str], observable_traits: List[str]) -> bool:
    """Check if core and observable traits are too similar (no contradiction).

    Args:
        core_traits: Internal character traits
        observable_traits: External observable traits

    Returns:
        True if traits are too similar (>70% overlap), False otherwise
    """
    # Simple heuristic: if >70% of traits overlap semantically, they're too similar
    core_set = set([t.lower().strip() for t in core_traits])
    obs_set = set([t.lower().strip() for t in observable_traits])

    overlap = len(core_set & obs_set)
    total = max(len(core_set), len(obs_set))

    if total == 0:
        return True  # No traits defined

    similarity = overlap / total
    return similarity > 0.7  # >70% similarity = no real contradiction


def detect_trait_polarity(traits: List[str]) -> Optional[str]:
    """
    Detect if contradictory traits exist within character.

    Looks for opposing trait pairs that create internal tension.

    Args:
        traits: List of character traits

    Returns:
        Description of contradiction if found, None otherwise
    """
    # Known opposition pairs
    oppositions = [
        (["ambitious", "driven", "determined", "goal-oriented"], ["guilty", "self-doubting", "ashamed", "insecure"]),
        (["compassionate", "kind", "empathetic", "caring"], ["cruel", "ruthless", "cold", "harsh"]),
        (["loyal", "faithful", "devoted", "dedicated"], ["betraying", "traitorous", "deceitful", "disloyal"]),
        (["charming", "charismatic", "likable", "friendly"], ["thief", "criminal", "dishonest", "manipulative"]),
        (["lonely", "isolated", "alone", "solitary"], ["smiling", "cheerful", "upbeat", "outgoing"]),
        (["brave", "courageous", "bold", "fearless"], ["fearful", "cowardly", "hesitant", "anxious"]),
        (["arrogant", "prideful", "confident"], ["insecure", "self-loathing", "doubtful"]),
        (["generous", "giving", "selfless"], ["selfish", "greedy", "self-serving"]),
        (["honest", "truthful", "sincere"], ["lying", "deceptive", "secretive"]),
        (["patient", "calm", "composed"], ["impulsive", "reckless", "hasty"]),
    ]

    traits_lower = [t.lower().strip() for t in traits]

    for group1, group2 in oppositions:
        has_group1 = any(any(t1 in trait for t1 in group1) for trait in traits_lower)
        has_group2 = any(any(t2 in trait for t2 in group2) for trait in traits_lower)

        if has_group1 and has_group2:
            # Found contradiction!
            t1_found = next((trait for trait in traits_lower if any(t1 in trait for t1 in group1)), group1[0])
            t2_found = next((trait for trait in traits_lower if any(t2 in trait for t2 in group2)), group2[0])
            return f"{t1_found} yet {t2_found}"

    return None


def analyze_protagonist_dimensionality(
    protagonist_data: Dict[str, Any],
    supporting_cast_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Check if protagonist is most dimensional character.

    Analyzes supporting cast to ensure they serve protagonist's complexity.

    Args:
        protagonist_data: Protagonist character data
        supporting_cast_data: List of supporting character data

    Returns:
        Dictionary with:
            - is_most_dimensional: Boolean
            - flags: List of issues detected
    """
    results = {
        "is_most_dimensional": True,
        "flags": []
    }

    # Get protagonist depth score
    protagonist_analysis = analyze_character_depth(protagonist_data)
    protagonist_score = protagonist_analysis["depth_score"]

    # Check each supporting character
    for support_char in supporting_cast_data:
        support_analysis = analyze_character_depth(support_char)
        support_score = support_analysis["depth_score"]

        if support_score > protagonist_score:
            results["is_most_dimensional"] = False
            results["flags"].append({
                "severity": "CRITICAL",
                "type": "PROTAGONIST_LESS_DIMENSIONAL",
                "message": f"Protagonist is less dimensional than Supporting Character '{support_char.get('name')}'.",
                "protagonist_score": protagonist_score,
                "support_score": support_score,
                "recommendation": "Protagonist MUST be the most dimensional character in the cast. Add more contradictions to protagonist."
            })

        # Check if supporting character reveals protagonist dimension
        reveals_dimension = support_char.get("reveals_protagonist_dimension", "")
        if not reveals_dimension:
            results["flags"].append({
                "severity": "MEDIUM",
                "type": "REDUNDANT_SUPPORTING_CHARACTER",
                "message": f"Character '{support_char.get('name')}' does not delineate protagonist's complexity.",
                "recommendation": "Each secondary character should reveal a specific contradictory side of protagonist (e.g., cruel side, compassionate side)"
            })

    return results


def get_depth_color(depth_score: int) -> str:
    """Get color code for depth score visualization.

    Args:
        depth_score: Character depth score (0-100)

    Returns:
        Color name ('red', 'yellow', or 'green')
    """
    if depth_score < 50:
        return 'red'  # Flat character
    elif depth_score < 80:
        return 'yellow'  # Developing
    else:
        return 'green'  # Dimensional
