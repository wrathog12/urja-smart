# test_llm.py
from dotenv import load_dotenv
load_dotenv()

from backend.app.services.llm import llm_service

def test_queries():
    queries = [
        "Hi, kaise ho?",
        "Mera paisa kat gaya, check karo.",
        "Battery station kahan hai?"
    ]

    for q in queries:
        print(f"\nUser: {q}")
        print("-" * 30)
        
        # Fake history
        history = [{"role": "user", "content": q}]
        
        # Call LLM
        speech, tool = llm_service.get_response(history)
        
        print(f"🗣️  Speech (For TTS): {speech}")
        print(f"🔧 Tool (For Backend): {tool}")

if __name__ == "__main__":
    test_queries()