#!/usr/bin/env python3
"""
Comprehensive per-strategy performance analysis for Round 3 validation.
Analyzes all signal_outcomes_*.jsonl files across all symbols.
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

LOG_DIR = Path("/home/hologaun/projects/syngex/log")
OUTPUT_FILE = Path("/home/hologaun/projects/syngex/analysis/analyzed_strategies_forge.md")

# ── Time window definitions ──────────────────────────────────────────
# Market opens at 9:30 AM PT. Timestamps are epoch seconds.
# We detect the first signal timestamp as "market open" for each symbol.
TIME_WINDOW_SIZE = 10  # seconds for temporal confluence

TIME_WINDOWS = {
    "ORB (9:30-10:00)":  (0,   30*60),    # 0-30 min
    "Early (10:00-11:30)": (30*60, 90*60),  # 30-90 min
    "Mid-day (11:30-14:00)": (90*60, 240*60), # 90-240 min
    "Late (14:00-16:00)": (240*60, 480*60),  # 240-480 min
},

CONFIDENCE_BUCKETS = [
    ("10-19%",  0.10, 0.20),
    ("20-29%",  0.20, 0.30),
    ("30-39%",  0.30, 0.40),
    ("40-49%",  0.40, 0.50),
    ("50-59%",  0.50, 0.60),
    ("60-69%",  0.60, 0.70),
    ("70-79%",  0.70, 0.80),
    ("80-89%",  0.80, 0.90),
    ("90-99%",  0.90, 1.00),
    ("100%",    1.00, 1.01),
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


def load_all_outcomes():
    """Load all signal outcome files."""
    all_signals = []
    import glob
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


def time_window_label(hold_time_sec, resolution_time_sec, first_ts):
    """Determine which time window a signal falls into based on resolution time."""
    elapsed = resolution_time_sec - first_ts
    for label, (lo, hi) in TIME_WINDOWS.items():
        if lo <= elapsed < hi:
            return label
    return "Post-close / Unknown"


def analyze_strategy(signals):
    """Analyze a single strategy across all symbols."""
    results = {}
    
    for sig in signals:
        sid = sig["strategy_id"]
        if sid not in results:
            results[sid] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "closed": 0,
                "total_pnl": 0.0,
                "total_pnl_pct": 0.0,
                "avg_hold_time": 0.0,
                "confidence_buckets": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0, "pnl_pct": 0.0}),
                "trend_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "regime_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "time_window_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "direction_perf": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "hold_time_buckets": defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "closed": 0, "pnl": 0.0}),
                "symbols": set(),
                "pnl_list": [],
                "hold_times": [],
                # SI score tracking
                "si_buckets": defaultdict(lambda: {"pnl": [], "win": []}),
                "si_winners": [],
                "si_losers": [],
                # SI component breakdown
                "si_mom_winners": [], "si_mom_losers": [],
                "si_liq_winners": [], "si_liq_losers": [],
                "si_reg_winners": [], "si_reg_losers": [],
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
        r["total_pnl"] += pnl
        r["total_pnl_pct"] += pnl_pct
        r["pnl_list"].append(pnl)
        
        hold = sig.get("hold_time", 0.0)
        r["hold_times"].append(hold)
        
        # Confidence bucket
        conf = sig.get("confidence", 0.5)
        cb = bucket_confidence(conf)
        cb_data = r["confidence_buckets"][cb]
        cb_data["total"] += 1
        if outcome == "WIN": cb_data["wins"] += 1
        elif outcome == "LOSS": cb_data["losses"] += 1
        elif outcome == "CLOSED": cb_data["closed"] += 1
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
        
        # Time window (use resolution_time - first_ts approximation)
        # We'll use hold_time as proxy for time-of-day grouping
        tw = "Unknown"
        if hold < 30*60:
            tw = "ORB / Early (0-30 min)"
        elif hold < 90*60:
            tw = "Early (30-90 min)"
        elif hold < 240*60:
            tw = "Mid-day (90-240 min)"
        elif hold < 480*60:
            tw = "Late (240-480 min)"
        else:
            tw = "Extended (>8h)"
        twp = r["time_window_perf"][tw]
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
        
        # SI Score tracking
        meta = sig.get("metadata", {})
        si_score = meta.get("si_score")
        if si_score is not None:
            pnl = sig.get("pnl", 0.0)
            if si_score < 0.3:
                bucket = "0.0-0.3"
            elif si_score < 0.6:
                bucket = "0.3-0.6"
            elif si_score < 0.9:
                bucket = "0.6-0.9"
            else:
                bucket = "0.9-1.0"
            r["si_buckets"][bucket]["pnl"].append(pnl)
            r["si_buckets"][bucket]["win"].append(pnl > 0)
            if pnl > 0:
                r["si_winners"].append(si_score)
            else:
                r["si_losers"].append(si_score)

            # SI component breakdown
            si_mom = meta.get("si_momentum")
            si_liq = meta.get("si_liquidity")
            si_reg = meta.get("si_regime")
            if si_mom is not None:
                (r["si_mom_winners"] if pnl > 0 else r["si_mom_losers"]).append(si_mom)
            if si_liq is not None:
                (r["si_liq_winners"] if pnl > 0 else r["si_liq_losers"]).append(si_liq)
            if si_reg is not None:
                (r["si_reg_winners"] if pnl > 0 else r["si_reg_losers"]).append(si_reg)

        # Hold time buckets
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
        htb = r["hold_time_buckets"][ht_key]
        htb["total"] += 1
        if outcome == "WIN": htb["wins"] += 1
        elif outcome == "LOSS": htb["losses"] += 1
        elif outcome == "CLOSED": htb["closed"] += 1
        htb["pnl"] += pnl
    
    return results


def extract_signal_timestamp(sig):
    """Extract epoch-second timestamp from signal_id (format: strategy_timestamp_random)."""
    sid = sig.get("signal_id", "")
    parts = sid.split("_")
    # Find the numeric timestamp part (usually 13 digits for epoch ms)
    for part in parts:
        if part.isdigit() and len(part) >= 10:
            ts_ms = int(part)
            # If it looks like epoch milliseconds (>1e12), convert to seconds
            if ts_ms > 1e12:
                return ts_ms / 1000.0
            return float(ts_ms)
    return 0.0


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


def fmt_num(v, decimals=1):
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


def output_si_analysis(lines, r):
    """Output SI score analysis section for a strategy."""
    lines.append("#### SI Score Analysis")
    lines.append("")

    si_buckets = r["si_buckets"]
    si_winners = r["si_winners"]
    si_losers = r["si_losers"]

    bucket_order = ["0.0-0.3", "0.3-0.6", "0.6-0.9", "0.9-1.0"]

    # Check if we have any SI data at all
    total_si = sum(len(si_buckets[b]["pnl"]) for b in bucket_order)
    if total_si == 0:
        lines.append("**No SI score data available for this strategy.**")
        lines.append("")
        return

    # Print bucket stats
    widths = [10, 5, 8, 14]
    h = table_header(["Bucket", "N", "Win Rate", "Avg P&L"], widths)
    lines.append(h)

    for bucket in bucket_order:
        entries = si_buckets[bucket]
        pnls = entries["pnl"]
        wins_list = entries["win"]
        if not pnls:
            lines.append(table_row([bucket, "0", "N/A", "N/A"], widths))
            continue
        wins = sum(1 for w in wins_list if w)
        total = len(pnls)
        avg_p = sum(pnls) / total
        wr = win_rate(wins, total - wins, 0)
        lines.append(table_row([bucket, str(total), f"{wr:.1f}%", f"${fmt_num(avg_p)}"], widths))

    lines.append("")

    # Average SI score for winners vs losers
    if si_winners and si_losers:
        avg_w = sum(si_winners) / len(si_winners)
        avg_l = sum(si_losers) / len(si_losers)
        lines.append(f"**Avg SI score (winners):** {avg_w:.3f}  |  **Avg SI score (losers):** {avg_l:.3f}")
        lines.append("")
    elif si_winners:
        avg_w = sum(si_winners) / len(si_winners)
        lines.append(f"**Avg SI score (winners):** {avg_w:.3f} (no losers with SI data)")
        lines.append("")
    elif si_losers:
        avg_l = sum(si_losers) / len(si_losers)
        lines.append(f"**Avg SI score (losers):** {avg_l:.3f} (no winners with SI data)")
        lines.append("")

    # SI Component Breakdown
    lines.append("**SI Component Breakdown:**")
    lines.append("")
    widths = [12, 18, 18]
    h = table_header(["Component", "Winners Avg", "Losers Avg"], widths)
    lines.append(h)

    # Momentum
    mom_w = r["si_mom_winners"]
    mom_l = r["si_mom_losers"]
    if mom_w and mom_l:
        lines.append(table_row(["Momentum", f"{sum(mom_w)/len(mom_w):.3f}", f"{sum(mom_l)/len(mom_l):.3f}"], widths))
    elif mom_w:
        lines.append(table_row(["Momentum", f"{sum(mom_w)/len(mom_w):.3f}", "N/A"], widths))
    elif mom_l:
        lines.append(table_row(["Momentum", "N/A", f"{sum(mom_l)/len(mom_l):.3f}"], widths))
    else:
        lines.append(table_row(["Momentum", "N/A", "N/A"], widths))

    # Liquidity
    liq_w = r["si_liq_winners"]
    liq_l = r["si_liq_losers"]
    if liq_w and liq_l:
        lines.append(table_row(["Liquidity", f"{sum(liq_w)/len(liq_w):.3f}", f"{sum(liq_l)/len(liq_l):.3f}"], widths))
    elif liq_w:
        lines.append(table_row(["Liquidity", f"{sum(liq_w)/len(liq_w):.3f}", "N/A"], widths))
    elif liq_l:
        lines.append(table_row(["Liquidity", "N/A", f"{sum(liq_l)/len(liq_l):.3f}"], widths))
    else:
        lines.append(table_row(["Liquidity", "N/A", "N/A"], widths))

    # Regime
    reg_w = r["si_reg_winners"]
    reg_l = r["si_reg_losers"]
    if reg_w and reg_l:
        lines.append(table_row(["Regime", f"{sum(reg_w)/len(reg_w):.3f}", f"{sum(reg_l)/len(reg_l):.3f}"], widths))
    elif reg_w:
        lines.append(table_row(["Regime", f"{sum(reg_w)/len(reg_w):.3f}", "N/A"], widths))
    elif reg_l:
        lines.append(table_row(["Regime", "N/A", f"{sum(reg_l)/len(reg_l):.3f}"], widths))
    else:
        lines.append(table_row(["Regime", "N/A", "N/A"], widths))

    lines.append("")


def generate_report(all_signals, strategy_results):
    """Generate the markdown report with fixed-width tables."""
    lines = []
    lines.append("# Strategy Performance Analysis — Round 3 Validation")
    lines.append("")
    lines.append(f"**Date:** 2026-05-06  |  **Total Resolved Signals:** {len(all_signals):,}  |  **Strategies Analyzed:** {len(strategy_results)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Overall Summary ──────────────────────────────────────────
    total_wins = sum(r["wins"] for r in strategy_results.values())
    total_losses = sum(r["losses"] for r in strategy_results.values())
    total_closed = sum(r["closed"] for r in strategy_results.values())
    total_pnl = sum(r["total_pnl"] for r in strategy_results.values())
    all_pnl = [s.get("pnl", 0) for s in all_signals]

    lines.append("## Overall Summary")
    lines.append("")
    lines.append(table_header(["Metric", "Value"], [20, 60]))
    lines.append(table_row(["Total Resolved Signals", f"{len(all_signals):,}"], [20, 60]))
    lines.append(table_row(["Total Wins", f"{total_wins:,}"], [20, 60]))
    lines.append(table_row(["Total Losses", f"{total_losses:,}"], [20, 60]))
    lines.append(table_row(["Time-Expired (CLOSED)", f"{total_closed:,}"], [20, 60]))
    lines.append(table_row(["Overall Win Rate", f"{win_rate(total_wins, total_losses, total_closed):.1f}%"], [20, 60]))
    lines.append(table_row(["Total P&L", f"${fmt_num_no_comma(total_pnl, 2)}"], [20, 60]))
    lines.append(table_row(["Avg P&L per Signal", f"${fmt_num_no_comma(avg_pnl(all_pnl))}"], [20, 60]))
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
        avg_p = avg_pnl(r["pnl_list"])
        avg_h = avg_hold(r["hold_times"])
        med_h = median_hold(r["hold_times"])

        lines.append(f"### {sid}")
        lines.append("")
        lines.append(
            f"**Symbols:** {', '.join(sorted(r['symbols']))}  |  "
            f"**Total Signals:** {total:,}  |  "
            f"**Win Rate:** {wr:.1f}%  |  "
            f"**Avg P&L:** ${fmt_num(avg_p)}  |  "
            f"**Avg Hold:** {avg_h:.0f}s ({avg_h/60:.1f}m)  |  "
            f"**Median Hold:** {med_h:.0f}s"
        )
        lines.append("")

        # ── 1. Confidence Level Performance ──────────────────────
        lines.append("#### 1) Performance by Confidence Level")
        lines.append("")
        widths = [14, 5, 5, 6, 6, 9, 8, 8]
        h = table_header(["Confidence", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L", "Avg P&L%"], widths)
        lines.append(h)

        for label, lo, hi in CONFIDENCE_BUCKETS:
            cb = r["confidence_buckets"].get(label)
            if cb and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                cap = cb["pnl"] / cb["total"] if cb["total"] > 0 else 0
                cpp = cb["pnl_pct"] / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap)}", f"{cpp:.1f}%"], widths))

        # Any "Other" bucket
        for label, cb in r["confidence_buckets"].items():
            if label not in [l for l, _, _ in CONFIDENCE_BUCKETS] and cb["total"] > 0:
                cwr = win_rate(cb["wins"], cb["losses"], cb["closed"])
                cap = cb["pnl"] / cb["total"] if cb["total"] > 0 else 0
                cpp = cb["pnl_pct"] / cb["total"] if cb["total"] > 0 else 0
                lines.append(table_row([label, cb["total"], cb["wins"], cb["losses"], cb["closed"],
                                       f"{cwr:.1f}%", f"${fmt_num(cap)}", f"{cpp:.1f}%"], widths))

        lines.append("")

        # ── SI Score Analysis ────────────────────────────────────
        output_si_analysis(lines, r)

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

        # ── 3. Timeframe Performance ─────────────────────────────
        lines.append("#### 3) Performance by Timeframe (Hold Duration)")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Timeframe", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for tk in sorted(r["time_window_perf"].keys()):
            twp = r["time_window_perf"][tk]
            if twp["total"] > 0:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                tap = twp["pnl"] / twp["total"]
                lines.append(table_row([tk, twp["total"], twp["wins"], twp["losses"], twp["closed"],
                                       f"{twr:.1f}%", f"${fmt_num(tap)}"], widths))

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

        # ── 5. Hold Time Distribution ────────────────────────────
        lines.append("#### 5) Hold Time Distribution")
        lines.append("")
        widths = [22, 5, 5, 6, 6, 9, 8]
        h = table_header(["Hold Time", "Total", "Wins", "Losses", "Closed", "Win Rate", "Avg P&L"], widths)
        lines.append(h)

        for hk in sorted(r["hold_time_buckets"].keys()):
            htb = r["hold_time_buckets"][hk]
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

    # ── Cross-Strategy Rankings ──────────────────────────────────
    lines.append("## Cross-Strategy Rankings")
    lines.append("")
    widths = [5, 24, 7, 8, 8, 16, 14, 14]
    lines.append(
        table_header(["Rank", "Strategy", "Signals", "Win Rate", "Avg P&L",
                      "Best Confidence", "Best Market", "Best Timeframe"], widths)
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
        for tk, twp in r["time_window_perf"].items():
            if twp["total"] >= 5:
                twr = win_rate(twp["wins"], twp["losses"], twp["closed"])
                if twr > best_tf_wr:
                    best_tf_wr = twr
                    best_tf = tk

        ranked.append((sid, r["total"], wr, avg_p, best_cb, best_mt, best_tf))

    ranked.sort(key=lambda x: x[3], reverse=True)

    for i, (sid, total, wr, avg_p, best_cb, best_mt, best_tf) in enumerate(ranked, 1):
        lines.append(table_row([
            str(i), sid, f"{total:,}", f"{wr:.1f}%", f"${fmt_num(avg_p)}",
            best_cb or "N/A", best_mt or "N/A", best_tf or "N/A"
        ], widths))

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Forge 🐙 — Round 3 Validation Analysis*")

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
    avg_p = avg_pnl(r["pnl_list"])
    avg_h = avg_hold(r["hold_times"])
    
    # Win rate assessment
    if wr >= 65:
        insights.append(f"✅ Strong win rate of {wr:.1f}% — this strategy consistently picks directional moves.")
    elif wr >= 50:
        insights.append(f"⚖️ Moderate win rate of {wr:.1f}% — strategy works but needs tighter entry/exit or higher confidence thresholds.")
    else:
        insights.append(f"⚠️ Low win rate of {wr:.1f}% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.")
    
    # P&L assessment
    if avg_p > 0:
        insights.append(f"💰 Positive avg P&L of ${avg_p:.2f} per signal — profitable even with {wr:.1f}% win rate (good risk/reward).")
    else:
        insights.append(f"📉 Negative avg P&L of ${avg_p:.2f} per signal — losses outweigh wins. Review stop-loss placement and entry timing.")
    
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
    
    # Timeframe
    best_tf = None
    best_tf_pnl = -999999
    for tk, twp in r["time_window_perf"].items():
        if twp["total"] >= 5:
            tap = twp["pnl"] / twp["total"]
            if tap > best_tf_pnl:
                best_tf_pnl = tap
                best_tf = tk
    if best_tf:
        insights.append(f"⏰ Best timeframe: {best_tf} (avg P&L ${best_tf_pnl:.2f}) — optimal hold duration is {best_tf}.")
    
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
