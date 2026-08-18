"""L7: orb_probe _parse_depth_line/_parse_depth_agg_line sort by best level.

Old code assumed bids[0]/asks[0] was already the best (highest bid / lowest
ask). If the feed returns levels unsorted, best_bid/best_ask were wrong. After
the fix, both functions sort explicitly before selecting the top level.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import orb_probe


def _parse_depth_line(levels):
    """Call orb_probe._parse_depth_line with a raw depth-quotes message."""
    return orb_probe._parse_depth_line({"symbol": "TEST", "Bids": levels, "Asks": levels})


def test_best_bid_is_highest_even_when_unsorted():
    # Feed reversed/unsorted levels: a lower bid first, higher bid later.
    raw = {
        "symbol": "TEST",
        "Bids": [
            {"Price": "495.5", "Size": 10},
            {"Price": "497.0", "Size": 25},
            {"Price": "496.1", "Size": 12},
        ],
        "Asks": [
            {"Price": "497.5", "Size": 9},
        ],
    }
    parsed = orb_probe._parse_depth_line(raw)
    # Best bid = highest = 497.0
    assert parsed["best_bid"] == 497.0


def test_best_ask_is_lowest_even_when_unsorted():
    raw = {
        "symbol": "TEST",
        "Bids": [{"Price": "496.0", "Size": 5}],
        "Asks": [
            {"Price": "500.0", "Size": 8},
            {"Price": "498.5", "Size": 15},
            {"Price": "499.0", "Size": 7},
        ],
    }
    parsed = orb_probe._parse_depth_line(raw)
    # Best ask = lowest = 498.5
    assert parsed["best_ask"] == 498.5


def test_empty_depth_returns_zero():
    parsed = orb_probe._parse_depth_line({"symbol": "TEST", "Bids": [], "Asks": []})
    assert parsed["best_bid"] == 0.0
    assert parsed["best_ask"] == 0.0


def test_parse_depth_agg_line_best_levels():
    raw = {
        "symbol": "TEST",
        "Bids": [
            {"Price": "100.0", "TotalSize": 10, "NumParticipants": 2},
            {"Price": "101.5", "TotalSize": 30, "NumParticipants": 3},
        ],
        "Asks": [
            {"Price": "102.5", "TotalSize": 20, "NumParticipants": 2},
            {"Price": "101.9", "TotalSize": 12, "NumParticipants": 1},
        ],
    }
    parsed = orb_probe._parse_depth_agg_line(raw)
    assert parsed["best_bid"] == 101.5   # highest bid
    assert parsed["best_ask"] == 101.9   # lowest ask

# ---------------------------------------------------------------------------
# L6: orb_probe _parse_option_symbol fractional-strike handling
# (grounded in real TS API captures: "TSLA 260511C382.5", "TSLA 260511P422.5")
# ---------------------------------------------------------------------------

def test_parse_whole_strike():
    assert orb_probe._parse_option_symbol("TSLA 260511C465") == ("TSLA", "call", 465.0)


def test_parse_fractional_strike():
    # Real captured format: decimal point literal, fractional strike must survive
    assert orb_probe._parse_option_symbol("TSLA 260511C382.5") == ("TSLA", "call", 382.5)


def test_parse_fractional_put():
    assert orb_probe._parse_option_symbol("TSLA 260511P422.5") == ("TSLA", "put", 422.5)


def test_parse_padded_whole_strike():
    assert orb_probe._parse_option_symbol("SPY  260116P0500") == ("SPY", "put", 500.0)


def test_parse_doc_example_fractional():
    assert orb_probe._parse_option_symbol("MSFT 110122C27.5") == ("MSFT", "call", 27.5)


def test_parse_invalid_strike_rejected_not_parsed():
    # Non-numeric strike (letters) must be rejected loudly, not silently wrong
    assert orb_probe._parse_option_symbol("TSLA 260511CABC") == ("unknown", "", 0.0)


def test_parse_malformed_short_suffix():
    assert orb_probe._parse_option_symbol("TSLA 2605C4") == ("unknown", "", 0.0)
