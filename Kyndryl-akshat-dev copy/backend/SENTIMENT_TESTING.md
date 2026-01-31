# Sentiment-Aware Response Testing Guide

## Overview

The system now includes **sentiment analysis** that detects customer emotions (frustration, confusion, satisfaction, or neutral) and adjusts the response tone, empathy level, and explanation depth accordingly.

## How It Works

### 1. Sentiment Detection
The system analyzes the user's message for emotional cues:
- **Frustrated**: Angry, upset, experiencing issues
- **Confused**: Unclear, asking for clarification
- **Satisfied**: Happy, grateful, content
- **Neutral**: Straightforward inquiry

### 2. Response Adaptation
Based on detected sentiment, the LLM:
- Adjusts **tone** (empathetic vs. professional)
- Modifies **explanation depth** (simple, moderate, detailed, brief)
- Changes **empathy level** (high, moderate, positive, neutral)

### 3. Technical Literacy Detection
The system also detects technical literacy from keywords and adjusts complexity:
- Technical users → More detailed technical terms
- Non-technical users → Simpler explanations with analogies

## Testing Examples

### Test Case 1: Frustrated Customer

**Input:**
```
"This is so frustrating!! My account is still not working after 3 days. Why isn't anyone fixing this problem??"
```

**Expected Behavior:**
- Sentiment: `frustrated`
- Confidence: High (0.7+)
- Response should:
  - Acknowledge frustration immediately
  - Be solution-focused and reassuring
  - Use simple language
  - Provide clear actionable steps
  - Avoid technical jargon

**Example Response:**
```
I understand this is frustrating. Let me help resolve this for you right away.

When an account issue persists for multiple days, it usually means...
[Solution-focused explanation in simple terms]

Let's get this fixed step by step:
1. [Actionable step]
2. [Actionable step]

Let me know if you need any help with these steps.
```

---

### Test Case 2: Confused Customer

**Input:**
```
"I don't understand what KYC means and how to do it. Can you explain this in simple terms?"
```

**Expected Behavior:**
- Sentiment: `confused`
- Confidence: Moderate to High
- Response should:
  - Be patient and educational
  - Break down concepts step-by-step
  - Use analogies and examples
  - Avoid assumptions about prior knowledge
  - Encourage follow-up questions

**Example Response:**
```
Let me explain this clearly.

KYC stands for "Know Your Customer" - think of it like showing your ID when you enter a building. Banks need to verify who you are for security.

Here's how it works step by step:
1. [Simple explanation]
2. [Simple explanation with example]

Does this make sense? Feel free to ask if you want me to clarify any part.
```

---

### Test Case 3: Satisfied Customer

**Input:**
```
"Thank you so much! This worked perfectly. You've been very helpful."
```

**Expected Behavior:**
- Sentiment: `satisfied`
- Confidence: High
- Response should:
  - Warm and encouraging
  - Reinforce positive experience
  - Be brief (don't overwhelm)
  - Maintain friendly tone

**Example Response:**
```
I'm glad things are working well!

If you need any help with anything else related to your account, feel free to ask.
```

---

### Test Case 4: Neutral Inquiry

**Input:**
```
"What is the interest rate for savings accounts?"
```

**Expected Behavior:**
- Sentiment: `neutral`
- Confidence: Low (0.0-0.3)
- Response should:
  - Professional and clear
  - Direct and accurate
  - Concise but thorough
  - Maintain helpful tone

**Example Response:**
```
Savings account interest rates in India typically range from 2.7% to 4% per annum, depending on the bank...

[Clear, factual response]

Let me know if you want details about any specific bank.
```

---

## API Response Format

The chat endpoint now returns sentiment information:

```json
{
  "response": "AI-generated response text...",
  "mode": "rag" or "general",
  "detected_language": "en",
  "language_name": "English",
  "document_id": null,
  "chunks_used": null,
  "sentiment": "frustrated",
  "sentiment_confidence": 0.85
}
```

## Testing with CURL

### Test Frustrated Sentiment:
```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "This is so annoying!! My transfer failed again. Why does this keep happening??",
    "document_id": null
  }'
```

### Test Confused Sentiment:
```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I am confused about what IFSC code means. Can you explain?",
    "document_id": null
  }'
```

### Test Satisfied Sentiment:
```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Thank you! That worked great and solved my problem perfectly.",
    "document_id": null
  }'
```

### Test Neutral:
```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the charges for NEFT transactions?",
    "document_id": null
  }'
```

## Testing with Frontend

1. Start the backend server
2. Start the frontend
3. Try the test messages above
4. Observe:
   - Response tone and empathy
   - Explanation depth
   - Use of technical terms
   - Opening phrases

## Monitoring Logs

The backend logs sentiment detection:

```
INFO: Sentiment detected: frustrated (confidence: 0.85)
INFO: Processing RAG query: 'This is so annoying!! My transfer...'
INFO: RAG query completed successfully. Used 30 chunks, Language: en, Sentiment: frustrated
```

Check the logs to verify sentiment detection is working correctly.

## Fine-Tuning Sentiment Keywords

To adjust sentiment detection, edit `/backend/src/services/sentiment_service.py`:

- `frustration_keywords` - Words indicating frustration
- `confusion_keywords` - Words indicating confusion
- `satisfaction_keywords` - Words indicating satisfaction
- Adjust confidence thresholds in `analyze_sentiment()`

## Edge Cases to Test

1. **Mixed Emotions**: "I'm happy with the service but confused about fees"
   - Should detect dominant sentiment (confused > satisfied in this case)

2. **Non-English**: "यह बहुत निराशाजनक है" (This is very frustrating in Hindi)
   - Should detect sentiment even after translation

3. **Multiple Questions**: Long message with both frustration and genuine inquiry
   - Should prioritize emotional tone over neutral inquiry

4. **Sarcasm**: "Great, another error. Just perfect."
   - May be detected as satisfied (limitation - sarcasm detection not implemented)

## Success Metrics

✅ Correct sentiment detection (>80% accuracy on test cases)
✅ Appropriate tone adjustment in responses
✅ Explanation depth matches customer need
✅ Empathetic opening phrases for frustrated/confused
✅ Brief responses for satisfied customers
✅ Professional responses for neutral queries

## Troubleshooting

**Issue**: Sentiment always shows as "neutral"
- Check if sentiment_service is properly initialized in RAG service
- Verify sentiment data is being passed to LLM service
- Check logs for sentiment detection results

**Issue**: Response doesn't match sentiment
- Review LLM prompt construction in llm_service.py
- Check if sentiment_data is None or empty
- Verify tone_guide and explanation_depth values

**Issue**: TTS doesn't reflect empathy
- TTS uses the text generated by sentiment-aware LLM
- Empathy comes from text content, not voice tone
- ElevenLabs voice model doesn't change based on sentiment (it's the same voice)
- The empathetic response should be visible in the text itself

## Next Steps

Consider these enhancements:
1. **Conversation History**: Track sentiment over multiple turns
2. **Escalation Detection**: Alert human agent when frustration persists
3. **Satisfaction Surveys**: Ask for feedback when sentiment is satisfied
4. **Analytics Dashboard**: Track sentiment trends over time
5. **Multi-turn Context**: Remember previous sentiment in conversation
