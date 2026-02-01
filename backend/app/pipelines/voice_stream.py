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
from datetime import datetime
from fastrtc import Stream, AdditionalOutputs, ReplyOnPause

# Import the specific service INSTANCES (singleton objects)
from backend.app.services.stt import stt_service
from backend.app.services.llm import llm_service
from backend.app.services.tts import tts_service
from backend.app.tools.handoff import handoff_guard
from backend.app.tools.end_call import end_call_tool
from backend.app.tools.battery import station_tool
from backend.app.tools.knowledge_base import knowledge_tool
from backend.app.tools.invoice import invoice_tool
from backend.app.core.prompts import ESCALATION_MESSAGE, END_CALL_MESSAGE, SALES_PITCH

# --- Configuration ---
MIN_CONFIDENCE_THRESHOLD = 0.70  # Reject transcriptions below 70% confidence
MIN_TEXT_LENGTH = 3  # Reject very short transcriptions (likely noise)
ESCALATION_SENTIMENT_THRESHOLD = 0.3  # Auto-escalate if sentiment drops below this

# --- Barge-In Configuration ---
MIN_AUDIO_ENERGY = 800       # Minimum energy to even consider audio
BARGE_IN_ENERGY = 1500       # Higher threshold for interrupting during TTS
BARGE_IN_CHUNKS_REQUIRED = 3 # Must sustain for 3 chunks (~1.5 sec) to interrupt

# --- Global Session State (accessible from main.py) ---
session_state = {
    "is_active": False,
    "is_speaking": False,  # True while TTS is playing
    "should_end": False,
    "end_reason": None,
    "last_user_text": "",
    "last_bot_text": "",
    "last_tool": None,
    "last_sentiment": 0.7,
    "sentiment_history": [],
    "metrics": {"stt": 0, "llm": 0, "tts": 0},
    "service_resolved": False,
    "pitch_offered": False,
    "barge_in_counter": 0,  # Track consecutive high-energy chunks for barge-in
    "customer_phone": None,  # Customer phone number for callback
    "customer_name": None    # Customer name if collected
}

# --- Chat History (keeps last 5 turns for context) ---
chat_history = []

# --- Full Conversation History (for escalation with metadata) ---
conversation_history = []  # Stores {sender, text, confidence, timestamp, tool}


def reset_session():
    """Reset session state for new conversation."""
    global chat_history, session_state, conversation_history
    chat_history = []
    conversation_history = []  # Reset full history too
    end_call_tool.reset()
    invoice_tool.reset()
    handoff_guard.strike_count = 0
    session_state.update({
        "is_active": False,
        "is_speaking": False,
        "should_end": False,
        "end_reason": None,
        "last_user_text": "",
        "last_bot_text": "",
        "last_tool": None,
        "last_sentiment": 0.7,
        "sentiment_history": [],
        "metrics": {"stt": 0, "llm": 0, "tts": 0},
        "service_resolved": False,
        "pitch_offered": False,
        "barge_in_counter": 0,
        "customer_phone": None,
        "customer_name": None
    })


