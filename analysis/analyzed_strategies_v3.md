# Strategy Performance Analysis — Round 3 Validation (Regular Hours)

**Date:** 2026-07-21  |  **Generated:** 2026-07-21 01:06 UTC  |  **Total Resolved Signals:** 52,221  |  **Strategies Analyzed:** 22  |  **Confidence ≥ 5%**  |  **Regular Hours**

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 52,221                                                       |
| Total Wins           | 6,363                                                        |
| Total Losses         | 16,378                                                       |
| Time-Expired (CLOSED) | 0                                                            |
| Overall Win Rate     | 28.0%                                                        |
| Total P&L (resolved) | $-10255.76                                                   |
| Avg P&L per Resolved Signal | $-0.45                                                       |
| Symbols Traded       | AMD, INTC, NVDA, SPY, TSLA                                   |

---

## Per-Strategy Deep Dive

### call_put_flow_asymmetry

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 2,020  |  **Win Rate:** 24.0%  |  **Avg P&L (resolved):** $-1.243  |  **Avg P&L (all):** $-1.243  |  **Avg Hold:** 37575s (626.3m)  |  **Median Hold:** 52349s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 84    | 0     | 84     | 0      | 0.0%      | $-2.260  | $-2.260  | -100.0%  |
| 20-29%         | 775   | 98    | 677    | 0      | 12.6%     | $-0.508  | $-0.508  | -62.1%   |
| 30-39%         | 774   | 387   | 387    | 0      | 50.0%     | $-1.015  | $-1.015  | 50.4%    |
| 50-59%         | 387   | 0     | 387    | 0      | 0.0%      | $-2.950  | $-2.950  | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2020  | 485   | 1535   | 0      | 24.0%     | $-1.243  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 858   | 44    | 814    | 0      | 5.1%      | $-3.217  |
| Positive Gamma (Range-Bound friendly) | 1162  | 441   | 721    | 0      | 38.0%     | $0.215   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 288   | 45    | 243    | 0      | 15.6%     | $-0.636  |
| Time Held: 90-240m     | 213   | 27    | 186    | 0      | 12.7%     | $-0.457  |
| Time Held: <30m        | 358   | 26    | 332    | 0      | 7.3%      | $-0.846  |
| Time Held: >480m       | 1161  | 387   | 774    | 0      | 33.3%     | $-1.660  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1192  | 286   | 906    | 0      | 24.0%     | $-1.171  | 🔴          |
| Morning (10:00-12:00)  | 648   | 161   | 487    | 0      | 24.8%     | $-1.322  | 🟢          |
| ORB (9:30-10:00)       | 180   | 38    | 142    | 0      | 21.1%     | $-1.437  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 180    | 0          | 30         | 150        | 0.0%      | 16.7%     | 83.3%     |
| Morning (10:00-12:00)  | 648    | 0          | 119        | 529        | 0.0%      | 18.4%     | 81.6%     |
| Afternoon (12:00-16:00) | 1192   | 0          | 238        | 954        | 0.0%      | 20.0%     | 80.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 30     | 0     | 30     | 0      | 0.0%      | $-2.284      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 60     | 8     | 52     | 0      | 13.3%     | $-0.681      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 60     | 30    | 30     | 0      | 50.0%     | $-1.015      | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 30     | 0     | 30     | 0      | 0.0%      | $-2.950      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 54     | 0     | 54     | 0      | 0.0%      | $-2.247      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 237    | 42    | 195    | 0      | 17.7%     | $-0.601      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 238    | 119   | 119    | 0      | 50.0%     | $-1.015      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 119    | 0     | 119    | 0      | 0.0%      | $-2.950      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 478    | 48    | 430    | 0      | 10.0%     | $-0.440      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 476    | 238   | 238    | 0      | 50.0%     | $-1.015      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 238    | 0     | 238    | 0      | 0.0%      | $-2.950      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1137  | 441   | 696    | 0      | 38.8%     | $0.269   |
| SHORT        | 883   | 44    | 839    | 0      | 5.0%      | $-3.190  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 36    | 5     | 31     | 0      | 13.9%     | $-0.770  |
| Long (30-60 min)       | 171   | 28    | 143    | 0      | 16.4%     | $-0.714  |
| Medium (5-15 min)      | 122   | 10    | 112    | 0      | 8.2%      | $-0.762  |
| Slow (15-30 min)       | 196   | 11    | 185    | 0      | 5.6%      | $-0.908  |
| Very Fast (<1 min)     | 4     | 0     | 4      | 0      | 0.0%      | $-1.022  |
| Very Long (>1h)        | 1491  | 431   | 1060   | 0      | 28.9%     | $-1.399  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.24 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-1.24) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $-0.46) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Morning (10:00-12:00) (24.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (37575s / 626.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### confluence_reversal

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,768  |  **Win Rate:** 25.3%  |  **Avg P&L (resolved):** $-0.742  |  **Avg P&L (all):** $-0.742  |  **Avg Hold:** 7039s (117.3m)  |  **Median Hold:** 4065s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 58    | 20    | 38     | 0      | 34.5%     | $0.440   | $0.440   | 3.3%     |
| 10-19%         | 388   | 105   | 283    | 0      | 27.1%     | $-0.034  | $-0.034  | -18.9%   |
| 20-29%         | 591   | 150   | 441    | 0      | 25.4%     | $-1.371  | $-1.371  | -24.2%   |
| 30-39%         | 362   | 103   | 259    | 0      | 28.5%     | $-0.815  | $-0.815  | -14.6%   |
| 40-49%         | 227   | 53    | 174    | 0      | 23.3%     | $-0.188  | $-0.188  | -30.0%   |
| 50-59%         | 123   | 14    | 109    | 0      | 11.4%     | $-1.145  | $-1.145  | -65.9%   |
| 60-69%         | 19    | 2     | 17     | 0      | 10.5%     | $-1.882  | $-1.882  | -68.4%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1081  | 294   | 787    | 0      | 27.2%     | $-0.510  |
| Trending (Up)        | 687   | 153   | 534    | 0      | 22.3%     | $-1.108  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 258   | 84    | 174    | 0      | 32.6%     | $0.499   |
| Positive Gamma (Range-Bound friendly) | 1510  | 363   | 1147   | 0      | 24.0%     | $-0.955  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 300   | 127   | 173    | 0      | 42.3%     | $-0.622  |
| Time Held: 30-90m      | 489   | 117   | 372    | 0      | 23.9%     | $-1.021  |
| Time Held: 90-240m     | 439   | 116   | 323    | 0      | 26.4%     | $0.313   |
| Time Held: <30m        | 536   | 83    | 453    | 0      | 15.5%     | $-1.447  |
| Time Held: >480m       | 4     | 4     | 0      | 0      | 100.0%    | $2.960   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 883   | 223   | 660    | 0      | 25.3%     | $-0.526  | 🔴          |
| Morning (10:00-12:00)  | 666   | 160   | 506    | 0      | 24.0%     | $-1.310  | 🔴          |
| ORB (9:30-10:00)       | 219   | 64    | 155    | 0      | 29.2%     | $0.109   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 219    | 0          | 34         | 185        | 0.0%      | 15.5%     | 84.5%     |
| Morning (10:00-12:00)  | 666    | 0          | 65         | 601        | 0.0%      | 9.8%      | 90.2%     |
| Afternoon (12:00-16:00) | 883    | 0          | 43         | 840        | 0.0%      | 4.9%      | 95.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 3      | 1     | 2      | 0      | 33.3%     | $0.043       | ⚠️         |
| ORB (9:30-10:00)       | 10-19%     | 39     | 5     | 34     | 0      | 12.8%     | $-0.998      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 69     | 30    | 39     | 0      | 43.5%     | $2.247       | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 41     | 19    | 22     | 0      | 46.3%     | $2.739       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 33     | 7     | 26     | 0      | 21.2%     | $-1.730      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 28     | 2     | 26     | 0      | 7.1%      | $-4.343      | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 6      | 0     | 6      | 0      | 0.0%      | $-4.308      | ⚠️         |
| Morning (10:00-12:00)  | 5-9%       | 15     | 7     | 8      | 0      | 46.7%     | $1.682       | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 131    | 39    | 92     | 0      | 29.8%     | $0.091       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 256    | 77    | 179    | 0      | 30.1%     | $-1.535      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 126    | 32    | 94     | 0      | 25.4%     | $-1.989      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 73     | 5     | 68     | 0      | 6.8%      | $-1.878      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 57     | 0     | 57     | 0      | 0.0%      | $-1.960      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 8      | 0     | 8      | 0      | 0.0%      | $-2.130      | ⚠️         |
| Afternoon (12:00-16:00) | 5-9%       | 40     | 12    | 28     | 0      | 30.0%     | $0.005       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 218    | 61    | 157    | 0      | 28.0%     | $0.063       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 266    | 43    | 223    | 0      | 16.2%     | $-2.153      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 195    | 52    | 143    | 0      | 26.7%     | $-0.804      | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 121    | 41    | 80     | 0      | 33.9%     | $1.252       | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 38     | 12    | 26     | 0      | 31.6%     | $2.436       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 5      | 2     | 3      | 0      | 40.0%     | $1.426       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1205  | 107   | 1098   | 0      | 8.9%      | $-2.839  |
| SHORT        | 563   | 340   | 223    | 0      | 60.4%     | $3.745   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 82    | 12    | 70     | 0      | 14.6%     | $-0.725  |
| Long (30-60 min)       | 294   | 59    | 235    | 0      | 20.1%     | $-1.991  |
| Medium (5-15 min)      | 192   | 26    | 166    | 0      | 13.5%     | $-1.482  |
| Slow (15-30 min)       | 235   | 41    | 194    | 0      | 17.4%     | $-1.759  |
| Very Fast (<1 min)     | 27    | 4     | 23     | 0      | 14.8%     | $-0.674  |
| Very Long (>1h)        | 938   | 305   | 633    | 0      | 32.5%     | $0.052   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.74 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 5-9% confidence (34.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (10.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.51) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.31) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (29.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (7039s / 117.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_gamma_squeeze

**Symbols:** TSLA  |  **Total Signals:** 6  |  **Win Rate:** 16.7%  |  **Avg P&L (resolved):** $-1.497  |  **Avg P&L (all):** $-1.497  |  **Avg Hold:** 8120s (135.3m)  |  **Median Hold:** 7909s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 6     | 1     | 5      | 0      | 16.7%     | $-1.497  | $-1.497  | -50.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 6     | 1     | 5      | 0      | 16.7%     | $-1.497  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 6     | 1     | 5      | 0      | 16.7%     | $-1.497  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1     | 1     | 0      | 0      | 100.0%    | $5.980   |
| Time Held: 30-90m      | 2     | 0     | 2      | 0      | 0.0%      | $-2.990  |
| Time Held: 90-240m     | 3     | 0     | 3      | 0      | 0.0%      | $-2.993  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Morning (10:00-12:00)  | 6     | 1     | 5      | 0      | 16.7%     | $-1.497  | ⚠️         |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 6      | 0          | 0          | 6          | 0.0%      | 0.0%      | 100.0%    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3     | 0     | 3      | 0      | 0.0%      | $-2.993  |
| SHORT        | 3     | 1     | 2      | 0      | 33.3%     | $0.000   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Long (30-60 min)       | 2     | 0     | 2      | 0      | 0.0%      | $-2.990  |
| Very Long (>1h)        | 4     | 1     | 3      | 0      | 25.0%     | $-0.750  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 16.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.50 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (16.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (16.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-1.50) — this strategy thrives in sideways conditions.
- ⚠️ Best signal generation window: Morning (10:00-12:00) (16.7% win rate) — but only 6 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (8120s / 135.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_volume_exhaustion

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,686  |  **Win Rate:** 34.0%  |  **Avg P&L (resolved):** $-0.358  |  **Avg P&L (all):** $-0.358  |  **Avg Hold:** 9430s (157.2m)  |  **Median Hold:** 8562s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 248   | 68    | 180    | 0      | 27.4%     | $-1.161  | $-1.161  | -31.5%   |
| 10-19%         | 841   | 248   | 593    | 0      | 29.5%     | $-0.833  | $-0.833  | -26.3%   |
| 20-29%         | 394   | 129   | 265    | 0      | 32.7%     | $-0.020  | $-0.020  | -18.1%   |
| 30-39%         | 160   | 91    | 69     | 0      | 56.9%     | $1.600   | $1.600   | 42.2%    |
| 40-49%         | 39    | 34    | 5      | 0      | 87.2%     | $3.131   | $3.131   | 117.9%   |
| 50-59%         | 4     | 4     | 0      | 0      | 100.0%    | $3.718   | $3.718   | 149.9%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1686  | 574   | 1112   | 0      | 34.0%     | $-0.358  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 248   | 82    | 166    | 0      | 33.1%     | $-0.792  |
| Positive Gamma (Range-Bound friendly) | 1438  | 492   | 946    | 0      | 34.2%     | $-0.283  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 390   | 184   | 206    | 0      | 47.2%     | $0.813   |
| Time Held: 30-90m      | 408   | 108   | 300    | 0      | 26.5%     | $-0.845  |
| Time Held: 90-240m     | 651   | 224   | 427    | 0      | 34.4%     | $-0.229  |
| Time Held: <30m        | 228   | 52    | 176    | 0      | 22.8%     | $-1.906  |
| Time Held: >480m       | 9     | 6     | 3      | 0      | 66.7%     | $0.879   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 823   | 263   | 560    | 0      | 32.0%     | $-0.556  | 🔴          |
| Morning (10:00-12:00)  | 659   | 219   | 440    | 0      | 33.2%     | $-0.348  | 🔴          |
| ORB (9:30-10:00)       | 204   | 92    | 112    | 0      | 45.1%     | $0.411   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 204    | 0          | 1          | 203        | 0.0%      | 0.5%      | 99.5%     |
| Morning (10:00-12:00)  | 659    | 0          | 0          | 659        | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 823    | 0          | 3          | 820        | 0.0%      | 0.4%      | 99.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 34     | 12    | 22     | 0      | 35.3%     | $-0.763      | 🟢          |
| ORB (9:30-10:00)       | 10-19%     | 92     | 34    | 58     | 0      | 37.0%     | $-0.329      | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 56     | 29    | 27     | 0      | 51.8%     | $1.224       | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 17     | 12    | 5      | 0      | 70.6%     | $3.226       | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 4      | 4     | 0      | 0      | 100.0%    | $3.248       | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 1      | 1     | 0      | 0      | 100.0%    | $3.740       | ⚠️         |
| Morning (10:00-12:00)  | 5-9%       | 102    | 26    | 76     | 0      | 25.5%     | $-1.199      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 329    | 113   | 216    | 0      | 34.3%     | $-0.383      | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 153    | 38    | 115    | 0      | 24.8%     | $-0.602      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 61     | 30    | 31     | 0      | 49.2%     | $1.090       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 14     | 12    | 2      | 0      | 85.7%     | $3.180       | ⚠️         |
| Afternoon (12:00-16:00) | 5-9%       | 112    | 30    | 82     | 0      | 26.8%     | $-1.247      | 🔴          |
| Afternoon (12:00-16:00) | 10-19%     | 420    | 101   | 319    | 0      | 24.0%     | $-1.295      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 185    | 62    | 123    | 0      | 33.5%     | $0.084       | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 82     | 49    | 33     | 0      | 59.8%     | $1.642       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 21     | 18    | 3      | 0      | 85.7%     | $3.077       | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 3      | 3     | 0      | 0      | 100.0%    | $3.710       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1028  | 33    | 995    | 0      | 3.2%      | $-3.138  |
| SHORT        | 658   | 541   | 117    | 0      | 82.2%     | $3.986   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 10    | 2     | 8      | 0      | 20.0%     | $-2.740  |
| Long (30-60 min)       | 196   | 40    | 156    | 0      | 20.4%     | $-1.733  |
| Medium (5-15 min)      | 87    | 17    | 70     | 0      | 19.5%     | $-1.998  |
| Slow (15-30 min)       | 131   | 33    | 98     | 0      | 25.2%     | $-1.782  |
| Very Long (>1h)        | 1262  | 482   | 780    | 0      | 38.2%     | $0.136   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 34.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.36 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (87.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 5-9% (27.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.36) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $0.88) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (45.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (9430s / 157.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_decay_momentum

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,374  |  **Win Rate:** 33.5%  |  **Avg P&L (resolved):** $-0.556  |  **Avg P&L (all):** $-0.556  |  **Avg Hold:** 3547s (59.1m)  |  **Median Hold:** 1873s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 6     | 2     | 4      | 0      | 33.3%     | $-0.253  | $-0.253  | -16.7%   |
| 50-59%         | 610   | 216   | 394    | 0      | 35.4%     | $-0.298  | $-0.298  | -11.5%   |
| 60-69%         | 618   | 193   | 425    | 0      | 31.2%     | $-0.861  | $-0.861  | -21.9%   |
| 70-79%         | 129   | 45    | 84     | 0      | 34.9%     | $-0.370  | $-0.370  | -12.9%   |
| 80-89%         | 11    | 4     | 7      | 0      | 36.4%     | $-0.087  | $-0.087  | -8.8%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1374  | 460   | 914    | 0      | 33.5%     | $-0.556  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 346   | 59    | 287    | 0      | 17.1%     | $-1.755  |
| Positive Gamma (Range-Bound friendly) | 1028  | 401   | 627    | 0      | 39.0%     | $-0.152  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 51    | 6     | 45     | 0      | 11.8%     | $-2.628  |
| Time Held: 30-90m      | 420   | 179   | 241    | 0      | 42.6%     | $-0.105  |
| Time Held: 90-240m     | 232   | 47    | 185    | 0      | 20.3%     | $-1.754  |
| Time Held: <30m        | 671   | 228   | 443    | 0      | 34.0%     | $-0.267  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 779   | 229   | 550    | 0      | 29.4%     | $-0.651  | 🔴          |
| Morning (10:00-12:00)  | 458   | 175   | 283    | 0      | 38.2%     | $-0.501  | 🟢          |
| ORB (9:30-10:00)       | 137   | 56    | 81     | 0      | 40.9%     | $-0.199  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 137    | 16         | 121        | 0          | 11.7%     | 88.3%     | 0.0%      |
| Morning (10:00-12:00)  | 458    | 46         | 410        | 2          | 10.0%     | 89.5%     | 0.4%      |
| Afternoon (12:00-16:00) | 779    | 78         | 697        | 4          | 10.0%     | 89.5%     | 0.5%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 50-59%     | 53     | 20    | 33     | 0      | 37.7%     | $-0.088      | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 68     | 27    | 41     | 0      | 39.7%     | $-0.439      | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 13     | 7     | 6      | 0      | 53.8%     | $0.399       | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 3      | 2     | 1      | 0      | 66.7%     | $0.690       | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 2      | 1     | 1      | 0      | 50.0%     | $0.470       | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 203    | 87    | 116    | 0      | 42.9%     | $-0.108      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 207    | 71    | 136    | 0      | 34.3%     | $-0.918      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 46     | 16    | 30     | 0      | 34.8%     | $-0.400      | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 4      | 1     | 3      | 0      | 25.0%     | $-0.615      | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 354    | 109   | 245    | 0      | 30.8%     | $-0.438      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 343    | 95    | 248    | 0      | 27.7%     | $-0.910      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 70     | 22    | 48     | 0      | 31.4%     | $-0.494      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 8      | 2     | 6      | 0      | 25.0%     | $-0.379      | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 829   | 159   | 670    | 0      | 19.2%     | $-1.205  |
| SHORT        | 545   | 301   | 244    | 0      | 55.2%     | $0.432   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 103   | 23    | 80     | 0      | 22.3%     | $-0.859  |
| Long (30-60 min)       | 274   | 106   | 168    | 0      | 38.7%     | $-0.213  |
| Medium (5-15 min)      | 258   | 92    | 166    | 0      | 35.7%     | $-0.205  |
| Slow (15-30 min)       | 296   | 111   | 185    | 0      | 37.5%     | $-0.094  |
| Very Fast (<1 min)     | 14    | 2     | 12     | 0      | 14.3%     | $-0.680  |
| Very Long (>1h)        | 429   | 126   | 303    | 0      | 29.4%     | $-1.227  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.56 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (36.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (31.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.56) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $-0.10) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (40.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3547s / 59.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_imbalance_momentum

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 565  |  **Win Rate:** 54.9%  |  **Avg P&L (resolved):** $1.559  |  **Avg P&L (all):** $1.559  |  **Avg Hold:** 6776s (112.9m)  |  **Median Hold:** 4763s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 25    | 4     | 21     | 0      | 16.0%     | $-1.008  | $-1.008  | -52.1%   |
| 40-49%         | 156   | 75    | 81     | 0      | 48.1%     | $0.715   | $0.715   | 44.2%    |
| 50-59%         | 297   | 180   | 117    | 0      | 60.6%     | $2.044   | $2.044   | 81.8%    |
| 60-69%         | 66    | 37    | 29     | 0      | 56.1%     | $1.631   | $1.631   | 68.1%    |
| 70-79%         | 21    | 14    | 7      | 0      | 66.7%     | $3.789   | $3.789   | 100.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 565   | 310   | 255    | 0      | 54.9%     | $1.559   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 66    | 27    | 39     | 0      | 40.9%     | $0.666   |
| Positive Gamma (Range-Bound friendly) | 499   | 283   | 216    | 0      | 56.7%     | $1.677   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 59    | 54    | 5      | 0      | 91.5%     | $4.478   |
| Time Held: 30-90m      | 150   | 71    | 79     | 0      | 47.3%     | $1.873   |
| Time Held: 90-240m     | 209   | 138   | 71     | 0      | 66.0%     | $1.602   |
| Time Held: <30m        | 147   | 47    | 100    | 0      | 32.0%     | $0.005   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 261   | 160   | 101    | 0      | 61.3%     | $1.893   | 🟢          |
| Morning (10:00-12:00)  | 225   | 104   | 121    | 0      | 46.2%     | $0.942   | 🔴          |
| ORB (9:30-10:00)       | 79    | 46    | 33     | 0      | 58.2%     | $2.211   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 79     | 5          | 55         | 19         | 6.3%      | 69.6%     | 24.1%     |
| Morning (10:00-12:00)  | 225    | 10         | 155        | 60         | 4.4%      | 68.9%     | 26.7%     |
| Afternoon (12:00-16:00) | 261    | 6          | 153        | 102        | 2.3%      | 58.6%     | 39.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.220      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 17     | 7     | 10     | 0      | 41.2%     | $0.518       | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 47     | 30    | 17     | 0      | 63.8%     | $2.546       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 8      | 5     | 3      | 0      | 62.5%     | $2.695       | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 5      | 4     | 1      | 0      | 80.0%     | $5.412       | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 6      | 2     | 4      | 0      | 33.3%     | $0.357       | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 54     | 22    | 32     | 0      | 40.7%     | $0.254       | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 121    | 56    | 65     | 0      | 46.3%     | $1.017       | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 34     | 20    | 14     | 0      | 58.8%     | $1.646       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 10     | 4     | 6      | 0      | 40.0%     | $1.707       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 17     | 2     | 15     | 0      | 11.8%     | $-1.465      | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 85     | 46    | 39     | 0      | 54.1%     | $1.047       | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 129    | 94    | 35     | 0      | 72.9%     | $2.824       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 24     | 12    | 12     | 0      | 50.0%     | $1.256       | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 6      | 6     | 0      | 0      | 100.0%    | $5.905       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 142   | 23    | 119    | 0      | 16.2%     | $-0.965  |
| SHORT        | 423   | 287   | 136    | 0      | 67.8%     | $2.406   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 21    | 1     | 20     | 0      | 4.8%      | $-1.716  |
| Long (30-60 min)       | 89    | 32    | 57     | 0      | 36.0%     | $0.956   |
| Medium (5-15 min)      | 51    | 17    | 34     | 0      | 33.3%     | $0.286   |
| Slow (15-30 min)       | 73    | 29    | 44     | 0      | 39.7%     | $0.371   |
| Very Fast (<1 min)     | 2     | 0     | 2      | 0      | 0.0%      | $-2.455  |
| Very Long (>1h)        | 329   | 231   | 98     | 0      | 70.2%     | $2.416   |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 54.9% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 💰 Positive avg P&L per resolved signal: $1.56 — profitable even with 54.9% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (66.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (16.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $1.56) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $4.48) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (61.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6776s / 112.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_asymmetry

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 668  |  **Win Rate:** 21.7%  |  **Avg P&L (resolved):** $-0.249  |  **Avg P&L (all):** $-0.249  |  **Avg Hold:** 6311s (105.2m)  |  **Median Hold:** 4338s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 70-79%         | 9     | 2     | 7      | 0      | 22.2%     | $-1.051  | $-1.051  | -22.2%   |
| 80-89%         | 659   | 143   | 516    | 0      | 21.7%     | $-0.238  | $-0.238  | -24.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 668   | 145   | 523    | 0      | 21.7%     | $-0.249  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 668   | 145   | 523    | 0      | 21.7%     | $-0.249  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 66    | 41    | 25     | 0      | 62.1%     | $3.891   |
| Time Held: 30-90m      | 216   | 31    | 185    | 0      | 14.4%     | $-1.047  |
| Time Held: 90-240m     | 234   | 56    | 178    | 0      | 23.9%     | $0.246   |
| Time Held: <30m        | 152   | 17    | 135    | 0      | 11.2%     | $-1.675  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 318   | 72    | 246    | 0      | 22.6%     | $-0.188  | 🟢          |
| Morning (10:00-12:00)  | 266   | 50    | 216    | 0      | 18.8%     | $-0.564  | 🔴          |
| ORB (9:30-10:00)       | 84    | 23    | 61     | 0      | 27.4%     | $0.517   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 84     | 84         | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 266    | 266        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 318    | 318        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 70-79%     | 3      | 2     | 1      | 0      | 66.7%     | $5.007       | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 81     | 21    | 60     | 0      | 25.9%     | $0.351       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 2      | 0     | 2      | 0      | 0.0%      | $-4.070      | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 264    | 50    | 214    | 0      | 18.9%     | $-0.537      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 4      | 0     | 4      | 0      | 0.0%      | $-4.085      | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 314    | 72    | 242    | 0      | 22.9%     | $-0.138      | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 422   | 6     | 416    | 0      | 1.4%      | $-2.298  |
| SHORT        | 246   | 139   | 107    | 0      | 56.5%     | $3.267   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 16    | 1     | 15     | 0      | 6.2%      | $-2.281  |
| Long (30-60 min)       | 146   | 12    | 134    | 0      | 8.2%      | $-1.788  |
| Medium (5-15 min)      | 59    | 5     | 54     | 0      | 8.5%      | $-1.746  |
| Slow (15-30 min)       | 76    | 11    | 65     | 0      | 14.5%     | $-1.459  |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-4.130  |
| Very Long (>1h)        | 370   | 116   | 254    | 0      | 31.4%     | $0.944   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 21.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.25 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (22.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (21.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.25) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $3.89) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (27.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6311s / 105.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_concentration

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,133  |  **Win Rate:** 30.5%  |  **Avg P&L (resolved):** $-0.518  |  **Avg P&L (all):** $-0.518  |  **Avg Hold:** 4382s (73.0m)  |  **Median Hold:** 1513s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 20    | 3     | 17     | 0      | 15.0%     | $-1.243  | $-1.243  | -62.4%   |
| 20-29%         | 62    | 14    | 48     | 0      | 22.6%     | $-0.677  | $-0.677  | -43.6%   |
| 30-39%         | 197   | 43    | 154    | 0      | 21.8%     | $-0.989  | $-0.989  | -45.4%   |
| 40-49%         | 386   | 107   | 279    | 0      | 27.7%     | $-0.633  | $-0.633  | -30.7%   |
| 50-59%         | 211   | 69    | 142    | 0      | 32.7%     | $-0.399  | $-0.399  | -18.2%   |
| 60-69%         | 257   | 110   | 147    | 0      | 42.8%     | $0.015   | $0.015   | 7.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1133  | 346   | 787    | 0      | 30.5%     | $-0.518  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 219   | 51    | 168    | 0      | 23.3%     | $-1.331  |
| Positive Gamma (Range-Bound friendly) | 914   | 295   | 619    | 0      | 32.3%     | $-0.323  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 38    | 10    | 28     | 0      | 26.3%     | $-1.270  |
| Time Held: 30-90m      | 314   | 120   | 194    | 0      | 38.2%     | $-0.137  |
| Time Held: 90-240m     | 128   | 5     | 123    | 0      | 3.9%      | $-2.182  |
| Time Held: <30m        | 627   | 185   | 442    | 0      | 29.5%     | $-0.435  |
| Time Held: >480m       | 26    | 26    | 0      | 0      | 100.0%    | $2.185   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 641   | 172   | 469    | 0      | 26.8%     | $-0.590  | 🔴          |
| Morning (10:00-12:00)  | 380   | 136   | 244    | 0      | 35.8%     | $-0.465  | 🟢          |
| ORB (9:30-10:00)       | 112   | 38    | 74     | 0      | 33.9%     | $-0.284  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 112    | 0          | 53         | 59         | 0.0%      | 47.3%     | 52.7%     |
| Morning (10:00-12:00)  | 380    | 0          | 156        | 224        | 0.0%      | 41.1%     | 58.9%     |
| Afternoon (12:00-16:00) | 641    | 0          | 259        | 382        | 0.0%      | 40.4%     | 59.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 3      | 0     | 3      | 0      | 0.0%      | $-2.263      | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 17     | 6     | 11     | 0      | 35.3%     | $-0.358      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 39     | 12    | 27     | 0      | 30.8%     | $-0.325      | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 24     | 10    | 14     | 0      | 41.7%     | $0.279       | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 29     | 10    | 19     | 0      | 34.5%     | $-0.445      | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 10     | 0     | 10     | 0      | 0.0%      | $-1.731      | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 14     | 4     | 10     | 0      | 28.6%     | $-0.599      | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 77     | 24    | 53     | 0      | 31.2%     | $-0.936      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 123    | 46    | 77     | 0      | 37.4%     | $-0.551      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 79     | 26    | 53     | 0      | 32.9%     | $-0.389      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 77     | 36    | 41     | 0      | 46.8%     | $0.255       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 10     | 3     | 7      | 0      | 30.0%     | $-0.754      | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 45     | 10    | 35     | 0      | 22.2%     | $-0.596      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 103    | 13    | 90     | 0      | 12.6%     | $-1.132      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 224    | 49    | 175    | 0      | 21.9%     | $-0.732      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 108    | 33    | 75     | 0      | 30.6%     | $-0.556      | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 151    | 64    | 87     | 0      | 42.4%     | $-0.019      | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 935   | 242   | 693    | 0      | 25.9%     | $-0.731  |
| SHORT        | 198   | 104   | 94     | 0      | 52.5%     | $0.490   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 108   | 21    | 87     | 0      | 19.4%     | $-0.925  |
| Long (30-60 min)       | 227   | 93    | 134    | 0      | 41.0%     | $-0.080  |
| Medium (5-15 min)      | 220   | 73    | 147    | 0      | 33.2%     | $-0.344  |
| Slow (15-30 min)       | 287   | 88    | 199    | 0      | 30.7%     | $-0.295  |
| Very Fast (<1 min)     | 12    | 3     | 9      | 0      | 25.0%     | $-1.048  |
| Very Long (>1h)        | 279   | 68    | 211    | 0      | 24.4%     | $-1.059  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.52 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (42.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (15.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.52) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $2.19) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (35.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4382s / 73.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_imbalance

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 574  |  **Win Rate:** 32.2%  |  **Avg P&L (resolved):** $-0.061  |  **Avg P&L (all):** $-0.061  |  **Avg Hold:** 2413s (40.2m)  |  **Median Hold:** 1409s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 1     | 1     | 0      | 0      | 100.0%    | $2.020   | $2.020   | 200.0%   |
| 30-39%         | 6     | 2     | 4      | 0      | 33.3%     | $-0.008  | $-0.008  | -0.4%    |
| 40-49%         | 38    | 9     | 29     | 0      | 23.7%     | $-0.487  | $-0.487  | -28.9%   |
| 50-59%         | 108   | 38    | 70     | 0      | 35.2%     | $0.069   | $0.069   | 5.6%     |
| 60-69%         | 122   | 37    | 85     | 0      | 30.3%     | $-0.187  | $-0.187  | -9.1%    |
| 70-79%         | 206   | 65    | 141    | 0      | 31.6%     | $-0.085  | $-0.085  | -5.4%    |
| 80-89%         | 93    | 33    | 60     | 0      | 35.5%     | $0.156   | $0.156   | 6.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 574   | 185   | 389    | 0      | 32.2%     | $-0.061  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 48    | 5     | 43     | 0      | 10.4%     | $-1.591  |
| Positive Gamma (Range-Bound friendly) | 526   | 180   | 346    | 0      | 34.2%     | $0.079   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 7     | 0     | 7      | 0      | 0.0%      | $-3.726  |
| Time Held: 30-90m      | 185   | 99    | 86     | 0      | 53.5%     | $1.290   |
| Time Held: 90-240m     | 50    | 8     | 42     | 0      | 16.0%     | $-1.188  |
| Time Held: <30m        | 331   | 77    | 254    | 0      | 23.3%     | $-0.591  |
| Time Held: >480m       | 1     | 1     | 0      | 0      | 100.0%    | $7.480   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 334   | 109   | 225    | 0      | 32.6%     | $0.050   | 🟢          |
| Morning (10:00-12:00)  | 183   | 58    | 125    | 0      | 31.7%     | $-0.315  | 🔴          |
| ORB (9:30-10:00)       | 57    | 18    | 39     | 0      | 31.6%     | $0.104   | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 57     | 30         | 26         | 1          | 52.6%     | 45.6%     | 1.8%      |
| Morning (10:00-12:00)  | 183    | 95         | 75         | 13         | 51.9%     | 41.0%     | 7.1%      |
| Afternoon (12:00-16:00) | 334    | 174        | 129        | 31         | 52.1%     | 38.6%     | 9.3%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 40-49%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.500      | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 8      | 1     | 7      | 0      | 12.5%     | $-1.419      | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 18     | 6     | 12     | 0      | 33.3%     | $0.432       | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 18     | 5     | 13     | 0      | 27.8%     | $-0.285      | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 12     | 6     | 6      | 0      | 50.0%     | $1.261       | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.870      | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 12     | 3     | 9      | 0      | 25.0%     | $-0.235      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 35     | 17    | 18     | 0      | 48.6%     | $0.530       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 40     | 14    | 26     | 0      | 35.0%     | $-0.308      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 75     | 19    | 56     | 0      | 25.3%     | $-0.617      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 20     | 5     | 15     | 0      | 25.0%     | $-0.645      | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 1      | 1     | 0      | 0      | 100.0%    | $2.020       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 5      | 2     | 3      | 0      | 40.0%     | $0.364       | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 25     | 6     | 19     | 0      | 24.0%     | $-0.607      | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 65     | 20    | 45     | 0      | 30.8%     | $0.003       | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 64     | 17    | 47     | 0      | 26.6%     | $-0.286      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 113    | 41    | 72     | 0      | 36.3%     | $0.299       | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 61     | 22    | 39     | 0      | 36.1%     | $0.202       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 322   | 85    | 237    | 0      | 26.4%     | $-0.419  |
| SHORT        | 252   | 100   | 152    | 0      | 39.7%     | $0.397   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 68    | 6     | 62     | 0      | 8.8%      | $-1.597  |
| Long (30-60 min)       | 138   | 83    | 55     | 0      | 60.1%     | $1.695   |
| Medium (5-15 min)      | 122   | 25    | 97     | 0      | 20.5%     | $-0.792  |
| Slow (15-30 min)       | 133   | 46    | 87     | 0      | 34.6%     | $0.210   |
| Very Fast (<1 min)     | 8     | 0     | 8      | 0      | 0.0%      | $-2.306  |
| Very Long (>1h)        | 105   | 25    | 80     | 0      | 23.8%     | $-0.697  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 32.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.06 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (35.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (23.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.06) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $1.29) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (32.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2413s / 40.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_flip_breakout

**Symbols:** NVDA  |  **Total Signals:** 156  |  **Win Rate:** 19.9%  |  **Avg P&L (resolved):** $-0.607  |  **Avg P&L (all):** $-0.607  |  **Avg Hold:** 3467s (57.8m)  |  **Median Hold:** 2352s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 1     | 0     | 1      | 0      | 0.0%      | $-3.060  | $-3.060  | -100.0%  |
| 10-19%         | 11    | 0     | 11     | 0      | 0.0%      | $-2.746  | $-2.746  | -100.0%  |
| 20-29%         | 8     | 0     | 8      | 0      | 0.0%      | $-2.330  | $-2.330  | -100.0%  |
| 30-39%         | 8     | 0     | 8      | 0      | 0.0%      | $-1.887  | $-1.887  | -100.0%  |
| 40-49%         | 24    | 3     | 21     | 0      | 12.5%     | $-0.862  | $-0.862  | -56.3%   |
| 50-59%         | 1     | 0     | 1      | 0      | 0.0%      | $-1.290  | $-1.290  | -100.0%  |
| 60-69%         | 68    | 16    | 52     | 0      | 23.5%     | $-0.136  | $-0.136  | -17.6%   |
| 70-79%         | 35    | 12    | 23     | 0      | 34.3%     | $0.102   | $0.102   | 20.3%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 82    | 19    | 63     | 0      | 23.2%     | $-0.599  |
| Trending (Up)        | 74    | 12    | 62     | 0      | 16.2%     | $-0.615  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 156   | 31    | 125    | 0      | 19.9%     | $-0.607  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 67    | 19    | 48     | 0      | 28.4%     | $-0.282  |
| Time Held: 90-240m     | 32    | 5     | 27     | 0      | 15.6%     | $-1.343  |
| Time Held: <30m        | 57    | 7     | 50     | 0      | 12.3%     | $-0.575  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 153   | 31    | 122    | 0      | 20.3%     | $-0.568  | 🟢          |
| Morning (10:00-12:00)  | 3     | 0     | 3      | 0      | 0.0%      | $-2.600  | ⚠️         |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 3      | 0          | 0          | 3          | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 153    | 35         | 69         | 49         | 22.9%     | 45.1%     | 32.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Morning (10:00-12:00)  | 10-19%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.740      | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-2.320      | ⚠️         |
| Afternoon (12:00-16:00) | 5-9%       | 1      | 0     | 1      | 0      | 0.0%      | $-3.060      | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 9      | 0     | 9      | 0      | 0.0%      | $-2.748      | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 7      | 0     | 7      | 0      | 0.0%      | $-2.331      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 8      | 0     | 8      | 0      | 0.0%      | $-1.887      | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 24     | 3     | 21     | 0      | 12.5%     | $-0.862      | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.290      | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 68     | 16    | 52     | 0      | 23.5%     | $-0.136      | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 35     | 12    | 23     | 0      | 34.3%     | $0.102       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 78    | 7     | 71     | 0      | 9.0%      | $-0.988  |
| SHORT        | 78    | 24    | 54     | 0      | 30.8%     | $-0.226  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 4     | 0     | 4      | 0      | 0.0%      | $-0.465  |
| Long (30-60 min)       | 52    | 17    | 35     | 0      | 32.7%     | $-0.258  |
| Medium (5-15 min)      | 32    | 0     | 32     | 0      | 0.0%      | $-0.726  |
| Slow (15-30 min)       | 20    | 7     | 13     | 0      | 35.0%     | $-0.366  |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-0.360  |
| Very Long (>1h)        | 47    | 7     | 40     | 0      | 14.9%     | $-1.031  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 19.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.61 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (34.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.60) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $-0.28) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (20.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3467s / 57.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 511  |  **Win Rate:** 30.7%  |  **Avg P&L (resolved):** $-0.435  |  **Avg P&L (all):** $-0.435  |  **Avg Hold:** 17283s (288.0m)  |  **Median Hold:** 2885s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 114   | 46    | 68     | 0      | 40.4%     | $0.543   | $0.543   | 21.1%    |
| 40-49%         | 337   | 96    | 241    | 0      | 28.5%     | $-0.782  | $-0.782  | -14.5%   |
| 50-59%         | 60    | 15    | 45     | 0      | 25.0%     | $-0.347  | $-0.347  | -25.3%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 354   | 123   | 231    | 0      | 34.7%     | $-0.362  |
| Trending (Up)        | 157   | 34    | 123    | 0      | 21.7%     | $-0.601  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 76    | 10    | 66     | 0      | 13.2%     | $-1.856  |
| Positive Gamma (Range-Bound friendly) | 435   | 147   | 288    | 0      | 33.8%     | $-0.187  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 29    | 0     | 29     | 0      | 0.0%      | $-2.685  |
| Time Held: 30-90m      | 105   | 51    | 54     | 0      | 48.6%     | $0.759   |
| Time Held: 90-240m     | 45    | 5     | 40     | 0      | 11.1%     | $-0.659  |
| Time Held: <30m        | 206   | 36    | 170    | 0      | 17.5%     | $-0.770  |
| Time Held: >480m       | 126   | 65    | 61     | 0      | 51.6%     | $-0.286  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 254   | 89    | 165    | 0      | 35.0%     | $-0.033  | 🟢          |
| Morning (10:00-12:00)  | 179   | 57    | 122    | 0      | 31.8%     | $-0.431  | 🟢          |
| ORB (9:30-10:00)       | 78    | 11    | 67     | 0      | 14.1%     | $-1.757  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 78     | 0          | 5          | 73         | 0.0%      | 6.4%      | 93.6%     |
| Morning (10:00-12:00)  | 179    | 0          | 26         | 153        | 0.0%      | 14.5%     | 85.5%     |
| Afternoon (12:00-16:00) | 254    | 0          | 29         | 225        | 0.0%      | 11.4%     | 88.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 22     | 3     | 19     | 0      | 13.6%     | $-1.841      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 51     | 7     | 44     | 0      | 13.7%     | $-1.840      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 5      | 1     | 4      | 0      | 20.0%     | $-0.532      | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 33     | 19    | 14     | 0      | 57.6%     | $1.593       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 120    | 36    | 84     | 0      | 30.0%     | $-0.906      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 26     | 2     | 24     | 0      | 7.7%      | $-0.808      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 59     | 24    | 35     | 0      | 40.7%     | $0.845       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 166    | 53    | 113    | 0      | 31.9%     | $-0.367      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 29     | 12    | 17     | 0      | 41.4%     | $0.098       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 435   | 147   | 288    | 0      | 33.8%     | $-0.187  |
| SHORT        | 76    | 10    | 66     | 0      | 13.2%     | $-1.856  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 53    | 7     | 46     | 0      | 13.2%     | $-0.789  |
| Long (30-60 min)       | 68    | 40    | 28     | 0      | 58.8%     | $1.462   |
| Medium (5-15 min)      | 67    | 7     | 60     | 0      | 10.4%     | $-1.225  |
| Slow (15-30 min)       | 81    | 22    | 59     | 0      | 27.2%     | $-0.351  |
| Very Fast (<1 min)     | 5     | 0     | 5      | 0      | 0.0%      | $-1.248  |
| Very Long (>1h)        | 237   | 81    | 156    | 0      | 34.2%     | $-0.689  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.44 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (40.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (25.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.36) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.76) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (35.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (17283s / 288.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_wall_bounce

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 504  |  **Win Rate:** 18.1%  |  **Avg P&L (resolved):** $-1.928  |  **Avg P&L (all):** $-1.928  |  **Avg Hold:** 46665s (777.7m)  |  **Median Hold:** 61471s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 3     | 0     | 3      | 0      | 0.0%      | $-0.767  | $-0.767  | -100.0%  |
| 30-39%         | 343   | 4     | 339    | 0      | 1.2%      | $-3.555  | $-3.555  | -97.0%   |
| 40-49%         | 26    | 7     | 19     | 0      | 26.9%     | $-0.018  | $-0.018  | -27.2%   |
| 50-59%         | 37    | 17    | 20     | 0      | 45.9%     | $1.165   | $1.165   | 30.4%    |
| 60-69%         | 19    | 11    | 8      | 0      | 57.9%     | $2.663   | $2.663   | 99.6%    |
| 70-79%         | 5     | 4     | 1      | 0      | 80.0%     | $4.048   | $4.048   | 196.3%   |
| 80-89%         | 6     | 6     | 0      | 0      | 100.0%    | $2.335   | $2.335   | 150.1%   |
| 90-99%         | 9     | 8     | 1      | 0      | 88.9%     | $1.733   | $1.733   | 122.3%   |
| 100%           | 56    | 34    | 22     | 0      | 60.7%     | $1.907   | $1.907   | 51.7%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 418   | 49    | 369    | 0      | 11.7%     | $-2.536  |
| Trending (Up)        | 86    | 42    | 44     | 0      | 48.8%     | $1.025   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 332   | 0     | 332    | 0      | 0.0%      | $-3.690  |
| Positive Gamma (Range-Bound friendly) | 172   | 91    | 81     | 0      | 52.9%     | $1.472   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 23    | 23    | 0      | 0      | 100.0%    | $5.865   |
| Time Held: 30-90m      | 58    | 28    | 30     | 0      | 48.3%     | $0.408   |
| Time Held: 90-240m     | 12    | 5     | 7      | 0      | 41.7%     | $0.660   |
| Time Held: <30m        | 71    | 27    | 44     | 0      | 38.0%     | $0.448   |
| Time Held: >480m       | 340   | 8     | 332    | 0      | 2.4%      | $-3.442  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 270   | 34    | 236    | 0      | 12.6%     | $-2.264  | 🔴          |
| Morning (10:00-12:00)  | 103   | 1     | 102    | 0      | 1.0%      | $-3.594  | 🔴          |
| ORB (9:30-10:00)       | 131   | 56    | 75     | 0      | 42.7%     | $0.073   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 131    | 73         | 19         | 39         | 55.7%     | 14.5%     | 29.8%     |
| Morning (10:00-12:00)  | 103    | 0          | 0          | 103        | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 270    | 3          | 37         | 230        | 1.1%      | 13.7%     | 85.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.820      | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 29     | 0     | 29     | 0      | 0.0%      | $-3.490      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 9      | 1     | 8      | 0      | 11.1%     | $-0.913      | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 11     | 5     | 6      | 0      | 45.5%     | $0.013       | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 8      | 1     | 7      | 0      | 12.5%     | $-1.868      | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 2      | 1     | 1      | 0      | 50.0%     | $-0.905      | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 6      | 6     | 0      | 0      | 100.0%    | $2.335       | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 9      | 8     | 1      | 0      | 88.9%     | $1.733       | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 56     | 34    | 22     | 0      | 60.7%     | $1.907       | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 102    | 0     | 102    | 0      | 0.0%      | $-3.690      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 1      | 1     | 0      | 0      | 100.0%    | $6.210       | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 2      | 0     | 2      | 0      | 0.0%      | $-0.740      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 212    | 4     | 208    | 0      | 1.9%      | $-3.499      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 16     | 5     | 11     | 0      | 31.2%     | $0.096       | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 26     | 12    | 14     | 0      | 46.2%     | $1.652       | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 11     | 10    | 1      | 0      | 90.9%     | $5.958       | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 3      | 3     | 0      | 0      | 100.0%    | $7.350       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 70    | 3     | 67     | 0      | 4.3%      | $-2.636  |
| SHORT        | 434   | 88    | 346    | 0      | 20.3%     | $-1.814  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 14    | 4     | 10     | 0      | 28.6%     | $-0.615  |
| Long (30-60 min)       | 30    | 19    | 11     | 0      | 63.3%     | $1.980   |
| Medium (5-15 min)      | 26    | 6     | 20     | 0      | 23.1%     | $-0.723  |
| Slow (15-30 min)       | 30    | 17    | 13     | 0      | 56.7%     | $2.036   |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-1.830  |
| Very Long (>1h)        | 403   | 45    | 358    | 0      | 11.2%     | $-2.638  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 18.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.93 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (1.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $1.02) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $5.86) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (42.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (46665s / 777.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_divergence

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 686  |  **Win Rate:** 25.1%  |  **Avg P&L (resolved):** $-0.468  |  **Avg P&L (all):** $-0.468  |  **Avg Hold:** 2264s (37.7m)  |  **Median Hold:** 1336s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 50-59%         | 41    | 12    | 29     | 0      | 29.3%     | $-0.762  | $-0.762  | -26.8%   |
| 60-69%         | 325   | 82    | 243    | 0      | 25.2%     | $-0.486  | $-0.486  | -36.9%   |
| 70-79%         | 285   | 67    | 218    | 0      | 23.5%     | $-0.456  | $-0.456  | -41.2%   |
| 80-89%         | 35    | 11    | 24     | 0      | 31.4%     | $-0.043  | $-0.043  | -21.4%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 543   | 128   | 415    | 0      | 23.6%     | $-0.523  |
| Trending (Up)        | 143   | 44    | 99     | 0      | 30.8%     | $-0.259  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 37    | 14    | 23     | 0      | 37.8%     | $-0.351  |
| Positive Gamma (Range-Bound friendly) | 649   | 158   | 491    | 0      | 24.3%     | $-0.474  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 3     | 0     | 3      | 0      | 0.0%      | $-3.733  |
| Time Held: 30-90m      | 171   | 73    | 98     | 0      | 42.7%     | $0.285   |
| Time Held: 90-240m     | 78    | 4     | 74     | 0      | 5.1%      | $-1.128  |
| Time Held: <30m        | 434   | 95    | 339    | 0      | 21.9%     | $-0.623  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 385   | 88    | 297    | 0      | 22.9%     | $-0.443  | 🔴          |
| Morning (10:00-12:00)  | 219   | 74    | 145    | 0      | 33.8%     | $-0.202  | 🟢          |
| ORB (9:30-10:00)       | 82    | 10    | 72     | 0      | 12.2%     | $-1.295  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 82     | 52         | 30         | 0          | 63.4%     | 36.6%     | 0.0%      |
| Morning (10:00-12:00)  | 219    | 108        | 111        | 0          | 49.3%     | 50.7%     | 0.0%      |
| Afternoon (12:00-16:00) | 385    | 160        | 225        | 0          | 41.6%     | 58.4%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 60-69%     | 30     | 5     | 25     | 0      | 16.7%     | $-1.555      | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 33     | 1     | 32     | 0      | 3.0%      | $-1.582      | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 19     | 4     | 15     | 0      | 21.1%     | $-0.387      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 21     | 7     | 14     | 0      | 33.3%     | $-0.406      | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 90     | 30    | 60     | 0      | 33.3%     | $-0.189      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 101    | 32    | 69     | 0      | 31.7%     | $-0.282      | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 7      | 5     | 2      | 0      | 71.4%     | $1.410       | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 20     | 5     | 15     | 0      | 25.0%     | $-1.137      | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 205    | 47    | 158    | 0      | 22.9%     | $-0.460      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 151    | 34    | 117    | 0      | 22.5%     | $-0.326      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 9      | 2     | 7      | 0      | 22.2%     | $-0.448      | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 572   | 124   | 448    | 0      | 21.7%     | $-0.571  |
| SHORT        | 114   | 48    | 66     | 0      | 42.1%     | $0.052   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 82    | 19    | 63     | 0      | 23.2%     | $-0.762  |
| Long (30-60 min)       | 97    | 35    | 62     | 0      | 36.1%     | $0.051   |
| Medium (5-15 min)      | 157   | 25    | 132    | 0      | 15.9%     | $-0.859  |
| Slow (15-30 min)       | 186   | 51    | 135    | 0      | 27.4%     | $-0.312  |
| Very Fast (<1 min)     | 9     | 0     | 9      | 0      | 0.0%      | $-1.650  |
| Very Long (>1h)        | 155   | 42    | 113    | 0      | 27.1%     | $-0.357  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.47 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (31.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (23.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.26) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.28) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (33.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2264s / 37.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_imbalance

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,635  |  **Win Rate:** 37.8%  |  **Avg P&L (resolved):** $-0.082  |  **Avg P&L (all):** $-0.082  |  **Avg Hold:** 13498s (225.0m)  |  **Median Hold:** 438s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 96    | 36    | 60     | 0      | 37.5%     | $-0.009  | $-0.009  | -6.3%    |
| 20-29%         | 350   | 165   | 185    | 0      | 47.1%     | $0.230   | $0.230   | 17.9%    |
| 30-39%         | 502   | 67    | 435    | 0      | 13.3%     | $-0.666  | $-0.666  | -66.6%   |
| 40-49%         | 106   | 49    | 57     | 0      | 46.2%     | $0.469   | $0.469   | 15.5%    |
| 50-59%         | 495   | 254   | 241    | 0      | 51.3%     | $0.117   | $0.117   | 28.2%    |
| 60-69%         | 82    | 44    | 38     | 0      | 53.7%     | $0.158   | $0.158   | 34.4%    |
| 70-79%         | 4     | 3     | 1      | 0      | 75.0%     | $0.197   | $0.197   | 89.6%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1158  | 376   | 782    | 0      | 32.5%     | $-0.224  |
| Trending (Up)        | 477   | 242   | 235    | 0      | 50.7%     | $0.263   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 17    | 3     | 14     | 0      | 17.6%     | $-0.312  |
| Positive Gamma (Range-Bound friendly) | 1618  | 615   | 1003   | 0      | 38.0%     | $-0.079  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 5     | 5     | 0      | 0      | 100.0%    | $6.132   |
| Time Held: 30-90m      | 48    | 29    | 19     | 0      | 60.4%     | $0.609   |
| Time Held: 90-240m     | 11    | 7     | 4      | 0      | 63.6%     | $1.343   |
| Time Held: <30m        | 1184  | 577   | 607    | 0      | 48.7%     | $0.158   |
| Time Held: >480m       | 387   | 0     | 387    | 0      | 0.0%      | $-1.020  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 901   | 330   | 571    | 0      | 36.6%     | $-0.169  | 🔴          |
| Morning (10:00-12:00)  | 558   | 194   | 364    | 0      | 34.8%     | $-0.163  | 🔴          |
| ORB (9:30-10:00)       | 176   | 94    | 82     | 0      | 53.4%     | $0.628   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 176    | 0          | 56         | 120        | 0.0%      | 31.8%     | 68.2%     |
| Morning (10:00-12:00)  | 558    | 0          | 167        | 391        | 0.0%      | 29.9%     | 70.1%     |
| Afternoon (12:00-16:00) | 901    | 4          | 354        | 543        | 0.4%      | 39.3%     | 60.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 10     | 10    | 0      | 0      | 100.0%    | $1.238       | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 27     | 18    | 9      | 0      | 66.7%     | $1.843       | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 52     | 13    | 39     | 0      | 25.0%     | $-0.494      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 31     | 19    | 12     | 0      | 61.3%     | $1.626       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 47     | 29    | 18     | 0      | 61.7%     | $0.448       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 9      | 5     | 4      | 0      | 55.6%     | $0.298       | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 56     | 16    | 40     | 0      | 28.6%     | $-0.163      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 146    | 63    | 83     | 0      | 43.2%     | $-0.033      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 172    | 30    | 142    | 0      | 17.4%     | $-0.538      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 17     | 5     | 12     | 0      | 29.4%     | $-0.108      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 141    | 68    | 73     | 0      | 48.2%     | $0.082       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 26     | 12    | 14     | 0      | 46.2%     | $0.215       | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 30     | 10    | 20     | 0      | 33.3%     | $-0.138      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 177    | 84    | 93     | 0      | 47.5%     | $0.202       | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 278    | 24    | 254    | 0      | 8.6%      | $-0.777      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 58     | 25    | 33     | 0      | 43.1%     | $0.020       | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 307    | 157   | 150    | 0      | 51.1%     | $0.082       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 47     | 27    | 20     | 0      | 57.4%     | $0.100       | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 4      | 3     | 1      | 0      | 75.0%     | $0.197       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 14    | 0     | 14     | 0      | 0.0%      | $-0.512  |
| SHORT        | 1621  | 618   | 1003   | 0      | 38.1%     | $-0.078  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 535   | 234   | 301    | 0      | 43.7%     | $0.020   |
| Long (30-60 min)       | 43    | 27    | 16     | 0      | 62.8%     | $0.639   |
| Medium (5-15 min)      | 393   | 219   | 174    | 0      | 55.7%     | $0.208   |
| Slow (15-30 min)       | 139   | 94    | 45     | 0      | 67.6%     | $0.812   |
| Very Fast (<1 min)     | 117   | 30    | 87     | 0      | 25.6%     | $-0.158  |
| Very Long (>1h)        | 408   | 14    | 394    | 0      | 3.4%      | $-0.852  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 37.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.08 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (53.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (13.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.26) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $6.13) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (53.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (13498s / 225.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### magnet_accelerate

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,423  |  **Win Rate:** 16.5%  |  **Avg P&L (resolved):** $-0.181  |  **Avg P&L (all):** $-0.181  |  **Avg Hold:** 1538s (25.6m)  |  **Median Hold:** 508s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 11    | 0     | 11     | 0      | 0.0%      | $-0.943  | $-0.943  | -100.0%  |
| 10-19%         | 98    | 0     | 98     | 0      | 0.0%      | $-1.104  | $-1.104  | -100.0%  |
| 20-29%         | 193   | 4     | 189    | 0      | 2.1%      | $-1.167  | $-1.167  | -94.0%   |
| 30-39%         | 206   | 2     | 204    | 0      | 1.0%      | $-1.526  | $-1.526  | -97.5%   |
| 40-49%         | 166   | 42    | 124    | 0      | 25.3%     | $-0.669  | $-0.669  | -33.7%   |
| 50-59%         | 192   | 82    | 110    | 0      | 42.7%     | $0.062   | $0.062   | 16.0%    |
| 60-69%         | 521   | 78    | 443    | 0      | 15.0%     | $0.920   | $0.920   | 89.1%    |
| 70-79%         | 35    | 26    | 9      | 0      | 74.3%     | $0.572   | $0.572   | 107.6%   |
| 80-89%         | 1     | 1     | 0      | 0      | 100.0%    | $0.850   | $0.850   | 119.7%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 991   | 119   | 872    | 0      | 12.0%     | $0.087   |
| Trending (Up)        | 432   | 116   | 316    | 0      | 26.9%     | $-0.795  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 544   | 53    | 491    | 0      | 9.7%      | $0.729   |
| Positive Gamma (Range-Bound friendly) | 879   | 182   | 697    | 0      | 20.7%     | $-0.744  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 6     | 0     | 6      | 0      | 0.0%      | $-4.137  |
| Time Held: 30-90m      | 257   | 79    | 178    | 0      | 30.7%     | $-0.729  |
| Time Held: 90-240m     | 92    | 7     | 85     | 0      | 7.6%      | $-0.962  |
| Time Held: <30m        | 1068  | 149   | 919    | 0      | 14.0%     | $0.040   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 874   | 98    | 776    | 0      | 11.2%     | $-0.254  | 🔴          |
| Morning (10:00-12:00)  | 404   | 82    | 322    | 0      | 20.3%     | $-0.271  | 🟢          |
| ORB (9:30-10:00)       | 145   | 55    | 90     | 0      | 37.9%     | $0.511   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 145    | 0          | 77         | 68         | 0.0%      | 53.1%     | 46.9%     |
| Morning (10:00-12:00)  | 404    | 22         | 195        | 187        | 5.4%      | 48.3%     | 46.3%     |
| Afternoon (12:00-16:00) | 874    | 14         | 441        | 419        | 1.6%      | 50.5%     | 47.9%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 1      | 0     | 1      | 0      | 0.0%      | $-1.570      | ⚠️         |
| ORB (9:30-10:00)       | 10-19%     | 11     | 0     | 11     | 0      | 0.0%      | $-1.185      | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 16     | 4     | 12     | 0      | 25.0%     | $0.520       | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 20     | 2     | 18     | 0      | 10.0%     | $-0.979      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 20     | 14    | 6      | 0      | 70.0%     | $0.855       | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 38     | 32    | 6      | 0      | 84.2%     | $1.233       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 39     | 3     | 36     | 0      | 7.7%      | $0.925       | 🔴          |
| Morning (10:00-12:00)  | 5-9%       | 6      | 0     | 6      | 0      | 0.0%      | $-0.770      | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 31     | 0     | 31     | 0      | 0.0%      | $-1.175      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 68     | 0     | 68     | 0      | 0.0%      | $-1.642      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 61     | 0     | 61     | 0      | 0.0%      | $-2.192      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 21     | 3     | 18     | 0      | 14.3%     | $-1.612      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 34     | 31    | 3      | 0      | 91.2%     | $1.189       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 161    | 34    | 127    | 0      | 21.1%     | $1.000       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 22     | 14    | 8      | 0      | 63.6%     | $0.425       | ⚠️         |
| Afternoon (12:00-16:00) | 5-9%       | 4      | 0     | 4      | 0      | 0.0%      | $-1.045      | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 56     | 0     | 56     | 0      | 0.0%      | $-1.050      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 109    | 0     | 109    | 0      | 0.0%      | $-1.119      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 125    | 0     | 125    | 0      | 0.0%      | $-1.289      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 125    | 25    | 100    | 0      | 20.0%     | $-0.755      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 120    | 19    | 101    | 0      | 15.8%     | $-0.628      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 321    | 41    | 280    | 0      | 12.8%     | $0.879       | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 13     | 12    | 1      | 0      | 92.3%     | $0.819       | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 1      | 1     | 0      | 0      | 100.0%    | $0.850       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1250  | 90    | 1160   | 0      | 7.2%      | $-0.389  |
| SHORT        | 173   | 145   | 28     | 0      | 83.8%     | $1.321   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 170   | 19    | 151    | 0      | 11.2%     | $-0.764  |
| Long (30-60 min)       | 186   | 55    | 131    | 0      | 29.6%     | $-0.877  |
| Medium (5-15 min)      | 285   | 46    | 239    | 0      | 16.1%     | $-0.655  |
| Slow (15-30 min)       | 181   | 72    | 109    | 0      | 39.8%     | $-0.320  |
| Very Fast (<1 min)     | 432   | 12    | 420    | 0      | 2.8%      | $0.967   |
| Very Long (>1h)        | 169   | 31    | 138    | 0      | 18.3%     | $-0.813  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 16.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.18 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (74.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.09) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.04) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: ORB (9:30-10:00) (37.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1538s / 25.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### order_book_fragmentation

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,771  |  **Win Rate:** 20.3%  |  **Avg P&L (resolved):** $-0.355  |  **Avg P&L (all):** $-0.355  |  **Avg Hold:** 3305s (55.1m)  |  **Median Hold:** 1217s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 10    | 1     | 9      | 0      | 10.0%     | $-0.918  | $-0.918  | -59.9%   |
| 40-49%         | 254   | 66    | 188    | 0      | 26.0%     | $0.043   | $0.043   | 3.9%     |
| 50-59%         | 838   | 176   | 662    | 0      | 21.0%     | $-0.381  | $-0.381  | -15.9%   |
| 60-69%         | 387   | 66    | 321    | 0      | 17.1%     | $-0.584  | $-0.584  | -31.7%   |
| 70-79%         | 222   | 41    | 181    | 0      | 18.5%     | $-0.241  | $-0.241  | -26.1%   |
| 80-89%         | 54    | 9     | 45     | 0      | 16.7%     | $-0.509  | $-0.509  | -33.5%   |
| 90-99%         | 3     | 0     | 3      | 0      | 0.0%      | $-1.157  | $-1.157  | -100.0%  |
| 100%           | 3     | 1     | 2      | 0      | 33.3%     | $-0.333  | $-0.333  | 32.8%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1771  | 360   | 1411   | 0      | 20.3%     | $-0.355  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1771  | 360   | 1411   | 0      | 20.3%     | $-0.355  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 40    | 4     | 36     | 0      | 10.0%     | $-1.337  |
| Time Held: 30-90m      | 453   | 154   | 299    | 0      | 34.0%     | $-0.114  |
| Time Held: 90-240m     | 200   | 23    | 177    | 0      | 11.5%     | $-1.258  |
| Time Held: <30m        | 1049  | 175   | 874    | 0      | 16.7%     | $-0.261  |
| Time Held: >480m       | 29    | 4     | 25     | 0      | 13.8%     | $0.042   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1065  | 192   | 873    | 0      | 18.0%     | $-0.427  | 🔴          |
| Morning (10:00-12:00)  | 564   | 118   | 446    | 0      | 20.9%     | $-0.437  | 🟢          |
| ORB (9:30-10:00)       | 142   | 50    | 92     | 0      | 35.2%     | $0.506   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 142    | 30         | 94         | 18         | 21.1%     | 66.2%     | 12.7%     |
| Morning (10:00-12:00)  | 564    | 91         | 397        | 76         | 16.1%     | 70.4%     | 13.5%     |
| Afternoon (12:00-16:00) | 1065   | 161        | 734        | 170        | 15.1%     | 68.9%     | 16.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.560      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 17     | 7     | 10     | 0      | 41.2%     | $0.574       | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 64     | 24    | 40     | 0      | 37.5%     | $0.634       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 30     | 11    | 19     | 0      | 36.7%     | $0.824       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 23     | 6     | 17     | 0      | 26.1%     | $-0.152      | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 7      | 2     | 5      | 0      | 28.6%     | $0.274       | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 4      | 1     | 3      | 0      | 25.0%     | $0.005       | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 72     | 15    | 57     | 0      | 20.8%     | $-0.342      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 269    | 53    | 216    | 0      | 19.7%     | $-0.564      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 128    | 28    | 100    | 0      | 21.9%     | $-0.471      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 71     | 17    | 54     | 0      | 23.9%     | $0.004       | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 17     | 3     | 14     | 0      | 17.6%     | $-0.533      | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.430      | ⚠️         |
| Morning (10:00-12:00)  | 100%       | 1      | 1     | 0      | 0      | 100.0%    | $1.850       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 5      | 0     | 5      | 0      | 0.0%      | $-1.528      | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 165    | 44    | 121    | 0      | 26.7%     | $0.157       | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 505    | 99    | 406    | 0      | 19.6%     | $-0.412      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 229    | 27    | 202    | 0      | 11.8%     | $-0.832      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 128    | 18    | 110    | 0      | 14.1%     | $-0.392      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 30     | 4     | 26     | 0      | 13.3%     | $-0.677      | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.610      | ⚠️         |
| Afternoon (12:00-16:00) | 100%       | 2      | 0     | 2      | 0      | 0.0%      | $-1.425      | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1050  | 112   | 938    | 0      | 10.7%     | $-0.825  |
| SHORT        | 721   | 248   | 473    | 0      | 34.4%     | $0.330   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 267   | 13    | 254    | 0      | 4.9%      | $-0.662  |
| Long (30-60 min)       | 312   | 118   | 194    | 0      | 37.8%     | $0.056   |
| Medium (5-15 min)      | 424   | 73    | 351    | 0      | 17.2%     | $-0.176  |
| Slow (15-30 min)       | 307   | 86    | 221    | 0      | 28.0%     | $0.060   |
| Very Fast (<1 min)     | 51    | 3     | 48     | 0      | 5.9%      | $-0.796  |
| Very Long (>1h)        | 410   | 67    | 343    | 0      | 16.3%     | $-0.909  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 20.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.36 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (26.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.36) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $0.04) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (35.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3305s / 55.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_divergence_scalper

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,770  |  **Win Rate:** 36.6%  |  **Avg P&L (resolved):** $-0.233  |  **Avg P&L (all):** $-0.233  |  **Avg Hold:** 2254s (37.6m)  |  **Median Hold:** 748s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 6     | 5     | 1      | 0      | 83.3%     | $1.665   | $1.665   | 108.7%   |
| 20-29%         | 124   | 58    | 66     | 0      | 46.8%     | $0.174   | $0.174   | 17.0%    |
| 30-39%         | 662   | 242   | 420    | 0      | 36.6%     | $-0.401  | $-0.401  | -8.7%    |
| 40-49%         | 679   | 235   | 444    | 0      | 34.6%     | $-0.182  | $-0.182  | -13.5%   |
| 50-59%         | 257   | 97    | 160    | 0      | 37.7%     | $-0.125  | $-0.125  | -5.7%    |
| 60-69%         | 42    | 10    | 32     | 0      | 23.8%     | $-0.528  | $-0.528  | -40.3%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1770  | 647   | 1123   | 0      | 36.6%     | $-0.233  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 465   | 75    | 390    | 0      | 16.1%     | $-1.225  |
| Positive Gamma (Range-Bound friendly) | 1305  | 572   | 733    | 0      | 43.8%     | $0.121   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 62    | 33    | 29     | 0      | 53.2%     | $0.740   |
| Time Held: 30-90m      | 264   | 93    | 171    | 0      | 35.2%     | $-0.539  |
| Time Held: 90-240m     | 116   | 3     | 113    | 0      | 2.6%      | $-2.128  |
| Time Held: <30m        | 1321  | 518   | 803    | 0      | 39.2%     | $-0.040  |
| Time Held: >480m       | 7     | 0     | 7      | 0      | 0.0%      | $-2.230  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1048  | 357   | 691    | 0      | 34.1%     | $-0.328  | 🔴          |
| Morning (10:00-12:00)  | 576   | 224   | 352    | 0      | 38.9%     | $-0.182  | 🟢          |
| ORB (9:30-10:00)       | 146   | 66    | 80     | 0      | 45.2%     | $0.254   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 146    | 0          | 34         | 112        | 0.0%      | 23.3%     | 76.7%     |
| Morning (10:00-12:00)  | 576    | 0          | 109        | 467        | 0.0%      | 18.9%     | 81.1%     |
| Afternoon (12:00-16:00) | 1048   | 0          | 156        | 892        | 0.0%      | 14.9%     | 85.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 4      | 1     | 3      | 0      | 25.0%     | $-0.210      | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 47     | 32    | 15     | 0      | 68.1%     | $1.251       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 61     | 22    | 39     | 0      | 36.1%     | $-0.113      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 28     | 11    | 17     | 0      | 39.3%     | $-0.215      | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 6      | 0     | 6      | 0      | 0.0%      | $-1.333      | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 1      | 1     | 0      | 0      | 100.0%    | $2.300       | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 41     | 17    | 24     | 0      | 41.5%     | $-0.189      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 203    | 88    | 115    | 0      | 43.3%     | $-0.140      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 222    | 76    | 146    | 0      | 34.2%     | $-0.215      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 96     | 37    | 59     | 0      | 38.5%     | $-0.174      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 13     | 5     | 8      | 0      | 38.5%     | $-0.517      | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 5      | 4     | 1      | 0      | 80.0%     | $1.538       | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 79     | 40    | 39     | 0      | 50.6%     | $0.381       | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 412    | 122   | 290    | 0      | 29.6%     | $-0.718      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 396    | 137   | 259    | 0      | 34.6%     | $-0.174      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 133    | 49    | 84     | 0      | 36.8%     | $-0.070      | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 23     | 5     | 18     | 0      | 21.7%     | $-0.325      | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1063  | 245   | 818    | 0      | 23.0%     | $-0.709  |
| SHORT        | 707   | 402   | 305    | 0      | 56.9%     | $0.484   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 356   | 92    | 264    | 0      | 25.8%     | $-0.318  |
| Long (30-60 min)       | 207   | 76    | 131    | 0      | 36.7%     | $-0.472  |
| Medium (5-15 min)      | 551   | 245   | 306    | 0      | 44.5%     | $0.096   |
| Slow (15-30 min)       | 338   | 161   | 177    | 0      | 47.6%     | $0.108   |
| Very Fast (<1 min)     | 76    | 20    | 56     | 0      | 26.3%     | $-0.380  |
| Very Long (>1h)        | 242   | 53    | 189    | 0      | 21.9%     | $-1.080  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.23 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (83.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (23.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.23) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $0.74) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (45.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2254s / 37.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_diversity_conviction

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 1,350  |  **Win Rate:** 30.1%  |  **Avg P&L (resolved):** $-0.373  |  **Avg P&L (all):** $-0.373  |  **Avg Hold:** 7267s (121.1m)  |  **Median Hold:** 4171s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 194   | 75    | 119    | 0      | 38.7%     | $0.369   | $0.369   | 16.0%    |
| 40-49%         | 358   | 135   | 223    | 0      | 37.7%     | $-0.259  | $-0.259  | 13.1%    |
| 50-59%         | 561   | 150   | 411    | 0      | 26.7%     | $-0.558  | $-0.558  | -19.8%   |
| 60-69%         | 170   | 33    | 137    | 0      | 19.4%     | $-0.820  | $-0.820  | -41.8%   |
| 70-79%         | 56    | 10    | 46     | 0      | 17.9%     | $-0.808  | $-0.808  | -46.5%   |
| 80-89%         | 11    | 4     | 7      | 0      | 36.4%     | $1.371   | $1.371   | 9.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1350  | 407   | 943    | 0      | 30.1%     | $-0.373  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 262   | 86    | 176    | 0      | 32.8%     | $-0.051  |
| Positive Gamma (Range-Bound friendly) | 1088  | 321   | 767    | 0      | 29.5%     | $-0.451  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 98    | 66    | 32     | 0      | 67.3%     | $1.966   |
| Time Held: 30-90m      | 444   | 98    | 346    | 0      | 22.1%     | $-0.680  |
| Time Held: 90-240m     | 462   | 166   | 296    | 0      | 35.9%     | $-0.045  |
| Time Held: <30m        | 320   | 51    | 269    | 0      | 15.9%     | $-1.548  |
| Time Held: >480m       | 26    | 26    | 0      | 0      | 100.0%    | $4.660   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 757   | 212   | 545    | 0      | 28.0%     | $-0.510  | 🔴          |
| Morning (10:00-12:00)  | 457   | 137   | 320    | 0      | 30.0%     | $-0.309  | 🔴          |
| ORB (9:30-10:00)       | 136   | 58    | 78     | 0      | 42.6%     | $0.168   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 136    | 6          | 66         | 64         | 4.4%      | 48.5%     | 47.1%     |
| Morning (10:00-12:00)  | 457    | 30         | 245        | 182        | 6.6%      | 53.6%     | 39.8%     |
| Afternoon (12:00-16:00) | 757    | 31         | 420        | 306        | 4.1%      | 55.5%     | 40.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 22     | 18    | 4      | 0      | 81.8%     | $4.793       | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 42     | 21    | 21     | 0      | 50.0%     | $0.701       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 50     | 12    | 38     | 0      | 24.0%     | $-2.066      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 16     | 6     | 10     | 0      | 37.5%     | $0.001       | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 5      | 1     | 4      | 0      | 20.0%     | $-1.436      | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.650      | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 63     | 30    | 33     | 0      | 47.6%     | $1.002       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 119    | 42    | 77     | 0      | 35.3%     | $-0.164      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 180    | 42    | 138    | 0      | 23.3%     | $-0.777      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 65     | 15    | 50     | 0      | 23.1%     | $-0.629      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 27     | 7     | 20     | 0      | 25.9%     | $-0.326      | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 3      | 1     | 2      | 0      | 33.3%     | $1.617       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 109    | 27    | 82     | 0      | 24.8%     | $-0.890      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 197    | 72    | 125    | 0      | 36.5%     | $-0.522      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 331    | 96    | 235    | 0      | 29.0%     | $-0.212      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 89     | 12    | 77     | 0      | 13.5%     | $-1.107      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 24     | 2     | 22     | 0      | 8.3%      | $-1.221      | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 7      | 3     | 4      | 0      | 42.9%     | $1.697       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 838   | 72    | 766    | 0      | 8.6%      | $-1.874  |
| SHORT        | 512   | 335   | 177    | 0      | 65.4%     | $2.083   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 24    | 4     | 20     | 0      | 16.7%     | $-1.904  |
| Long (30-60 min)       | 285   | 45    | 240    | 0      | 15.8%     | $-1.060  |
| Medium (5-15 min)      | 133   | 14    | 119    | 0      | 10.5%     | $-1.779  |
| Slow (15-30 min)       | 162   | 33    | 129    | 0      | 20.4%     | $-1.311  |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-0.790  |
| Very Long (>1h)        | 745   | 311   | 434    | 0      | 41.7%     | $0.394   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.37 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (38.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (17.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.37) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $4.66) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (42.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (7267s / 121.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### prob_weighted_magnet

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 2,700  |  **Win Rate:** 20.1%  |  **Avg P&L (resolved):** $-0.487  |  **Avg P&L (all):** $-0.487  |  **Avg Hold:** 4194s (69.9m)  |  **Median Hold:** 2236s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 852   | 88    | 764    | 0      | 10.3%     | $-0.740  | $-0.740  | -58.7%   |
| 40-49%         | 1848  | 454   | 1394   | 0      | 24.6%     | $-0.371  | $-0.371  | -1.7%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1673  | 324   | 1349   | 0      | 19.4%     | $-0.496  |
| Trending (Up)        | 1027  | 218   | 809    | 0      | 21.2%     | $-0.473  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2700  | 542   | 2158   | 0      | 20.1%     | $-0.487  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 126   | 54    | 72     | 0      | 42.9%     | $-0.448  |
| Time Held: 30-90m      | 768   | 171   | 597    | 0      | 22.3%     | $0.043   |
| Time Held: 90-240m     | 613   | 199   | 414    | 0      | 32.5%     | $-0.462  |
| Time Held: <30m        | 1193  | 118   | 1075   | 0      | 9.9%      | $-0.846  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1481  | 268   | 1213   | 0      | 18.1%     | $-0.528  | 🔴          |
| Morning (10:00-12:00)  | 952   | 187   | 765    | 0      | 19.6%     | $-0.654  | 🔴          |
| ORB (9:30-10:00)       | 267   | 87    | 180    | 0      | 32.6%     | $0.331   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 267    | 0          | 0          | 267        | 0.0%      | 0.0%      | 100.0%    |
| Morning (10:00-12:00)  | 952    | 0          | 0          | 952        | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 1481   | 0          | 0          | 1481       | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 86     | 40    | 46     | 0      | 46.5%     | $2.014       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 181    | 47    | 134    | 0      | 26.0%     | $-0.469      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 267    | 22    | 245    | 0      | 8.2%      | $-0.968      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 685    | 165   | 520    | 0      | 24.1%     | $-0.531      | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 499    | 26    | 473    | 0      | 5.2%      | $-1.092      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 982    | 242   | 740    | 0      | 24.6%     | $-0.242      | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1596  | 90    | 1506   | 0      | 5.6%      | $-1.362  |
| SHORT        | 1104  | 452   | 652    | 0      | 40.9%     | $0.777   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 189   | 4     | 185    | 0      | 2.1%      | $-1.564  |
| Long (30-60 min)       | 480   | 96    | 384    | 0      | 20.0%     | $0.094   |
| Medium (5-15 min)      | 441   | 34    | 407    | 0      | 7.7%      | $-0.975  |
| Slow (15-30 min)       | 539   | 80    | 459    | 0      | 14.8%     | $-0.459  |
| Very Fast (<1 min)     | 24    | 0     | 24     | 0      | 0.0%      | $-1.503  |
| Very Long (>1h)        | 1027  | 328   | 699    | 0      | 31.9%     | $-0.343  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 20.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.49 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (24.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (10.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.47) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.04) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (32.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4194s / 69.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### strike_concentration

**Symbols:** AMD, INTC, NVDA, SPY  |  **Total Signals:** 248  |  **Win Rate:** 41.1%  |  **Avg P&L (resolved):** $-0.685  |  **Avg P&L (all):** $-0.685  |  **Avg Hold:** 3981s (66.3m)  |  **Median Hold:** 1269s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 4     | 1     | 3      | 0      | 25.0%     | $-2.538  | $-2.538  | -61.8%   |
| 30-39%         | 55    | 10    | 45     | 0      | 18.2%     | $-2.288  | $-2.288  | -60.4%   |
| 40-49%         | 86    | 31    | 55     | 0      | 36.0%     | $-0.988  | $-0.988  | -14.0%   |
| 50-59%         | 78    | 46    | 32     | 0      | 59.0%     | $0.474   | $0.474   | 42.2%    |
| 60-69%         | 25    | 14    | 11     | 0      | 56.0%     | $0.568   | $0.568   | 39.4%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 139   | 67    | 72     | 0      | 48.2%     | $-0.108  |
| Trending (Up)        | 109   | 35    | 74     | 0      | 32.1%     | $-1.419  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 248   | 102   | 146    | 0      | 41.1%     | $-0.685  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 36    | 8     | 28     | 0      | 22.2%     | $-2.222  |
| Time Held: 30-90m      | 58    | 26    | 32     | 0      | 44.8%     | $-0.722  |
| Time Held: 90-240m     | 3     | 3     | 0      | 0      | 100.0%    | $1.587   |
| Time Held: <30m        | 149   | 63    | 86     | 0      | 42.3%     | $-0.422  |
| Time Held: >480m       | 2     | 2     | 0      | 0      | 100.0%    | $5.110   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 117   | 59    | 58     | 0      | 50.4%     | $-0.221  | 🟢          |
| Morning (10:00-12:00)  | 82    | 26    | 56     | 0      | 31.7%     | $-1.091  | 🔴          |
| ORB (9:30-10:00)       | 49    | 17    | 32     | 0      | 34.7%     | $-1.113  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 49     | 0          | 23         | 26         | 0.0%      | 46.9%     | 53.1%     |
| Morning (10:00-12:00)  | 82     | 0          | 29         | 53         | 0.0%      | 35.4%     | 64.6%     |
| Afternoon (12:00-16:00) | 117    | 0          | 51         | 66         | 0.0%      | 43.6%     | 56.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 3      | 0     | 3      | 0      | 0.0%      | $-4.490      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 23     | 4     | 19     | 0      | 17.4%     | $-2.836      | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 18     | 10    | 8      | 0      | 55.6%     | $1.305       | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 5      | 3     | 2      | 0      | 60.0%     | $0.136       | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 2      | 0     | 2      | 0      | 0.0%      | $-4.050      | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 26     | 5     | 21     | 0      | 19.2%     | $-2.354      | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 25     | 11    | 14     | 0      | 44.0%     | $-0.012      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 26     | 7     | 19     | 0      | 26.9%     | $-1.147      | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 3      | 3     | 0      | 0      | 100.0%    | $3.330       | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 2      | 1     | 1      | 0      | 50.0%     | $-1.025      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 26     | 5     | 21     | 0      | 19.2%     | $-1.968      | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 38     | 16    | 22     | 0      | 42.1%     | $-0.512      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 34     | 29    | 5      | 0      | 85.3%     | $1.274       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 17     | 8     | 9      | 0      | 47.1%     | $0.207       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 129   | 33    | 96     | 0      | 25.6%     | $-1.701  |
| SHORT        | 119   | 69    | 50     | 0      | 58.0%     | $0.417   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 47    | 17    | 30     | 0      | 36.2%     | $-0.653  |
| Long (30-60 min)       | 39    | 20    | 19     | 0      | 51.3%     | $-0.471  |
| Medium (5-15 min)      | 51    | 24    | 27     | 0      | 47.1%     | $0.017   |
| Slow (15-30 min)       | 42    | 20    | 22     | 0      | 47.6%     | $-0.546  |
| Very Fast (<1 min)     | 9     | 2     | 7      | 0      | 22.2%     | $-1.133  |
| Very Long (>1h)        | 60    | 19    | 41     | 0      | 31.7%     | $-1.474  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 41.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.68 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (59.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (18.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.11) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-0.42) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (50.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3981s / 66.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### theta_burn

**Symbols:** TSLA  |  **Total Signals:** 44  |  **Win Rate:** 2.3%  |  **Avg P&L (resolved):** $-0.186  |  **Avg P&L (all):** $-0.186  |  **Avg Hold:** 424s (7.1m)  |  **Median Hold:** 9s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 5     | 0     | 5      | 0      | 0.0%      | $0.072   | $0.072   | 60.0%    |
| 20-29%         | 5     | 0     | 5      | 0      | 0.0%      | $-0.812  | $-0.812  | -100.0%  |
| 30-39%         | 33    | 1     | 32     | 0      | 3.0%      | $-0.141  | $-0.141  | -7.5%    |
| 40-49%         | 1     | 0     | 1      | 0      | 0.0%      | $0.170   | $0.170   | 100.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 31    | 0     | 31     | 0      | 0.0%      | $-0.199  |
| Trending (Up)        | 13    | 1     | 12     | 0      | 7.7%      | $-0.155  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 44    | 1     | 43     | 0      | 2.3%      | $-0.186  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1     | 0     | 1      | 0      | 0.0%      | $-1.050  |
| Time Held: <30m        | 43    | 1     | 42     | 0      | 2.3%      | $-0.166  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 42    | 1     | 41     | 0      | 2.4%      | $-0.208  | 🟢          |
| Morning (10:00-12:00)  | 2     | 0     | 2      | 0      | 0.0%      | $0.290   | ⚠️         |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 2      | 0          | 0          | 2          | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 42     | 0          | 0          | 42         | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Morning (10:00-12:00)  | 10-19%     | 2      | 0     | 2      | 0      | 0.0%      | $0.290       | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 3      | 0     | 3      | 0      | 0.0%      | $-0.073      | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 5      | 0     | 5      | 0      | 0.0%      | $-0.812      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 33     | 1     | 32     | 0      | 3.0%      | $-0.141      | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 1      | 0     | 1      | 0      | 0.0%      | $0.170       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| SHORT        | 44    | 1     | 43     | 0      | 2.3%      | $-0.186  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 3     | 0     | 3      | 0      | 0.0%      | $-0.117  |
| Medium (5-15 min)      | 9     | 1     | 8      | 0      | 11.1%     | $-0.567  |
| Slow (15-30 min)       | 8     | 0     | 8      | 0      | 0.0%      | $-0.834  |
| Very Fast (<1 min)     | 23    | 0     | 23     | 0      | 0.0%      | $0.217   |
| Very Long (>1h)        | 1     | 0     | 1      | 0      | 0.0%      | $-1.050  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 2.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.19 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (3.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.15) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-0.17) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (2.4% win rate) — statistically significant above overall WR.

---

### vol_compression_range

**Symbols:** AMD, INTC, NVDA, SPY, TSLA  |  **Total Signals:** 149  |  **Win Rate:** 31.5%  |  **Avg P&L (resolved):** $-0.742  |  **Avg P&L (all):** $-0.742  |  **Avg Hold:** 5640s (94.0m)  |  **Median Hold:** 3203s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 14    | 4     | 10     | 0      | 28.6%     | $-0.924  | $-0.924  | -28.6%   |
| 30-39%         | 34    | 9     | 25     | 0      | 26.5%     | $-1.434  | $-1.434  | -33.8%   |
| 40-49%         | 41    | 6     | 35     | 0      | 14.6%     | $-1.223  | $-1.223  | -63.4%   |
| 50-59%         | 26    | 10    | 16     | 0      | 38.5%     | $-0.242  | $-0.242  | -3.9%    |
| 60-69%         | 21    | 13    | 8      | 0      | 61.9%     | $0.030   | $0.030   | 54.7%    |
| 70-79%         | 13    | 5     | 8      | 0      | 38.5%     | $0.536   | $0.536   | -4.0%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 103   | 27    | 76     | 0      | 26.2%     | $-1.312  |
| Trending (Up)        | 46    | 20    | 26     | 0      | 43.5%     | $0.535   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 149   | 47    | 102    | 0      | 31.5%     | $-0.742  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 15    | 2     | 13     | 0      | 13.3%     | $-2.432  |
| Time Held: 30-90m      | 47    | 24    | 23     | 0      | 51.1%     | $-0.128  |
| Time Held: 90-240m     | 34    | 3     | 31     | 0      | 8.8%      | $-1.588  |
| Time Held: <30m        | 52    | 17    | 35     | 0      | 32.7%     | $-0.397  |
| Time Held: >480m       | 1     | 1     | 0      | 0      | 100.0%    | $6.610   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 56    | 31    | 25     | 0      | 55.4%     | $0.406   | 🟢          |
| Morning (10:00-12:00)  | 53    | 3     | 50     | 0      | 5.7%      | $-1.928  | 🔴          |
| ORB (9:30-10:00)       | 40    | 13    | 27     | 0      | 32.5%     | $-0.775  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 40     | 3          | 13         | 24         | 7.5%      | 32.5%     | 60.0%     |
| Morning (10:00-12:00)  | 53     | 3          | 13         | 37         | 5.7%      | 24.5%     | 69.8%     |
| Afternoon (12:00-16:00) | 56     | 7          | 21         | 28         | 12.5%     | 37.5%     | 50.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 3      | 0     | 3      | 0      | 0.0%      | $-3.603      | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 10     | 3     | 7      | 0      | 30.0%     | $-1.204      | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 11     | 2     | 9      | 0      | 18.2%     | $-0.410      | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 4      | 2     | 2      | 0      | 50.0%     | $-0.135      | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 9      | 4     | 5      | 0      | 44.4%     | $-1.388      | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 3      | 2     | 1      | 0      | 66.7%     | $3.127       | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 6      | 1     | 5      | 0      | 16.7%     | $-2.037      | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 10     | 0     | 10     | 0      | 0.0%      | $-3.428      | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 21     | 2     | 19     | 0      | 9.5%      | $-1.631      | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 12     | 0     | 12     | 0      | 0.0%      | $-1.402      | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.150      | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 3      | 0     | 3      | 0      | 0.0%      | $-1.160      | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 5      | 3     | 2      | 0      | 60.0%     | $2.018       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 14     | 6     | 8      | 0      | 42.9%     | $-0.174      | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 9      | 2     | 7      | 0      | 22.2%     | $-1.263      | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 10     | 8     | 2      | 0      | 80.0%     | $1.108       | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 11     | 9     | 2      | 0      | 81.8%     | $1.298       | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 7      | 3     | 4      | 0      | 42.9%     | $0.153       | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 105   | 10    | 95     | 0      | 9.5%      | $-2.329  |
| SHORT        | 44    | 37    | 7      | 0      | 84.1%     | $3.046   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 5     | 0     | 5      | 0      | 0.0%      | $-2.138  |
| Long (30-60 min)       | 29    | 15    | 14     | 0      | 51.7%     | $-0.736  |
| Medium (5-15 min)      | 21    | 5     | 16     | 0      | 23.8%     | $-0.748  |
| Slow (15-30 min)       | 26    | 12    | 14     | 0      | 46.2%     | $0.222   |
| Very Long (>1h)        | 68    | 15    | 53     | 0      | 22.1%     | $-1.008  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.74 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (61.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (14.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.53) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $-0.13) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (55.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (5640s / 94.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

---

## Statistical Edge Anomalies (Phase 1)

Strategies that statistically deviate from the global win-rate baseline within
specific confidence buckets. Flagged when lift > 50% above global OR > 1.5 sigma.

---

## Temporal Burst Events (Phase 2)

High-frequency bursts where multiple independent strategies fire simultaneously,
indicating multi-factor market events. Window: 10 seconds.

### Top Temporal Bursts

| Timestamp (s)  | Count  | Strategies | Coincidence  | Reason                                   |
+----------------+--------+----------+--------------+------------------------------------------+
| 1784571606.461 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 16           | DOWN trend exhausted: delta declining (below av... |
| 1784572463.929 | 21     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, theta_burn | 16           | ROBUST_SHORT SHORT: frag_bid=0.147 frag_ask=0.1... |
| 1784555123.989 | 22     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration | 15           | ROBUST_SHORT SHORT: frag=0.100/0.096 decay=-0.8... |
| 1784555154.986 | 22     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | ROBUST_SHORT SHORT: frag_bid=0.175 frag_ask=0.1... |
| 1784555186.206 | 23     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 15           | ROBUST_LONG LONG: frag_bid=0.125 frag_ask=0.170... |
| 1784572843.76  | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Call flow dominant (ratio=4.2×): call score 545... |
| 1784547619.188 | 23     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 14           | Squeeze LONG: breakout through call wall at 385... |
| 1784551119.961 | 20     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 14           | DOWN trend exhausted: delta declining (below av... |
| 1784555242.969 | 19     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration, vol_compression_range | 14           | Exchange flow LONG: VSI=3.00 (+200.0%), ROC=+2.... |
| 1784555368.531 | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 14           | Exchange flow LONG: VSI=2.70 (+170.0%), ROC=+2.... |
| 1784555733.185 | 18     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 14           | Velocity-Magnet LONG: delta accelerating at 500... |
| 1784559790.871 | 17     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | Squeeze LONG: breakout through call wall at 205... |
| 1784571080.107 | 15     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 14           | Magnet pull LONG: price 98.61 below magnet 100.... |
| 1784572763.796 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_squeeze, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, theta_burn | 14           | Call flow dominant (ratio=4.6×): call score 170... |
| 1784572887.175 | 18     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, theta_burn, vol_compression_range | 14           | Depth imbalance SHORT: IR=0.46 (+54.0%), ROC=-0... |
| 1784534400.706 | 39     | confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | Call wall at 744.0 rejected price, GEX=-1918846... |
| 1784535616.462 | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_imbalance, magnet_accelerate, participant_diversity_conviction, prob_weighted_magnet | 13           | Squeeze SHORT: breakout through put wall at 502... |
| 1784535676.5   | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Confluence LONG at 380: 2 structural signals, t... |
| 1784545201.734 | 15     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 13           | Exchange flow LONG: VSI=2.64 (+164.4%), ROC=+1.... |
| 1784546775.861 | 21     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 13           | Depth decay SHORT: ROC=-0.2415 (-24.15%), vol/d... |
| 1784548944.405 | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 13           | ROBUST_SHORT SHORT: frag=0.167/0.200 decay=+0.0... |
| 1784551240.684 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Participant conviction LONG: participants=1.4, ... |
| 1784554218.416 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, participant_diversity_conviction | 13           | Call flow dominant (ratio=4.0×): call score 193... |
| 1784554607.269 | 21     | confluence_reversal, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | ROBUST_SHORT SHORT: frag=0.054/0.080 decay=+0.0... |
| 1784554910.42  | 20     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, strike_concentration, vol_compression_range | 13           | Depth decay SHORT: ROC=-0.2105 (-21.05%), vol/d... |
| 1784555001.708 | 19     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration, vol_compression_range | 13           | Depth decay LONG: ROC=-0.1880 (-18.80%), vol/de... |
| 1784555429.149 | 21     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | Exchange flow SHORT: VSI=0.15 (+85.0%), ROC=-0.... |
| 1784555461.373 | 24     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | DOWN trend exhausted: delta declining (below av... |
| 1784555522.143 | 21     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | DOWN trend exhausted: delta declining (below av... |
| 1784556405.628 | 21     | call_put_flow_asymmetry, confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, strike_concentration | 13           | Flow imbalance LONG: AggVSI=0.940 (+94.0%), ROC... |
| 1784565574.439 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | Exchange flow LONG: VSI=8.25 (+725.0%), ROC=+0.... |
| 1784570699.986 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 13           | ROBUST_LONG LONG: frag_bid=0.114 frag_ask=0.085... |
| 1784571485.778 | 17     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1784571783.859 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | GEX divergence (bullish): price falling but GEX... |
| 1784572405.747 | 17     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Participant conviction SHORT: participants=1.6,... |
| 1784576703.856 | 17     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 13           | Squeeze LONG: breakout through call wall at 507... |
| 1784534474.858 | 18     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper | 12           | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1784547662.059 | 21     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 12           | ROBUST_LONG LONG: frag_bid=0.111 frag_ask=0.200... |
| 1784548193.265 | 15     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, participant_divergence_scalper, participant_diversity_conviction | 12           | ROBUST_LONG LONG: frag=0.120/0.150 decay=-0.300... |
| 1784548779.057 | 18     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, order_book_fragmentation, prob_weighted_magnet, strike_concentration | 12           | DOWN trend exhausted: delta declining (below av... |
| 1784549763.805 | 21     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper | 12           | ROBUST_LONG LONG: frag_bid=0.143 frag_ask=0.150... |
| 1784549818.422 | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 12           | Depth imbalance LONG: IR=3.76 (+276.0%), ROC=+0... |
| 1784551604.092 | 20     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 12           | UP trend exhausted: delta declining (below avg)... |
| 1784552399.909 | 18     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration | 12           | Call flow dominant (ratio=4.0×): call score 144... |
| 1784552957.849 | 18     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_diversity_conviction, strike_concentration | 12           | Participant conviction LONG: participants=1.8, ... |
| 1784554075.247 | 25     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gex_divergence, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 12           | ROBUST_SHORT SHORT: frag=0.173/0.143 decay=+1.4... |
| 1784554277.89  | 21     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, participant_diversity_conviction, prob_weighted_magnet | 12           | Exchange flow LONG: VSI=3.38 (+237.9%), ROC=+1.... |
| 1784554399.075 | 19     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, participant_diversity_conviction, prob_weighted_magnet | 12           | Velocity-Magnet SHORT: delta accelerating at 52... |
| 1784554543.643 | 19     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper | 12           | UP trend exhausted: delta declining (below avg)... |
| 1784554566.246 | 20     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 12           | Velocity-Magnet LONG: delta accelerating at 360... |

**8329 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 31,205   | 13         | net_gamma=< 24.02      | 25.9%    | $-0.754    |
| Volume Spike                 | 5,911    | 2          | vol_ratio=0.5          | 28.7%    | $-0.230    |
| IV Expansion                 | 4,546    | 2          | iv_skew=< 0.15         | 22.5%    | $-1.915    |
| Gamma Wall Support (744.0)   | 2,037    | 3          | wall_strike=744.0      | 3.2%     | $-3.355    |
| Gamma Wall Support (200.0)   | 723      | 4          | wall_strike=200.0      | 72.5%    | $1.188     |
| Gamma Wall Support (492.5)   | 691      | 4          | wall_strike=492.5      | 12.0%    | $-1.840    |
| Gamma Wall Support (97.0)    | 332      | 4          | wall_strike=97.0       | 10.8%    | $-0.346    |
| Gamma Wall Support (385.0)   | 298      | 5          | wall_strike=385.0      | 36.9%    | $0.112     |
| Gamma Wall Support (522.5)   | 71       | 3          | wall_strike=522.5      | 33.8%    | $-0.027    |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 11605  | 10     | 10       | 10.3%    | $-1.577    | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 11607  | 9      | 9        | 42.7%    | $0.376     | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 5380   | 6      | 6        | 16.5%    | $-1.922    | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Exposur  | 2613   | 5      | 5        | 39.6%    | $0.291     | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 298    | 5      | 5        | 36.9%    | $0.112     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 723    | 4      | 4        | 72.5%    | $1.188     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 691    | 4      | 4        | 12.0%    | $-1.840    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 332    | 4      | 4        | 10.8%    | $-0.346    | wall_stri  | gamma_squeeze, gamma_wall_bounce, theta  |
| Gamma Wall Su  | 71     | 3      | 3        | 33.8%    | $-0.027    | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 2037   | 3      | 3        | 3.2%     | $-3.355    | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Volume Spike   | 5911   | 2      | 2        | 28.7%    | $-0.230    | vol_ratio  | order_book_fragmentation, participant_d  |
| IV Expansion   | 4546   | 2      | 2        | 22.5%    | $-1.915    | iv_skew=<  | call_put_flow_asymmetry, iv_gex_diverge  |

**12 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 5-9%           | 318      | 88     | 230    | 0      | 27.7%     | 18.2      |
| 10-19%         | 1555     | 398    | 1157   | 0      | 25.6%     | 26.0      |
| 20-29%         | 2524     | 624    | 1900   | 0      | 24.7%     | 17.9      |
| 30-39%         | 4537     | 1175   | 3362   | 0      | 25.9%     | 17.4      |
| 40-49%         | 4778     | 1404   | 3374   | 0      | 29.4%     | 16.9      |
| 50-59%         | 4326     | 1380   | 2946   | 0      | 31.9%     | 16.1      |
| 60-69%         | 2742     | 746    | 1996   | 0      | 27.2%     | 17.9      |
| 70-79%         | 1020     | 294    | 726    | 0      | 28.8%     | 22.7      |
| 80-89%         | 870      | 211    | 659    | 0      | 24.3%     | 27.7      |
| 90-99%         | 12       | 8      | 4      | 0      | 66.7%     | 0.0       |
| 100%           | 59       | 35     | 24     | 0      | 59.3%     | 0.0       |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| ORB (9:30-10:00)       | 2464     | 892    | 1572   | 0      | 36.2%     | 11.8     |
| Morning (10:00-12:00)  | 7643     | 2167   | 5476   | 0      | 28.4%     | 13.3     |
| Afternoon (12:00-16:00) | 12634    | 3304   | 9330   | 0      | 26.2%     | 14.3     |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| ORB (9:30-10:00)       | 5-9%         | 38       | 13     | 25     | 0      | 34.2%     |
| ORB (9:30-10:00)       | 10-19%       | 182      | 49     | 133    | 0      | 26.9%     |
| ORB (9:30-10:00)       | 20-29%       | 239      | 90     | 149    | 0      | 37.7%     |
| ORB (9:30-10:00)       | 30-39%       | 429      | 178    | 251    | 0      | 41.5%     |
| ORB (9:30-10:00)       | 40-49%       | 540      | 174    | 366    | 0      | 32.2%     |
| ORB (9:30-10:00)       | 50-59%       | 456      | 190    | 266    | 0      | 41.7%     |
| ORB (9:30-10:00)       | 60-69%       | 281      | 86     | 195    | 0      | 30.6%     |
| ORB (9:30-10:00)       | 70-79%       | 105      | 29     | 76     | 0      | 27.6%     |
| ORB (9:30-10:00)       | 80-89%       | 129      | 41     | 88     | 0      | 31.8%     |
| ORB (9:30-10:00)       | 100%         | 56       | 34     | 22     | 0      | 60.7%     |
| Morning (10:00-12:00)  | 5-9%         | 123      | 33     | 90     | 0      | 26.8%     |
| Morning (10:00-12:00)  | 10-19%       | 622      | 170    | 452    | 0      | 27.3%     |
| Morning (10:00-12:00)  | 20-29%       | 924      | 242    | 682    | 0      | 26.2%     |
| Morning (10:00-12:00)  | 30-39%       | 1450     | 402    | 1048   | 0      | 27.7%     |
| Morning (10:00-12:00)  | 40-49%       | 1581     | 445    | 1136   | 0      | 28.1%     |
| Morning (10:00-12:00)  | 50-59%       | 1419     | 433    | 986    | 0      | 30.5%     |
| Morning (10:00-12:00)  | 60-69%       | 853      | 268    | 585    | 0      | 31.4%     |
| Morning (10:00-12:00)  | 70-79%       | 357      | 109    | 248    | 0      | 30.5%     |
| Morning (10:00-12:00)  | 80-89%       | 311      | 64     | 247    | 0      | 20.6%     |
| Afternoon (12:00-16:00) | 5-9%         | 157      | 42     | 115    | 0      | 26.8%     |
| Afternoon (12:00-16:00) | 10-19%       | 751      | 179    | 572    | 0      | 23.8%     |
| Afternoon (12:00-16:00) | 20-29%       | 1361     | 292    | 1069   | 0      | 21.5%     |
| Afternoon (12:00-16:00) | 30-39%       | 2658     | 595    | 2063   | 0      | 22.4%     |
| Afternoon (12:00-16:00) | 40-49%       | 2657     | 785    | 1872   | 0      | 29.5%     |
| Afternoon (12:00-16:00) | 50-59%       | 2451     | 757    | 1694   | 0      | 30.9%     |
| Afternoon (12:00-16:00) | 60-69%       | 1608     | 392    | 1216   | 0      | 24.4%     |
| Afternoon (12:00-16:00) | 70-79%       | 558      | 156    | 402    | 0      | 28.0%     |
| Afternoon (12:00-16:00) | 80-89%       | 430      | 106    | 324    | 0      | 24.7%     |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] gamma_wall_bounce | 80-89%       | 100.0%    | 24.3%     | 312%     | 2.74     | 6        | 6        | 0        |
| [ALPHA] participant_divergence_scalper | 10-19%       | 83.3%     | 25.6%     | 226%     | 2.22     | 6        | 5        | 1        |
| [ALPHA] delta_volume_exhaustion | 40-49%       | 87.2%     | 29.4%     | 197%     | 3.42     | 39       | 34       | 5        |
| [ALPHA] gamma_wall_bounce | 70-79%       | 80.0%     | 28.8%     | 178%     | 2.25     | 5        | 4        | 1        |
| [ALPHA] magnet_accelerate | 70-79%       | 74.3%     | 28.8%     | 158%     | 2.00     | 35       | 26       | 9        |
| [ALPHA] depth_imbalance_momentum | 70-79%       | 66.7%     | 28.8%     | 131%     | 1.67     | 21       | 14       | 7        |
| [ALPHA] vol_compression_range | 60-69%       | 61.9%     | 27.2%     | 128%     | 1.94     | 21       | 13       | 8        |
| [ALPHA] delta_volume_exhaustion | 30-39%       | 56.9%     | 25.9%     | 120%     | 1.78     | 160      | 91       | 69       |
| [ALPHA] gamma_wall_bounce | 60-69%       | 57.9%     | 27.2%     | 113%     | 1.71     | 19       | 11       | 8        |
| [ALPHA] depth_imbalance_momentum | 60-69%       | 56.1%     | 27.2%     | 106%     | 1.61     | 66       | 37       | 29       |
| [ALPHA] strike_concentration | 60-69%       | 56.0%     | 27.2%     | 106%     | 1.61     | 25       | 14       | 11       |
| [ALPHA] gex_imbalance    | 60-69%       | 53.7%     | 27.2%     | 97%      | 1.48     | 82       | 44       | 38       |
| [ALPHA] call_put_flow_asymmetry | 30-39%       | 50.0%     | 25.9%     | 93%      | 1.39     | 774      | 387      | 387      |
| [ALPHA] gex_imbalance    | 20-29%       | 47.1%     | 24.7%     | 91%      | 1.26     | 350      | 165      | 185      |
| [ALPHA] depth_imbalance_momentum | 50-59%       | 60.6%     | 31.9%     | 90%      | 1.79     | 297      | 180      | 117      |
| [ALPHA] participant_divergence_scalper | 20-29%       | 46.8%     | 24.7%     | 89%      | 1.24     | 124      | 58       | 66       |
| [ALPHA] strike_concentration | 50-59%       | 59.0%     | 31.9%     | 85%      | 1.68     | 78       | 46       | 32       |
| [ALPHA] depth_imbalance_momentum | 40-49%       | 48.1%     | 29.4%     | 64%      | 1.11     | 156      | 75       | 81       |
| [ALPHA] gex_imbalance    | 50-59%       | 51.3%     | 31.9%     | 61%      | 1.21     | 495      | 254      | 241      |
| [ALPHA] exchange_flow_concentration | 60-69%       | 42.8%     | 27.2%     | 57%      | 0.87     | 257      | 110      | 147      |
| [ALPHA] gex_imbalance    | 40-49%       | 46.2%     | 29.4%     | 57%      | 1.00     | 106      | 49       | 57       |
| [ALPHA] gamma_squeeze    | 30-39%       | 40.4%     | 25.9%     | 56%      | 0.83     | 114      | 46       | 68       |

**22 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 60-69%       | 11      | 10     | 1      | 90.9%    | 24.4%    | 273%   | 2.75    | ⚡ HIGH       |
| [ALPHA] gex_imbalance    | ORB (9:30-10:00) | 10-19%       | 10      | 10     | 0      | 100.0%   | 26.9%    | 271%   | 1.74    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Afternoon (12:00-16:00) | 70-79%       | 6       | 6      | 0      | 100.0%   | 28.0%    | 258%   | 2.22    | ⚡ HIGH       |
| [ALPHA] gex_divergence   | Morning (10:00-12:00) | 80-89%       | 7       | 5      | 2      | 71.4%    | 20.6%    | 247%   | 1.98    | 🔥 STRONG     |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 10-19%       | 5       | 4      | 1      | 80.0%    | 23.8%    | 236%   | 2.09    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 60-69%       | 11      | 9      | 2      | 81.8%    | 24.4%    | 236%   | 2.37    | ⚡ HIGH       |
| [ALPHA] magnet_accelerate | Afternoon (12:00-16:00) | 70-79%       | 13      | 12     | 1      | 92.3%    | 28.0%    | 230%   | 1.99    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | ORB (9:30-10:00) | 80-89%       | 6       | 6      | 0      | 100.0%   | 31.8%    | 215%   | 2.09    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 40-49%       | 14      | 12     | 2      | 85.7%    | 28.1%    | 205%   | 2.98    | ⚡ HIGH       |
| [ALPHA] magnet_accelerate | Morning (10:00-12:00) | 50-59%       | 34      | 31     | 3      | 91.2%    | 30.5%    | 199%   | 2.49    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 40-49%       | 21      | 18     | 3      | 85.7%    | 29.5%    | 190%   | 3.27    | ⚡ HIGH       |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 70-79%       | 5       | 4      | 1      | 80.0%    | 27.6%    | 190%   | 1.91    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 20-29%       | 5       | 3      | 2      | 60.0%    | 21.5%    | 180%   | 1.70    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 50-59%       | 34      | 29     | 5      | 85.3%    | 30.9%    | 176%   | 2.33    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 30-39%       | 82      | 49     | 33     | 59.8%    | 22.4%    | 167%   | 1.95    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 50-59%       | 10      | 8      | 2      | 80.0%    | 30.9%    | 159%   | 2.10    | ⚡ HIGH       |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 20-29%       | 79      | 40     | 39     | 50.6%    | 21.5%    | 136%   | 1.29    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Afternoon (12:00-16:00) | 50-59%       | 129     | 94     | 35     | 72.9%    | 30.9%    | 136%   | 1.80    | 🔥 STRONG     |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 60-69%       | 47      | 27     | 20     | 57.4%    | 24.4%    | 136%   | 1.37    | 🔥 STRONG     |
| [ALPHA] call_put_flow_asymmetry | Afternoon (12:00-16:00) | 30-39%       | 476     | 238    | 238    | 50.0%    | 22.4%    | 123%   | 1.44    | 🔥 STRONG     |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 20-29%       | 177     | 84     | 93     | 47.5%    | 21.5%    | 121%   | 1.15    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 40-49%       | 20      | 14     | 6      | 70.0%    | 32.2%    | 117%   | 2.04    | ⚡ HIGH       |
| [ALPHA] magnet_accelerate | Morning (10:00-12:00) | 70-79%       | 22      | 14     | 8      | 63.6%    | 30.5%    | 108%   | 2.39    | ⚡ HIGH       |
| [ALPHA] gamma_squeeze    | Morning (10:00-12:00) | 30-39%       | 33      | 19     | 14     | 57.6%    | 27.7%    | 108%   | 1.47    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Afternoon (12:00-16:00) | 60-69%       | 24      | 12     | 12     | 50.0%    | 24.4%    | 105%   | 1.06    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 60-69%       | 8       | 5      | 3      | 62.5%    | 30.6%    | 104%   | 1.51    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 50-59%       | 38      | 32     | 6      | 84.2%    | 41.7%    | 102%   | 1.79    | 🔥 STRONG     |
| [ALPHA] participant_diversity_conviction | ORB (9:30-10:00) | 30-39%       | 22      | 18     | 4      | 81.8%    | 41.5%    | 97%    | 1.58    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | ORB (9:30-10:00) | 60-69%       | 5       | 3      | 2      | 60.0%    | 30.6%    | 96%    | 1.39    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | ORB (9:30-10:00) | 70-79%       | 13      | 7      | 6      | 53.8%    | 27.6%    | 95%    | 0.96    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 60-69%       | 17      | 8      | 9      | 47.1%    | 24.4%    | 93%    | 0.94    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 30-39%       | 14      | 6      | 8      | 42.9%    | 22.4%    | 91%    | 1.07    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | ORB (9:30-10:00) | 40-49%       | 31      | 19     | 12     | 61.3%    | 32.2%    | 90%    | 1.57    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 60-69%       | 34      | 20     | 14     | 58.8%    | 31.4%    | 87%    | 1.73    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | Afternoon (12:00-16:00) | 40-49%       | 85      | 46     | 39     | 54.1%    | 29.5%    | 83%    | 1.43    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 30-39%       | 59      | 24     | 35     | 40.7%    | 22.4%    | 82%    | 0.95    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | ORB (9:30-10:00) | 60-69%       | 9       | 5      | 4      | 55.6%    | 30.6%    | 82%    | 1.18    | ⚠ MODERATE   |
| [ALPHA] call_put_flow_asymmetry | Morning (10:00-12:00) | 30-39%       | 238     | 119    | 119    | 50.0%    | 27.7%    | 80%    | 1.09    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | Afternoon (12:00-16:00) | 30-39%       | 5       | 2      | 3      | 40.0%    | 22.4%    | 79%    | 0.92    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 30-39%       | 61      | 30     | 31     | 49.2%    | 27.7%    | 77%    | 1.05    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | ORB (9:30-10:00) | 20-29%       | 27      | 18     | 9      | 66.7%    | 37.7%    | 77%    | 1.37    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 5-9%         | 15      | 7      | 8      | 46.7%    | 26.8%    | 74%    | 0.85    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Afternoon (12:00-16:00) | 60-69%       | 151     | 64     | 87     | 42.4%    | 24.4%    | 74%    | 0.74    | ⚠ MODERATE   |
| [ALPHA] participant_diversity_conviction | Afternoon (12:00-16:00) | 80-89%       | 7       | 3      | 4      | 42.9%    | 24.7%    | 74%    | 1.71    | ⚠ MODERATE   |
| [ALPHA] participant_diversity_conviction | Morning (10:00-12:00) | 30-39%       | 63      | 30     | 33     | 47.6%    | 27.7%    | 72%    | 0.98    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | ORB (9:30-10:00) | 30-39%       | 17      | 12     | 5      | 70.6%    | 41.5%    | 70%    | 1.14    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 50-59%       | 307     | 157    | 150    | 51.1%    | 30.9%    | 66%    | 0.87    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 20-29%       | 146     | 63     | 83     | 43.2%    | 26.2%    | 65%    | 1.21    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | ORB (9:30-10:00) | 30-39%       | 47      | 32     | 15     | 68.1%    | 41.5%    | 64%    | 1.04    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | Afternoon (12:00-16:00) | 60-69%       | 5       | 2      | 3      | 40.0%    | 24.4%    | 64%    | 0.65    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | Morning (10:00-12:00) | 50-59%       | 35      | 17     | 18     | 48.6%    | 30.5%    | 59%    | 0.74    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | Morning (10:00-12:00) | 20-29%       | 41      | 17     | 24     | 41.5%    | 26.2%    | 58%    | 1.09    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 50-59%       | 141     | 68     | 73     | 48.2%    | 30.5%    | 58%    | 0.73    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | ORB (9:30-10:00) | 80-89%       | 12      | 6      | 6      | 50.0%    | 31.8%    | 57%    | 0.56    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | Morning (10:00-12:00) | 30-39%       | 203     | 88     | 115    | 43.3%    | 27.7%    | 56%    | 0.77    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 40-49%       | 25      | 11     | 14     | 44.0%    | 28.1%    | 56%    | 0.82    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 20-29%       | 185     | 62     | 123    | 33.5%    | 21.5%    | 56%    | 0.53    | ⚠ MODERATE   |
| [ALPHA] participant_diversity_conviction | ORB (9:30-10:00) | 40-49%       | 42      | 21     | 21     | 50.0%    | 32.2%    | 55%    | 0.96    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 70-79%       | 7       | 3      | 4      | 42.9%    | 28.0%    | 53%    | 0.46    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 50-59%       | 47      | 30     | 17     | 63.8%    | 41.7%    | 53%    | 0.93    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 50-59%       | 121     | 56     | 65     | 46.3%    | 30.5%    | 52%    | 0.65    | ⚠ MODERATE   |

**61 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | depth_imbalance_momentum | 565     | 54.9%    | $1.559   | 70-79%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 70-79% | UNKNOWN        | Time Held: 240-480m |
| 2     | exchange_flow_imbalance  | 574     | 32.2%    | $-0.061  | 80-89%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 80-89% | UNKNOWN        | Time Held: 30-90m |
| 3     | gex_imbalance            | 1,635   | 37.8%    | $-0.082  | 60-69%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 10-19% | Trending (Up)  | Time Held: 240-480m |
| 4     | magnet_accelerate        | 1,423   | 16.5%    | $-0.181  | 70-79%         | ORB (9:30-10:00) | Afternoon (12:00-16:00) @ 70-79% | Trending (Up)  | Time Held: 30-90m |
| 5     | theta_burn               | 44      | 2.3%     | $-0.186  | 30-39%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 30-39% | Trending (Up)  | Time Held: <30m |
| 6     | participant_divergence_scalper | 1,770   | 36.6%    | $-0.233  | 10-19%         | ORB (9:30-10:00) | Afternoon (12:00-16:00) @ 10-19% | UNKNOWN        | Time Held: 240-480m |
| 7     | exchange_flow_asymmetry  | 668     | 21.7%    | $-0.249  | 70-79%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 80-89% | UNKNOWN        | Time Held: 240-480m |
| 8     | order_book_fragmentation | 1,771   | 20.3%    | $-0.355  | 40-49%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 40-49% | UNKNOWN        | Time Held: 30-90m |
| 9     | delta_volume_exhaustion  | 1,686   | 34.0%    | $-0.358  | 40-49%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 40-49% | UNKNOWN        | Time Held: >480m |
| 10    | participant_diversity_conviction | 1,350   | 30.1%    | $-0.373  | 30-39%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 30-39% | UNKNOWN        | Time Held: >480m |
| 11    | gamma_squeeze            | 511     | 30.7%    | $-0.435  | 30-39%         | Afternoon (12:00-16:00) | Morning (10:00-12:00) @ 30-39% | Sideways       | Time Held: >480m |
| 12    | gex_divergence           | 686     | 25.1%    | $-0.468  | 80-89%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 80-89% | Trending (Up)  | Time Held: 30-90m |
| 13    | prob_weighted_magnet     | 2,700   | 20.1%    | $-0.487  | 40-49%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 30-39% | Trending (Up)  | Time Held: 240-480m |
| 14    | exchange_flow_concentration | 1,133   | 30.5%    | $-0.518  | 60-69%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 60-69% | UNKNOWN        | Time Held: >480m |
| 15    | depth_decay_momentum     | 1,374   | 33.5%    | $-0.556  | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 70-79% | UNKNOWN        | Time Held: 30-90m |
| 16    | gamma_flip_breakout      | 156     | 19.9%    | $-0.607  | 70-79%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 70-79% | Sideways       | Time Held: 30-90m |
| 17    | strike_concentration     | 248     | 41.1%    | $-0.685  | 50-59%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 50-59% | Sideways       | Time Held: 30-90m |
| 18    | vol_compression_range    | 149     | 31.5%    | $-0.742  | 60-69%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 60-69% | Trending (Up)  | Time Held: 30-90m |
| 19    | confluence_reversal      | 1,768   | 25.3%    | $-0.742  | 5-9%           | ORB (9:30-10:00) | Morning (10:00-12:00) @ 5-9% | Sideways       | Time Held: 240-480m |
| 20    | call_put_flow_asymmetry  | 2,020   | 24.0%    | $-1.243  | 30-39%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 30-39% | UNKNOWN        | Time Held: >480m |
| 21    | delta_gamma_squeeze      | 6       | 16.7%    | $-1.497  | 10-19%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 10-19% | Sideways       | N/A            |
| 22    | gamma_wall_bounce        | 504     | 18.1%    | $-1.928  | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 80-89% | Trending (Up)  | Time Held: 240-480m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis — Regular Hours Only*