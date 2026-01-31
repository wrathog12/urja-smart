# backend/app/tools/end_call.py
"""
End Call Tool - Handles call termination triggered by LLM
"""
import logging

logger = logging.getLogger(__name__)

class EndCallTool:
    """
    Tool to handle call termination.
    When triggered, this signals the voice stream to end the session.
    """
    
    def __init__(self):
        self.call_ended = False
        self.end_reason = None
    
    def execute(self, args: dict) -> dict:
        """
        Execute the end_call tool.
        
        Args:
            args: {"reason": "user_requested" | "issue_resolved"}
        
        Returns:
            Status dict
        """
        self.call_ended = True
        self.end_reason = args.get("reason", "user_requested")
        
        logger.info(f"📞 END CALL EXECUTED - Reason: {self.end_reason}")
        
        return {
            "success": True,
            "action": "end_call",
            "reason": self.end_reason
        }
    
    def reset(self):
        """Reset tool state for new session."""
        self.call_ended = False
        self.end_reason = None
    
    def should_end_call(self) -> bool:
        """Check if call should be ended."""
        return self.call_ended
    
    def get_end_reason(self) -> str | None:
        """Get the reason for ending the call."""
        return self.end_reason


# Singleton instance
end_call_tool = EndCallTool()
