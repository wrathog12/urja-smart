"""
Voice Stream Pipeline - The Core Audio Processing Loop
Handles: User Speech → STT → LLM → TTS → Audio Response

Features:
- Sentiment tracking with auto-escalation
- End call tool handling
- Language-aware responses
- Context window (last 5 turns)
"""
import time
import json
import numpy as np
import gradio as gr
from fastrtc import Stream, AdditionalOutputs, ReplyOnPause

# Import the specific service INSTANCES (singleton objects)
from backend.app.services.stt import stt_service
from backend.app.services.llm import llm_service
from backend.app.services.tts import tts_service
from backend.app.tools.handoff import handoff_guard
from backend.app.tools.end_call import end_call_tool
from backend.app.core.prompts import ESCALATION_MESSAGE, END_CALL_MESSAGE

# --- Configuration ---
MIN_CONFIDENCE_THRESHOLD = 0.70  # Reject transcriptions below 70% confidence
MIN_TEXT_LENGTH = 3  # Reject very short transcriptions (likely noise)
ESCALATION_SENTIMENT_THRESHOLD = 0.3  # Auto-escalate if sentiment drops below this

# --- Global Session State (accessible from main.py) ---
session_state = {
    "is_active": False,
    "should_end": False,
    "end_reason": None,
    "last_user_text": "",
    "last_bot_text": "",
    "last_tool": None,
    "last_sentiment": 0.7,
    "sentiment_history": [],
    "metrics": {"stt": 0, "llm": 0, "tts": 0}
}

# --- Chat History (keeps last 5 turns for context) ---
chat_history = []


def reset_session():
    """Reset session state for new conversation."""
    global chat_history, session_state
    chat_history = []
    end_call_tool.reset()
    handoff_guard.strike_count = 0
    session_state.update({
        "is_active": False,
        "should_end": False,
        "end_reason": None,
        "last_user_text": "",
        "last_bot_text": "",
        "last_tool": None,
        "last_sentiment": 0.7,
        "sentiment_history": [],
        "metrics": {"stt": 0, "llm": 0, "tts": 0}
    })


