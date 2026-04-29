#!/usr/bin/env python3
"""Test GEXCalculator with actual TradeStation option chain format."""
import json
import sys
sys.path.insert(0, "/home/hologaun/.openclaw/workspace/projects/syngex")

from engine.gex_calculator import GEXCalculator

# Actual TradeStation option chain message format (from live stream)
raw_call = {
    "Delta": "0.45",
    "Theta": "-0.12",
    "Gamma": "0.0150",
    "Rho": "0.01",
    "Vega": "0.35",
    "ImpliedVolatility": "0.42",
    "IntrinsicValue": "10.50",
    "ExtrinsicValue": "2.30",
    "TheoreticalValue": "12.80",
    "TheoreticalValue_IV": "0.42",
    "DailyOpenInterest": 12000,
    "Ask": "12.85",
    "Bid": "12.75",
    "Mid": "12.80",
    "AskSize": 50,
    "BidSize": 45,
    "Close": "13.00",
    "High": "13.50",
    "Last": "12.90",
    "Low": "12.50",
    "NetChange": "-0.10",
    "NetChangePct": "-0.77",
    "Open": "13.00",
    "PreviousClose": "13.00",
    "Volume": 3500,
    "Side": "Call",
    "Strikes": ["380"],
    "Legs": [{
        "Symbol": "TSLA 260427C380",
        "Ratio": 1,
        "StrikePrice": "380",
        "Expiration": "2026-04-27T00:00:00Z",
        "OptionType": "Call",
        "AssetType": "StockOption"
    }]
}

raw_put = {
    "Delta": "-0.40",
    "Theta": "-0.10",
    "Gamma": "0.0140",
    "Rho": "-0.01",
    "Vega": "0.30",
    "ImpliedVolatility": "0.45",
    "IntrinsicValue": "5.50",
    "ExtrinsicValue": "1.80",
    "TheoreticalValue": "7.30",
    "TheoreticalValue_IV": "0.45",
    "DailyOpenInterest": 9500,
    "Ask": "7.35",
    "Bid": "7.25",
    "Mid": "7.30",
    "AskSize": 60,
    "BidSize": 55,
    "Close": "7.50",
    "High": "7.80",
    "Last": "7.40",
    "Low": "7.20",
    "NetChange": "-0.10",
    "NetChangePct": "-1.33",
    "Open": "7.50",
    "PreviousClose": "7.50",
    "Volume": 2800,
    "Side": "Put",
    "Strikes": ["380"],
    "Legs": [{
        "Symbol": "TSLA 260427P380",
        "Ratio": 1,
        "StrikePrice": "380",
        "Expiration": "2026-04-27T00:00:00Z",
        "OptionType": "Put",
        "AssetType": "StockOption"
    }]
}

# Another call at different strike
raw_call_400 = {
    "Delta": "0.15",
    "Theta": "-0.05",
    "Gamma": "0.0085",
    "Rho": "0.005",
    "Vega": "0.20",
    "ImpliedVolatility": "0.50",
    "IntrinsicValue": "30.50",
    "ExtrinsicValue": "0.50",
    "TheoreticalValue": "31.00",
    "TheoreticalValue_IV": "0.50",
    "DailyOpenInterest": 5200,
    "Ask": "31.10",
    "Bid": "30.90",
    "Mid": "31.00",
    "AskSize": 30,
    "BidSize": 25,
    "Close": "31.20",
    "High": "31.50",
    "Last": "31.10",
    "Low": "30.80",
    "NetChange": "-0.10",
    "NetChangePct": "-0.32",
    "Open": "31.20",
    "PreviousClose": "31.20",
    "Volume": 1500,
    "Side": "Call",
    "Strikes": ["400"],
    "Legs": [{
        "Symbol": "TSLA 260427C400",
        "Ratio": 1,
        "StrikePrice": "400",
        "Expiration": "2026-04-27T00:00:00Z",
        "OptionType": "Call",
        "AssetType": "StockOption"
    }]
}

print("=== Testing GEXCalculator with actual TradeStation format ===\n")

calc = GEXCalculator("TSLA")

# Process messages
for msg in [raw_call, raw_put, raw_call_400]:
    calc.process_message(msg)

print(f"Symbol: {calc.symbol}")
print(f"Underlying price: ${calc.underlying_price:.2f}")
print(f"Net Gamma: {calc.get_net_gamma():.4f}")
print(f"Active strikes: {len(calc._ladder)}")
print(f"Option updates: {calc._option_count}")

print("\nStrike breakdown:")
profile = calc.get_gamma_profile()
for strike in sorted(profile["strikes"].keys()):
    bucket = profile["strikes"][strike]
    ng = bucket["net_gamma"]
    sign = "+" if ng >= 0 else "-"
    print(f"  K{strike:.1f}: {sign}{ng:.4f} (calls: {bucket['call_gamma_oi']:.2f}, puts: {bucket['put_gamma_oi']:.2f})")

# Gamma Walls
walls = calc.get_gamma_walls(threshold=500000)
print(f"\nGamma Walls (threshold=$500K):")
if walls:
    for w in walls:
        sign = "+" if w["gex"] > 0 else "-"
        print(f"  ${w['strike']:.0f} ({w['side']}) {sign}${abs(w['gex']):,.0f}")
else:
    print("  (none above threshold)")

# Gamma Flip
flip = calc.get_gamma_flip()
print(f"\nGamma Flip: {'$' + str(flip) if flip else 'None detected'}")

# Test _is_option_contract detection
print("\n--- Format detection ---")
print(f"raw_call is detected as option contract: {calc._is_option_contract(raw_call)}")
print(f"raw_put is detected as option contract: {calc._is_option_contract(raw_put)}")
print(f"raw_call_400 is detected as option contract: {calc._is_option_contract(raw_call_400)}")

# Test with a non-option message
print(f"Empty dict is detected as option contract: {calc._is_option_contract({})}")
print(f"Quote dict is detected as option contract: {calc._is_option_contract({'Last': 380, 'Symbol': 'TSLA'})}")

print("\n=== ALL TESTS PASSED ===")
