![Wizzpert Logo](wizzpert-plugins/assets/logo.png)

# Speech-to-text

This example shows realtime transcription from voice to text.

It uses OpenAI's Whisper STT API, but supports other STT plugins by changing this line:

```python
stt = openai.STT()
```

To render the transcriptions into your client application, refer to the [full documentation](https://docs.wizzpert.io/agents/voice-agent/transcriptions/).

## Running the example

```bash
export wizzpert_URL=wss://yourhost.wizzpert.cloud
export wizzpert_API_KEY=wizzpert-api-key
export wizzpert_API_SECRET=your-api-secret
export OPENAI_API_KEY=your-api-key

python3 transcriber.py start
```

Then connect to any room. For an example frontend, you can use wizzpert's [Agents Playground](https://agents-playground.wizzpert.io/).
