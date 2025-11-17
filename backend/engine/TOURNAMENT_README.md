# Multi-Agent Scene Tournament System

**Version**: 1.0 (November 2025)
**Project**: The Explants Novel Trilogy

---

## Overview

The Multi-Agent Scene Tournament System automates the proven scene generation workflow for The Explants trilogy. It orchestrates multiple AI agents to generate, score, critique, and synthesize high-quality scenes that maintain Enhanced Mickey Bardot's voice authenticity.

**Key Achievement**: Automates the manual 5-agent variation → critique → synthesis workflow that was successfully used for Volume 2, Chapter 3 scenes.

---

## Quick Start

### 1. Configure API Keys

```bash
cd framework/config
cp credentials.example.json credentials.json
# Edit credentials.json with your API keys
```

**Minimum**: Anthropic API key (Claude Sonnet 4.5)

### 2. Run First Tournament

```bash
cd /home/user/The-Explants

python3 framework/orchestration/tournament.py \
  --scene "Mickey discovers evidence of Vance's manipulation" \
  --output output/test-tournament.json \
  --synthesize
```

**Cost**: ~$0.50-1.50 per tournament (5 agents)

### 3. Review Results

```bash
cat output/test-summary.md        # Score summary
cat output/test-hybrid.md          # Synthesized scene
cat output/test-tournament.json    # Complete results
```

---

## What's Included

### Phase 1: Core Tournament (COMPLETED)
- ✅ Multi-agent scene generation (5 agents in parallel)
- ✅ Hybrid scoring system (rule-based + LLM)
- ✅ Cross-agent critique
- ✅ Hybrid synthesis from best elements
- ✅ CLI interface with comprehensive options

### Phase 2: Batch Processing (COMPLETED)
- ✅ Process multiple scenes with rate limiting
- ✅ Batch summary and cost tracking
- ✅ Parallel or sequential processing
- ✅ JSON input format for chapter outlines

### Phase 3: Agent Analytics (COMPLETED)
- ✅ Identify agent strengths and weaknesses
- ✅ Scene-type recommendations
- ✅ Cost efficiency analysis
- ✅ Optimal tournament lineup generation

---

## System Components

```
framework/
├── orchestration/
│   ├── tournament.py           # Core single-scene tournament
│   ├── batch-tournament.py     # Batch processing system
│   └── agent-analytics.py      # Performance analysis
│
├── utils/
│   ├── validation.py           # Rule-based validation
│   └── scoring.py              # Hybrid scoring system
│
└── docs/
    ├── TOURNAMENT_SYSTEM.md    # Architecture overview
    └── TOURNAMENT_USAGE.md     # Complete usage guide
```

---

## Core Features

### 1. Multi-Agent Generation
Generates 5 variations in parallel:
- **Claude Sonnet 4.5**: Voice authenticity, emotional impact
- **Gemini 1.5 Pro**: Philosophical arguments, structure
- **GPT-4o**: Dialogue, character consistency
- **Grok-2**: Worldbuilding integration
- **Claude Haiku**: Budget option

### 2. Hybrid Scoring (7 Criteria)
- Voice authenticity (0-10)
- Character consistency (0-10)
- Worldbuilding integration (0-10)
- Pacing (0-10)
- Dialogue naturalness (0-10)
- Emotional impact (0-10)
- Consciousness war argument (0-10)

**Total**: 70 points

### 3. Voice Validation
**Forbidden jargon detection**:
- ❌ "quantum link"
- ❌ "bi-location mode"
- ❌ "split consciousness"

**Required terms**:
- ✅ "The Line"
- ✅ "The Tether"
- ✅ "The Shared Vein"

### 4. Hybrid Synthesis
- Filters variations by score threshold (default: 7.0/10)
- Extracts best structural chassis
- Combines best philosophical moments
- Applies Enhanced Mickey voice

---

## Usage Examples

### Single Scene

```bash
python3 framework/orchestration/tournament.py \
  --scene "Noni detects corruption through The Line" \
  --chapter 2.4.2 \
  --context-requirements "Mickey" "Noni" "The Line" "morphic resonance" \
  --output output/2.4.2-tournament.json \
  --synthesize \
  --synthesis-threshold 7.5
```

### Batch Chapter

```bash
# Create input file
cat > input/chapter-2-4.json << 'EOF'
{
  "chapter": "2.4",
  "scenes": [
    {
      "scene_id": "2.4.1",
      "outline": "Vance makes his offer explicit...",
      "context_requirements": ["Mickey", "Vance"]
    }
  ]
}
EOF

# Process batch
python3 framework/orchestration/batch-tournament.py \
  --input input/chapter-2-4.json \
  --output output/chapter-2-4/ \
  --synthesize
```

### Agent Analytics

```bash
python3 framework/orchestration/agent-analytics.py \
  --input "output/*-tournament.json" \
  --output output/agent-analytics.json
```

---

## Output Files

### Tournament Results (`*-tournament.json`)
Complete JSON with:
- All 5 variations + scores
- Validation results
- Critique analysis
- Hybrid synthesis
- Cost tracking

