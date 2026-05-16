# Syngex Strategy Audit Plan — v2.21 Series

**Purpose:** Batch audit, fix, and release remaining strategies from hmstrat.md
**Source of Truth:** Original design files in `plan/` → fallback to docstrings
**Version Strategy:** v2.211, v2.212, v2.213, ... (one commit per batch)

---

## Progress Summary

| Phase | Strategies | Status |
|-------|-----------|--------|
| v2.21 | 11 strategies | ✅ Complete |
| v2.21x | 29 strategies (hmstrat.md) | 🔄 In Progress |

---

## hmstrat.md Strategy Mapping

| Heatmap Name | Strategy File | Plan File | Status |
|--------------|---------------|-----------|--------|
| OBI_AF | `layer2/obi_aggression_flow.py` | `obi_aggression_flow.md` | ⏳ Pending |
| CALL_PUT_FLOW | `layer2/call_put_flow_asymmetry.py` | `call_put_flow_asymmetry_v2.md` | ⏳ Pending |
| IV_GEX_DIV | `layer2/iv_gex_divergence.py` | `iv_gex_divergence_v2.md` | ✅ Fixed (v2.21) |
| TAIL_RISK | **REMOVED** | N/A | ❌ Not needed (per Hologaun 2026-05-16) |
| DEPTH_IMBAL | `layer2/depth_imbalance_momentum.py` | `depth_imbalance_momentum.md` | ⏳ Pending |
| DEPTH_DECAY | `layer2/depth_decay_momentum.py` | `depth_decay_momentum.md` | ⏳ Pending |
| EXCHANGE | `layer2/exchange_flow_asymmetry.py` | `exchange_flow_asymmetry.md` | ⏳ Pending |
| PARTICIPANT_CONV | `layer2/participant_diversity_conviction.py` | `participant_diversity_conviction.md` | ⏳ Pending |
| DIVERGENCE_SCALP | `layer2/participant_divergence_scalper.py` | `participant_divergence_scalper.md` | ⏳ Pending |
| FLOW_IMBALANCE | `layer2/exchange_flow_imbalance.py` | `exchange_flow_imbalance.md` | ⏳ Pending |
| OB_FRAGMENT | `layer2/order_book_fragmentation.py` | `order_book_fragmentation.md` | ⏳ Pending |
| STACKING | `layer2/order_book_stacking.py` | `order_book_stacking.md` | ⏳ Pending |
| GAMMA_VOL | `layer3/gamma_volume_convergence.py` | `gamma_volume_convergence_v2.md` | ⏳ Pending |
| IV_BAND | `layer3/iv_band_breakout.py` | `iv_band_breakout_v2.md` | ⏳ Pending |
| STRIKE_CONC | `layer3/strike_concentration.py` | `strike_concentration_v2.md` | ⏳ Pending |
| IV_SKEW | `full_data/iv_skew_squeeze.py` | `iv_skew_squeeze_v2.md` | ⏳ Pending |
| SKEW_DYN | `full_data/skew_dynamics.py` | N/A | ⏳ Pending (docstring only) |
| SMILE_DYN | `full_data/smile_dynamics.py` | N/A | ⏳ Pending (docstring only) |
| THETA_BURN | `layer3/theta_burn.py` | `theta_burn_v2.md` | ⏳ Pending |
| PROB_DIST | `full_data/prob_distribution_shift.py` | `prob_distribution_shift_v2.md` | ⏳ Pending |
| EXTRINSIC | `full_data/extrinsic_intrinsic_flow.py` | `extrinsic_intrinsic_flow_v2.md` | ⏳ Pending |
| GHOST_PREM | `full_data/ghost_premium.py` | N/A | ⏳ Pending (docstring only) |
| EXTRINSIC_FLOW | `full_data/extrinsic_flow.py` | N/A | ⏳ Pending (docstring only) |
| GAMMA_BREAK | `full_data/gamma_breaker.py` | N/A | ⏳ Pending (docstring only) |
| IRON_ANCHOR | `full_data/iron_anchor.py` | N/A | ⏳ Pending (docstring only) |
| VORTEX | `layer2/vortex_compression_breakout.py` | N/A | ⏳ Pending (docstring only) |
| SENT_SYNC | `full_data/sentiment_sync.py` | N/A | ⏳ Pending (docstring only) |
| WHALE_TRACK | `full_data/whale_tracker.py` | N/A | ⏳ Pending (docstring only) |

