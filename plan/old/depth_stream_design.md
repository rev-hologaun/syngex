# Market Depth Stream Integration — Design Document

**Date:** 2026-05-12
**Issue:** C1 — Market Depth Streams Are No-Op Stubs
**Root Cause:** `tradestation_client.py` has no-op stubs for depth endpoints despite the TradeStation API having real endpoints at `/v3/marketdata/stream/marketdepth/quotes/` and `/v3/marketdata/stream/marketdepth/aggregates/`.

---

## Current State

### What Works
- `orb_probe.py` successfully connects to both depth endpoints and writes parsed JSONL files
- `main.py` has ~400 lines of `_on_message` logic that processes `market_depth_quotes` and `market_depth_agg` messages
- `main.py` populates 20+ rolling window keys from depth data (VSI, ESI, OBI, SIS, fragility, decay, etc.)
- 14+ Layer2/FullData strategies are wired to consume these rolling window keys

### What's Broken
- `TradeStationClient.subscribe_to_market_depth_quotes()` — logs "no-op stub", does nothing
- `TradeStationClient.subscribe_to_market_depth_aggregates()` — logs "no-op stub", does nothing
- Neither `subscribe_to_*` method stores symbols in any list
- Neither method spawns a background streaming task in `connect()`
- Result: `_on_message` never receives `market_depth_quotes` or `market_depth_agg` messages
- Result: all 20+ rolling depth keys stay at count=0, all 14+ strategies silently return `[]`

---

## TradeStation API Endpoints (confirmed via orb_probe.py)

| Endpoint | Method | Params | Output |
|----------|--------|--------|--------|
| `/v3/marketdata/stream/marketdepth/quotes/{symbol}` | GET | `maxlevels=20` | Per-exchange order book (Level 2 / TotalView) |
| `/v3/marketdata/stream/marketdepth/aggregates/{symbol}` | GET | `maxlevels=20` | Aggregated depth per price level |

Both use HTTP chunked streaming (same pattern as quotes and option chain).

---

## Raw Data Format

### Market Depth Quotes (per-exchange / TotalView)
```json
{
  "symbol": "TSLA",
  "Bids": [
    {"Price": 419.68, "Size": 372, "OrderCount": 3, "TimeStamp": "...", "Name": "NSDQ"},
    {"Price": 419.67, "Size": 1, "OrderCount": 1, "TimeStamp": "...", "Name": "NSDQ"}
  ],
  "Asks": [
    {"Price": 419.75, "Size": 40, "OrderCount": 1, "TimeStamp": "...", "Name": "BATY"},
    {"Price": 419.75, "Size": 80, "OrderCount": 2, "TimeStamp": "...", "Name": "NSDQ"}
  ]
}
```

Key fields: `symbol`, `Bids[]`, `Asks[]`, each entry has `Price`, `Size`, `OrderCount`, `TimeStamp`, `Name` (exchange)

### Market Depth Aggregates
```json
{
  "symbol": "TSLA",
  "Bids": [
    {"Price": 419.52, "TotalSize": 3, "BiggestSize": 3, "SmallestSize": 3,
     "NumParticipants": 1, "TotalOrderCount": 2, "EarliestTime": "...", "LatestTime": "..."}
  ],
  "Asks": [
    {"Price": 419.57, "TotalSize": 8, "BiggestSize": 8, "SmallestSize": 8,
     "NumParticipants": 1, "TotalOrderCount": 1, "EarliestTime": "...", "LatestTime": "..."}
  ]
}
```

Key fields: `symbol`, `Bids[]`, `Asks[]`, each entry has `Price`, `TotalSize`, `BiggestSize`, `SmallestSize`, `NumParticipants`, `TotalOrderCount`, `EarliestTime`, `LatestTime`

---

## Data Flow Architecture

```
TradeStation API
    ├── quotes stream ──→ TradeStationClient._stream_quotes_loop() ──→ _dispatch() ──→ main._on_message()
    ├── option chain ──→ TradeStationClient._fetch_option_chain_loop() ──→ _dispatch() ──→ main._on_message()
    ├── marketdepth/quotes ──→ TradeStationClient._stream_depth_quotes_loop() ──→ _dispatch() ──→ main._on_message()  ← NEW
    └── marketdepth/aggregates ──→ TradeStationClient._stream_depth_agg_loop() ──→ _dispatch() ──→ main._on_message()  ← NEW

main._on_message()
    ├── GEXCalculator.process_message(data)  ← depth messages pass through (no-op for calculator)
    └── depth data processing (~400 lines)
        ├── Exchange Flow Concentration (VSI, IEX intent)
        ├── Exchange Flow Imbalance (MEMX/BATS VSI, venue concentration)
        ├── Exchange Flow Asymmetry (ESI MEMX/BATS, baseline deviation)
        ├── Participant Diversity Conviction (participant/exchange scores)
        ├── Participant Divergence Scalper (fragility, decay velocity)
        ├── Depth metrics (bid/ask size, spread, levels)
        ├── VAMP Momentum (center of gravity)
        ├── Depth Decay Momentum (depth ROC)
        ├── Depth Imbalance Momentum (IR, IR ROC)
        ├── Order Book Stacking (SIS, level avg)
        ├── Whale Tracker (concentration ratio)
        └── Vortex Compression (spread z-score, liquidity density)
```

---

## Implementation Plan

### Step 1: Add Depth Subscription Lists to TradeStationClient

In `__init__`, add:
```python
self._depth_quote_symbols: List[str] = []
self._depth_agg_symbols: List[str] = []
```

### Step 2: Implement `subscribe_to_market_depth_quotes()`

