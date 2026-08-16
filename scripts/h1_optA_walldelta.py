#!/usr/bin/env python3
"""
H1 Option-A wall-set delta: how many strikes qualify as walls under the current
ABSOLUTE thresholds vs the proposed RANK gate, per symbol.

Uses the gex_state_<SYMBOL>.json ladder snapshots (the actual per-strike |gex|
values in production). For each strategy's current absolute threshold (its
MIN_WALL_GEX / MIN_NET_GAMMA / min_gamma_wall_gex constant), we count:
  - abs_fire: strikes passing the absolute threshold today
  - rank_fire@keep: strikes passing the rank gate (keep top X% of book)
And the wall-set delta (rank vs abs) — the real behavioral change Option A makes.

This is a wall-SET comparison (the layer H1 touches), not a full temporal
signal replay (no raw feeder capture is persisted). Directional + grounded.
"""
import json, sys, glob
from collections import defaultdict

# (display, current absolute threshold) per wall-family strategy
STRATEGY_GATES = [
    ("gamma_squeeze",           100),
    ("iron_anchor",             10),
    ("theta_burn",              5000),
    ("extrinsic_intrinsic_flow",5000),
    ("gamma_volume_convergence",500000),
    ("gamma_wall_bounce",       500000),
    ("delta_gamma_squeeze",     500000),
]

# Snapshots with representative message counts (skip the 74-msg AMD fresh start)
def load_books():
    from_ = {}
    for sym in ["TSLA", "SPY", "NVDA", "INTC", "AMD"]:
        try:
            d = json.load(open(f"data/gex_state_{sym}.json"))
        except Exception:
            continue
        msgs = d.get("total_messages", 0)
        st = d.get("strikes", {})
        price = d.get("underlying_price", 0)
        vals = sorted(abs(v.get("net_gamma", 0)) * 100 * price
                      for v in st.values() if v.get("net_gamma"))
        from_[sym] = {"msgs": msgs, "vals": vals}
    return from_

def rank_cutoff(vals, keep_frac):
    if not vals:
        return 0.0
    if keep_frac >= 1.0:
        return 0.0
    idx = int(len(vals) * (1.0 - keep_frac))
    idx = min(idx, len(vals) - 1)
    return vals[idx]

def main():
    books = load_books()
    print("=" * 100)
    print("H1 Option-A: WALL-SET delta — absolute threshold vs rank gate (per symbol book)")
    print("=" * 100)
    print(f"{'strategy':24} {'sym':5} {'strikes':>7} {'msgs':>9} | "
          f"{'abs@thr':>8} {'rank25%':>7} {'rank10%':>7} {'rank5%':>6}  | {'.25Δ':>6} {'.10Δ':>6} {'.05Δ':>6}")
    print("-" * 100)
    for name, thr in STRATEGY_GATES:
        for sym, b in books.items():
            vals = b["vals"]
            if not vals:
                continue
            n = len(vals)
            abs_fire = sum(1 for v in vals if v >= thr)
            r = {}
            for keep in (0.25, 0.10, 0.05):
                c = rank_cutoff(vals, keep)
                r[keep] = sum(1 for v in vals if v >= c)
            d = lambda keep: r[keep] - abs_fire
            # flag unrepresentative snapshot (tiny msg count)
            rep = "" if b["msgs"] > 1000 else " (stale snapshot)"
            print(f"{name:24} {sym:<5} {n:>7} {b['msgs']:>9} | "
                  f"{abs_fire:>8} {r[0.25]:>7} {r[0.10]:>7} {r[0.05]:>6}  | "
                  f"{d(0.25):>+6} {d(0.10):>+6} {d(0.05):>+6}{rep}")
    print("\nΔ = (rank-fire − abs-fire) strikes. Negative = Option-A drops strikes the")
    print("absolute gate was passing (noise filtering). Positive = Option-A adds strikes")
    print("the absolute gate was missing (currently dead on that symbol).")

if __name__ == "__main__":
    main()