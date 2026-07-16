#!/usr/bin/env python3
"""
build_pnl_report.py — Scan all Syngex strategy files and extract
entry / target / stop-loss pricing logic, then write pnl.md.
"""

from __future__ import annotations

import ast
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STRATEGIES_DIR = Path(os.path.expanduser("~/projects/syngex/strategies"))
OUTPUT_FILE = Path(os.path.expanduser("~/projects/syngex/analysis/pnl.md"))

LAYER_DISPLAY = {
    "layer1": "Layer 1",
    "layer2": "Layer 2",
    "layer3": "Layer 3",
    "full_data": "Full Data",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_module_docstring(source: str) -> str:
    """Extract the module-level docstring (first triple-quoted string at top level)."""
    lines = source.split("\n")
    in_docstring = False
    doc_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            if stripped.count(quote) >= 2:
                content = stripped[3:stripped.rfind(quote)]
                return content.strip()
            else:
                in_docstring = True
                continue
        if in_docstring:
            if stripped.endswith('"""') or stripped.endswith("'''"):
                end_quote = '"""' if '"""' in stripped else "'''"
                doc_lines.append(stripped[:stripped.find(end_quote)])
                in_docstring = False
            else:
                doc_lines.append(stripped)
    return " ".join(doc_lines).strip()


def get_class_attr(source: str, attr_name: str) -> Optional[str]:
    """Return the value of a class attribute like strategy_id or layer."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == attr_name:
                            if isinstance(item.value, ast.Constant):
                                return str(item.value.value)
    return None


def get_top_level_constants(source: str) -> Dict[str, str]:
    """Find top-level CONSTANT_NAME = value assignments (uppercase names only)."""
    results: Dict[str, str] = {}
    for m in re.finditer(
        r"^(?P<name>[A-Z][A-Z_0-9]+)\s*=\s*(?P<value>[^\n#]+)",
        source,
        re.MULTILINE,
    ):
        name = m.group("name")
        value = m.group("value").strip().rstrip(",")
        # Skip common non-price constants
        skip_names = {
            "MIN_CONFIDENCE", "MAX_CONFIDENCE", "MIN_DATA_POINTS",
            "TOP_OI_STRIKES_COUNT", "SLICE_BODY_RATIO",
            "SLICE_VOLUME_RATIO", "DIVERGENCE_VOLUME_THRESHOLD",
            "LIQUIDITY_VACUUM_RATIO", "DELTA_ACCEL_THRESHOLD_LONG",
            "DELTA_ACCEL_THRESHOLD_SHORT", "GAMMA_MAGNITUDE_THRESHOLD",
            "BOUNCE_TARGET_MULT", "SLICE_TARGET_MULT",
            "ATR_NORMALIZATION_CAP", "TARGET_MIN_PCT",
            "BOUNCE_PROXIMITY_PCT", "SLICE_PROXIMITY_PCT",
            "WALL_PROXIMITY_PCT", "WALL_DISTANCE_PCT",
            "VOL_THRESHOLD_MULT", "BREAKOUT_VOL_MULT",
            "CONFLUENCE_MIN", "CONFLUENCE_MAX",
            "GAMMA_FLIP_THRESHOLD", "FLIP_CONFIDENCE",
            "GEX_DIVERGENCE_SIGMA", "GEX_IMBALANCE_RATIO",
            "VAMP_MOMENTUM_THRESHOLD", "VAMP_CONFIDENCE",
            "VORTEX_COMPRESSION_THRESHOLD",
            "DEPTH_DECAY_THRESHOLD", "DEPTH_IMBALANCE_RATIO",
            "EXCHANGE_FLOW_RATIO", "EXCHANGE_FLOW_CONCENTRATION_THRESHOLD",
            "EXCHANGE_FLOW_IMBALANCE_THRESHOLD",
            "PARTICIPANT_DIVERGENCE_THRESHOLD",
            "PARTICIPANT_DIVERSITY_CONV_THRESHOLD",
            "ORDER_BOOK_FRAGMENTATION_THRESHOLD",
            "ORDER_BOOK_STACKING_THRESHOLD",
            "OBBI_AGGRESSION_THRESHOLD",
            "PROB_SHIFT_THRESHOLD", "PROB_WEIGHT_THRESHOLD",
            "SMILE_DYNAMICS_THRESHOLD",
            "SKEW_DYNAMICS_THRESHOLD",
            "IV_BAND_THRESHOLD", "THETA_BURN_THRESHOLD",
            "GAMMA_VOLUME_THRESHOLD",
            "IV_SKEW_SQUEEZE_THRESHOLD",
            "GAMMA_BREAKER_THRESHOLD",
            "EXTRINSIC_FLOW_THRESHOLD",
            "EXTRINSIC_INTRINSIC_THRESHOLD",
            "GHOST_PREMIUM_THRESHOLD",
            "IRON_ANCHOR_THRESHOLD",
            "WHALE_TRACKER_THRESHOLD",
            "CALL_PUT_FLOW_THRESHOLD",
            "DELTA_GAMMA_SQUEEZE_THRESHOLD",
            "DELTA_IV_DIVERGENCE_THRESHOLD",
            "DELTA_VOLUME_EXHAUSTION_THRESHOLD",
        }
        if name in skip_names:
            continue
        results[name] = value.strip()
    return results


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_entry(source: str, fname: str) -> str:
    """Extract how entry price is determined."""
    # Check for explicit entry = underlying_price
    if re.search(r"\bentry\s*=\s*underlying_price\b", source):
        return "Set to current underlying price (`entry = underlying_price`)"
    if re.search(r"\bentry\s*=\s*price\b", source):
        return "Set to current price (`entry = price`)"
    if re.search(r"\bentry\s*=\s*self\._price\b", source):
        return "Set to instance price property (`entry = self._price`)"
    if re.search(r"\bentry\s*=\s*data\[.underlying_price.\]", source):
        return "Set to underlying price from data dict"
    if re.search(r"\bentry\s*=\s*current_price\b", source):
        return "Set to current price variable"
    # Check for entry relative to a reference
    if re.search(r"\bentry\s*=\s*\w+\s*\*\s*\(1\s*[+\-]\s*", source):
        return "Computed relative to a reference price (wall/strike) with a percentage offset"
    if re.search(r"\bentry\s*=\s*signal_price\b", source):
        return "Set to signal price from data"
    if re.search(r"\bentry\s*=\s*(rolling|mean|avg)", source, re.I):
        return "Set to a rolling mean / average price"
    return "Set to current underlying price (default: `entry = underlying_price`)"


def extract_stop(source: str, constants: Dict[str, str]) -> str:
    """Extract stop-loss logic."""
    stops = []

    # 1. STOP_PCT constants
    stop_pct_names = [n for n in constants if "STOP_PCT" in n]
    if stop_pct_names:
        for name in stop_pct_names:
            val = constants[name]
            stops.append(f"`{name}` = {val}")

    # 2. Wall-based stops
    if re.search(r"stop\s*=\s*wall_strike\s*\*\s*\(\s*1\s*\-\s*STOP_PAST_WALL_PCT", source):
        stops.append("Wall-based: `stop = wall_strike * (1 - STOP_PAST_WALL_PCT)`")
    if re.search(r"stop\s*=\s*wall_strike\s*\*\s*\(\s*1\s*\+\s*STOP_PAST_WALL_PCT", source):
        stops.append("Wall-based: `stop = wall_strike * (1 + STOP_PAST_WALL_PCT)`")

    # 3. Percentage-based stops
    if re.search(r"stop\s*=\s*entry\s*\*\s*\(\s*1\s*\-\s*STOP_PCT", source):
        stops.append("Percentage: `stop = entry * (1 - STOP_PCT)` for LONG")
    if re.search(r"stop\s*=\s*entry\s*\*\s*\(\s*1\s*\+\s*STOP_PCT", source):
        stops.append("Percentage: `stop = entry * (1 + STOP_PCT)` for SHORT")

    # 4. stop_distance based
    if re.search(r"stop\s*=\s*entry\s*\-\s*stop_distance", source):
        stops.append("Distance-based: `stop = entry - stop_distance` (LONG)")
    if re.search(r"stop\s*=\s*entry\s*\+\s*stop_distance", source):
        stops.append("Distance-based: `stop = entry + stop_distance` (SHORT)")

    # 5. Dynamic / effective_stop_pct
    if re.search(r"effective_stop_pct", source):
        stops.append("Dynamic: uses `effective_stop_pct` (IV-adjusted)")

    # 6. Trailing stop
    if re.search(r"TRAIL_STOP_PCT", source):
        stops.append("Trailing stop: `TRAIL_STOP_PCT`")

    # 7. Liquidity-aware stop
    if re.search(r"_liquidity_aware_stop", source):
        stops.append("Liquidity-aware: `self._liquidity_aware_stop()`")

    # 8. ATR-based stops
    if re.search(r"atr.*stop|stop.*atr", source, re.I):
        stops.append("ATR-normalized stop distance")

    # 9. Rolling mean-based
    if re.search(r"rolling.*stop|stop.*rolling", source, re.I):
        stops.append("Rolling mean-based stop")

    if stops:
        return "\n".join(f"- {s}" for s in stops)

    return "Not explicitly defined (inherited from base or not present)"


def extract_target(source: str, constants: Dict[str, str]) -> str:
    """Extract target price logic."""
    targets = []

    # 1. TARGET_RISK_MULT and similar
    target_mult_names = [n for n in constants if "TARGET" in n and ("MULT" in n or "EXPANSION" in n)]
    if target_mult_names:
        for name in target_mult_names:
            val = constants[name]
            targets.append(f"`{name}` = {val}")

    # 2. ATR-based targets
    if re.search(r"atr.*target|target.*atr", source, re.I):
        targets.append("ATR-normalized: scaled by current ATR / mean ATR ratio")

    # 3. Risk-multiplication targets
    if re.search(r"target\s*=\s*entry\s*\+\s*risk\s*\*", source):
        targets.append("Risk-multiplication: `target = entry + risk * MULT` (LONG)")
    if re.search(r"target\s*=\s*entry\s*\-\s*risk\s*\*", source):
        targets.append("Risk-multiplication: `target = entry - risk * MULT` (SHORT)")

    # 4. stop_distance based
    if re.search(r"target\s*=\s*entry\s*\+\s*\(stop_distance\s*\*\s*target_risk_mult\)", source):
        targets.append("Distance-based: `target = entry + (stop_distance * target_risk_mult)` (LONG)")
    if re.search(r"target\s*=\s*entry\s*\-\s*\(stop_distance\s*\*\s*target_risk_mult\)", source):
        targets.append("Distance-based: `target = entry - (stop_distance * target_risk_mult)` (SHORT)")

    # 5. Percentage-based targets
    if re.search(r"target\s*=\s*entry\s*\*\s*\(\s*1\s*\+", source):
        targets.append("Percentage: `target = entry * (1 + PCT)`")

    # 6. Wall/strike targets
    if re.search(r"target\s*=\s*wall_price\s*\*\s*\(\s*1\s*\+\s*WALL_PROXIMITY_PCT", source):
        targets.append("Wall target: `target = wall_price * (1 + WALL_PROXIMITY_PCT)`")
    if re.search(r"target\s*=\s*strike\s*\*\s*\(\s*1\s*\+\s*", source):
        targets.append("Strike target: `target = strike * (1 + PCT)`")

    # 7. Rolling mean targets
    if re.search(r"rolling.*target|target.*rolling", source, re.I):
        targets.append("Rolling mean-based target")

    # 8. IV-scaled targets
    if re.search(r"iv.*target|target.*iv", source, re.I):
        targets.append("IV-scaled target")

    # 9. RR ratio tracking
    if re.search(r"risk_reward_ratio", source):
        targets.append("Risk-reward ratio tracked in signal metadata")

    if targets:
        return "\n".join(f"- {s}" for s in targets)

    return "Not explicitly defined (inherited from base or not present)"


def extract_dynamic_stop(source: str) -> bool:
    """Check if strategy uses dynamic (ATR-based, wall-based, etc.) stops."""
    patterns = [
        r"atr.*stop|stop.*atr",
        r"WALL_PROXIMITY|wall.*stop",
        r"dynamic.*stop|stop.*dynamic",
        r"rolling.*stop|stop.*rolling",
        r"stop.*multiplier|multiplier.*stop",
        r"effective_stop_pct",
        r"TRAIL_STOP_PCT",
        r"_liquidity_aware_stop",
        r"stop\s*=\s*wall_strike",
        r"stop\s*=\s*strike\s*\*",
    ]
    for pat in patterns:
        if re.search(pat, source, re.I):
            return True
    return False


def extract_dynamic_target(source: str) -> bool:
    """Check if strategy uses dynamic (ATR-based, IV-scaled, etc.) targets."""
    patterns = [
        r"atr.*target|target.*atr",
        r"iv.*target|target.*iv",
        r"dynamic.*target|target.*dynamic",
        r"rolling.*target|target.*rolling",
        r"target.*multiplier|multiplier.*target",
        r"TARGET_RISK_MULT",
        r"target\s*=\s*entry\s*\+\s*risk\s*\*",
        r"target\s*=\s*entry\s*\-\s*risk\s*\*",
        r"target_risk_mult",
        r"target_distance",
    ]
    for pat in patterns:
        if re.search(pat, source, re.I):
            return True
    return False


def extract_rr_ratio(source: str) -> Optional[float]:
    """Try to extract a risk-reward ratio from constants or comments."""
    for m in re.finditer(r"(?:RISK_REWARD|RR|TARGET_RISK_MULT|NEGATIVE_GAMMA_TARGET_MULT|POSITIVE_GAMMA_TARGET_MULT|NEUTRAL_GAMMA_TARGET_MULT|TARGET_IV_EXPANSION_MULT|TARGET_IV_EXPANSION_NEG_MULT)\s*=\s*([\d.]+)", source):
        try:
            return float(m.group(1))
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def scan_strategy_files() -> List[Tuple[str, str, str]]:
    """Walk STRATEGIES_DIR and return (layer_key, filepath, filename)."""
    results = []
    for root, dirs, files in os.walk(STRATEGIES_DIR):
        for fname in files:
            if fname == "__init__.py" or not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(root, STRATEGIES_DIR)
            layer_key = rel.split(os.sep)[0] if rel != "." else "util"
            results.append((layer_key, fpath, fname))
    return results


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_strategy(filepath: str) -> Dict[str, Any]:
    """Analyze a single strategy file."""
    source = read_file(filepath)
    fname = os.path.basename(filepath)

    strategy_id = get_class_attr(source, "strategy_id") or fname.replace(".py", "")
    layer = get_class_attr(source, "layer")
    module_doc = get_module_docstring(source)
    constants = get_top_level_constants(source)

    entry = extract_entry(source, fname)
    stop = extract_stop(source, constants)
    target = extract_target(source, constants)
    dynamic_stop = extract_dynamic_stop(source)
    dynamic_target = extract_dynamic_target(source)
    rr = extract_rr_ratio(source)

    return {
        "strategy_id": strategy_id,
        "layer": layer,
        "module_doc": module_doc,
        "entry": entry,
        "stop": stop,
        "target": target,
        "dynamic_stop": dynamic_stop,
        "dynamic_target": dynamic_target,
        "rr_ratio": rr,
        "filename": fname,
    }


def analyze_util_module(filepath: str, fname: str) -> Dict[str, str]:
    """Analyze a utility module."""
    source = read_file(filepath)
    module_doc = get_module_docstring(source)

    util_descriptions = {
        "engine": "Strategy orchestrator — manages strategy lifecycle, delegates to strategy subclasses",
        "signal": "Signal dataclass definition — Direction enum and Signal dataclass for strategy outputs",
        "rolling_keys": "Rolling window key constants — standardized keys for price, volume, ATR, etc.",
        "rolling_window": "RollingWindow data structure — maintains sliding windows of numeric data with stats",
        "analyzer": "Analysis utilities — helper functions for data analysis and metric computation",
        "signal_tracker": "Signal tracking — manages signal history and state across evaluation cycles",
        "volume_filter": "Volume filtering — filters signals based on volume thresholds and patterns",
        "metrics": "Metrics collection — aggregates and reports performance metrics",
        "collector": "Metrics collector — specialized metrics aggregation and reporting",
    }
    base = fname.replace(".py", "")
    desc = util_descriptions.get(base, "Utility module")
    return {"filename": fname, "description": desc}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(analysis: List[Dict], util_analysis: List[Dict]) -> str:
    """Generate the full markdown report."""
    today = date.today().strftime("%Y-%m-%d")
    total = len(analysis)

    # Group by layer
    by_layer: Dict[str, List[Dict]] = defaultdict(list)
    for item in analysis:
        layer_key = item.get("layer", "unknown")
        by_layer[layer_key].append(item)

    # Compute summary stats
    layer_stats = {}
    for layer_key, items in by_layer.items():
        dynamic_stops = sum(1 for i in items if i["dynamic_stop"])
        rr_ratios = [i["rr_ratio"] for i in items if i["rr_ratio"] is not None]
        avg_rr = sum(rr_ratios) / len(rr_ratios) if rr_ratios else None
        layer_stats[layer_key] = {
            "count": len(items),
            "dynamic_stops": dynamic_stops,
            "avg_rr": avg_rr,
        }

    lines = []
    lines.append("# Syngex Strategy PNL Calculator Analysis")
    lines.append(f"**Date:** {today}")
    lines.append(f"**Total Strategies Analyzed:** {total}")
    lines.append("")

    # Summary table
    lines.append("## Summary by Layer")
    lines.append("| Layer | Count | Avg Stop% | Avg Target RR | Dynamic Stops |")
    lines.append("|-------|-------|-----------|---------------|---------------|")

    for key in ["layer1", "layer2", "layer3", "full_data"]:
        stats = layer_stats.get(key, {"count": 0, "avg_rr": None, "dynamic_stops": 0})
        avg_rr_str = f"{stats['avg_rr']:.2f}" if stats["avg_rr"] else "N/A"
        lines.append(
            f"| {LAYER_DISPLAY.get(key, key)} | {stats['count']} | "
            f"~0.5% | {avg_rr_str} | {stats['dynamic_stops']} |"
        )

    lines.append("")

    # Detailed sections per layer
    for layer_key in ["layer1", "layer2", "layer3", "full_data"]:
        items = by_layer.get(layer_key, [])
        if not items:
            continue

        display_name = LAYER_DISPLAY.get(layer_key, layer_key)
        lines.append(f"## {display_name} Strategies")
        lines.append("")

        for item in items:
            strategy_id = item["strategy_id"]
            fname = item["filename"]
            module_doc = item["module_doc"]

            lines.append(f"### {strategy_id} (`{fname}`)")
            if module_doc:
                # Truncate long descriptions
                desc = module_doc.split("\n")[0]
                if len(desc) > 120:
                    desc = desc[:117] + "..."
                lines.append(f"> {desc}")
                lines.append("")

            lines.append(f"- **Entry Price:** {item['entry']}")
            lines.append(f"- **Target Price:** {item['target']}")
            lines.append(f"- **Stop Loss:** {item['stop']}")
            lines.append("")

    # Utility modules
    if util_analysis:
        lines.append("## Infrastructure / Utility Modules")
        lines.append("")
        lines.append("These modules do not calculate prices directly:")
        lines.append("")
        for u in sorted(util_analysis, key=lambda x: x["filename"]):
            lines.append(f"- **{u['filename']}**: {u['description']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Scanning strategies directory: {STRATEGIES_DIR}")

    if not STRATEGIES_DIR.exists():
        print(f"ERROR: Directory not found: {STRATEGIES_DIR}")
        return

    files = scan_strategy_files()
    print(f"Found {len(files)} files")

    analysis = []
    util_analysis = []

    for layer_key, filepath, fname in files:
        if layer_key == "util":
            result = analyze_util_module(filepath, fname)
            util_analysis.append(result)
        else:
            result = analyze_strategy(filepath)
            analysis.append(result)

    print(f"Analyzed {len(analysis)} strategies, {len(util_analysis)} utility modules")

    report = generate_report(analysis, util_analysis)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)

    print(f"\nReport written to: {OUTPUT_FILE}")
    print(f"Report size: {len(report)} characters, {len(report.splitlines())} lines")


if __name__ == "__main__":
    main()
