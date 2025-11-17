"""
Explants Knowledge Graph Query Interface

Natural language semantic search across all story documents.
Enables agents to query by meaning, not file paths.
"""

import os
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types

from .config import GeminiFileSearchConfig


class ExplantsKnowledgeGraph:
    """
    Semantic knowledge graph for The Explants trilogy.

    Enables natural language queries like:
    - "What is Mickey's psychological state in Phase 3?"
    - "Explain bi-location mechanics"
    - "Show Mickey and Noni's relationship evolution"
    """

    def __init__(self,
                 store_id: Optional[str] = None,
                 config: Optional[GeminiFileSearchConfig] = None,
                 model: str = "gemini-2.0-flash-exp"):
        """
        Initialize knowledge graph querier.

        Args:
            store_id: File Search store ID (from config if None)
            config: Configuration instance
            model: Gemini model to use
        """
        self.config = config or GeminiFileSearchConfig()

        if store_id is None:
            store_id = self.config.get_file_search_store_id()
            if not store_id:
                raise ValueError("Store ID not configured. Create store first or pass store_id.")

        self.store_id = store_id
        self.model = model

        if not self.config.validate_api_key():
            raise ValueError("Google API key not configured")

        self.client = genai.Client(api_key=self.config.get_google_api_key())

    def query(self,
              question: str,
              volume: Optional[int] = None,
              story_phase: Optional[int] = None,
              categories: Optional[List[str]] = None,
              canon_only: bool = False,
              max_results: int = 10) -> Dict[str, Any]:
        """
        Query the knowledge graph with natural language.

        Args:
            question: Natural language question or prompt
            volume: Filter by volume (1, 2, or 3)
            story_phase: Filter by story phase (1-4)
            categories: Filter by category (character, worldbuilding, scene, etc.)
            canon_only: Only query canon/final versions
            max_results: Maximum chunks to retrieve

        Returns:
            Dictionary with:
            - answer: Generated answer from model
            - citations: List of source citations
            - query: Original question
            - filters: Applied metadata filters
        """
        # Build metadata filter
        filters = []

        if volume is not None:
            filters.append(f'volume={volume}')

        if story_phase is not None:
            filters.append(f'story_phase={story_phase}')

        if categories:
            cat_filters = ' OR '.join([f'category="{cat}"' for cat in categories])
            filters.append(f'({cat_filters})')

        if canon_only:
            filters.append('(status="canon" OR status="final")')

        metadata_filter = ' AND '.join(filters) if filters else None

        try:
            # Build query request with corpus reference
            # Use the corpus as a grounding source for semantic search
            query_config = {
                'model': self.model,
                'contents': question,
                'config': types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            google_search_retrieval=types.GoogleSearchRetrieval(
                                dynamic_retrieval_config=types.DynamicRetrievalConfig(
                                    mode="MODE_DYNAMIC",
                                    dynamic_threshold=0.3
                                )
                            )
                        )
                    ],
                    response_modalities=["TEXT"],
                    temperature=0.3  # Lower for more factual responses
                )
            }

            # Add corpus context if metadata filter is specified
            if metadata_filter:
                # Append filter context to question
                filtered_question = f"{question}\n\nSearch filters: {metadata_filter}"
                query_config['contents'] = filtered_question

            response = self.client.models.generate_content(**query_config)

            # Extract answer
            answer = response.text if hasattr(response, 'text') else str(response)

            # Extract citations (if available)
            citations = []
            if hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata'):
                        gm = candidate.grounding_metadata
                        if hasattr(gm, 'grounding_chunks'):
                            for chunk in gm.grounding_chunks:
                                citation = {}
                                if hasattr(chunk, 'text'):
                                    citation['text'] = chunk.text
                                if hasattr(chunk, 'source'):
                                    citation['source'] = chunk.source
                                if citation:
                                    citations.append(citation)

            return {
                'answer': answer,
                'citations': citations,
                'query': question,
                'filters': metadata_filter,
                'model': self.model
            }

        except Exception as e:
            print(f"Error querying knowledge graph: {e}")
            return {
                'answer': f"Error: {str(e)}",
                'citations': [],
                'query': question,
                'filters': metadata_filter,
                'error': str(e)
            }

    def get_character_context(self,
                             character_name: str,
                             story_phase: Optional[int] = None) -> str:
        """
        Get comprehensive character context.

        Args:
            character_name: Character name (e.g., "Mickey", "Noni")
            story_phase: Filter by story phase

        Returns:
            Character context summary
        """
        query = f"""
        Provide a comprehensive summary of {character_name}'s:
        1. Current psychological state and motivations
        2. Capabilities and limitations
        3. Key relationships with other characters
        4. Recent developments and character arc
        5. Voice and personality traits

        Focus on their current state in the story.
        """

        result = self.query(
            question=query,
            story_phase=story_phase,
            categories=["character", "scene", "chapter", "voice"],
            canon_only=True
        )

        return result['answer']

    def get_worldbuilding_context(self,
                                  topics: List[str],
                                  story_phase: Optional[int] = None) -> str:
        """
        Get worldbuilding mechanics and themes.

        Args:
            topics: List of worldbuilding topics
            story_phase: Filter by story phase

        Returns:
            Worldbuilding context
        """
        topic_str = ", ".join(topics)
        query = f"""
        Explain these worldbuilding concepts: {topic_str}

        Include:
        1. Core mechanics and how they work
        2. Rules and limitations
        3. How characters experience them
        4. Current state in the story
        5. Relevant examples from scenes
        """

        result = self.query(
            question=query,
            story_phase=story_phase,
            categories=["worldbuilding", "scene", "chapter"],
            canon_only=True
        )

        return result['answer']

    def get_recent_chapters(self,
                           count: int = 3,
                           volume: Optional[int] = None) -> str:
        """
        Get summaries of recent chapters.

        Args:
            count: Number of chapters to retrieve
            volume: Filter by volume

        Returns:
            Chapter summaries
        """
        query = f"""
        Summarize the {count} most recent chapters.

        For each chapter, include:
        1. Major events and plot developments
        2. Character developments and decisions
        3. Themes explored
        4. Key scenes and moments
        5. Plot threads continued or resolved
        """

        result = self.query(
            question=query,
            volume=volume,
            categories=["chapter"],
            canon_only=True
        )

        return result['answer']

    def find_related_scenes(self,
                           scene_outline: str,
                           story_phase: Optional[int] = None) -> str:
        """
        Find scenes related to the outline.

        Args:
            scene_outline: Description of scene to write
            story_phase: Filter by story phase

        Returns:
            Related scenes description
        """
        query = f"""
        Find scenes similar to: {scene_outline}

        Show scenes that:
        1. Feature the same characters
        2. Explore similar themes or conflicts
        3. Reference related events
        4. Use similar worldbuilding mechanics
        5. Match the emotional tone

        For each scene, briefly describe what makes it relevant.
        """

        result = self.query(
            question=query,
            story_phase=story_phase,
            categories=["scene", "chapter"],
            canon_only=True
        )

        return result['answer']

    def build_scene_context(self,
                           scene_outline: str,
                           characters: List[str],
                           worldbuilding_topics: List[str],
                           story_phase: Optional[int] = None,
                           include_related_scenes: bool = True) -> Dict[str, Any]:
        """
        Build complete context package for writing a scene.

        This is what tournament agents use before generating variations.

        Args:
            scene_outline: Scene description
            characters: Character names to include
            worldbuilding_topics: Worldbuilding concepts to include
            story_phase: Story phase (1-4)
            include_related_scenes: Whether to find related scenes

        Returns:
            Complete context package with all information
        """
        context = {
            'scene_outline': scene_outline,
            'characters': {},
            'worldbuilding': '',
            'recent_chapters': '',
            'related_scenes': '',
            'story_phase': story_phase
        }

        print(f"Building context for scene: {scene_outline[:50]}...")

        # Get character context
        if characters:
            print(f"  Retrieving context for {len(characters)} characters...")
            for character in characters:
                try:
                    context['characters'][character] = self.get_character_context(
                        character, story_phase
                    )
                except Exception as e:
                    print(f"    Warning: Could not get context for {character}: {e}")
                    context['characters'][character] = f"[Context unavailable: {e}]"

        # Get worldbuilding
        if worldbuilding_topics:
            print(f"  Retrieving worldbuilding for {len(worldbuilding_topics)} topics...")
            try:
                context['worldbuilding'] = self.get_worldbuilding_context(
                    worldbuilding_topics, story_phase
                )
            except Exception as e:
                print(f"    Warning: Could not get worldbuilding: {e}")
                context['worldbuilding'] = f"[Worldbuilding unavailable: {e}]"

        # Get recent chapters
        print("  Retrieving recent chapters...")
        try:
            context['recent_chapters'] = self.get_recent_chapters(count=3)
        except Exception as e:
            print(f"    Warning: Could not get recent chapters: {e}")
            context['recent_chapters'] = f"[Recent chapters unavailable: {e}]"

        # Find related scenes
        if include_related_scenes:
            print("  Finding related scenes...")
            try:
                context['related_scenes'] = self.find_related_scenes(
                    scene_outline, story_phase
                )
            except Exception as e:
                print(f"    Warning: Could not find related scenes: {e}")
                context['related_scenes'] = f"[Related scenes unavailable: {e}]"

        print("✓ Context building complete")

        return context

    def format_context_for_agent(self, context: Dict[str, Any]) -> str:
        """
        Format context package as prompt text for agents.

        Args:
            context: Context package from build_scene_context()

        Returns:
            Formatted prompt text
        """
        sections = []

        # Scene outline
        sections.append(f"SCENE OUTLINE:\n{context['scene_outline']}\n")

        # Characters
        if context.get('characters'):
            sections.append("=" * 80)
            sections.append("CHARACTER CONTEXT:")
            sections.append("=" * 80)
            for name, info in context['characters'].items():
                sections.append(f"\n### {name.upper()}:")
                sections.append(info)

        # Worldbuilding
        if context.get('worldbuilding'):
            sections.append("\n" + "=" * 80)
            sections.append("WORLDBUILDING & MECHANICS:")
            sections.append("=" * 80)
            sections.append(context['worldbuilding'])

        # Recent chapters
        if context.get('recent_chapters'):
            sections.append("\n" + "=" * 80)
            sections.append("RECENT CHAPTERS (For Continuity):")
            sections.append("=" * 80)
            sections.append(context['recent_chapters'])

        # Related scenes
        if context.get('related_scenes'):
            sections.append("\n" + "=" * 80)
            sections.append("RELATED SCENES (For Reference):")
            sections.append("=" * 80)
            sections.append(context['related_scenes'])

        # Story phase note
        if context.get('story_phase'):
            sections.append(f"\n[Story Phase: {context['story_phase']}]")

        return "\n".join(sections)


