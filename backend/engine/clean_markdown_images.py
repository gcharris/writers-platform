#!/usr/bin/env python3
"""Remove base64-encoded images from markdown files."""

import re
import sys
from pathlib import Path

def remove_base64_images(input_file: str, output_file: str):
    """Remove base64 images from markdown file."""

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: Standard markdown images ![alt](data:image/...)
    pattern1 = r'!\[.*?\]\(data:image/[^)]+\)'

    # Pattern 2: Reference-style markdown [label]: <data:image/...>
    pattern2 = r'\[image\d+\]:\s*<data:image/[^>]+>'

    # Count images before removal
    matches1 = re.findall(pattern1, content, re.DOTALL)
    matches2 = re.findall(pattern2, content, re.DOTALL)

    total_matches = len(matches1) + len(matches2)
    print(f"Found {total_matches} embedded image(s)")
    print(f"  - Standard format: {len(matches1)}")
    print(f"  - Reference-style: {len(matches2)}")

    if matches1:
        print(f"Standard image starts with: {matches1[0][:100]}...")
    if matches2:
        print(f"Reference image starts with: {matches2[0][:100]}...")

    # Replace both patterns with placeholder text
    cleaned = re.sub(pattern1, '[Image removed for processing]', content, flags=re.DOTALL)
    cleaned = re.sub(pattern2, '[image]: [Image removed for processing]', cleaned, flags=re.DOTALL)

    # Verify removal
    remaining = re.findall(r'data:image/', cleaned)
    print(f"Remaining 'data:image/' references: {len(remaining)}")

    # Write cleaned version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"✓ Cleaned file written to: {output_file}")

    # Calculate size reduction
    original_size = len(content)
    cleaned_size = len(cleaned)
    saved = original_size - cleaned_size
    print(f"Size reduced by {saved:,} characters ({original_size:,} → {cleaned_size:,})")

if __name__ == "__main__":
    input_file = "The Explants Series/Knowledge Graph test docs/perplexity editing convo.md"
    output_file = "The Explants Series/Knowledge Graph test docs/perplexity editing convo - clean.md"

    remove_base64_images(input_file, output_file)
