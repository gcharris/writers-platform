"""Creation Wizard - guided story development process."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WizardPhase(Enum):
    """Wizard phases following 15-beat narrative structure."""
    FOUNDATION = "foundation"  # Genre, theme, concept
    CHARACTER = "character"    # Protagonist development
    PLOT = "plot"             # 15-beat structure
    WORLD = "world"           # Setting and context
    SYMBOLISM = "symbolism"   # Deeper layers


@dataclass
class WizardResult:
    """Result from wizard completion."""
    story_bible: str
    responses: Dict[str, str] = field(default_factory=dict)
    phase_completed: WizardPhase = WizardPhase.FOUNDATION
    word_count: int = 0
    completed_at: Optional[datetime] = None


class CreationWizard:
    """Conversational wizard for story development.

    Guides writers through 5 phases:
    1. Foundation - Genre, theme, concept
    2. Character - Protagonist and supporting cast
    3. Plot - 15-beat narrative structure
    4. World - Setting and context
    5. Symbolism - Deeper thematic layers

    Outputs 4,000-6,000 word story bible.
    """

    STORY_BEATS = [
        "Opening Image",
        "Theme Stated",
        "Setup",
        "Catalyst",
        "Debate",
        "Break into Two",
        "B Story",
        "Fun and Games",
        "Midpoint",
        "Bad Guys Close In",
        "All Is Lost",
        "Dark Night of the Soul",
        "Break into Three",
        "Finale",
        "Final Image"
    ]

    def __init__(self, project_path: Path):
        """Initialize wizard.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.responses: Dict[str, str] = {}
        self.current_phase = WizardPhase.FOUNDATION
        
    def get_phase_questions(self, phase: WizardPhase) -> List[str]:
        """Get questions for a phase.
        
        Args:
            phase: Wizard phase
            
        Returns:
            List of questions for the phase
        """
        questions = {
            WizardPhase.FOUNDATION: [
                "Why are you writing this novel? (mindset check)",
                "What genre best fits your story?",
                "In one sentence, what is your story about?",
                "What is the core theme or message?",
                "Who is your target audience?"
            ],
            WizardPhase.CHARACTER: [
                "Who is your protagonist?",
                "What does your protagonist want?",
                "What does your protagonist need (internally)?",
                "What is their greatest flaw or wound?",
                "Who are the key supporting characters?"
            ],
            WizardPhase.PLOT: [
                f"Describe: {beat}" for beat in self.STORY_BEATS[:5]
            ],
            WizardPhase.WORLD: [
                "When and where does your story take place?",
                "What are the rules of your story world?",
                "What cultural/social context is important?",
                "What visual details define your world?"
            ],
            WizardPhase.SYMBOLISM: [
                "What objects or images carry symbolic meaning?",
                "What deeper philosophical questions does your story explore?",
                "What allegorical layers exist in your narrative?"
            ]
        }
        
        return questions.get(phase, [])
    
    def record_response(self, question: str, answer: str) -> None:
        """Record a response.
        
        Args:
            question: The question asked
            answer: User's answer
        """
        self.responses[question] = answer
        logger.info(f"Recorded response for: {question[:50]}...")
    
    def advance_phase(self) -> bool:
        """Advance to next phase.
        
        Returns:
            True if advanced, False if already at final phase
        """
        phases = list(WizardPhase)
        current_idx = phases.index(self.current_phase)
        
        if current_idx < len(phases) - 1:
            self.current_phase = phases[current_idx + 1]
            return True
        return False
    
    def generate_story_bible(self) -> WizardResult:
        """Generate complete story bible from responses.
        
        Returns:
            WizardResult with formatted story bible
        """
        bible_sections = []
        
        # Title
        bible_sections.append("# Story Bible")
        bible_sections.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        # Foundation
        bible_sections.append("## Part 1: Foundation")
        for q, a in self.responses.items():
            if any(word in q.lower() for word in ["genre", "theme", "about", "audience"]):
                bible_sections.append(f"\n**{q}**")
                bible_sections.append(f"{a}\n")
        
        # Character
        bible_sections.append("\n## Part 2: Character Development")
        for q, a in self.responses.items():
            if any(word in q.lower() for word in ["protagonist", "character", "want", "need", "flaw"]):
                bible_sections.append(f"\n**{q}**")
                bible_sections.append(f"{a}\n")
        
        # Plot Structure
        bible_sections.append("\n## Part 3: Plot Structure (15-Beat Narrative)")
        for beat in self.STORY_BEATS:
            beat_key = f"Describe: {beat}"
            if beat_key in self.responses:
                bible_sections.append(f"\n### {beat}")
                bible_sections.append(f"{self.responses[beat_key]}\n")
        
        # World Building
        bible_sections.append("\n## Part 4: World & Context")
        for q, a in self.responses.items():
            if any(word in q.lower() for word in ["place", "world", "rules", "cultural", "visual"]):
                bible_sections.append(f"\n**{q}**")
                bible_sections.append(f"{a}\n")
        
        # Symbolism
        bible_sections.append("\n## Part 5: Symbolic & Thematic Layers")
        for q, a in self.responses.items():
            if any(word in q.lower() for word in ["symbolic", "philosophical", "allegorical"]):
                bible_sections.append(f"\n**{q}**")
                bible_sections.append(f"{a}\n")
        
        # Writing Guidelines
        bible_sections.append("\n## Part 6: Writing Guidelines")
        bible_sections.append("\n**Voice & Style**")
        bible_sections.append("- Show, don't tell")
        bible_sections.append("- Compressed phrasing")
        bible_sections.append("- Embedded philosophy")
        bible_sections.append("- 3-dimensional characters\n")
        
        story_bible = "\n".join(bible_sections)
        word_count = len(story_bible.split())
        
        return WizardResult(
            story_bible=story_bible,
            responses=self.responses.copy(),
            phase_completed=self.current_phase,
            word_count=word_count,
            completed_at=datetime.now()
        )
    
    def save_story_bible(self, result: WizardResult, filename: str = "story_bible.md") -> Path:
        """Save story bible to file.
        
        Args:
            result: Wizard result
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.project_path / filename
        output_path.write_text(result.story_bible)
        logger.info(f"Saved story bible to {output_path} ({result.word_count} words)")
        return output_path
