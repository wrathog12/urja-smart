from fastrtc import ReplyOnPause

def get_vad_handler(handler_function):
    """
    Wraps your main logic with a tuned VAD.
    We isolate it here so we can tweak 'Traffic Sensitivity' without breaking the app.
    """
    return ReplyOnPause(
        handler_function,
        # 0.5 is default. 
        # Higher (0.6+) = Harder to trigger (ignores light noise).
        # Lower (0.3) = Sensitive (triggers on whispers).
        vad_threshold=0.5, 
        
        # How long to wait after they stop speaking before replying?
        # Drivers speak slowly. Increase this to avoid cutting them off.
        pause_threshold=0.7,  
        
        # Model options (Silero is efficient)
        model_options={"language": "en"}
    )