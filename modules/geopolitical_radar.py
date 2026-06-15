def geopolitical_impact_scorer(region, event_type, historical_precedent=None):
    """Model market reaction to geopolitical shocks"""
    precedents = {
        "strait_threat": {"oil": +5.2, "usd": +1.8, "gold": +2.1},
        "election_shock": {"volatility": +40, "equity": -3.5},
        "sanctions": {"ruble": -8, "brent": +4}
    }

    return {
        "event": event_type,
        "historical_reaction": precedents.get(event_type, historical_precedent),
        "pairs_affected": ["XAUUSD", "EURUSD", "USDCAD"],
        "timing": "next_6_hours_critical"
    }


def social_media_sentiment_cluster(twitter_mentions=None, reddit_wsb_posts=None,
                                    telegram_wallets=None):
    """Retail vs whale sentiment divergence"""
    twitter_mentions = twitter_mentions or {}
    reddit_wsb_posts = reddit_wsb_posts or {}
    telegram_wallets = telegram_wallets or {}

    total_tweets = twitter_mentions.get("total", 1)
    bullish_tweets = twitter_mentions.get("bullish", 0)

    large_wallet_inflows = telegram_wallets.get("large_inflows", 0)
    volume = telegram_wallets.get("total_volume", 1)

    retail_bullish = bullish_tweets / total_tweets if total_tweets > 0 else 0
    whale_accumulation = large_wallet_inflows / volume if volume > 0 else 0

    if retail_bullish > 0.75 and whale_accumulation < 0.2:
        return {
            "signal": "RETAIL_FOMO_TOP",
            "trade": "SHORT",
            "confidence": "HIGH"
        }

    return {"signal": "NEUTRAL", "trade": "WAIT", "confidence": "LOW"}
