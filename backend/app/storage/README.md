# Storage & Analytics

SQLite database for tracking sessions, results, costs, and analytics.

## Database Schema

### Tables
- **sessions**: Workflow execution sessions
- **results**: Generation results from agents
- **scores**: Quality scores for results
- **winners**: Selected winning results
- **agent_stats**: Agent performance statistics
- **cost_tracking**: Detailed cost tracking

### Views
- **v_agent_performance**: Agent performance metrics
- **v_session_costs**: Session-level cost summary
- **v_agent_win_rates**: Agent win rates
- **v_daily_costs**: Daily cost breakdown

## Usage

```python
from factory.storage.database import Database

# Initialize database
db = Database(".factory/analytics.db")

# Insert session
db.insert_session(
    session_id="session-123",
    workflow_name="multi-model-generation",
    status="running"
)

# Insert result
db.insert_result(
    result_id="result-456",
    session_id="session-123",
    agent_name="claude-sonnet-4.5",
    prompt="Write a scene...",
    output="Generated text...",
    tokens_input=100,
    tokens_output=500,
    cost=0.015,
    response_time_ms=2500,
    model_version="claude-sonnet-4-5-20250929"
)

# Get analytics
stats = db.get_agent_stats("claude-sonnet-4.5")
print(f"Average cost: ${stats[0]['avg_cost']:.4f}")

# Get session results
results = db.get_session_results("session-123")
for result in results:
    print(f"{result['agent_name']}: {result['cost']}")
```

## Analytics Queries

### Agent Performance
```python
# Get all agent statistics
stats = db.get_agent_stats()
for stat in stats:
    print(f"{stat['agent_name']}: {stat['total_generations']} generations, ${stat['avg_cost']:.4f} avg")
```

### Cost Tracking
```python
# Daily costs
costs = db.get_daily_costs(days=30)
for day in costs:
    print(f"{day['date']}: ${day['total_cost']:.2f} ({day['num_requests']} requests)")

# Session costs
sessions = db.get_session_costs(limit=10)
for session in sessions:
    print(f"{session['workflow_name']}: ${session['total_cost']:.2f}")
```

### Win Rates
```python
# Get agent win rates
win_rates = db.get_agent_win_rates()
for agent in win_rates:
    print(f"{agent['agent_name']}: {agent['win_rate']:.1%} ({agent['wins']}/{agent['total_sessions']})")
```

## Maintenance

```python
# Cleanup old sessions (keep last 90 days)
deleted = db.cleanup_old_sessions(days=90)
print(f"Deleted {deleted} old sessions")

# Close connection
db.close()
```
