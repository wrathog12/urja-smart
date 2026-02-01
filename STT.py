import os
import httpx
import threading
import time
from datetime import datetime

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)

# CONFIGURATION
# ------------------------------------------------------------------
# Replace with your key or use os.getenv("DEEPGRAM_API_KEY")
API_KEY = "" 
STREAM_URL = "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"
MODEL = "nova-3"
# ------------------------------------------------------------------

def main():
    try:
        # 1. Initialize Deepgram Client (v5.x API - no DeepgramClientOptions needed)
        deepgram = DeepgramClient(API_KEY)

        # 2. Configure the Live Connection
        # We use "en" (Global English) or "en-US". 
        # For your hackathon, you will switch this to "en-IN" later.
        options = LiveOptions(
            model=MODEL, 
            language="en-US", 
            smart_format=True,  # Crucial for "20%" instead of "twenty percent"
            # encoding="linear16", # Raw stream format
            # channels=1, 
            # sample_rate=16000, 
            interim_results=True, # Set to True to see text *while* speaking (Low Latency)
        )

        # Create the connection
        dg_connection = deepgram.listen.live.v("1")

        # 3. Define Event Handlers
        def on_open(self, open, **kwargs):
            print(f"\n[✓] Connection to Deepgram {MODEL} Established. Fetching BBC Stream...\n")

        def on_message(self, result, **kwargs):
            # This runs every time Deepgram sends back text
            sentence = result.channel.alternatives[0].transcript
            
            if len(sentence) == 0:
                return

            # Calculate a rough "Processing Timestamp"
            now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Check if this is a "Final" sentence or just "Interim" (flickering text)
            is_final = result.is_final
            status = "[FINAL]" if is_final else "[INTERIM]"
            
            # Print with timestamp to check latency
            print(f"{now} {status} {sentence}")

        def on_error(self, error, **kwargs):
            print(f"\n[!] Error: {error}\n")

        # Register handlers
        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        # 4. Start the Connection
        if dg_connection.start(options) is False:
            print("Failed to start connection")
            return

        # 5. Audio Streaming Thread
        # We use a lock to ensure safe exit
        lock_exit = threading.Lock()
        exit_event = threading.Event()

        def stream_audio():
            print(f"[*] Buffering audio from {STREAM_URL}...")
            try:
                with httpx.stream("GET", STREAM_URL) as r:
                    for data in r.iter_bytes():
                        if exit_event.is_set():
                            break
                        # Send raw audio data to Deepgram
                        dg_connection.send(data)
            except Exception as e:
                print(f"Stream Error: {e}")

        # Start streaming in background
        stream_thread = threading.Thread(target=stream_audio)
        stream_thread.start()

        # Keep main thread alive until user quits
        input("\nPress Enter to stop testing...\n")
        
        # Cleanup
        exit_event.set()
        stream_thread.join()
        dg_connection.finish()
        print("[*] Connection Closed.")

    except Exception as e:
        print(f"Could not open socket: {e}")

if __name__ == "__main__":
    if API_KEY == "YOUR_DEEPGRAM_API_KEY":
        print("Please set your API_KEY in the script first!")
    else:
        main()
