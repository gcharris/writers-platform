# Explants Anti-Patterns

This document defines anti-patterns that violate Explants writing craft standards.

## Zero-Tolerance Anti-Patterns (-2 points each)

### 1. First-Person Italics
**Pattern:** Using italics for first-person internal thoughts
**Example:** *I need to get out of here*, she thought.
**Why Forbidden:** Creates observer-consciousness split. Violates cognitive fusion principle.
**Fix:** Use regular text for consciousness: She needed to get out of there.

### 2. "With [Precision]" Construction
**Pattern:** Using "with [emotion/quality]" to describe actions
**Example:** "She spoke with anger" or "He moved with caution"
**Why Forbidden:** Tells emotion rather than showing it. Creates distance.
**Fix:** Show the emotion through concrete details: "Her voice sharpened" or "He stepped softly"

### 3. Computer Psychology
**Pattern:** Mechanistic emotional descriptions
**Examples:**
- "Anger flared"
- "Fear gripped her"
- "Relief washed over him"
**Why Forbidden:** Emotions don't work like switches or external forces
**Fix:** Show physical manifestations and thoughts that reveal emotional state

### 4. Emotional Algebra
**Pattern:** Using mathematical operators for emotions
**Example:** "Her fear + confusion = paralysis"
**Why Forbidden:** Emotions blend, don't add
**Fix:** Show the blended emotional state through concrete experience

## Formulaic Anti-Patterns (-1 point each)

### 5. Weak Similes
**Pattern:** Similes that don't earn their place
**Example:** "Fast as lightning" or "Cold as ice"
**Why Problematic:** Generic, don't add specific meaning
**Fix:** Use fresh comparisons or concrete description

### 6. Adverb Reliance
**Pattern:** Using adverbs as shortcuts
**Example:** "She said angrily" or "He walked quickly"
**Why Problematic:** Tells rather than shows
**Fix:** Choose stronger verbs or show through action

### 7. Expository Dialogue
**Pattern:** Characters explaining things unnaturally
**Example:** "As you know, Bob, our company has been struggling..."
**Why Problematic:** People don't talk like this
**Fix:** Show information through action or natural conversation

### 8. Filter Words
**Pattern:** Unnecessary perception filters
**Examples:**
- "She saw..."
- "He heard..."
- "She felt..."
- "He noticed..."
**Why Problematic:** Creates distance in close POV
**Fix:** Present the perception directly

## Detection Priority

1. **Zero-Tolerance patterns** must be caught first - these are craft violations
2. **Formulaic patterns** should be flagged but won't disqualify a scene
3. Context matters - some patterns acceptable in Phase 1 (learning) but not Phase 2/3

## Reference Implementation

The SceneAnalyzerAgent uses regex patterns to detect these anti-patterns automatically.
See `factory/agents/explants/scene_analyzer.py` for the implementation.
