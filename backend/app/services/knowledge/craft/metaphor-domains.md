# Metaphor Discipline - Domain Consistency

## Core Principle

**Metaphor Domain:** A consistent conceptual framework for comparisons throughout a work.

**Why it matters:**
- Random metaphors create tonal chaos
- Consistent domains create subliminal thematic unity
- Readers feel domain consistency even if they can't articulate it

## Explants Metaphor Domains

### Primary Domain: Military/Combat
**Why:** Mickey is ex-military, thinks in tactical terms

**Examples:**
- "She flanked the conversation"
- "Retreat wasn't an option"
- "He deployed a smile"
- "The room felt like contested territory"

**Usage:** Can be used liberally, especially for Mickey POV

### Secondary Domain: Mechanism/Machine
**Why:** Sci-fi setting, technology-heavy world

**Examples:**
- "His thoughts clicked into place"
- "The conversation ground to a halt"
- "She recalibrated her approach"

**Usage:** Moderate use, especially for technical situations

### Tertiary Domain: Navigation/Journey
**Why:** Story about finding one's place, literal travel

**Examples:**
- "She charted a new course"
- "The conversation veered off track"
- "He was adrift"

**Usage:** Sparingly, for thematic resonance

## Forbidden Domains

### ❌ Nature/Weather (unless literal)
**Why:** Doesn't fit sci-fi setting or Mickey's character
- Don't: "Her anger bloomed like a flower"
- Don't: "Storm clouds gathered in his mind"

### ❌ Medieval/Fantasy
**Why:** Wrong genre
- Don't: "She wielded her words like a sword"
- Don't: "He donned a mask of civility"

### ❌ Domestic/Cooking
**Why:** Mickey's background doesn't support it
- Don't: "She stirred up trouble"
- Don't: "The plan was half-baked"

## Metaphor Discipline Scoring

**20 points maximum:**
- Domain consistency: 12 points
- Metaphor earning: 5 points (does it add meaning?)
- Freshness: 3 points (avoid clichés)

**Deductions:**
- Random domain violation: -2 points
- Forbidden domain use: -3 points
- Clichéd metaphor: -1 point
- Unearned comparison: -1 point

## Earning Your Metaphors

Not every comparison needs to be metaphorical.

**Unearned:**
"The door was like a portal to another world"
- Why: It's literally a door, overdramatic

**Earned:**
"The airlock hissed—atmosphere meeting void, her old life meeting the new"
- Why: The comparison adds thematic meaning

## Testing Metaphors

### Test 1: Domain Check
Does this metaphor fit our established domains?
- Military/Combat: Yes
- Mechanism/Machine: Yes
- Navigation/Journey: Use sparingly
- Other: Justify or cut

### Test 2: Earned Status
Does this metaphor add meaning beyond literal description?
- If no: Use literal description
- If yes: Keep it

### Test 3: Freshness
Have I seen this comparison before?
- If yes: Cut or remake
- If no: Does it work?

## Examples Analysis

### ❌ Bad:
"His anger was a volcano"
- Domain: Nature (forbidden)
- Earned: No (cliché)
- Freshness: Terrible

### ✅ Good:
"His anger had a blast radius"
- Domain: Military (primary)
- Earned: Yes (implies danger to others)
- Freshness: Fresh take on common idea

### ❌ Bad:
"She felt like a caged bird"
- Domain: Nature (forbidden)
- Earned: No (overdone)
- Character: Wrong (Mickey doesn't think this way)

### ✅ Good:
"She felt pinned down, waiting for covering fire"
- Domain: Military (primary)
- Earned: Yes (implies tactical thinking)
- Character: Perfect for Mickey

## Implementation Notes

The SceneAnalyzerAgent checks for:
1. Domain consistency across all metaphors/similes
2. Cliché detection (common phrases)
3. Character-appropriate comparisons

See `factory/agents/explants/scene_analyzer.py` for implementation details.
