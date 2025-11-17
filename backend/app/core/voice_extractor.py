"""Voice Profile Extractor - Extract voice characteristics from example passages.

Uses LLM analysis to identify:
- Sentence structure (compression, length, patterns)
- Vocabulary (formality, complexity, distinctive words)
- Metaphor style (domains, frequency, directness)
- POV handling (depth, filter words, consciousness immersion)
- Dialogue patterns
- Anti-patterns to avoid
- Quality criteria for scoring
"""

from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import json
import logging

logger = logging.getLogger(__name__)


class VoiceProfile:
    """Complete voice profile for a project."""

    def __init__(
        self,
        voice_name: str,
        genre: str,
        primary_characteristics: List[str],
        sentence_structure: Dict[str, Any],
        vocabulary: Dict[str, Any],
        pov_style: Dict[str, Any],
        metaphor_domains: Optional[Dict[str, 'MetaphorDomain']] = None,
        anti_patterns: Optional[List['AntiPattern']] = None,
        quality_criteria: Optional['QualityCriteria'] = None,
        voice_consistency_notes: Optional[List[str]] = None
    ):
        self.voice_name = voice_name
        self.genre = genre
        self.primary_characteristics = primary_characteristics
        self.sentence_structure = sentence_structure
        self.vocabulary = vocabulary
        self.pov_style = pov_style
        self.metaphor_domains = metaphor_domains or {}
        self.anti_patterns = anti_patterns or []
        self.quality_criteria = quality_criteria
        self.voice_consistency_notes = voice_consistency_notes or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        """Create VoiceProfile from dictionary."""
        return cls(
            voice_name=data["voice_name"],
            genre=data["genre"],
            primary_characteristics=data["primary_characteristics"],
            sentence_structure=data["sentence_structure"],
            vocabulary=data["vocabulary"],
            pov_style=data["pov_style"],
            voice_consistency_notes=data.get("voice_consistency_notes", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "voice_name": self.voice_name,
            "genre": self.genre,
            "primary_characteristics": self.primary_characteristics,
            "sentence_structure": self.sentence_structure,
            "vocabulary": self.vocabulary,
            "pov_style": self.pov_style,
            "metaphor_domains": {
                name: {
                    "max_percentage": domain.max_percentage,
                    "keywords": domain.keywords,
                    "examples": domain.examples
                }
                for name, domain in self.metaphor_domains.items()
            },
            "anti_patterns": [
                {
                    "pattern_id": ap.pattern_id,
                    "name": ap.name,
                    "description": ap.description,
                    "why_avoid": ap.why_avoid,
                    "detection_method": ap.detection_method,
                    "severity": ap.severity,
                    "regex": ap.regex,
                    "keywords": ap.keywords,
                    "examples": ap.examples
                }
                for ap in self.anti_patterns
            ],
            "quality_criteria": self.quality_criteria.to_dict() if self.quality_criteria else None,
            "voice_consistency_notes": self.voice_consistency_notes
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "voice_name": self.voice_name,
            "genre": self.genre,
            "primary_characteristics": self.primary_characteristics,
            "sentence_structure": self.sentence_structure,
            "vocabulary": self.vocabulary,
            "pov_style": self.pov_style
        }, indent=2)


class MetaphorDomain:
    """A metaphor domain with usage limits."""

    def __init__(
        self,
        max_percentage: int,
        keywords: List[str],
        examples: List[str]
    ):
        self.max_percentage = max_percentage
        self.keywords = keywords
        self.examples = examples


class AntiPattern:
    """A pattern to avoid in this voice."""

    def __init__(
        self,
        pattern_id: str,
        name: str,
        description: str,
        why_avoid: str,
        detection_method: str,
        severity: str,
        examples: List[str],
        regex: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ):
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.why_avoid = why_avoid
        self.detection_method = detection_method
        self.severity = severity
        self.examples = examples
        self.regex = regex
        self.keywords = keywords or []


class QualityCriteria:
    """Scoring criteria for this voice/genre."""

    def __init__(self, total_points: int, categories: List[Dict[str, Any]]):
        self.total_points = total_points
        self.categories = categories

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityCriteria':
        """Create QualityCriteria from dictionary."""
        return cls(
            total_points=data["total_points"],
            categories=data["categories"]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_points": self.total_points,
            "categories": self.categories
        }


