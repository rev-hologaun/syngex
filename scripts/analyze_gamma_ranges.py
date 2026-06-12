#!/usr/bin/env python3
"""
Scan syngex data directories for gamma/net_gamma values and compute
descriptive statistics per symbol.

Sources:
  - ~/projects/syngex/data/gex_state_*.json   (one JSON per symbol snapshot,
    contains BOTH net_gamma and net_gamma_normalized)
  - ~/projects/syngex/log/*.jsonl              (time-series readings,
    metadata.net_gamma per line; symbol at top level)

Output: clean tabular stats per symbol with raw net_gamma analysis,
        percentile-based threshold recommendations, and normalization
        factor estimates.
"""

import glob
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path.home() / "projects" / "syngex" / "data"
LOG_DIR  = Path.home() / "projects" / "syngex" / "log"

# Candidate thresholds to count readings above/below
THRESHOLDS = [100, 200, 300, 500, 1000, 2000, 5000, 10000]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def percentile(sorted_vals, p):
    """Compute the p-th percentile (0-100) via linear interpolation."""
    if not sorted_vals:
        return 0
    n = len(sorted_vals)
    k = (p / 100.0) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1


def fmt(v, decimals=2):
    if v is None:
        return "N/A"
    if abs(v) >= 1e6:
        return f"{v:,.0f}"
    if abs(v) >= 1e4:
        return f"{v:,.{decimals}f}"
    return f"{v:,.{decimals}f}"


def fmt_pct(v):
    if v is None:
        return "N/A"
    return f"{v * 100:.1f}%"


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------
def collect_from_gex_state_files():
    """Read gex_state_*.json files — one snapshot per symbol.

    Returns:
        dict  symbol -> list of dicts with 'net_gamma' and 'net_gamma_normalized'
    """
    results = {}
    pattern = str(DATA_DIR / "gex_state_*.json")
    files = sorted(glob.glob(pattern))
    for fpath in files:
        try:
            with open(fpath) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        symbol = data.get("symbol")
        if not symbol:
            continue
        ng = data.get("net_gamma")
        ngn = data.get("net_gamma_normalized")
        if ng is None and ngn is None:
            continue
        results.setdefault(symbol, []).append(
            {"net_gamma": ng, "net_gamma_normalized": ngn}
        )
    return results


def collect_from_log_files():
    """Scan log/*.jsonl files for metadata.net_gamma values.

    Each line is a JSON object with:
      - top-level 'symbol' (e.g. "AAPL")
      - 'metadata.net_gamma' (raw gamma reading)

    Returns:
        dict  symbol -> list of float (net_gamma values)
    """
    results = defaultdict(list)
    jsonl_patterns = [
        str(LOG_DIR / "*.jsonl"),
    ]
    for pattern in jsonl_patterns:
        for fpath in sorted(glob.glob(pattern)):
            try:
                with open(fpath) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        # Extract symbol from top level
                        symbol = data.get("symbol")
                        if not symbol:
                            continue

                        # Extract net_gamma from metadata
                        metadata = data.get("metadata")
                        if not isinstance(metadata, dict):
                            continue
                        ng = metadata.get("net_gamma")
                        if ng is None:
                            continue

                        # Skip non-numeric / sentinel values
                        try:
                            ng = float(ng)
                        except (TypeError, ValueError):
                            continue
                        if math.isnan(ng) or math.isinf(ng):
                            continue

                        results[symbol].append(ng)
            except OSError:
                continue

    return dict(results)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def compute_stats(values):
    """Return dict of stats for a list of numeric values."""
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mean = sum(s) / n
    median = percentile(s, 50)
    stddev = math.sqrt(sum((v - mean) ** 2 for v in s) / n) if n > 1 else 0.0

    pos = sum(1 for v in s if v > 0)
    neg = sum(1 for v in s if v < 0)
    zero = sum(1 for v in s if v == 0)

    above = {t: sum(1 for v in s if v >= t) for t in THRESHOLDS}
    below = {t: sum(1 for v in s if v < t) for t in THRESHOLDS}

    return {
        "count": n,
        "min": s[0],
        "max": s[-1],
        "mean": mean,
        "median": median,
        "stddev": stddev,
        "p25": percentile(s, 25),
        "p50": percentile(s, 50),
        "p75": percentile(s, 75),
        "p90": percentile(s, 90),
        "p95": percentile(s, 95),
        "p99": percentile(s, 99),
        "pos": pos,
        "neg": neg,
        "zero": zero,
        "above": above,
        "below": below,
    }


