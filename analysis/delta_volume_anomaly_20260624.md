# Delta Volume Exhaustion Anomaly Report — 2026-06-24

**Status:** CONFIRMED BUG  
**Severity:** HIGH — Strategy appears profitable but all outcomes misclassified  
**Root Cause:** Stop-loss placed on the wrong side of entry, causing every trade to be flagged as "LOSS" despite being profitable  

---

## Executive Summary

The `delta_volume_exhaustion` strategy produced 5,368 signals across all symbols today, all classified as **LOSS** with **0.0% win rate**. Yet every single trade generated **positive P&L**, averaging **$2.19 per signal** (range: $1.02–$4.32). This was not a data bug or artifact — it is a systematic logic error in stop-placement.

---

## What Happened

### The Bug: Inverted Stop-Loss Direction

The `delta_volume_exhaustion` strategy is a **mean-reversion fade**: it detects an exhausted trend and enters in the OPPOSITE direction. A key design principle is:
- **When a UP trend exhausts → go SHORT** (betting the price falls back down)
- **When a DOWN trend exhausts → go LONG** (betting the price rises back up)

However, the stop-loss calculation uses `reverse = -1` for SHORT and `+1` for LONG positions, then computes:

```python
stop = entry * (1 + swing_pct * reverse)
```

For a **SHORT** entry ($527.18), with `reverse = -1`:
- Stop = 527.18 × (1 − 0.008) = **$522.96**
- The stop is **BELOW** entry

For a **LONG** entry ($527.18), with `reverse = +1`:
- Stop = 527.18 × (1 + 0.008) = **$531.39**
- The stop is **ABOVE** entry

**Both stops are on the WRONG SIDE.** 

A short's stop should be ABOVE entry (protects against price rising further).  
A long's stop should be BELOW entry (protects against price falling further).

By placing them on the profit-side, the stop triggers **every time the trade moves in your favor by just 0.8%** — exactly when you've earned money.

### Why Every Trade Is a "Loss" Despite Positive P&L

The SignalTracker resolves trades like this:

```python
if open_sig.direction == "SHORT" and price >= open_sig.stop:
    # LOSS — price hit stop from below? No, price >= stop
    ... LOSS
```

For our SHORT example:
- Entry: $527.18, Stop: $522.96 (WRONG — should be above entry)
- Market dips to $522.96 → price < stop → NOT triggered
- Market continues dipping to $518.42... wait, that's even lower.

Actually looking more carefully at the resolution flow:

```python
if open_sig.direction == "SHORT" and price >= open_sig.stop:
    return LOSS   # STOP HIT (price rose too high for short)
    
if open_sig.direction == "SHORT" and price <= open_sig.target:
    return WIN    # TARGET HIT (price dropped enough)
```

For our SHORT:
- Stop = $522.96 (below entry!)
- Target = $526.64 (above entry!)
- Actual exit = $522.96 = **EXACTLY the stop**
- Since price fell TO the stop, price ≤ target ($522.96 ≤ $526.64) should fire first!

But it fired as LOSS, which means price was checked at $522.96 and:
- Price ≥ stop? $522.96 ≥ $522.96 → **TRUE** → immediately returns LOSS

**The bug is that the stop check comes BEFORE the target check AND the stop IS the exit point.** When price hits the inverted stop, it simultaneously satisfies both conditions but the stop check fires first.

### Verification

All 5,368 signals show:
- 100% classified as LOSS
- 100% had positive P&L ($1.02 minimum, $4.32 maximum)
- 100% had exit_price ≈ stop price (traded exactly to the stop)
- Average hold time: ~1 second (instant resolution at the inverted stop)

---

## By Confidence Level

| Bucket | Signals | Avg P&L/Signal | Min P&L | Max P&L | Avg Hold |
|--------|---------|---------------|---------|---------|----------|
| 5-9%   | 699     | $2.39         | $1.03   | $4.31   | 1.0s     |
| 10-19% | 2,524   | $2.31         | $1.02   | $4.32   | 1.0s     |
| 20-29% | 1,464   | $2.12         | $1.02   | $4.31   | 1.0s     |
| 30-39% | 568     | $1.71         | $1.02   | $4.25   | 1.0s     |
| 40-49% | 121     | $1.86         | $1.02   | $4.23   | 1.0s     |

**Total theoretical daily P&L: ~$11,784** (if these were real, actionable trades)

Note the higher-confidence buckets produce LOWER average P&L — confirming they tend to pick larger underlying prices where the 0.8% absolute dollar amount still works out, but the risk profile shifts.

---

## Financial Impact Assessment

### If This Were Real Trading
At $2.19 avg P&L × 5,368 signals = **~$11,756 daily revenue**. That would make this one of our most active strategies.

### Reality
This is completely non-functional. Every trade exits at ~1 second with exactly 0.8% risk taken — no actual exposure to market movement. It's a cost-center that wastes CPU cycles and pollutes signal logs.

Even accounting for commissions and slippage, this strategy would burn cash in production:
- Estimated commission per round-trip: ~$0.65-$1.30
- Slippage at 1-second holds: variable but meaningful
- Net: likely slightly negative after costs

---

## The Fix

Two approaches, either of which would resolve this:

### Option 1: Fix Stop Logic (Quick Fix)

Change the stop formula so the stop is always on the loss side:

```python
# Current (BUGGY):
reverse = -1 if trend_direction == "UP" else 1  # reversed logic
stop = entry * (1 + swing_pct * reverse)

# Fixed:
direction_mult = -1 if direction == "LONG" else 1  # based on SIGNAL direction, not trend
stop = entry + (entry - stop) if direction == "SHORT" else entry + (stop - entry)
# Or simply:
if direction == "SHORT":
    stop = entry + risk  # ABOVE entry
else:
    stop = entry - risk  # BELOW entry
```

### Option 2: Fix Exit Priority (Better Fix)

Reorder the resolution checks so TARGET takes priority over STOP when both could trigger simultaneously. The current order always checks STOP first, which catches the inverted-stop cases. But properly fixing Option 1 makes this moot.

### Option 3: Both

Do both. It's defensive programming.

---

## Recommendations

1. **IMMEDIATE:** Flag `delta_volume_exhaustion` as broken/inactive until fixed. Add it to the blocklist or set max_hold_seconds = 0 effectively disables new signals, but old signals may persist.

2. **HIGH PRIORITY:** Fix the stop-loss calculation in `strategies/layer2/delta_volume_exhaustion.py`. The fix is straightforward — change line ~161 from using `reverse = -1 if trend_direction == "UP"` to use the actual signal direction.

3. **MEDIUM:** Review all other strategies for similar stop-direction bugs. While only DVE showed this extreme pattern (all-positive-Loss), other strategies with stop/target configurations worth auditing.

4. **LOW:** Consider adding automated regression tests that verify: for every signal, `stop` must be on the correct side (above for shorts, below for longs) before emitting.

5. **MONITORING:** Add a health-check alert: "Strategy X has 0% win rate but positive avg P&L" — this exact anomaly should flag immediately in any future runs.

---

## Conclusion

This is not a mystery anomaly — it is a simple directional sign error in one line of code. The strategy itself has merit (fade exhaustion into the mean), and its 100% positive P&L suggests the underlying signal quality is decent. But until the stop-loss direction is fixed, every single signal instantly exits as a LOSS at the moment it turns profitable.

**Bottom line: $2.19 average P&L is fake. The strategy produces zero real value today due to the inverted stop bug.**
