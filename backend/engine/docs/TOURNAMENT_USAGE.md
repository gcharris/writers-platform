# Tournament System Usage Guide

Complete guide for using the Multi-Agent Scene Tournament System for The Explants novel.

---

## Quick Start

### 1. Setup API Keys

Create `framework/config/credentials.json`:

```bash
cd /home/user/The-Explants/framework/config
cp credentials.example.json credentials.json
# Edit credentials.json with your API keys
```

**Minimum required**: Anthropic API key (for Claude Sonnet 4.5)

**Recommended**: Anthropic + OpenAI + Google (for full 5-agent tournament)

### 2. Run Your First Tournament

```bash
cd /home/user/The-Explants

python3 framework/orchestration/tournament.py \
  --scene "Mickey discovers evidence of Vance's manipulation" \
  --chapter 2.4.3 \
  --context-requirements "Mickey Bardot" "Vance" "betrayal" \
  --output output/test-tournament.json \
  --synthesize
```

**Expected cost**: ~$0.50-1.50 per tournament (5 agents)

### 3. Review Results

```bash
# View JSON results
cat output/test-tournament.json | jq '.summary'

# Read hybrid scene
cat output/test-hybrid.md

# Read summary
cat output/test-summary.md
```

---

## Command Reference

### Single Scene Tournament

```bash
python3 framework/orchestration/tournament.py \
  --scene "SCENE_DESCRIPTION" \
  --chapter CHAPTER_ID \
  --context-requirements CONTEXT_ITEMS \
  --output OUTPUT_PATH \
  [OPTIONS]
```

#### Required Arguments

- `--scene`: Scene outline/description (string)
- `--output`: Output file path for JSON results

#### Optional Arguments

- `--chapter`: Chapter identifier (e.g., "2.3.6")
- `--context-requirements`: Space-separated list of context items
  - Capitalized items treated as characters: "Mickey Bardot" "Vance"
  - Lowercase items treated as worldbuilding: "bi-location" "consciousness war"
- `--previous-scenes`: Space-separated list of previous scene IDs
- `--instructions`: Custom writing instructions (string)
- `--agents`: Specific agents to use (space-separated)
  - Choices: `claude-sonnet-4-5`, `gemini-1-5-pro`, `gpt-4o`, `grok-2`, `claude-haiku`
  - Default: all 5 agents
- `--synthesize`: Flag to synthesize hybrid scene (default: no synthesis)
- `--synthesis-threshold`: Minimum score for hybrid inclusion (default: 7.0)
- `--max-tokens`: Maximum tokens per generation (default: 4000)
- `--project`: Project name (default: "The-Explants")

#### Examples

**Minimal tournament** (Anthropic key only, no synthesis):
```bash
python3 framework/orchestration/tournament.py \
  --scene "Mickey meditates in the dojo while monitoring Shanghai facility" \
  --output output/2.3.1-tournament.json
```

**Full tournament with synthesis**:
```bash
python3 framework/orchestration/tournament.py \
  --scene "Noni detects corruption through the Line, confronts Mickey" \
  --chapter 2.4.2 \
  --context-requirements "Mickey Bardot" "Noni" "The Line" "The Shared Vein" \
  --previous-scenes "2.4.1" \
  --instructions "Focus on Noni's active interpretation via morphic resonance" \
  --output output/2.4.2-tournament.json \
  --synthesize \
  --synthesis-threshold 7.5
```

**Budget tournament** (2 agents only):
```bash
python3 framework/orchestration/tournament.py \
  --scene "Brief transition scene" \
  --agents claude-haiku gemini-1-5-pro \
  --output output/2.5.1-tournament.json \
  --synthesize \
  --max-tokens 2000
```

---

### Batch Processing

```bash
python3 framework/orchestration/batch-tournament.py \
  --input INPUT_JSON \
  --output OUTPUT_DIR \
  [OPTIONS]
```

#### Required Arguments

- `--input`: Path to input JSON file with scene configurations
- `--output`: Output directory for all tournament results

#### Optional Arguments

- `--parallel`: Number of scenes to process in parallel (default: 1)
  - **Caution**: Parallel > 1 may hit rate limits
  - Recommended: 1-2 for safety
- `--synthesize`: Flag to synthesize hybrid scenes
- `--synthesis-threshold`: Minimum score for hybrid inclusion (default: 7.0)
- `--agents`: Specific agents to use
- `--max-tokens`: Maximum tokens per generation (default: 4000)
- `--project`: Project name (default: "The-Explants")

#### Input JSON Format

