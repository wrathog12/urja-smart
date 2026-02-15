from fastrtc import ReplyOnPause

def get_vad_handler(handler_function):
    """
    Wraps your main logic with a tuned VAD.
    We isolate it here so we can tweak 'Traffic Sensitivity' without breaking the app.
    
    NOTE: This function is kept for reference but voice_stream.py now configures
    VAD directly in the Stream() call for barge-in support.
    """
    return ReplyOnPause(
        handler_function,
        # 0.65 is stricter than default (0.5)
        # Higher = Harder to trigger (ignores light noise/background chatter)
        vad_threshold=0.65, 
        
        # How long to wait after they stop speaking before replying?
        # 0.5 is faster response. Was 0.7 which felt slow.
        pause_threshold=0.5,  
        
        # Model options (Silero is efficient)
        model_options={"language": "en"}
    )