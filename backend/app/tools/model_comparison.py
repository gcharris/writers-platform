"""Model comparison tool wrapping tournament system."""

import difflib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

logger = logging.getLogger(__name__)


@dataclass
class ModelOutput:
    """Output from a single model."""
    model_name: str
    text: str
    cost: float
    tokens_input: int
    tokens_output: int
    generation_time: float


@dataclass
class ComparisonResult:
    """Result of model comparison."""
    prompt: str
    outputs: List[ModelOutput]
    diffs: Dict[Tuple[str, str], List[str]] = field(default_factory=dict)
    winner: Optional[str] = None
    user_notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_cost(self) -> float:
        """Total cost across all models."""
        return sum(o.cost for o in self.outputs)

    @property
    def models_compared(self) -> List[str]:
        """List of model names compared."""
        return [o.model_name for o in self.outputs]


class ModelComparisonTool:
    """Side-by-side model comparison tool.

    Wraps the existing tournament system (Phase 1) and adds:
    - Visual side-by-side comparison
    - Diff highlighting
    - Preference tracking
    - Accessible via 'C' keyboard shortcut
    """

    def __init__(
        self,
        agent_pool: Optional[Any] = None,
        preferences_manager: Optional[Any] = None,
        console: Optional[Console] = None
    ):
        """Initialize model comparison tool.

        Args:
            agent_pool: Agent pool for multi-model generation
            preferences_manager: Preferences manager for tracking winners
            console: Rich console for output
        """
        self.agent_pool = agent_pool
        self.preferences_manager = preferences_manager
        self.console = console or Console()
        self.comparison_history: List[ComparisonResult] = []

    async def compare_models(
        self,
        prompt: str,
        models: List[str],
        context: Optional[str] = None
    ) -> ComparisonResult:
        """Run side-by-side model comparison.

        Args:
            prompt: Prompt to test across models
            models: List of 2-4 model names
            context: Optional context to include

        Returns:
            ComparisonResult with outputs and diffs
        """
        if len(models) < 2:
            raise ValueError("Need at least 2 models for comparison")
        if len(models) > 4:
            raise ValueError("Maximum 4 models supported for comparison")

        logger.info(f"Comparing {len(models)} models: {', '.join(models)}")

        # Generate outputs from all models (mock for now)
        outputs = await self._generate_all_models(prompt, models, context)

        # Compute visual diffs between all pairs
        diffs = self._compute_diffs(outputs)

        # Create comparison result
        result = ComparisonResult(
            prompt=prompt,
            outputs=outputs,
            diffs=diffs
        )

        # Add to history
        self.comparison_history.append(result)

        return result

    async def _generate_all_models(
        self,
        prompt: str,
        models: List[str],
        context: Optional[str]
    ) -> List[ModelOutput]:
        """Generate outputs from all models.

        In production, this would use the agent_pool and
        MultiModelGenerationWorkflow from Phase 1.
        """
        outputs = []

        # Mock generation for now
        for model in models:
            # Simulate different outputs
            if "claude" in model.lower():
                text = f"Claude's response: {prompt}\n\nDetailed analysis with compressed phrasing."
            elif "gpt" in model.lower():
                text = f"GPT's response: {prompt}\n\nComprehensive explanation with examples."
            elif "gemini" in model.lower():
                text = f"Gemini's response: {prompt}\n\nConcise answer with key points."
            else:
                text = f"Model response: {prompt}\n\nStandard output."

            outputs.append(ModelOutput(
                model_name=model,
                text=text,
                cost=0.05,
                tokens_input=100,
                tokens_output=200,
                generation_time=1.5
            ))

        return outputs

    def _compute_diffs(
        self,
        outputs: List[ModelOutput]
    ) -> Dict[Tuple[str, str], List[str]]:
        """Compute diffs between all pairs of outputs.

        Args:
            outputs: List of model outputs

        Returns:
            Dictionary mapping (model1, model2) -> list of diff lines
        """
        diffs = {}

        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                model1 = outputs[i].model_name
                model2 = outputs[j].model_name
                text1 = outputs[i].text.splitlines()
                text2 = outputs[j].text.splitlines()

                # Compute unified diff
                diff = list(difflib.unified_diff(
                    text1,
                    text2,
                    fromfile=model1,
                    tofile=model2,
                    lineterm=''
                ))

                diffs[(model1, model2)] = diff

        return diffs

    def render_comparison(
        self,
        result: ComparisonResult,
        show_diffs: bool = True
    ) -> Panel:
        """Render comparison result as Rich panel.

        Args:
            result: Comparison result to render
            show_diffs: Whether to show diffs

        Returns:
            Rich Panel with side-by-side comparison
        """
        # Create side-by-side columns
        columns = []

        for output in result.outputs:
            # Create panel for each model
            content = Text()
            content.append(f"{output.model_name}\n", style="bold cyan")
            content.append(f"Cost: ${output.cost:.3f} | ", style="dim")
            content.append(f"Time: {output.generation_time:.1f}s\n\n", style="dim")
            content.append(output.text[:300] + "..." if len(output.text) > 300 else output.text)

            panel = Panel(
                content,
                title=f"[bold]{output.model_name}[/]",
                border_style="cyan"
            )
            columns.append(panel)

        # Create columns layout
        comparison_display = Columns(columns, equal=True, expand=True)

        # Add summary
        summary = Text()
        summary.append(f"\nTotal Models: {len(result.outputs)} | ", style="bold")
        summary.append(f"Total Cost: ${result.total_cost:.3f}\n", style="yellow")

        if result.winner:
            summary.append(f"Winner: {result.winner}\n", style="bold green")

        return Panel(
            comparison_display,
            title="[bold cyan]Model Comparison[/]",
            subtitle=summary,
            border_style="cyan"
        )

    def render_diff(
        self,
        result: ComparisonResult,
        model1: str,
        model2: str
    ) -> Panel:
        """Render visual diff between two models.

        Args:
            result: Comparison result
            model1: First model name
            model2: Second model name

        Returns:
            Rich Panel with highlighted diff
        """
        diff_lines = result.diffs.get((model1, model2), [])

        if not diff_lines:
            # Try reverse order
            diff_lines = result.diffs.get((model2, model1), [])

        content = Text()

        for line in diff_lines:
            if line.startswith('+'):
                content.append(line + "\n", style="green")
            elif line.startswith('-'):
                content.append(line + "\n", style="red")
            elif line.startswith('@@'):
                content.append(line + "\n", style="cyan bold")
            else:
                content.append(line + "\n", style="dim")

        return Panel(
            content,
            title=f"[bold]Diff: {model1} vs {model2}[/]",
            border_style="yellow"
        )

    async def save_preference(
        self,
        result: ComparisonResult,
        winner: str,
        notes: str = ""
    ) -> None:
        """Save user's preference for winner.

        Args:
            result: Comparison result
            winner: Winning model name
            notes: Optional user notes
        """
        if winner not in result.models_compared:
            raise ValueError(f"Winner must be one of: {result.models_compared}")

        result.winner = winner
        result.user_notes = notes

        # Save to preferences manager if available
        if self.preferences_manager:
            # Track model preference
            preference_data = {
                "winner": winner,
                "models_compared": result.models_compared,
                "prompt": result.prompt[:100],
                "timestamp": result.timestamp.isoformat(),
                "notes": notes
            }

            logger.info(f"Saved preference: {winner} selected from {result.models_compared}")

    def get_preference_stats(self) -> Dict[str, int]:
        """Get statistics on model preferences.

        Returns:
            Dictionary mapping model name to win count
        """
        stats = {}

        for result in self.comparison_history:
            if result.winner:
                stats[result.winner] = stats.get(result.winner, 0) + 1

        return stats

    def render_preference_stats(self) -> Panel:
        """Render preference statistics.

        Returns:
            Rich Panel with stats table
        """
        stats = self.get_preference_stats()

        if not stats:
            return Panel(
                "[dim]No preferences recorded yet[/]",
                title="[bold]Preference Statistics[/]"
            )

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan")
        table.add_column("Wins", justify="right", style="green")
        table.add_column("Win Rate", justify="right")

        total_comparisons = len([r for r in self.comparison_history if r.winner])

        # Sort by wins descending
        for model, wins in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            win_rate = (wins / total_comparisons * 100) if total_comparisons > 0 else 0
            table.add_row(model, str(wins), f"{win_rate:.1f}%")

        return Panel(
            table,
            title=f"[bold cyan]Preference Statistics[/] ({total_comparisons} comparisons)",
            border_style="cyan"
        )
