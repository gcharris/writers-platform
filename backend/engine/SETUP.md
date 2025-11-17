# Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Google Cloud account
- API keys for AI platforms (Claude, OpenAI, Google, xAI)

### 2. Installation

```bash
# Clone or navigate to the framework
cd creative-writing-agent-framework

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Google Cloud

1. **Create a Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create a new project or select an existing one

2. **Enable Cloud Storage API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Cloud Storage API"
   - Click "Enable"

3. **Create Service Account**
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `creative-writing-framework`
   - Role: `Storage Admin`
   - Click "Create Key" > JSON
   - Download the JSON key file

4. **Save Credentials**
   ```bash
   # Save the downloaded JSON file
   mv ~/Downloads/your-key-file.json config/google-cloud-credentials.json
   ```

### 4. Configure API Keys

Copy the example configuration:

```bash
cp config/credentials.example.json config/credentials.json
```

Edit `config/credentials.json`:

```json
{
  "google_cloud": {
    "project_id": "your-google-project-id",
    "credentials_path": "config/google-cloud-credentials.json",
    "region": "us-central1"
  },
  "ai_platforms": {
    "claude": {
      "api_key": "your-anthropic-api-key-here",
      "model": "claude-sonnet-4-5-20250929"
    },
    "openai": {
      "api_key": "your-openai-api-key-here",
      "model": "gpt-4o"
    },
    "google": {
      "api_key": "your-google-api-key-here",
      "model": "gemini-1.5-pro"
    },
    "xai": {
      "api_key": "your-xai-api-key-here",
      "model": "grok-2"
    }
  },
  "projects": {}
}
```

**Getting API Keys:**
- **Claude/Anthropic**: https://console.anthropic.com
- **OpenAI**: https://platform.openai.com/api-keys
- **Google AI**: https://makersuite.google.com/app/apikey
- **xAI (Grok)**: https://x.ai/api

### 5. Initialize Your First Project

```bash
python orchestration/init-project.py \
  --name "the-explants" \
  --bucket "explants-story-store" \
  --description "Science fiction novel trilogy" \
  --local-path /path/to/The-Explants
```

This will:
- Create a Google Cloud Storage bucket
- Set up standard folder structure
- Add project to configuration
- Create project README

### 6. Upload Your Story Assets

```bash
# From your project directory with story assets
python /path/to/framework/google-store/sync.py \
  --project the-explants \
  --action upload \
  --local-dir . \
  --categories characters worldbuilding chapters
```

### 7. Build Search Index

```bash
python google-store/indexer.py \
  --project the-explants \
  --action build
```

### 8. Generate Your First Scene

```bash
python orchestration/scene-writer.py \
  --project the-explants \
  --scene "Mickey confronts the AI overseer about her neural implant" \
  --agents claude gemini \
  --characters Mickey "AI Overseer" \
  --worldbuilding "neural implants" "corporate control" \
  --output output/scene-01-variations.md
```

### 9. Critique the Variations

```bash
python orchestration/critique.py \
  --input output/scene-01-variations.json \
  --output output/scene-01-critique.md
```

## For The-Explants Specifically

### Quick Integration

1. **Your existing Claude Code skills** in `/The-Explants/.claude/skills/` will continue to work
2. **Use the framework** for multi-agent scene generation
3. **See** `examples/explants-config.json` for recommended settings

### Recommended Workflow

1. Use existing skills for single-agent work
2. Use framework when you want:
   - Multiple agents to write the same scene (comparison)
   - Automatic context from Google File Store
   - Critique and comparative analysis

### Example: Generate Scene with Mickey Voice

```bash
python orchestration/scene-writer.py \
  --project the-explants \
  --scene "Mickey discovers corporate surveillance in her neural implant" \
  --agents claude gemini chatgpt \
  --characters Mickey \
  --worldbuilding "neural implants" "consciousness war" \
  --chapters 3 \
  --instructions "Use Enhanced Mickey Bardot voice: compressed phrasing, direct metaphors, present-tense urgency" \
  --output output/chapter-2-scene-5-variations.md
```

## Troubleshooting

### "No API key configured"
- Check `config/credentials.json` exists and has correct API keys

### "Google Cloud credentials not found"
- Verify path to service account JSON file in `config/credentials.json`
- Ensure the file exists at that path

### "Bucket does not exist"
- Run `init-project.py` to create the bucket
- Or manually create it in Google Cloud Console

### "Permission denied" on bucket
- Check service account has "Storage Admin" role
- Verify project ID matches in credentials

### Import errors
- Run `pip install -r requirements.txt`
- Ensure you're in the framework directory

## Cost Management

Each API call costs money. Approximate costs:

- **Claude Sonnet**: $3/M input tokens, $15/M output tokens
- **GPT-4o**: $5/M input, $15/M output
- **Gemini Pro**: $3.50/M input, $10.50/M output
- **Grok**: ~$5/M input, ~$15/M output (estimated)

**Tips:**
- Use `--max-tokens` to limit output length
- Use fewer agents when testing
- Claude Haiku is cheaper for experimentation

## Next Steps

1. Read the main [README.md](README.md) for architecture details
2. Check [examples/explants-config.json](examples/explants-config.json) for project setup
3. Explore [templates/](templates/) for reusable skills
4. Build your story assets in the standard folder structure

## Support

For issues or questions:
- Check this documentation
- Review example configurations
- Open an issue on GitHub (when repository is public)
