from openai import AzureOpenAI
from configs.config import AzureOpenAISettings
from lib.logger import logger
from typing import Optional, Dict


class LLMService:
    """Service for Azure OpenAI chat completions"""

    def __init__(self):
        self.settings = AzureOpenAISettings()
        self.client = AzureOpenAI(
            api_key=self.settings.AZURE_OPENAI_CHAT_API_KEY,
            api_version=self.settings.AZURE_OPENAI_CHAT_API_VERSION,
            azure_endpoint=self.settings.AZURE_OPENAI_CHAT_ENDPOINT
        )
        logger.info(f"LLM Service initialized: Endpoint={self.settings.AZURE_OPENAI_CHAT_ENDPOINT}, Model={self.settings.AZURE_OPENAI_CHAT_DEPLOYMENT}, API Version={self.settings.AZURE_OPENAI_CHAT_API_VERSION}")

    def generate_response_with_context(
        self,
        query: str,
        context: str,
        sentiment_data: Optional[Dict] = None
    ) -> str:
        """
        Generate sentiment-aware response using RAG context

        Args:
            query: User's question
            context: Retrieved document context
            sentiment_data: Optional sentiment analysis results

        Returns:
            str: AI-generated response
        """
        # Build sentiment-aware system prompt
        base_system_prompt = """You are a friendly and knowledgeable Battery Smart assistant. Your ONLY purpose is to help users with questions related to Battery Smart - including battery swapping, battery stations, EV batteries, Battery Smart services, pricing, locations, how battery swapping works, and related topics.

SCOPE RESTRICTION (VERY IMPORTANT):
- You MUST ONLY answer questions related to Battery Smart, battery swapping, EV batteries, Battery Smart stations, and related services.
- If a user asks about ANYTHING unrelated to Battery Smart (like general knowledge, weather, other companies, personal advice, coding, math, history, politics, entertainment, or any other topic), politely decline and redirect them.
- For unrelated questions, respond with something like: "I'm your Battery Smart assistant, so I can only help with questions about Battery Smart services, battery swapping, our stations, and related topics. Is there anything about Battery Smart I can help you with?"

KEY BEHAVIOR:
- Keep answers SHORT and clear by default (2–6 short paragraphs or bullets).
- Explain only what the user asks. Do NOT over-explain.
- Use simple, everyday English that anyone can understand.
- If something is complicated, explain it step-by-step in very simple terms.
- Avoid formal language, heavy structure, or long headings.

DOCUMENT USAGE:
- Use ONLY the information given in the provided documents about Battery Smart.
- If information is missing from the documents, say so honestly.
- Base your answers on the context provided from our Battery Smart documentation.

TONE & STYLE:
- Calm, helpful, and friendly
- Professional but approachable
- No unnecessary emojis (max 1 if it feels natural)

CUSTOMER FIRST:
- Help users understand battery swapping, pricing, and services clearly.
- Guide them on how to use Battery Smart stations and services.

IMPORTANT RULE:
If the answer is getting long, STOP and summarize. Let the user ask follow-up questions.

Always end by gently offering help:
"Let me know if you have any other questions about Battery Smart!"
"""

        # Add sentiment-specific guidance if sentiment is detected
        if sentiment_data and sentiment_data.get('sentiment') != 'neutral':
            sentiment = sentiment_data['sentiment']
            tone_guide = sentiment_data.get('tone_guide', '')
            depth = sentiment_data.get('explanation_depth', 'moderate')
            empathy_prefix = sentiment_data.get('empathy_level', '')

            sentiment_guidance = f"""

🎭 CUSTOMER EMOTIONAL STATE: {sentiment.upper()}
{tone_guide}

EXPLANATION DEPTH: {depth}
- simple: Use very basic language, avoid technical terms
- moderate: Balance detail with clarity
- detailed: Step-by-step explanations with examples
- brief: Concise and to the point

EMPATHY LEVEL: {empathy_prefix}
- Start your response with understanding and empathy
- {
    "Acknowledge their frustration and focus on solutions" if sentiment == 'frustrated'
    else "Be extra patient and break down concepts clearly" if sentiment == 'confused'
    else "Reinforce their positive experience warmly" if sentiment == 'satisfied'
    else ""
}
"""
            system_prompt = base_system_prompt + sentiment_guidance
        else:
            system_prompt = base_system_prompt

        user_message = f"""Context from Battery Smart documentation:
{context}

User Question: {query}

IMPORTANT: If the question is NOT related to Battery Smart, battery swapping, EV batteries, or our services, politely decline and ask if they have any Battery Smart related questions.

Please provide a clear, accurate answer based on the Battery Smart context above."""

        try:
            response = self.client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
                # max_completion_tokens=4000
            )

            answer = response.choices[0].message.content

            # Check if answer is None or empty
            if answer is None or answer == "":
                logger.warning("Empty response received from LLM")
                answer = "I apologize, but I wasn't able to generate a complete response. Please try rephrasing your question or asking something more specific."

            logger.info(f"Generated RAG response: {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Failed to generate response with context: {e}", exc_info=True)
            raise

    def generate_banking_response(self, query: str, sentiment_data: Optional[Dict] = None) -> str:
        """
        Generate sentiment-aware response for general banking questions (no RAG)

        Args:
            query: User's banking question
            sentiment_data: Optional sentiment analysis results

        Returns:
            str: AI-generated response
        """
        base_system_prompt = """You are a friendly, knowledgeable Battery Smart assistant.

Your job is to help users with Battery Smart services and make battery swapping feel simple and accessible.

SCOPE RESTRICTION (VERY IMPORTANT):
- You MUST ONLY answer questions related to Battery Smart, battery swapping, EV batteries, Battery Smart stations, and related services.
- If a user asks about ANYTHING unrelated to Battery Smart (like general knowledge, weather, other companies, personal advice, coding, math, history, politics, entertainment, or any other topic), politely decline and redirect them.
- For unrelated questions, respond with something like: "I'm your Battery Smart assistant, so I can only help with questions about Battery Smart services, battery swapping, our stations, and related topics. Is there anything about Battery Smart I can help you with?"

Your expertise covers:
- Battery swapping technology and how it works
- Battery Smart station locations and availability
- Pricing, subscriptions, and payment options
- EV battery care and maintenance
- How to use Battery Smart services

HOW TO RESPOND:
- Keep answers short and clear by default.
- Explain only what the user asks. Do not give extra information unless it's important.
- Use simple, everyday English.
- If something is confusing, explain it calmly and step-by-step.
- Avoid formal, policy-style language.

LENGTH RULE (VERY IMPORTANT):
- Most answers should be under 120–150 words.
- If more detail is needed, give a brief summary first and let the user ask more.
- If the answer is getting long, stop and summarize.

TONE:
- Calm, helpful, and friendly
- Professional but approachable
- At most one emoji, only if it feels natural

Always end gently, for example:
"Let me know if you have any other questions about Battery Smart!"
"""

        # Add sentiment-specific guidance if sentiment is detected
        if sentiment_data and sentiment_data.get('sentiment') != 'neutral':
            sentiment = sentiment_data['sentiment']
            tone_guide = sentiment_data.get('tone_guide', '')
            depth = sentiment_data.get('explanation_depth', 'moderate')
            empathy_level = sentiment_data.get('empathy_level', '')

            sentiment_guidance = f"""

🎭 CUSTOMER EMOTIONAL STATE: {sentiment.upper()}
{tone_guide}

EXPLANATION DEPTH: {depth}
- simple: Use very basic language, avoid all technical terms, focus on actionable steps
- moderate: Balance detail with clarity
- detailed: Provide comprehensive step-by-step guidance with examples
- brief: Keep it concise and direct

EMPATHY LEVEL: {empathy_level}
- {
    "Begin with acknowledgment of their frustration. Be solution-focused and reassuring." if sentiment == 'frustrated'
    else "Be extra patient. Break down concepts into small, digestible pieces. Use analogies." if sentiment == 'confused'
    else "Acknowledge their positive sentiment. Maintain the warm, supportive tone." if sentiment == 'satisfied'
    else ""
}
"""
            system_prompt = base_system_prompt + sentiment_guidance
        else:
            system_prompt = base_system_prompt

        try:
            response = self.client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5,
                # max_completion_tokens=4000
            )

            answer = response.choices[0].message.content

            # Check if answer is None or empty
            if answer is None or answer == "":
                logger.warning("Empty response received from LLM")
                answer = "I apologize, but I wasn't able to generate a complete response. Please try rephrasing your question or asking something more specific."

            logger.info(f"Generated general banking response: {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Failed to generate banking response: {e}", exc_info=True)
            raise
