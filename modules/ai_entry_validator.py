"""OmniBrain V2 — AI Entry Validator (OpenRouter / Claude 3.5 Sonnet)"""

import json
import os
import re
import time
from openai import OpenAI


class AIEntryValidator:
    def __init__(self, max_retries=3):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"),
            default_headers={
                "HTTP-Referer": "https://github.com/Ajay-NooB143/omni-brain-v2",
                "X-Title": "OmniBrain V2",
            },
        )
        self.max_retries = max_retries

    def format_candles(self, candles):
        return "\n".join([
            f"{c['time']}: O={c['open']} H={c['high']} L={c['low']} C={c['close']}"
            for c in candles[-10:]
        ])

    def validate_setup(self, setup_data, market_context, recent_candles):
        for attempt in range(self.max_retries):
            try:
                setup_prompt = f"""
Analyze this XAU/USD entry setup:

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

Is this a valid entry? Respond with EXACTLY one word: EXECUTE, REFINE, or BLOCK. Then a brief reason.
"""

                response = self.client.chat.completions.create(
                    model="~anthropic/claude-sonnet-latest",
                    messages=[{"role": "user", "content": setup_prompt}],
                    max_tokens=10,
                )

                if not response.choices:
                    raise ValueError("Empty response from AI")

                verdict_text = response.choices[0].message.content or ""

                if "EXECUTE" in verdict_text.upper():
                    verdict = "EXECUTE"
                elif "REFINE" in verdict_text.upper():
                    verdict = "REFINE"
                else:
                    verdict = "BLOCK"

                return {
                    'action': verdict,
                    'confidence': 0.9 if verdict == "EXECUTE" else 0.5,
                    'reason': verdict_text[:200],
                    'error': None,
                }

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'action': 'BLOCK',
                    'confidence': 0.0,
                    'reason': None,
                    'error': str(e),
                }


def ai_entry_filter(setup_data, market_context, recent_candles):
    validator = AIEntryValidator()
    return validator.validate_setup(setup_data, market_context, recent_candles)