# ---------------------------------------------------------------------------
# Normalization factor analysis
# ---------------------------------------------------------------------------
def compute_normalization_analysis(gex_data, log_data):
    """Estimate normalization factors and suggest new thresholds.

    Compares gex_state net_gamma (raw, millions) vs net_gamma_normalized
    (hundreds) to derive a per-symbol scaling factor. Then suggests
    new thresholds based on percentile markers.
    """
    analysis = {}
    for symbol in sorted(gex_data):
        snapshots = gex_data[symbol]
        raw_vals = [s["net_gamma"] for s in snapshots if s["net_gamma"] is not None]
        norm_vals = [s["net_gamma_normalized"] for s in snapshots if s["net_gamma_normalized"] is not None]
        if not raw_vals or not norm_vals:
            continue

        # Compute per-snapshot ratio (raw / normalized), skip zero/near-zero
        ratios = []
        for raw, norm in zip(raw_vals, norm_vals):
            if norm != 0:
                ratios.append(abs(raw / norm))

        if not ratios:
            continue

        median_ratio = percentile(sorted(ratios), 50)
        mean_ratio = sum(ratios) / len(ratios)

        # The old "5M threshold" in normalized space:
        # If raw 5,000,000 maps to normalized ~500 (median ratio ~10000),
        # then new threshold in raw space = old_threshold_normalized * median_ratio
        old_threshold_normalized = 500  # the "5M" space reference
        suggested_raw_threshold = old_threshold_normalized * median_ratio

        # Suggested thresholds as percentile markers
        pct_markers = [25, 50, 75, 90, 95, 99]
        pct_suggestions = {}
        for p in pct_markers:
            pct_suggestions[p] = percentile(sorted(ratios), p)

        analysis[symbol] = {
            "median_ratio": median_ratio,
            "mean_ratio": mean_ratio,
            "suggested_raw_threshold": suggested_raw_threshold,
            "ratio_percentiles": pct_suggestions,
            "sample_count": len(ratios),
        }

    return analysis


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_header():
    print()
    print("=" * 140)
    print("  GAMMA RANGE ANALYSIS — Raw net_gamma + gex_state snapshots")
    print("=" * 140)
    print()


def print_gex_state_table(gex_data):
    """Print gex_state snapshot data."""
    print("-" * 140)
    print("  GEX STATE SNAPSHOTS (gex_state_*.json)")
    print("-" * 140)
    print()
    print(f"  {'Symbol':<12} {'Raw net_gamma':>20} {'Normalized':>20} {'Ratio':>15} {'Active Strikes':>16}")
    print(f"  {'-'*12} {'-'*20} {'-'*20} {'-'*15} {'-'*16}")
    for symbol in sorted(gex_data):
        for snap in gex_data[symbol]:
            raw = snap["net_gamma"]
            norm = snap["net_gamma_normalized"]
            ratio = abs(raw / norm) if norm and norm != 0 else None
            strikes = snap.get("active_strikes", "N/A")
            ratio_str = f"{ratio:,.1f}" if ratio else "N/A"
            print(f"  {symbol:<12} {fmt(raw):>20} {fmt(norm):>20} {ratio_str:>15} {str(strikes):>16}")
    print()


def print_jsonl_stats_table(symbol, stats):
    """Print a single symbol's jsonl time-series stats."""
    if not stats:
        return
    print(f"  ┌─ {symbol} ─" + "─" * (len(symbol) + 2))
    print(f"  {'Metric':<28} {'Value':>22}")
    print(f"  {'-'*28} {'-'*22}")

    rows = [
        ("Count", str(stats["count"])),
        ("Min", fmt(stats["min"])),
        ("Max", fmt(stats["max"])),
        ("Mean", fmt(stats["mean"])),
        ("StdDev", fmt(stats["stddev"])),
        ("Median", fmt(stats["median"])),
        ("P25", fmt(stats["p25"])),
        ("P50", fmt(stats["p50"])),
        ("P75", fmt(stats["p75"])),
        ("P90", fmt(stats["p90"])),
        ("P95", fmt(stats["p95"])),
        ("P99", fmt(stats["p99"])),
        ("Positive", fmt_pct(stats["pos"] / stats["count"])),
        ("Negative", fmt_pct(stats["neg"] / stats["count"])),
        ("Zero", str(stats["zero"])),
    ]
    for row in rows:
        print(f"  {row[0]:<28} {row[1]:>22}")

    print(f"  {'─'*28} {'─'*22}")
    print(f"  {'Readings above threshold':<28} {'Count':>22}")
    for t in THRESHOLDS:
        cnt = stats["above"].get(t, 0)
        pct = cnt / stats["count"] * 100 if stats["count"] else 0
        print(f"  {'≥ ' + f'{t:,}':<28} {cnt:>22}  ({pct:.1f}%)")

    print(f"  {'─'*28} {'─'*22}")
    print(f"  {'Readings below threshold':<28} {'Count':>22}")
    for t in THRESHOLDS:
        cnt = stats["below"].get(t, 0)
        pct = cnt / stats["count"] * 100 if stats["count"] else 0
        print(f"  {'< ' + f'{t:,}':<28} {cnt:>22}  ({pct:.1f}%)")

    print("  └" + "─" * (len(symbol) + 2))
    print()


