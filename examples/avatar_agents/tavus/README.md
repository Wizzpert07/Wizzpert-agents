# wizzpert Tavus Avatar Agent

This example demonstrates how to create a animated avatar using [Tavus](https://platform.tavus.io/).

## Usage

* Update the environment:

```bash
# Tavus Config
export TAVUS_API_KEY="..."
export TAVUS_REPLICA_ID="..."

# OpenAI config (or other models, tts, stt)
export OPENAI_API_KEY="..."

# wizzpert config
export wizzpert_API_KEY="..."
export wizzpert_API_SECRET="..."
export wizzpert_URL="..."
```

* Start the agent worker:

```bash
python examples/avatar_agents/tavus/agent_worker.py dev
```
