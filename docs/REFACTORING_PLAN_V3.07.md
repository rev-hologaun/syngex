# Syngex V3.07 - Refactoring Plan & Issue Tracker

**Current Version**: V3.06 (detached HEAD with uncommitted changes)  
**Target Version**: V3.07  
**Code Quality Score**: 7.5/10 → Target: 9.0/10  
**Status**: In Progress

---

## 🔴 CRITICAL ISSUES (Must Fix Before V3.07)

### Issue #1: Uncommitted Changes on V3.06 Tag
**Priority**: 🔴 CRITICAL  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py`, `log/heatmap.log`, `core/config_loader.py`, `core/container.py`, `core/events.py`, `docs/ARCHITECTURE.md`  
**Impact**: V3.06 is not a clean release state  
**Fix**: Commit Phase 7 changes properly or revert to clean V3.06 tag  
**Estimated Effort**: 30 min  
**Completed**: No  
**Notes**: Decision needed: commit changes or create V3.07 directly from current state

---

### Issue #2: Error Handling Gaps - Silent Failures
**Priority**: 🔴 CRITICAL  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py` (message processing), `data/ingestor.py`, `engine/gex_calculator.py`  
**Impact**: Silent data loss, operators won't know when streams fail  
**Fix**: Implement circuit breaker pattern or re-raise critical exceptions  
**Estimated Effort**: 2 hours  
**Completed**: No  
**Notes**: Need to define which exceptions should trigger alerts vs. be tolerated

---

### Issue #3: Missing Input Validation
**Priority**: 🔴 CRITICAL  
**Status**: ⏳ Pending  
**Files**: `engine/gex_calculator.py` (`_update_strike`, `_update_underlying_price`, `_update_strike_from_stream`)  
**Impact**: Division by zero, corrupted gamma ladder, crashes from malformed data  
**Fix**: Add type/range validation on all external inputs, return early on invalid data  
**Estimated Effort**: 1.5 hours  
**Completed**: No  
**Notes**: Should validate strike price (>0), gamma (numeric), price ranges before processing

---

### Issue #4: Assertions in Production Code
**Priority**: 🔴 CRITICAL  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py` (multiple locations, e.g., line ~167)  
**Impact**: Assertions stripped with `-O` flag, can bypass critical validation  
**Fix**: Replace all `assert` statements with proper validation raising `RuntimeError` or `ValueError`  
**Estimated Effort**: 1 hour  
**Completed**: No  
**Notes**: Search for all `assert ` statements and convert to proper exceptions

---

## 🟠 HIGH PRIORITY (Must Fix Before V3.08)

### Issue #5: Tight Coupling - Orchestrator Knows Too Much
**Priority**: 🟠 HIGH  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py` (imports 20+ strategy classes directly)  
**Impact**: Violates Dependency Inversion Principle, hard to test and extend  
**Fix**: Use dependency injection with interfaces/protocols for strategy registration  
**Estimated Effort**: 4 hours  
**Completed**: No  
**Notes**: Long-term refactor, should be V4.0 scope. For V3.07, add factory pattern at minimum

---

### Issue #6: Memory Management - Inefficient Buffer Sizing
**Priority**: 🟠 HIGH  
**Status**: ⏳ Pending  
**Files**: `strategies/engine.py` (`_recent_signals` buffer)  
**Impact**: Creates new list on every trim, generates garbage, memory fragmentation  
**Fix**: Use `collections.deque(maxlen=200)` instead of list slicing  
**Estimated Effort**: 30 min  
**Completed**: No  
**Notes**: Simple one-line fix, should be done immediately

---

### Issue #7: Conflicting Configuration Sources
**Priority**: 🟠 HIGH  
**Status**: ⏳ Pending  
**Files**: Multiple strategy files (hardcoded constants), `config/strategies.yaml`  
**Impact**: Source of truth unclear, inconsistent behavior, hard to tune  
**Examples**:
- `MIN_CONFIDENCE`: 0.55 (code) vs 0.35 (config)
- `MIN_NET_GAMMA`: 10,000 vs 500,000 across strategies
**Fix**: Remove all hardcoded thresholds, use config values only with validation at startup  
**Estimated Effort**: 2 hours  
**Completed**: No  
**Notes**: Need to audit all strategies for hardcoded constants

---