```json
{
  "chapter": "2.4",
  "scenes": [
    {
      "scene_id": "2.4.1",
      "title": "The Seduction Deepens",
      "outline": "Vance makes his offer explicit. Mickey's resistance weakens as optimization mathematics seduce him with their elegance.",
      "context_requirements": [
        "Mickey Bardot",
        "Vance",
        "consciousness war",
        "bi-location strain"
      ],
      "previous_scenes": ["2.3.3", "2.3.4", "2.3.5"],
      "custom_instructions": "Show Mickey's internal conflict through physical strain symptoms"
    },
    {
      "scene_id": "2.4.2",
      "title": "Noni's Warning",
      "outline": "Through the Line, Noni detects corruption in Mickey's patterns.",
      "context_requirements": [
        "Mickey Bardot",
        "Noni",
        "The Line",
        "The Tether",
        "morphic resonance"
      ],
      "previous_scenes": ["2.4.1"]
    }
  ]
}
```

#### Examples

**Sequential processing** (safest):
```bash
python3 framework/orchestration/batch-tournament.py \
  --input input/chapter-2-4-scenes.json \
  --output output/chapter-2-4/ \
  --synthesize
```

**Parallel processing** (faster, more risk):
```bash
python3 framework/orchestration/batch-tournament.py \
  --input input/chapter-2-4-scenes.json \
  --output output/chapter-2-4/ \
  --parallel 2 \
  --synthesize
```

---

### Agent Analytics

```bash
python3 framework/orchestration/agent-analytics.py \
  --input "GLOB_PATTERN" \
  --output OUTPUT_JSON
```

#### Required Arguments

- `--input`: Glob pattern for tournament JSON files
  - Example: `"output/*-tournament.json"`
  - Example: `"output/chapter-2-*/*-tournament.json"`
- `--output`: Output path for analytics JSON

#### Examples

**Analyze all tournaments**:
```bash
python3 framework/orchestration/agent-analytics.py \
  --input "output/*-tournament.json" \
  --output output/agent-analytics.json
```

**Analyze specific chapter**:
```bash
python3 framework/orchestration/agent-analytics.py \
  --input "output/chapter-2-4/*-tournament.json" \
  --output output/chapter-2-4-analytics.json
```

**Review analytics**:
```bash
cat output/agent-analytics.json | jq '.recommendations.overall_recommendations'
```

---

## Workflows

### Workflow 1: Single Scene Development

**Use case**: Developing one critical scene with high quality requirements

```bash
# 1. Run tournament with synthesis
python3 framework/orchestration/tournament.py \
  --scene "Your scene outline" \
  --chapter 2.X.X \
  --context-requirements "Characters" "themes" \
  --output output/scene-tournament.json \
  --synthesize \
  --synthesis-threshold 7.5

# 2. Review results
cat output/scene-summary.md

# 3. Read hybrid scene
cat output/scene-hybrid.md

# 4. If unsatisfied, try different threshold
python3 framework/orchestration/tournament.py \
  --scene "Your scene outline" \
  --output output/scene-tournament-v2.json \
  --synthesize \
  --synthesis-threshold 6.5
```

### Workflow 2: Chapter Batch Processing

**Use case**: Generate all scenes for a chapter

```bash
# 1. Create input file
cat > input/chapter-2-5-scenes.json << 'EOF'
{
  "chapter": "2.5",
  "scenes": [
    {
      "scene_id": "2.5.1",
      "outline": "...",
      "context_requirements": [...]
    },
    ...
  ]
}
EOF

# 2. Run batch processing
python3 framework/orchestration/batch-tournament.py \
  --input input/chapter-2-5-scenes.json \
  --output output/chapter-2-5/ \
  --synthesize

# 3. Review batch summary
cat output/chapter-2-5/batch-summary.json | jq '.cost_summary'

# 4. Review individual hybrid scenes
ls output/chapter-2-5/*-hybrid.md
```

### Workflow 3: Cost-Optimized Development

**Use case**: Tight budget, need to optimize agent selection

```bash
# 1. Run initial small batch with all agents
python3 framework/orchestration/batch-tournament.py \
  --input input/test-scenes.json \
  --output output/test-batch/ \
  --synthesize

# 2. Analyze agent performance
python3 framework/orchestration/agent-analytics.py \
  --input "output/test-batch/*-tournament.json" \
  --output output/test-analytics.json

# 3. Review recommendations
cat output/test-analytics.json | jq '.recommendations.overall_recommendations'

# 4. Run full batch with optimal agents only
python3 framework/orchestration/batch-tournament.py \
  --input input/full-chapter.json \
  --output output/full-chapter/ \
  --agents claude-sonnet-4-5 gemini-1-5-pro gpt-4o \
  --synthesize
```

### Workflow 4: Iterative Quality Improvement

**Use case**: Continuously improving scene quality

