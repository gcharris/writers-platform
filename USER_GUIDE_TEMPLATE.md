# How to Create User Guides from Technical Documentation

This template shows how to transform technical documentation into user-friendly guides.

---

## The Formula

**Technical Docs** → **User Guide**

1. **Extract the "What"** - What does it do?
2. **Simplify the "Why"** - Why would users care?
3. **Break down the "How"** - Step-by-step instructions
4. **Add visuals** - Screenshots, diagrams
5. **Use friendly language** - No jargon
6. **Include examples** - Real use cases

---

## Example 1: Entity-Based Discovery

### From Technical Docs:

```
## Entity-Based Discovery

**Purpose**: Find stories by searching for specific characters, locations, or themes.

**Backend Implementation**:
- Endpoint: GET /api/browse/by-entity
- Queries: project_graphs table
- Searches: JSONB graph_data for matching nodes
- Fuzzy logic: "Mickey" matches "Mickey Mouse", "Michael"
```

### User Guide Version:

```
# Finding Stories by Character or Location 🔍

Ever wanted to find all stories featuring a specific character like "Mickey Mouse"
or set in a particular location like "Shanghai"? Now you can!

## How It Works

Our Entity-Based Discovery lets you search for stories using characters,
locations, or themes instead of just keywords.

## Step-by-Step Guide

1. **Go to the Browse Page**
   - Visit writerscommunity.app/browse

2. **Find the Purple Search Box**
   - Look for "Entity-Based Discovery" section
   - It's in a purple gradient box near the top

3. **Enter Your Search**
   - Type the character, location, or theme you're looking for
   - Examples: "Mickey", "Shanghai", "AI", "time travel"

4. **Select Type (Optional)**
   - Choose from dropdown: Character, Location, Theme, etc.
   - This helps narrow results

5. **Click Search**
   - Hit the search button
   - Results appear instantly!

6. **Browse Results**
   - See all stories featuring your search
   - Each result shows: title, author, excerpt

## Examples

**Find character-driven stories:**
- Search: "Sherlock Holmes"
- Type: Character
- Results: All detective stories with Sherlock

**Discover location-based fiction:**
- Search: "Mars"
- Type: Location
- Results: Sci-fi stories set on Mars

**Explore themes:**
- Search: "artificial intelligence"
- Type: Theme
- Results: Stories exploring AI concepts

## Tips

✅ The search is "fuzzy" - it finds similar matches too
✅ You don't need to know the exact spelling
✅ Try searching without selecting a type first - you might discover more!

## Troubleshooting

**Q: No results found?**
A: Try searching without selecting a type, or use shorter search terms.

**Q: Too many results?**
A: Select a specific type from the dropdown to narrow results.

**Q: Wrong results?**
A: Be more specific - instead of "John", try "John Watson".
```

---

## Example 2: NotebookLM Integration

### From Technical Docs:

```
## NotebookLM Integration

**Purpose**: Ground fiction writing in real-world research by integrating
Google's NotebookLM.

**How It Works**:
1. Writer creates NotebookLM notebooks externally
2. Adds research sources (YouTube, PDFs, articles)
3. Configures notebook URLs in Factory settings
4. AI Copilot queries notebooks for context
5. Entity extraction pulls from notebooks

**Notebook Types**:
- Character Research: Interviews, personality studies
- World Building: Future tech, social trends
- Themes & Philosophy: Ethical frameworks
```

### User Guide Version:

```
# Using Real Research in Your Fiction 📚

Want your sci-fi to be scientifically accurate? Your historical fiction
grounded in real events? NotebookLM integration lets you add real research
to your writing!

## What is NotebookLM?

NotebookLM is Google's AI research assistant. You feed it YouTube videos,
PDFs, articles, and it answers questions about them. We've integrated it
into Writers Factory so your AI writing assistant can reference YOUR research!

## Quick Start (5 Minutes)

### Step 1: Create a NotebookLM Notebook

1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Sign in with your Google account
3. Click "Create New Notebook"
4. Give it a name (e.g., "Character Research - Dr. Sarah Chen")

### Step 2: Add Your Research

Upload any of these:
- 📹 YouTube video URLs (interviews, documentaries)
- 📄 PDF files (research papers, reports)
- 📝 Text documents (articles, notes)
- 🔗 Website links

**Example for a character**:
- YouTube interview with a similar person
- PDF of their biography
- Articles about their field of expertise

### Step 3: Get the Notebook URL

1. Once you've added sources, copy the notebook URL from your browser
2. It looks like: `https://notebooklm.google.com/notebook/abc123`

