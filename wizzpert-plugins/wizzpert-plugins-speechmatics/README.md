![Wizzpert Logo](wizzpert-plugins/assets/logo.png)

# Speechmatics STT plugin for wizzpert Agents

Support for Speechmatics STT.

See [https://docs.wizzpert.io/agents/integrations/stt/speechmatics/](https://docs.wizzpert.io/agents/integrations/stt/speechmatics/) for more information.

## Installation

```bash
pip install wizzpert-plugins-speechmatics
```

Usage:

```python
from wizzpert.agents import AgentSession
from wizzpert.plugins.turn_detector.english import EnglishModel
from wizzpert.plugins import speechmatics

agent = AgentSession(
    stt=speechmatics.STT(),
    turn_detector=EnglishModel(),
    min_endpointing_delay=0.5,
    max_endpointing_delay=5.0,
    ...
)
```

Note: The plugin was built with
wizzpert's [end-of-turn detection feature](https://docs.wizzpert.io/agents/v1/build/turn-detection/) in mind,
and it doesn't implement phrase endpointing. `AddTranscript` and `AddPartialTranscript` events are emitted as soon
as they’re received from the Speechmatics STT engine.

## Pre-requisites

You'll need to specify a Speechmatics API Key. It can be set as environment variable `SPEECHMATICS_API_KEY` or
`.env.local` file.