```bash
# 1. Initial tournament
python3 framework/orchestration/tournament.py \
  --scene "Scene outline" \
  --output output/v1-tournament.json \
  --synthesize

# 2. Review scores
cat output/v1-tournament.json | jq '.variations[] | {agent: .agent, total: .scores.total}'

# 3. Identify issues
cat output/v1-tournament.json | jq '.variations[] | .validation.bi_location.issues'

# 4. Refine prompt with custom instructions
python3 framework/orchestration/tournament.py \
  --scene "Scene outline" \
  --instructions "Emphasize physical bi-location strain. Use The Line/Tether/Shared Vein. Show Noni's active interpretation." \
  --output output/v2-tournament.json \
  --synthesize \
  --synthesis-threshold 7.5

# 5. Compare results
diff <(cat output/v1-hybrid.md) <(cat output/v2-hybrid.md)
```

---

## Output Files

### Tournament JSON

**File**: `{output-path}.json`

**Structure**:
```json
{
  "tournament_metadata": {
    "scene_outline": "...",
    "chapter": "2.4.3",
    "timestamp": "2025-11-12T...",
    "elapsed_time_seconds": 45.2
  },
  "variations": [
    {
      "agent": "claude-sonnet-4-5",
      "content": "...",
      "word_count": 543,
      "scores": {
        "voice_authenticity": 8.5,
        "character_consistency": 9.0,
        ...
        "total": 58.5
      },
      "validation": {
        "bi_location": {
          "forbidden_jargon_found": [],
          "correct_terms_used": ["The Line", "The Tether"],
          "issues": [],
          "strengths": [...]
        }
      }
    }
  ],
  "critiques": {...},
  "hybrid_synthesis": {
    "content": "...",
    "scores": {...},
    "sources": ["claude-sonnet-4-5", "gemini-1-5-pro"]
  },
  "summary": {
    "total_cost": 0.8734,
    "highest_scoring": "claude-sonnet-4-5",
    "hybrid_score": 62.0
  }
}
```

### Hybrid Markdown

**File**: `{output-path}-hybrid.md`

**Format**:
```markdown
# Hybrid Scene: Scene Title

**Score:** 62.0/70
**Word Count:** 567
**Sources:** claude-sonnet-4-5, gemini-1-5-pro, gpt-4o

---

[Hybrid scene content]
```

### Summary Markdown

**File**: `{output-path}-summary.md`

**Format**:
```markdown
# Tournament Summary: Scene Title

**Project:** The-Explants
**Chapter:** 2.4.3
**Date:** 2025-11-12
**Duration:** 45.2s
**Total Cost:** $0.8734

## Score Rankings

Rank   Agent                Total      Voice    Char     World    ...
------------------------------------------------------------------
1      claude-sonnet-4-5     58.5      8.5      9.0      8.0     ...
2      gemini-1-5-pro        56.0      7.5      8.5      8.5     ...
...

## Hybrid Results

**Total Score:** 62.0/70
**Word Count:** 567
**Sources:** claude-sonnet-4-5, gemini-1-5-pro, gpt-4o
```

### Batch Summary JSON

**File**: `{output-dir}/batch-summary.json`

**Structure**:
```json
{
  "batch_metadata": {
    "chapter": "2.4",
    "total_scenes": 5,
    "processed": 5,
    "failed": 0
  },
  "cost_summary": {
    "total_cost": 6.2345,
    "average_cost_per_scene": 1.2469
  },
  "quality_summary": {
    "average_highest_score": 57.8,
    "average_hybrid_score": 60.2
  }
}
```

### Agent Analytics JSON

**File**: `{output-path}.json`

**Key Sections**:
- `agent_profiles`: Performance stats for each agent
- `recommendations`: Scene-type recommendations, optimal lineup
- `summary`: Overview statistics

---

## Best Practices

### Scene Outline Quality

**Good outlines**:
- ✅ Clear action/conflict: "Mickey confronts Vance about betrayal"
- ✅ Emotional stakes: "Noni's warning forces Mickey to choose"
- ✅ Specific details: "Via The Line, Noni detects corruption patterns"

**Poor outlines**:
- ❌ Too vague: "Something happens"
- ❌ Too detailed: [Full scene already written]
- ❌ Missing stakes: "Mickey walks to the dojo"

### Context Requirements

**Effective context**:
- Characters involved: "Mickey Bardot", "Noni", "Vance"
- Key themes: "consciousness war", "bi-location strain"
- Mechanics: "The Line", "The Tether", "morphic resonance"

**Avoid**:
- Generic terms: "AI", "technology"
- Spoilers: Don't include outcome in context
- Redundancy: Scene outline already has this

### Custom Instructions

**When to use**:
- Specific voice emphasis needed
- Particular mechanics focus required
- Character development goals

