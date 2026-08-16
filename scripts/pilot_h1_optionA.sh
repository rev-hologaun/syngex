#!/bin/bash
# ============================================================================
# H1 Option-A pilot harness
# ----------------------------------------------------------------------------
# Runs a controlled A/B comparison for the gamma wall gate change:
#   baseline : no env vars -> legacy absolute MIN_WALL_GEX (500k)
#   pilot    : SYNGEX_WALL_RANK_KEEP_FRAC=<rank> -> Option-A rank gate
#              (top <rank> of the symbol's own |gex| book, scale-invariant)
#
# Each run logs signals to an ISOLATED directory (SYNGEX_LOG_DIR) so pilot
# output never collides with the live log/ dir.
#
#   Ingest streams come from live TradeStation feed. The harness is READY to
#   run once feed is up (feed tails off ~1am, real data at 6:30am open).
#
# Usage:
#   ./scripts/pilot_h1_optionA.sh [SYMBOL] [RANK] [RUNTIME_SEC]
#   e.g. ./scripts/pilot_h1_optionA.sh TSLA 0.25 3600
#
#   SYMBOL      default TSLA
#   RANK        default 0.25   (0.25 = keep top quartile)
#   RUNTIME_SEC default 3600
# ============================================================================
set -u

SYMBOL="${1:-TSLA}"
RANK="${2:-0.25}"
RUNTIME="${3:-3600}"
REPO="/home/hologaun/projects/syngex"
cd "$REPO"

PILOT_LOG_DIR="$REPO/log/pilot_rank${RANK}_${SYMBOL}"
BASELINE_LOG_DIR="$REPO/log/pilot_baseline_${SYMBOL}"

echo "=== H1 Option-A pilot :: $SYMBOL  rank=$RANK  runtime=${RUNTIME}s ==="
echo "baseline log dir : $BASELINE_LOG_DIR"
echo "pilot    log dir : $PILOT_LOG_DIR"

# Sanity: feed must be present before launching (TradeStation SSE).
# The reuse of restart.sh's port scheme (dashboard streams) — we run "stream" mode
# to avoid binding Streamlit dashboards on top of live ones.

# --- baseline process (legacy gate, isolated logs) ---
SYNGEX_LOG_DIR="$BASELINE_LOG_DIR" \
  nohup python3 main.py "$SYMBOL" stream --port 18900 > /tmp/h1_baseline_$SYMBOL.log 2>&1 &
BASE_PID=$!

# --- pilot process (Option-A rank gate, isolated logs) ---
SYNGEX_LOG_DIR="$PILOT_LOG_DIR" SYNGEX_WALL_RANK_KEEP_FRAC="$RANK" \
  nohup python3 main.py "$SYMBOL" stream --port 18901 > /tmp/h1_pilot_$SYMBOL.log 2>&1 &
PILOT_PID=$!

echo "baseline PID=$BASE_PID  pilot PID=$PILOT_PID"
echo "running ${RUNTIME}s... (Ctrl-C kills nothing; use kill \$BASEPID \$PILOTPID)"

sleep "$RUNTIME"

kill "$BASE_PID" "$PILOT_PID" 2>/dev/null
wait 2>/dev/null
sleep 2

# ============================================================================
# Compare gamma_wall_bounce signal counts in baseline vs pilot logs
# ============================================================================
echo
echo "=== Signal counts (whole logged history in each isolated dir) ==="
for d in "$BASELINE_LOG_DIR" "$PILOT_LOG_DIR"; do
  if [ -d "$d" ]; then
    echo ""
    echo "--- $d ---"
    python3 - "$d" <<'PY'
import sys, glob, json, os
from collections import Counter
logdir = sys.argv[1]
# only the current run's file (baseline/pilot dirs are fresh per run)
files = sorted(glob.glob(os.path.join(logdir, "signals_*.jsonl")))
c = Counter()
total = 0
for f in files:
    try:
        for line in open(f):
            try:
                d = json.loads(line)
            except Exception:
                continue
            c[d.get("strategy_id", "?")] += 1
            total += 1
    except FileNotFoundError:
        pass
if total == 0:
    print("  (no signals logged yet — feed may be up but market closed/thin)")
for sid, n in c.most_common():
    print(f"  {sid:<34} {n:>7}")
print(f"  {'TOTAL':<34} {total:>7}")
PY
  else
    echo "--- $d  (no log dir yet) ---"
  fi
done
echo
echo "NOTE: A/B is only meaningful once both processes have ingested the SAME"
echo "live feed window. Compare gamma_wall_bounce counts across the two dirs."