---

## Known Issues to Check (Common Patterns)

### 1. **Unused Parameters (Priority: High)**
- `depth_score: Optional[float] = None` — never used in confidence calculations
- `regime_intensity` — calculated but not added to confidence
- `wall_bonus` — calculated but not added to confidence
- `gex_accel` — calculated but not added to confidence
- `iv_roc_bonus` — calculated but not added to confidence

### 2. **MIN_CONFIDENCE Threshold (Priority: Medium)**
- Check if `MIN_CONFIDENCE = 0.15` — should be `0.10`
- Strategies that were never relaxed need adjustment

### 3. **Docstring Mismatches (Priority: High)**
- Docstring claims "X components" but formula has fewer
- Features documented but never implemented
- Parameters in signature but never used

### 4. **Logic Bugs (Priority: Critical)**
- Wrong direction checks (LONG vs SHORT)
- Incorrect gamma regime requirements
- Clamping/capping errors
- Off-by-one errors in rolling windows

### 5. **Missing Plan Files (Priority: Low)**
- Strategies with no plan file use docstring as source of truth
- If docstring is also unclear, flag for Hologaun review

---

## Batch Strategy

**Batch Size:** 3-5 strategies per commit
**Rationale:** Balance speed with manageable diff review

| Batch | Version | Strategies | Plan Files |
|-------|---------|------------|------------|
| Batch 1 | v2.211 | OBI_AF, CALL_PUT_FLOW, DEPTH_IMBAL, DEPTH_DECAY, EXCHANGE | All have plan files |
| Batch 2 | v2.212 | PARTICIPANT_CONV, DIVERGENCE_SCALP, FLOW_IMBALANCE, OB_FRAGMENT, STACKING | All have plan files |
| Batch 3 | v2.213 | GAMMA_VOL, IV_BAND, STRIKE_CONC, IV_SKEW | All have plan files |
| Batch 4 | v2.214 | SKEW_DYN, SMILE_DYN, THETA_BURN, PROB_DIST, EXTRINSIC | Mixed (some plan, some docstring) |
| Batch 5 | v2.215 | GHOST_PREM, EXTRINSIC_FLOW, GAMMA_BREAK, IRON_ANCHOR, VORTEX | Mostly docstring |
| Batch 6 | v2.216 | SENT_SYNC, WHALE_TRACK, TAIL_RISK* | *TAIL_RISK missing |

---

## Workflow Per Strategy

1. **Read strategy file** → identify issues
2. **Cross-reference with plan file** (if exists) or docstring
3. **Classify issues:**
   - ✅ **Auto-fix:** Unused params, MIN_CONFIDENCE, docstring mismatches
   - ⚠️ **Flag for review:** Logic bugs, missing features, unclear design
4. **Spawn Forge** with fix instructions (for auto-fixes)
5. **Report back** to Hologaun (for flagged issues)
6. **Commit** with descriptive message

---

## Critical Questions for Hologaun

1. **TAIL_RISK strategy:** Removed from audit per Hologaun 2026-05-16. Not needed.

2. **Strategies without plan files:** Should I use docstrings as source of truth, or do you have designs for these elsewhere?

3. **Batch commit frequency:** Confirm 3-5 strategies per commit is acceptable, or adjust?

4. **Escalation threshold:** If I find a critical logic bug in a strategy, should I:
   - Stop and ask before fixing?
   - Fix and note it in the commit message?
   - Flag and wait for review?

5. **Depth functions:** Confirm we continue the pattern of removing unused `depth_score` parameters while preserving functional depth calls (KEY_DEPTH_SPREAD_5M, depth_snapshot, etc.)

---

## Success Criteria

- [ ] All 29 strategies in hmstrat.md reviewed
- [ ] Unused parameters removed
- [ ] MIN_CONFIDENCE standardized to 0.10
- [ ] Docstrings match implementation
- [ ] v2 features integrated where promised
- [ ] Each batch committed with clear version tag
- [ ] Critical issues escalated to Hologaun
- [ ] Missing strategies documented

---

**Last Updated:** Sat 2026-05-16 02:00 PDT
**Prepared by:** Archon (Celestial Loom)
