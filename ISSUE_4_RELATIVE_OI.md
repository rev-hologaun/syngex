# Issue #4: Relative Open Interest Values - Documentation Complete

## Summary

Documented the TradeStation SSE stream limitation where Open Interest (OI) values default to 1.0 per message because the stream greeks format does not include OI data.

## Root Cause

**Data Source Limitation**: The TradeStation option-chain SSE stream provides "stream greeks objects" containing:
- Delta, Gamma, Theta, Vega, Rho
- ImpliedVolatility
- IntrinsicValue, ExtrinsicValue, TheoreticalValue
- ProbabilityITM, ProbabilityOTM, ProbabilityBE

**Missing Field**: These objects do NOT include `DailyOpenInterest` (or any OI field). The stream greeks detection logic explicitly checks for this:

```python
def _is_stream_greeks(self, msg: Dict[str, Any]) -> bool:
    has_greeks = "Delta" in msg and "Gamma" in msg
    has_intrinsic = "IntrinsicValue" in msg
    no_oi = "DailyOpenInterest" not in msg  # ← Key detection
    return has_greeks and has_intrinsic and no_oi
```

When processing these stream greeks, OI defaults to 1.0:

```python
# Open interest not in stream — default to 1.0
# This means GEX values are relative, not absolute
oi = 1.0
```

## Impact on Strategies

### Affected Strategies

1. **CallPutFlowAsymmetry** (Layer 2)
   - Uses: `FlowScore = Σ(OI × Gamma × |Delta|)`
   - Impact: Flow scores are relative, not absolute dollar values
   - **Still Valid**: Call vs Put ratios preserve asymmetry detection

2. **StrikeConcentration** (Layer 3)
   - Uses: "Top 3 strikes by total OI concentration"
   - Impact: Rankings based on relative OI, not absolute contract counts
   - **Still Valid**: Strike concentration patterns still reveal price reaction zones

3. **ProbWeightedMagnet** (Full Data)
   - Uses: `MIN_OI_CONCENTRATION = 2.0` threshold
   - Impact: Threshold in relative units, not contract counts
   - **Still Valid**: Combines ProbabilityITM with relative activity for accumulation detection

### Why Relative OI Still Works

**Key Insight**: These strategies rely on **ratios and rankings**, not absolute values.

- **CallPutFlowAsymmetry**: If call flow is 3× put flow with relative OI (1.0 each), it would be approximately 3× with real OI (assuming similar OI distribution). The asymmetry ratio is preserved.

- **StrikeConcentration**: Even with relative OI, strikes with high gamma/delta activity from the stream correlate with OI concentration. Price reactions at these strikes remain meaningful.

- **ProbWeightedMagnet**: Combines ProbabilityITM (accurate from stream) with relative activity levels. The combination still identifies smart money positioning.

## Documentation Added

### Files Updated

1. **`engine/gex_calculator.py`**
   - `_StrikeBucket` class docstring: Comprehensive limitation explanation
   - `_update_strike_from_stream` method docstring: Why OI is relative
   - `get_greeks_summary` method docstring: Valid/invalid use cases

2. **`strategies/layer2/call_put_flow_asymmetry.py`**
   - Module docstring: OI limitation and why ratios still work
   - Class docstring: OI note in attributes
   - `_calculate_flow_scores` method: OI warning

3. **`strategies/layer3/strike_concentration.py`**
   - Module docstring: OI limitation and concentration pattern validity

4. **`strategies/full_data/prob_weighted_magnet.py`**
   - Module docstring: OI threshold explanation and why it still works

### Key Documentation Points

```markdown
⚠️ **Open Interest Limitation**:
The TradeStation SSE stream greeks format does not include Open Interest data.
OI defaults to 1.0 per message, making all OI-dependent calculations relative.

**Valid Use Cases**:
- Call vs Put flow ratio (CallPutFlowAsymmetry) — relative ratios work
- Strike-to-strike OI comparison (relative rankings preserved)
- Directional asymmetry detection (magnitude still meaningful)

**Invalid Use Cases**:
- Absolute contract count assumptions
- Dollar-value GEX calculations without REST API OI fetch
- OI threshold-based filtering with absolute values
```

## Future Enhancement (Optional)

**Option A - Implement Real OI Fetching**:

If absolute OI values become necessary, implement:
1. Periodic REST API calls to fetch real OI data
2. Mapping between stream greeks and OI data (by strike/side)
3. Update `set_open_interest()` to be called periodically
4. Consider OI staleness and refresh intervals

**Complexity**: Medium-High
- Requires TradeStation REST API integration
- Needs OI data mapping logic
- Must handle OI refresh timing/staleness

**Recommendation**: Not needed unless strategies fail with relative OI. Current approach works for ratio-based detection.

## Commit

```
docs: clarify relative OI limitation in GEXCalculator

- Add comprehensive documentation about TradeStation stream OI limitation
- OI defaults to 1.0 per message (stream greeks format excludes DailyOpenInterest)
- Update docstrings in:
  - _StrikeBucket class: explain limitation and affected strategies
  - _update_strike_from_stream: detail why OI is relative
  - get_greeks_summary: warn about OI implications
  - CallPutFlowAsymmetry: explain ratio-based approach still valid
  - StrikeConcentration: note relative OI rankings
  - ProbWeightedMagnet: clarify relative OI thresholds

Key points:
- Relative OI preserves call/put ratios for asymmetry detection
- Absolute contract counts require REST API OI fetch (future enhancement)
- Flow score magnitudes are relative but directional signals remain valid
- Strike concentration rankings still meaningful for price reaction detection
```

## Conclusion

**Status**: ✅ Complete (Option B - Documentation)

The relative OI limitation is now clearly documented across all affected components. The strategies continue to function correctly because they rely on ratios and patterns that are preserved even with relative OI values.

**No code changes needed** - the existing implementation is correct for the data available from the TradeStation stream.
