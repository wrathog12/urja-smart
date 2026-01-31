# backend/app/tools/handoff.py

class HandoffGuard:
    def __init__(self):
        # Configuration
        self.CONFIDENCE_THRESHOLD = 0.50
        self.STRIKE_LIMIT = 2
        
        # State
        self.strike_count = 0

    def check_and_update(self, confidence_score: float) -> bool:
        """
        Feeds the score to the guard.
        Returns:
            True  -> TRIGGGER HANDOFF IMMEDIATELY
            False -> Continue normally
        """
        # 1. Good Audio? Reset checks.
        if confidence_score >= self.CONFIDENCE_THRESHOLD:
            self.strike_count = 0
            return False
            
        # 2. Bad Audio? Increment Strike.
        self.strike_count += 1
        print(f"⚠️ Handoff Guard Warning: Low Confidence Strike {self.strike_count}/{self.STRIKE_LIMIT}")
        
        # 3. Check Limit
        if self.strike_count >= self.STRIKE_LIMIT:
            return True
            
        return False

    def get_escalation_message(self):
        """
        Returns the standard handoff script.
        """
        # Reset state so the next user starts fresh
        self.strike_count = 0 
        return "I am having trouble hearing you clearly. To ensure you get the right help, I am connecting you to a human agent now. Please hold on."

# Create a Singleton Instance to be imported
handoff_guard = HandoffGuard()