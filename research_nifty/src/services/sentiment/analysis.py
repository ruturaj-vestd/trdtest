from __future__ import annotations

from datetime import datetime

import feedparser

from models import SentimentItem, SentimentReport
from services.llm import LLMRouter


async def compute_sentiment_report(ticker: str, ynews: list[dict], llm: LLMRouter) -> SentimentReport:
    items: list[SentimentItem] = []
    evidence: list[str] = []
    feeds = [
        f"https://news.google.com/rss/search?q={ticker.replace('.NS', '')}%20NSE",
    ]
    for f in feeds:
        parsed = feedparser.parse(f)
        for e in parsed.entries[:3]:
            items.append(
                SentimentItem(
                    headline=e.get("title", ""),
                    source="Google News",
                    timestamp=datetime.utcnow(),
                    classification="neutral",
                    catalyst_type="priced_in",
                    tag="continuation",
                )
            )
    for n in ynews[:3]:
        items.append(
            SentimentItem(
                headline=n.get("title", ""),
                source=n.get("publisher", "yfinance"),
                timestamp=datetime.utcfromtimestamp(n.get("providerPublishTime", int(datetime.utcnow().timestamp()))),
                classification="neutral",
                catalyst_type="incremental",
                tag="one_off",
            )
        )
    if not items:
        return SentimentReport(score=0.5, confidence=0.3, evidence=["No fresh news"], risks=["Data sparse"])

    prompt = "Classify sentiment for headlines: " + " | ".join(i.headline for i in items[:6])
    resp = await llm.complete(prompt, task="sentiment")
    txt = resp.text.lower()
    score = 0.5 + (0.2 if "bull" in txt else -0.2 if "bear" in txt else 0.0)
    score = max(0.0, min(1.0, score))

    cls = "bullish" if score > 0.6 else "bearish" if score < 0.4 else "neutral"
    for i in items:
        i.classification = cls
    evidence.append(resp.text[:200])
    risks = ["Potential event volatility"] if "regime" in txt or "probe" in txt else []
    return SentimentReport(score=score, confidence=0.65, evidence=evidence, risks=risks, items=items)