def voice_handler(audio: tuple[int, np.ndarray]):
    """
    The Main Orchestrator Loop. 
    FastRTC calls this whenever the user stops speaking (via ReplyOnPause VAD).
    
    Note on latency: ReplyOnPause has inherent latency because it waits for 
    the user to stop speaking. This is intentional to avoid cutting off users.
    """
    global chat_history, session_state
    
    session_state["is_active"] = True
    start_time = time.perf_counter()

    # 1. THE EARS (STT - Deepgram)
    user_text, confidence = stt_service.stt(audio)
    
    t_stt = time.perf_counter()
    session_state["metrics"]["stt"] = (t_stt - start_time) * 1000
    
    # --- Human-like VAD: Reject low confidence / short transcriptions ---
    if not user_text:
        print("❌ No speech detected")
        yield AdditionalOutputs(
            "⏳ Listening...", 
            session_state.get("last_bot_text", "..."), 
            "None", 
            "❌ No Speech Detected"
        )
        return
    
    if confidence < MIN_CONFIDENCE_THRESHOLD:
        print(f"🔇 Rejected (low confidence): '{user_text}' ({confidence:.2f})")
        yield AdditionalOutputs(
            f"🔇 [Filtered: {user_text[:30]}...]",
            session_state.get("last_bot_text", "..."),
            "None",
            f"⚠️ Low confidence ({confidence:.0%})"
        )
        return
    
    if len(user_text.strip()) < MIN_TEXT_LENGTH:
        print(f"🔇 Rejected (too short): '{user_text}'")
        yield AdditionalOutputs(
            "⏳ Listening...",
            session_state.get("last_bot_text", "..."),
            "None",
            "⚠️ Too short"
        )
        return

    print(f"📝 Transcript: {user_text} (confidence: {confidence:.2f})")
    session_state["last_user_text"] = user_text
    
    # 2. THE GUARD (Handoff Logic - Check for repeated low confidence)
    should_escalate = handoff_guard.check_and_update(confidence)
    
    if should_escalate:
        print("🚨 GUARD TRIGGERED HANDOFF")
        handoff_msg = handoff_guard.get_escalation_message()
        
        yield AdditionalOutputs(user_text, "[HANDOFF]", "{}", "🚨 Escalating")
        
        for audio_chunk in tts_service.generate_audio(handoff_msg):
            yield audio_chunk
        
        session_state["should_end"] = True
        session_state["end_reason"] = "audio_quality_escalation"
        return

    # 3. UPDATE MEMORY (keep last 5 turns = 10 messages)
    chat_history.append({"role": "user", "content": user_text})
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
    
    # 4. THE BRAIN (LLM - Groq/Llama)
    print("🧠 Thinking...")
    speech_text, tool_data, sentiment_score = llm_service.get_response(chat_history)
    
    t_llm = time.perf_counter()
    session_state["metrics"]["llm"] = (t_llm - t_stt) * 1000
    
    print(f"🤖 Bot Reply: {speech_text}")
    print(f"💭 Sentiment: {sentiment_score}")
    
    session_state["last_bot_text"] = speech_text
    session_state["last_sentiment"] = sentiment_score
    session_state["sentiment_history"].append(sentiment_score)
    
    # Format tool data for display
    tool_display = "None"
    if tool_data:
        print(f"🔧 Tool Trigger: {tool_data['name']}")
        tool_display = json.dumps(tool_data, indent=2)
        session_state["last_tool"] = tool_data
        
        # Handle end_call tool
        if tool_data.get("name") == "end_call":
            print("📞 END CALL TRIGGERED")
            result = end_call_tool.execute(tool_data.get("args", {}))
            session_state["should_end"] = True
            session_state["end_reason"] = tool_data.get("args", {}).get("reason", "user_requested")

    # 5. CHECK FOR AUTO-ESCALATION (Low Sentiment)
    if sentiment_score <= ESCALATION_SENTIMENT_THRESHOLD and not (tool_data and tool_data.get("name") == "escalate_to_agent"):
        print(f"😠 LOW SENTIMENT ({sentiment_score}) - Auto-escalating")
        
        yield AdditionalOutputs(
            f"🗣️ {user_text}",
            f"🤖 {ESCALATION_MESSAGE}",
            '{"name": "escalate_to_agent", "args": {"reason": "low_sentiment"}}',
            f"😠 Sentiment: {sentiment_score}"
        )
        
        for audio_chunk in tts_service.generate_audio(ESCALATION_MESSAGE):
            yield audio_chunk
        
        session_state["should_end"] = True
        session_state["end_reason"] = "sentiment_escalation"
        return

    # Update memory with bot's reply
    chat_history.append({"role": "assistant", "content": speech_text})

    # 6. UI UPDATE
    sentiment_emoji = "😊" if sentiment_score >= 0.7 else "😐" if sentiment_score >= 0.5 else "😟"
    latency_msg = f"⚡ STT: {session_state['metrics']['stt']:.0f}ms | LLM: {session_state['metrics']['llm']:.0f}ms | {sentiment_emoji} {sentiment_score:.1f}"
    
    yield AdditionalOutputs(
        f"🗣️ {user_text}",
        f"🤖 {speech_text}",
        tool_display,
        latency_msg
    )

    # 7. THE MOUTH (TTS - Cartesia)
    print("🔊 Speaking...")
    t_tts_start = time.perf_counter()
    
    for i, audio_chunk in enumerate(tts_service.generate_audio(speech_text)):
        if i == 0:
            tts_latency = (time.perf_counter() - t_tts_start) * 1000
            session_state["metrics"]["tts"] = tts_latency
            print(f"⚡ TTS: {tts_latency:.0f}ms")
            
            latency_msg = f"⚡ STT: {session_state['metrics']['stt']:.0f}ms | LLM: {session_state['metrics']['llm']:.0f}ms | TTS: {tts_latency:.0f}ms | {sentiment_emoji}"
            
            yield AdditionalOutputs(
                f"🗣️ {user_text}",
                f"🤖 {speech_text}",
                tool_display,
                latency_msg
            )
        
        yield audio_chunk
    
    print("✅ Response Complete\n")
    
    # If call should end
    if session_state["should_end"]:
        print(f"📞 Call ending: {session_state['end_reason']}")
        session_state["is_active"] = False


# --- Additional Outputs Handler ---
def handle_additional_outputs(
    old_user_text, old_bot_response, old_tool_data, old_latency,
    new_user_text, new_bot_response, new_tool_data, new_latency
):
    """Handler for additional outputs from the stream."""
    return new_user_text, new_bot_response, new_tool_data, new_latency


# --- THE STREAM OBJECT ---
voice_stream = Stream(
    ReplyOnPause(
        voice_handler
    ),
    modality="audio",
    mode="send-receive",
    additional_outputs_handler=handle_additional_outputs,
    additional_outputs=[
        gr.Textbox(label="🎤 Your Speech", lines=2),
        gr.Textbox(label="🤖 Urja's Response", lines=3),
        gr.Code(label="🔧 Tool Activation", language="json"),
        gr.Textbox(label="⚡ Metrics", elem_id="latency-box")
    ]
)