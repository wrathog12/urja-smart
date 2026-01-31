"""
Sentiment Analysis Service

Analyzes customer emotions and determines appropriate response tone.
Supports: frustration, confusion, satisfaction, neutral states.
"""

import re
from typing import Dict, Tuple, Optional
from lib.logger import logger


class SentimentService:
    """
    Detects customer sentiment and provides empathetic response guidelines.

    Sentiment Categories:
    - frustrated: Customer is angry, upset, or experiencing issues
    - confused: Customer is unclear, asking for clarification
    - satisfied: Customer is happy, grateful, or content
    - neutral: Default state, straightforward inquiry
    """

    def __init__(self):
        # Keyword patterns for sentiment detection
        self.frustration_keywords = [
            r'\bfrustrat\w*\b', r'\banger\w*\b', r'\bupset\b', r'\bannoy\w*\b',
            r'\bterrible\b', r'\bawful\b', r'\bhorrible\b', r'\bworse\b', r'\bworst\b',
            r'\bstuck\b', r'\bbroken\b', r'\bnot working\b', r'\bfail\w*\b',
            r'\bproblem\w*\b', r'\bissue\w*\b', r'\berror\w*\b', r'\bwrong\b',
            r'\bwhy (is|are|does|do|did|isn\'t|aren\'t|doesn\'t|don\'t)\b',
            r'\bstill not\b', r'\bagain\b', r'\bkeep\w* (getting|having)\b',
            r'\bdisappoint\w*\b', r'\bunacceptable\b', r'\bwaste\b'
        ]

        self.confusion_keywords = [
            r'\bconfus\w*\b', r'\bunsure\b', r'\bdon\'t understand\b', r'\bunclear\b',
            r'\bwhat (is|are|does|do|did|mean|means)\b', r'\bhow (to|do|does|did)\b',
            r'\bcan you explain\b', r'\bwhat\'s\b', r'\bhelp me understand\b',
            r'\bdon\'t know\b', r'\bnot sure\b', r'\bwhich\b', r'\bwhere\b',
            r'\bwhen\b', r'\bwhy\b', r'\bclarify\b', r'\bexplain\b',
            r'\bmean by\b', r'\brefer to\b', r'\bsimpler\b', r'\beasier\b'
        ]

        self.satisfaction_keywords = [
            r'\bthank\w*\b', r'\bgreat\b', r'\bexcellent\b', r'\bperfect\b',
            r'\bamazing\b', r'\bwonderful\b', r'\bawesome\b', r'\bfantastic\b',
            r'\bhelpful\b', r'\bappreciate\b', r'\bglad\b', r'\bhappy\b',
            r'\bwork\w* (great|well|perfectly|fine)\b', r'\bsolve\w*\b', r'\bfix\w*\b',
            r'\bsuccess\w*\b', r'\bgood\b', r'\blove\b', r'\bnice\b',
            r'\bthat worked\b', r'\bgot it\b', r'\bmakes sense\b'
        ]

        # Punctuation indicators
        self.frustration_punctuation = r'[!]{2,}|\?\?+'
        self.confusion_punctuation = r'\?{2,}'

    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze text and return sentiment with confidence and guidelines.

        Args:
            text: User's message text

        Returns:
            Dictionary with sentiment, confidence, tone_guide, and explanation_depth
        """
        if not text or not text.strip():
            return self._neutral_response()

        text_lower = text.lower()

        # Calculate sentiment scores
        frustration_score = self._calculate_score(text_lower, self.frustration_keywords)
        confusion_score = self._calculate_score(text_lower, self.confusion_keywords)
        satisfaction_score = self._calculate_score(text_lower, self.satisfaction_keywords)

        # Punctuation analysis
        if re.search(self.frustration_punctuation, text):
            frustration_score += 0.3
        if re.search(self.confusion_punctuation, text):
            confusion_score += 0.2

        # Determine dominant sentiment
        scores = {
            'frustrated': frustration_score,
            'confused': confusion_score,
            'satisfied': satisfaction_score
        }

        max_score = max(scores.values())

        # Threshold for sentiment detection
        if max_score < 0.3:
            return self._neutral_response()

        sentiment = max(scores, key=scores.get)
        confidence = min(max_score, 1.0)

        logger.info(f"Sentiment detected: {sentiment} (confidence: {confidence:.2f})")

        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'tone_guide': self._get_tone_guide(sentiment),
            'explanation_depth': self._get_explanation_depth(sentiment, text_lower),
            'empathy_level': self._get_empathy_level(sentiment, confidence)
        }

    def _calculate_score(self, text: str, keywords: list) -> float:
        """Calculate sentiment score based on keyword matches."""
        matches = sum(1 for pattern in keywords if re.search(pattern, text))
        return min(matches * 0.25, 1.0)

    def _get_tone_guide(self, sentiment: str) -> str:
        """Get tone guidelines for response generation."""
        tone_guides = {
            'frustrated': (
                "Empathetic and solution-focused. Acknowledge frustration, "
                "apologize if appropriate, provide clear actionable steps. "
                "Avoid technical jargon. Be patient and reassuring."
            ),
            'confused': (
                "Patient and educational. Break down complex concepts into simple steps. "
                "Use analogies and examples. Check for understanding. "
                "Encourage questions. Avoid assumptions about prior knowledge."
            ),
            'satisfied': (
                "Warm and encouraging. Reinforce positive experience. "
                "Offer additional helpful information if relevant. "
                "Maintain friendly, supportive tone."
            ),
            'neutral': (
                "Professional and clear. Provide direct, accurate information. "
                "Be concise but thorough. Maintain helpful tone."
            )
        }
        return tone_guides.get(sentiment, tone_guides['neutral'])

    def _get_explanation_depth(self, sentiment: str, text: str) -> str:
        """Determine appropriate explanation depth."""
        # Check for indicators of technical literacy
        technical_terms = r'\b(api|database|configuration|server|deployment|authentication|authorization)\b'
        is_technical = bool(re.search(technical_terms, text))

        if sentiment == 'confused':
            return 'detailed' if not is_technical else 'moderate'
        elif sentiment == 'frustrated':
            return 'simple'  # Keep it simple when frustrated
        elif sentiment == 'satisfied':
            return 'brief'  # They're happy, don't overwhelm
        else:
            return 'moderate'

    def _get_empathy_level(self, sentiment: str, confidence: float) -> str:
        """Determine empathy level for response."""
        if sentiment == 'frustrated' and confidence > 0.6:
            return 'high'
        elif sentiment in ['frustrated', 'confused'] and confidence > 0.4:
            return 'moderate'
        elif sentiment == 'satisfied':
            return 'positive'
        else:
            return 'neutral'

    def _neutral_response(self) -> Dict[str, any]:
        """Return neutral sentiment response."""
        return {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'tone_guide': self._get_tone_guide('neutral'),
            'explanation_depth': 'moderate',
            'empathy_level': 'neutral'
        }

    def get_empathetic_prefix(self, sentiment_data: Dict[str, any]) -> str:
        """
        Get empathetic opening phrase based on sentiment.

        Args:
            sentiment_data: Result from analyze_sentiment()

        Returns:
            Opening phrase to prepend to system prompt
        """
        sentiment = sentiment_data['sentiment']
        empathy_level = sentiment_data['empathy_level']

        prefixes = {
            'frustrated': {
                'high': "I understand this is frustrating. Let me help resolve this for you right away. ",
                'moderate': "I can see this is causing issues. Let's work through this together. ",
            },
            'confused': {
                'high': "I'm here to help clarify this for you. Let's break it down step by step. ",
                'moderate': "Let me explain this clearly. ",
            },
            'satisfied': {
                'positive': "I'm glad things are working well! ",
            },
            'neutral': {
                'neutral': "",
            }
        }

        return prefixes.get(sentiment, {}).get(empathy_level, "")

    def create_sentiment_aware_prompt(
        self,
        base_query: str,
        sentiment_data: Dict[str, any],
        context: Optional[str] = None
    ) -> str:
        """
        Create a sentiment-aware prompt for the LLM.

        Args:
            base_query: User's original query
            sentiment_data: Result from analyze_sentiment()
            context: Optional context from RAG

        Returns:
            Enhanced prompt with sentiment guidance
        """
        sentiment = sentiment_data['sentiment']
        tone_guide = sentiment_data['tone_guide']
        depth = sentiment_data['explanation_depth']
        empathy_prefix = self.get_empathetic_prefix(sentiment_data)

        # Depth instructions
        depth_instructions = {
            'simple': "Keep explanations very simple and avoid technical details. Use everyday language.",
            'moderate': "Provide clear explanations with necessary details.",
            'detailed': "Provide comprehensive explanations with examples and step-by-step guidance.",
            'brief': "Be concise and to the point."
        }

        prompt = f"""You are an empathetic AI assistant. The customer appears to be {sentiment}.

TONE GUIDELINES: {tone_guide}

EXPLANATION DEPTH: {depth_instructions[depth]}

EMPATHETIC RESPONSE: {empathy_prefix}

USER QUERY: {base_query}
"""

        if context:
            prompt += f"\nRELEVANT CONTEXT:\n{context}\n"

        prompt += f"\nRespond in a way that addresses their {sentiment} state while providing accurate, helpful information."

        return prompt
