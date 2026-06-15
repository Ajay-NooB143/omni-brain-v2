def post_to_instagram(caption):
    """Post to Instagram (placeholder)"""
    print(f"[INSTAGRAM] Posted: {caption[:50]}...")
    return "insta_post_12345"

def extract_signal(text):
    """Extract trading signal from lesson text"""
    import re
    # Simple extraction - look for pair + direction
    pairs = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'BTC', 'ETH']
    for pair in pairs:
        if pair in text.upper():
            direction = "LONG" if "LONG" in text.upper() or "BULLISH" in text.upper() else "SHORT"
            return f"{pair} {direction}"
    return "NO_SIGNAL"

def send_telegram(message):
    """Send to Telegram (placeholder)"""
    print(f"[TELEGRAM] {message}")

def publish_reel(hinglish_caption, trading_lesson):
    """@forextrader_9 Reels → auto-post to Telegram channel"""
    # Post to Instagram
    instagram_post_id = post_to_instagram(hinglish_caption)
    
    # Extract trading signal if any
    if "setup" in trading_lesson.lower():
        signal = extract_signal(trading_lesson)
        # Post to Telegram with signal + reel link
        send_telegram(f"🎬 New Reel: {hinglish_caption}\n\n📊 Setup: {signal}")
    
    return {"instagram_id": instagram_post_id, "cross_posted": True}

def sync_instagram_reels():
    """Entry point for Instagram sync"""
    print("Instagram bridge module loaded")