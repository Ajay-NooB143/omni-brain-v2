"""Sentiment analysis engine for forex markets."""


def forex_sentiment(pair):
    """Placeholder: return sentiment score 0-1."""
    return 0.5


def forex_sentiment_analyzer(pair, news_articles=None, social_signals=None, macro_events=None):
    """
    Analyze sentiment from news, social, and macro sources.

    Returns:
        dict: {
            'composite_sentiment': float (-1.0 to 1.0),
            'sentiment_label': 'BULLISH' | 'NEUTRAL' | 'BEARISH',
            'confidence': float (0-1),
            'sources': dict
        }
    """
    news_articles = news_articles or []
    social_signals = social_signals or {}
    macro_events = macro_events or []

    scores = []

    # News sentiment (simple keyword scoring)
    if news_articles:
        bullish_words = {'surge', 'rally', 'gain', 'rise', 'bull', 'strong', 'uptrend'}
        bearish_words = {'drop', 'fall', 'decline', 'crash', 'bear', 'weak', 'downtrend'}
        for article in news_articles[:5]:
            text = str(article).lower()
            b = sum(1 for w in bullish_words if w in text)
            s = sum(1 for w in bearish_words if w in text)
            scores.append((b - s) / max(b + s, 1))

    # Social signals
    if social_signals:
        social_score = social_signals.get('score', 0.0)
        scores.append(social_score)

    # Macro events
    if macro_events:
        for event in macro_events[:3]:
            impact = event.get('impact', 0)
            scores.append(impact / 10.0 if impact else 0.0)

    # Default neutral if no data
    if not scores:
        composite = 0.0
    else:
        composite = sum(scores) / len(scores)

    composite = max(-1.0, min(1.0, composite))

    if composite > 0.1:
        label = 'BULLISH'
    elif composite < -0.1:
        label = 'BEARISH'
    else:
        label = 'NEUTRAL'

    return {
        'composite_sentiment': round(composite, 3),
        'sentiment_label': label,
        'confidence': round(abs(composite), 3),
        'sources': {
            'news_count': len(news_articles),
            'social_count': len(social_signals) if isinstance(social_signals, dict) else 0,
            'macro_count': len(macro_events),
        },
    }