def get_conversation_history():
    """Get full conversation history for escalation display."""
    global conversation_history
    return conversation_history


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
    
    # --- AUDIO ENERGY GATE: Reject quiet background noise ---
    sample_rate, audio_data = audio
    audio_energy = np.abs(audio_data).mean()
    
    if audio_energy < MIN_AUDIO_ENERGY:
        print(f"🔇 Rejected: Audio too quiet (energy: {audio_energy:.0f} < {MIN_AUDIO_ENERGY})")
        return
    
    print(f"🎙️ Audio accepted (energy: {audio_energy:.0f})")

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
    
    # Record user message in full conversation history (for escalation)
    conversation_history.append({
        "sender": "user",
        "text": user_text,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
        "tool": None
    })
    
    # 2. THE GUARD (Handoff Logic - Check for repeated low confidence)
    should_escalate = handoff_guard.check_and_update(confidence)
    
    if should_escalate:
        print("🚨 GUARD TRIGGERED HANDOFF - LOW AUDIO QUALITY")
        handoff_msg = handoff_guard.get_escalation_message()
        
        # Record escalation message in conversation history
        conversation_history.append({
            "sender": "bot",
            "text": handoff_msg,
            "confidence": None,
            "timestamp": datetime.now().isoformat(),
            "tool": "escalate_to_agent",
            "sentiment": None
        })
        
        # Send proper tool JSON so frontend can trigger escalation
        escalation_tool = json.dumps({
            "name": "escalate_to_agent",
            "args": {"reason": "audio_quality_escalation"}
        })
        
        yield AdditionalOutputs(user_text, handoff_msg, escalation_tool, "🚨 Escalating - Audio Quality")
        
        for audio_chunk in tts_service.generate_audio(handoff_msg):
            yield audio_chunk
        
        session_state["should_end"] = True
        session_state["end_reason"] = "audio_quality_escalation"
        session_state["is_active"] = False
        print("🚨 Bot stopped - Audio quality escalation complete")
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
    
    # Format tool data for display (compact JSON for frontend parsing)
    tool_display = "None"
    tool_name = None
    if tool_data:
        print(f"🔧 Tool Trigger: {tool_data['name']}")
        tool_display = json.dumps(tool_data)  # Compact JSON for frontend
        tool_name = tool_data.get("name")
        session_state["last_tool"] = tool_data
        
        try:
            # Handle end_call tool
            if tool_data.get("name") == "end_call":
                print("📞 END CALL TRIGGERED")
                result = end_call_tool.execute(tool_data.get("args", {}))
                session_state["should_end"] = True
                session_state["end_reason"] = tool_data.get("args", {}).get("reason", "user_requested")
            
            # Handle get_nearest_station tool
            elif tool_data.get("name") == "get_nearest_station":
                print("📍 NEAREST STATION TOOL TRIGGERED")
                result = station_tool.find_nearest_stations()
                print(f"📍 Station tool result: {result.get('best_station', {}).get('name', 'No station')}")
                # Replace LLM placeholder with actual station data response
                speech_text = result["speech"]
                print(f"📍 New speech_text: {speech_text[:100]}...")
                session_state["last_bot_text"] = speech_text
                session_state["station_data"] = result
                session_state["service_resolved"] = True
            
            # Handle search_knowledge_base tool
            elif tool_data.get("name") == "search_knowledge_base":
                query = tool_data.get("args", {}).get("query", "")
                print(f"📚 KNOWLEDGE BASE TOOL TRIGGERED: {query}")
                result = knowledge_tool.search(query)
                print(f"📚 KB result found: {result.get('found', False)}")
                speech_text = result["speech"]
                session_state["last_bot_text"] = speech_text
            
            # Handle show_directions tool - triggers map popup on frontend
            elif tool_data.get("name") == "show_directions":
                print("🗺️ SHOW DIRECTIONS TOOL TRIGGERED")
                # Get the best station from session state (set by get_nearest_station)
                station_data = session_state.get("station_data", {})
                best_station = station_data.get("best_station")
                
                if best_station:
                    speech_text = f"Main aapko {best_station.get('name', 'station').split(' - ')[-1]} ka raasta dikha rahi hu. Map open ho raha hai."
                else:
                    speech_text = "Ek second, main aapko map dikha rahi hu jisme saare stations hain."
                
                session_state["last_bot_text"] = speech_text
                session_state["show_map_popup"] = True  # Flag for frontend
                print(f"🗺️ Speech: {speech_text}")
            
            # Handle get_invoice tool (multi-turn)
            elif tool_data.get("name") == "get_invoice":
                action = tool_data.get("args", {}).get("action", "initiate")
                print(f"🧾 INVOICE TOOL TRIGGERED: action={action}")
                
                if action == "initiate":
                    result = invoice_tool.initiate()
                elif action == "provide_id":
                    driver_id = tool_data.get("args", {}).get("driver_id", "")
                    result = invoice_tool.receive_id(driver_id)
                elif action == "confirm":
                    confirmed = tool_data.get("args", {}).get("confirmed", False)
                    result = invoice_tool.confirm(confirmed)
                elif action == "get_penalty":
                    result = invoice_tool.get_penalty_details()
                elif action == "get_swaps":
                    result = invoice_tool.get_swap_details()
                elif action == "get_summary":
                    result = invoice_tool.get_summary()
                else:
                    result = {"speech": "Maaf kijiye, kuch problem hai. Kya aap phir se try karenge?"}
                
                print(f"🧾 Invoice result: state={result.get('state', 'unknown')}, action={result.get('action', 'unknown')}")
                speech_text = result["speech"]
                session_state["last_bot_text"] = speech_text
                session_state["invoice_data"] = result
            
            # Handle escalate_to_agent tool - STOP BOT IMMEDIATELY
            elif tool_data.get("name") == "escalate_to_agent":
                escalation_reason = tool_data.get("args", {}).get("reason", "agent_requested")
                print(f"🚨 ESCALATION TRIGGERED: {escalation_reason}")
                
                # Record bot message for escalation
                conversation_history.append({
                    "sender": "bot",
                    "text": speech_text,
                    "confidence": None,
                    "timestamp": datetime.now().isoformat(),
                    "tool": "escalate_to_agent",
                    "sentiment": sentiment_score
                })
                
                # Send the escalation message via TTS, then stop
                yield AdditionalOutputs(
                    f"🗣️ {user_text}",
                    f"🤖 {speech_text}",
                    tool_display,
                    f"🚨 Escalating: {escalation_reason}"
                )
                
                for audio_chunk in tts_service.generate_audio(speech_text):
                    yield audio_chunk
                
                # Mark session as ended due to escalation
                session_state["should_end"] = True
                session_state["end_reason"] = f"escalation_{escalation_reason}"
                session_state["is_active"] = False
                print("🚨 Bot stopped - Escalation complete")
                return  # EXIT IMMEDIATELY - Don't continue processing
        
        except Exception as e:
            print(f"❌ TOOL ERROR: {e}")
            speech_text = "Maaf kijiye, mujhe kuch technical problem aa rahi hai. Kya aap phir se bata sakte hain?"
    
    print(f"🔄 Flow check: After tools, before escalation. speech_text length: {len(speech_text)}")

    # 5. CHECK FOR AUTO-ESCALATION (Low Sentiment)
    if sentiment_score <= ESCALATION_SENTIMENT_THRESHOLD and not (tool_data and tool_data.get("name") == "escalate_to_agent"):
        print(f"😠 LOW SENTIMENT ({sentiment_score}) - Auto-escalating")
        
        # Record escalation message in conversation history
        conversation_history.append({
            "sender": "bot",
            "text": ESCALATION_MESSAGE,
            "confidence": None,
            "timestamp": datetime.now().isoformat(),
            "tool": "escalate_to_agent",
            "sentiment": sentiment_score
        })
        
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
        session_state["is_active"] = False
        print("🚨 Bot stopped - Low sentiment escalation complete")
        return

    # Update memory with bot's reply
    chat_history.append({"role": "assistant", "content": speech_text})
    
    # Record bot message in full conversation history (for escalation)
    conversation_history.append({
        "sender": "bot",
        "text": speech_text,
        "confidence": None,  # Bot messages don't have confidence
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "sentiment": sentiment_score
    })

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
    print(f"🔊 About to speak: '{speech_text[:50]}...'")
    print("🔊 Speaking...")
    session_state["is_speaking"] = True  # Lock to prevent barge-in
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
    
    session_state["is_speaking"] = False  # Unlock after TTS completes
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
# NOTE: can_interrupt=False means no barge-in. This is intentional for stability.
# FastRTC's interrupt mechanism kills the generator before our code can handle it.
voice_stream = Stream(
    ReplyOnPause(
        voice_handler,
        can_interrupt=False  # STABLE: Bot finishes speaking before processing new input
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