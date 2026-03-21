from services.market_data import NIFTY50


def test_nifty50_has_50_symbols():
    assert len(NIFTY50) == 50
    assert len(set(NIFTY50)) == 50
