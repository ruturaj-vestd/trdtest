from models import SentimentItem, SentimentReport


def test_sentiment_exports_available():
    item = SentimentItem(
        headline="x",
        source="y",
        timestamp=__import__("datetime").datetime.utcnow(),
        classification="neutral",
    )
    report = SentimentReport(items=[item])
    assert report.items[0].headline == "x"