### Issue #8: No Backpressure Mechanism
**Priority**: 🟠 HIGH  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py` (main loop), `strategies/engine.py` (process method)  
**Impact**: If strategy evaluation >250ms, system falls behind, no queue management  
**Fix**: Implement priority queue or adaptive sleep based on processing time  
**Estimated Effort**: 2 hours  
**Completed**: No  
**Notes**: Can start simple - track processing time and adjust sleep interval dynamically

---

### Issue #9: Test Coverage Gaps
**Priority**: 🟠 HIGH  
**Status**: ⏳ Pending  
**Files**: `tests/` directory - missing tests for Phase 4 components  
**Impact**: New code untested, high risk of regressions  
**Missing Tests**:
- `StrategyEvaluationEngine`
- `GammaProfileEngine`
- `NetGammaFilter` (new from `core.filters`)
- Individual strategies (Layer 1, 2, 3, full_data)
**Estimated Effort**: 6 hours  
**Completed**: No  
**Notes**: Should add integration tests + unit tests for each strategy type

---

## 🟡 MEDIUM PRIORITY (Nice to Have for V3.07)

### Issue #10: Logging Inconsistencies
**Priority**: 🟡 MEDIUM  
**Status**: ⏳ Pending  
**Files**: Throughout codebase - mixed `log_with_correlation()` and direct `logger.info()`  
**Impact**: Inconsistent traceability, correlation IDs not always propagated  
**Fix**: Standardize on `log_with_correlation()` for all module-level logging  
**Estimated Effort**: 1 hour  
**Completed**: No  
**Notes**: Search for `logger.info(` and `logger.debug(` patterns that don't use correlation

---

### Issue #11: Race Condition in Config Hot-Reload
**Priority**: 🟡 MEDIUM  
**Status**: ⏳ Pending  
**Files**: `core/orchestrator.py` (`_watch_config`, `_reload_config`)  
**Impact**: File modification detection is not atomic - can miss changes or reload twice  
**Fix**: Use file watcher library (inotify, watchdog) for atomic change detection  
**Estimated Effort**: 1.5 hours  
**Completed**: No  
**Notes**: Alternative: use checksums instead of mtime, or file locking

---

### Issue #12: Documentation Gaps
**Priority**: 🟡 MEDIUM  
**Status**: ⏳ Pending  
**Files**: `strategies/layer2/`, `strategies/layer3/` (no module docstrings)  
**Impact**: Hard for new developers to understand, missing API docs  
**Fix**: Add module docstrings, API documentation, Architecture Decision Records (ADRs)  
**Estimated Effort**: 2 hours  
**Completed**: No  
**Notes**: Can use existing docstrings in Layer 1 as template

---

### Issue #13: No Connection Pool Limits
**Priority**: 🟡 MEDIUM  
**Status**: ⏳ Pending  
**Files**: `data/ingestor.py` (aiohttp sessions)  
**Impact**: Can hang indefinitely, no resource limits  
**Fix**: Add aiohttp timeout and connection pool limits  
**Estimated Effort**: 1 hour  
**Completed**: No  
**Notes**: Should add timeout to all HTTP requests, set connection pool size

---

## 📊 PROGRESS TRACKER

### Phase 1: Critical Fixes (V3.07)
- [ ] **Issue #1**: Resolve uncommitted changes (Decision: commit or revert)
- [ ] **Issue #2**: Add circuit breaker to error handling
- [ ] **Issue #3**: Add input validation to GEXCalculator
- [ ] **Issue #4**: Replace assertions with proper exceptions

### Phase 2: High Priority Fixes (V3.07)
- [ ] **Issue #6**: Fix deque buffer (quick win)
- [ ] **Issue #7**: Consolidate config constants
- [ ] **Issue #8**: Add basic backpressure mechanism
- [ ] **Issue #9**: Add tests for Phase 4 components

### Phase 3: Medium Priority (V3.08)
- [ ] **Issue #10**: Standardize logging
- [ ] **Issue #11**: Fix config reload race condition
- [ ] **Issue #12**: Add documentation
- [ ] **Issue #13**: Add connection pool limits

### Phase 4: Long-term (V4.0)
- [ ] **Issue #5**: Refactor orchestrator with dependency injection

---

## 📝 EXECUTION LOG

| Date | Issue | Status | Notes |
|------|-------|--------|-------|
| 2026-05-19 | All | Created | Plan created based on code review |

---

## 🎯 TESTING REQUIREMENTS

Before V3.07 release:
- [ ] All Phase 4 components have unit tests
- [ ] Integration tests for message flow (Ingestor → Calculator → StrategyEngine)
- [ ] Input validation tests for all public APIs
- [ ] Error handling tests (circuit breaker triggers correctly)
- [ ] Backpressure tests (system doesn't fall behind)

---

## 🚀 DEPLOYMENT CHECKLIST

Before V3.07 deployment:
- [ ] All critical issues resolved
- [ ] All high priority issues resolved
- [ ] Test coverage >70% for new components
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] ADRs created for major decisions

---

*Generated: 2026-05-19 06:17 PDT*  
*Last Updated: 2026-05-19 06:17 PDT*  
*Owner: Archon / Forge*
