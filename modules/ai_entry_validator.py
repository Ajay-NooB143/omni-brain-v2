import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def format_candles(candles):
    """Format recent candles for prompt"""
    return "\n".join([f"{c['time']}: O={c['open']} H={c['high']} L={c['low']} C={c['close']}" for c in candles[-10:]])

def extract_confidence(text):
    """Extract confidence score from AI response"""
    import re
    match = re.search(r'confidence[:\s]+(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 50

def ai_entry_filter(setup_data, market_context, recent_candles):
    """Real-time AI validation of setup"""
    conversation_history = []
    
    # Step 1: Describe the setup
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
    {format_candles(recent_candles)}
    
    Is this a valid entry? Verdict: EXECUTE / REFINE / BLOCK?
    """
    
    conversation_history.append({
        "role": "user",
        "content": setup_prompt
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=conversation_history
    )
    
    ai_verdict = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": ai_verdict
    })
    
    # Step 2: Ask for risk/reward assessment
    follow_up = "What's the risk/reward ratio and suggested stop loss for this setup?"
    conversation_history.append({
        "role": "user",
        "content": follow_up
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=conversation_history
    )
    
    rr_analysis = response.content[0].text
    
    # Parse verdicts
    if "EXECUTE" in ai_verdict.upper():
        action = "EXECUTE"
    elif "REFINE" in ai_verdict.upper() or "WAIT" in ai_verdict.upper():
        action = "REFINE"
    else:
        action = "BLOCK"
    
    return {
        "action": action,
        "ai_analysis": ai_verdict,
        "rr_analysis": rr_analysis,
        "confidence": extract_confidence(ai_verdict)
    }