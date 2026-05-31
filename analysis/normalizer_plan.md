# Hidden Logic Leak Fix — Data Normalizer Plan

## Problem

Raw JSON from the TradeStation API contains numeric fields as strings (e.g., `"Size": "150"`, `"Gamma": "0.02"`, `"TotalSize": "500"`). These strings flow through the pipeline and are only cast to float/int at the LAST possible moment — in main.py's `_on_message` handler. This means:

1. **Ingestor normalizers** (`_normalize_depth_quotes`, `_normalize_depth_agg`, `_extract_contracts`) pass raw strings through unchanged
2. **GEXCalculator** casts some fields but not all (e.g., `_extract_contracts` → `_update_strike` has partial casting)
3. **main.py** does cast before using, but only in specific paths — any new code path that accesses raw message fields directly is vulnerable
4. **Strategies** read from `rolling_data` (which is clean), but also read from `depth_snapshot` and `greeks_summary` — these may contain uncast values

## Root Cause

The cast is scattered across 4+ layers instead of centralized. The ingestor normalizers are the natural single point of entry.

## Solution: Centralize Casting in the Ingestor

### Task 1: Fix `_normalize_depth_quotes` — cast all numeric fields

**File:** `ingestor/tradestation_client.py`
**Method:** `_normalize_depth_quotes`

Cast these fields to their proper types:
- `Size` → `int(b.get("Size", 0))`
- `Price` → `float(b.get("Price", 0))`
- `OrderCount` → `int(b.get("OrderCount", 0))`

Same for asks.

### Task 2: Fix `_normalize_depth_agg` — cast all numeric fields

**File:** `ingestor/tradestation_client.py`
**Method:** `_normalize_depth_agg`

Cast these fields:
- `TotalSize` → `int(b.get("TotalSize", 0))`
- `BiggestSize` → `int(b.get("BiggestSize", 0))`
- `SmallestSize` → `int(b.get("SmallestSize", 0))`
- `NumParticipants` → `int(b.get("NumParticipants", 0))`
- `TotalOrderCount` → `int(b.get("TotalOrderCount", 0))`
- `Price` → `float(b.get("Price", 0))`

### Task 3: Fix `_extract_contracts` — cast all numeric fields

**File:** `ingestor/tradestation_client.py`
**Method:** `_extract_contracts`

Cast these fields:
- `strike` → `float(leg.get("strike", 0))`
- `gamma` → `float(leg.get("Gamma", leg.get("gamma", 0)))`
- `oi` → `float(leg.get("DailyOpenInterest", leg.get("openInterest", leg.get("open_interest", 0))))`
- `delta` → `float(leg.get("Delta", leg.get("delta", 0.0)))`
- `iv` → `float(leg.get("ImpliedVolatility", leg.get("impliedVolatility", leg.get("iv", 0.0))))`
- `price` (underlying) → `float(price)`

### Task 4: Add type guards to GEXCalculator

**File:** `engine/gex_calculator.py`
**Method:** `_update_strike`

Add assertions at the top of `_update_strike` that verify all incoming values are numeric (int or float), and log a clear error if not. This catches any remaining leaks that slip past the ingestor.

### Task 5: Add type guards to `greeks_summary` output

**File:** `engine/gex_calculator.py`
**Method:** `get_greeks_summary`

Ensure all values returned are guaranteed floats (not strings). Add a type assertion loop.

### Task 6: Verify depth_snapshot values

**File:** `main.py`
**Method:** `_build_depth_snapshot`

Verify all values pulled from `rolling_data` are floats (RollingWindow.push accepts Any but strategies expect float). The RollingWindow class already accepts Any, so we should add a type hint or assertion.

### Task 7: Run existing tests

Run the full test suite to ensure no regressions:
```bash
cd /home/hologaun/projects/syngex && python3 -m pytest -xvs
```

## Execution Order

1. Task 1 (depth_quotes normalizer)
2. Task 2 (depth_agg normalizer)
3. Task 3 (contracts normalizer)
4. Task 4 (GEXCalculator type guards)
5. Task 5 (greeks_summary type guards)
6. Task 6 (depth_snapshot verification)
7. Task 7 (run tests)

Tasks 1-3 are independent and can be done in parallel by different Forge instances.
Tasks 4-6 depend on 1-3 being done.
Task 7 depends on everything.