def print_normalization_analysis(norm_analysis):
    """Print normalization factor analysis and threshold recommendations."""
    print("-" * 140)
    print("  NORMALIZATION FACTOR ANALYSIS & THRESHOLD RECOMMENDATIONS")
    print("-" * 140)
    print()
    print("  Reference: old 5M threshold → ~500 in normalized space")
    print("  Formula: suggested_raw_threshold = 500 × median(raw/normalized ratio)")
    print()

    for symbol in sorted(norm_analysis):
        a = norm_analysis[symbol]
        print(f"  ┌─ {symbol} ─" + "─" * (len(symbol) + 2))
        print(f"  {'Metric':<40} {'Value':>20}")
        print(f"  {'-'*40} {'-'*20}")
        print(f"  {'Median raw/normalized ratio':<40} {fmt(a['median_ratio']):>20}")
        print(f"  {'Mean raw/normalized ratio':<40} {fmt(a['mean_ratio']):>20}")
        print(f"  {'Suggested raw threshold (500×median)':<40} {fmt(a['suggested_raw_threshold']):>20}")
        print()
        print(f"  {'Ratio Percentiles':<40} {'Value':>20}")
        for p, v in sorted(a["ratio_percentiles"].items()):
            print(f"  {'P' + str(p):<40} {fmt(v):>20}")
        print(f"  {'─'*40} {'-'*20}")
        print(f"  {'Sample snapshots':<40} {a['sample_count']:>20}")

        # Threshold recommendations
        print()
        print(f"  {'Threshold Recommendations':<40}")
        print(f"  {'─'*40}")
        print(f"  {'Floor (P25)':<40} Use values below {fmt(a['ratio_percentiles'][25])} with caution")
        print(f"  {'Normal range (P25-P75)':<40} {fmt(a['ratio_percentiles'][25])} – {fmt(a['ratio_percentiles'][75])}")
        print(f"  {'Ceiling (P90)':<40} Flag values above {fmt(a['ratio_percentiles'][90])}")
        print(f"  {'Extreme (P99)':<40} Investigate values above {fmt(a['ratio_percentiles'][99])}")
        print("  └" + "─" * (len(symbol) + 2))
        print()


def print_summary(log_data, gex_data):
    print("=" * 140)
    all_symbols = sorted(set(list(log_data.keys()) + list(gex_data.keys())))
    print(f"  TOTAL UNIQUE SYMBOLS: {len(all_symbols)}")
    print(f"  JSONL readings total: {sum(len(v) for v in log_data.values()):,}")
    print(f"  Gex state snapshots:  {sum(len(v) for v in gex_data.values()):,}")
    print("=" * 140)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print_header()

    # Collect from gex_state files
    gex_data = collect_from_gex_state_files()
    print(f"  Found {len(gex_data)} symbols in gex_state_*.json files:")
    for sym in sorted(gex_data):
        print(f"    - {sym} ({len(gex_data[sym])} snapshot(s))")
    print()

    # Collect from log files
    log_data = collect_from_log_files()
    print(f"  Found {len(log_data)} symbols in log/*.jsonl files:")
    for sym in sorted(log_data):
        print(f"    - {sym} ({len(log_data[sym]):,} reading(s))")
    print()

    # ---- Section 1: Gex state snapshots ----
    print_gex_state_table(gex_data)

    # ---- Section 2: JSONL time-series stats (raw net_gamma) ----
    print("-" * 140)
    print("  PER-SYMBOL JSONL TIME-SERIES STATISTICS (metadata.net_gamma)")
    print("-" * 140)
    print()

    for symbol in sorted(log_data):
        stats = compute_stats(log_data[symbol])
        print_jsonl_stats_table(symbol, stats)

    # ---- Section 3: Normalization analysis ----
    norm_analysis = compute_normalization_analysis(gex_data, log_data)
    if norm_analysis:
        print_normalization_analysis(norm_analysis)
    else:
        print("  No normalization data available (need gex_state snapshots with both fields).")
        print()

    # ---- Summary ----
    print_summary(log_data, gex_data)


if __name__ == "__main__":
    main()
