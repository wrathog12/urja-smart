import time
import json
import numpy as np
import gradio as gr
from fastapi import FastAPI
from dotenv import load_dotenv

# FastRTC Imports
from fastrtc import Stream, ReplyOnPause, AdditionalOutputs

# Import Your Services
from backend.app.services.stt import stt_service
from backend.app.services.llm import llm_service
from backend.app.services.tts import tts_service

# Load Env Vars
load_dotenv()

# --- Configuration ---
# Confidence threshold for echo/noise rejection (acts as human VAD)
MIN_CONFIDENCE_THRESHOLD = 0.70  # Reject transcriptions below 70% confidence
MIN_TEXT_LENGTH = 3  # Reject very short transcriptions (likely noise)

# --- Global Latency Tracker ---
metrics = {"stt": 0, "llm": 0, "tts": 0}

def conversation_handler(audio: tuple[int, np.ndarray]):
    """
    The Orchestrator Loop - Called automatically when user pauses speaking.
    Uses FastRTC's ReplyOnPause for automatic voice activity detection.
    Supports barge-in: user can interrupt bot's response by speaking.
    """
    global metrics
    start_time = time.perf_counter()

    # 1. STT (Deepgram)
    print("\n🎤 User Speaking...")
    user_text, confidence = stt_service.stt(audio)
    
    t_stt = time.perf_counter()
    metrics["stt"] = (t_stt - start_time) * 1000

    # --- Human-like VAD: Reject low confidence / short transcriptions ---
    # This helps filter out echo from TTS playback and background noise
    if not user_text:
        print("❌ No speech detected")
        yield AdditionalOutputs(
            "⏳ Listening...", 
            "...", 
            "None", 
            "❌ No Speech Detected"
        )
        return
    
    if confidence < MIN_CONFIDENCE_THRESHOLD:
        print(f"🔇 Rejected (low confidence): '{user_text}' ({confidence:.2f} < {MIN_CONFIDENCE_THRESHOLD})")
        yield AdditionalOutputs(
            f"🔇 [Filtered: {user_text[:30]}...]",
            "...",
            "None",
            f"⚠️ Low confidence ({confidence:.0%}) - likely echo/noise"
        )
        return
    
    if len(user_text.strip()) < MIN_TEXT_LENGTH:
        print(f"🔇 Rejected (too short): '{user_text}'")
        yield AdditionalOutputs(
            "⏳ Listening...",
            "...",
            "None",
            "⚠️ Too short - likely noise"
        )
        return

    print(f"📝 Transcript: {user_text} (confidence: {confidence:.2f})")

    # 2. LLM (Groq - Llama 3)
    # Mock history for testing (always fresh conversation)
    fake_history = [{"role": "user", "content": user_text}]
    
    print("🧠 Thinking...")
    speech_text, tool_data = llm_service.get_response(fake_history)
    
    t_llm = time.perf_counter()
    metrics["llm"] = (t_llm - t_stt) * 1000

    print(f"🤖 Bot Reply: {speech_text}")
    
    # Format tool data for display
    if tool_data:
        print(f"🔧 Tool Trigger: {tool_data['name']}")
        tool_display = json.dumps(tool_data, indent=2)
    else:
        tool_display = "None"

    # 3. TTS (Cartesia) & Response
    # Yield AdditionalOutputs FIRST so text updates instantly on UI
    # TTS latency will be updated after first audio chunk arrives
    latency_msg = f"⚡ STT: {metrics['stt']:.0f}ms | LLM: {metrics['llm']:.0f}ms | TTS: ⏳"
    
    yield AdditionalOutputs(
        f"🗣️ {user_text}",         # Box 1: User transcription
        f"🤖 {speech_text}",        # Box 2: Bot response
        tool_display,               # Box 3: Tool data (JSON)
        latency_msg                 # Box 4: Latency stats
    )

    # Now we Stream the Audio
    print("🔊 Speaking...")
    t_tts_start = time.perf_counter()
    tts_latency = 0
    
    # Yield audio chunks as they arrive from Cartesia
    for i, audio_chunk in enumerate(tts_service.generate_audio(speech_text)):
        if i == 0:
            # Measure time to first audio byte (TTFB)
            tts_latency = (time.perf_counter() - t_tts_start) * 1000
            metrics["tts"] = tts_latency
            print(f"⚡ Time to First Audio: {tts_latency:.0f}ms")
            
            # Update UI with complete latency stats
            total_latency = metrics['stt'] + metrics['llm'] + tts_latency
            latency_msg = f"⚡ STT: {metrics['stt']:.0f}ms | LLM: {metrics['llm']:.0f}ms | TTS: {tts_latency:.0f}ms | Total: {total_latency:.0f}ms"
            
            yield AdditionalOutputs(
                f"🗣️ {user_text}",
                f"🤖 {speech_text}",
                tool_display,
                latency_msg
            )
        
        # Yield audio chunk for playback through speakers
        yield audio_chunk
    
    print("✅ Response Complete\n")


# --- Additional Outputs Handler ---
def handle_additional_outputs(
    old_user_text, old_bot_response, old_tool_data, old_latency,
    new_user_text, new_bot_response, new_tool_data, new_latency
):
    """
    Handler for additional outputs from the stream.
    FastRTC passes: (4 current UI values, 4 new values from AdditionalOutputs)
    We return only the NEW values to update the UI.
    """
    return new_user_text, new_bot_response, new_tool_data, new_latency


# --- UI Setup ---
stream = Stream(
    ReplyOnPause(
        conversation_handler,
        # Barge-in enabled by default - user can interrupt by speaking
        # can_interrupt=True  # This is the default
    ),
    modality="audio",
    mode="send-receive",  # We send mic audio, we receive bot audio
    additional_outputs_handler=handle_additional_outputs,
    additional_outputs=[
        gr.Textbox(label="🎤 Your Speech (Deepgram STT)", lines=2),
        gr.Textbox(label="🤖 Bot Response (Llama-3)", lines=3),
        gr.Code(label="🔧 Tool Activation", language="json"),
        gr.Textbox(label="⚡ Latency Metrics", elem_id="latency-box")
    ]
)

app = FastAPI()
stream.mount(app)
gr.mount_gradio_app(app, stream.ui, path="/")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 END-TO-END VOICE AI TEST SYSTEM")
    print("=" * 60)
    print(f"📍 URL: http://localhost:8000")
    print("")
    print("📋 FEATURES:")
    print("   • ReplyOnPause: Auto-detects when you stop speaking")
    print("   • Barge-in: Interrupt the bot by speaking")
    print("   • Live Metrics: STT, LLM, TTS timing displayed")
    print("   • Tool Display: See activated tools in JSON format")
    print(f"   • Echo Filter: Rejects confidence < {MIN_CONFIDENCE_THRESHOLD:.0%}")
    print("")
    print("🎤 Just speak and wait - no buttons needed!")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)