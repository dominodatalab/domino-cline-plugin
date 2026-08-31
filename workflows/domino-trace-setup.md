# Domino Trace Setup

Set up GenAI tracing for agent and LLM applications in Domino. Invoke with
`/domino-trace-setup` (optionally with `--framework <openai|anthropic|langchain>`
or `--name <agent-name>`).

## Steps

1. **Check environment requirements** (MLflow 3.2.0, Domino SDK with
   `agents`/`aisystems` support).
2. **Create `tracing_setup.py`** with auto-tracing setup and an evaluator.
3. **Generate an example evaluator** for quality scoring.
4. **Create `config.yaml`** for agent configuration.
5. **Provide example traced-agent code.**

If run with no framework given, ask which of OpenAI/Anthropic/LangChain to use.

## Environment check

Verify before generating files:

```
Checking environment requirements...

MLflow version: 3.2.0 required
Domino SDK: needs agents/aisystems support
LLM SDK (OpenAI/Anthropic/etc.): whichever framework is selected
```

If MLflow is below 3.2.0, tell the user to add to their Dockerfile:
```
RUN pip install mlflow==3.2.0
RUN pip install "dominodatalab[data,aisystems] @ git+https://github.com/dominodatalab/python-domino.git@master"
```

## tracing_setup.py

```python
"""Domino GenAI Tracing Setup

Requirements:
- mlflow==3.2.0
- dominodatalab[data,aisystems] @ git+https://github.com/dominodatalab/python-domino.git@master
"""

import mlflow
from domino.agents.tracing import add_tracing
from domino.agents.logging import DominoRun
import os

def setup_tracing(framework: str = "openai"):
    """
    Enable auto-tracing for LLM framework.

    Args:
        framework: One of 'openai', 'anthropic', 'langchain'
    """
    if framework == "openai":
        mlflow.openai.autolog()
    elif framework == "anthropic":
        mlflow.anthropic.autolog()
    elif framework == "langchain":
        mlflow.langchain.autolog()
    else:
        raise ValueError(f"Unknown framework: {framework}")

    print(f"Enabled {framework} auto-tracing")

def create_evaluator(metrics: list = None):
    """
    Create a basic evaluator function.

    Args:
        metrics: List of metrics to evaluate

    Returns:
        Evaluator function for @add_tracing
    """
    if metrics is None:
        metrics = ["quality_score", "response_length"]

    def evaluator(inputs, output):
        scores = {}

        if isinstance(output, str):
            scores["response_length"] = len(output)
        elif isinstance(output, dict):
            scores["response_length"] = len(str(output))

        # Placeholder for quality score — replace with actual evaluation logic
        scores["quality_score"] = 0.8

        return scores

    return evaluator

default_evaluator = create_evaluator()
```

## config.yaml

```yaml
# Agent Configuration
# Used with DominoRun(agent_config_path="config.yaml")

models:
  primary: gpt-4o-mini
  fallback: gpt-3.5-turbo
  judge: gpt-4o

agents:
  default:
    temperature: 0.7
    max_tokens: 1000

settings:
  retry_count: 3
  timeout_seconds: 30
```

## Example traced agent (example_agent.py)

```python
import mlflow
from domino.agents.tracing import add_tracing
from domino.agents.logging import DominoRun
from openai import OpenAI

mlflow.openai.autolog()
client = OpenAI()

def quality_evaluator(inputs, output):
    return {
        "response_length": len(output.get("response", "")),
        "confidence": output.get("confidence", 0),
    }

@add_tracing(name="my_agent", evaluator=quality_evaluator)
def my_agent(query: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}]
    )

    return {
        "response": response.choices[0].message.content,
        "confidence": 0.9,
        "model": "gpt-4o-mini"
    }

if __name__ == "__main__":
    aggregated_metrics = [
        ("response_length", "mean"),
        ("confidence", "mean"),
    ]

    with DominoRun(
        run_name="example-run",
        agent_config_path="config.yaml",
        custom_summary_metrics=aggregated_metrics
    ) as run:
        queries = [
            "What is machine learning?",
            "Explain neural networks",
            "How does gradient descent work?"
        ]

        for query in queries:
            result = my_agent(query)
            print(f"Q: {query}")
            print(f"A: {result['response'][:100]}...")
            print()

        print(f"Run ID: {run.run_id}")
```

## Framework-specific setup

### OpenAI
```python
import mlflow
mlflow.openai.autolog()

from openai import OpenAI
client = OpenAI()
```

### Anthropic
```python
import mlflow
mlflow.anthropic.autolog()

from anthropic import Anthropic
client = Anthropic()
```

### LangChain
```python
import mlflow
mlflow.langchain.autolog()

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
```

## Viewing traces

After running traced code:

1. Go to **Experiments** in Domino.
2. Find experiment: `tracing-{username}`.
3. Select the run.
4. Click the **Traces** tab.

The trace view shows the span tree (agents, tools, messages), token usage,
latency, and evaluator scores.

## Related

- `/domino-experiment-setup` - Set up traditional ML tracking instead.
- `/domino-app-init` - Initialize a web application.
- `domino-genai-tracing` skill - Deeper reference (decorators, DominoRun,
  evaluators, multi-agent tracing) used alongside this.
