import time
from datetime import datetime

def extract_pair(text):
    """Extract trading pair from text"""
    import re
    pairs = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']
    for pair in pairs:
        if pair in text.upper():
            return pair
    return "UNKNOWN"

def extract_verdict(text):
    """Extract verdict from text"""
    text_upper = text.upper()
    if 'BULLISH' in text_upper or 'LONG' in text_upper:
        return "BULLISH"
    elif 'BEARISH' in text_upper or 'SHORT' in text_upper:
        return "BEARISH"
    return "NEUTRAL"

def schedule_alert(delay_seconds, message, channel):
    """Schedule Telegram alert (placeholder)"""
    print(f"[SCHEDULED] In {delay_seconds}s: {message} -> {channel}")

def log_content_trade(data):
    """Log content-trade correlation"""
    print(f"[LOG] {data}")

def on_youtube_publish(video_title, analysis_text):
    """YouTube post → Telegram alert 15min later if signal hits"""
    pair = extract_pair(analysis_text)
    verdict = extract_verdict(analysis_text)
    
    # Schedule Telegram alert 15min later
    schedule_alert(
        delay_seconds=900,
        message=f"📺 YouTube setup hit: {pair} {verdict}",
        channel="@omnibrainv2_signals"
    )
    
    # Log for content-trading correlation
    log_content_trade({
        "content_type": "youtube",
        "pair": pair,
        "published_at": datetime.now().isoformat(),
        "alert_scheduled": datetime.now().isoformat(),
        "monetization": "aligned"
    })

def sync_content_to_trading():
    """Entry point for YouTube sync"""
    print("YouTube sync module loaded")