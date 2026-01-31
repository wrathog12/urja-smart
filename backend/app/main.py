# 🚀 SERVER ENTRY POINT (The "Host")
# This is the main FastAPI application that mounts the FastRTC stream

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gradio as gr

# Import the configured stream from voice_stream pipeline
from backend.app.pipelines.voice_stream import voice_stream, session_state, reset_session, get_conversation_history
from backend.app.services.tts import tts_service

# --- Pydantic Models ---
class VoicePersonaRequest(BaseModel):
    persona: str  # "male" or "female"

class CustomVoiceRequest(BaseModel):
    voice_id: str

# --- FastAPI App ---
app = FastAPI(
    title="Battery Smart Voice AI",
    description="Real-time voice AI customer service using FastRTC",
    version="1.0.0"
)

# --- CORS (for frontend integration) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Simple health check for monitoring."""
    return {"status": "healthy", "service": "voice-ai"}

# --- Voice Persona Endpoints ---
@app.get("/api/voice/persona")
async def get_voice_persona():
    """Get current voice persona info."""
    return tts_service.get_current_persona()

@app.post("/api/voice/persona")
async def set_voice_persona(request: VoicePersonaRequest):
    """
    Switch voice persona.
    Available personas: "male", "female"
    """
    success = tts_service.set_voice_persona(request.persona)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid persona: {request.persona}. Available: male, female"
        )
    return {"success": True, "current_persona": tts_service.get_current_persona()}

@app.post("/api/voice/custom")
async def set_custom_voice(request: CustomVoiceRequest):
    """Set a custom Cartesia voice ID directly."""
    tts_service.set_custom_voice_id(request.voice_id)
    return {"success": True, "voice_id": request.voice_id}

# --- Session State Endpoints ---
@app.get("/api/session/state")
async def get_session_state():
    """
    Get current session state for frontend polling.
    Frontend can use this to:
    - Check if call should end
    - Get latest transcript/response
    - Get sentiment score
    """
    return {
        "is_active": session_state.get("is_active", False),
        "should_end": session_state.get("should_end", False),
        "end_reason": session_state.get("end_reason"),
        "last_user_text": session_state.get("last_user_text", ""),
        "last_bot_text": session_state.get("last_bot_text", ""),
        "last_tool": session_state.get("last_tool"),
        "last_sentiment": session_state.get("last_sentiment", 0.7),
        "metrics": session_state.get("metrics", {}),
        "station_data": session_state.get("station_data")  # For map popup
    }

@app.post("/api/session/reset")
async def reset_session_endpoint():
    """
    Reset session state. Call this when:
    - Starting a new call
    - After call ends
    """
    reset_session()
    return {"success": True, "message": "Session reset"}

@app.post("/api/session/end")
async def end_session_endpoint():
    """
    Manually end the session from frontend.
    Use when user clicks "Stop" button.
    """
    session_state["should_end"] = True
    session_state["end_reason"] = "manual_stop"
    session_state["is_active"] = False
    return {"success": True, "message": "Session ended"}

@app.get("/api/session/history")
async def get_session_history():
    """
    Get full conversation history with confidence scores for escalation.
    Returns:
        - history: List of {sender, text, confidence, timestamp, tool}
        - summary: Auto-generated summary of conversation
        - stats: {totalTurns, avgConfidence, lowConfidenceCount}
        - metrics: {stt, llm, tts} latencies
    """
    history = get_conversation_history()
    
    # Calculate stats
    user_messages = [m for m in history if m.get("sender") == "user"]
    confidence_scores = [m.get("confidence", 0) for m in user_messages if m.get("confidence") is not None]
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
    low_confidence_count = len([c for c in confidence_scores if c < 0.7])
    
    # Generate summary
    summary = generate_summary(history)
    
    return {
        "history": history,
        "summary": summary,
        "stats": {
            "totalTurns": len(history),
            "userMessages": len(user_messages),
            "botMessages": len([m for m in history if m.get("sender") == "bot"]),
            "avgConfidence": avg_confidence,
            "lowConfidenceCount": low_confidence_count
        },
        "metrics": session_state.get("metrics", {}),
        "sentiment_history": session_state.get("sentiment_history", []),
        "customerPhone": session_state.get("customer_phone"),
        "customerName": session_state.get("customer_name")
    }

class CustomerInfoRequest(BaseModel):
    phone: str = None
    name: str = None

@app.post("/api/session/customer-info")
async def set_customer_info(request: CustomerInfoRequest):
    """
    Set customer phone number and name for callback.
    Can be called from frontend when user provides their number.
    """
    if request.phone:
        session_state["customer_phone"] = request.phone
    if request.name:
        session_state["customer_name"] = request.name
    return {"success": True, "phone": request.phone, "name": request.name}

def generate_summary(history: list) -> str:
    """Generate a quick summary from conversation history."""
    if not history:
        return "No conversation history available."
    
    user_messages = [m.get("text", "") for m in history if m.get("sender") == "user"]
    
    if not user_messages:
        return "No user messages recorded."
    
    # Extract keywords for topics
    keywords = []
    keyword_patterns = [
        ("invoice|bill|payment|paisa", "Invoice/Payment"),
        ("battery|swap|charge", "Battery/Swap"),
        ("station|location|nearest", "Station Location"),
        ("problem|issue|help|complaint", "Support Issue"),
        ("penalty|fine|late", "Penalty Inquiry"),
    ]
    
    all_text = " ".join(user_messages).lower()
    import re
    for pattern, topic in keyword_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            keywords.append(topic)
    
    topics_str = ", ".join(keywords) if keywords else "General inquiry"
    last_message = user_messages[-1][:100] + ("..." if len(user_messages[-1]) > 100 else "")
    
    return f"Customer discussed: {topics_str}. Last message: \"{last_message}\""

# --- Mount FastRTC Stream ---
# This exposes the WebRTC endpoints for audio streaming
# FastRTC automatically creates:
#   - /webrtc/offer (POST) - for WebRTC signaling
voice_stream.mount(app)

# --- Mount Gradio UI (optional, for testing) ---
# This serves the Gradio interface at /gradio path
gr.mount_gradio_app(app, voice_stream.ui, path="/gradio")

# --- Run Server ---
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 BATTERY SMART VOICE AI SERVER - URJA")
    print("=" * 60)
    print(f"📍 Main API: http://localhost:8000")
    print(f"📍 Gradio UI: http://localhost:8000/gradio")
    print(f"📍 WebRTC: http://localhost:8000/webrtc/offer")
    print("")
    print("📋 FEATURES:")
    print("   • Opening Message: Urja greets when call starts")
    print("   • Sentiment Tracking: Monitors user mood")
    print("   • Auto-Escalation: Transfers angry users to agent")
    print("   • Language Match: Responds in user's language")
    print("   • End Call: Voice-triggered call termination")
    print("")
    print("🎤 API Endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /api/session/state - Get call state (for polling)")
    print("   POST /api/session/reset - Reset session")
    print("   POST /api/session/end - End session manually")
    print("   POST /api/voice/persona - Switch voice (male/female)")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)