**Examples**:
- "Emphasize physical bi-location strain symptoms"
- "Show Noni's active morphic resonance interpretation"
- "Use con artist/gambling metaphors for Mickey's perspective"
- "Avoid any technical exposition"

### Synthesis Threshold Tuning

**Threshold Guidelines**:
- `6.0`: Include most variations (more diverse hybrid)
- `7.0`: **(Default)** Balanced quality filter
- `7.5`: High quality only (fewer sources)
- `8.0`: Exceptional quality (may exclude all)

**Adjust based on**:
- Agent performance (check analytics)
- Scene complexity (lower threshold for complex scenes)
- Voice criticality (higher threshold for voice-critical passages)

---

## Troubleshooting

### Low Scores Across All Agents

**Symptoms**: All variations scoring < 6.0

**Likely causes**:
- Scene outline too vague
- Missing critical context
- Agents unfamiliar with voice requirements

**Solutions**:
1. Add more specific context requirements
2. Include custom instructions emphasizing voice
3. Reference previous high-scoring scenes in context
4. Provide character personality details

### Forbidden Jargon Appearing

**Symptoms**: Variations flagged for "quantum link", "bi-location mode"

**Likely causes**:
- Insufficient voice instruction
- Agents falling back to generic sci-fi language

**Solutions**:
1. Add to custom instructions: "Use Mickey's terms: The Line, The Tether, The Shared Vein. NEVER use 'quantum link' or 'bi-location mode'."
2. Include example passages with correct terminology
3. Lower synthesis threshold to only use cleanest variations

### Hybrid Synthesis Fails

**Symptoms**: No hybrid generated, or hybrid scores lower than best variation

**Likely causes**:
- Threshold too high (no variations qualify)
- Synthesis prompt unclear
- Conflicting elements from variations

**Solutions**:
1. Lower `--synthesis-threshold`
2. Check critique output for guidance
3. Try synthesizing from top 2 agents only: `--agents claude-sonnet-4-5 gemini-1-5-pro`

### High Costs

**Symptoms**: Single tournament costing > $2

**Likely causes**:
- Very long context (previous chapters)
- High max_tokens setting
- Multiple retry attempts

**Solutions**:
1. Reduce `--max-tokens` (try 3000)
2. Limit agents: `--agents claude-sonnet-4-5 gemini-1-5-pro claude-haiku`
3. Use analytics to identify most cost-efficient agents
4. Process scenes sequentially in batches (better error handling)

---

## Advanced Usage

### Environment Variables

Set API keys via environment instead of credentials.json:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export XAI_API_KEY="..."

python3 framework/orchestration/tournament.py ...
```

### Custom Scoring Weights

**(Future feature)** Adjust relative importance of criteria:

```bash
# Hypothetical
python3 framework/orchestration/tournament.py \
  --scene "..." \
  --score-weights voice:2.0 dialogue:1.5 pacing:0.5 \
  --output ...
```

### Integration with Git

Manual workflow for committing winning scenes:

```bash
# 1. Run tournament
python3 framework/orchestration/tournament.py ... --output output/scene.json

# 2. Review hybrid
cat output/scene-hybrid.md

# 3. If acceptable, copy to manuscript
cp output/scene-hybrid.md "The Explants Series/Volume 2/Chapter 2/Scene 2.4.3.md"

# 4. Commit
git add "The Explants Series/Volume 2/Chapter 2/Scene 2.4.3.md"
git commit -m "Add scene 2.4.3 from tournament (hybrid, score: 62.0/70)"
```

---

## FAQ

**Q: Which agents are required?**
A: Minimum: Anthropic (Claude). Recommended: Anthropic + OpenAI + Google for full 5-agent tournament.

**Q: How long does a tournament take?**
A: 30-60 seconds for single scene with 5 agents (parallel generation).

**Q: Can I run tournaments without Google Cloud Storage?**
A: Yes. System uses minimal context fallback if storage unavailable.

**Q: Should I always synthesize hybrids?**
A: Not always. Sometimes highest-scoring variation is best as-is. Compare hybrid score to highest variation score.

**Q: How do I improve voice authenticity scores?**
A: Add custom instructions emphasizing Mickey's voice, provide example passages, use "The Line/Tether/Shared Vein" in context.

**Q: Can I use different Claude models?**
A: Yes. Modify `AGENT_CONFIGS` in `tournament.py` or use `--agents` with custom model names (requires code changes).

**Q: What if I hit rate limits?**
A: Reduce `--parallel` in batch processing, add delays between tournaments, or run fewer agents per tournament.

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/gcharris/The-Explants/issues
- Review documentation: `framework/docs/TOURNAMENT_SYSTEM.md`
- Check analytics for performance insights

---

**Version**: 1.0 (November 2025)
**Maintained by**: Claude Code Cloud Agent
