<!--BEGIN_BANNER_IMAGE-->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/.github/banner_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="/.github/banner_light.png">
  <img style="width:100%;" alt="The wizzpert icon, the name of the repository and some sample code in the background." src="https://raw.githubusercontent.com/wizzpert/agents/main/.github/banner_light.png">
</picture>

<!--END_BANNER_IMAGE-->

<br />

<img src="wizzpert-plugins/assets/icon.png" alt="Wizzpert Icon" width="100" />

<br /><br />


# Wizzpert Agents for Python

![Wizzpert Logo](wizzpert-plugins/assets/logo.png)

Realtime framework for production-grade multimodal and voice AI agents.

See [https://docs.wizzpert.io/agents/](https://docs.wizzpert.io/agents/) for quickstarts, documentation, and examples.

Looking for the JS/TS library? Check out [AgentsJS](https://github.com/wizzpert/agents-js)

## ✨ 1.0 release ✨

This README reflects the 1.0 release. For documentation on the previous 0.x release, see the [0.x branch](https://github.com/wizzpert/agents/tree/0.x)

## What is Agents?

<!--BEGIN_DESCRIPTION-->

The **Agents framework** enables you to build voice AI agents that can see, hear, and speak in realtime. It provides a fully open-source platform for creating server-side agentic applications.

<!--END_DESCRIPTION-->

## Features

- **Flexible integrations**: A comprehensive ecosystem to mix and match the right STT, LLM, TTS, and Realtime API to suit your use case.
- **Integrated job scheduling**: Built-in task scheduling and distribution with [dispatch APIs](https://docs.wizzpert.io/agents/build/dispatch/) to connect end users to agents.
- **Extensive WebRTC clients**: Build client applications using wizzpert's open-source SDK ecosystem, supporting nearly all major platforms.
- **Telephony integration**: Works seamlessly with wizzpert's [telephony stack](https://docs.wizzpert.io/sip/), allowing your agent to make calls to or receive calls from phones.
- **Exchange data with clients**: Use [RPCs](https://docs.wizzpert.io/home/client/data/rpc/) and other [Data APIs](https://docs.wizzpert.io/home/client/data/) to seamlessly exchange data with clients.
- **Semantic turn detection**: Uses a transformer model to detect when a user is done with their turn, helps to reduce interruptions.
- **Open-source**: Fully open-source, allowing you to run the entire stack on your own servers, including [wizzpert server](https://github.com/wizzpert/wizzpert), one of the most widely used WebRTC media servers.

## Installation

To install the core Agents library, along with plugins for popular model providers:

```bash
pip install "wizzpert-agents[openai,silero,deepgram,cartesia,turn-detector]~=1.0"
```

## Docs and guides

Documentation on the framework and how to use it can be found [here](https://docs.wizzpert.io/agents/)

## Core concepts

- Agent: An LLM-based application with defined instructions.
- AgentSession: A container for agents that manages interactions with end users.
- entrypoint: The starting point for an interactive session, similar to a request handler in a web server.

## Usage

### Simple voice agent

---

```python
from wizzpert.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from wizzpert.plugins import deepgram, openai, silero

@function_tool
async def lookup_weather(
    context: RunContext,
    location: str,
):
    """Used to look up weather information."""

    return {"weather": "sunny", "temperature": 70}


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by wizzpert.",
        tools=[lookup_weather],
    )
    session = AgentSession(
        vad=silero.VAD.load(),
        # any combination of STT, LLM, TTS, or realtime API can be used
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="ash"),
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="greet the user and ask about their day")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

You'll need the following environment variables for this example:

- wizzpert_URL
- wizzpert_API_KEY
- wizzpert_API_SECRET
- DEEPGRAM_API_KEY
- OPENAI_API_KEY

### Multi-agent handoff

---

This code snippet is abbreviated. For the full example, see [multi_agent.py](examples/voice_agents/multi_agent.py)

```python
...
class IntroAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"You are a story teller. Your goal is to gather a few pieces of information from the user to make the story personalized and engaging."
            "Ask the user for their name and where they are from"
        )

    async def on_enter(self):
        self.session.generate_reply(instructions="greet the user and gather information")

    @function_tool
    async def information_gathered(
        self,
        context: RunContext,
        name: str,
        location: str,
    ):
        """Called when the user has provided the information needed to make the story personalized and engaging.

        Args:
            name: The name of the user
            location: The location of the user
        """

        context.userdata.name = name
        context.userdata.location = location

        story_agent = StoryAgent(name, location)
        return story_agent, "Let's start the story!"


class StoryAgent(Agent):
    def __init__(self, name: str, location: str) -> None:
        super().__init__(
            instructions=f"You are a storyteller. Use the user's information in order to make the story personalized."
            f"The user's name is {name}, from {location}"
            # override the default model, switching to Realtime API from standard LLMs
            llm=openai.realtime.RealtimeModel(voice="echo"),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    userdata = StoryData()
    session = AgentSession[StoryData](
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="echo"),
        userdata=userdata,
    )

    await session.start(
        agent=IntroAgent(),
        room=ctx.room,
    )
...
```

## Examples

<table>
<tr>
<td width="50%">
<h3>🎙️ Starter Agent</h3>
<p>A starter agent optimized for voice conversations.</p>
<p>
<a href="examples/voice_agents/basic_agent.py">Code</a>
</p>
</td>
<td width="50%">
<h3>🔄 Multi-user push to talk</h3>
<p>Responds to multiple users in the room via push-to-talk.</p>
<p>
<a href="examples/voice_agents/push_to_talk.py">Code</a>
</p>
</td>
</tr>

<tr>
<td width="50%">
<h3>🎵 Background audio</h3>
<p>Background ambient and thinking audio to improve realism.</p>
<p>
<a href="examples/voice_agents/background_audio.py">Code</a>
</p>
</td>
<td width="50%">
<h3>🛠️ Dynamic tool creation</h3>
<p>Creating function tools dynamically.</p>
<p>
<a href="examples/voice_agents/dynamic_tool_creation.py">Code</a>
</p>
</td>
</tr>

<tr>
<td width="50%">
<h3>☎️ Phone Caller</h3>
<p>Agent that makes outbound phone calls</p>
<p>
<a href="https://github.com/wizzpert-examples/outbound-caller-python">Code</a>
</p>
</td>
<td width="50%">
<h3>📋 Structured output</h3>
<p>Using structured output from LLM to guide TTS tone.</p>
<p>
<a href="examples/voice_agents/structured_output.py">Code</a>
</p>
</td>
</tr>

<tr>
<td width="50%">
<h3>🍽️ Restaurant ordering and reservations</h3>
<p>Full example of an agent that handles calls for a restaurant.</p>
<p>
<a href="examples/full_examples/restaurant_agent/">Code</a>
</p>
</td>
<td width="50%">
<h3>👁️ Gemini Live vision</h3>
<p>Full example (including iOS app) of Gemini Live agent that can see.</p>
<p>
<a href="https://github.com/wizzpert-examples/vision-demo">Code</a>
</p>
</td>
</tr>

</table>

## Running your agent

### Testing in terminal

```shell
python myagent.py console
```

Runs your agent in terminal mode, enabling local audio input and output for testing.
This mode doesn't require external servers or dependencies and is useful for quickly validating behavior.

### Developing with wizzpert clients

```shell
python myagent.py dev
```

Starts the agent server and enables hot reloading when files change. This mode allows each process to host multiple concurrent agents efficiently.

The agent connects to wizzpert Cloud or your self-hosted server. Set the following environment variables:
- wizzpert_URL
- wizzpert_API_KEY
- wizzpert_API_SECRET

You can connect using any wizzpert client SDK or telephony integration.
To get started quickly, try the [Agents Playground](https://agents-playground.wizzpert.io/).

### Running for production

```shell
python myagent.py start
```

Runs the agent with production-ready optimizations.

## Contributing

The Agents framework is under active development in a rapidly evolving field. We welcome and appreciate contributions of any kind, be it feedback, bugfixes, features, new plugins and tools, or better documentation. You can file issues under this repo, open a PR, or chat with us in wizzpert's [Slack community](https://wizzpert.io/join-slack).

<!--BEGIN_REPO_NAV-->

<br/><table>

<thead><tr><th colspan="2">wizzpert Ecosystem</th></tr></thead>
<tbody>
<tr><td>wizzpert SDKs</td><td><a href="https://github.com/wizzpert/client-sdk-js">Browser</a> · <a href="https://github.com/wizzpert/client-sdk-swift">iOS/macOS/visionOS</a> · <a href="https://github.com/wizzpert/client-sdk-android">Android</a> · <a href="https://github.com/wizzpert/client-sdk-flutter">Flutter</a> · <a href="https://github.com/wizzpert/client-sdk-react-native">React Native</a> · <a href="https://github.com/wizzpert/rust-sdks">Rust</a> · <a href="https://github.com/wizzpert/node-sdks">Node.js</a> · <a href="https://github.com/wizzpert/python-sdks">Python</a> · <a href="https://github.com/wizzpert/client-sdk-unity">Unity</a> · <a href="https://github.com/wizzpert/client-sdk-unity-web">Unity (WebGL)</a></td></tr><tr></tr>
<tr><td>Server APIs</td><td><a href="https://github.com/wizzpert/node-sdks">Node.js</a> · <a href="https://github.com/wizzpert/server-sdk-go">Golang</a> · <a href="https://github.com/wizzpert/server-sdk-ruby">Ruby</a> · <a href="https://github.com/wizzpert/server-sdk-kotlin">Java/Kotlin</a> · <a href="https://github.com/wizzpert/python-sdks">Python</a> · <a href="https://github.com/wizzpert/rust-sdks">Rust</a> · <a href="https://github.com/agence104/wizzpert-server-sdk-php">PHP (community)</a> · <a href="https://github.com/pabloFuente/wizzpert-server-sdk-dotnet">.NET (community)</a></td></tr><tr></tr>
<tr><td>UI Components</td><td><a href="https://github.com/wizzpert/components-js">React</a> · <a href="https://github.com/wizzpert/components-android">Android Compose</a> · <a href="https://github.com/wizzpert/components-swift">SwiftUI</a></td></tr><tr></tr>
<tr><td>Agents Frameworks</td><td><b>Python</b> · <a href="https://github.com/wizzpert/agents-js">Node.js</a> · <a href="https://github.com/wizzpert/agent-playground">Playground</a></td></tr><tr></tr>
<tr><td>Services</td><td><a href="https://github.com/wizzpert/wizzpert">wizzpert server</a> · <a href="https://github.com/wizzpert/egress">Egress</a> · <a href="https://github.com/wizzpert/ingress">Ingress</a> · <a href="https://github.com/wizzpert/sip">SIP</a></td></tr><tr></tr>
<tr><td>Resources</td><td><a href="https://docs.wizzpert.io">Docs</a> · <a href="https://github.com/wizzpert-examples">Example apps</a> · <a href="https://wizzpert.io/cloud">Cloud</a> · <a href="https://docs.wizzpert.io/home/self-hosting/deployment">Self-hosting</a> · <a href="https://github.com/wizzpert/wizzpert-cli">CLI</a></td></tr>
</tbody>
</table>
<!--END_REPO_NAV-->
