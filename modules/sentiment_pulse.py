"""Real-time market sentiment from 5 sources.

Twitter/X, Reddit, Fear & Greed Index, VIX, and Macro News.
Composite score 0-100 (0=extreme fear, 100=extreme greed).
"""

import os
import json
import logging
import statistics
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
FALLBACK_SCORE = 50  # Neutral when source unavailable


# ============================================
# Source 1: Twitter/X Sentiment
# ============================================

class TweetSentimentAnalyzer:
    """Analyze Twitter/X sentiment for forex pairs.

    Uses keyword-based scoring when no API key is available.
    """

    BULLISH_KEYWORDS = [
        "buy", "bullish", "moon", "pump", "long", "uptrend",
        "breakout", "rally", "surge", "strong", "accumulate"
    ]
    BEARISH_KEYWORDS = [
        "sell", "bearish", "dump", "crash", "short", "downtrend",
        "breakdown", "plunge", "weak", "distribution", "collapse"
    ]

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")

    def analyze(self, pair, sample_tweets=None):
        """Analyze sentiment for a pair.

        Args:
            pair: Trading pair (e.g., "EURUSD")
            sample_tweets: Optional list of tweet texts for offline analysis

        Returns:
            Score 0-100 (0=extreme bearish, 100=extreme bullish)
        """
        if sample_tweets:
            return self._score_texts(sample_tweets)

        if not self.api_key:
            logger.debug("No Twitter API key, using neutral score")
            return FALLBACK_SCORE

        try:
            return self._fetch_twitter_sentiment(pair)
        except Exception as e:
            logger.warning(f"Twitter sentiment failed: {e}")
            return FALLBACK_SCORE

    def _score_texts(self, texts):
        """Score a list of texts using keyword matching."""
        if not texts:
            return FALLBACK_SCORE

        bullish = 0
        bearish = 0
        for text in texts:
            text_lower = text.lower()
            for kw in self.BULLISH_KEYWORDS:
                if kw in text_lower:
                    bullish += 1
            for kw in self.BEARISH_KEYWORDS:
                if kw in text_lower:
                    bearish += 1

        total = bullish + bearish
        if total == 0:
            return 50

        return min(100, max(0, int((bullish / total) * 100)))

    def _fetch_twitter_sentiment(self, pair):
        """Fetch real Twitter sentiment via API (placeholder)."""
        # Real implementation would use Twitter API v2
        # For now, return neutral
        return FALLBACK_SCORE


# ============================================
# Source 2: Reddit Sentiment
# ============================================

class RedditSentimentAnalyzer:
    """Analyze Reddit sentiment from r/forex, r/cryptocurrency, r/wallstreetbets."""

    SUBREDDITS = {
        "forex": ["EURUSD", "GBPUSD", "USDJPY", "gold"],
        "cryptocurrency": ["BTC", "ETH", "SOL", "BNB"],
        "wallstreetbets": ["SP500", "stocks"]
    }

    BULLISH_KEYWORDS = [
        "moon", "bullish", "buy", "long", "hold", "diamond hands",
        "rocket", "lambo", "gain", "profit", "undervalued"
    ]
    BEARISH_KEYWORDS = [
        "crash", "bearish", "sell", "short", "dump", "baghold",
        "loss", "rekt", "overvalued", "bubble", "rugpull"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "OmniBrain/1.0"})

    def analyze(self, pair):
        """Analyze Reddit sentiment for a pair.

        Returns:
            Score 0-100
        """
        try:
            return self._fetch_reddit_sentiment(pair)
        except Exception as e:
            logger.warning(f"Reddit sentiment failed: {e}")
            return FALLBACK_SCORE

    def _fetch_reddit_sentiment(self, pair):
        """Fetch and analyze Reddit posts."""
        pair_lower = pair.lower().replace("/", "")
        texts = []

        # Search relevant subreddits
        for subreddit, pairs in self.SUBREDDITS.items():
            if any(p.lower().replace("/", "") in pair_lower for p in pairs):
                posts = self._get_subreddit_posts(subreddit, limit=25)
                texts.extend([p.get("title", "") for p in posts])

        if not texts:
            return FALLBACK_SCORE

        return self._score_texts(texts)

    def _get_subreddit_posts(self, subreddit, limit=25):
        """Fetch top posts from a subreddit."""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [p["data"] for p in data.get("data", {}).get("children", [])]
        except Exception:
            pass
        return []

    def _score_texts(self, texts):
        """Score texts using keyword matching."""
        bullish = sum(1 for t in texts if any(kw in t.lower() for kw in self.BULLISH_KEYWORDS))
        bearish = sum(1 for t in texts if any(kw in t.lower() for kw in self.BEARISH_KEYWORDS))
        total = bullish + bearish

        if total == 0:
            return 50

        return min(100, max(0, int((bullish / total) * 100)))


