"""Cost tracking for AI operations."""

import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional

import aiofiles

from .models import CostData, CostOperation

logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks costs across operations with budget warnings.

    Features:
    - Per-operation cost tracking
    - Daily/weekly/monthly summaries
    - Budget warnings
    - Atomic writes to costs.json
    """

    def __init__(self, session_path: Path):
        """Initialize cost tracker.

        Args:
            session_path: Path to .session directory
        """
        self.session_path = Path(session_path)
        self.costs_file = self.session_path / "costs.json"

        # Load existing cost data
        self.data = self._load_or_create()

    def _load_or_create(self) -> CostData:
        """Load existing cost data or create new."""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, 'r') as f:
                    data_dict = json.load(f)

                    # Convert timestamps
                    if 'operations' in data_dict:
                        for op in data_dict['operations']:
                            if 'timestamp' in op:
                                op['timestamp'] = datetime.fromisoformat(op['timestamp'])

                    # Convert daily_costs dates
                    if 'daily_costs' in data_dict:
                        converted = {}
                        for date_str, daily in data_dict['daily_costs'].items():
                            if 'date' in daily:
                                daily['date'] = date.fromisoformat(daily['date'])
                            converted[date_str] = daily
                        data_dict['daily_costs'] = converted

                    return CostData(**data_dict)
            except Exception as e:
                logger.error(f"Failed to load costs: {e}. Creating new.")

        return CostData()

    async def save(self) -> bool:
        """Save cost data to disk."""
        try:
            temp_path = self.costs_file.with_suffix('.tmp')
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write(self.data.model_dump_json(indent=2))
            temp_path.replace(self.costs_file)
            return True
        except Exception as e:
            logger.error(f"Failed to save costs: {e}")
            return False

    async def log_operation(
        self,
        operation_type: str,
        model_name: str,
        tokens_input: int,
        tokens_output: int,
        cost: float,
        stage: str,
        context: Optional[dict] = None
    ) -> bool:
        """Log a cost operation.

        Args:
            operation_type: Type of operation (generation, enhancement, etc.)
            model_name: Name of model used
            tokens_input: Input tokens
            tokens_output: Output tokens
            cost: Total cost in USD
            stage: Stage where operation occurred
            context: Additional context

        Returns:
            True if logged successfully
        """
        operation = CostOperation(
            timestamp=datetime.now(),
            operation_type=operation_type,
            model_name=model_name,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            stage=stage,
            context=context or {}
        )

        self.data.add_operation(operation)
        await self.save()

        # Check budgets
        if self.data.should_warn("daily"):
            logger.warning("Approaching daily budget limit!")

        return True

    def get_session_cost(self) -> float:
        """Get total cost for current session."""
        return self.data.session_cost

    def get_today_cost(self) -> float:
        """Get total cost for today."""
        return self.data.get_today_cost()

    def get_budget_status(self) -> dict:
        """Get budget status."""
        return {
            "daily": {
                "spent": self.get_today_cost(),
                "budget": self.data.budget_daily,
                "over_budget": self.data.is_over_budget("daily"),
                "should_warn": self.data.should_warn("daily"),
            },
            "session": {
                "spent": self.get_session_cost(),
            }
        }
