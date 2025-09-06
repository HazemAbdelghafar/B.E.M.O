# Networks in BEMO

## Communication stack, security, and data flow

Internal module-to-module messaging uses Paho-MQTT with a local Mosquitto broker and MQTT QoS = 1 (at-least-once delivery) to ensure reliable delivery with minimal overhead. Because the broker is local, pub/sub latencies are effectively real-time (millisecond-level; typically <5–10 ms for small payloads on localhost/edge setups), making MQTT a low-latency control plane for perception, dialog state, and actuation. External messaging (robot ↔ server ↔ app) runs over secure WebSockets (wss) for low-latency, full-duplex streams, through a free tier Render-hosted relay: all traffic is forwarded by the relay and remains TLS-encrypted and authenticated. Relaying adds measurable latency (community/free tiers typically show median round-trip times ≈ 500–700 ms, while paid/professional tiers can reduce p50 to ≈ 100–200 ms and improve p90), but provides robust NAT/firewall traversal, centralized auth/TLS termination, unified logging/metrics, managed retries/buffering, region-based routing, and much simpler client implementations that simplify deployment and debugging.

### Useful links / citations

-   Eclipse Paho (Python client). [https://eclipse.dev/paho/files/paho.mqtt.python/html/](https://eclipse.dev/paho/files/paho.mqtt.python/html/)
-   Eclipse Mosquitto (broker). [https://mosquitto.org/](https://mosquitto.org/)
-   MQTT QoS explanation (HiveMQ). [https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/](https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/)
-   WebSocket overview (MDN / RFC). [https://developer.mozilla.org/en-US/docs/Web/API/WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
-   Deploying WebSocket services on Render (how-to & notes). [https://websockets.readthedocs.io/en/12.0/howto/render.html](https://websockets.readthedocs.io/en/12.0/howto/render.html)

---

## LLM calls and failure handling

All conversational inference is executed through LangChain with the Google Gemini API, with no on-device LLM fallback maintained. LLM calls are monitored against conservative thresholds of 200 ms RTT and ≤2% packet loss; conditions worse than these are flagged as degraded, and a call is marked as failed if it exceeds 60 s timeout or hits 2 retry attempts (LangChain’s built-in retry/backoff policy). When such failures occur, users receive actionable error messages, a visible offline indicator in the UI, and cached fallback responses for frequent queries (e.g., greetings, simple reminders), ensuring continuity despite connectivity loss. For persistent WebSocket channels we allow up to 10 reconnection attempts with a 10 s retry interval, while heartbeat pings every 10 s require a pong within 5 s; if no pong arrives, the link is declared stalled in ≈5 s and triggers immediate reconnection or graceful error handling. These measures keep conversation flow smooth while making reliability transparent to the user.

### Useful links / citations

-   LangChain – Google Gemini integration. [https://python.langchain.com/api_reference/google_genai/index.html](https://python.langchain.com/api_reference/google_genai/index.html)
-   ITU-T Recommendation G.114 — _One-way transmission time (delay) guidance_. [https://www.itu.int/rec/T-REC-G.114](https://www.itu.int/rec/T-REC-G.114)
-   RFC 6455 — _The WebSocket Protocol_. [https://datatracker.ietf.org/doc/html/rfc6455](https://datatracker.ietf.org/doc/html/rfc6455)
-   Python websockets — ping interval / ping timeout reference. [https://websockets.readthedocs.io/en/stable/reference/sync/client.html](https://websockets.readthedocs.io/en/stable/reference/sync/client.html)
-   WebSocket pings & pongs (MDN). [https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers)
-   Cisco QoS guidelines on delay, jitter, and loss. [https://www.cisco.com/c/en/us/support/docs/availability/high-availability/24121-saa.html](https://www.cisco.com/c/en/us/support/docs/availability/high-availability/24121-saa.html)

---

## Server & robot API calls

On the robot, only a single local API is used: Python's Edge TTS library, which in testing produced audible responses with first-byte latencies of 0.3–2.0 s depending on utterance length (short prompts approach real time). If a request exceeds 3 s or if the robot is offline, the system falls back to an offline TTS model (LJSpeech/Tacotron2-DDC_ph), which synthesizes cached error messages. All other integrations occur on the server and are HTTPS/TLS-secured: LangChain’s Gemini API calls (task classification, QA, reasoning) typically return in 0.7–2.5 s; Tavily (HTTPS SDK) adds ≈0.5–1.0 s to fetch learning resources or answer general questions; TinyTuya via the Tuya Cloud responds in ≈1–2 s; and Google APIs (Todo, Gmail) as well as Microsoft MSAL (Outlook/Hotmail) use OAuth2 for authentication, where short-lived access tokens and secure refresh flows protect user credentials. Average API latencies for these calls are ≈0.5–1.0 s. All tokens and secrets are securely hashed on the server, API keys are stored as environment variables, and enforced free-tier Gemini limits (10 requests/minute, 250k tokens/minute) are respected to avoid rate-limit errors.

### Useful links / citations

-   Python Edge TTS library. [https://github.com/rany2/edge-tts](https://github.com/rany2/edge-tts)
-   NVIDIA Tacotron2 / LJSpeech pretrained offline TTS model. [https://huggingface.co/speechbrain/tts-tacotron2-ljspeech](https://huggingface.co/speechbrain/tts-tacotron2-ljspeech)
-   LangChain – Google Gemini integration. [https://python.langchain.com/api_reference/google_genai/index.html](https://python.langchain.com/api_reference/google_genai/index.html)
-   Tavily API (Python SDK). [https://python.langchain.com/api_reference/tavily/index.html](https://python.langchain.com/api_reference/tavily/index.html)
-   TinyTuya (Python Tuya API). [https://github.com/jasonacox/tinytuya](https://github.com/jasonacox/tinytuya)
-   Google API Client (Python). [https://github.com/googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client)
-   Microsoft Authentication Library (MSAL) for Python. [https://github.com/AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
-   OAuth 2.0 Framework (RFC 6749). [https://datatracker.ietf.org/doc/html/rfc6749](https://datatracker.ietf.org/doc/html/rfc6749)
-   Gemini API limits. [https://ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)
