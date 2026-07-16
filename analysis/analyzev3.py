#!/usr/bin/env python3
"""
Comprehensive per-strategy performance analysis for Round 3 validation.
Analyzes all signal_outcomes_*.jsonl files across all symbols.
"""

import glob
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("/home/hologaun/projects/syngex/log")
OUTPUT_FILE = Path("/home/hologaun/projects/syngex/analysis/analyzed_strategies_v3.md")

CONFIDENCE_BUCKETS = [
    ("5-9%",    0.05, 0.10),
    ("10-19%",  0.10, 0.20),
    ("20-29%",  0.20, 0.30),
    ("30-39%",  0.30, 0.40),
    ("40-49%",  0.40, 0.50),
    ("50-59%",  0.50, 0.60),
    ("60-69%",  0.60, 0.70),
    ("70-79%",  0.70, 0.80),
    ("80-89%",  0.80, 0.90),
    ("90-99%",  0.90, 1.00),
    ("100%",    1.00, 1.10),
]

TREND_MAP = {
    "UP": "Trending (Up)",
    "DOWN": "Trending (Down)",
    "FLAT": "Sideways",
}

REGIME_MAP = {
    "POSITIVE": "Positive Gamma (Range-Bound friendly)",
    "NEGATIVE": "Negative Gamma (Volatile/Breakout friendly)",
}


def binomial_z_score(win_rate_val, total, overall_wr):
    """Calculate z-score of a win rate vs the overall win rate.

    Returns (z_score, is_significant, low_sample) where:
    - z_score: how many standard deviations away from overall WR
    - is_significant: True if |z_score| > 1.645 (p < 0.10, one-tailed)
    - low_sample: True if total < 30 (not enough data for reliable stats)
    """
    if total < 5:
        return 0.0, False, True
    if total < 30:
        low_sample = True
    else:
        low_sample = False

    # Standard error of binomial proportion
    se = math.sqrt(overall_wr * (1 - overall_wr) / total) if total > 0 and overall_wr > 0 and overall_wr < 1 else 0.01
    if se == 0:
        se = 0.01  # guard against zero variance

    z = (win_rate_val - overall_wr) / se
    is_sig = abs(z) > 1.645  # p < 0.10 one-tailed

    return round(z, 2), is_sig, low_sample


def load_all_outcomes():
    """Load all signal outcome files."""
    all_signals = []
    files = sorted(glob.glob(str(LOG_DIR / "signal_outcomes_*.jsonl")))
    for f in files:
        symbol = Path(f).stem.replace("signal_outcomes_", "")
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    rec["_symbol"] = symbol
                    # Filter out signals below minimum confidence threshold
                    min_confidence = rec.get("confidence", 0.0)
                    if min_confidence < 0.05:
                        continue
                    all_signals.append(rec)
                except json.JSONDecodeError:
                    continue
    return all_signals


def bucket_confidence(conf):
    """Return confidence bucket label."""
    for label, lo, hi in CONFIDENCE_BUCKETS:
        if lo <= conf < hi:
            return label
    return "Other"


def analyze_strategy(signals, market_opens=None):
    """Analyze a single strategy across all symbols."""
    results = {}
    
    for sig in signals:
        # Extract signal timestamp for session filtering
        sig_ts = extract_signal_timestamp(sig)
        sw_label = signal_time_window_label(sig_ts)
        # Only process ORB, Morning, and Afternoon sessions
        valid_sessions = {"ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"}
        if sw_label not in valid_sessions:
            continue

        sid = sig["strategy_id"]
        if sid not in results:
            results[sid] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "total_pnl": 0.0,
                "total_pnl_pct": 0.0,
                "closed_pnl": 0.0,
                "closed_pnl_pct": 0.0,
                "resolved_pnl": [],
                "avg_hold_time": 0.0,
                "confidence_buckets": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0, "pnl_pct": 0.0, "closed_pnl": 0.0, "closed_pnl_pct": 0.0}),
                "trend_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "regime_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "time_held_broad": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "signal_time_window": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "session_confidence": defaultdict(lambda: {"high": 0, "medium": 0, "low": 0, "total": 0}),
                "session_confidence_perf": defaultdict(lambda: defaultdict(lambda: {
                    "total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0,
                })),
                "direction_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "time_held_fine": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "symbols": set(),
                "pnl_list": [],
                "hold_times": [],
            }
        
        r = results[sid]
        r["total"] += 1
        r["symbols"].add(sig["_symbol"])
        
        outcome = sig.get("outcome", "UNKNOWN")
        if outcome == "WIN":
            r["wins"] += 1
        elif outcome == "LOSS":
            r["losses"] += 1
        elif outcome == "CLOSED":
            r["closed"] += 1
        
        pnl = sig.get("pnl", 0.0)
        pnl_pct = sig.get("pnl_pct", 0.0)
        r["pnl_list"].append(pnl)

        if outcome == "CLOSED":
            r["closed_pnl"] += pnl
            r["closed_pnl_pct"] += pnl_pct
        else:
            r["total_pnl"] += pnl
            r["total_pnl_pct"] += pnl_pct
            r["resolved_pnl"].append(pnl)
        
        hold = sig.get("hold_time", 0.0)
        r["hold_times"].append(hold)
        
        # Confidence bucket
        conf = sig.get("confidence", 0.5)
        cb = bucket_confidence(conf)
        cb_data = r["confidence_buckets"][cb]
        cb_data["total"] += 1
        if outcome == "WIN":
            cb_data["wins"] += 1
            cb_data["pnl"] += pnl
            cb_data["pnl_pct"] += pnl_pct
        elif outcome == "LOSS":
            cb_data["losses"] += 1
            cb_data["pnl"] += pnl
            cb_data["pnl_pct"] += pnl_pct
        elif outcome == "CLOSED":
            cb_data["closed"] += 1
            cb_data["closed_pnl"] += pnl
            cb_data["closed_pnl_pct"] += pnl_pct
        else:
            cb_data["pnl"] += pnl
            cb_data["pnl_pct"] += pnl_pct
        
        # Trend
        meta = sig.get("metadata", {})
        trend = meta.get("trend", "UNKNOWN")
        trend_key = TREND_MAP.get(trend, trend)
        tp = r["trend_perf"][trend_key]
        tp["total"] += 1
        if outcome == "WIN": tp["wins"] += 1
        elif outcome == "LOSS": tp["losses"] += 1
        elif outcome == "CLOSED": tp["closed"] += 1
        tp["pnl"] += pnl
        
        # Regime
        regime = meta.get("regime", "UNKNOWN")
        regime_key = REGIME_MAP.get(regime, regime)
        rp = r["regime_perf"][regime_key]
        rp["total"] += 1
        if outcome == "WIN": rp["wins"] += 1
        elif outcome == "LOSS": rp["losses"] += 1
        elif outcome == "CLOSED": rp["closed"] += 1
        rp["pnl"] += pnl
        
        # Time window (broad buckets — major session windows)
        tw = "Unknown"
        if hold < 30*60:
            tw = "Time Held: <30m"
        elif hold < 90*60:
            tw = "Time Held: 30-90m"
        elif hold < 240*60:
            tw = "Time Held: 90-240m"
        elif hold < 480*60:
            tw = "Time Held: 240-480m"
        else:
            tw = "Time Held: >480m"
        twp = r["time_held_broad"][tw]
        twp["total"] += 1
        if outcome == "WIN": twp["wins"] += 1
        elif outcome == "LOSS": twp["losses"] += 1
        elif outcome == "CLOSED": twp["closed"] += 1
        twp["pnl"] += pnl
        
        # Direction
        direction = sig.get("direction", "UNKNOWN")
        dp = r["direction_perf"][direction]
        dp["total"] += 1
        if outcome == "WIN": dp["wins"] += 1
        elif outcome == "LOSS": dp["losses"] += 1
        elif outcome == "CLOSED": dp["closed"] += 1
        dp["pnl"] += pnl
        
        # Signal generation time window (US equity session buckets in ET)
        sig_ts = extract_signal_timestamp(sig)
        sw_label = signal_time_window_label(sig_ts)
        swp = r["signal_time_window"][sw_label]
        swp["total"] += 1
        if outcome == "WIN": swp["wins"] += 1
        elif outcome == "LOSS": swp["losses"] += 1
        elif outcome == "CLOSED": swp["closed"] += 1
        swp["pnl"] += pnl

        # Confidence distribution by session
        sc = r["session_confidence"][sw_label]
        sc["total"] += 1
        if conf >= 0.70:
            sc["high"] += 1
        elif conf >= 0.50:
            sc["medium"] += 1
        else:
            sc["low"] += 1

        # Session × Confidence cross-tabulation
        cb = bucket_confidence(conf)
        scp = r["session_confidence_perf"][sw_label][cb]
        scp["total"] += 1
        if outcome == "WIN":
            scp["wins"] += 1
        elif outcome == "LOSS":
            scp["losses"] += 1
        elif outcome == "CLOSED":
            scp["closed"] += 1
        scp["pnl"] += pnl

        # Hold time buckets (fine-grained — detailed hold durations)
        if hold < 60:
            ht_key = "Very Fast (<1 min)"
        elif hold < 300:
            ht_key = "Fast (1-5 min)"
        elif hold < 900:
            ht_key = "Medium (5-15 min)"
        elif hold < 1800:
            ht_key = "Slow (15-30 min)"
        elif hold < 3600:
            ht_key = "Long (30-60 min)"
        else:
            ht_key = "Very Long (>1h)"
        htb = r["time_held_fine"][ht_key]
        htb["total"] += 1
        if outcome == "WIN": htb["wins"] += 1
        elif outcome == "LOSS": htb["losses"] += 1
        elif outcome == "CLOSED": htb["closed"] += 1
        htb["pnl"] += pnl
    
    return results


