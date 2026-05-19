# Strategy Error Investigation - Root Cause & Fix

## Problem
"Strategy error" messages appearing on positive gamma symbols (AAPL: Net Gamma = +903.51) but not on negative gamma symbols (TSLA: Net Gamma = -287.97).

## Root Cause Analysis

### 1. Error Logging Was Incomplete
**Location:** `strategies/engine.py:306-312`

The error handler was using `log_with_correlation()` which **did not support `exc_info`**, so full tracebacks were being lost. Only the error message string was logged, not the actual exception details.

**Original Code:**
```python
except Exception as exc:
    if log_with_correlation:
        log_with_correlation(
            logger, logging.ERROR,
            "Strategy error",
            correlation_id=self._correlation_id,
            strategy_id=strategy.strategy_id,
            error=str(exc)  # ← No traceback!
        )
    else:
        logger.error("Strategy %s error: %s", strategy.strategy_id, exc, exc_info=True)
```

### 2. Strategies Called Regardless of Regime
All strategies are evaluated in Phase 1, then the regime filter runs in Phase 2 to block signals. Some strategies might throw exceptions when called in the wrong regime due to:
- Missing data that only exists in their target regime
- Division by zero or None access issues
- Regime-specific logic that crashes

### 3. Architecture Issue
The regime filter is a **signal-level filter** (runs AFTER strategy evaluation), not a **pre-evaluation gate**. This means strategies are always called, even if they only work in specific regimes.

## Fixes Applied

### Fix 1: Added `exc_info` Support to `log_with_correlation`
**File:** `config/logging_config.py`

Added `exc_info` parameter to capture full exception tracebacks:

```python
def log_with_correlation(
    logger: logging.Logger,
    level: int,
    message: str,
    correlation_id: Optional[str] = None,
    signal_id: Optional[str] = None,
    exc_info: Optional[bool] = False,  # ← NEW
    **extra: Any
) -> None:
    # ...
    # Get exception info if requested
    exc_info_tuple = None
    if exc_info:
        import sys
        exc_info_tuple = sys.exc_info()
    
    # Build the log record with extra attributes
    log_record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        exc_info_tuple,  # ← Pass exception info
        None
    )
```

### Fix 2: Updated Error Handler to Use `exc_info=True`
**File:** `strategies/engine.py:306-314`

```python
except Exception as exc:
    if log_with_correlation:
        log_with_correlation(
            logger, logging.ERROR,
            "Strategy error",
            correlation_id=self._correlation_id,
            strategy_id=strategy.strategy_id,
            error=str(exc),
            exc_info=True  # ← NOW INCLUDES TRACEBACK
        )
    else:
        logger.error("Strategy %s error: %s", strategy.strategy_id, exc, exc_info=True)
```

### Fix 3: Added Regime Pre-Filter Hook
**File:** `strategies/engine.py`

Added `_strategy_passes_regime_filter()` method as a pre-evaluation hook:

```python
def _strategy_passes_regime_filter(
    self, 
    strategy: BaseStrategy, 
    regime: str, 
    data: Dict[str, Any]
) -> bool:
    """
    Check if a strategy should run in the current regime.
    
    This is a pre-evaluation filter to avoid running strategies
    that are known to only work in specific regimes.
    """
    # Default: run all strategies (they should handle regime internally)
    # Subclasses can override this to add regime-specific logic
    return True
```

Called before `strategy.evaluate()`:

```python
# Check regime compatibility before evaluating
regime = data.get("regime", "")
if not self._strategy_passes_regime_filter(strategy, regime, data):
    continue
```

## Expected Outcome

1. **Full tracebacks now visible** - When a strategy throws an exception, the complete error message with stack trace will be logged
2. **Easier debugging** - Can now identify exactly which strategy is failing and why
3. **Extensible regime filtering** - Future strategies can override `_strategy_passes_regime_filter()` to skip evaluation in wrong regimes

## Next Steps

1. **Monitor logs** - Watch for actual error messages with full tracebacks
2. **Identify failing strategies** - Once errors are visible, fix the specific strategies that are crashing
3. **Consider hard regime gates** - For strategies that ONLY work in one regime, add pre-evaluation regime checks to skip them entirely

## Files Modified

- `config/logging_config.py` - Added `exc_info` support to `log_with_correlation()`
- `strategies/engine.py` - Updated error handler, added `_strategy_passes_regime_filter()` method