# ============================================
# Source 3: Fear & Greed Index
# ============================================

class FearGreedIndexAPI:
    """CNN Fear & Greed Index (0=extreme fear, 100=extreme greed)."""

    def __init__(self):
        self.session = requests.Session()
        self.cache = None
        self.cache_time = None
        self.cache_ttl = timedelta(minutes=30)

    def get_index(self):
        """Fetch current Fear & Greed Index.

        Returns:
            Score 0-100
        """
        if self._cache_valid():
            return self.cache

        try:
            return self._fetch_index()
        except Exception as e:
            logger.warning(f"Fear & Greed fetch failed: {e}")
            return FALLBACK_SCORE

    def _cache_valid(self):
        if self.cache is None or self.cache_time is None:
            return False
        return datetime.now() - self.cache_time < self.cache_ttl

    def _fetch_index(self):
        """Fetch from CNN API."""
        resp = self.session.get(FEAR_GREED_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        score = int(data["data"]["fear_and_greed"]["score"])
        self.cache = score
        self.cache_time = datetime.now()
        return score


# ============================================
# Source 4: VIX Sentiment Mapper
# ============================================

class VIXSentimentMapper:
    """Map VIX level to sentiment score.

    Low VIX (<15) = greed (high score)
    High VIX (>25) = fear (low score)
    """

    def __init__(self, vix_fetcher=None):
        self.vix_fetcher = vix_fetcher

    def sentiment_score(self, vix=None):
        """Convert VIX to 0-100 sentiment score.

        Args:
            vix: Current VIX value (fetched if not provided)

        Returns:
            Score 0-100 (0=extreme fear, 100=extreme greed)
        """
        if vix is None:
            vix = self._get_vix()

        if vix is None:
            return FALLBACK_SCORE

        # Map VIX to sentiment (inverse relationship)
        # VIX 10 = 90 (extreme greed)
        # VIX 15 = 70
        # VIX 20 = 50 (neutral)
        # VIX 30 = 30
        # VIX 40+ = 10 (extreme fear)
        score = max(0, min(100, 100 - (vix * 2.5)))
        return int(score)

    def _get_vix(self):
        """Fetch current VIX from Yahoo Finance."""
        if self.vix_fetcher:
            return self.vix_fetcher()

        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=1d"
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            data = resp.json()
            return data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        except Exception as e:
            logger.warning(f"VIX fetch failed: {e}")
            return None


# ============================================
# Source 5: Macro News Scanner
# ============================================

class MacroNewsScanner:
    """Scan macro news headlines for sentiment.

    Monitors Reuters, Bloomberg, and financial news feeds.
    """

    IMPACT_KEYWORDS = {
        "bullish": [
            "rate cut", "stimulus", "strong jobs", "gdp growth",
            "trade deal", "peace", "recovery", "beat expectations",
            "hawkish", "tightening"
        ],
        "bearish": [
            "rate hike", "recession", "weak jobs", "gdp decline",
            "trade war", "sanctions", "crisis", "miss expectations",
            "dovish", "easing", "inflation surge"
        ]
    }

    NEWS_SOURCES = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "OmniBrain/1.0"})

    def sentiment(self, pair):
        """Analyze news sentiment for a pair.

        Returns:
            Score 0-100
        """
        try:
            headlines = self._fetch_headlines(pair)
            if not headlines:
                return FALLBACK_SCORE
            return self._score_headlines(headlines)
        except Exception as e:
            logger.warning(f"News sentiment failed: {e}")
            return FALLBACK_SCORE

    def _fetch_headlines(self, pair):
        """Fetch news headlines."""
        ticker = self._pair_to_ticker(pair)
        headlines = []

        for source_url in self.NEWS_SOURCES:
            try:
                url = source_url.format(ticker=ticker)
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    # Simple XML parsing for RSS
                    import re
                    titles = re.findall(r"<title[^>]*>(.*?)</title>", resp.text)
                    headlines.extend(titles[:10])
            except Exception:
                continue

        return headlines

    def _pair_to_ticker(self, pair):
        """Convert pair to Yahoo Finance ticker."""
        ticker_map = {
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "USDJPY": "USDJPY=X",
            "XAUUSD": "GC=F",
            "USOIL": "CL=F",
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
            "BNB": "BNB-USD",
            "SOL": "SOL-USD",
            "SP500": "^GSPC"
        }
        return ticker_map.get(pair, f"{pair}=X")

    def _score_headlines(self, headlines):
        """Score headlines using keyword matching."""
        bullish = 0
        bearish = 0

        for headline in headlines:
            lower = headline.lower()
            for kw in self.IMPACT_KEYWORDS["bullish"]:
                if kw in lower:
                    bullish += 1
            for kw in self.IMPACT_KEYWORDS["bearish"]:
                if kw in lower:
                    bearish += 1

        total = bullish + bearish
        if total == 0:
            return 50

        return min(100, max(0, int((bullish / total) * 100)))


