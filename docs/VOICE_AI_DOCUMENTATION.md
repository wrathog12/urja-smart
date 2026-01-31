# Voice AI Customer Service System
## Technical Documentation & Roadmap

**Project:** Assembly AI Voice Customer Service  
**Date:** January 29, 2026  
**Version:** 1.0

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Current Implementation](#current-implementation)
4. [Error Resolution Log](#error-resolution-log)
5. [Future Roadmap](#future-roadmap)
6. [Configuration Reference](#configuration-reference)

---

## System Overview

End-to-end voice AI customer service system with real-time conversation capabilities.

### Pipeline Flow
```
User Speech → STT (Deepgram) → LLM (Groq/Llama-3) → TTS (Cartesia) → Audio Output
```

### Key Features
| Feature | Status | Description |
|---------|--------|-------------|
| ReplyOnPause | ✅ Done | Auto-detects speech end via VAD |
| Barge-in | ✅ Done | User can interrupt bot response |
| Latency Metrics | ✅ Done | STT, LLM, TTS timing displayed |
| Tool Activation | ✅ Done | Shows triggered tools in UI |
| Echo Rejection | ✅ Done | Confidence-based noise filter |

---

## Architecture

### Current Stack
```
┌─────────────────────────────────────────────────────┐
│                    test4.py                          │
│         (FastRTC Stream + Gradio UI)                 │
├─────────────────────────────────────────────────────┤
│  STT Service     │  LLM Service    │  TTS Service   │
│  (Deepgram)      │  (Groq/Llama)   │  (Cartesia)    │
├─────────────────────────────────────────────────────┤
│                  FastAPI Server                      │
│              (uvicorn @ port 8000)                   │
└─────────────────────────────────────────────────────┘
```

### File Structure
```
Assembly AI/
├── test4.py                      # Main test file
├── .env                          # API keys
├── backend/
│   ├── .env                      # Backend API keys
│   └── app/
│       ├── core/
│       │   ├── config.py         # Settings/env loading
│       │   └── prompts.py        # System prompts
│       └── services/
│           ├── stt.py            # Deepgram STT
│           ├── llm.py            # Groq LLM
│           └── tts.py            # Cartesia TTS
└── two/                          # Virtual environment
```

---

## Current Implementation

### STT Service (stt.py)
- **Provider:** Deepgram Nova-3
- **Mode:** Pre-recorded (REST API per turn)
- **Returns:** `(transcript: str, confidence: float)`
- **Language:** Multi-language (Hinglish support)

### LLM Service (llm.py)
- **Provider:** Groq
- **Model:** llama-3.3-70b-versatile
- **Returns:** `(speech_text: str, tool_data: dict|None)`
- **Tool Pattern:** `[TOOL: {...}]` in response

### TTS Service (tts.py)
- **Provider:** Cartesia Sonic-3
- **Sample Rate:** 24,000 Hz
- **Encoding:** PCM Float32
- **Mode:** WebSocket streaming

### Echo Rejection (Human VAD)
```python
MIN_CONFIDENCE_THRESHOLD = 0.70  # Reject < 70%
MIN_TEXT_LENGTH = 3              # Reject short text
```

---

## Error Resolution Log

### 1. TTS Import Path Error
- **Error:** `ModuleNotFoundError: No module named 'app'`
- **Fix:** Changed `from app.core.config` → `from backend.app.core.config`

### 2. STT Return Type Mismatch
- **Error:** Code expected `(text, confidence)` but got `str`
- **Fix:** Updated `stt.py` to return tuple `(transcript, confidence)`

### 3. Missing CARTESIA_API_KEY
- **Error:** `'Settings' object has no attribute 'CARTESIA_API_KEY'`
- **Fix:** Added field to `config.py` and fixed `.env` path resolution

### 4. FastRTC additional_outputs_handler
- **Error:** `additional_outputs_handler must be provided`
- **Fix:** Added handler function with 8 parameters (4 old + 4 new values)

### 5. Audio Array Shape Error
- **Error:** `Expected planar array.shape[0] to equal 1 but got 44100`
- **Fix:** Changed sample rate to 24kHz, removed reshape

### 6. Cartesia voice_id Deprecated
- **Error:** `TtsWebsocket.send() got unexpected keyword argument 'voice_id'`
- **Fix:** Changed to `voice={"mode": "id", "id": voice_id}` format

---

## Future Roadmap

### Phase 1: Handoff System

#### 1.1 User-Requested Handoff
```
User says: "I want to talk to a human" / "Connect me to agent"
→ LLM detects intent
→ Trigger handoff tool
→ Transfer to human agent
```

#### 1.2 Sentiment-Based Handoff
```
User sentiment score (from LLM) < threshold
→ Detect frustration/anger
→ Auto-trigger handoff
→ Notify agent with context
```

**LLM Response Format (Future):**
```json
{
  "speech_text": "...",
  "tool": {...},
  "sentiment_score": 0.3,
  "handoff_recommended": true
}
```

#### 1.3 Confidence-Based Handoff
```
STT confidence < MIN_THRESHOLD for N consecutive turns
→ Likely poor audio quality or language barrier
→ Suggest handoff to human
```

---

### Phase 2: FastRTC Native Integration

#### Goal
Connect each service directly with FastRTC for minimal latency.

#### Current vs. Target Architecture
```
CURRENT:
FastRTC → test4.py (orchestrator) → Services → Response

TARGET:
FastRTC ←→ STT (WebSocket streaming)
FastRTC ←→ LLM (streaming tokens)
FastRTC ←→ TTS (WebSocket streaming)
```

#### Implementation Steps
1. Convert STT to WebSocket streaming (live transcription)
2. Implement LLM token streaming
3. Use Cartesia SSE/WebSocket for TTS
4. Replace ReplyOnPause with custom VAD integration

---

### Phase 3: FastAPI Backend Integration

#### Services to Expose
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversation/start` | POST | Initialize session |
| `/api/conversation/{id}/message` | POST | Send user message |
| `/api/conversation/{id}/stream` | WebSocket | Real-time audio |
| `/api/handoff/{id}` | POST | Trigger handoff |
| `/api/metrics/{id}` | GET | Get latency stats |

#### Frontend Integration
```
React/Next.js Frontend
        ↓
   FastAPI Backend
        ↓
  FastRTC Stream (WebSocket)
        ↓
   STT → LLM → TTS
```

---

## Configuration Reference

### Environment Variables (.env)
```bash
DEEPGRAM_API_KEY=your_key
GROQ_API_KEY=your_key
CARTESIA_API_KEY=your_key
```

### Thresholds (test4.py)
```python
MIN_CONFIDENCE_THRESHOLD = 0.70  # Echo rejection
MIN_TEXT_LENGTH = 3              # Noise rejection
```

### TTS Settings (tts.py)
```python
voice_id = "faf0731e-dfb9-4cfc-8119-259a79b27e12"
model_id = "sonic-3"
sample_rate = 24000
encoding = "pcm_f32le"
```

---

## Quick Commands

```bash
# Activate environment
two/scripts/activate

# Run test
python test4.py

# Access UI
http://localhost:8000
```

---

*Document generated: January 29, 2026*
