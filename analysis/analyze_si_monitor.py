#!/usr/bin/env python3
"""Analyze SI monitor log data and produce a markdown report."""

import json
import math
import os
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "si_monitor.jsonl")
REPORT_DIR = os.path.join(PROJECT_ROOT, "analysis")
REPORT_FILE = os.path.join(REPORT_DIR, "si_monitor_report.md")


def percentile(data, p):
    """Compute the p-th percentile of a sorted list of numbers."""
    s = sorted(data)
    n = len(s)
    if n == 0:
        return 0.0
    if n == 1:
        return s[0]
    k = (n - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def load_records():
    """Load and parse JSONL records. Exit gracefully if file missing."""
    if not os.path.exists(LOG_FILE):
        print(f"SI monitor log not found at: {LOG_FILE}")
        print("Run the SI monitor first to generate data, then re-run this script.")
        sys.exit(0)

    records = []
    with open(LOG_FILE, "r") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                ts = rec["timestamp"]
                if isinstance(ts, (int, float)):
                    rec["_ts"] = datetime.fromtimestamp(ts)
                else:
                    rec["_ts"] = datetime.fromisoformat(str(ts))
                # Skip old raw-input records that don't have SI scores
                if "si_score" not in rec:
                    continue
                records.append(rec)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: skipping malformed line {line_no}: {e}")
    return records


def fmt(val, decimals=4):
    return f"{val:.{decimals}f}"


def data_quality_audit(records):
    """Analyze data quality and return a markdown report section."""
    lines = []
    n = len(records)
    if n == 0:
        lines.append("## F. Data Quality Audit\n")
        lines.append("No records to audit.\n")
        return "\n".join(lines)

    # --- Flatline Detection ---
    lines.append("## F. Data Quality Audit\n")
    lines.append("### Flatline Detection\n")

    momentum_flat = sum(1 for r in records if r.get("momentum") == 0.01)
    liquidity_flat = sum(1 for r in records if r.get("liquidity") == 0.01)
    both_flat = sum(1 for r in records if r.get("momentum") == 0.01 and r.get("liquidity") == 0.01)

    lines.append(f"- **Momentum flatlined (0.01):** {momentum_flat}/{n} ({momentum_flat/n*100:.1f}%)")
    lines.append(f"- **Liquidity flatlined (0.01):** {liquidity_flat}/{n} ({liquidity_flat/n*100:.1f}%)")
    lines.append(f"- **Both flatlined:** {both_flat}/{n} ({both_flat/n*100:.1f}%)")

    # --- Symbol Coverage ---
    lines.append("\n### Symbol Coverage\n")
    symbol_groups = defaultdict(list)
    for r in records:
        sym = r.get("symbol", r.get("Symbol", "UNKNOWN"))
        symbol_groups[sym].append(r)

    lines.append("| Symbol | Records | Flatline % | Mean SI |")
    lines.append("| --- | --- | --- | --- |")
    for sym in sorted(symbol_groups.keys()):
        group = symbol_groups[sym]
        gn = len(group)
        g_flat = sum(1 for r in group if r.get("momentum") == 0.01 and r.get("liquidity") == 0.01)
        g_mean = statistics.mean([r["si_score"] for r in group])
        lines.append(f"| {sym} | {gn} | {g_flat/gn*100:.1f}% | {fmt(g_mean)} |")

    # --- Field Analysis ---
    lines.append("\n### Field Analysis\n")
    numeric_fields = ["net_gamma", "delta_density", "distance_to_wall_pct", "wall_depth", "book_depth", "volume_zscore"]

    lines.append("| Field | Non-null % | Zero % | Mean |")
    lines.append("| --- | --- | --- | --- |")
    for field in numeric_fields:
        vals = [r.get(field) for r in records]
        non_null = [v for v in vals if v is not None]
        null_count = n - len(non_null)
        zero_count = sum(1 for v in non_null if v == 0)
        mean_val = statistics.mean(non_null) if non_null else None
        nn_pct = len(non_null) / n * 100
        zero_pct = zero_count / n * 100
        mean_str = fmt(mean_val) if mean_val is not None else "N/A"
        lines.append(f"| {field} | {nn_pct:.1f}% | {zero_pct:.1f}% | {mean_str} |")

    # --- Regime Distribution ---
    lines.append("\n### Regime Distribution\n")
    regime_counts = defaultdict(int)
    for r in records:
        regime_counts[r.get("regime", "UNKNOWN")] += 1

    lines.append("| Regime | Count | % |")
    lines.append("| --- | --- | --- |")
    for regime in sorted(regime_counts.keys()):
        cnt = regime_counts[regime]
        lines.append(f"| {regime} | {cnt} | {cnt/n*100:.1f}% |")

    # --- Signal Direction Distribution ---
    lines.append("\n### Signal Direction Distribution\n")
    signal_counts = defaultdict(int)
    for r in records:
        sig = r.get("signal_direction", "UNKNOWN")
        signal_counts[sig] += 1

    lines.append("| Signal | Count | % |")
    lines.append("| --- | --- | --- |")
    for sig in sorted(signal_counts.keys()):
        cnt = signal_counts[sig]
        lines.append(f"| {sig} | {cnt} | {cnt/n*100:.1f}% |")

    # --- Time Coverage Gaps ---
    lines.append("\n### Time Coverage Gaps (>5 min)\n")
    sorted_records = sorted(records, key=lambda r: r["_ts"])
    gaps = []
    for i in range(1, len(sorted_records)):
        delta = (sorted_records[i]["_ts"] - sorted_records[i - 1]["_ts"]).total_seconds()
        if delta > 300:  # 5 minutes
            gaps.append((sorted_records[i - 1]["_ts"], sorted_records[i]["_ts"], delta))

    if gaps:
        lines.append(f"**{len(gaps)} gap(s) detected:**\n")
        lines.append("| End of Gap | Start of Gap | Duration |")
        lines.append("| --- | --- | --- |")
        for start, end, delta_s in gaps:
            lines.append(f"| {start.strftime("%H:%M:%S")} | {end.strftime("%H:%M:%S")} | {delta_s/60:.1f} min |")
    else:
        lines.append("No gaps > 5 minutes detected.\n")

    return "\n".join(lines)


def build_report(records):
    lines = []
    lines.append("# SI Monitor Analysis Report\n")
    lines.append(f"*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*\n")

    if not records:
        lines.append("No records found in the log file.\n")
        return "\n".join(lines)

    # --- A. Overview ---
    lines.append("## A. Overview\n")
    lines.append(f"- **Total records:** {len(records)}")
    timestamps = [r["_ts"] for r in records]
    first_ts = min(timestamps)
    last_ts = max(timestamps)
    lines.append(f"- **Date range:** {first_ts.isoformat()} to {last_ts.isoformat()}")

    scores = [r["si_score"] for r in records]
    lines.append(f"\n### SI Score Statistics\n")
    lines.append(f"| Stat | Value |")
    lines.append(f"| --- | --- |")
    lines.append(f"| Mean | {fmt(statistics.mean(scores))} |")
    lines.append(f"| Median | {fmt(statistics.median(scores))} |")
    lines.append(f"| Std | {fmt(statistics.stdev(scores)) if len(scores) > 1 else 'N/A'} |")
    lines.append(f"| Min | {fmt(min(scores))} |")
    lines.append(f"| Max | {fmt(max(scores))} |")
    lines.append(f"| P25 | {fmt(percentile(scores, 25))} |")
    lines.append(f"| P75 | {fmt(percentile(scores, 75))} |")
    lines.append(f"| P90 | {fmt(percentile(scores, 90))} |")
    lines.append(f"| P95 | {fmt(percentile(scores, 95))} |")

    # --- B. Component Breakdown ---
    lines.append("\n## B. Component Breakdown\n")
    components = ["momentum", "liquidity", "regime_coherence"]
    comp_data = {c: [r[c] for r in records] for c in components}

    lines.append("| Component | Mean | Std | Min | Max |")
    lines.append("| --- | --- | --- | --- | --- |")
    for c in components:
        vals = comp_data[c]
        lines.append(
            f"| {c} | {fmt(statistics.mean(vals))} | "
            f"{fmt(statistics.stdev(vals)) if len(vals) > 1 else 'N/A'} | "
            f"{fmt(min(vals))} | {fmt(max(vals))} |"
        )

    weakest = min(components, key=lambda c: statistics.mean(comp_data[c]))
    most_var = max(components, key=lambda c: statistics.stdev(comp_data[c]) if len(comp_data[c]) > 1 else 0)
    lines.append(f"\n- **Weakest component (lowest mean):** {weakest} ({fmt(statistics.mean(comp_data[weakest]))})")
    lines.append(f"- **Most variance (highest std):** {most_var} ({fmt(statistics.stdev(comp_data[most_var]))})")

    # --- C. Threshold Analysis ---
    lines.append("\n## C. Threshold Analysis\n")
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
    lines.append("| Threshold | Records Above | % of Total |")
    lines.append("| --- | --- | --- |")
    threshold_pass = {}
    for t in thresholds:
        above = [r for r in records if r["si_score"] > t]
        pct = len(above) / len(records) * 100
        lines.append(f"| > {t} | {len(above)} | {pct:.1f}% |")
        threshold_pass[t] = above

    lines.append(f"\n### Average Components When SI > 0.7\n")
    lines.append("| Component | Mean |")
    lines.append("| --- | --- |")
    above_7 = threshold_pass.get(0.7, [])
    if above_7:
        for c in components:
            lines.append(f"| {c} | {fmt(statistics.mean([r[c] for r in above_7]))} |")
    else:
        lines.append("| No records with SI > 0.7 |")

    # --- D. Regime Correlation ---
    lines.append("\n## D. Regime Correlation\n")
    regime_groups = defaultdict(list)
    for r in records:
        regime_groups[r.get("regime", "UNKNOWN")].append(r)

    lines.append("| Regime | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean Regime Coherence |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for regime in sorted(regime_groups.keys()):
        group = regime_groups[regime]
        n = len(group)
        lines.append(
            f"| {regime} | {n} | {fmt(statistics.mean([r['si_score'] for r in group]))} | "
            f"{fmt(statistics.mean([r['momentum'] for r in group]))} | "
            f"{fmt(statistics.mean([r['liquidity'] for r in group]))} | "
            f"{fmt(statistics.mean([r['regime_coherence'] for r in group]))} |"
        )

    # --- E. Time Series Summary ---
    lines.append("\n## E. Time Series Summary\n")
    lines.append("### 30-Minute Buckets\n")
    if records:
        bucket_size = timedelta(minutes=30)
        bucket_start = first_ts.replace(minute=(first_ts.minute // 30) * 30, second=0, microsecond=0)
        buckets = defaultdict(list)
        for r in records:
            diff = r["_ts"] - bucket_start
            bucket_idx = int(diff.total_seconds() // bucket_size.total_seconds())
            buckets[bucket_idx].append(r)

        bucket_keys = sorted(buckets.keys())
        lines.append("| Bucket | Mean SI | Records |")
        lines.append("| --- | --- | --- |")
        bucket_means = {}
        for bk in bucket_keys:
            group = buckets[bk]
            mean_si = statistics.mean([r["si_score"] for r in group])
            bucket_means[bk] = mean_si
            bucket_ts = bucket_start + timedelta(minutes=bk * 30)
            lines.append(
                f"| {bucket_ts.strftime("%H:%M")} | {fmt(mean_si)} | {len(group)} |"
            )

        if bucket_means:
            peak_bucket = max(bucket_means, key=bucket_means.get)
            trough_bucket = min(bucket_means, key=bucket_means.get)
            peak_ts = bucket_start + timedelta(minutes=peak_bucket * 30)
            trough_ts = bucket_start + timedelta(minutes=trough_bucket * 30)
            lines.append(f"\n- **Peak SI:** {fmt(bucket_means[peak_bucket])} at {peak_ts.strftime("%H:%M")}")
            lines.append(f"- **Trough SI:** {fmt(bucket_means[trough_bucket])} at {trough_ts.strftime("%H:%M")}")

    # --- F. Data Quality Audit ---
    lines.append("\n" + data_quality_audit(records))

    # --- G. Per-Symbol Deep Dive ---
    lines.append("\n" + per_symbol_deep_dive(records))

    # --- H. Component Correlations & Regime Cross-Tab ---
    lines.append("\n" + correlations_and_regime_analysis(records))

    return "\n".join(lines)


def per_symbol_deep_dive(records):
    """Build section G: Per-Symbol Deep Dive."""
    lines = []
    lines.append("## G. Per-Symbol Deep Dive\n")

    symbol_groups = defaultdict(list)
    for r in records:
        symbol_groups[r.get("symbol", "UNKNOWN")].append(r)

    for symbol in sorted(symbol_groups.keys()):
        group = symbol_groups[symbol]
        lines.append(f"### {symbol}\n")

        # --- Basic info ---
        timestamps = [r["_ts"] for r in group]
        first = min(timestamps)
        last = max(timestamps)
        lines.append(
            f"- **Records:** {len(group)} | **Range:** "
            f"{first.strftime('%Y-%m-%d %H:%M')} to {last.strftime('%Y-%m-%d %H:%M')}"
        )

        # --- SI Score stats ---
        scores = [r["si_score"] for r in group]
        lines.append(
            f"- **SI Score:** mean={fmt(statistics.mean(scores))}, "
            f"median={fmt(statistics.median(scores))}, "
            f"std={fmt(statistics.stdev(scores)) if len(scores) > 1 else 'N/A'}, "
            f"min={fmt(min(scores))}, max={fmt(max(scores))}, "
            f"P25={fmt(percentile(scores, 25))}, P75={fmt(percentile(scores, 75))}, "
            f"P90={fmt(percentile(scores, 90))}, P95={fmt(percentile(scores, 95))}"
        )

        # --- Component breakdown ---
        for comp in ["momentum", "liquidity", "regime_coherence"]:
            vals = [r[comp] for r in group]
            lines.append(
                f"- **{comp}:** mean={fmt(statistics.mean(vals))}, "
                f"median={fmt(statistics.median(vals))}, "
                f"std={fmt(statistics.stdev(vals)) if len(vals) > 1 else 'N/A'}, "
                f"min={fmt(min(vals))}, max={fmt(max(vals))}, "
                f"P25={fmt(percentile(vals, 25))}, P75={fmt(percentile(vals, 75))}, "
                f"P90={fmt(percentile(vals, 90))}, P95={fmt(percentile(vals, 95))}"
            )

        # --- Regime distribution ---
        regime_counts = defaultdict(int)
        for r in group:
            regime_counts[r.get("regime", "OTHER")] += 1
        total = len(group)
        regime_parts = []
        for regime in ["POSITIVE", "NEGATIVE", "OTHER"]:
            cnt = regime_counts.get(regime, 0)
            regime_parts.append(f"{regime} {cnt / total * 100:.0f}%")
        # include any other regimes not in the standard list
        for regime in sorted(regime_counts.keys()):
            if regime not in ("POSITIVE", "NEGATIVE", "OTHER"):
                cnt = regime_counts[regime]
                regime_parts.append(f"{regime} {cnt / total * 100:.0f}%")
        lines.append(f"- **Regime:** {', '.join(regime_parts)}")

        # --- Signal direction ---
        dir_counts = defaultdict(int)
        for r in group:
            direction = r.get("signal_direction", "unknown")
            dir_counts[direction] += 1
        dir_parts = []
        for d in ["long", "short"]:
            cnt = dir_counts.get(d, 0)
            dir_parts.append(f"{d} {cnt / total * 100:.0f}%")
        for d in sorted(dir_counts.keys()):
            if d not in ("long", "short"):
                cnt = dir_counts[d]
                dir_parts.append(f"{d} {cnt / total * 100:.0f}%")
        lines.append(f"- **Direction:** {', '.join(dir_parts)}")

        # --- Time series: 30-minute buckets ---
        lines.append("\n#### Time Series (30-min buckets)\n")
        lines.append("| Bucket | Mean SI | Records |")
        lines.append("| --- | --- | --- |")

        bucket_size = timedelta(minutes=30)
        bucket_start = first.replace(minute=(first.minute // 30) * 30, second=0, microsecond=0)
        buckets = defaultdict(list)
        for r in group:
            diff = r["_ts"] - bucket_start
            bucket_idx = int(diff.total_seconds() // bucket_size.total_seconds())
            buckets[bucket_idx].append(r)

        for bk in sorted(buckets.keys()):
            bgroup = buckets[bk]
            mean_si = statistics.mean([r["si_score"] for r in bgroup])
            bucket_ts = bucket_start + timedelta(minutes=bk * 30)
            lines.append(
                f"| {bucket_ts.strftime('%H:%M')} | {fmt(mean_si)} | {len(bgroup)} |"
            )

        lines.append("")

    return "\n".join(lines)


def pearson(x, y):
    """Compute Pearson correlation coefficient between two lists."""
    n = len(x)
    if n == 0:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def correlations_and_regime_analysis(records):
    """Build section H: Component Correlations & Regime Cross-Tab."""
    lines = []
    lines.append("## H. Component Correlations & Regime Cross-Tab\n")

    n = len(records)
    if n == 0:
        lines.append("No records to analyze.\n")
        return "\n".join(lines)

    # --- Extract fields ---
    si_scores = [r["si_score"] for r in records]
    momentums = [r["momentum"] for r in records]
    liquidities = [r["liquidity"] for r in records]
    coherences = [r["regime_coherence"] for r in records]
    net_gammas = [r.get("net_gamma", 0) or 0 for r in records]
    regimes = [r.get("regime", "UNKNOWN") for r in records]
    directions = [r.get("signal_direction", "unknown") for r in records]

    # --- 1. Correlation Matrix ---
    lines.append("### Correlation Matrix\n")
    lines.append("| Pair | Correlation |")
    lines.append("| --- | --- |")

    pairs = [
        ("si_score vs momentum", si_scores, momentums),
        ("si_score vs liquidity", si_scores, liquidities),
        ("si_score vs regime_coherence", si_scores, coherences),
        ("momentum vs liquidity", momentums, liquidities),
        ("momentum vs regime_coherence", momentums, coherences),
        ("liquidity vs regime_coherence", liquidities, coherences),
    ]
    for label, x, y in pairs:
        r_val = pearson(x, y)
        lines.append(f"| {label} | {fmt(r_val, 4)} |")

    # --- 2. Regime × Direction Cross-Tab ---
    lines.append("\n### Regime × Direction Cross-Tab\n")
    combo_data = defaultdict(list)
    for i in range(n):
        key = (regimes[i], directions[i])
        combo_data[key].append(si_scores[i])

    lines.append("| Regime | Direction | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean RegimeCoherence |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for (regime, direction) in sorted(combo_data.keys()):
        indices = [
            i for i in range(n) if regimes[i] == regime and directions[i] == direction
        ]
        cnt = len(indices)
        mean_si = statistics.mean([si_scores[i] for i in indices])
        mean_mom = statistics.mean([momentums[i] for i in indices])
        mean_liq = statistics.mean([liquidities[i] for i in indices])
        mean_coh = statistics.mean([coherences[i] for i in indices])
        lines.append(
            f"| {regime} | {direction} | {cnt} | "
            f"{fmt(mean_si)} | {fmt(mean_mom)} | {fmt(mean_liq)} | {fmt(mean_coh)} |"
        )

    # --- 3. SI Score Distribution Histogram ---
    lines.append("\n### SI Score Distribution\n")
    bin_edges = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    bin_labels = []
    for i in range(len(bin_edges) - 1):
        bin_labels.append(f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}")
    bin_counts = [0] * len(bin_labels)
    for s in si_scores:
        for i in range(len(bin_labels)):
            if bin_edges[i] <= s < bin_edges[i + 1]:
                bin_counts[i] += 1
                break
        else:
            # Handle edge case: score == 1.0
            bin_counts[-1] += 1

    max_count = max(bin_counts) if bin_counts else 1
    bar_max = 40  # max bar width in chars

    for i, label in enumerate(bin_labels):
        cnt = bin_counts[i]
        pct = cnt / n * 100
        bar_len = int(cnt / max_count * bar_max) if max_count > 0 else 0
        bar = "\u2588" * bar_len
        lines.append(f"| {label} | {cnt:>4} | {pct:>5.1f}% | {bar}")
    lines.append("| --- | --- | --- | --- |")

    # --- 3b. SI Score Distribution (High-Resolution: 0.00–0.10) ---
    lines.append("\n### SI Score Distribution (High-Resolution: 0.00–0.10)\n")
    hr_bins = [
        (0.0100, 0.0120),
        (0.0120, 0.0140),
        (0.0140, 0.0160),
        (0.0160, 0.0180),
        (0.0180, 0.0200),
        (0.0200, 0.0250),
        (0.0250, 0.0300),
        (0.0300, 0.0500),
        (0.0500, 0.1000),
    ]
    hr_labels = [f"{lo:.4f}-{hi:.4f}" for lo, hi in hr_bins]
    hr_counts = [0] * len(hr_labels)
    for s in si_scores:
        for i, (lo, hi) in enumerate(hr_bins):
            if lo <= s < hi:
                hr_counts[i] += 1
                break

    max_hr = max(hr_counts) if hr_counts else 1
    for i, label in enumerate(hr_labels):
        cnt = hr_counts[i]
        pct = cnt / n * 100
        bar_len = int(cnt / max_hr * bar_max) if max_hr > 0 else 0
        bar = "\u2588" * bar_len
        lines.append(f"| {label} | {cnt:>4} | {pct:>5.1f}% | {bar}")
    lines.append("| --- | --- | --- | --- |")

    # --- 3c. Top 20 Lowest SI Scores ---
    lines.append("\n### Top 20 Lowest SI Scores\n")
    sorted_by_si = sorted(records, key=lambda r: r["si_score"])
    top20 = sorted_by_si[:20]

    lines.append("| Timestamp | Symbol | Regime | Direction | SI Score | Momentum | Liquidity | Regime Coherence |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in top20:
        ts = r["_ts"].strftime("%H:%M:%S")
        sym = r.get("symbol", r.get("Symbol", "UNKNOWN"))
        regime = r.get("regime", "UNKNOWN")
        direction = r.get("signal_direction", "unknown")
        score = r["si_score"]
        mom = r.get("momentum", "N/A")
        liq = r.get("liquidity", "N/A")
        coh = r.get("regime_coherence", "N/A")
        mom_str = fmt(mom) if isinstance(mom, (int, float)) else str(mom)
        liq_str = fmt(liq) if isinstance(liq, (int, float)) else str(liq)
        coh_str = fmt(coh) if isinstance(coh, (int, float)) else str(coh)
        lines.append(f"| {ts} | {sym} | {regime} | {direction} | {score:.6f} | {mom_str} | {liq_str} | {coh_str} |")

    lines.append("")

    # --- 4. Net Gamma Distribution ---
    lines.append("\n### Net Gamma Distribution\n")

    def gamma_bin(g):
        if g < 0:
            return "< 0"
        elif g < 1000:
            return "0 – 1K"
        elif g < 10000:
            return "1K – 10K"
        elif g < 100000:
            return "10K – 100K"
        else:
            return "> 100K"

    gamma_bins = defaultdict(list)
    for i in range(n):
        b = gamma_bin(net_gammas[i])
        gamma_bins[b].append(si_scores[i])

    # Ordered display
    bin_order = ["< 0", "0 – 1K", "1K – 10K", "10K – 100K", "> 100K"]

    lines.append("| Net Gamma Bin | Count | Mean SI | % of Total |")
    lines.append("| --- | --- | --- | --- |")
    for label in bin_order:
        vals = gamma_bins.get(label, [])
        cnt = len(vals)
        mean_si = statistics.mean(vals) if vals else 0.0
        pct = cnt / n * 100
        lines.append(f"| {label} | {cnt:>4} | {fmt(mean_si)} | {pct:>5.1f}% |")

    lines.append("")
    return "\n".join(lines)


def main():
    records = load_records()
    report = build_report(records)
    print(report)

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
