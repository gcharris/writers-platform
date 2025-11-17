"""Pydantic models for cost tracking."""

from datetime import datetime, date
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class CostOperation(BaseModel):
    """Single cost operation record."""

    timestamp: datetime
    operation_type: str  # "generation", "enhancement", "analysis", "comparison"
    model_name: str
    tokens_input: int
    tokens_output: int
    cost: float
    stage: str  # Which stage this operation was performed in
    context: Dict[str, str] = Field(default_factory=dict)  # Additional context


class DailyCost(BaseModel):
    """Daily cost summary."""

    date: date
    total_cost: float = 0.0
    total_tokens: int = 0
    operations_count: int = 0
    by_model: Dict[str, float] = Field(default_factory=dict)
    by_stage: Dict[str, float] = Field(default_factory=dict)


class CostData(BaseModel):
    """Complete cost tracking data."""

    # Current session costs
    session_cost: float = 0.0
    session_tokens: int = 0

    # Operation history (kept for current session + last 1000)
    operations: List[CostOperation] = Field(default_factory=list)

    # Daily summaries (kept for last 90 days)
    daily_costs: Dict[str, DailyCost] = Field(default_factory=dict)

    # Budget tracking
    budget_daily: Optional[float] = 5.0  # Default $5/day budget
    budget_weekly: Optional[float] = 30.0
    budget_monthly: Optional[float] = 100.0

    # Warnings
    budget_warning_threshold: float = 0.8  # Warn at 80% of budget

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }

    def add_operation(self, operation: CostOperation):
        """Add a new cost operation."""
        self.operations.append(operation)
        self.session_cost += operation.cost
        self.session_tokens += operation.tokens_input + operation.tokens_output

        # Update daily summary
        day_key = operation.timestamp.date().isoformat()
        if day_key not in self.daily_costs:
            self.daily_costs[day_key] = DailyCost(date=operation.timestamp.date())

        daily = self.daily_costs[day_key]
        daily.total_cost += operation.cost
        daily.total_tokens += operation.tokens_input + operation.tokens_output
        daily.operations_count += 1

        # Update by model
        if operation.model_name not in daily.by_model:
            daily.by_model[operation.model_name] = 0.0
        daily.by_model[operation.model_name] += operation.cost

        # Update by stage
        if operation.stage not in daily.by_stage:
            daily.by_stage[operation.stage] = 0.0
        daily.by_stage[operation.stage] += operation.cost

        # Trim old operations (keep last 1000)
        if len(self.operations) > 1000:
            self.operations = self.operations[-1000:]

    def get_today_cost(self) -> float:
        """Get today's total cost."""
        today_key = date.today().isoformat()
        if today_key in self.daily_costs:
            return self.daily_costs[today_key].total_cost
        return 0.0

    def is_over_budget(self, period: str = "daily") -> bool:
        """Check if over budget for given period."""
        if period == "daily":
            budget = self.budget_daily
            cost = self.get_today_cost()
        elif period == "weekly":
            # TODO: Implement weekly calculation
            return False
        elif period == "monthly":
            # TODO: Implement monthly calculation
            return False
        else:
            return False

        if budget is None:
            return False

        return cost >= budget

    def should_warn(self, period: str = "daily") -> bool:
        """Check if should warn about approaching budget."""
        if period == "daily":
            budget = self.budget_daily
            cost = self.get_today_cost()
        else:
            return False

        if budget is None:
            return False

        return cost >= (budget * self.budget_warning_threshold)