### Step 4: Connect to Writers Factory

1. Open your project in Factory
2. Go to **Settings** → **NotebookLM Integration**
3. Paste your notebook URL in the appropriate field:
   - **Character Research**: For character personalities, backgrounds
   - **World Building**: For settings, technologies, societies
   - **Themes**: For philosophical concepts, ethics

4. Click "Save Configuration"

### Step 5: Use It!

Now when you write:
- Your AI Copilot will reference your research
- Entity extraction will be grounded in real sources
- You'll see citations showing which research informed each detail

## Real-World Example

**Project**: Sci-fi novel set in 2045

**NotebookLM Setup**:

1. **Character Research Notebook**:
   - YouTube: Interviews with AI researchers
   - PDF: Cognitive psychology papers
   - Goal: Create realistic AI scientist character

2. **World Building Notebook**:
   - YouTube: Future tech predictions
   - PDF: Climate change reports
   - Articles: Smart city designs
   - Goal: Accurate 2045 setting

3. **Themes Notebook**:
   - YouTube: Philosophy lectures on consciousness
   - PDF: AI ethics frameworks
   - Goal: Explore AI consciousness theme

**Result**: Fiction grounded in real research, with citations showing sources!

## Pro Tips

💡 **One notebook per project** - Keep research organized

💡 **Update as you research** - Add sources as you find them

💡 **Use Batch Extraction** - Extract all notebooks at once instead of one-by-one

💡 **Check citations** - See which research influenced each character/location

## Batch Extraction (Advanced)

Instead of extracting one notebook at a time:

1. Go to NotebookLM Settings
2. Find the purple "Batch Extraction" section
3. Check which types to extract (Character, World, Themes)
4. Click "Start Batch Extraction"
5. Wait for completion (shows progress)
6. See results: entities added and enriched

**Saves hours** if you have multiple projects!

## Troubleshooting

**Q: Can't find NotebookLM Settings?**
A: Open a project → Settings menu → NotebookLM Integration

**Q: "MCP server not available" error?**
A: Contact support - the NotebookLM connector needs to be running

**Q: Citations not showing?**
A: Re-extract entities after configuring notebooks

**Q: Free or paid?**
A: NotebookLM itself is FREE! You just need a Google account.
```

---

## Example 3: AI Wizard

### From Technical Docs:

```
## AI Wizard

**Purpose**: Conversational interface to guide users through complex
setup via chat (like ChatGPT).

**Contexts**:
1. Onboarding - First-time users
2. Project Setup - Creating new projects
3. NotebookLM - Research integration
4. Knowledge Graph - Entity management
5. Copilot - AI assistant setup
```

### User Guide Version:

```
# Your AI Setup Assistant 🧙‍♂️

Overwhelmed by all the features? Don't worry - our AI Wizard will guide you
through everything via friendly chat!

## What is the AI Wizard?

Think of it as ChatGPT specifically trained to help you set up Writers Platform.
Instead of reading manuals, just chat with the wizard and it'll guide you step-by-step.

## How to Access

**Method 1: Floating Button**
- Look for the wizard icon (🧙‍♂️) in the bottom-right corner
- Click it to open chat
- Available on most pages

**Method 2: Full Page**
- Go to writersfactory.app/wizard
- Full-screen chat experience
- Perfect for initial setup

**Method 3: Help Button**
- Click any "Need Help?" button
- Wizard opens in modal
- Contextual help for that feature

## What the Wizard Can Help With

### 1️⃣ First-Time Setup (Onboarding)
**Start here if you're new!**

Chat starts with:
> "👋 Welcome to Writers Factory! What kind of story are you working on?"

Guides you through:
- Choosing genre
- Creating your first project
- Optional research setup
- Quick tour of features

**Time**: 5 minutes

### 2️⃣ Creating New Projects
**Use when starting a new story**

Chat flow:
> "What's your project name?"
> "Would you like to set up research?"

Creates project for you automatically!

### 3️⃣ NotebookLM Research Setup
**Use when adding research**

Wizard explains:
- How to create NotebookLM notebooks
- Where to paste URLs
- How to use batch extraction

Opens NotebookLM in new tab for you!

### 4️⃣ Knowledge Graph Help
**Use when building character/location maps**

Options:
> "Extract from scenes" - Automatic entity detection
> "Start fresh" - Manual entity creation

Starts extraction with one click!

### 5️⃣ AI Copilot Configuration
**Use when setting up writing assistant**

Choice:
> "FREE Local AI (Ollama)" - No cost, runs on your computer
> "Premium Models" - Claude, GPT-4 (requires API keys)

