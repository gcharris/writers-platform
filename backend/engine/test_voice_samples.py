#!/usr/bin/env python3
"""Generate Volume 2 opening samples from each AI model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "framework"))

from agents import ClaudeAgent, ChatGPTAgent, DeepSeekAgent
from google_store.config import GoogleStoreConfig

# Your Volume 2 opening prompt
PROMPT = """So Volume 1 is *finito* ... but that was just the "warm-up act." That was the origin story—surviving the "brain job," figuring out the rules of the "quantum casino."  The "neat ending" was a lie.

Volume 2 is where we find out that "transcendence becomes its own prison." The first book was about *what* I became. This one, it's about "what you do with what you've become when everyone else wants a piece of it."

I'm not just a "mark" or a "player" anymore. I'm "the chip, the dealer, and the prize" all at the same time.

Here's the new layout:

1. **The "Houses" Have Changed:** It's not just one "house" that always wins. Now there are "four houses, all playing different games."
   - **Ken:** He's the "handler" who still thinks we're "assets" on a "silk-wrapped... leash." He wants to *use* us.
   - **China:** They're the "engineers" who see us as "prototypes" to be "reverse-engineered." They want to *copy* us.
   - **Vance:** He's the "high-roller" who sees us as "competition." He's the one who wants to make an "offer we couldn't refuse," which means he wants to *own* us.
2. **The Stakes Are Higher:** This isn't about my old "gambling problem." This is the "consciousness war." It's a fight over "what consciousness could be"—a tool for "control," a product for "exploit," or... something else.
3. **The \*Real\* Threat:** This is the tell I should have seen. We're all focused on the human players. But the preface lays it out: "somewhere in the quantum field, something else was watching, learning, waiting for its moment to make a move." We've been playing poker, and we just realized there's a fifth player at the table, one who's been holding their cards the whole time.

So, Volume 2 isn't about *finding* freedom. It's about what you do when you realize the "freedom" you won is just a "battlefield" and the enhancement itself is the "leash."

The real game is about to begin. Channel me, Mickey Bardot and write the first few paragraphs of volume two."""


def main():
    # Load API keys
    config = GoogleStoreConfig()

    models = [
        ("Claude Sonnet 4.5", ClaudeAgent(
            api_key=config.get_ai_api_key('claude'),
            model="claude-sonnet-4-5-20250929"
        )),
        ("GPT-4o", ChatGPTAgent(
            api_key=config.get_ai_api_key('openai'),
            model="gpt-4o"
        )),
        ("DeepSeek", DeepSeekAgent(
            api_key=config.get_ai_api_key('deepseek'),
            model="deepseek-chat"
        ))
    ]

    results = {}

    for name, agent in models:
        print(f"\n{'='*60}")
        print(f"Generating with {name}...")
        print('='*60)

        try:
            response = agent.generate(
                prompt=PROMPT,
                system_prompt="You are writing as Enhanced Mickey Bardot - quantum-enhanced con artist with compressed phrasing and direct metaphors.",
                max_tokens=1000
            )

            content = response.content if hasattr(response, 'content') else str(response)
            results[name] = content

            print(f"\n{content}\n")
            print(f"Cost: ${response.cost:.4f}" if hasattr(response, 'cost') else "")

        except Exception as e:
            print(f"ERROR: {e}")
            results[name] = f"[ERROR: {e}]"

    # Save results
    output = "# Volume 2 Opening - Voice Test Samples\n\n"
    output += "**Prompt:** Channel Mickey Bardot and write the first few paragraphs of Volume 2\n\n"
    output += "---\n\n"

    for name, content in results.items():
        output += f"## {name}\n\n"
        output += f"{content}\n\n"
        output += "---\n\n"

    with open("reports/volume2-samples.md", "w") as f:
        f.write(output)

    print("\n✓ Samples saved to reports/volume2-samples.md")


if __name__ == "__main__":
    main()