```python
def subscribe_to_market_depth_quotes(self, symbol: str) -> None:
    if symbol not in self._depth_quote_symbols:
        self._depth_quote_symbols.append(symbol)
        logger.info("Queued market-depth-quotes subscription for %s", symbol)
```

### Step 3: Implement `subscribe_to_market_depth_aggregates()`

```python
def subscribe_to_market_depth_aggregates(self, symbol: str) -> None:
    if symbol not in self._depth_agg_symbols:
        self._depth_agg_symbols.append(symbol)
        logger.info("Queued market-depth-aggregates subscription for %s", symbol)
```

### Step 4: Add Depth Streaming Methods

Two new methods mirroring the existing `_stream_quotes_loop` pattern:

```python
async def _stream_depth_quotes_loop(self, symbol: str) -> None:
    """Stream market depth quotes (per-exchange TotalView data)."""
    url = f"{self.base_url}/marketdata/stream/marketdepth/quotes/{symbol}"
    params = {"maxlevels": 20}
    ...

async def _stream_depth_agg_loop(self, symbol: str) -> None:
    """Stream market depth aggregates (total size per level)."""
    url = f"{self.base_url}/marketdata/stream/marketdepth/aggregates/{symbol}"
    params = {"maxlevels": 20}
    ...
```

Both methods follow the same structure as `_stream_quotes_loop`:
- Connect with retry/backoff
- Parse JSON lines from HTTP chunked stream
- Dispatch each line as a dict via `_dispatch()`
- Handle 401 (refresh token), 404 (fail), 429 (backoff), connection errors

### Step 5: Wire Depth Streams into `connect()`

In `connect()`, after the existing quote/option-chain task spawning:

```python
if self._depth_quote_symbols:
    for sym in self._depth_quote_symbols:
        self._stream_tasks.append(
            asyncio.create_task(
                self._stream_depth_quotes_loop(sym),
                name=f"DepthQuoteStream-{sym}",
            )
        )

if self._depth_agg_symbols:
    for sym in self._depth_agg_symbols:
        self._stream_tasks.append(
            asyncio.create_task(
                self._stream_depth_agg_loop(sym),
                name=f"DepthAggStream-{sym}",
            )
        )
```

### Step 6: Data Normalization in main.py `_on_message()`

The raw TradeStation depth data uses different field names than what `main.py` expects:

| Raw API Field | main.py Expects |
|---------------|----------------|
| `Price` | `price` |
| `Size` | `size` |
| `TotalSize` | `TotalSize` (already correct) |
| `OrderCount` | `order_count` |
| `NumParticipants` | `num_participants` |
| `Name` | `exchange` |
| `Bids` | `Bids` (already correct) |
| `Asks` | `Asks` (already correct) |

**Two approaches:**

**Approach A (Preferred):** Normalize in the depth streaming loop in `tradestation_client.py`, before dispatch. This keeps the orchestrator clean and follows the orb_probe.py pattern.

**Approach B:** Add a normalization step in `main.py _on_message()` before the existing depth processing.

**Recommendation: Approach A** — normalize in the client. The streaming methods should transform raw API fields to the canonical names that `main.py` already expects.

### Step 7: GEXCalculator Message Handling

The `GEXCalculator.process_message()` method processes `option_update`, `underlying_update`, and raw quote data. Depth messages have `type="market_depth_quotes"` or `type="market_depth_agg"` — the calculator's `process_message()` will hit the `else` branch and log a debug message. This is fine — no change needed.

---

## Data Flow Verification

After implementation, the data flow will be:

1. **TradeStation API** sends depth JSON over HTTP chunked stream
2. **TradeStationClient** receives raw JSON, normalizes field names, dispatches dict
3. **main.py `_on_message()`** receives dict with `type="market_depth_quotes"` or `type="market_depth_agg"`
4. **GEXCalculator.process_message()** passes through (no-op for depth types)
5. **Depth processing block** (~400 lines) extracts bids/asks, computes 20+ metrics
6. **Rolling windows** get populated with depth data at every tick
7. **Strategies** read from rolling windows via `data["rolling_data"]`

---

## Files to Modify

| File | Changes |
|------|---------|
| `ingestor/tradestation_client.py` | Add depth subscription lists, implement subscribe methods, add 2 streaming loops, add field normalization |
| `main.py` | No changes needed (depth processing already exists in `_on_message`) |

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| API endpoint changes | Low | orb_probe.py already confirmed endpoints work |
| Field name mismatch | Medium | Normalize in client to match main.py expectations |
| Stream overload (4 concurrent HTTP streams) | Low | TradeStation rate limits via 429 responses; backoff already implemented |
| Token expiration on depth streams | Low | Same token refresh logic as quotes stream |
| Data volume increase | Low | Depth streams send ~1-5 msgs/sec per stream |

---

## Testing Strategy

1. **Unit test:** Verify `_stream_depth_quotes_loop` produces correctly normalized dicts
2. **Integration test:** Run orchestrator with depth subscriptions, verify rolling window counts > 0
3. **Strategy test:** Verify at least one L2 strategy produces signals (e.g., `ObiAggressionFlow`)
4. **Data comparison:** Compare depth rolling window values against orb_probe.py JSONL samples

---

## Implementation Notes

- The depth streaming loops should be nearly identical to `_stream_quotes_loop` — just different URL, params, and field normalization
- The existing `_on_message` depth processing in `main.py` is already correct — it just never receives data
- The `main.py` code uses `b.get("Price", 0)` and `b.get("Size", 0)` for quotes data, and `b.get("TotalSize", 0)` for aggregates — the normalization must produce these exact field names
- For depth quotes: normalize `Name` → `exchange`, `Size` → `size`, `OrderCount` → `order_count`
- For depth aggregates: normalize `NumParticipants` → `num_participants`, keep `TotalSize` as-is
