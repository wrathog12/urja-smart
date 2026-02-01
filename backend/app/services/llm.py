import json
import re
import logging
from groq import Groq
from backend.app.core.config import settings
from backend.app.core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GroqLLM:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Fast, smart, cheap
    
    def get_response(self, chat_history: list) -> tuple[str, dict | None, float]:
        """
        Input: Conversation History
        Output: (spoken_text, tool_call_json, sentiment_score)
        """
        # 1. Prepare Messages
        # Ensure System Prompt is always at the top, keep last 5 turns for context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[-5:]

        try:
            # 2. Call Groq (Llama 3)
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=200,  # Slightly more for sentiment
                stop=None
            )
            
            raw_content = completion.choices[0].message.content
            
            # 3. Parse output (Tool, Sentiment, Speech)
            return self._parse_output(raw_content)

        except Exception as e:
            logger.error(f"❌ LLM Error: {e}")
            return "Maaf kijiye, connection issue hai. Ek moment please.", None, 0.5

    def _parse_output(self, raw_text: str) -> tuple[str, dict | None, float]:
        """
        Parse the new response format:
        [TOOL: {...} | null]
        [SENTIMENT: 0.7]
        <Spoken text>
        
        Returns: (spoken_text, tool_data, sentiment_score)
        """
        tool_data = None
        sentiment_score = 0.7  # Default neutral
        spoken_text = raw_text

        # 1. Extract TOOL
        tool_pattern = r"\[TOOL:\s*({.*?}|null)\]"
        tool_match = re.search(tool_pattern, raw_text, re.DOTALL | re.IGNORECASE)
        
        if tool_match:
            json_str = tool_match.group(1)
            spoken_text = re.sub(tool_pattern, "", spoken_text, flags=re.DOTALL | re.IGNORECASE)
            
            try:
                if json_str.lower() != "null":
                    tool_data = json.loads(json_str)
                    logger.info(f"🔧 Tool Triggered: {tool_data.get('name', 'unknown')}")
            except json.JSONDecodeError as e:
                logger.error(f"⚠️ LLM generated bad JSON: {json_str} - {e}")

        # 2. Extract SENTIMENT
        sentiment_pattern = r"\[SENTIMENT:\s*([\d.]+)\]"
        sentiment_match = re.search(sentiment_pattern, raw_text, re.IGNORECASE)
        
        if sentiment_match:
            try:
                sentiment_score = float(sentiment_match.group(1))
                sentiment_score = max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1
                logger.info(f"💭 Sentiment Score: {sentiment_score}")
            except ValueError:
                sentiment_score = 0.7
            
            spoken_text = re.sub(sentiment_pattern, "", spoken_text, flags=re.IGNORECASE)

        # 3. Clean up spoken text
        spoken_text = spoken_text.strip()
        
        # Remove any remaining brackets or formatting
        spoken_text = re.sub(r"\[.*?\]", "", spoken_text).strip()
        
        return spoken_text, tool_data, sentiment_score

# Singleton Instance
llm_service = GroqLLM()