def extract_signal_timestamp(sig):
    """Extract epoch-second timestamp from signal_id (format: strategy_timestamp_random).

    The timestamp is always the second-to-last underscore-separated part.
    This avoids picking up digits from strategy_id (e.g. 'v2', 'v3').
    """
    sid = sig.get("signal_id", "")
    parts = sid.split("_")
    # The timestamp is always the second-to-last part
    if len(parts) < 2:
        return 0.0
    ts_part = parts[-2]
    if ts_part.isdigit() and len(ts_part) >= 10:
        ts_ms = int(ts_part)
        if ts_ms > 1e12:
            return ts_ms / 1000.0
        return float(ts_ms)
    return 0.0


def signal_et_hour(signal_epoch):
    """Convert a UTC epoch timestamp to the hour-of-day in US Eastern time.

    For May 2026, EDT is in effect (UTC-4), so we subtract 4 hours.
    Returns the hour as a float (e.g. 9.5 for 9:30 AM ET).
    """
    if signal_epoch <= 0:
        return 0.0
    # EDT offset: UTC-4
    et_epoch = signal_epoch - 4 * 3600
    # Fractional hour within the day
    et_hour = (et_epoch % 86400) / 3600.0
    return et_hour


def signal_time_window_label(signal_epoch):
    """Classify signal by US equity market session bucket (ET time).

    Returns one of:
      Pre-market      — 4:00–9:30 AM ET
      ORB (9:30-10:00) — 9:30–10:00 AM ET (open range breakout)
      Morning (10:00-12:00) — 10:00 AM–12:00 PM ET
      Afternoon (12:00-16:00) — 12:00–4:00 PM ET
      After-hours (16:00-20:00) — 4:00–8:00 PM ET
      Overnight        — outside 4:00–20:00 ET
    """
    if signal_epoch <= 0:
        return "Overnight"
    et_hour = signal_et_hour(signal_epoch)

    if et_hour < 9.5:
        return "Pre-market"
    elif et_hour < 10.0:
        return "ORB (9:30-10:00)"
    elif et_hour < 12.0:
        return "Morning (10:00-12:00)"
    elif et_hour < 16.0:
        return "Afternoon (12:00-16:00)"
    elif et_hour < 20.0:
        return "After-hours (16:00-20:00)"
    else:
        return "Overnight"


# ── Phase 3: Microstructure Fingerprinting ────────────────────────

# Metadata key categories for event classification
KEY_CATEGORIES = {
    # Gamma wall / strike-level keys
    "gamma_wall": ["wall_strike", "call_wall_strike", "put_wall_strike", "gamma_wall", "gex_wall", "dex_wall"],
    # Gamma exposure keys
    "gamma_exposure": ["wall_gex", "gamma_exposure", "net_gex", "total_gex", "gex", "dex", "dgamma", "gmma", "net_gamma"],
    # Exchange / venue concentration keys
    "exchange_sweep": ["venue_concentration", "esi_memx", "esi_bats", "esi_cboe", "esi_nasdaq", "esi_arca",
                       "memx_volume", "bats_volume", "exchange_sweep", "iex_intent", "vsi", "vsi_pct", "vsi_roc"],
    # IV / volatility keys
    "iv_expansion": ["iv_skew", "iv_rank", "iv_percentile", "iv_expansion", "vix", "vvix", "vol_support_score"],
    # Volume keys
    "volume_spike": ["volume_ratio", "volume_spike", "relative_volume", "vol_ratio", "volume_surge",
                     "depth_bid_size", "depth_ask_size"],
    # Momentum / flow keys
    "momentum_burst": ["vamp_bias", "momentum_score", "momentum", "vamp_score", "flow_imbalance",
                       "buy_sell_ratio", "order_flow", "rejection_score", "liquidity_validation_score"],
    # Risk / quality keys
    "risk_quality": ["risk", "risk_reward_ratio", "liquidity_vacuum", "wall_strength",
                     "distance_to_wall_pct", "wall_side"],
}

# Thresholds for "extreme" values on numeric metadata keys
KEY_THRESHOLDS = {
    "wall_gex": 500000,        # $500K+ GEX threshold
    "wall_strike": None,       # use value matching (same strike)
    "vsi": 100,                # high VSI
    "vsi_pct": 1000,           # high VSI pct
    "vsi_roc": 100,            # high VSI ROC
    "iex_intent": 0.5,
    "rejection_score": 0.6,
    "liquidity_validation_score": 0.5,
    "vol_support_score": 0.5,
    "wall_strength": 0.5,
    "liquidity_vacuum": 0.5,
    "distance_to_wall_pct": 1.0,
    "risk_reward_ratio": 1.5,
    "gamma_exposure": 1000000,
    "volume_ratio": 2.0,
    "volume_spike": 2.0,
    "relative_volume": 2.0,
    "vol_ratio": 2.0,
    "buy_sell_ratio": 1.5,
    "venue_concentration": 2.5,
    "esi_memx": 0.5,
    "esi_bats": 0.5,
    "vamp_bias": 0.3,
    "iv_skew": 0.15,
}


def _is_numeric_key(key, sample_values):
    """Check if a metadata key is numeric across all sample values."""
    for v in sample_values:
        if v is None:
            continue
        if isinstance(v, (int, float)):
            continue
        if isinstance(v, str):
            try:
                float(v)
                continue
            except ValueError:
                return False
        return False
    return True


def _classify_key(key):
    """Classify a metadata key into a category."""
    key_lower = key.lower()
    for cat, keys in KEY_CATEGORIES.items():
        for k in keys:
            if k in key_lower:
                return cat
    return "other"


def _group_numeric_values(values, tolerance_pct=0.05):
    """Group numeric values that are close together (within tolerance_pct of the mean).
    
    Returns dict: group_label -> list of signal_id strings.
    """
    if not values:
        return {}
    
    filtered = [(float(v), sid) for v, sid in values if v is not None and isinstance(v, (int, float)) and abs(float(v)) > 0]
    if not filtered:
        return {}
    
    groups = {}
    used = [False] * len(filtered)
    
    for i in range(len(filtered)):
        if used[i]:
            continue
        group_center = filtered[i][0]
        group_label = f"{group_center:.1f}"
        group = [filtered[i][1]]  # signal_id
        used[i] = True
        
        for j in range(i + 1, len(filtered)):
            if used[j]:
                continue
            # Check if within tolerance of the group center
            if abs(filtered[j][0] - group_center) / abs(group_center) <= tolerance_pct:
                group.append(filtered[j][1])
                used[j] = True
        
        groups[group_label] = group
    
    return groups


def _group_threshold_values(values, threshold):
    """Group values by whether they exceed a threshold.
    
    values: list of (signal_value, signal_id) tuples.
    Returns dict: group_label -> list of signal_id strings.
    """
    above = [sid for v, sid in values if v is not None and isinstance(v, (int, float)) and float(v) >= threshold]
    below = [sid for v, sid in values if v is not None and isinstance(v, (int, float)) and float(v) < threshold]
    result = {}
    if above:
        result[f">= {threshold:.2f}"] = above
    if below:
        result[f"< {threshold:.2f}"] = below
    return result