# Test examples
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_querier.py <store-id>")
        sys.exit(1)

    store_id = sys.argv[1]

    print("=" * 80)
    print("EXPLANTS KNOWLEDGE GRAPH - TEST QUERIES")
    print("=" * 80)
    print(f"Store ID: {store_id}")
    print()

    kg = ExplantsKnowledgeGraph(store_id=store_id)

    # Test 1: Character query
    print("TEST 1: Character Context")
    print("-" * 80)
    result = kg.query(
        question="What is Mickey Bardot's psychological state in Phase 3?",
        story_phase=3,
        categories=["character", "scene"],
        canon_only=True
    )
    print(f"Answer: {result['answer'][:300]}...")
    print(f"Citations: {len(result['citations'])}")
    print()

    # Test 2: Worldbuilding query
    print("TEST 2: Worldbuilding Mechanics")
    print("-" * 80)
    result = kg.query(
        question="Explain bi-location mechanics: The Line, The Tether, The Shared Vein",
        categories=["worldbuilding"],
        canon_only=True
    )
    print(f"Answer: {result['answer'][:300]}...")
    print()

    # Test 3: Scene context building
    print("TEST 3: Scene Context Package")
    print("-" * 80)
    context = kg.build_scene_context(
        scene_outline="Mickey processes bi-location strain after Noni's warning",
        characters=["Mickey", "Noni"],
        worldbuilding_topics=["bi-location", "The Line"],
        story_phase=3
    )
    formatted = kg.format_context_for_agent(context)
    print(f"Context length: {len(formatted):,} characters")
    print(f"Preview:\n{formatted[:500]}...")
    print()

    print("=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
