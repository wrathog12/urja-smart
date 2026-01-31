import os
import threading
import numpy as np
import gradio as gr
from dotenv import load_dotenv

from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

# 1. Load Configuration
load_dotenv()
API_KEY = "2185f293a20092b424619d78c960db61ca615f46"
MODEL = "nova-3"

# 2. Global State with thread safety
class TranscriptionState:
    def __init__(self):
        self.lock = threading.Lock()
        self.transcript_parts = []
        self.dg_connection = None
        self.is_connected = False
        self.audio_received = False
    
    def reset(self):
        with self.lock:
            self.transcript_parts = []
            self.audio_received = False
    
    def add_transcript(self, text):
        with self.lock:
            self.transcript_parts.append(text)
    
    def get_transcript(self):
        with self.lock:
            return " ".join(self.transcript_parts)
    
    def connect(self, sample_rate=48000):
        with self.lock:
            if self.is_connected and self.dg_connection:
                return self.dg_connection
            
            self.transcript_parts = []
            
            print(f"[*] Initializing Deepgram connection (sample_rate={sample_rate})...")
            deepgram = DeepgramClient(API_KEY)
            self.dg_connection = deepgram.listen.websocket.v("1")
            
            # Event handlers - capture self reference
            state_ref = self
            
            def on_message(ws, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) > 0:
                    is_final = result.is_final
                    print(f"[{'FINAL' if is_final else 'INTERIM'}] {sentence}")
                    if is_final:
                        state_ref.add_transcript(sentence)

            def on_error(ws, error, **kwargs):
                print(f"[!] Deepgram Error: {error}")
            
            def on_open(ws, open, **kwargs):
                print("[✓] Deepgram Live Connection Ready.")

            self.dg_connection.on(LiveTranscriptionEvents.Open, on_open)
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            # Use the sample rate from the audio
            options = LiveOptions(
                model=MODEL,
                language="multi",
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=sample_rate,
                interim_results=True,  # Show interim results too
            )
            
            if self.dg_connection.start(options):
                self.is_connected = True
                print(f"[✓] Connection started with sample_rate={sample_rate}")
            else:
                print("[!] Failed to start Deepgram connection")
                self.is_connected = False
            
            return self.dg_connection
    
    def disconnect(self):
        with self.lock:
            if self.dg_connection and self.is_connected:
                try:
                    self.dg_connection.finish()
                    print("[*] Deepgram connection closed.")
                except Exception as e:
                    print(f"Error closing connection: {e}")
            self.dg_connection = None
            self.is_connected = False

state = TranscriptionState()

def process_audio(audio):
    """Process incoming audio chunks and send to Deepgram."""
    if audio is None:
        return state.get_transcript()
    
    sample_rate, audio_data = audio
    
    # Debug first audio chunk
    if not state.audio_received:
        print(f"[DEBUG] First audio chunk received:")
        print(f"        Sample rate: {sample_rate}")
        print(f"        Audio shape: {audio_data.shape}")
        print(f"        Audio dtype: {audio_data.dtype}")
        print(f"        Audio range: [{audio_data.min()}, {audio_data.max()}]")
        state.audio_received = True
    
    # Ensure connection exists with correct sample rate
    connection = state.connect(sample_rate=sample_rate)
    if not connection or not state.is_connected:
        return "Error: Could not connect to Deepgram"
    
    # Convert to int16 if needed
    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
        # Check if already normalized (-1 to 1) or raw
        if audio_data.max() <= 1.0 and audio_data.min() >= -1.0:
            audio_data = (audio_data * 32767).astype(np.int16)
        else:
            audio_data = audio_data.astype(np.int16)
    elif audio_data.dtype != np.int16:
        audio_data = audio_data.astype(np.int16)
    
    # Send to Deepgram
    try:
        connection.send(audio_data.tobytes())
    except Exception as e:
        print(f"[!] Error sending audio: {e}")
    
    return state.get_transcript()

def on_stop():
    """Called when recording stops."""
    import time
    time.sleep(1.0)  # Wait for last transcripts to arrive
    
    full_transcript = state.get_transcript()
    print(f"\n{'='*50}")
    print(f"[FINAL TRANSCRIPT]: {full_transcript}")
    print(f"{'='*50}\n")
    
    state.disconnect()
    return full_transcript

def on_start():
    """Called when recording starts."""
    print("\n[*] Recording started...")
    state.disconnect()
    state.reset()
    return ""

# Create Gradio UI
with gr.Blocks(title="Deepgram Live Transcription") as demo:
    gr.Markdown("# 🎙️ Deepgram Nova-3 Live Transcription")
    gr.Markdown("Click the **microphone button** to start recording, speak, then click again to stop.")
    
    audio_input = gr.Audio(
        sources=["microphone"],
        streaming=True,
        label="🎤 Click to Record"
    )
    
    transcript_box = gr.Textbox(
        label="📝 Live Transcription",
        lines=5,
        placeholder="Your transcription will appear here as you speak..."
    )
    
    audio_input.stream(
        fn=process_audio,
        inputs=[audio_input],
        outputs=[transcript_box]
    )
    
    audio_input.stop_recording(fn=on_stop, outputs=[transcript_box])
    audio_input.start_recording(fn=on_start, outputs=[transcript_box])

if __name__ == "__main__":
    print("----------------------------------------------------------------")
    print("🚀 Starting Deepgram Transcription Demo!")
    print("   Open http://localhost:7860 in your browser")
    print("----------------------------------------------------------------")
    demo.launch(server_name="0.0.0.0", server_port=7860)