class VoiceProfileExtractor:
    """
    Extracts voice profile from example passages using LLM analysis.

    Analyzes:
    - Sentence structure (short/long, compressed/flowing)
    - Vocabulary (formal/casual, technical/simple)
    - Metaphor style (direct/complex, domains)
    - POV handling (deep/shallow, filter words)
    - Dialogue patterns
    - Internal monologue style
    """

    def __init__(self, anthropic_client: Anthropic):
        """Initialize voice profile extractor.

        Args:
            anthropic_client: Anthropic API client for LLM analysis
        """
        self.client = anthropic_client

    async def extract_voice_profile(
        self,
        example_passages: List[str],
        uploaded_docs: List[Dict[str, Any]],
        notebooklm_context: Optional[str] = None
    ) -> VoiceProfile:
        """
        Extract comprehensive voice profile from inputs.

        Args:
            example_passages: 3-5 scene excerpts (500-1000 words each)
            uploaded_docs: Previous drafts, style guides
            notebooklm_context: Knowledge from NotebookLM notebook

        Returns:
            VoiceProfile with extracted characteristics
        """
        logger.info(f"Extracting voice profile from {len(example_passages)} passages")

        # Step 1: Analyze each passage individually
        passage_analyses = []
        for i, passage in enumerate(example_passages):
            logger.info(f"Analyzing passage {i+1}/{len(example_passages)}")
            analysis = await self._analyze_single_passage(passage, i+1)
            passage_analyses.append(analysis)

        # Step 2: Synthesize across all passages
        logger.info("Synthesizing voice profile from all passages")
        voice_profile = await self._synthesize_voice_profile(
            passage_analyses,
            uploaded_docs,
            notebooklm_context
        )

        # Step 3: Extract specific elements
        logger.info("Extracting metaphor domains")
        voice_profile.metaphor_domains = await self._extract_metaphor_domains(
            example_passages
        )

        logger.info("Identifying anti-patterns")
        voice_profile.anti_patterns = await self._identify_anti_patterns(
            example_passages,
            uploaded_docs
        )

        logger.info("Deriving quality criteria")
        voice_profile.quality_criteria = await self._derive_quality_criteria(
            voice_profile,
            genre=voice_profile.genre
        )

        logger.info(f"Voice profile extraction complete: {voice_profile.voice_name}")
        return voice_profile

    async def _analyze_single_passage(
        self,
        passage: str,
        passage_num: int
    ) -> Dict[str, Any]:
        """
        Deep analysis of a single passage.

        Returns characteristics:
        - sentence_length_avg, sentence_length_variance
        - compression_level (1-10)
        - metaphor_density, metaphor_complexity
        - filter_word_count
        - pov_depth (shallow/medium/deep)
        - vocabulary_level (simple/moderate/complex)
        - dialogue_ratio

        Args:
            passage: Text to analyze
            passage_num: Passage number for logging

        Returns:
            Dictionary of voice characteristics
        """

        prompt = f"""Analyze this passage from a novel and extract detailed voice characteristics.

PASSAGE {passage_num}:
{passage}

Provide JSON analysis with these fields:

{{
  "sentence_structure": {{
    "avg_length": <number of words>,
    "variance": "high|medium|low",
    "compression_style": "compressed|flowing|mixed",
    "fragment_usage": "frequent|occasional|rare"
  }},
  "vocabulary": {{
    "formality": "formal|neutral|casual",
    "complexity": "simple|moderate|complex",
    "jargon_domains": ["domain1", "domain2"],
    "distinctive_words": ["word1", "word2", "word3"]
  }},
  "metaphor_style": {{
    "frequency": "high|medium|low",
    "directness": "direct|extended|mixed",
    "primary_domains": ["domain1", "domain2"],
    "examples": ["metaphor1", "metaphor2"]
  }},
  "pov_handling": {{
    "depth": "shallow|medium|deep",
    "filter_words": {{
      "saw": <count>,
      "heard": <count>,
      "felt": <count>,
      "noticed": <count>,
      "thought": <count>,
      "wondered": <count>,
      "realized": <count>
    }},
    "thought_tags": <count of "she thought", "he wondered", etc>,
    "consciousness_immersion": "high|medium|low"
  }},
  "dialogue": {{
    "dialogue_to_narrative_ratio": "<percentage>",
    "dialogue_style": "sparse|balanced|heavy",
    "tag_style": "minimal|standard|varied"
  }},
  "distinctive_traits": [
    "trait 1",
    "trait 2",
    "trait 3"
  ]
}}

Be precise and analytical. This will be used to generate writing quality criteria."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze passage {passage_num}: {e}")
            # Return minimal analysis on error
            return {
                "sentence_structure": {"avg_length": 15, "variance": "medium", "compression_style": "mixed", "fragment_usage": "occasional"},
                "vocabulary": {"formality": "neutral", "complexity": "moderate", "jargon_domains": [], "distinctive_words": []},
                "metaphor_style": {"frequency": "medium", "directness": "mixed", "primary_domains": [], "examples": []},
                "pov_handling": {"depth": "medium", "filter_words": {}, "thought_tags": 0, "consciousness_immersion": "medium"},
                "dialogue": {"dialogue_to_narrative_ratio": "50%", "dialogue_style": "balanced", "tag_style": "standard"},
                "distinctive_traits": []
            }

    async def _synthesize_voice_profile(
        self,
        passage_analyses: List[Dict[str, Any]],
        uploaded_docs: List[Dict[str, Any]],
        notebooklm_context: Optional[str]
    ) -> VoiceProfile:
        """
        Synthesize individual passage analyses into unified voice profile.

        Args:
            passage_analyses: List of passage analysis dictionaries
            uploaded_docs: Uploaded documents with metadata
            notebooklm_context: Context from NotebookLM

        Returns:
            Unified VoiceProfile object
        """

        prompt = f"""Given these {len(passage_analyses)} passage analyses, synthesize a unified voice profile.

