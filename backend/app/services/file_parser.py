"""
File Parser Service
===================

Parses uploaded files (DOCX, PDF, TXT) into structured content.
Extracts chapters, scenes, and metadata for Factory analysis.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import io

# File processing libraries
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

import charset_normalizer


class FileParser:
    """Parse uploaded files and extract structured content."""

    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> Dict:
        """
        Parse a file based on its extension.

        Args:
            file_content: Raw file bytes
            filename: Original filename with extension

        Returns:
            Dict with:
                - title: str
                - content: str (full text)
                - word_count: int
                - chapters: List[Dict] (optional)
                - metadata: Dict

        Raises:
            ValueError: If file type not supported or parsing fails
        """
        ext = Path(filename).suffix.lower()

        if ext == '.docx':
            return FileParser.parse_docx(file_content)
        elif ext == '.pdf':
            return FileParser.parse_pdf(file_content)
        elif ext in ['.txt', '.md']:
            return FileParser.parse_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported: .docx, .pdf, .txt, .md")

    @staticmethod
    def parse_docx(file_content: bytes) -> Dict:
        """Parse DOCX file."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")

        try:
            doc = Document(io.BytesIO(file_content))

            # Extract paragraphs
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

            # Join to full text
            full_text = '\n\n'.join(paragraphs)

            # Detect title (first non-empty paragraph)
            title = paragraphs[0] if paragraphs else "Untitled"

            # Detect chapters/structure
            chapters = FileParser.detect_chapters(paragraphs)

            return {
                'title': title,
                'content': full_text,
                'word_count': len(full_text.split()),
                'chapters': chapters,
                'metadata': {
                    'source': 'docx',
                    'paragraph_count': len(paragraphs),
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    @staticmethod
    def parse_pdf(file_content: bytes) -> Dict:
        """Parse PDF file."""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

        try:
            pdf = PdfReader(io.BytesIO(file_content))

            # Extract text from all pages
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text.strip():
                    pages_text.append(text)

            # Join all text
            full_text = '\n\n'.join(pages_text)

            # Split into paragraphs (for chapter detection)
            paragraphs = [p.strip() for p in full_text.split('\n') if p.strip()]

            # Detect title
            title = paragraphs[0] if paragraphs else "Untitled"

            # Detect chapters
            chapters = FileParser.detect_chapters(paragraphs)

            return {
                'title': title,
                'content': full_text,
                'word_count': len(full_text.split()),
                'chapters': chapters,
                'metadata': {
                    'source': 'pdf',
                    'page_count': len(pdf.pages),
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def parse_txt(file_content: bytes) -> Dict:
        """Parse plain text file."""
        try:
            # Detect encoding
            detection = charset_normalizer.from_bytes(file_content).best()
            if not detection:
                # Fallback to utf-8
                text = file_content.decode('utf-8', errors='ignore')
            else:
                text = str(detection)

            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

            # Detect title
            title = paragraphs[0] if paragraphs else "Untitled"

            # Detect chapters
            chapters = FileParser.detect_chapters(paragraphs)

            return {
                'title': title,
                'content': text,
                'word_count': len(text.split()),
                'chapters': chapters,
                'metadata': {
                    'source': 'txt',
                    'line_count': len(paragraphs),
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to parse text file: {str(e)}")

    @staticmethod
    def detect_chapters(paragraphs: List[str]) -> List[Dict]:
        """
        Detect chapter boundaries in text.

        Looks for patterns like:
        - "Chapter 1", "Chapter One"
        - "CHAPTER 1", "CHAPTER ONE"
        - "1.", "I.", "Part 1"
        - Lines with only numbers or roman numerals

        Returns:
            List of chapter dicts with:
                - number: int
                - title: str
                - start_para: int
                - content: str (optional)
        """
        chapters = []
        current_chapter = None
        chapter_start_idx = 0

        # Chapter patterns
        patterns = [
            r'^Chapter\s+(\d+)',  # Chapter 1
            r'^CHAPTER\s+(\d+)',  # CHAPTER 1
            r'^Ch\.\s*(\d+)',     # Ch. 1
            r'^(\d+)\.\s*$',      # 1.
            r'^Part\s+(\d+)',     # Part 1
            r'^PART\s+(\d+)',     # PART 1
        ]

        for i, para in enumerate(paragraphs):
            # Check if this paragraph is a chapter heading
            is_chapter = False
            chapter_num = None

            for pattern in patterns:
                match = re.match(pattern, para.strip())
                if match:
                    is_chapter = True
                    chapter_num = int(match.group(1)) if match.groups() else len(chapters) + 1
                    break

            if is_chapter:
                # Save previous chapter
                if current_chapter:
                    current_chapter['content'] = '\n\n'.join(
                        paragraphs[chapter_start_idx:i]
                    )
                    chapters.append(current_chapter)

                # Start new chapter
                current_chapter = {
                    'number': chapter_num,
                    'title': para.strip(),
                    'start_para': i,
                    'content': ''
                }
                chapter_start_idx = i + 1

        # Add final chapter
        if current_chapter:
            current_chapter['content'] = '\n\n'.join(
                paragraphs[chapter_start_idx:]
            )
            chapters.append(current_chapter)

        # If no chapters detected, treat whole text as one chapter
        if not chapters and paragraphs:
            chapters = [{
                'number': 1,
                'title': 'Full Text',
                'start_para': 0,
                'content': '\n\n'.join(paragraphs)
            }]

        return chapters

    @staticmethod
    def split_into_scenes(text: str, max_words_per_scene: int = 1000) -> List[Dict]:
        """
        Split text into scenes based on natural boundaries.

        Looks for:
        - Scene breaks (### or ---)
        - Large paragraph breaks
        - Natural splitting points if chapter too long

        Args:
            text: Chapter or full text
            max_words_per_scene: Maximum words per scene (for splitting long chapters)

        Returns:
            List of scene dicts with:
                - number: int
                - content: str
                - word_count: int
        """
        scenes = []

        # First, check for explicit scene breaks
        scene_markers = [
            r'\n#{3,}\n',  # ### or ####
            r'\n---+\n',   # ---
            r'\n\*\*\*+\n', # ***
        ]

        # Try to split by scene markers
        parts = [text]
        for marker in scene_markers:
            if re.search(marker, text):
                parts = re.split(marker, text)
                break

        # If no markers, split by large paragraph breaks (2+ empty lines)
        if len(parts) == 1:
            parts = re.split(r'\n{3,}', text)

        # Create scenes from parts
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            word_count = len(part.split())

            # If part is too long, split further
            if word_count > max_words_per_scene * 1.5:
                # Split by paragraphs
                paragraphs = [p.strip() for p in part.split('\n\n') if p.strip()]
                sub_scenes = []
                current_scene = []
                current_words = 0

                for para in paragraphs:
                    para_words = len(para.split())
                    if current_words + para_words > max_words_per_scene and current_scene:
                        # Save current scene
                        sub_scenes.append('\n\n'.join(current_scene))
                        current_scene = [para]
                        current_words = para_words
                    else:
                        current_scene.append(para)
                        current_words += para_words

                # Add final scene
                if current_scene:
                    sub_scenes.append('\n\n'.join(current_scene))

                # Add all sub-scenes
                for sub_scene in sub_scenes:
                    scenes.append({
                        'number': len(scenes) + 1,
                        'content': sub_scene,
                        'word_count': len(sub_scene.split())
                    })
            else:
                # Add as single scene
                scenes.append({
                    'number': len(scenes) + 1,
                    'content': part,
                    'word_count': word_count
                })

        return scenes if scenes else [{
            'number': 1,
            'content': text,
            'word_count': len(text.split())
        }]
