# LLM Agents

This directory contains integrations for various LLM providers.

## Architecture

All agents inherit from `BaseAgent` which provides:
- Standard generation interface
- Automatic token counting
- Cost tracking
- Retry logic with exponential backoff
- Statistics collection

## Supported Providers

### Chinese LLMs

#### Qwen (通义千问) - Alibaba Cloud
- **Models**: qwen-max, qwen-plus, qwen-turbo
- **Strengths**: Multilingual, creative, reasoning
- **API**: DashScope API
- **Docs**: https://help.aliyun.com/zh/dashscope/

#### DeepSeek
- **Models**: deepseek-chat (V3)
- **Strengths**: Extremely cost-effective, fast, creative
- **API**: OpenAI-compatible
- **Docs**: https://platform.deepseek.com/

#### Doubao (豆包) - ByteDance
- **Models**: doubao-pro-32k
- **Strengths**: Cost-effective, Chinese language, dialogue
- **API**: Volcengine (OpenAI-compatible)
- **Docs**: https://www.volcengine.com/docs/82379

#### Baichuan (百川)
- **Models**: Baichuan4
- **Strengths**: Reasoning, professional writing
- **API**: OpenAI-compatible
- **Docs**: https://platform.baichuan-ai.com/

#### Kimi (月之暗面) - Moonshot AI
- **Models**: moonshot-v1-128k
- **Strengths**: Long context (128K tokens)
- **API**: OpenAI-compatible
- **Docs**: https://platform.moonshot.cn/

## Adding a New Agent

### 1. Create Agent Class

Create a new file in the appropriate subdirectory (e.g., `chinese/newagent.py`):

```python
from factory.agents.base_agent import BaseAgent, AgentConfig
import httpx

class NewAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.provider.com/v1"

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Implement API call
        # Return dict with: output, tokens_input, tokens_output, cost, model_version, metadata
        pass
```

### 2. Register in agents.yaml

Add to `factory/core/config/agents.yaml`:

```yaml
new-agent:
  provider: provider_name
  model: model-name
  enabled: true
  context_window: 32000
  max_output: 4000
  cost_per_1k_input: 0.001
  cost_per_1k_output: 0.002
  strengths:
    - strength1
    - strength2
  handler: factory.agents.chinese.newagent.NewAgent
  description: "Description of the agent"
```

### 3. Test the Agent

```python
from factory.agents.chinese.newagent import NewAgent
from factory.agents.base_agent import AgentConfig

config = AgentConfig(
    name="new-agent",
    model="model-name",
    api_key="your_api_key"
)

agent = NewAgent(config)
result = await agent.generate("Hello, world!")
print(result["output"])
```

## API Key Configuration

API keys should be stored in `config/credentials.json`:

```json
{
  "qwen_api_key": "your_qwen_key",
  "deepseek_api_key": "your_deepseek_key",
  "doubao_api_key": "your_doubao_key",
  "baichuan_api_key": "your_baichuan_key",
  "kimi_api_key": "your_kimi_key"
}
```

## Usage Example

```python
from factory.core.agent_pool import AgentPool
from factory.agents.chinese.qwen import QwenAgent
from factory.agents.base_agent import AgentConfig

# Create agent pool
pool = AgentPool()

# Register agents
qwen_config = AgentConfig(
    name="qwen-max",
    model="qwen-max",
    api_key="your_api_key"
)
pool.register_agent("qwen-max", QwenAgent(qwen_config))

# Use agent
result = await pool.execute_single(
    "qwen-max",
    "Write a short story about a robot."
)

print(result.output)
print(f"Cost: ${result.cost:.4f}")
print(f"Tokens: {result.total_tokens}")
```

## Cost Tracking

All agents automatically track:
- Request count
- Total tokens used
- Total cost
- Average tokens per request
- Average cost per request

Access stats with:

```python
stats = agent.get_stats()
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Total tokens: {stats['total_tokens']}")
```

## Error Handling

All agents support automatic retry with exponential backoff:

```python
config = AgentConfig(
    name="agent",
    model="model",
    retry_attempts=3,  # Retry up to 3 times
    retry_delay=1.0,   # Start with 1s delay, exponentially increase
)
```

## Best Practices

1. **Always check API key validity** before making requests
2. **Use appropriate timeouts** for different model speeds
3. **Monitor costs** especially with expensive models
4. **Implement rate limiting** if needed for your use case
5. **Test with small prompts first** to verify integration
6. **Handle API errors gracefully** with proper error messages

## Troubleshooting

### "API key is required" error
- Ensure API key is set in config
- Check credentials.json exists and is valid

### Timeout errors
- Increase timeout in config
- Check network connectivity
- Verify API endpoint is accessible

### Cost discrepancies
- Token counts are estimates for some providers
- Update cost_per_1k values in agents.yaml
- Check provider's pricing page for latest rates

### Import errors
- Ensure httpx is installed: `pip install httpx`
- Check __init__.py files exist in all directories
