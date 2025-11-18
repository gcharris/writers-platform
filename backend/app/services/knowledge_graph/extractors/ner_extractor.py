"""
Fast NER-based extraction using spaCy.
Fallback for when LLM extraction is too slow/expensive.
"""

import logging
from typing import List, Optional
import re

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from ..models import Entity, EntityType

logger = logging.getLogger(__name__)


class NERExtractor:
    """Fast entity extraction using spaCy NER."""

    def __init__(self):
        """Initialize spaCy model."""
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_lg")

        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.warning("en_core_web_lg not found, trying en_core_web_sm...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("No spaCy model found. Run: python -m spacy download en_core_web_sm")
                raise

    def extract_entities(self, scene_content: str, scene_id: str) -> List[Entity]:
        """
        Extract entities using spaCy NER.

        Faster than LLM but less accurate. Good for:
        - Quick extraction
        - Large volumes of text
        - Cost-sensitive scenarios
        """
        doc = self.nlp(scene_content)

        entities = []
        seen_names = set()

        for ent in doc.ents:
            # Skip duplicates
            if ent.text in seen_names:
                continue
            seen_names.add(ent.text)

            # Map spaCy types to our types
            entity_type = self._map_spacy_type(ent.label_)
            if not entity_type:
                continue

            # Get context sentence for description
            description = self._get_entity_context(ent, doc)

            entity = Entity(
                id=self._create_entity_id(ent.text),
                name=ent.text,
                entity_type=entity_type,
                description=description,
                first_appearance=scene_id,
                appearances=[scene_id],
                mentions=1,
                confidence=0.7  # Lower confidence for NER
            )
            entities.append(entity)

        logger.info(f"NER extracted {len(entities)} entities from scene {scene_id}")
        return entities

    def _map_spacy_type(self, spacy_label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our entity types."""
        mapping = {
            'PERSON': EntityType.CHARACTER,
            'GPE': EntityType.LOCATION,  # Geopolitical entity
            'LOC': EntityType.LOCATION,
            'FAC': EntityType.LOCATION,  # Facility
            'ORG': EntityType.ORGANIZATION,
            'EVENT': EntityType.EVENT,
            'PRODUCT': EntityType.OBJECT,
            'WORK_OF_ART': EntityType.OBJECT,
        }
        return mapping.get(spacy_label)

    def _get_entity_context(self, ent, doc) -> str:
        """Extract context sentence for entity description."""
        # Find the sentence containing this entity
        for sent in doc.sents:
            if ent.start >= sent.start and ent.end <= sent.end:
                # Return the sentence as context
                return sent.text.strip()
        return f"Extracted from scene context"

    def _create_entity_id(self, name: str) -> str:
        """Create normalized entity ID."""
        normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        return f"entity_{normalized}"