def detect_event_clusters(all_signals):
    """Detect event clusters by grouping signals that share significant metadata values.
    
    Returns a list of cluster dicts sorted by coincidence_score (unique strategy count).
    Each cluster represents an "event type" — signals from different strategies
    triggered by the same microstructure condition.
    """
    # Step 1: Collect all metadata keys and their values across all signals
    key_values = defaultdict(list)  # key -> [(signal, value)]
    total_with_meta = 0
    for sig in all_signals:
        meta = sig.get("metadata", {})
        if not meta:
            continue
        total_with_meta += 1
        for k, v in meta.items():
            key_values[k].append((sig, v))
    
    if not key_values:
        return []
    
    # Step 2: Filter out non-discriminative keys
    # Only cluster on keys that are meaningful microstructure indicators.
    # Generic keys like "trend", "regime", "direction", "risk", "risk_reward_ratio",
    # "wall_side" are set by most strategies and don't represent specific
    # microstructure conditions.
    all_microstructure_keys = set()
    for cat_keys in KEY_CATEGORIES.values():
        all_microstructure_keys.update(cat_keys)
    
    # Keys to always exclude (too generic across strategies)
    EXCLUDED_KEYS = {"trend", "regime", "direction", "risk", "risk_reward_ratio",
                     "wall_side", "gates", "flip_mid", "flip_zone_lower",
                     "flip_zone_upper", "breakout_type", "liquidity_vacuum"}
    
    discriminative_keys = {}
    for key, entries in key_values.items():
        key_lower = key.lower()
        # Skip explicitly excluded generic keys
        if key_lower in EXCLUDED_KEYS:
            continue
        # Only include keys that match a known microstructure category
        is_micro = any(k in key_lower for k in all_microstructure_keys)
        if not is_micro:
            continue
        # Also skip keys that appear in >95% of signals
        coverage = len(entries) / total_with_meta if total_with_meta > 0 else 0
        if coverage > 0.95:
            continue
        discriminative_keys[key] = entries
    
    if not discriminative_keys:
        # Fallback: use all keys if none pass the filter
        discriminative_keys = key_values
    
    # Step 3: For each key, determine if numeric and group values
    # Build cluster assignments: each signal gets assigned to clusters for each key
    # Signal -> list of (key, group_label, cluster_id)
    signal_clusters = defaultdict(list)  # signal_id -> [(key, group_label, category)]
    
    # Track key stats
    key_stats = {}  # key -> {"category", "is_numeric", "groups", "threshold"}
    
    for key, entries in discriminative_keys.items():
        sample_values = [v for _, v in entries]
        is_num = _is_numeric_key(key, sample_values)
        category = _classify_key(key)
        
        if is_num:
            # Try value grouping first (for things like strike prices)
            # Pass (value, signal_id) tuples for tracking
            value_entries = [(v, sig.get("signal_id", "")) for sig, v in entries]
            groups = _group_numeric_values(value_entries, tolerance_pct=0.05)
            
            # If too many groups (>20), fall back to threshold grouping
            if len(groups) > 20:
                threshold = KEY_THRESHOLDS.get(key, None)
                if threshold is None:
                    # Use median as dynamic threshold
                    sorted_vals = sorted(float(v) for v in sample_values if v is not None and isinstance(v, (int, float)))
                    threshold = sorted_vals[len(sorted_vals) // 2] if sorted_vals else 0
                groups = _group_threshold_values(value_entries, threshold)
                key_stats[key] = {"category": category, "is_numeric": True, "groups": groups, "threshold": threshold, "group_type": "threshold"}
            else:
                key_stats[key] = {"category": category, "is_numeric": True, "groups": groups, "threshold": None, "group_type": "value"}
        else:
            # Categorical: group by exact string value
            cat_groups = defaultdict(list)
            for sig, v in entries:
                cat_groups[str(v)].append(sig.get("signal_id", ""))
            groups = dict(cat_groups)
            key_stats[key] = {"category": category, "is_numeric": False, "groups": groups, "threshold": None, "group_type": "categorical"}
        
        # Assign signals to clusters for this key
        for group_label, group_sigs in groups.items():
            # group_sigs is a list of signal_id strings; filter out empties
            valid_sigs = [s for s in group_sigs if s]
            if not valid_sigs:
                continue
            sig_tuple = tuple(valid_sigs)
            signal_clusters[sig_tuple].append((key, group_label, category))
    
    # Step 3: Build actual clusters by merging overlapping signal sets
    # Each cluster = set of signal_ids + list of (key, group_label, category)
    raw_clusters = []
    
    # Build a lookup map for signal_id -> signal object
    sig_map = {s.get("signal_id"): s for s in all_signals}
    
    for sig_tuple, assignments in signal_clusters.items():
        if len(sig_tuple) < 3:  # minimum 3 signals
            continue
        
        # Get unique strategies by looking up signal objects
        all_sigs = list(sig_tuple)
        strategies = set()
        for sid in all_sigs:
            sig = sig_map.get(sid)
            if sig:
                strategies.add(sig.get("strategy_id", "unknown"))
        
        if len(strategies) < 2:  # minimum 2 unique strategies
            continue
        
        raw_clusters.append({
            "signal_ids": set(all_sigs),
            "strategies": strategies,
            "assignments": assignments,
            "coincidence_score": len(strategies),
        })
    
    # Step 4: Merge overlapping clusters (same signals, same key)
    # Simple greedy merge: if two clusters share >50% of signals and same category, merge
    merged = [raw_clusters[0]] if raw_clusters else []
    for cluster in raw_clusters[1:]:
        merged_idx = None
        for i, existing in enumerate(merged):
            overlap = len(cluster["signal_ids"] & existing["signal_ids"])
            min_size = min(len(cluster["signal_ids"]), len(existing["signal_ids"]))
            if min_size > 0 and overlap / min_size > 0.5:
                # Check if same category is dominant
                existing_cats = {a[2] for a in existing["assignments"]}
                cluster_cats = {a[2] for a in cluster["assignments"]}
                if existing_cats & cluster_cats:  # shared category
                    merged_idx = i
                    break
        
        if merged_idx is not None:
            # Merge: union signals, union strategies, union assignments
            merged[merged_idx]["signal_ids"] |= cluster["signal_ids"]
            merged[merged_idx]["strategies"] |= cluster["strategies"]
            merged[merged_idx]["assignments"].extend(cluster["assignments"])
            merged[merged_idx]["coincidence_score"] = len(merged[merged_idx]["strategies"])
        else:
            merged.append(cluster)
    
    # Step 5: Build final clusters with metadata
    final_clusters = []
    
    for cluster in merged:
        signal_ids = cluster["signal_ids"]
        strategies = cluster["strategies"]
        assignments = cluster["assignments"]
        
        # Look up signal data
        sig_map = {s.get("signal_id"): s for s in all_signals}
        cluster_signals = [sig_map[sid] for sid in signal_ids if sid in sig_map]
        
        if len(cluster_signals) < 3:
            continue
        
        # Calculate win rate and avg P&L
        wins = sum(1 for s in cluster_signals if s.get("outcome") == "WIN")
        losses = sum(1 for s in cluster_signals if s.get("outcome") == "LOSS")
        total = wins + losses
        pnl_list = [s.get("pnl", 0.0) for s in cluster_signals]
        
        wr = win_rate(wins, losses, 0)
        avg_p = avg_pnl(pnl_list)
        
        # Determine dominant category and trigger
        category_counts = defaultdict(int)
        for _, _, cat in assignments:
            category_counts[cat] += 1
        dominant_cat = max(category_counts, key=category_counts.get)
        
        # Find the most common key in this category
        key_counts = defaultdict(int)
        for key, _, cat in assignments:
            if cat == dominant_cat:
                key_counts[key] += 1
        dominant_key = max(key_counts, key=key_counts.get) if key_counts else "unknown"
        
        # Find the most common group label for the dominant key
        dominant_group = None
        for key, group_label, cat in assignments:
            if key == dominant_key:
                dominant_group = group_label
                break
        
        # Classify event type name
        event_type = _classify_event_type(dominant_cat, dominant_key, dominant_group)
        
        # Build common trigger description
        trigger_desc = f"{dominant_key}={dominant_group}" if dominant_group else dominant_key
        if len(trigger_desc) > 35:
            trigger_desc = trigger_desc[:32] + "..."
        
        final_clusters.append({
            "event_type": event_type,
            "dominant_category": dominant_cat,
            "dominant_key": dominant_key,
            "dominant_group": dominant_group or "",
            "trigger_desc": trigger_desc,
            "signal_ids": signal_ids,
            "signal_count": len(cluster_signals),
            "unique_strategies": len(strategies),
            "strategies": sorted(strategies),
            "win_rate": wr,
            "avg_pnl": avg_p,
            "coincidence_score": len(strategies),
            "category_counts": dict(category_counts),
        })
    
    # Sort by coincidence_score descending, then by win_rate descending
    final_clusters.sort(key=lambda x: (x["coincidence_score"], x["win_rate"]), reverse=True)
    
    return final_clusters


def _classify_event_type(category, key, group_label):
    """Map category/key info to a human-readable event type name."""
    type_map = {
        "gamma_wall": "Gamma Wall Support",
        "exchange_sweep": "Exchange Sweep",
        "iv_expansion": "IV Expansion",
        "volume_spike": "Volume Spike",
        "momentum_burst": "Momentum Burst",
        "gamma_exposure": "Gamma Exposure",
    }
    
    base_name = type_map.get(category, "Cross-Strategy Consensus")
    
    # If multiple categories are represented, it's a consensus event
    # (handled by caller — this is the fallback)
    
    # Add strike info for gamma walls
    if category == "gamma_wall" and group_label:
        return f"Gamma Wall Support ({group_label})"
    
    # Add threshold info for exchange sweeps
    if category == "exchange_sweep" and group_label:
        return f"Exchange Sweep ({group_label})"
    
    # Add key info for others
    if category in ("iv_expansion", "volume_spike", "momentum_burst"):
        return base_name
    
    return base_name


def detect_temporal_bursts(all_signals, window_sec=10):
    """Detect clusters of signals from different strategies within a window.
    
    Uses the timestamp embedded in signal_id (epoch ms) since outcomes
    don't have real-time fields.
    """
    # Extract timestamps and sort
    signals_with_ts = []
    for sig in all_signals:
        ts = extract_signal_timestamp(sig)
        signals_with_ts.append((ts, sig))
    signals_with_ts.sort(key=lambda x: x[0])
    
    bursts = []
    
    i = 0
    while i < len(signals_with_ts):
        current_ts, current_sig = signals_with_ts[i]
        
        # Look ahead for signals within the window
        window_signals = [current_sig]
        j = i + 1
        while j < len(signals_with_ts) and signals_with_ts[j][0] <= current_ts + window_sec:
            window_signals.append(signals_with_ts[j][1])
            j += 1
        
        if len(window_signals) > 1:
            unique_strategies = {s["strategy_id"] for s in window_signals}
            if len(unique_strategies) > 1:
                # It's a confluence!
                strategies_list = ", ".join(sorted(list(unique_strategies)))
                # Determine primary reason from metadata overlap
                reasons = [s.get("reason", "") for s in window_signals if s.get("reason")]
                primary_reason = reasons[0] if reasons else "Multi-Strategy Confluence"
                # Truncate reason if too long
                if len(primary_reason) > 50:
                    primary_reason = primary_reason[:47] + "..."
                
                bursts.append({
                    "timestamp": current_ts,
                    "count": len(window_signals),
                    "strategies": strategies_list,
                    "coincidence_score": len(unique_strategies),
                    "reason": primary_reason
                })
                # Move i to j to avoid redundant overlapping windows of the same burst
                i = j
                continue
        i += 1
    return bursts


def win_rate(w, l, c):
    """Win rate excluding CLOSED (time expired)."""
    resolved = w + l
    if resolved == 0:
        return 0.0
    return (w / resolved) * 100


def avg_pnl(pnl_list):
    if not pnl_list:
        return 0.0
    return sum(pnl_list) / len(pnl_list)


def avg_hold(hold_times):
    if not hold_times:
        return 0.0
    return sum(hold_times) / len(hold_times)


def median_hold(hold_times):
    if not hold_times:
        return 0.0
    s = sorted(hold_times)
    n = len(s)
    if n % 2 == 0:
        return (s[n//2 - 1] + s[n//2]) / 2
    return s[n//2]


def fmt_pct(v):
    return f"{v:.1f}%"


def fmt_num(v, decimals=3):
    return f"{v:,.{decimals}f}"


def fmt_num_no_comma(v, decimals=2):
    return f"{v:.{decimals}f}"


def fmt_pnl(v):
    """Format P&L value for fixed-width display."""
    if v >= 0:
        return f" +${v:,.2f}"
    else:
        return f"-${abs(v):,.2f}"


def fmt_pct_cell(v):
    """Format percentage for fixed-width cell."""
    return f"{v:6.1f}%"


def fmt_count(v):
    """Format count for fixed-width cell."""
    return f"{v:>5}"


def fmt_pct_pct(v):
    """Format P&L% for fixed-width cell."""
    return f"{v:7.1f}%"


def table_header(cols, widths=None):
    """Build a fixed-width table header.
    cols: list of column name strings.
    widths: optional list of column widths (defaults to len of each col name).
    """
    if widths is None:
        widths = [len(c) for c in cols]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header = "|" + "|".join(f" {c:<{w}} " for c, w in zip(cols, widths)) + "|"
    return header + "\n" + sep  # no trailing newline — data rows follow immediately


def table_row(values, widths):
    """Build a fixed-width table row."""
    cells = []
    for v, w in zip(values, widths):
        cells.append(f" {str(v):<{w}} ")
    return "|" + "|".join(cells) + "|"


def generate_report(all_signals, strategy_results):
    """Generate the markdown report with fixed-width tables."""
    lines = []
    lines.append("# Strategy Performance Analysis — Round 3 Validation (Regular Hours)")
    lines.append("")
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"**Date:** {report_date}  |  **Generated:** {report_time}  |  **Total Resolved Signals:** {len(all_signals):,}  |  **Strategies Analyzed:** {len(strategy_results)}  |  **Confidence ≥ 5%**  |  **Regular Hours**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Overall Summary ──────────────────────────────────────────
    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    total_closed = sum(r["closed"] for r in strategy_results.values())
    total_pnl = sum(r["total_pnl"] for r in strategy_results.values())
    total_closed_pnl = sum(r["closed_pnl"] for r in strategy_results.values())
    all_pnl = [s.get("pnl", 0) for s in all_signals]
    resolved_pnl_all = []
    for r in strategy_results.values():
        resolved_pnl_all.extend(r.get("resolved_pnl", []))

    lines.append("## Overall Summary")
    lines.append("")
    lines.append(table_header(["Metric", "Value"], [20, 60]))
    lines.append(table_row(["Total Resolved Signals", f"{len(all_signals):,}"], [20, 60]))
    lines.append(table_row(["Total Wins", f"{total_wins:,}"], [20, 60]))
    lines.append(table_row(["Total Losses", f"{total_losses:,}"], [20, 60]))
    lines.append(table_row(["Time-Expired (CLOSED)", f"{total_closed:,}"], [20, 60]))
    lines.append(table_row(["Overall Win Rate", f"{win_rate(total_wins, total_losses, total_closed):.1f}%"], [20, 60]))
    lines.append(table_row(["Total P&L (resolved)", f"${fmt_num_no_comma(total_pnl, 2)}"], [20, 60]))
    lines.append(table_row(["Avg P&L per Resolved Signal", f"${fmt_num_no_comma(avg_pnl(resolved_pnl_all))}"], [20, 60]))
    if total_closed_pnl != 0:
        lines.append(table_row(["Total P&L (time-outs)", f"${fmt_num_no_comma(total_closed_pnl, 2)}"], [20, 60]))
        lines.append(table_row(["Avg P&L per Signal (all)", f"${fmt_num_no_comma(avg_pnl(all_pnl))}"], [20, 60]))
    lines.append(table_row(["Symbols Traded", ", ".join(sorted(set(s["_symbol"] for s in all_signals)))], [20, 60]))
    lines.append("")

    # ── Per-Strategy Deep Dive ───────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Per-Strategy Deep Dive")
    lines.append("")

    for sid in sorted(strategy_results.keys()):
        r = strategy_results[sid]
        total = r["total"]
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        overall_wr = win_rate(r["wins"], r["losses"], r["closed"])
        avg_p = avg_pnl(r["pnl_list"])
        avg_h = avg_hold(r["hold_times"])
        med_h = median_hold(r["hold_times"])

        lines.append(f"### {sid}")
        lines.append("")
        avg_p_resolved = avg_pnl(r.get("resolved_pnl", [])) if r.get("resolved_pnl") else 0.0
        avg_p_all = avg_pnl(r["pnl_list"]) if r["pnl_list"] else 0.0
        lines.append(
            f"**Symbols:** {', '.join(sorted(r['symbols']))}  |  "
            f"**Total Signals:** {total:,}  |  "
            f"**Win Rate:** {wr:.1f}%  |  "
            f"**Avg P&L (resolved):** ${fmt_num(avg_p_resolved)}  |  "
            f"**Avg P&L (all):** ${fmt_num(avg_p_all)}  |  "
            f"**Avg Hold:** {avg_h:.0f}s ({avg_h/60:.1f}m)  |  "
            f"**Median Hold:** {med_h:.0f}s"
        )
        lines.append("")

        # ── 1. Confidence Level Performance ──────────────────────
        lines.append("#### 1) Performance by Confidence Level")
        lines.append("")
        widths = [14, 5, 5, 6, 6, 9, 8, 8, 8]
        h = table_header(["Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L (resolved)", "Avg P&L (all)", "Avg P&L%"], widths)
        lines.append(h)

        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if cb and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                resolved_total = cb["wins"] + cb["losses"]
                cap_resolved = cb["pnl"] / resolved_total if resolved_total > 0 else 0
                cap_all = (cb["pnl"] + cb["closed_pnl"]) / cb["total"] if cb["total"] > 0 else 0
                cpp = (cb["pnl_pct"] + cb["closed_pnl_pct"]) / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap_resolved)}", f"${fmt_num(cap_all)}", f"{cpp:.1f}%"], widths))

        # Any "Other" bucket
        for label, cb in r["confidence_buckets"].items():
            if label not in [l for l, _, _ in CONFIDENCE_BUCKETS] and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                resolved_total = cb["wins"] + cb["losses"]
                cap_resolved = cb["pnl"] / resolved_total if resolved_total > 0 else 0
                cap_all = (cb["pnl"] + cb["closed_pnl"]) / cb["total"] if cb["total"] > 0 else 0
                cpp = (cb["pnl_pct"] + cb["closed_pnl_pct"]) / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap_resolved)}", f"${fmt_num(cap_all)}", f"{cpp:.1f}%"], widths))

        lines.append("")

        # ── 2. Market Type Performance ───────────────────────────
        lines.append("#### 2) Performance by Market Type")
        lines.append("")
        widths = [20, 5, 5, 6, 6, 9, 8]
        h = table_header(["Market Type", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for mk in sorted(r["trend_perf"].keys()):
            tp = r["trend_perf"][mk]
            if tp["total"] > 0:
                twr = win_rate(tp["wins"], tp["losses"], tp["closed"])
                tap = tp["pnl"] / tp["total"]
                lines.append(table_row([mk, tp["total"], tp["wins"], tp["losses"], tp["closed"],
                                       f"{twr:.1f}%", f"${fmt_num(tap)}"], widths))

        lines.append("")
        lines.append("**Regime Performance:**")
        lines.append("")
        widths = [20, 5, 5, 6, 6, 9, 8]
        h = table_header(["Regime", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for rk in sorted(r["regime_perf"].keys()):
            rp = r["regime_perf"][rk]
            if rp["total"] > 0:
                rwr = win_rate(rp["wins"], rp["losses"], rp["closed"])
                rap = rp["pnl"] / rp["total"]
                lines.append(table_row([rk, rp["total"], rp["wins"], rp["losses"], rp["closed"],
                                       f"{rwr:.1f}%", f"${fmt_num(rap)}"], widths))

        lines.append("")

        # ── 3. Timeframe Performance (Broad) ─────────────────────
        lines.append("#### 3) Performance by Timeframe (Time Held — Broad)")
        lines.append("")
        lines.append("*Broad buckets covering major session windows.*")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Time Held", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for tk in sorted(r["time_held_broad"].keys()):
            twp = r["time_held_broad"][tk]
            if twp["total"] > 0:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                tap = twp["pnl"] / twp["total"]
                lines.append(table_row([tk, twp["total"], twp["wins"], twp["losses"], twp["closed"],
                                       f"{twr:.1f}%", f"${fmt_num(tap)}"], widths))

        lines.append("")

        # ── 3b. Signal Generation Time ───────────────────────────
        lines.append("#### 3b) Signal Generation Time")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8, 10]
        h = table_header(["Time Window", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L", "Significance"], widths)
        lines.append(h)

        for sk in sorted(r["signal_time_window"].keys()):
            sp = r["signal_time_window"][sk]
            if sp["total"] > 0:
                swr = win_rate(sp["wins"], sp["losses"], sp["closed"])
                sap = sp["pnl"] / sp["total"]
                z, is_sig, low_sample = binomial_z_score(swr, sp["total"], overall_wr)
                if low_sample:
                    sig_marker = "⚠️"
                elif is_sig:
                    sig_marker = "🟢" if z > 0 else "🔴"
                else:
                    sig_marker = "—"
                lines.append(table_row([sk, sp["total"], sp["wins"], sp["losses"], sp["closed"],
                                       f"{swr:.1f}%", f"${fmt_num(sap)}", sig_marker], widths))

        lines.append("")

        # ── 3c. Confidence Distribution by Session ───────────────
        lines.append("#### 3c) Confidence Distribution by Session")
        lines.append("")
        lines.append("*Percentage of signals by confidence tier within each regular hours session window.*")
        lines.append("")
        widths_sc = [22, 6, 10, 10, 10, 9, 9, 9]
        h_sc = table_header(["Session", "Total", "High (70%+)", "Medium (50-69%)", "Low (<50%)", "High %", "Medium %", "Low %"], widths_sc)
        lines.append(h_sc)

        session_order = ["ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"]
        for sk in session_order:
            sc = r["session_confidence"].get(sk)
            if sc and sc["total"] > 0:
                high_pct = (sc["high"] / sc["total"]) * 100
                med_pct = (sc["medium"] / sc["total"]) * 100
                low_pct = (sc["low"] / sc["total"]) * 100
                lines.append(table_row([sk, sc["total"], sc["high"], sc["medium"], sc["low"],
                                       f"{high_pct:.1f}%", f"{med_pct:.1f}%", f"{low_pct:.1f}%"], widths_sc))

        lines.append("")

        # ── 3d. Session × Confidence Cross-Tabulation ────────────
        # Only show for strategies with data in >=2 sessions AND >=2 confidence buckets
        scp = r["session_confidence_perf"]
        sessions_with_data = {s for s, buckets in scp.items() if any(b["total"] > 0 for b in buckets.values())}
        all_conf_buckets = set()
        for buckets in scp.values():
            for label, data in buckets.items():
                if data["total"] > 0:
                    all_conf_buckets.add(label)

        if len(sessions_with_data) >= 2 and len(all_conf_buckets) >= 2:
            lines.append("#### 3d) Session × Confidence Cross-Tabulation")
            lines.append("")
            lines.append("*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*")
            lines.append("")
            widths_xc = [22, 10, 6, 5, 6, 6, 9, 12, 10]
            h_xc = table_header(["Session", "Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L (resolved)", "Significance"], widths_xc)
            lines.append(h_xc)

            session_order = ["ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"]
            conf_order = [l for l, _, _ in CONFIDENCE_BUCKETS]

            for sk in session_order:
                if sk not in sessions_with_data:
                    continue
                for cb_label in conf_order:
                    cell = scp[sk].get(cb_label)
                    if not cell or cell["total"] == 0:
                        continue
                    cwr = win_rate(cell["wins"], cell["losses"], cell["closed"])
                    resolved = cell["wins"] + cell["losses"]
                    avg_p_xc = cell["pnl"] / resolved if resolved > 0 else 0.0
                    z, is_sig, low_sample = binomial_z_score(cwr, cell["total"], overall_wr)
                    if low_sample:
                        sig_marker = "⚠️"
                    elif is_sig:
                        sig_marker = "🟢" if z > 0 else "🔴"
                    else:
                        sig_marker = "—"
                    lines.append(table_row([sk, cb_label, cell["total"], cell["wins"], cell["losses"], cell["closed"],
                                           f"{cwr:.1f}%", f"${fmt_num(avg_p_xc)}", sig_marker], widths_xc))

            lines.append("")

        # ── 4. Direction Performance ─────────────────────────────
        lines.append("#### 4) Performance by Direction")
        lines.append("")
        widths = [12, 5, 5, 6, 6, 9, 8]
        h = table_header(["Direction", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for dk in sorted(r["direction_perf"].keys()):
            dp = r["direction_perf"][dk]
            if dp["total"] > 0:
                dwr = win_rate(dp["wins"], dp["losses"], dp["closed"])
                dap = dp["pnl"] / dp["total"]
                lines.append(table_row([dk, dp["total"], dp["wins"], dp["losses"], dp["closed"],
                                       f"{dwr:.1f}%", f"${fmt_num(dap)}"], widths))

        lines.append("")

        # ── 5. Hold Time Distribution (Fine-Grained) ─────────────
        lines.append("#### 5) Hold Time Distribution (Fine-Grained)")
        lines.append("")
        lines.append("*Fine-grained buckets covering detailed hold durations.*")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Hold Time", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for hk in sorted(r["time_held_fine"].keys()):
            htb = r["time_held_fine"][hk]
            if htb["total"] > 0:
                hwr = win_rate(htb["wins"], htb["losses"], htb["closed"])
                hap = htb["pnl"] / htb["total"]
                lines.append(table_row([hk, htb["total"], htb["wins"], htb["losses"], htb["closed"],
                                       f"{hwr:.1f}%", f"${fmt_num(hap)}"], widths))

        lines.append("")

        # ── 6. Insights & Recommendations ────────────────────────
        lines.append("#### 6) Insights & Recommendations")
        lines.append("")

        insights = generate_insights(sid, r)
        for insight in insights:
            lines.append(f"- {insight}")
        lines.append("")

        lines.append("---")
        lines.append("")

    # ── Phase 1: Statistical Edge Discovery ──────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Statistical Edge Anomalies (Phase 1)")
    lines.append("")
    lines.append("Strategies that statistically deviate from the global win-rate baseline within")
    lines.append("specific confidence buckets. Flagged when lift > 50% above global OR > 1.5 sigma.")
    lines.append("")

    global_buckets = compute_global_baseline(strategy_results)
    stddevs = compute_bucket_stddev(strategy_results)
    anomalies = detect_edge_anomalies(strategy_results, global_buckets, stddevs)

    # ── Phase 2: Temporal Confluence Engine ──────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Temporal Burst Events (Phase 2)")
    lines.append("")
    lines.append("High-frequency bursts where multiple independent strategies fire simultaneously,")
    lines.append("indicating multi-factor market events. Window: 10 seconds.")
    lines.append("")

    bursts = detect_temporal_bursts(all_signals, window_sec=10)

    if bursts:
        # Sort by coincidence score descending
        bursts.sort(key=lambda x: x["coincidence_score"], reverse=True)
        # Limit to top 50 to keep report readable
        top_bursts = bursts[:50]

        lines.append("### Top Temporal Bursts")
        lines.append("")
        widths = [14, 6, 8, 12, 40]
        h = table_header(["Timestamp (s)", "Count", "Strategies", "Coincidence", "Reason"], widths)
        lines.append(h)

        for b in top_bursts:
            lines.append(table_row([
                b["timestamp"], b["count"], b["strategies"],
                b["coincidence_score"], b["reason"]
            ], widths))

        lines.append("")
        lines.append(f"**{len(bursts)} total burst(s) detected.** Top {len(top_bursts)} shown above.")
    else:
        lines.append("**No temporal bursts detected.** No multi-strategy confluence events found in the dataset.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Phase 3: Microstructure Event Clusters ─────────────────────
    lines.append("## Microstructure Event Clusters (Phase 3)")
    lines.append("")
    lines.append("Signals grouped by shared metadata fingerprints, not strategy names.")
    lines.append("When independent strategies fire on the same microstructure condition,")
    lines.append("they form an **Event Cluster** — a signal that the market is reacting to")
    lines.append("a specific structural event, regardless of which strategy detected it.")
    lines.append("")

    clusters = detect_event_clusters(all_signals)

    if clusters:
        # ── Event Type Summary Table ─────────────────────────────
        lines.append("### Event Type Summary")
        lines.append("")
        widths = [28, 8, 10, 22, 8, 10]
        h = table_header(["Event Type", "Signals", "Strategies", "Common Trigger", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        # Group by event_type, aggregate
        type_groups = defaultdict(list)
        for c in clusters:
            type_groups[c["event_type"]].append(c)

        # Show top event types (up to 15)
        # Pre-build a signal_id -> outcome map for fast lookup
        sig_outcome = {s.get("signal_id"): s.get("outcome") for s in all_signals}
        shown = 0
        for etype, clist in sorted(type_groups.items(), key=lambda x: sum(c["signal_count"] for c in x[1]), reverse=True):
            if shown >= 15:
                break
            total_sigs = sum(c["signal_count"] for c in clist)
            total_strats = len(set(s for c in clist for s in c["strategies"]))
            all_pnl = sum(c["avg_pnl"] * c["signal_count"] for c in clist) / total_sigs if total_sigs > 0 else 0
            total_wins = sum(1 for c in clist for sid in c["signal_ids"] if sig_outcome.get(sid) == "WIN")
            total_losses = sum(1 for c in clist for sid in c["signal_ids"] if sig_outcome.get(sid) == "LOSS")
            combined_wr = win_rate(total_wins, total_losses, 0)

            lines.append(table_row([
                etype[:27], f"{total_sigs:,}", str(total_strats),
                clist[0]["trigger_desc"][:21],
                f"{combined_wr:.1f}%", f"${fmt_num(all_pnl)}"
            ], widths))
            shown += 1

        lines.append("")

        # ── Top Event Clusters ───────────────────────────────────
        lines.append("### Top Event Clusters")
        lines.append("")
        lines.append("Top 20 clusters sorted by coincidence score (unique strategy count).")
        lines.append("Each cluster represents signals from different strategies triggered by the same")
        lines.append("microstructure condition — evidence of a real market event.")
        lines.append("")
        widths = [14, 6, 6, 8, 8, 10, 10, 40]
        h = table_header(["Event Type", "Signals", "Strats", "Score", "Win Rate", "Avg P&L", "Trigger", "Strategy List"], widths)
        lines.append(h)

        for c in clusters[:20]:
            strat_list = ", ".join(c["strategies"][:4])
            if len(c["strategies"]) > 4:
                strat_list += f" (+{len(c['strategies'])-4})"
            lines.append(table_row([
                c["event_type"][:13],
                c["signal_count"],
                c["unique_strategies"],
                c["coincidence_score"],
                f"{c['win_rate']:.1f}%",
                f"${fmt_num(c['avg_pnl'])}",
                c["trigger_desc"][:9],
                strat_list[:39]
            ], widths))

        lines.append("")
        lines.append(f"**{len(clusters)} event cluster(s) detected.** Clusters with higher coincidence scores")
        lines.append(f"represent stronger evidence of structural market events.")
    else:
        lines.append("**No event clusters detected.** Insufficient metadata overlap between strategies to form clusters.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Global baseline table
    lines.append("### Global Baseline Win Rates by Confidence Bucket")
    lines.append("")
    widths = [14, 8, 6, 6, 6, 9, 9]
    h = table_header(["Bucket", "Total", "Wins", "Losses", "Closed", "Win Rate", "StdDev"], widths)
    lines.append(h)

    for label, lo, hi in CONFIDENCE_BUCKETS:
        g = global_buckets[label]
        sd = stddevs.get(label, 0.0)
        if g["total"] > 0:
            lines.append(table_row([label, g["total"], g["wins"], g["losses"], g["closed"],
                                   f"{g['win_rate']:.1f}%", f"{sd:.1f}"], widths))

    lines.append("")

    # ── Table A: Global Baseline by Session ─────────────────────
    lines.append("### Global Baseline by Session")
    lines.append("")
    lines.append("*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*")
    lines.append("")
    widths_session = [22, 8, 6, 6, 6, 9, 8]
    h_session = table_header(["Session", "Total", "Wins", "Losses", "Closed", "Win Rate", "StdDev"], widths_session)
    lines.append(h_session)

    session_order = ["ORB (9:30-10:00)", "Morning (10:00-12:00)", "Afternoon (12:00-16:00)"]
    session_agg = {s: {"total": 0, "wins": 0, "losses": 0, "closed": 0} for s in session_order}
    session_strat_rates = {s: [] for s in session_order}

    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_confidence_perf", {}).items():
            if session not in session_agg:
                continue
            s_agg = session_agg[session]
            s_rates = session_strat_rates[session]
            session_total = 0
            session_wins = 0
            session_losses = 0
            session_closed = 0
            for conf_label, data in buckets.items():
                if data["total"] > 0:
                    session_total += data["total"]
                    session_wins += data["wins"]
                    session_losses += data["losses"]
                    session_closed += data.get("closed", 0)
            if session_total > 0:
                s_agg["total"] += session_total
                s_agg["wins"] += session_wins
                s_agg["losses"] += session_losses
                s_agg["closed"] += session_closed
                s_rates.append(win_rate(session_wins, session_losses, session_closed))

    for s in session_order:
        sa = session_agg[s]
        if sa["total"] > 0:
            sr = session_strat_rates[s]
            sd = 0.0
            if len(sr) >= 2:
                mean = sum(sr) / len(sr)
                variance = sum((r - mean) ** 2 for r in sr) / (len(sr) - 1)
                sd = variance ** 0.5
            lines.append(table_row([s, sa["total"], sa["wins"], sa["losses"], sa["closed"],
                                   f"{win_rate(sa['wins'], sa['losses'], sa['closed']):.1f}%", f"{sd:.1f}"], widths_session))

    lines.append("")

    # ── Table B: Global Baseline by Session × Confidence ────────
    lines.append("### Global Baseline by Session × Confidence")
    lines.append("")
    lines.append("*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*")
    lines.append("")
    widths_xc = [22, 12, 8, 6, 6, 6, 9]
    h_xc = table_header(["Session", "Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate"], widths_xc)
    lines.append(h_xc)

    conf_order = [l for l, _, _ in CONFIDENCE_BUCKETS]
    global_session_buckets = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0})
    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_confidence_perf", {}).items():
            if session not in session_agg:
                continue
            for conf_label, data in buckets.items():
                if data["total"] > 0:
                    gsb = global_session_buckets[(session, conf_label)]
                    gsb["total"] += data["total"]
                    gsb["wins"] += data["wins"]
                    gsb["losses"] += data["losses"]
                    gsb["closed"] += data.get("closed", 0)

    for sk in session_order:
        for cb_label in conf_order:
            gsb = global_session_buckets.get((sk, cb_label))
            if gsb and gsb["total"] >= 10:
                lines.append(table_row([sk, cb_label, gsb["total"], gsb["wins"], gsb["losses"], gsb["closed"],
                                       f"{win_rate(gsb['wins'], gsb['losses'], gsb['closed']):.1f}%"], widths_xc))

    lines.append("")

    # Anomalies table
    if anomalies:
        lines.append("### Detected Anomalies")
        lines.append("")
        widths = [24, 12, 9, 9, 8, 8, 8, 8, 8]
        h = table_header(["Strategy", "Bucket", "Strat WR", "Global WR", "Lift", "Sigma", "Total", "Wins", "Losses"], widths)
        lines.append(h)

        for a in anomalies:
            tag = "[ALPHA]"
            lines.append(table_row([f"{tag} {a['strategy']}", a["bucket"],
                                   f"{a['strategy_wr']:.1f}%", f"{a['global_wr']:.1f}%",
                                   f"{a['lift']:.0f}%", f"{a['sigma']:.2f}",
                                   a["total"], a["wins"], a["losses"]], widths))

        lines.append("")
        lines.append(f"**{len(anomalies)} anomaly(ies) detected.** These represent potential micro-edges worth investigating.")
    else:
        lines.append("**No anomalies detected.** All strategies are performing within expected deviation from global baselines.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Session × Confidence Anomalies ─────────────────────────────
    lines.append("## Session × Confidence Anomalies")
    lines.append("")
    lines.append("Cross-tab analysis: how each strategy performs in specific session×confidence combos")
    lines.append("compared to the global baseline for that same combo. Flags combos where a strategy")
    lines.append("shows a significant lift (>50% above global) or >1.5σ deviation.")
    lines.append("")

    # Compute global session×confidence baseline
    global_session_buckets = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0})
    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_confidence_perf", {}).items():
            for conf_label, data in buckets.items():
                if data["total"] > 0:
                    gsb = global_session_buckets[(session, conf_label)]
                    gsb["total"] += data["total"]
                    gsb["wins"] += data["wins"]
                    gsb["losses"] += data["losses"]
                    gsb["closed"] += data.get("closed", 0)

    # Compute win_rate for each global session×confidence combo
    for key, gsb in global_session_buckets.items():
        gsb["win_rate"] = win_rate(gsb["wins"], gsb["losses"], gsb["closed"])

    # Compute stddev per session×confidence combo for sigma calculation
    session_conf_rates = defaultdict(list)
    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_confidence_perf", {}).items():
            for conf_label, data in buckets.items():
                if data["total"] >= 5:  # minimum sample size
                    wr = win_rate(data["wins"], data["losses"], data.get("closed", 0))
                    session_conf_rates[(session, conf_label)].append(wr)

    session_conf_stddevs = {}
    for key, rates in session_conf_rates.items():
        if len(rates) >= 2:
            mean = sum(rates) / len(rates)
            variance = sum((r - mean) ** 2 for r in rates) / (len(rates) - 1)
            session_conf_stddevs[key] = variance ** 0.5
        else:
            session_conf_stddevs[key] = 0.0

    # Detect session×confidence anomalies
    session_conf_anomalies = []
    for sid, r in strategy_results.items():
        for session, buckets in r.get("session_confidence_perf", {}).items():
            for conf_label, data in buckets.items():
                if data["total"] < 5:  # minimum sample size
                    continue

                gsb = global_session_buckets.get((session, conf_label))
                if not gsb or gsb["total"] < 10:  # minimum global sample size
                    continue

                strategy_wr = win_rate(data["wins"], data["losses"], data.get("closed", 0))
                global_wr = gsb["win_rate"]

                if global_wr == 0:
                    continue

                # Lift: how much better than global baseline
                lift = ((strategy_wr - global_wr) / global_wr) * 100 if global_wr > 0 else 0

                # Sigma deviation
                sd = session_conf_stddevs.get((session, conf_label), 0)
                sigma = (strategy_wr - global_wr) / sd if sd > 0 else 0

                # Flag if: lift > 50% above global OR > 1.5 sigma above global
                if lift > 50 or sigma > 1.5:
                    session_conf_anomalies.append({
                        "strategy": sid,
                        "session": session,
                        "confidence": conf_label,
                        "strategy_wr": strategy_wr,
                        "global_wr": global_wr,
                        "lift": lift,
                        "sigma": sigma,
                        "total": data["total"],
                        "wins": data["wins"],
                        "losses": data["losses"],
                    })

    # Sort by lift descending
    session_conf_anomalies.sort(key=lambda x: x["lift"], reverse=True)

    if session_conf_anomalies:
        widths = [24, 12, 12, 7, 6, 6, 8, 8, 6, 7, 12]
        h = table_header(["Strategy", "Session", "Confidence", "Total", "Wins", "Losses",
                          "Strat WR", "Global WR", "Lift", "Sigma", "Significance"], widths)
        lines.append(h)

        for a in session_conf_anomalies:
            if a["sigma"] > 2.0:
                sig = "⚡ HIGH"
            elif a["lift"] > 100:
                sig = "🔥 STRONG"
            else:
                sig = "⚠ MODERATE"
            lines.append(table_row([
                f"[ALPHA] {a['strategy']}", a["session"], a["confidence"],
                a["total"], a["wins"], a["losses"],
                f"{a['strategy_wr']:.1f}%", f"{a['global_wr']:.1f}%",
                f"{a['lift']:.0f}%", f"{a['sigma']:.2f}", sig
            ], widths))

        lines.append("")
        lines.append(f"**{len(session_conf_anomalies)} session×confidence anomaly(ies) detected.** "
                     f"These represent strategy-specific edges that are active in particular sessions "
                     f"and confidence levels — useful for time-aware strategy tuning.")
    else:
        lines.append("**No session×confidence anomalies detected.** Strategy performance is consistent across sessions and confidence levels.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Cross-Strategy Rankings ──────────────────────────────────
    lines.append("## Cross-Strategy Rankings")
    lines.append("")
    widths = [5, 24, 7, 8, 8, 14, 16, 22, 14, 14]
    lines.append(
        table_header(["Rank", "Strategy", "Signals", "Win Rate", "Avg P&L",
                      "Best Confidence", "Best Session", "Best Session×Conf", "Best Market", "Best Timeframe"], widths)
    )

    ranked = []
    for sid, r in strategy_results.items():
        wr = win_rate(r["wins"], r["losses"], r["closed"])
        avg_p = avg_pnl(r["pnl_list"])

        best_cb = None
        best_cb_wr = -1
        for label, cb in r["confidence_buckets"].items():
            if cb["total"] >= 5:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                if cwr > best_cb_wr:
                    best_cb_wr = cwr
                    best_cb = label

        best_mt = None
        best_mt_wr = -1
        for mk, tp in r["trend_perf"].items():
            if tp["total"] >= 5:
                twr = win_rate(tp["wins"], tp["losses"], tp["closed"])
                if twr > best_mt_wr:
                    best_mt_wr = twr
                    best_mt = mk

        best_tf = None
        best_tf_wr = -1
        for tk, twp in r["time_held_broad"].items():
            if twp["total"] >= 5:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                if twr > best_tf_wr:
                    best_tf_wr = twr
                    best_tf = tk

        # Best session
        best_session = None
        best_session_wr = -1
        for session, buckets in r.get("session_confidence_perf", {}).items():
            session_total = sum(b["total"] for b in buckets.values())
            session_wins = sum(b["wins"] for b in buckets.values())
            session_losses = sum(b["losses"] for b in buckets.values())
            if session_total >= 5:
                s_wr = win_rate(session_wins, session_losses, 0)
                if s_wr > best_session_wr:
                    best_session_wr = s_wr
                    best_session = session

        # Best session × confidence combo
        best_sc_combo = None
        best_sc_wr = -1
        for session, buckets in r.get("session_confidence_perf", {}).items():
            for conf_label, data in buckets.items():
                if data["total"] >= 5:
                    c_wr = win_rate(data["wins"], data["losses"], data["closed"])
                    if c_wr > best_sc_wr:
                        best_sc_wr = c_wr
                        best_sc_combo = f"{session} @ {conf_label}"

        ranked.append((sid, r["total"], wr, avg_p, best_cb, best_session, best_sc_combo, best_mt, best_tf))

    ranked.sort(key=lambda x: x[3], reverse=True)

    for i, (sid, total, wr, avg_p, best_cb, best_session, best_sc_combo, best_mt, best_tf) in enumerate(ranked, 1):
        lines.append(table_row([
            str(i), sid, f"{total:,}", f"{wr:.1f}%", f"${fmt_num(avg_p)}",
            best_cb or "N/A", best_session or "N/A", best_sc_combo or "N/A",
            best_mt or "N/A", best_tf or "N/A"
        ], widths))

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Forge 🐙 — Round 3 Validation Analysis — Regular Hours Only*")

    return "\n".join(lines)


def compute_global_baseline(strategy_results):
    """Compute global win-rate baseline per confidence bucket across all strategies.
    
    Returns a dict mapping bucket label -> {"total", "wins", "losses", "win_rate"}.
    """
    global_buckets = {}
    for label, lo, hi in CONFIDENCE_BUCKETS:
        global_buckets[label] = {"total": 0, "wins": 0, "losses": 0, "closed": 0}
    
    for sid, r in strategy_results.items():
        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if cb and cb["total"] > 0:
                g = global_buckets[label]
                g["total"] += cb["total"]
                g["wins"] += cb["wins"]
                g["losses"] += cb["losses"]
                g["closed"] += cb["closed"]
    
    for label, g in global_buckets.items():
        g["win_rate"] = win_rate(g["wins"], g["losses"], g["closed"])
    
    return global_buckets


def compute_bucket_stddev(strategy_results):
    """Compute per-bucket standard deviation of win-rates across strategies.
    
    Returns a dict mapping bucket label -> stddev.
    """
    bucket_rates = {label: [] for label, _, _ in CONFIDENCE_BUCKETS}
    
    for sid, r in strategy_results.items():
        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if cb and cb["total"] >= 5:  # minimum sample size
                wr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                bucket_rates[label].append(wr)
    
    stddevs = {}
    for label, rates in bucket_rates.items():
        if len(rates) >= 2:
            mean = sum(rates) / len(rates)
            variance = sum((r - mean) ** 2 for r in rates) / (len(rates) - 1)
            stddevs[label] = variance ** 0.5
        else:
            stddevs[label] = 0.0
    
    return stddevs


def detect_edge_anomalies(strategy_results, global_buckets, stddevs):
    """Detect strategies that outperform the global baseline within their confidence buckets.
    
    Returns a list of anomaly dicts:
    [
        {"strategy": sid, "bucket": label, "strategy_wr": x, "global_wr": y, "lift": z, "sigma": s},
        ...
    ]
    """
    anomalies = []
    
    for sid, r in strategy_results.items():
        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if not cb or cb["total"] < 5:  # minimum sample size
                continue
            
            g = global_buckets[label]
            if g["total"] < 10:  # minimum global sample size
                continue
            
            strategy_wr = win_rate(cb["wins"], cb["losses"], cb["closed"])
            global_wr = g["win_rate"]
            
            if global_wr == 0:
                continue
            
            # Lift: how much better than global baseline
            lift = ((strategy_wr - global_wr) / global_wr) * 100 if global_wr > 0 else 0
            
            # Sigma deviation
            sd = stddevs.get(label, 0)
            sigma = (strategy_wr - global_wr) / sd if sd > 0 else 0
            
            # Flag if: lift > 50% above global OR > 1.5 sigma above global
            if lift > 50 or sigma > 1.5:
                anomalies.append({
                    "strategy": sid,
                    "bucket": label,
                    "strategy_wr": strategy_wr,
                    "global_wr": global_wr,
                    "lift": lift,
                    "sigma": sigma,
                    "total": cb["total"],
                    "wins": cb["wins"],
                    "losses": cb["losses"],
                })
    
    # Sort by lift descending
    anomalies.sort(key=lambda x: x["lift"], reverse=True)
    return anomalies


def generate_insights(sid, r):
    """Generate qualitative insights for a strategy."""
    insights = []
    total = r["total"]
    wr = win_rate(r["wins"], r["losses"], r["closed"])
    overall_wr = wr  # overall WR for this strategy
    avg_p = avg_pnl(r["pnl_list"])
    avg_h = avg_hold(r["hold_times"])
    
    # Win rate assessment
    if wr >= 65:
        insights.append(f"✅ Strong win rate of {wr:.1f}% — this strategy consistently picks directional moves.")
    elif wr >= 50:
        insights.append(f"⚖️ Moderate win rate of {wr:.1f}% — strategy works but needs tighter entry/exit or higher confidence thresholds.")
    else:
        insights.append(f"⚠️ Low win rate of {wr:.1f}% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.")
    
    # P&L assessment — resolved vs all-inclusive
    resolved_pnl = r.get("resolved_pnl", [])
    avg_p_resolved = avg_pnl(resolved_pnl) if resolved_pnl else 0.0
    avg_p_all = avg_pnl(r["pnl_list"]) if r["pnl_list"] else 0.0

    if avg_p_resolved > 0:
        insights.append(f"💰 Positive avg P&L per resolved signal: ${avg_p_resolved:.2f} — profitable even with {wr:.1f}% win rate (good risk/reward).")
    else:
        insights.append(f"📉 Negative avg P&L per resolved signal: ${avg_p_resolved:.2f} — losses outweigh wins. Review stop-loss placement and entry timing.")

    if avg_p_all != avg_p_resolved:
        closed_count = r["closed"]
        if avg_p_all > 0:
            insights.append(f"💰 Avg P&L per signal (incl. {closed_count} time-outs): ${avg_p_all:.2f}")
        else:
            insights.append(f"📉 Avg P&L per signal (incl. {closed_count} time-outs): ${avg_p_all:.2f}")
    
    # Confidence analysis
    best_cb = None
    best_cb_wr = -1
    for label, cb in r["confidence_buckets"].items():
        if cb["total"] >= 5:
            cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
            if cwr > best_cb_wr:
                best_cb_wr = cwr
                best_cb = label
    if best_cb:
        insights.append(f"🎯 Best performance at {best_cb} confidence ({best_cb_wr:.1f}% win rate) — consider raising minimum confidence threshold.")
    
    # Worst confidence
    worst_cb = None
    worst_cb_wr = 101
    for label, cb in r["confidence_buckets"].items():
        if cb["total"] >= 5:
            cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
            if cwr < worst_cb_wr:
                worst_cb_wr = cwr
                worst_cb = label
    if worst_cb:
        insights.append(f"🚫 Worst at {worst_cb} ({worst_cb_wr:.1f}% win rate) — signals in this range may be noise. Consider filtering them out.")
    
    # Market type
    best_mt = None
    best_mt_pnl = -999999
    for mk, tp in r["trend_perf"].items():
        if tp["total"] >= 5:
            tap = tp["pnl"] / tp["total"]
            if tap > best_mt_pnl:
                best_mt_pnl = tap
                best_mt = mk
    if best_mt:
        insights.append(f"📈 Best market type: {best_mt} (avg P&L ${best_mt_pnl:.2f}) — this strategy thrives in {best_mt.lower()} conditions.")
    
    # Timeframe (broad)
    best_tf = None
    best_tf_pnl = -999999
    for tk, twp in r["time_held_broad"].items():
        if twp["total"] >= 5:
            tap = twp["pnl"] / twp["total"]
            if tap > best_tf_pnl:
                best_tf_pnl = tap
                best_tf = tk
    if best_tf:
        insights.append(f"⏰ Best timeframe: {best_tf} (avg P&L ${best_tf_pnl:.2f}) — optimal time held is {best_tf}.")

    # Signal generation time
    best_sw = None
    best_sw_wr = -1
    best_sw_total = 0
    for label, sp in r["signal_time_window"].items():
        if sp["total"] >= 5:
            swr = win_rate(sp["wins"], sp["losses"], sp["closed"])
            if swr > best_sw_wr:
                best_sw_wr = swr
                best_sw = label
                best_sw_total = sp["total"]
    if best_sw:
        _, is_sig, low_sample = binomial_z_score(best_sw_wr, best_sw_total, overall_wr)
        if low_sample:
            insights.append(f"⚠️ Best signal generation window: {best_sw} ({best_sw_wr:.1f}% win rate) — but only {best_sw_total} signals, results may not be statistically significant.")
        elif is_sig:
            insights.append(f"✅ Best signal generation window: {best_sw} ({best_sw_wr:.1f}% win rate) — statistically significant above overall WR.")
        else:
            insights.append(f"🕐 Best signal generation window: {best_sw} ({best_sw_wr:.1f}% win rate) — signals in this window have the highest hit rate.")
    
    # Hold time
    if avg_h > 600:
        insights.append(f"⏱️ Long avg hold time ({avg_h:.0f}s / {avg_h/60:.1f}m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.")
    elif avg_h < 60:
        insights.append(f"⚡ Very fast avg hold time ({avg_h:.0f}s) — strategy captures quick moves. Ensure slippage/commissions don't eat into thin margins.")
    
    # CLOSED signals
    closed_pct = (r["closed"] / total * 100) if total > 0 else 0
    if closed_pct > 30:
        insights.append(f"⏳ {closed_pct:.0f}% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.")
    
    return insights


def main():
    print("Loading all signal outcomes...")
    all_signals = load_all_outcomes()
    print(f"Loaded {len(all_signals):,} resolved signals")

    # Market open timestamp detection no longer needed — time windows now use ET session buckets.

    # Verify timestamp extraction on first few signals
    sample_count = 0
    for sig in all_signals[:100]:
        ts = extract_signal_timestamp(sig)
        if ts > 0:
            sample_count += 1
            if sample_count <= 3:
                print(f"Sample signal: {sig.get('signal_id', '')[:80]} -> {ts}")
    print(f"Timestamp extraction: {sample_count}/100 samples had valid timestamps")

    print("Analyzing strategies...")
    strategy_results = analyze_strategy(all_signals)
    print(f"Found {len(strategy_results)} unique strategies")
    
    print("Generating report...")
    report = generate_report(all_signals, strategy_results)
    
    # Write to file
    OUTPUT_FILE.write_text(report)
    print(f"\n✅ Report written to {OUTPUT_FILE}")
    
    # Also print to stdout
    print("\n" + "=" * 80)
    print(report)


if __name__ == "__main__":
    main()
