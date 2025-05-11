# wizzpert Agents for Python

Realtime framework for production-grade multimodal and voice AI agents.

See [https://docs.wizzpert.io/agents/](https://docs.wizzpert.io/agents/) for quickstarts, documentation, and examples.

```python
from dotenv import load_dotenv

from wizzpert import agents
from wizzpert.agents import AgentSession, Agent, RoomInputOptions
from wizzpert.plugins import openai

load_dotenv()

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral"
        )
    )

    await session.start(
        room=ctx.room,
        agent=Agent(instructions="You are a helpful voice AI assistant.")
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
```
