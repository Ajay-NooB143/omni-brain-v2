import json
import os
import re
import time
from anthropic import Anthropic


class AIEntryValidator:
    def __init__(self, max_retries=3):
        self.client = Anthropic()
        self.max_retries = max_retries

    def format_candles(self, candles):
        """Format recent candles for prompt"""
        return "\n".join([
            f"{c['time']}: O={c['open']} H={c['high']} L={c['low']} C={c['close']}"
            for c in candles[-10:]
        ])

    def extract_confidence(self, text):
        """Extract confidence score from AI response"""
        match = re.search(r'confidence[:\s]+(\d+)', text, re.IGNORECASE)
        return int(match.group(1)) if match else 50

    def validate_setup(self, setup_data, market_context, recent_candles):
        """Real-time AI validation of setup with retry + exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                setup_prompt = f"""
                Analyze this forex entry setup:

                Pair: {setup_data['pair']}
                Timeframe: {setup_data['timeframe']}
                Entry Price: {setup_data['entry_price']}

                Technical Confluence:
                - Order Block: {setup_data['order_block']}
                - Fair Value Gap: {setup_data['fvg']}
                - VWAP: {setup_data['vwap']}
                - Market Structure: {setup_data['structure']}

                Market Context:
                - Volatility: {market_context['volatility']}
                - Sentiment: {market_context['sentiment']}
                - News Impact: {market_context['news_impact']}
                - Time of Day: {market_context['session']}

                Recent Price Action:
                {self.format_candles(recent_candles)}

                Is this a valid entry? Verdict: EXECUTE / REFINE / BLOCK?
                """

                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[{"role": "user", "content": setup_prompt}],
                    timeout=30
                )

                if not response.content:
                    raise ValueError("Empty response from AI")

                verdict_text = response.content[0].text

                if "EXECUTE" in verdict_text.upper():
                    verdict = "EXECUTE"
                elif "REFINE" in verdict_text.upper():
                    verdict = "REFINE"
                else:
                    verdict = "BLOCK"

                return {
                    'action': verdict,
                    'confidence': 0.9 if verdict == "EXECUTE" else 0.5,
                    'error': None
                }

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return {
                        'action': 'BLOCK',
                        'confidence': 0.0,
                        'error': str(e)
                    }


def ai_entry_filter(setup_data, market_context, recent_candles):
    """Backward-compatible wrapper"""
    validator = AIEntryValidator()
    return validator.validate_setup(setup_data, market_context, recent_candles)
