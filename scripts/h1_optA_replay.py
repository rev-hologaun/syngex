#!/usr/bin/env python3
"""
H1 Option-A replay: estimate signal-count deltas for gamma_wall_bounce if the
absolute wall-GEX threshold (500k) is replaced with a per-symbol RANK gate.

Method (honest, given no raw-feeder capture is persisted):
- Ground truth baseline: per-signal `metadata.wall_gex` currently logged by
  gamma_wall_bounce (what actually fired under the broken absolute threshold).
- Book context: gex_state_<SYMBOL>.json snapshots give the per-strike |gex|
  ladder at a point in time. We derive the percentile rank each fired wall_gex
  would occupy within its symbol's book, for a given rank gate (top quartile,
  top decile, top 5%).
- "Kept" = fired signal whose |wall_gex| >= the book percentile cutoff for
  that symbol. "Dropped" = below cutoff (would be gated out by Option A).

This models the SELECTIVE effect of the rank gate, not full temporal replay.
Caveat documented in output.
"""
import json, glob, statistics, sys
from collections import defaultdict

def load_book_gex(symbol, path_prefix="data"):
    """Load per-strike |gex| ladder from a gex_state snapshot.
    gex = per-strike net_gamma (normalized, OI-weighted) * 100 * price.
    """
    try:
        d = json.load(open(f"{path_prefix}/gex_state_{symbol}.json"))
    except Exception as e:
        return None, e
    st = d.get("strikes", {})
    price = d.get("underlying_price", 0)
    vals = []
    for k, v in st.items():
        ng = v.get("net_gamma", 0.0)
        g = abs(ng) * 100 * price
        if g > 0:
            vals.append(g)
    return sorted(vals), None

def percentile_cutoff(sorted_abs_gex, rank_keep_frac):
    """Return the |gex| value above which we keep the top ~(rank_keep_frac) of
    the book. rank_keep_frac=0.25 -> top quartile kept."""
    if not sorted_abs_gex:
        return 0.0
    # keep top `rank_keep_frac` -> index at (1 - rank_keep_frac) position
    idx = int(len(sorted_abs_gex) * (1.0 - rank_keep_frac))
    idx = min(idx, len(sorted_abs_gex) - 1)
    return sorted_abs_gex[idx]

def main():
    # Per-signal wall_gex, grouped by symbol
    per_sym = defaultdict(list)
    for f in glob.glob("log/signals_*.jsonl"):
        for line in open(f):
            if "gamma_wall_bounce" not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("strategy_id") != "gamma_wall_bounce":
                continue
            wg = d.get("metadata", {}).get("wall_gex")
            if wg is not None:
                per_sym[d.get("symbol", "?")].append(abs(wg))

    print("=" * 74)
    print("H1 Option-A replay — gamma_wall_bounce (500k -> rank gate)")
    print("=" * 74)
    print("Modeled rank gates: keep top 25% / 10% / 5% of the symbol's |gex| book")
    print("(book distribution from latest gex_state snapshot per symbol)\n")
    print(f"{'sym':5} {'fired':>7} | " + " | ".join(
        f"keep {p*100:.0f}%: kept/dropped (kept%)" for p in (0.25, 0.10, 0.05)
    ))
    print("-" * 74)

    for sym in sorted(per_sym):
        vals = sorted(per_sym[sym])
        n = len(vals)
        book, err = load_book_gex(sym)
        row = f"{sym:5} {n:>7} | "
        for keep_frac in (0.25, 0.10, 0.05):
            if book is None:
                row += f"  no-snapshot({err})   | "
                continue
            cutoff = percentile_cutoff(book, keep_frac)
            kept = sum(1 for v in vals if v >= cutoff)
            row += f" {kept:>5}/{n-kept:<5} ({100*kept/n:.0f}%) | "
        print(row)

    print("\nNOTE: book = single latest snapshot per symbol (not time-synced with")
    print("each signal). Absorb as directional estimate of gate selectivity, not")
    print("an exact temporal replay. No raw feeder capture is persisted on disk.")
    print("See scripts/h1_optA_replay.py for the model + caveats.")

if __name__ == "__main__":
    main()