Guides through installation!

## Example Conversation

**You**: *Click wizard button*

**Wizard**: 👋 Welcome! I'm your AI assistant. How can I help you today?

[Create a project] [Set up research] [Learn about features]

**You**: *Click "Create a project"*

**Wizard**: Great! What kind of story are you working on?

[Science Fiction] [Fantasy] [Mystery] [Other]

**You**: *Click "Science Fiction"*

**Wizard**: Excellent! Sci-fi is exciting. What's your project name?

**You**: "The Mars Colony"

**Wizard**: Perfect! "The Mars Colony" - love it! Would you like to set up
NotebookLM for research to make your Mars colony scientifically accurate?

[Yes, set up research] [Skip for now]

**You**: *Click "Yes"*

**Wizard**: Excellent! Let me guide you through NotebookLM setup...

[Continue to NotebookLM Setup]

...and so on!

## Tips for Using the Wizard

✅ **Read the full message** - Wizard provides helpful context

✅ **Use buttons when available** - Faster than typing

✅ **You can type too** - Natural language works!

✅ **Ask follow-up questions** - Wizard remembers context

✅ **Close anytime** - Progress is saved

## Common Questions

**Q: Is it actually AI or just scripted?**
A: It's conversational UI with smart branching logic - not real AI responses,
but feels natural!

**Q: Can I restart a conversation?**
A: Yes! Just refresh or close and reopen the wizard.

**Q: What if I don't know the answer?**
A: Wizard offers suggestions and examples. Just pick what seems closest!

**Q: Can I skip steps?**
A: Absolutely! Most steps are optional. Skip what you don't need.

## When to Use the Wizard

**First Time Using Platform**: Start with onboarding wizard

**Creating New Project**: Use project setup wizard

**Stuck on a Feature**: Click floating wizard button

**Want Quick Setup**: Wizard is faster than reading docs!

---

**Pro Tip**: The wizard is designed to make complex features feel simple.
Don't be intimidated by all the capabilities - just chat with the wizard
and it'll guide you!
```

---

## Template Structure

Every user guide should have:

### 1. Catchy Title + Emoji
Make it friendly and approachable

### 2. Opening Hook
One sentence explaining why they should care

### 3. "What Is This?" Section
Explain the feature in simple terms

### 4. "How It Works" Overview
High-level process before details

### 5. Step-by-Step Instructions
Numbered list with clear actions

### 6. Real Examples
Concrete use cases users can relate to

### 7. Tips & Tricks
Pro tips that make them feel smart

### 8. Troubleshooting
Common questions answered

### 9. Visual Aids (if possible)
Screenshots, diagrams, GIFs

### 10. Next Steps
Where to go from here

---

## Language Guidelines

### DO ✅
- Use "you" and "your"
- Keep sentences short
- Use emojis sparingly for visual interest
- Explain jargon in parentheses
- Use active voice
- Include examples
- Be encouraging

### DON'T ❌
- Use technical terms without explanation
- Write long paragraphs
- Assume prior knowledge
- Be condescending
- Skip the "why"
- Forget screenshots
- Make them feel dumb

---

## Quick Conversion Checklist

When creating a user guide from technical docs:

- [ ] Identify the feature from technical docs
- [ ] Write catchy, user-friendly title
- [ ] Explain "why" they'd use it (benefit-first)
- [ ] Break technical process into numbered steps
- [ ] Replace technical terms with plain language
- [ ] Add real-world examples
- [ ] Include screenshots/diagrams
- [ ] Write troubleshooting section
- [ ] Add tips and tricks
- [ ] Have someone non-technical review it

---

## Examples of Term Translation

| Technical | User-Friendly |
|-----------|---------------|
| "JSONB graph_data" | "your character relationships" |
| "Endpoint" | "feature" or "tool" |
| "Query parameters" | "search options" |
| "Authentication token" | "login session" |
| "Entity extraction" | "finding characters and locations" |
| "Knowledge graph" | "character relationship map" |
| "MCP server" | "research connector" |
| "Fuzzy matching" | "smart search that finds similar matches" |

---

## Final Tips

1. **Start with the problem** - "Want to find stories by character?"
2. **Show, don't tell** - Use examples liberally
3. **Test with real users** - Non-technical friends
4. **Keep it scannable** - Headers, bullets, short paragraphs
5. **Update regularly** - As features change

---

**Remember**: Technical docs are FOR developers. User guides are FOR users.
They serve different purposes and should be written differently!

Good user guides feel like a helpful friend explaining something, not a
manual reciting facts.
