![Wizzpert Logo](wizzpert-plugins/assets/logo.png)

# Gladia plugin for wizzpert Agents

Support for speech-to-text with [Gladia](https://gladia.io/).

See [https://docs.wizzpert.io/agents/integrations/stt/gladia/](https://docs.wizzpert.io/agents/integrations/stt/gladia/) for more information.

## Installation

```bash
pip install wizzpert-plugins-gladia
```

## Pre-requisites

You'll need an API key from Gladia. It can be set as an environment variable: `GLADIA_API_KEY`

## Features

- Streaming speech-to-text
- Multi-language support
- Code-switching between languages
- Interim results (partial transcriptions)
- Voice activity detection with energy filtering
- Optional real-time translation
- Customizable audio parameters (sample rate, bit depth, channels, encoding)

## Example Usage

```python
from wizzpert.stt import STT
from wizzpert.plugins.gladia.stt import STT as GladiaSTT

# Basic initialization
stt = GladiaSTT(
    api_key="your-api-key-here",  # or use GLADIA_API_KEY env var
    interim_results=True
)

# With more options
stt = GladiaSTT(
    languages=["en", "fr"],  # Specify languages or let Gladia auto-detect
    code_switching=True,     # Allow switching between languages during recognition
    sample_rate=16000,       # Audio sample rate in Hz
    bit_depth=16,            # Audio bit depth
    channels=1,              # Number of audio channels
    encoding="wav/pcm",      # Audio encoding format
    energy_filter=True,      # Enable voice activity detection
    translation_enabled=True,
    translation_target_languages=["en"],
    translation_model="base",
    translation_match_original_utterances=True
)

# Update options after initialization
stt.update_options(
    languages=["ja", "en"],
    translation_enabled=True,
    translation_target_languages=["fr"]
)
```

## Using with wizzpert Agents Framework

```python
from wizzpert.agents import Agent
from wizzpert.plugins.gladia.stt import STT as GladiaSTT

agent = Agent(
    stt=GladiaSTT(
        api_key="your-api-key-here",
        languages=["en"],
        translation_enabled=True,
        translation_target_languages=["es"]
    )
)

# Rest of your agent setup...
```