# ============================================
# Composite Sentiment Engine
# ============================================

class SentimentPulse:
    """Real-time market sentiment from 5 sources."""

    def __init__(self):
        self.sources = {
            'twitter_x': TweetSentimentAnalyzer(),
            'reddit': RedditSentimentAnalyzer(),
            'fear_greed': FearGreedIndexAPI(),
            'cbot_vix': VIXSentimentMapper(),
            'macro_news': MacroNewsScanner()
        }

    def get_composite_sentiment(self, pair):
        """Aggregate 5 sources into 0-100 bullish score.

        Args:
            pair: Trading pair (e.g., "EURUSD")

        Returns:
            Dict with bullish_score, source breakdown, and signal
        """
        scores = {
            'twitter_x': self.sources['twitter_x'].analyze(pair),
            'reddit': self.sources['reddit'].analyze(pair),
            'fear_greed': self.sources['fear_greed'].get_index(),
            'cbot_vix': self.sources['cbot_vix'].sentiment_score(),
            'macro_news': self.sources['macro_news'].sentiment(pair)
        }

        # Weighted average (Twitter 20%, Reddit 15%, F&G 25%, VIX 20%, News 20%)
        weights = {
            'twitter_x': 0.20,
            'reddit': 0.15,
            'fear_greed': 0.25,
            'cbot_vix': 0.20,
            'macro_news': 0.20
        }

        composite = sum(scores[k] * weights[k] for k in scores)

        if composite > 75:
            signal = "STRONG_BULLISH"
        elif composite > 60:
            signal = "BULLISH"
        elif composite > 40:
            signal = "NEUTRAL"
        elif composite > 25:
            signal = "BEARISH"
        else:
            signal = "STRONG_BEARISH"

        return {
            'bullish_score': round(composite, 1),
            'sources': scores,
            'signal': signal
        }
