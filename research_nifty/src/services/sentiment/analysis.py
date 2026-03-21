from __future__ import annotations

from datetime import datetime
from time import mktime

import feedparser

from models import SentimentItem, SentimentReport
from services.llm import LLMRouter


def _to_dt(struct_time) -> datetime:
    if not struct_time:
        return datetime.utcnow()
    return datetime.utcfromtimestamp(mktime(struct_time))


async def compute_sentiment_report(ticker: str, ynews: list[dict], llm: LLMRouter) -> SentimentReport:
    items: list[SentimentItem] = []
    evidence: list[str] = []
    query = ticker.replace(".NS", "")
    feeds = [
        f"https://news.google.com/rss/search?q={query}%20NSE%20stock&hl=en-IN&gl=IN&ceid=IN:en",
        f"https://news.google.com/rss/search?q={query}%20earnings&hl=en-IN&gl=IN&ceid=IN:en",
    ]

    for f in feeds:
        parsed = feedparser.parse(f)
        for e in parsed.entries[:10]:
            items.append(
                SentimentItem(
                    headline=e.get("title", ""),
                    source=e.get("source", {}).get("title", "Google News") if isinstance(e.get("source"), dict) else "Google News",
                    timestamp=_to_dt(e.get("published_parsed")),
                    classification="neutral",
                    catalyst_type="incremental",
                    tag="continuation",
                )
            )

    for n in ynews[:15]:
        items.append(
            SentimentItem(
                headline=n.get("title", ""),
                source=n.get("publisher", "yfinance"),
                timestamp=datetime.utcfromtimestamp(n.get("providerPublishTime", int(datetime.utcnow().timestamp()))),
                classification="neutral",
                catalyst_type="incremental",
                tag="earnings" if "earn" in (n.get("title", "").lower()) else "one_off",
            )
        )

    if not items:
        return SentimentReport(score=0.5, confidence=0.3, evidence=["No fresh news"], risks=["Data sparse"])

    # Keep only latest unique headlines.
    dedup: dict[str, SentimentItem] = {}
    for item in items:
        dedup[item.headline] = item
    items = sorted(dedup.values(), key=lambda x: x.timestamp, reverse=True)[:12]

    prompt = (
        "Classify these headlines into bullish/bearish/neutral with one-sentence rationale and risk tag: "
        + " | ".join(f"[{i.timestamp.isoformat()}] {i.headline}" for i in items)
    )
    resp = await llm.complete(prompt, task="sentiment")
    txt = resp.text.lower()
    score = 0.5 + (0.2 if "bull" in txt else -0.2 if "bear" in txt else 0.0)
    score = max(0.0, min(1.0, score))

    cls = "bullish" if score > 0.6 else "bearish" if score < 0.4 else "neutral"
    for i in items:
        i.classification = cls
    evidence.append(resp.text[:300])
    risks = ["Potential event volatility"] if any(k in txt for k in ["probe", "ban", "fraud", "downgrade", "lawsuit"]) else []
    return SentimentReport(score=score, confidence=0.7, evidence=evidence, risks=risks, items=items)
