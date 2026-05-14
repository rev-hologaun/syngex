import json
import glob
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict

def get_pdt_hour(signal_id):
    try:
        # signal_id format: gex_imbalance_1778069257
        timestamp = float(signal_id.split('_')[-1])
        dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        # Convert UTC to PDT (UTC-7)
        dt_pdt = dt_utc - timedelta(hours=7)
        return dt_pdt.hour, dt_pdt.minute
    except:
        return None, None

def get_time_period(hour, minute):
    time_val = hour * 60 + minute
    orb_start = 9 * 60 + 30
    orb_end = 10 * 60
    early_start = 10 * 60
    early_end = 12 * 60
    mid_start = 12 * 60
    mid_end = 14 * 60
    late_start = 14 * 60
    late_end = 16 * 60

    if orb_start <= time_val < orb_end:
        return "ORB"
    elif early_start <= time_val < early_end:
        return "Early"
    elif mid_start <= time_val < mid_end:
        return "Mid"
    elif late_start <= time_val < late_end:
        return "Late"
    else:
        return "Other"

def analyze():
    files = glob.glob('/home/hologaun/projects/syngex/log/signal_outcomes_*.jsonl')
    all_signals = []

    for f in files:
        symbol = os.path.basename(f).split('_')[-1].replace('.jsonl', '')
        with open(f, 'r') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    data['symbol'] = symbol
                    all_signals.append(data)
                except:
                    continue

    strategies = [
        "confluence_reversal", "gamma_flip_breakout", "gamma_squeeze", 
        "gamma_wall_bounce", "gex_imbalance", "magnet_accelerate", "vol_compression_range"
    ]

    report_path = '/home/hologaun/projects/syngex/analysis/strategy_performance_v3.md'
    
    with open(report_path, 'w') as report:
        report.write("# Syngex Strategy Performance Analysis Report\n\n")
        report.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for strat in strategies:
            strat_signals = [s for s in all_signals if s['strategy_id'] == strat]
            if not strat_signals:
                report.write(f"## Strategy: {strat}\n*No data found for this strategy.*\n\n")
                continue

            report.write(f"## Strategy: {strat}\n\n")

            # 1. Confidence Analysis
            report.write("### 1. Confidence Level Analysis\n")
            conf_buckets = defaultdict(lambda: {"count": 0, "wins": 0, "pnl": 0.0, "pnl_pct": 0.0, "hold_time": 0.0})
            for s in strat_signals:
                c = s['confidence']
                bucket = "Other"
                if 0.3 <= c < 0.4: bucket = "30-39%"
                elif 0.4 <= c < 0.5: bucket = "40-49%"
                elif 0.5 <= c < 0.6: bucket = "50-59%"
                elif 0.6 <= c < 0.7: bucket = "60-69%"
                elif 0.7 <= c < 0.8: bucket = "70-79%"
                elif 0.8 <= c < 0.9: bucket = "80-89%"
                elif c >= 0.9: bucket = "90%+"
                
                if bucket != "Other":
                    conf_buckets[bucket]["count"] += 1
                    is_win = s['outcome'] == "WIN"
                    if is_win: conf_buckets[bucket]["wins"] += 1
                    conf_buckets[bucket]["pnl"] += s['pnl']
                    conf_buckets[bucket]["pnl_pct"] += s['pnl_pct']
                    conf_buckets[bucket]["hold_time"] += s['hold_time']

            report.write("| Bucket | Count | Win Rate | Avg PnL | Avg PnL% | Avg Hold Time |\n")
            report.write("|---|---|---|---|---|---|\n")
            for b in ["30-39%", "40-49%", "50-59%", "60-69%", "70-79%", "80-89%", "90%+"]:
                if conf_buckets[b]["count"] > 0:
                    row = conf_buckets[b]
                    wr = (row["wins"] / row["count"]) * 100
                    avg_pnl = row["pnl"] / row["count"]
                    avg_pnl_pct = (row["pnl_pct"] / row["count"])
                    avg_hold = row["hold_time"] / row["count"]
                    report.write(f"| {b} | {row['count']} | {wr:.2f}% | {avg_pnl:.2f} | {avg_pnl_pct:.2f}% | {avg_hold:.2f} |\n")
            report.write("\n")

            # 2. Market Regime Analysis
            report.write("### 2. Market Regime Analysis\n")
            regime_data = defaultdict(lambda: {"count": 0, "wins": 0, "pnl": 0.0, "pnl_pct": 0.0, "hold_time": 0.0})
            for s in strat_signals:
                meta = s['metadata']
                trend = meta['trend']
                regime_name = meta['regime']
                
                # Volatility proxy: distance to stop relative to entry
                vol_proxy = abs(s['entry'] - s['stop']) / s['entry']
                is_volatile = vol_proxy > 0.01 # Threshold 1%
                
                reg_type = "Sideways"
                if is_volatile:
                    reg_type = "Volatile/Breakout"
                elif trend in ["UP", "DOWN"]:
                    reg_type = "Trending"
                
                key = f"{reg_type} ({regime_name} {trend})"
                regime_data[key]["count"] += 1
                if s['outcome'] == "WIN": regime_data[key]["wins"] += 1
                regime_data[key]["pnl"] += s['pnl']
                regime_data[key]["pnl_pct"] += s['pnl_pct']
                regime_data[key]["hold_time"] += s['hold_time']

            report.write("| Regime | Count | Win Rate | Avg PnL | Avg PnL% | Avg Hold Time |\n")
            report.write("|---|---|---|---|---|---|\n")
            for k, v in regime_data.items():
                wr = (v["wins"] / v["count"]) * 100
                avg_pnl = v["pnl"] / v["count"]
                avg_pnl_pct = (v["pnl_pct"] / v["count"])
                avg_hold = v["hold_time"] / v["count"]
                report.write(f"| {k} | {v['count']} | {wr:.2f}% | {avg_pnl:.2f} | {avg_pnl_pct:.2f}% | {avg_hold:.2f} |\n")
            report.write("\n")

            # 3. Time-of-Day Analysis
            report.write("### 3. Time-of-Day Analysis\n")
            tod_data = defaultdict(lambda: {"count": 0, "wins": 0, "pnl": 0.0, "pnl_pct": 0.0, "hold_time": 0.0})
            for s in strat_signals:
                h, m = get_pdt_hour(s['signal_id'])
                if h is not None:
                    period = get_time_period(h, m)
                    if period != "Other":
                        tod_data[period]["count"] += 1
                        if s['outcome'] == "WIN": tod_data[period]["wins"] += 1
                        tod_data[period]["pnl"] += s['pnl']
                        tod_data[period]["pnl_pct"] += s['pnl_pct']
                        tod_data[period]["hold_time"] += s['hold_time']

            report.write("| Period | Count | Win Rate | Avg PnL | Avg PnL% | Avg Hold Time |\n")
            report.write("|---|---|---|---|---|---|\n")
            for p in ["ORB", "Early", "Mid", "Late"]:
                if tod_data[p]["count"] > 0:
                    row = tod_data[p]
                    wr = (row["wins"] / row["count"]) * 100
                    avg_pnl = row["pnl"] / row["count"]
                    avg_pnl_pct = (row["pnl_pct"] / row["count"])
                    avg_hold = row["hold_time"] / row["count"]
                    report.write(f"| {p} | {row['count']} | {wr:.2f}% | {avg_pnl:.2f} | {avg_pnl_pct:.2f}% | {avg_hold:.2f} |\n")
            report.write("\n")

            # 4. General Insights
            report.write("### 4. General Insights\n")
            total_wins = sum(1 for s in strat_signals if s['outcome'] == "WIN")
            total_count = len(strat_signals)
            overall_wr = (total_wins / total_count) * 100
            
            symbol_performance = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0.0})
            direction_perf = {"LONG": {"wins": 0, "total": 0, "pnl": 0.0}, "SHORT": {"wins": 0, "total": 0, "pnl": 0.0}}
            rr_vals = [s['metadata']['risk_reward_ratio'] for s in strat_signals]
            avg_rr = sum(rr_vals)/len(rr_vals) if rr_vals else 0
            
            win_holds = []
            loss_holds = []

            for s in strat_signals:
                sym = s['symbol']
                symbol_performance[sym]["total"] += 1
                if s['outcome'] == "WIN":
                    symbol_performance[sym]["wins"] += 1
                    symbol_performance[sym]["pnl"] += s['pnl']
                    win_holds.append(s['hold_time'])
                else:
                    symbol_performance[sym]["pnl"] += s['pnl']
                
                direction_perf[s['direction']]["total"] += 1
                if s['outcome'] == "WIN":
                    direction_perf[s['direction']]["wins"] += 1
                    direction_perf[s['direction']]["pnl"] += s['pnl']
                else:
                    direction_perf[s['direction']]["pnl"] += s['pnl']
                
                if s['outcome'] == "WIN": win_holds.append(s['hold_time'])
                else: loss_holds.append(s['hold_time'])

            report.write(f"- **Overall Win Rate:** {overall_wr:.2f}%\n")
            
            best_sym = max(symbol_performance.items(), key=lambda x: (x[1]['wins']/x[1]['total'] if x[1]['total'] > 0 else 0), default=("None", {"wins":0, "total":0, "pnl":0}))
            worst_sym = min(symbol_performance.items(), key=lambda x: (x[1]['wins']/x[1]['total'] if x[1]['total'] > 0 else 0), default=("None", {"wins":0, "total":0, "pnl":0}))
            report.write(f"- **Best Symbol:** {best_sym[0]} ({best_sym[1]['wins']}/{best_sym[1]['total']} wins)\n")
            report.write(f"- **Worst Symbol:** {worst_sym[0]} ({worst_sym[1]['wins']}/{worst_sym[1]['total']} wins)\n")
            
            long_wr = (direction_perf["LONG"]["wins"] / direction_perf["LONG"]["total"] * 100) if direction_perf["LONG"]["total"] > 0 else 0
            short_wr = (direction_perf["SHORT"]["wins"] / direction_perf["SHORT"]["total"] * 100) if direction_perf["SHORT"]["total"] > 0 else 0
            report.write(f"- **Direction Bias:** LONG WR: {long_wr:.2f}%, SHORT WR: {short_wr:.2f}%\n")
            report.write(f"- **Avg Risk-Reward Ratio:** {avg_rr:.2f}\n")
            
            avg_win_hold = sum(win_holds)/len(win_holds) if win_holds else 0
            avg_loss_hold = sum(loss_holds)/len(loss_holds) if loss_holds else 0
            report.write(f"- **Hold Time Analysis:** Avg Win Hold: {avg_win_hold:.2f}m, Avg Loss Hold: {avg_loss_hold:.2f}m\n")
            report.write("\n")

            # 5. Recommendations
            report.write("### 5. Recommendations\n")
            if overall_wr > 55:
                report.write("- **Status:** ✅ KEEP / OPTIMIZE\n")
            elif overall_wr > 45:
                report.write("- **Status:** ⚠️ MODIFY\n")
            else:
                report.write("- **Status:** ❌ DEPRECATE / MAJOR REWORK\n")
            
            best_conf_bucket = None
            max_conf_wr = 0
            for b, row in conf_buckets.items():
                if row["count"] > 5:
                    wr = (row["wins"] / row["count"]) * 100
                    if wr > max_conf_wr:
                        max_conf_wr = wr
                        best_conf_bucket = b
            if best_conf_bucket:
                report.write(f"- **Optimal Confidence Threshold:** {best_conf_bucket} (Win Rate: {max_conf_wr:.2f}%)\n")
            
            report.write("- **Target Market Regime:** Analyze regime tables for highest win rates.\n")
            report.write("- **Best Time Window:** Check Time-of-Day table.\n")
            report.write("- **Actionable Logic Change:** Review low-performing segments for pattern mismatch.\n\n")
            report.write("---\n\n")

    print(f"Analysis complete. Report written to {report_path}")

if __name__ == "__main__":
    analyze()