### Hybrid Scene (`*-hybrid.md`)
Synthesized scene combining best elements

### Summary (`*-summary.md`)
Human-readable score rankings and analysis

### Batch Summary (`batch-summary.json`)
Batch processing statistics and cost breakdown

---

## Quality Assurance

### Validation Gates
- ✅ No forbidden jargon
- ✅ Mickey's terms used correctly
- ✅ Bi-location shown through strain
- ✅ Noni's morphic resonance active
- ✅ Voice authenticity score ≥7.0

### Score Thresholds
- **Acceptable**: 5.0+ per criterion
- **Synthesis threshold**: 7.0+ (configurable)
- **High quality**: 8.0+
- **Exceptional**: 9.0+

---

## Cost Tracking

### Single Tournament
- Generation: ~$0.30-0.60
- Scoring: ~$0.10-0.20
- Critique: ~$0.05-0.10
- Synthesis: ~$0.10-0.20
- **Total**: ~$0.55-1.10

### Batch (10 scenes)
- ~$7-10 total

### Full Chapter (30 scenes)
- ~$20-30 total

---

## Documentation

### Complete Guides
- **[TOURNAMENT_SYSTEM.md](docs/TOURNAMENT_SYSTEM.md)**: Architecture, components, data flow
- **[TOURNAMENT_USAGE.md](docs/TOURNAMENT_USAGE.MD)**: Command reference, workflows, examples

### Example Files
- **[chapter-2-4-test-scenes.json](examples/chapter-2-4-test-scenes.json)**: Sample batch input

### Tests
- **[test_validation.py](tests/test_validation.py)**: Validation system tests

---

## Key Voice Requirements

### Show Bi-Location Through:
- Physical strain (temples pulsing, shadow splitting)
- Sensory conflict (competing data streams)
- Exhaustion (sleep debt, phantom fatigue)

### NOT Through:
- Technical announcements
- Academic language
- Mode switching

### Noni's Role:
- **Active interpreter** with morphic resonance
- **Reads patterns**, detects contamination
- **NOT** passive receiver

---

## Agent Strengths (From Analytics)

| Agent | Best For | Cost Efficiency |
|-------|----------|----------------|
| Claude Sonnet 4.5 | Voice, emotion, Mickey POV | Medium |
| Gemini 1.5 Pro | Philosophy, structure | High |
| GPT-4o | Dialogue, characters | Medium |
| Grok-2 | Worldbuilding | Medium |
| Claude Haiku | Budget scenes | Very High |

---

## Testing

### Run Validation Tests
```bash
python3 framework/tests/test_validation.py
```

### Test Tournament (Low Cost)
```bash
python3 framework/orchestration/tournament.py \
  --scene "Test scene" \
  --agents claude-sonnet-4-5 \
  --output output/test.json \
  --max-tokens 1000
```

**Cost**: ~$0.10-0.15

---

## Troubleshooting

### Issue: No API key found
**Solution**: Create `framework/config/credentials.json` or set environment variables

### Issue: Low scores across all agents
**Solution**: Add more specific context requirements, custom instructions

### Issue: Forbidden jargon appearing
**Solution**: Add to custom instructions: "Use The Line/Tether/Shared Vein. NEVER use 'quantum link'."

### Issue: High costs
**Solution**: Reduce `--max-tokens`, use fewer agents, run analytics first

---

## Best Practices

### Development
1. Test with single scene first
2. Use `claude-haiku` for cheap testing
3. Start with sequential batch processing
4. Monitor costs during development

### Production
1. Set synthesis threshold appropriately
2. Review analytics before full batch runs
3. Use optimal agent lineup
4. Save all tournament results

### Cost Management
1. Use `--agents` to limit agents
2. Set reasonable `--max-tokens`
3. Run analytics to identify efficient agents
4. Consider scene complexity

---

## Roadmap

### Completed (v1.0)
- ✅ Phase 1: Core tournament system
- ✅ Phase 2: Batch processing
- ✅ Phase 3: Agent analytics
- ✅ Hybrid scoring (rule-based + LLM)
- ✅ Comprehensive documentation

### Future
- 🔲 Web dashboard
- 🔲 NotebookLM integration
- 🔲 Git auto-commit
- 🔲 Custom scoring weights
- 🔲 A/B testing strategies

---

## Credits

**Built by**: Claude Code Cloud Agent (November 2025)
**For**: Mickey Gemini Harris & The Explants Project
**Voice Authority**: Enhanced Mickey Bardot character system
**Budget**: $300-425 of $996 credit (estimated)

---

## Support

- **Documentation**: `framework/docs/`
- **GitHub Issues**: https://github.com/gcharris/The-Explants/issues
- **Examples**: `framework/examples/`

---

**Quality over speed. Voice authenticity is non-negotiable.**

Test incrementally. Analyze agent performance. Use credit wisely.

May your scenes score 9.0+ on voice authenticity! 🎯
