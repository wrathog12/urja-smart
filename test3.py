import time
import numpy as np
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your modules
from backend.app.services.llm import llm_service

# --- Deepgram STT (Direct implementation without audio_to_bytes) ---
import threading
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from backend.app.core.config import settings

class LiveSTT:
    """Simple STT using Deepgram WebSocket - no FFmpeg needed!"""
    def __init__(self):
        self.transcript_parts = []
        self.connection = None
        self.is_connected = False
        self.lock = threading.Lock()
    
    def connect(self, sample_rate=48000):
        with self.lock:
            if self.is_connected:
                return
            
            self.transcript_parts = []
            deepgram = DeepgramClient(settings.DEEPGRAM_API_KEY)
            self.connection = deepgram.listen.websocket.v("1")
            
            def on_message(ws, result, **kwargs):
                text = result.channel.alternatives[0].transcript
                if text and result.is_final:
                    print(f"[STT] {text}")
                    self.transcript_parts.append(text)
            
            def on_error(ws, error, **kwargs):
                print(f"[STT Error] {error}")
            
            self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.connection.on(LiveTranscriptionEvents.Error, on_error)
            
            options = LiveOptions(
                model="nova-3",
                language="multi",
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=sample_rate,
                interim_results=False
            )
            self.connection.start(options)
            self.is_connected = True
            print("[STT] Connected to Deepgram")
    
    def send_audio(self, audio_data: np.ndarray):
        if not self.is_connected:
            return
        
        # Convert to int16 if needed
        if audio_data.dtype in [np.float32, np.float64]:
            audio_data = (audio_data * 32767).astype(np.int16)
        elif audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)
        
        try:
            self.connection.send(audio_data.tobytes())
        except Exception as e:
            print(f"[STT Send Error] {e}")
    
    def get_transcript(self):
        with self.lock:
            return " ".join(self.transcript_parts)
    
    def disconnect(self):
        with self.lock:
            if self.connection and self.is_connected:
                try:
                    self.connection.finish()
                except:
                    pass
            self.connection = None
            self.is_connected = False

# Global STT instance
stt = LiveSTT()

# --- Performance Logger ---
def format_latency(start, end):
    return f"{(end - start) * 1000:.0f}ms"

# --- Gradio Handlers ---
def on_audio_stream(audio):
    """Called for each audio chunk while recording."""
    if audio is None:
        return "", ""
    
    sample_rate, audio_data = audio
    
    # Connect on first chunk
    if not stt.is_connected:
        stt.connect(sample_rate)
    
    # Send audio to Deepgram
    stt.send_audio(audio_data)
    
    # Return current transcript (live update)
    return stt.get_transcript(), ""

def on_stop_recording():
    """Called when recording stops - get final transcript and LLM response."""
    import time
    time.sleep(0.5)  # Wait for final transcripts
    
    t0 = time.perf_counter()
    
    # Get transcript
    user_text = stt.get_transcript()
    stt.disconnect()
    
    t1 = time.perf_counter()
    
    if not user_text:
        return "No speech detected", "...", "STT: 0ms | LLM: 0ms"
    
    # Call LLM
    print(f"\n🧠 Thinking about: {user_text}")
    fake_history = [{"role": "user", "content": user_text}]
    speech_text, tool_data = llm_service.get_response(fake_history)
    
    t2 = time.perf_counter()
    
    # Calculate latency
    stt_time = format_latency(t0, t1)
    llm_time = format_latency(t1, t2)
    latency = f"STT: {stt_time} | LLM: {llm_time} | Tool: {tool_data}"
    
    print(f"� Results: User='{user_text}' | Bot='{speech_text}'")
    
    return user_text, speech_text, latency

def on_start_recording():
    """Called when recording starts."""
    stt.disconnect()
    stt.transcript_parts = []
    return "", "", ""

# --- Gradio UI ---
with gr.Blocks(title="Voice AI Pipeline Test", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎙️ Voice AI Pipeline Test")
    gr.Markdown("Click microphone to record → Speak → Click again to stop → See transcription + LLM response")
    
    with gr.Row():
        audio_input = gr.Audio(
            sources=["microphone"],
            streaming=True,
            label="🎤 Click to Record"
        )
    
    with gr.Row():
        with gr.Column():
            user_box = gr.Textbox(
                label="📝 Your Transcription (STT)",
                lines=3,
                placeholder="Your speech will appear here..."
            )
        with gr.Column():
            bot_box = gr.Textbox(
                label="🤖 Bot Response (LLM)",
                lines=3,
                placeholder="LLM response will appear here..."
            )
    
    latency_box = gr.Textbox(label="⚡ Latency & Tool Info", lines=1)
    
    # Wire up events
    audio_input.stream(
        fn=on_audio_stream,
        inputs=[audio_input],
        outputs=[user_box, bot_box]
    )
    
    audio_input.stop_recording(
        fn=on_stop_recording,
        outputs=[user_box, bot_box, latency_box]
    )
    
    audio_input.start_recording(
        fn=on_start_recording,
        outputs=[user_box, bot_box, latency_box]
    )

if __name__ == "__main__":
    print("----------------------------------------------------------------")
    print("⚡ Voice AI Pipeline Test - http://localhost:7860")
    print("----------------------------------------------------------------")
    demo.launch(server_name="0.0.0.0", server_port=7860)