PASSAGE ANALYSES:
{json.dumps(passage_analyses, indent=2)}

UPLOADED DOCUMENTS:
{json.dumps([doc.get('summary', '') for doc in uploaded_docs], indent=2)}

NOTEBOOKLM CONTEXT:
{notebooklm_context or 'Not provided'}

Create a comprehensive voice profile:

{{
  "voice_name": "<descriptive name for this voice>",
  "genre": "<detected genre>",
  "primary_characteristics": [
    "characteristic 1 (consistent across all passages)",
    "characteristic 2",
    "characteristic 3"
  ],
  "sentence_structure": {{
    "typical_length": "<avg words>",
    "compression_level": "1-10 scale",
    "preferred_patterns": ["pattern1", "pattern2"]
  }},
  "vocabulary": {{
    "formality_level": "formal|neutral|casual",
    "complexity": "simple|moderate|complex",
    "distinctive_domains": ["domain1", "domain2"]
  }},
  "pov_style": {{
    "depth": "shallow|medium|deep",
    "consciousness_mode_percentage": "<estimated %>",
    "filter_word_tolerance": "strict|moderate|lenient"
  }},
  "voice_consistency_notes": [
    "What's consistent across passages",
    "What varies and why",
    "Potential anti-patterns"
  ]
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            profile_data = json.loads(response_text)
            return VoiceProfile.from_dict(profile_data)

        except Exception as e:
            logger.error(f"Failed to synthesize voice profile: {e}")
            # Return minimal profile on error
            return VoiceProfile(
                voice_name="Unknown Voice",
                genre="Literary Fiction",
                primary_characteristics=["analytical", "descriptive"],
                sentence_structure={"typical_length": "15", "compression_level": "5", "preferred_patterns": []},
                vocabulary={"formality_level": "neutral", "complexity": "moderate", "distinctive_domains": []},
                pov_style={"depth": "medium", "consciousness_mode_percentage": "50%", "filter_word_tolerance": "moderate"}
            )

    async def _extract_metaphor_domains(
        self,
        example_passages: List[str]
    ) -> Dict[str, MetaphorDomain]:
        """
        Identify primary metaphor domains and their usage patterns.

        Returns:
            {
                "domain_name": MetaphorDomain(
                    max_percentage=25,
                    keywords=["word1", "word2"],
                    examples=["metaphor1", "metaphor2"]
                )
            }

        Args:
            example_passages: List of example passage texts

        Returns:
            Dictionary mapping domain name to MetaphorDomain object
        """

        all_text = "\n\n".join(example_passages)

        prompt = f"""Identify the primary metaphor domains in this writing.

TEXT:
{all_text[:5000]}

For each domain, provide:
1. Domain name (e.g., "gambling", "medical", "nature")
2. Frequency (% of metaphors from this domain)
3. Key vocabulary
4. Example metaphors

Return JSON:
{{
  "domains": [
    {{
      "name": "domain_name",
      "frequency_percentage": <number>,
      "max_recommended_percentage": <suggested limit>,
      "keywords": ["word1", "word2", ...],
      "examples": ["full metaphor 1", "full metaphor 2"]
    }}
  ]
}}

Only include domains with 10%+ usage."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)

            metaphor_domains = {}
            for domain in result.get("domains", []):
                metaphor_domains[domain["name"]] = MetaphorDomain(
                    max_percentage=domain["max_recommended_percentage"],
                    keywords=domain["keywords"],
                    examples=domain["examples"]
                )

            return metaphor_domains

        except Exception as e:
            logger.error(f"Failed to extract metaphor domains: {e}")
            return {}

    async def _identify_anti_patterns(
        self,
        example_passages: List[str],
        uploaded_docs: List[Dict[str, Any]]
    ) -> List[AntiPattern]:
        """
        Identify patterns this writer wants to AVOID.

        Analyzes:
        - Patterns present in style guide as "don't do this"
        - Inconsistencies across passages (writer correcting themselves)
        - Common craft issues (filter words, weak similes, etc)

        Args:
            example_passages: List of example passage texts
            uploaded_docs: Uploaded documents (may include style guide)

        Returns:
            List of AntiPattern objects
        """

        # Check for style guide in uploaded docs
        style_guide_content = ""
        for doc in uploaded_docs:
            if "style" in doc.get("filename", "").lower():
                style_guide_content = doc.get("content", "")

        all_text = "\n\n".join(example_passages)

        prompt = f"""Identify anti-patterns this writer should avoid.

EXAMPLE PASSAGES:
{all_text[:4000]}

STYLE GUIDE (if provided):
{style_guide_content[:2000] if style_guide_content else "Not provided"}

Analyze for:
1. Patterns explicitly forbidden in style guide
2. Common craft issues (filter words, thought tags, weak constructions)
3. Voice-specific issues (e.g., similes in compressed prose)
4. Inconsistencies that suggest writer is self-correcting

Return JSON:
{{
  "anti_patterns": [
    {{
      "pattern_id": "snake_case_id",
      "name": "Human-readable name",
      "description": "What this pattern is",
      "why_avoid": "Why it's problematic for THIS voice",
      "detection_method": "regex|keyword|llm",
      "regex": "<if regex detection>",
      "keywords": ["if", "keyword", "detection"],
      "severity": "high|medium|low",
      "examples_from_text": ["example1", "example2"]
    }}
  ]
}}

Be specific to THIS writer's voice."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)

            anti_patterns = []
            for ap in result.get("anti_patterns", []):
                anti_patterns.append(AntiPattern(
                    pattern_id=ap["pattern_id"],
                    name=ap["name"],
                    description=ap["description"],
                    why_avoid=ap["why_avoid"],
                    detection_method=ap["detection_method"],
                    regex=ap.get("regex"),
                    keywords=ap.get("keywords", []),
                    severity=ap["severity"],
                    examples=ap.get("examples_from_text", [])
                ))

            return anti_patterns

        except Exception as e:
            logger.error(f"Failed to identify anti-patterns: {e}")
            return []

    async def _derive_quality_criteria(
        self,
        voice_profile: VoiceProfile,
        genre: str
    ) -> QualityCriteria:
        """
        Derive scoring criteria based on voice + genre.

        Different genres have different priorities:
        - Literary fiction: Voice (40%), Character (25%), Craft (20%)
        - Thriller: Pacing (30%), Tension (25%), Voice (20%)
        - Romance: Emotional beats (30%), Tension (25%), Voice (20%)

        Args:
            voice_profile: Extracted voice profile
            genre: Detected genre

        Returns:
            QualityCriteria object with scoring system
        """

        prompt = f"""Given this voice profile and genre, derive quality scoring criteria.

VOICE PROFILE:
{voice_profile.to_json()}

GENRE: {genre}

Create a 100-point scoring system with 5-7 categories.

Return JSON:
{{
  "total_points": 100,
  "categories": [
    {{
      "category_id": "voice_authenticity",
      "name": "Voice Authenticity",
      "points": 30,
      "description": "How well the scene maintains this specific voice",
      "sub_criteria": [
        {{
          "name": "Sentence compression",
          "points": 10,
          "check": "What to evaluate"
        }},
        {{
          "name": "Vocabulary consistency",
          "points": 10,
          "check": "What to evaluate"
        }},
        {{
          "name": "POV depth",
          "points": 10,
          "check": "What to evaluate"
        }}
      ]
    }},
    {{
      "category_id": "another_category",
      "name": "Category Name",
      "points": 20,
      "description": "Description",
      "sub_criteria": [...]
    }}
  ]
}}

Tailor to THIS voice and genre. Ensure categories sum to 100 points."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            criteria_data = json.loads(response_text)
            return QualityCriteria.from_dict(criteria_data)

        except Exception as e:
            logger.error(f"Failed to derive quality criteria: {e}")
            # Return minimal criteria on error
            return QualityCriteria(
                total_points=100,
                categories=[
                    {
                        "category_id": "voice_authenticity",
                        "name": "Voice Authenticity",
                        "points": 30,
                        "description": "How well the scene maintains the voice",
                        "sub_criteria": []
                    },
                    {
                        "category_id": "character_consistency",
                        "name": "Character Consistency",
                        "points": 20,
                        "description": "Character behavior and voice consistency",
                        "sub_criteria": []
                    },
                    {
                        "category_id": "craft_quality",
                        "name": "Craft Quality",
                        "points": 20,
                        "description": "Technical writing quality",
                        "sub_criteria": []
                    },
                    {
                        "category_id": "scene_structure",
                        "name": "Scene Structure",
                        "points": 15,
                        "description": "Scene pacing and structure",
                        "sub_criteria": []
                    },
                    {
                        "category_id": "metaphor_discipline",
                        "name": "Metaphor Discipline",
                        "points": 15,
                        "description": "Metaphor usage and domain discipline",
                        "sub_criteria": []
                    }
                ]
            )
