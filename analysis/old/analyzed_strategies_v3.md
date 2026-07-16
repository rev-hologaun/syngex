# Strategy Performance Analysis — Round 3 Validation (Regular Hours)

**Date:** 2026-07-16  |  **Generated:** 2026-07-16 08:07 UTC  |  **Total Resolved Signals:** 16,210,634  |  **Strategies Analyzed:** 22  |  **Confidence ≥ 5%**  |  **Regular Hours**

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 16,210,634                                                   |
| Total Wins           | 2,488,948                                                    |
| Total Losses         | 4,282,502                                                    |
| Time-Expired (CLOSED) | 0                                                            |
| Overall Win Rate     | 36.8%                                                        |
| Total P&L (resolved) | $-948040.25                                                  |
| Avg P&L per Resolved Signal | $-0.14                                                       |
| Symbols Traded       | AMD, INTC, MU, NVDA, SPCX, SPY, TSLA                         |

---

## Per-Strategy Deep Dive

### call_put_flow_asymmetry

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 418,493  |  **Win Rate:** 26.7%  |  **Avg P&L (resolved):** $-0.562  |  **Avg P&L (all):** $-0.562  |  **Avg Hold:** 8464s (141.1m)  |  **Median Hold:** 2411s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 19181 | 5656  | 13525  | 0      | 29.5%     | $-0.012  | $-0.012  | -11.6%   |
| 20-29%         | 58261 | 9623  | 48638  | 0      | 16.5%     | $-1.267  | $-1.267  | -50.4%   |
| 30-39%         | 251974 | 68034 | 183940 | 0      | 27.0%     | $-0.743  | $-0.743  | -19.0%   |
| 40-49%         | 64368 | 24062 | 40306  | 0      | 37.4%     | $0.905   | $0.905   | 12.2%    |
| 50-59%         | 24709 | 4478  | 20231  | 0      | 18.1%     | $-1.297  | $-1.297  | -45.6%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 418493 | 111853 | 306640 | 0      | 26.7%     | $-0.562  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 5189  | 910   | 4279   | 0      | 17.5%     | $-0.381  |
| Positive Gamma (Range-Bound friendly) | 413304 | 110943 | 302361 | 0      | 26.8%     | $-0.564  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 10168 | 1816  | 8352   | 0      | 17.9%     | $-0.709  |
| Time Held: 30-90m      | 102563 | 30226 | 72337  | 0      | 29.5%     | $0.016   |
| Time Held: 90-240m     | 93311 | 53176 | 40135  | 0      | 57.0%     | $0.743   |
| Time Held: <30m        | 182563 | 26411 | 156152 | 0      | 14.5%     | $-0.972  |
| Time Held: >480m       | 29888 | 224   | 29664  | 0      | 0.7%      | $-4.062  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 182916 | 31725 | 151191 | 0      | 17.3%     | $-1.105  | 🔴          |
| Morning (10:00-12:00)  | 186643 | 57646 | 128997 | 0      | 30.9%     | $-0.300  | 🟢          |
| ORB (9:30-10:00)       | 48934 | 22482 | 26452  | 0      | 45.9%     | $0.471   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 48934  | 0          | 3156       | 45778      | 0.0%      | 6.4%      | 93.6%     |
| Morning (10:00-12:00)  | 186643 | 0          | 17718      | 168925     | 0.0%      | 9.5%      | 90.5%     |
| Afternoon (12:00-16:00) | 182916 | 0          | 3835       | 179081     | 0.0%      | 2.1%      | 97.9%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 3432   | 2018  | 1414   | 0      | 58.8%     | $1.153       | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 2262   | 468   | 1794   | 0      | 20.7%     | $-0.588      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 26868  | 11916 | 14952  | 0      | 44.4%     | $0.020       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 13216  | 6592  | 6624   | 0      | 49.9%     | $1.419       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 3156   | 1488  | 1668   | 0      | 47.1%     | $0.369       | 🟢          |
| Morning (10:00-12:00)  | 10-19%     | 9516   | 2578  | 6938   | 0      | 27.1%     | $0.356       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 19783  | 4400  | 15383  | 0      | 22.2%     | $-0.644      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 94482  | 30744 | 63738  | 0      | 32.5%     | $-0.782      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 45144  | 17022 | 28122  | 0      | 37.7%     | $1.136       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 17718  | 2902  | 14816  | 0      | 16.4%     | $-1.362      | 🔴          |
| Afternoon (12:00-16:00) | 10-19%     | 6233   | 1060  | 5173   | 0      | 17.0%     | $-1.218      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 36216  | 4755  | 31461  | 0      | 13.1%     | $-1.650      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 130624 | 25374 | 105250 | 0      | 19.4%     | $-0.872      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 6008   | 448   | 5560   | 0      | 7.5%      | $-1.956      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 3835   | 88    | 3747   | 0      | 2.3%      | $-2.369      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 415018 | 111371 | 303647 | 0      | 26.8%     | $-0.563  |
| SHORT        | 3475  | 482   | 2993   | 0      | 13.9%     | $-0.457  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 40980 | 3841  | 37139  | 0      | 9.4%      | $-1.432  |
| Long (30-60 min)       | 65468 | 20648 | 44820  | 0      | 31.5%     | $0.074   |
| Medium (5-15 min)      | 77894 | 10338 | 67556  | 0      | 13.3%     | $-1.039  |
| Slow (15-30 min)       | 58792 | 11948 | 46844  | 0      | 20.3%     | $-0.565  |
| Very Fast (<1 min)     | 4897  | 284   | 4613   | 0      | 5.8%      | $-0.937  |
| Very Long (>1h)        | 170462 | 64794 | 105668 | 0      | 38.0%     | $-0.367  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 26.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.56 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (37.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (16.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.56) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.74) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (45.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (8464s / 141.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### confluence_reversal

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 525,599  |  **Win Rate:** 29.9%  |  **Avg P&L (resolved):** $-0.386  |  **Avg P&L (all):** $-0.386  |  **Avg Hold:** 15077s (251.3m)  |  **Median Hold:** 2629s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 17997 | 5292  | 12705  | 0      | 29.4%     | $-0.075  | $-0.075  | -11.8%   |
| 10-19%         | 143182 | 36867 | 106315 | 0      | 25.7%     | $-0.131  | $-0.131  | -22.7%   |
| 20-29%         | 147909 | 45587 | 102322 | 0      | 30.8%     | $-0.157  | $-0.157  | -7.6%    |
| 30-39%         | 95096 | 25415 | 69681  | 0      | 26.7%     | $-1.083  | $-1.083  | -19.8%   |
| 40-49%         | 57936 | 18650 | 39286  | 0      | 32.2%     | $-0.646  | $-0.646  | -3.5%    |
| 50-59%         | 44749 | 17361 | 27388  | 0      | 38.8%     | $-0.215  | $-0.215  | 16.3%    |
| 60-69%         | 15274 | 6966  | 8308   | 0      | 45.6%     | $-0.172  | $-0.172  | 36.7%    |
| 70-79%         | 3456  | 1032  | 2424   | 0      | 29.9%     | $-1.922  | $-1.922  | -10.5%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 309369 | 97190 | 212179 | 0      | 31.4%     | $-0.255  |
| Trending (Up)        | 216230 | 59980 | 156250 | 0      | 27.7%     | $-0.573  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 7463  | 924   | 6539   | 0      | 12.4%     | $-2.190  |
| Positive Gamma (Range-Bound friendly) | 518136 | 156246 | 361890 | 0      | 30.2%     | $-0.360  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 20631 | 9472  | 11159  | 0      | 45.9%     | $0.609   |
| Time Held: 30-90m      | 126024 | 33237 | 92787  | 0      | 26.4%     | $-1.053  |
| Time Held: 90-240m     | 87015 | 26593 | 60422  | 0      | 30.6%     | $-0.434  |
| Time Held: <30m        | 214089 | 47260 | 166829 | 0      | 22.1%     | $-0.907  |
| Time Held: >480m       | 77840 | 40608 | 37232  | 0      | 52.2%     | $1.919   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 205531 | 59147 | 146384 | 0      | 28.8%     | $-0.192  | 🔴          |
| Morning (10:00-12:00)  | 239238 | 71265 | 167973 | 0      | 29.8%     | $-0.572  | 🔴          |
| ORB (9:30-10:00)       | 80830 | 26758 | 54072  | 0      | 33.1%     | $-0.327  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 80830  | 140        | 10220      | 70470      | 0.2%      | 12.6%     | 87.2%     |
| Morning (10:00-12:00)  | 239238 | 1436       | 25571      | 212231     | 0.6%      | 10.7%     | 88.7%     |
| Afternoon (12:00-16:00) | 205531 | 1880       | 24232      | 179419     | 0.9%      | 11.8%     | 87.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 1165   | 482   | 683    | 0      | 41.4%     | $1.217       | 🟢          |
| ORB (9:30-10:00)       | 10-19%     | 14736  | 7778  | 6958   | 0      | 52.8%     | $1.438       | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 23451  | 7582  | 15869  | 0      | 32.3%     | $-0.321      | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 21491  | 5888  | 15603  | 0      | 27.4%     | $-1.273      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 9627   | 2320  | 7307   | 0      | 24.1%     | $-0.741      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 8648   | 1580  | 7068   | 0      | 18.3%     | $-1.191      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 1572   | 1040  | 532    | 0      | 66.2%     | $1.903       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 140    | 88    | 52     | 0      | 62.9%     | $2.313       | 🟢          |
| Morning (10:00-12:00)  | 5-9%       | 7861   | 2374  | 5487   | 0      | 30.2%     | $-0.136      | 🟢          |
| Morning (10:00-12:00)  | 10-19%     | 61577  | 14798 | 46779  | 0      | 24.0%     | $-0.301      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 66718  | 22085 | 44633  | 0      | 33.1%     | $-0.010      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 46584  | 12417 | 34167  | 0      | 26.7%     | $-1.269      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 29491  | 8952  | 20539  | 0      | 30.4%     | $-1.325      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 18995  | 7469  | 11526  | 0      | 39.3%     | $-0.799      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 6576   | 2642  | 3934   | 0      | 40.2%     | $-0.363      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 1436   | 528   | 908    | 0      | 36.8%     | $-0.509      | 🟢          |
| Afternoon (12:00-16:00) | 5-9%       | 8971   | 2436  | 6535   | 0      | 27.2%     | $-0.189      | 🔴          |
| Afternoon (12:00-16:00) | 10-19%     | 66869  | 14291 | 52578  | 0      | 21.4%     | $-0.320      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 57740  | 15920 | 41820  | 0      | 27.6%     | $-0.259      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 27021  | 7110  | 19911  | 0      | 26.3%     | $-0.611      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 18818  | 7378  | 11440  | 0      | 39.2%     | $0.467       | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 17106  | 8312  | 8794   | 0      | 48.6%     | $0.925       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 7126   | 3284  | 3842   | 0      | 46.1%     | $-0.453      | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 1880   | 416   | 1464   | 0      | 22.1%     | $-3.316      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 266010 | 51078 | 214932 | 0      | 19.2%     | $-1.279  |
| SHORT        | 259589 | 106092 | 153497 | 0      | 40.9%     | $0.530   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 45281 | 9126  | 36155  | 0      | 20.2%     | $-0.765  |
| Long (30-60 min)       | 85217 | 24037 | 61180  | 0      | 28.2%     | $-0.995  |
| Medium (5-15 min)      | 75674 | 15013 | 60661  | 0      | 19.8%     | $-1.194  |
| Slow (15-30 min)       | 75833 | 19557 | 56276  | 0      | 25.8%     | $-0.827  |
| Very Fast (<1 min)     | 17301 | 3564  | 13737  | 0      | 20.6%     | $-0.371  |
| Very Long (>1h)        | 226293 | 85873 | 140420 | 0      | 37.9%     | $0.337   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.39 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (45.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (25.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.25) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $1.92) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (33.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (15077s / 251.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_gamma_squeeze

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 324  |  **Win Rate:** 4.9%  |  **Avg P&L (resolved):** $-1.285  |  **Avg P&L (all):** $-1.285  |  **Avg Hold:** 7171s (119.5m)  |  **Median Hold:** 3857s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 20    | 8     | 12     | 0      | 40.0%     | $0.641   | $0.641   | 20.1%    |
| 10-19%         | 82    | 4     | 78     | 0      | 4.9%      | $-1.344  | $-1.344  | -85.4%   |
| 20-29%         | 78    | 4     | 74     | 0      | 5.1%      | $-1.159  | $-1.159  | -84.6%   |
| 30-39%         | 142   | 0     | 142    | 0      | 0.0%      | $-1.575  | $-1.575  | -100.0%  |
| 40-49%         | 2     | 0     | 2      | 0      | 0.0%      | $-2.510  | $-2.510  | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 64    | 16    | 48     | 0      | 25.0%     | $-0.560  |
| Trending (Up)        | 260   | 0     | 260    | 0      | 0.0%      | $-1.464  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 288   | 4     | 284    | 0      | 1.4%      | $-1.507  |
| Positive Gamma (Range-Bound friendly) | 36    | 12    | 24     | 0      | 33.3%     | $0.487   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 74    | 6     | 68     | 0      | 8.1%      | $-0.643  |
| Time Held: 30-90m      | 222   | 2     | 220    | 0      | 0.9%      | $-1.610  |
| Time Held: 90-240m     | 28    | 8     | 20     | 0      | 28.6%     | $-0.407  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 286   | 10    | 276    | 0      | 3.5%      | $-1.286  | 🔴          |
| Morning (10:00-12:00)  | 38    | 6     | 32     | 0      | 15.8%     | $-1.281  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 38     | 0          | 0          | 38         | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 286    | 0          | 0          | 286        | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Morning (10:00-12:00)  | 10-19%     | 8      | 2     | 6      | 0      | 25.0%     | $-0.673      | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 14     | 4     | 10     | 0      | 28.6%     | $0.124       | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 14     | 0     | 14     | 0      | 0.0%      | $-2.857      | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.510      | ⚠️         |
| Afternoon (12:00-16:00) | 5-9%       | 20     | 8     | 12     | 0      | 40.0%     | $0.641       | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 74     | 2     | 72     | 0      | 2.7%      | $-1.416      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 64     | 0     | 64     | 0      | 0.0%      | $-1.440      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 128    | 0     | 128    | 0      | 0.0%      | $-1.435      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 224   | 2     | 222    | 0      | 0.9%      | $-1.624  |
| SHORT        | 100   | 14    | 86     | 0      | 14.0%     | $-0.526  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Long (30-60 min)       | 80    | 0     | 80     | 0      | 0.0%      | $-1.849  |
| Very Long (>1h)        | 244   | 16    | 228    | 0      | 6.6%      | $-1.101  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 4.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.29 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 5-9% confidence (40.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.56) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $-0.41) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Morning (10:00-12:00) (15.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (7171s / 119.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_volume_exhaustion

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 904,484  |  **Win Rate:** 68.8%  |  **Avg P&L (resolved):** $-0.006  |  **Avg P&L (all):** $-0.006  |  **Avg Hold:** 4671s (77.9m)  |  **Median Hold:** 939s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 91363 | 61651 | 29712  | 0      | 67.5%     | $-0.039  | $-0.039  | -1.6%    |
| 10-19%         | 300456 | 211931 | 88525  | 0      | 70.5%     | $0.061   | $0.061   | 1.6%     |
| 20-29%         | 273880 | 187191 | 86689  | 0      | 68.3%     | $-0.007  | $-0.007  | -2.0%    |
| 30-39%         | 169326 | 109324 | 60002  | 0      | 64.6%     | $-0.209  | $-0.209  | -7.8%    |
| 40-49%         | 55131 | 39754 | 15377  | 0      | 72.1%     | $0.049   | $0.049   | 3.0%     |
| 50-59%         | 12630 | 10942 | 1688   | 0      | 86.6%     | $0.935   | $0.935   | 20.8%    |
| 60-69%         | 1698  | 1546  | 152    | 0      | 91.0%     | $1.429   | $1.429   | 25.2%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 904484 | 622339 | 282145 | 0      | 68.8%     | $-0.006  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 23564 | 14678 | 8886   | 0      | 62.3%     | $0.089   |
| Positive Gamma (Range-Bound friendly) | 880920 | 607661 | 273259 | 0      | 69.0%     | $-0.009  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 2540  | 1796  | 744    | 0      | 70.7%     | $0.774   |
| Time Held: 30-90m      | 192137 | 119048 | 73089  | 0      | 62.0%     | $-0.216  |
| Time Held: 90-240m     | 62236 | 23085 | 39151  | 0      | 37.1%     | $-0.702  |
| Time Held: <30m        | 609363 | 458970 | 150393 | 0      | 75.3%     | $0.237   |
| Time Held: >480m       | 38208 | 19440 | 18768  | 0      | 50.9%     | $-1.763  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 451130 | 322121 | 129009 | 0      | 71.4%     | $0.008   | 🟢          |
| Morning (10:00-12:00)  | 365334 | 249921 | 115413 | 0      | 68.4%     | $0.047   | 🔴          |
| ORB (9:30-10:00)       | 88020 | 50297 | 37723  | 0      | 57.1%     | $-0.298  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 88020  | 0          | 764        | 87256      | 0.0%      | 0.9%      | 99.1%     |
| Morning (10:00-12:00)  | 365334 | 0          | 3812       | 361522     | 0.0%      | 1.0%      | 99.0%     |
| Afternoon (12:00-16:00) | 451130 | 0          | 9752       | 441378     | 0.0%      | 2.2%      | 97.8%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 11201  | 6646  | 4555   | 0      | 59.3%     | $-0.047      | 🔴          |
| ORB (9:30-10:00)       | 10-19%     | 29587  | 16630 | 12957  | 0      | 56.2%     | $-0.626      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 26363  | 16277 | 10086  | 0      | 61.7%     | $-0.162      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 16468  | 7415  | 9053   | 0      | 45.0%     | $-0.408      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 3637   | 2717  | 920    | 0      | 74.7%     | $0.773       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 724    | 572   | 152    | 0      | 79.0%     | $1.224       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 40     | 40    | 0      | 0      | 100.0%    | $1.922       | 🟢          |
| Morning (10:00-12:00)  | 5-9%       | 41932  | 27049 | 14883  | 0      | 64.5%     | $-0.230      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 131301 | 90773 | 40528  | 0      | 69.1%     | $0.028       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 113846 | 75825 | 38021  | 0      | 66.6%     | $0.031       | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 58940  | 41011 | 17929  | 0      | 69.6%     | $0.164       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 15503  | 11699 | 3804   | 0      | 75.5%     | $0.302       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 3100   | 2924  | 176    | 0      | 94.3%     | $1.344       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 712    | 640   | 72     | 0      | 89.9%     | $1.484       | 🟢          |
| Afternoon (12:00-16:00) | 5-9%       | 38230  | 27956 | 10274  | 0      | 73.1%     | $0.174       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 139568 | 104528 | 35040  | 0      | 74.9%     | $0.237       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 133671 | 95089 | 38582  | 0      | 71.1%     | $-0.009      | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 93918  | 60898 | 33020  | 0      | 64.8%     | $-0.409      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 35991  | 25338 | 10653  | 0      | 70.4%     | $-0.133      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 8806   | 7446  | 1360   | 0      | 84.6%     | $0.768       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 946    | 866   | 80     | 0      | 91.5%     | $1.366       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 439431 | 298306 | 141125 | 0      | 67.9%     | $-0.188  |
| SHORT        | 465053 | 324033 | 141020 | 0      | 69.7%     | $0.165   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 180354 | 153739 | 26615  | 0      | 85.2%     | $0.663   |
| Long (30-60 min)       | 134020 | 84976 | 49044  | 0      | 63.4%     | $-0.168  |
| Medium (5-15 min)      | 241902 | 179237 | 62665  | 0      | 74.1%     | $0.165   |
| Slow (15-30 min)       | 168271 | 108847 | 59424  | 0      | 64.7%     | $-0.192  |
| Very Fast (<1 min)     | 18836 | 17147 | 1689   | 0      | 91.0%     | $0.934   |
| Very Long (>1h)        | 161101 | 78393 | 82708  | 0      | 48.7%     | $-0.795  |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 68.8% — this strategy consistently picks directional moves.
- 📉 Negative avg P&L per resolved signal: $-0.01 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (91.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (64.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.01) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $0.77) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (71.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4671s / 77.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_decay_momentum

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 403,641  |  **Win Rate:** 40.6%  |  **Avg P&L (resolved):** $0.021  |  **Avg P&L (all):** $0.021  |  **Avg Hold:** 6421s (107.0m)  |  **Median Hold:** 1196s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 395   | 196   | 199    | 0      | 49.6%     | $0.521   | $0.521   | 23.9%    |
| 50-59%         | 116622 | 45489 | 71133  | 0      | 39.0%     | $-0.001  | $-0.001  | -2.5%    |
| 60-69%         | 191477 | 76644 | 114833 | 0      | 40.0%     | $-0.044  | $-0.044  | 0.1%     |
| 70-79%         | 78033 | 32640 | 45393  | 0      | 41.8%     | $0.052   | $0.052   | 4.5%     |
| 80-89%         | 16682 | 8532  | 8150   | 0      | 51.1%     | $0.757   | $0.757   | 27.9%    |
| 90-99%         | 432   | 184   | 248    | 0      | 42.6%     | $0.572   | $0.572   | 6.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 403641 | 163685 | 239956 | 0      | 40.6%     | $0.021   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 13435 | 5335  | 8100   | 0      | 39.7%     | $0.221   |
| Positive Gamma (Range-Bound friendly) | 390206 | 158350 | 231856 | 0      | 40.6%     | $0.014   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1490  | 640   | 850    | 0      | 43.0%     | $-0.094  |
| Time Held: 30-90m      | 104607 | 45680 | 58927  | 0      | 43.7%     | $0.049   |
| Time Held: 90-240m     | 32362 | 19056 | 13306  | 0      | 58.9%     | $0.543   |
| Time Held: <30m        | 240774 | 86221 | 154553 | 0      | 35.8%     | $-0.150  |
| Time Held: >480m       | 24408 | 12088 | 12320  | 0      | 49.5%     | $0.905   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 181027 | 72956 | 108071 | 0      | 40.3%     | $0.005   | 🔴          |
| Morning (10:00-12:00)  | 175733 | 70432 | 105301 | 0      | 40.1%     | $0.022   | 🔴          |
| ORB (9:30-10:00)       | 46881 | 20297 | 26584  | 0      | 43.3%     | $0.077   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 46881  | 10146      | 36727      | 8          | 21.6%     | 78.3%     | 0.0%      |
| Morning (10:00-12:00)  | 175733 | 40032      | 135572     | 129        | 22.8%     | 77.1%     | 0.1%      |
| Afternoon (12:00-16:00) | 181027 | 44969      | 135800     | 258        | 24.8%     | 75.0%     | 0.1%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 40-49%     | 8      | 4     | 4      | 0      | 50.0%     | $0.675       | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 11883  | 4639  | 7244   | 0      | 39.0%     | $-0.078      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 24844  | 10778 | 14066  | 0      | 43.4%     | $0.140       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 8454   | 4076  | 4378   | 0      | 48.2%     | $0.006       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 1636   | 752   | 884    | 0      | 46.0%     | $0.502       | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 56     | 48    | 8      | 0      | 85.7%     | $3.503       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 129    | 32    | 97     | 0      | 24.8%     | $-0.067      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 53773  | 21968 | 31805  | 0      | 40.9%     | $0.172       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 81799  | 31381 | 50418  | 0      | 38.4%     | $-0.107      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 33176  | 13235 | 19941  | 0      | 39.9%     | $-0.065      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 6656   | 3680  | 2976   | 0      | 55.3%     | $0.742       | 🟢          |
| Morning (10:00-12:00)  | 90-99%     | 200    | 136   | 64     | 0      | 68.0%     | $3.339       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 258    | 160   | 98     | 0      | 62.0%     | $0.811       | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 50966  | 18882 | 32084  | 0      | 37.0%     | $-0.166      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 84834  | 34485 | 50349  | 0      | 40.6%     | $-0.037      | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 36403  | 15329 | 21074  | 0      | 42.1%     | $0.169       | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 8390   | 4100  | 4290   | 0      | 48.9%     | $0.818       | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 176    | 0     | 176    | 0      | 0.0%      | $-3.504      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 204280 | 79467 | 124813 | 0      | 38.9%     | $-0.248  |
| SHORT        | 199361 | 84218 | 115143 | 0      | 42.2%     | $0.297   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 66168 | 19536 | 46632  | 0      | 29.5%     | $-0.473  |
| Long (30-60 min)       | 67649 | 27760 | 39889  | 0      | 41.0%     | $-0.064  |
| Medium (5-15 min)      | 95886 | 35556 | 60330  | 0      | 37.1%     | $-0.041  |
| Slow (15-30 min)       | 68541 | 29871 | 38670  | 0      | 43.6%     | $0.136   |
| Very Fast (<1 min)     | 10179 | 1258  | 8921   | 0      | 12.4%     | $-1.000  |
| Very Long (>1h)        | 95218 | 49704 | 45514  | 0      | 52.2%     | $0.514   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 40.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.02 — profitable even with 40.6% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (51.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (39.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.02) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $0.90) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (43.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6421s / 107.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_imbalance_momentum

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 171,677  |  **Win Rate:** 28.7%  |  **Avg P&L (resolved):** $-0.207  |  **Avg P&L (all):** $-0.207  |  **Avg Hold:** 6906s (115.1m)  |  **Median Hold:** 2450s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 4758  | 903   | 3855   | 0      | 19.0%     | $-0.588  | $-0.588  | -43.0%   |
| 40-49%         | 43181 | 11332 | 31849  | 0      | 26.2%     | $-0.334  | $-0.334  | -21.3%   |
| 50-59%         | 92718 | 28761 | 63957  | 0      | 31.0%     | $-0.037  | $-0.037  | -6.9%    |
| 60-69%         | 20809 | 5362  | 15447  | 0      | 25.8%     | $-0.560  | $-0.560  | -22.7%   |
| 70-79%         | 10211 | 2971  | 7240   | 0      | 29.1%     | $-0.317  | $-0.317  | -12.7%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 171677 | 49329 | 122348 | 0      | 28.7%     | $-0.207  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 3347  | 1713  | 1634   | 0      | 51.2%     | $0.413   |
| Positive Gamma (Range-Bound friendly) | 168330 | 47616 | 120714 | 0      | 28.3%     | $-0.219  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 5217  | 2016  | 3201   | 0      | 38.6%     | $0.786   |
| Time Held: 30-90m      | 52014 | 15798 | 36216  | 0      | 30.4%     | $0.182   |
| Time Held: 90-240m     | 35434 | 9349  | 26085  | 0      | 26.4%     | $-0.276  |
| Time Held: <30m        | 68244 | 13638 | 54606  | 0      | 20.0%     | $-1.159  |
| Time Held: >480m       | 10768 | 8528  | 2240   | 0      | 79.2%     | $3.692   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 56169 | 17551 | 38618  | 0      | 31.2%     | $0.156   | 🟢          |
| Morning (10:00-12:00)  | 84454 | 22272 | 62182  | 0      | 26.4%     | $-0.559  | 🔴          |
| ORB (9:30-10:00)       | 31054 | 9506  | 21548  | 0      | 30.6%     | $0.094   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 31054  | 2285       | 23350      | 5419       | 7.4%      | 75.2%     | 17.5%     |
| Morning (10:00-12:00)  | 84454  | 5500       | 57427      | 21527      | 6.5%      | 68.0%     | 25.5%     |
| Afternoon (12:00-16:00) | 56169  | 2426       | 32750      | 20993      | 4.3%      | 58.3%     | 37.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 989    | 593   | 396    | 0      | 60.0%     | $3.122       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 4430   | 1266  | 3164   | 0      | 28.6%     | $0.264       | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 17690  | 5328  | 12362  | 0      | 30.1%     | $0.194       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 5660   | 1498  | 4162   | 0      | 26.5%     | $-0.795      | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 2285   | 821   | 1464   | 0      | 35.9%     | $-0.115      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 1792   | 240   | 1552   | 0      | 13.4%     | $-0.943      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 19735  | 5122  | 14613  | 0      | 26.0%     | $-0.683      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 47325  | 13069 | 34256  | 0      | 27.6%     | $-0.470      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 10102  | 2380  | 7722   | 0      | 23.6%     | $-0.744      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 5500   | 1461  | 4039   | 0      | 26.6%     | $-0.415      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 1977   | 70    | 1907   | 0      | 3.5%      | $-2.123      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 19016  | 4944  | 14072  | 0      | 26.0%     | $-0.111      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 27703  | 10364 | 17339  | 0      | 37.4%     | $0.555       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 5047   | 1484  | 3563   | 0      | 29.4%     | $0.071       | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 2426   | 689   | 1737   | 0      | 28.4%     | $-0.284      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 37247 | 7744  | 29503  | 0      | 20.8%     | $-0.844  |
| SHORT        | 134430 | 41585 | 92845  | 0      | 30.9%     | $-0.030  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 11167 | 591   | 10576  | 0      | 5.3%      | $-2.040  |
| Long (30-60 min)       | 33824 | 11201 | 22623  | 0      | 33.1%     | $0.358   |
| Medium (5-15 min)      | 27902 | 5141  | 22761  | 0      | 18.4%     | $-1.405  |
| Slow (15-30 min)       | 28613 | 7906  | 20707  | 0      | 27.6%     | $-0.556  |
| Very Fast (<1 min)     | 562   | 0     | 562    | 0      | 0.0%      | $-2.176  |
| Very Long (>1h)        | 69609 | 24490 | 45119  | 0      | 35.2%     | $0.452   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 28.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.21 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (31.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (19.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.21) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $3.69) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (31.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6906s / 115.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_asymmetry

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 185,988  |  **Win Rate:** 21.2%  |  **Avg P&L (resolved):** $-0.406  |  **Avg P&L (all):** $-0.406  |  **Avg Hold:** 7872s (131.2m)  |  **Median Hold:** 2420s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 70-79%         | 3659  | 201   | 3458   | 0      | 5.5%      | $-2.727  | $-2.727  | -80.8%   |
| 80-89%         | 182329 | 39151 | 143178 | 0      | 21.5%     | $-0.360  | $-0.360  | -24.8%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 185988 | 39352 | 146636 | 0      | 21.2%     | $-0.406  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 185988 | 39352 | 146636 | 0      | 21.2%     | $-0.406  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 8546  | 4272  | 4274   | 0      | 50.0%     | $0.899   |
| Time Held: 30-90m      | 50917 | 12349 | 38568  | 0      | 24.3%     | $0.288   |
| Time Held: 90-240m     | 36272 | 9699  | 26573  | 0      | 26.7%     | $0.124   |
| Time Held: <30m        | 77677 | 5424  | 72253  | 0      | 7.0%      | $-1.832  |
| Time Held: >480m       | 12576 | 7608  | 4968   | 0      | 60.5%     | $3.176   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 63489 | 9619  | 53870  | 0      | 15.2%     | $-0.782  | 🔴          |
| Morning (10:00-12:00)  | 87240 | 17051 | 70189  | 0      | 19.5%     | $-0.644  | 🔴          |
| ORB (9:30-10:00)       | 35259 | 12682 | 22577  | 0      | 36.0%     | $0.859   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 35259  | 35259      | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 87240  | 87240      | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 63489  | 63489      | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 70-79%     | 121    | 17    | 104    | 0      | 14.0%     | $-1.190      | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 35138  | 12665 | 22473  | 0      | 36.0%     | $0.866       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 2620   | 80    | 2540   | 0      | 3.1%      | $-3.055      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 84620  | 16971 | 67649  | 0      | 20.1%     | $-0.570      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 918    | 104   | 814    | 0      | 11.3%     | $-1.993      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 62571  | 9515  | 53056  | 0      | 15.2%     | $-0.764      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 115984 | 18973 | 97011  | 0      | 16.4%     | $-0.916  |
| SHORT        | 70004 | 20379 | 49625  | 0      | 29.1%     | $0.439   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 14523 | 122   | 14401  | 0      | 0.8%      | $-2.428  |
| Long (30-60 min)       | 31651 | 7756  | 23895  | 0      | 24.5%     | $0.356   |
| Medium (5-15 min)      | 32839 | 2538  | 30301  | 0      | 7.7%      | $-1.651  |
| Slow (15-30 min)       | 29476 | 2764  | 26712  | 0      | 9.4%      | $-1.748  |
| Very Fast (<1 min)     | 839   | 0     | 839    | 0      | 0.0%      | $-1.610  |
| Very Long (>1h)        | 76660 | 26172 | 50488  | 0      | 34.1%     | $0.724   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 21.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.41 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (21.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (5.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.41) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $3.18) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (36.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (7872s / 131.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_concentration

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 283,460  |  **Win Rate:** 35.2%  |  **Avg P&L (resolved):** $-0.218  |  **Avg P&L (all):** $-0.218  |  **Avg Hold:** 6734s (112.2m)  |  **Median Hold:** 1056s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 6453  | 2759  | 3694   | 0      | 42.8%     | $0.101   | $0.101   | 6.9%     |
| 20-29%         | 14372 | 5137  | 9235   | 0      | 35.7%     | $-0.280  | $-0.280  | -10.6%   |
| 30-39%         | 39383 | 12326 | 27057  | 0      | 31.3%     | $-0.432  | $-0.432  | -21.8%   |
| 40-49%         | 96110 | 33983 | 62127  | 0      | 35.4%     | $-0.177  | $-0.177  | -11.6%   |
| 50-59%         | 55791 | 18762 | 37029  | 0      | 33.6%     | $-0.203  | $-0.203  | -15.9%   |
| 60-69%         | 71351 | 26691 | 44660  | 0      | 37.4%     | $-0.182  | $-0.182  | -6.5%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 283460 | 99658 | 183802 | 0      | 35.2%     | $-0.218  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 10295 | 4860  | 5435   | 0      | 47.2%     | $0.362   |
| Positive Gamma (Range-Bound friendly) | 273165 | 94798 | 178367 | 0      | 34.7%     | $-0.240  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 880   | 160   | 720    | 0      | 18.2%     | $-0.511  |
| Time Held: 30-90m      | 64110 | 27653 | 36457  | 0      | 43.1%     | $0.102   |
| Time Held: 90-240m     | 15898 | 9056  | 6842   | 0      | 57.0%     | $0.641   |
| Time Held: <30m        | 181716 | 56989 | 124727 | 0      | 31.4%     | $-0.310  |
| Time Held: >480m       | 20856 | 5800  | 15056  | 0      | 27.8%     | $-1.036  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 115523 | 39174 | 76349  | 0      | 33.9%     | $-0.306  | 🔴          |
| Morning (10:00-12:00)  | 128907 | 43737 | 85170  | 0      | 33.9%     | $-0.192  | 🔴          |
| ORB (9:30-10:00)       | 39030 | 16747 | 22283  | 0      | 42.9%     | $-0.042  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 39030  | 0          | 20043      | 18987      | 0.0%      | 51.4%     | 48.6%     |
| Morning (10:00-12:00)  | 128907 | 0          | 59159      | 69748      | 0.0%      | 45.9%     | 54.1%     |
| Afternoon (12:00-16:00) | 115523 | 0          | 47940      | 67583      | 0.0%      | 41.5%     | 58.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 388    | 96    | 292    | 0      | 24.7%     | $-0.229      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 1741   | 840   | 901    | 0      | 48.2%     | $-0.205      | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 5145   | 2771  | 2374   | 0      | 53.9%     | $0.134       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 11713  | 4687  | 7026   | 0      | 40.0%     | $-0.325      | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 7491   | 2430  | 5061   | 0      | 32.4%     | $-0.288      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 12552  | 5923  | 6629   | 0      | 47.2%     | $0.327       | 🟢          |
| Morning (10:00-12:00)  | 10-19%     | 2758   | 1521  | 1237   | 0      | 55.1%     | $0.222       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 5073   | 1373  | 3700   | 0      | 27.1%     | $-0.518      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 16422  | 3739  | 12683  | 0      | 22.8%     | $-0.486      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 45495  | 14456 | 31039  | 0      | 31.8%     | $-0.218      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 23996  | 8595  | 15401  | 0      | 35.8%     | $-0.138      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 35163  | 14053 | 21110  | 0      | 40.0%     | $-0.044      | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 3307   | 1142  | 2165   | 0      | 34.5%     | $0.039       | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 7558   | 2924  | 4634   | 0      | 38.7%     | $-0.138      | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 17816  | 5816  | 12000  | 0      | 32.6%     | $-0.547      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 38902  | 14840 | 24062  | 0      | 38.1%     | $-0.085      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 24304  | 7737  | 16567  | 0      | 31.8%     | $-0.241      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 23636  | 6715  | 16921  | 0      | 28.4%     | $-0.656      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 223943 | 73571 | 150372 | 0      | 32.9%     | $-0.393  |
| SHORT        | 59517 | 26087 | 33430  | 0      | 43.8%     | $0.441   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 48390 | 11257 | 37133  | 0      | 23.3%     | $-0.616  |
| Long (30-60 min)       | 46136 | 18844 | 27292  | 0      | 40.8%     | $0.015   |
| Medium (5-15 min)      | 74001 | 22957 | 51044  | 0      | 31.0%     | $-0.280  |
| Slow (15-30 min)       | 50561 | 21378 | 29183  | 0      | 42.3%     | $0.047   |
| Very Fast (<1 min)     | 8764  | 1397  | 7367   | 0      | 15.9%     | $-0.933  |
| Very Long (>1h)        | 55608 | 23825 | 31783  | 0      | 42.8%     | $-0.109  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 35.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.22 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (42.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (31.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.22) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.64) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (42.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6734s / 112.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_imbalance

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 182,610  |  **Win Rate:** 33.2%  |  **Avg P&L (resolved):** $-0.002  |  **Avg P&L (all):** $-0.002  |  **Avg Hold:** 4854s (80.9m)  |  **Median Hold:** 1176s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 100   | 1     | 99     | 0      | 1.0%      | $-1.622  | $-1.622  | -97.0%   |
| 30-39%         | 1576  | 264   | 1312   | 0      | 16.8%     | $-0.260  | $-0.260  | -49.9%   |
| 40-49%         | 6308  | 1929  | 4379   | 0      | 30.6%     | $-0.021  | $-0.021  | -8.3%    |
| 50-59%         | 30599 | 10413 | 20186  | 0      | 34.0%     | $0.019   | $0.019   | 2.1%     |
| 60-69%         | 32783 | 9819  | 22964  | 0      | 30.0%     | $-0.176  | $-0.176  | -10.1%   |
| 70-79%         | 74807 | 25077 | 49730  | 0      | 33.5%     | $-0.015  | $-0.015  | 0.6%     |
| 80-89%         | 36437 | 13053 | 23384  | 0      | 35.8%     | $0.182   | $0.182   | 7.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 182610 | 60556 | 122054 | 0      | 33.2%     | $-0.002  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 2919  | 1114  | 1805   | 0      | 38.2%     | $0.063   |
| Positive Gamma (Range-Bound friendly) | 179691 | 59442 | 120249 | 0      | 33.1%     | $-0.003  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1808  | 1216  | 592    | 0      | 67.3%     | $1.773   |
| Time Held: 30-90m      | 47398 | 20525 | 26873  | 0      | 43.3%     | $0.533   |
| Time Held: 90-240m     | 13488 | 6464  | 7024   | 0      | 47.9%     | $0.679   |
| Time Held: <30m        | 111660 | 28559 | 83101  | 0      | 25.6%     | $-0.432  |
| Time Held: >480m       | 8256  | 3792  | 4464   | 0      | 45.9%     | $1.235   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 64761 | 18912 | 45849  | 0      | 29.2%     | $-0.160  | 🔴          |
| Morning (10:00-12:00)  | 88924 | 31145 | 57779  | 0      | 35.0%     | $0.037   | 🟢          |
| ORB (9:30-10:00)       | 28925 | 10499 | 18426  | 0      | 36.3%     | $0.232   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 28925  | 18736      | 8949       | 1240       | 64.8%     | 30.9%     | 4.3%      |
| Morning (10:00-12:00)  | 88924  | 56166      | 28973      | 3785       | 63.2%     | 32.6%     | 4.3%      |
| Afternoon (12:00-16:00) | 64761  | 36342      | 25460      | 2959       | 56.1%     | 39.3%     | 4.6%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 32     | 0     | 32     | 0      | 0.0%      | $-1.980      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 288    | 32    | 256    | 0      | 11.1%     | $-0.153      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 920    | 116   | 804    | 0      | 12.6%     | $-0.777      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 3776   | 1479  | 2297   | 0      | 39.2%     | $0.418       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 5173   | 1616  | 3557   | 0      | 31.2%     | $0.000       | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 12447  | 4947  | 7500   | 0      | 39.7%     | $0.416       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 6289   | 2309  | 3980   | 0      | 36.7%     | $0.121       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 1      | 1     | 0      | 0      | 100.0%    | $1.590       | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 865    | 104   | 761    | 0      | 12.0%     | $-0.713      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 2919   | 1109  | 1810   | 0      | 38.0%     | $0.028       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 14146  | 5300  | 8846   | 0      | 37.5%     | $-0.055      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 14827  | 4472  | 10355  | 0      | 30.2%     | $-0.270      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 37859  | 13129 | 24730  | 0      | 34.7%     | $0.035       | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 18307  | 7030  | 11277  | 0      | 38.4%     | $0.397       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 67     | 0     | 67     | 0      | 0.0%      | $-1.499      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 423    | 128   | 295    | 0      | 30.3%     | $0.595       | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 2469   | 704   | 1765   | 0      | 28.5%     | $0.202       | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 12677  | 3634  | 9043   | 0      | 28.7%     | $-0.018      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 12783  | 3731  | 9052   | 0      | 29.2%     | $-0.139      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 24501  | 7001  | 17500  | 0      | 28.6%     | $-0.310      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 11841  | 3714  | 8127   | 0      | 31.4%     | $-0.118      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 96408 | 27658 | 68750  | 0      | 28.7%     | $-0.367  |
| SHORT        | 86202 | 32898 | 53304  | 0      | 38.2%     | $0.406   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 28308 | 3767  | 24541  | 0      | 13.3%     | $-1.171  |
| Long (30-60 min)       | 33560 | 13008 | 20552  | 0      | 38.8%     | $0.221   |
| Medium (5-15 min)      | 42475 | 12725 | 29750  | 0      | 30.0%     | $-0.229  |
| Slow (15-30 min)       | 35605 | 11667 | 23938  | 0      | 32.8%     | $0.021   |
| Very Fast (<1 min)     | 5272  | 400   | 4872   | 0      | 7.6%      | $-1.151  |
| Very Long (>1h)        | 37390 | 18989 | 18401  | 0      | 50.8%     | $1.081   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.00 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (35.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (1.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.00) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.77) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (36.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4854s / 80.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_flip_breakout

**Symbols:** INTC, MU, NVDA, SPY  |  **Total Signals:** 190,133  |  **Win Rate:** 53.5%  |  **Avg P&L (resolved):** $-0.007  |  **Avg P&L (all):** $-0.007  |  **Avg Hold:** 3931s (65.5m)  |  **Median Hold:** 1287s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 5792  | 3328  | 2464   | 0      | 57.5%     | $-0.571  | $-0.571  | -22.4%   |
| 10-19%         | 14200 | 8720  | 5480   | 0      | 61.4%     | $-0.156  | $-0.156  | -7.9%    |
| 20-29%         | 28914 | 17378 | 11536  | 0      | 60.1%     | $-0.201  | $-0.201  | -15.2%   |
| 30-39%         | 29868 | 17980 | 11888  | 0      | 60.2%     | $-0.066  | $-0.066  | -5.7%    |
| 40-49%         | 35095 | 17415 | 17680  | 0      | 49.6%     | $0.040   | $0.040   | 30.2%    |
| 50-59%         | 30198 | 15008 | 15190  | 0      | 49.7%     | $0.196   | $0.196   | 8.9%     |
| 60-69%         | 17604 | 8298  | 9306   | 0      | 47.1%     | $0.248   | $0.248   | 25.7%    |
| 70-79%         | 8922  | 3154  | 5768   | 0      | 35.4%     | $0.042   | $0.042   | 1.6%     |
| 80-89%         | 5222  | 2106  | 3116   | 0      | 40.3%     | $-0.053  | $-0.053  | 0.6%     |
| 90-99%         | 14318 | 8404  | 5914   | 0      | 58.7%     | $0.016   | $0.016   | 3.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 103676 | 52212 | 51464  | 0      | 50.4%     | $-0.026  |
| Trending (Up)        | 86457 | 49579 | 36878  | 0      | 57.3%     | $0.015   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 237   | 109   | 128    | 0      | 46.0%     | $-0.168  |
| Positive Gamma (Range-Bound friendly) | 189896 | 101682 | 88214  | 0      | 53.5%     | $-0.007  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 902   | 318   | 584    | 0      | 35.3%     | $-0.068  |
| Time Held: 30-90m      | 46196 | 22480 | 23716  | 0      | 48.7%     | $0.108   |
| Time Held: 90-240m     | 31574 | 17438 | 14136  | 0      | 55.2%     | $0.234   |
| Time Held: <30m        | 106837 | 59147 | 47690  | 0      | 55.4%     | $-0.119  |
| Time Held: >480m       | 4624  | 2408  | 2216   | 0      | 52.1%     | $-0.198  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 94565 | 44557 | 50008  | 0      | 47.1%     | $-0.073  | 🔴          |
| Morning (10:00-12:00)  | 75072 | 45522 | 29550  | 0      | 60.6%     | $0.153   | 🟢          |
| ORB (9:30-10:00)       | 20496 | 11712 | 8784   | 0      | 57.1%     | $-0.288  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 20496  | 1972       | 1960       | 16564      | 9.6%      | 9.6%      | 80.8%     |
| Morning (10:00-12:00)  | 75072  | 8694       | 9966       | 56412      | 11.6%     | 13.3%     | 75.1%     |
| Afternoon (12:00-16:00) | 94565  | 17796      | 35876      | 40893      | 18.8%     | 37.9%     | 43.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 5-9%       | 1792   | 1280  | 512    | 0      | 71.4%     | $-0.279      | 🟢          |
| ORB (9:30-10:00)       | 10-19%     | 2592   | 1024  | 1568   | 0      | 39.5%     | $-0.887      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 3756   | 1636  | 2120   | 0      | 43.6%     | $-0.572      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 5664   | 4008  | 1656   | 0      | 70.8%     | $0.061       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 2760   | 1976  | 784    | 0      | 71.6%     | $-0.057      | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 516    | 344   | 172    | 0      | 66.7%     | $-0.090      | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 1444   | 312   | 1132   | 0      | 21.6%     | $-0.545      | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 540    | 192   | 348    | 0      | 35.6%     | $0.164       | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 840    | 512   | 328    | 0      | 61.0%     | $-0.505      | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 592    | 428   | 164    | 0      | 72.3%     | $0.056       | 🟢          |
| Morning (10:00-12:00)  | 5-9%       | 3008   | 1984  | 1024   | 0      | 66.0%     | $-0.155      | 🟢          |
| Morning (10:00-12:00)  | 10-19%     | 8912   | 6032  | 2880   | 0      | 67.7%     | $-0.038      | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 19024  | 12080 | 6944   | 0      | 63.5%     | $-0.130      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 10898  | 7778  | 3120   | 0      | 71.4%     | $0.209       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 14570  | 8442  | 6128   | 0      | 57.9%     | $0.548       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 6114   | 2986  | 3128   | 0      | 48.8%     | $0.613       | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 3852   | 2488  | 1364   | 0      | 64.6%     | $0.515       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 3200   | 1166  | 2034   | 0      | 36.4%     | $-0.040      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 1092   | 480   | 612    | 0      | 44.0%     | $0.135       | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 4402   | 2086  | 2316   | 0      | 47.4%     | $-0.286      | 🔴          |
| Afternoon (12:00-16:00) | 5-9%       | 992    | 64    | 928    | 0      | 6.5%      | $-2.361      | 🔴          |
| Afternoon (12:00-16:00) | 10-19%     | 2696   | 1664  | 1032   | 0      | 61.7%     | $0.156       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 6134   | 3662  | 2472   | 0      | 59.7%     | $-0.197      | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 13306  | 6194  | 7112   | 0      | 46.6%     | $-0.346      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 17765  | 6997  | 10768  | 0      | 39.4%     | $-0.362      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 23568  | 11678 | 11890  | 0      | 49.6%     | $0.094       | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 12308  | 5498  | 6810   | 0      | 44.7%     | $0.258       | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 5182   | 1796  | 3386   | 0      | 34.7%     | $0.080       | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 3290   | 1114  | 2176   | 0      | 33.9%     | $-0.000      | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 9324   | 5890  | 3434   | 0      | 63.2%     | $0.155       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 82622 | 49214 | 33408  | 0      | 59.6%     | $0.126   |
| SHORT        | 107511 | 52577 | 54934  | 0      | 48.9%     | $-0.109  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 25308 | 16792 | 8516   | 0      | 66.4%     | $0.071   |
| Long (30-60 min)       | 31748 | 13774 | 17974  | 0      | 43.4%     | $-0.018  |
| Medium (5-15 min)      | 37282 | 15898 | 21384  | 0      | 42.6%     | $-0.251  |
| Slow (15-30 min)       | 28137 | 10783 | 17354  | 0      | 38.3%     | $-0.278  |
| Very Fast (<1 min)     | 16110 | 15674 | 436    | 0      | 97.3%     | $0.165   |
| Very Long (>1h)        | 51548 | 28870 | 22678  | 0      | 56.0%     | $0.232   |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 53.5% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 📉 Negative avg P&L per resolved signal: $-0.01 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (61.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (35.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.02) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.23) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Morning (10:00-12:00) (60.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3931s / 65.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 126,502  |  **Win Rate:** 23.9%  |  **Avg P&L (resolved):** $-0.518  |  **Avg P&L (all):** $-0.518  |  **Avg Hold:** 10269s (171.1m)  |  **Median Hold:** 1049s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 64    | 0     | 64     | 0      | 0.0%      | $-2.320  | $-2.320  | -100.0%  |
| 30-39%         | 16327 | 4769  | 11558  | 0      | 29.2%     | $-0.135  | $-0.135  | -12.4%   |
| 40-49%         | 68421 | 21294 | 47127  | 0      | 31.1%     | $0.066   | $0.066   | -6.6%    |
| 50-59%         | 30410 | 3796  | 26614  | 0      | 12.5%     | $-1.299  | $-1.299  | -62.5%   |
| 60-69%         | 11272 | 400   | 10872  | 0      | 3.5%      | $-2.501  | $-2.501  | -89.3%   |
| 70-79%         | 8     | 8     | 0      | 0      | 100.0%    | $1.350   | $1.350   | 201.5%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 73351 | 15613 | 57738  | 0      | 21.3%     | $-0.622  |
| Trending (Up)        | 53151 | 14654 | 38497  | 0      | 27.6%     | $-0.374  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 2269  | 351   | 1918   | 0      | 15.5%     | $-0.225  |
| Positive Gamma (Range-Bound friendly) | 124233 | 29916 | 94317  | 0      | 24.1%     | $-0.523  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 264   | 168   | 96     | 0      | 63.6%     | $2.688   |
| Time Held: 30-90m      | 25625 | 8833  | 16792  | 0      | 34.5%     | $0.163   |
| Time Held: 90-240m     | 8334  | 2206  | 6128   | 0      | 26.5%     | $-0.406  |
| Time Held: <30m        | 75727 | 18988 | 56739  | 0      | 25.1%     | $-0.220  |
| Time Held: >480m       | 16552 | 72    | 16480  | 0      | 0.4%      | $-3.041  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 54600 | 6871  | 47729  | 0      | 12.6%     | $-1.299  | 🔴          |
| Morning (10:00-12:00)  | 52363 | 13944 | 38419  | 0      | 26.6%     | $-0.210  | 🟢          |
| ORB (9:30-10:00)       | 19539 | 9452  | 10087  | 0      | 48.4%     | $0.842   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 19539  | 0          | 6576       | 12963      | 0.0%      | 33.7%     | 66.3%     |
| Morning (10:00-12:00)  | 52363  | 8          | 15314      | 37041      | 0.0%      | 29.2%     | 70.7%     |
| Afternoon (12:00-16:00) | 54600  | 0          | 19792      | 34808      | 0.0%      | 36.2%     | 63.8%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 1964   | 1360  | 604    | 0      | 69.2%     | $3.097       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 10999  | 6428  | 4571   | 0      | 58.4%     | $1.406       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 4760   | 1328  | 3432   | 0      | 27.9%     | $-0.376      | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 1816   | 336   | 1480   | 0      | 18.5%     | $-1.825      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 64     | 0     | 64     | 0      | 0.0%      | $-2.320      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 7320   | 2237  | 5083   | 0      | 30.6%     | $-0.207      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 29657  | 10867 | 18790  | 0      | 36.6%     | $0.442       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 11138  | 784   | 10354  | 0      | 7.0%      | $-1.103      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 4176   | 48    | 4128   | 0      | 1.1%      | $-2.442      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 8      | 8     | 0      | 0      | 100.0%    | $1.350       | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 7043   | 1172  | 5871   | 0      | 16.6%     | $-0.962      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 27765  | 3999  | 23766  | 0      | 14.4%     | $-0.866      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 14512  | 1684  | 12828  | 0      | 11.6%     | $-1.752      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 5280   | 16    | 5264   | 0      | 0.3%      | $-2.781      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 123491 | 29684 | 93807  | 0      | 24.0%     | $-0.527  |
| SHORT        | 3011  | 583   | 2428   | 0      | 19.4%     | $-0.129  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 23431 | 4368  | 19063  | 0      | 18.6%     | $-0.572  |
| Long (30-60 min)       | 18813 | 6437  | 12376  | 0      | 34.2%     | $0.042   |
| Medium (5-15 min)      | 29800 | 8862  | 20938  | 0      | 29.7%     | $0.036   |
| Slow (15-30 min)       | 17505 | 5542  | 11963  | 0      | 31.7%     | $-0.003  |
| Very Fast (<1 min)     | 4991  | 216   | 4775   | 0      | 4.3%      | $-0.854  |
| Very Long (>1h)        | 31962 | 4842  | 27120  | 0      | 15.1%     | $-1.553  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 23.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.52 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.37) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $2.69) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (48.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (10269s / 171.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_wall_bounce

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 174,075  |  **Win Rate:** 57.1%  |  **Avg P&L (resolved):** $1.695  |  **Avg P&L (all):** $1.695  |  **Avg Hold:** 41664s (694.4m)  |  **Median Hold:** 6759s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 620   | 421   | 199    | 0      | 67.9%     | $3.825   | $3.825   | 69.8%    |
| 10-19%         | 1753  | 964   | 789    | 0      | 55.0%     | $2.769   | $2.769   | 37.5%    |
| 20-29%         | 7178  | 1343  | 5835   | 0      | 18.7%     | $-1.739  | $-1.739  | -53.2%   |
| 30-39%         | 13559 | 5328  | 8231   | 0      | 39.3%     | $0.357   | $0.357   | -1.8%    |
| 40-49%         | 19575 | 9399  | 10176  | 0      | 48.0%     | $0.669   | $0.669   | 20.3%    |
| 50-59%         | 15762 | 7310  | 8452   | 0      | 46.4%     | $0.484   | $0.484   | 21.4%    |
| 60-69%         | 10660 | 4808  | 5852   | 0      | 45.1%     | $0.258   | $0.258   | 16.9%    |
| 70-79%         | 9775  | 3230  | 6545   | 0      | 33.0%     | $0.015   | $0.015   | -11.9%   |
| 80-89%         | 4487  | 2410  | 2077   | 0      | 53.7%     | $2.015   | $2.015   | 34.8%    |
| 90-99%         | 4286  | 3058  | 1228   | 0      | 71.3%     | $2.645   | $2.645   | 80.2%    |
| 100%           | 86420 | 61114 | 25306  | 0      | 70.7%     | $2.910   | $2.910   | 79.3%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 100026 | 55727 | 44299  | 0      | 55.7%     | $1.586   |
| Trending (Up)        | 74049 | 43658 | 30391  | 0      | 59.0%     | $1.842   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 7201  | 2535  | 4666   | 0      | 35.2%     | $-0.040  |
| Positive Gamma (Range-Bound friendly) | 166874 | 96850 | 70024  | 0      | 58.0%     | $1.770   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 3424  | 2720  | 704    | 0      | 79.4%     | $1.809   |
| Time Held: 30-90m      | 22692 | 13471 | 9221   | 0      | 59.4%     | $0.936   |
| Time Held: 90-240m     | 11405 | 9626  | 1779   | 0      | 84.4%     | $1.916   |
| Time Held: <30m        | 61154 | 21808 | 39346  | 0      | 35.7%     | $-0.216  |
| Time Held: >480m       | 75400 | 51760 | 23640  | 0      | 68.6%     | $3.435   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 101356 | 63042 | 38314  | 0      | 62.2%     | $2.037   | 🟢          |
| Morning (10:00-12:00)  | 53743 | 29759 | 23984  | 0      | 55.4%     | $1.660   | 🔴          |
| ORB (9:30-10:00)       | 18976 | 6584  | 12392  | 0      | 34.7%     | $-0.034  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 18976  | 6068       | 3960       | 8948       | 32.0%     | 20.9%     | 47.2%     |
| Morning (10:00-12:00)  | 53743  | 22906      | 10288      | 20549      | 42.6%     | 19.1%     | 38.2%     |
| Afternoon (12:00-16:00) | 101356 | 75994      | 12174      | 13188      | 75.0%     | 12.0%     | 13.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 2472   | 568   | 1904   | 0      | 23.0%     | $-1.101      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 3784   | 368   | 3416   | 0      | 9.7%      | $-2.473      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 2692   | 424   | 2268   | 0      | 15.8%     | $-1.468      | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 1812   | 424   | 1388   | 0      | 23.4%     | $-0.490      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 2148   | 1160  | 988    | 0      | 54.0%     | $0.260       | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 308    | 196   | 112    | 0      | 63.6%     | $1.530       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 160    | 136   | 24     | 0      | 85.0%     | $2.096       | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 72     | 28    | 44     | 0      | 38.9%     | $0.252       | 🔴          |
| ORB (9:30-10:00)       | 100%       | 5528   | 3280  | 2248   | 0      | 59.3%     | $2.695       | 🟢          |
| Morning (10:00-12:00)  | 5-9%       | 134    | 5     | 129    | 0      | 3.7%      | $-0.683      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 652    | 71    | 581    | 0      | 10.9%     | $-0.656      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 3266   | 327   | 2939   | 0      | 10.0%     | $-3.142      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 6205   | 3667  | 2538   | 0      | 59.1%     | $2.043       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 10292  | 6115  | 4177   | 0      | 59.4%     | $1.187       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 7268   | 3784  | 3484   | 0      | 52.1%     | $0.666       | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 3020   | 1736  | 1284   | 0      | 57.5%     | $1.243       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 2893   | 800   | 2093   | 0      | 27.7%     | $-0.753      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 435    | 88    | 347    | 0      | 20.2%     | $-0.734      | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 780    | 80    | 700    | 0      | 10.3%     | $-0.956      | 🔴          |
| Morning (10:00-12:00)  | 100%       | 18798  | 13086 | 5712   | 0      | 69.6%     | $3.710       | 🟢          |
| Afternoon (12:00-16:00) | 5-9%       | 486    | 416   | 70     | 0      | 85.6%     | $5.068       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 1101   | 893   | 208    | 0      | 81.1%     | $4.797       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 1440   | 448   | 992    | 0      | 31.1%     | $0.347       | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 3570   | 1293  | 2277   | 0      | 36.2%     | $0.425       | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 6591   | 2860  | 3731   | 0      | 43.4%     | $0.734       | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 6682   | 3102  | 3580   | 0      | 46.4%     | $0.550       | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 5492   | 1912  | 3580   | 0      | 34.8%     | $-0.284      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 6574   | 2234  | 4340   | 0      | 34.0%     | $0.281       | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 3892   | 2186  | 1706   | 0      | 56.2%     | $2.319       | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 3434   | 2950  | 484    | 0      | 85.9%     | $3.514       | 🟢          |
| Afternoon (12:00-16:00) | 100%       | 62094  | 44748 | 17346  | 0      | 72.1%     | $2.687       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 70226 | 20534 | 49692  | 0      | 29.2%     | $-1.528  |
| SHORT        | 103849 | 78851 | 24998  | 0      | 75.9%     | $3.875   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 14836 | 3196  | 11640  | 0      | 21.5%     | $-1.333  |
| Long (30-60 min)       | 18147 | 11515 | 6632   | 0      | 63.5%     | $1.097   |
| Medium (5-15 min)      | 25993 | 8361  | 17632  | 0      | 32.2%     | $-0.562  |
| Slow (15-30 min)       | 17636 | 9467  | 8169   | 0      | 53.7%     | $1.347   |
| Very Fast (<1 min)     | 2689  | 784   | 1905   | 0      | 29.2%     | $-0.969  |
| Very Long (>1h)        | 94774 | 66062 | 28712  | 0      | 69.7%     | $3.043   |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 57.1% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 💰 Positive avg P&L per resolved signal: $1.70 — profitable even with 57.1% win rate (good risk/reward).
- 🎯 Best performance at 90-99% confidence (71.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (18.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $1.84) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $3.44) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (62.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (41664s / 694.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_divergence

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 234,643  |  **Win Rate:** 35.3%  |  **Avg P&L (resolved):** $-0.132  |  **Avg P&L (all):** $-0.132  |  **Avg Hold:** 3242s (54.0m)  |  **Median Hold:** 926s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 50-59%         | 20250 | 7914  | 12336  | 0      | 39.1%     | $0.404   | $0.404   | -2.3%    |
| 60-69%         | 118970 | 43521 | 75449  | 0      | 36.6%     | $-0.213  | $-0.213  | -8.5%    |
| 70-79%         | 74820 | 22869 | 51951  | 0      | 30.6%     | $-0.271  | $-0.271  | -23.6%   |
| 80-89%         | 18421 | 7611  | 10810  | 0      | 41.3%     | $0.375   | $0.375   | 3.3%     |
| 90-99%         | 2178  | 955   | 1223   | 0      | 43.8%     | $-0.219  | $-0.219  | 9.5%     |
| 100%           | 4     | 4     | 0      | 0      | 100.0%    | $1.200   | $1.200   | 150.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 175008 | 64110 | 110898 | 0      | 36.6%     | $-0.135  |
| Trending (Up)        | 59635 | 18764 | 40871  | 0      | 31.5%     | $-0.126  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 4504  | 1295  | 3209   | 0      | 28.8%     | $-0.183  |
| Positive Gamma (Range-Bound friendly) | 230139 | 81579 | 148560 | 0      | 35.4%     | $-0.131  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1088  | 0     | 1088   | 0      | 0.0%      | $-1.141  |
| Time Held: 30-90m      | 54172 | 27553 | 26619  | 0      | 50.9%     | $0.312   |
| Time Held: 90-240m     | 16944 | 9132  | 7812   | 0      | 53.9%     | $0.616   |
| Time Held: <30m        | 157703 | 43533 | 114170 | 0      | 27.6%     | $-0.402  |
| Time Held: >480m       | 4736  | 2656  | 2080   | 0      | 56.1%     | $1.306   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 101314 | 39215 | 62099  | 0      | 38.7%     | $0.002   | 🟢          |
| Morning (10:00-12:00)  | 107178 | 34347 | 72831  | 0      | 32.0%     | $-0.266  | 🔴          |
| ORB (9:30-10:00)       | 26151 | 9312  | 16839  | 0      | 35.6%     | $-0.107  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 26151  | 12086      | 14065      | 0          | 46.2%     | 53.8%     | 0.0%      |
| Morning (10:00-12:00)  | 107178 | 52628      | 54550      | 0          | 49.1%     | 50.9%     | 0.0%      |
| Afternoon (12:00-16:00) | 101314 | 30709      | 70605      | 0          | 30.3%     | 69.7%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 50-59%     | 2344   | 104   | 2240   | 0      | 4.4%      | $-1.178      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 11721  | 4455  | 7266   | 0      | 38.0%     | $-0.159      | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 6076   | 2290  | 3786   | 0      | 37.7%     | $-0.027      | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 5422   | 2127  | 3295   | 0      | 39.2%     | $0.305       | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 588    | 336   | 252    | 0      | 57.1%     | $0.589       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 6766   | 1524  | 5242   | 0      | 22.5%     | $-0.332      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 47784  | 15520 | 32264  | 0      | 32.5%     | $-0.350      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 40553  | 12119 | 28434  | 0      | 29.9%     | $-0.342      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 10551  | 4564  | 5987   | 0      | 43.3%     | $0.476       | 🟢          |
| Morning (10:00-12:00)  | 90-99%     | 1520   | 616   | 904    | 0      | 40.5%     | $-0.465      | 🟢          |
| Morning (10:00-12:00)  | 100%       | 4      | 4     | 0      | 0      | 100.0%    | $1.200       | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 11140  | 6286  | 4854   | 0      | 56.4%     | $1.184       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 59465  | 23546 | 35919  | 0      | 39.6%     | $-0.114      | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 28191  | 8460  | 19731  | 0      | 30.0%     | $-0.222      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 2448   | 920   | 1528   | 0      | 37.6%     | $0.091       | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 70     | 3     | 67     | 0      | 4.3%      | $-1.660      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 184632 | 66729 | 117903 | 0      | 36.1%     | $-0.171  |
| SHORT        | 50011 | 16145 | 33866  | 0      | 32.3%     | $0.010   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 40673 | 10666 | 30007  | 0      | 26.2%     | $-0.550  |
| Long (30-60 min)       | 36911 | 17417 | 19494  | 0      | 47.2%     | $0.205   |
| Medium (5-15 min)      | 68137 | 19879 | 48258  | 0      | 29.2%     | $-0.302  |
| Slow (15-30 min)       | 42271 | 12166 | 30105  | 0      | 28.8%     | $-0.366  |
| Very Fast (<1 min)     | 6622  | 822   | 5800   | 0      | 12.4%     | $-0.751  |
| Very Long (>1h)        | 40029 | 21924 | 18105  | 0      | 54.8%     | $0.618   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 35.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.13 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 90-99% confidence (43.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (30.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.13) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $1.31) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (38.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3242s / 54.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_imbalance

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 509,127  |  **Win Rate:** 42.5%  |  **Avg P&L (resolved):** $0.083  |  **Avg P&L (all):** $0.083  |  **Avg Hold:** 587s (9.8m)  |  **Median Hold:** 279s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 8     | 0     | 8      | 0      | 0.0%      | $-3.815  | $-3.815  | -100.0%  |
| 10-19%         | 12398 | 4719  | 7679   | 0      | 38.1%     | $0.036   | $0.036   | -4.9%    |
| 20-29%         | 58703 | 17587 | 41116  | 0      | 30.0%     | $-0.320  | $-0.320  | -25.1%   |
| 30-39%         | 62876 | 23751 | 39125  | 0      | 37.8%     | $0.106   | $0.106   | -5.5%    |
| 40-49%         | 129751 | 57564 | 72187  | 0      | 44.4%     | $0.252   | $0.252   | 10.9%    |
| 50-59%         | 200807 | 92689 | 108118 | 0      | 46.2%     | $0.079   | $0.079   | 15.4%    |
| 60-69%         | 42249 | 18903 | 23346  | 0      | 44.7%     | $0.116   | $0.116   | 11.8%    |
| 70-79%         | 2335  | 1100  | 1235   | 0      | 47.1%     | $0.244   | $0.244   | 17.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 296160 | 124452 | 171708 | 0      | 42.0%     | $0.038   |
| Trending (Up)        | 212967 | 91861 | 121106 | 0      | 43.1%     | $0.146   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 7974  | 3161  | 4813   | 0      | 39.6%     | $-0.054  |
| Positive Gamma (Range-Bound friendly) | 501153 | 213152 | 288001 | 0      | 42.5%     | $0.085   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 144   | 144   | 0      | 0      | 100.0%    | $5.595   |
| Time Held: 30-90m      | 26100 | 12980 | 13120  | 0      | 49.7%     | $0.610   |
| Time Held: 90-240m     | 2581  | 1715  | 866    | 0      | 66.4%     | $0.922   |
| Time Held: <30m        | 480014 | 201186 | 278828 | 0      | 41.9%     | $0.047   |
| Time Held: >480m       | 288   | 288   | 0      | 0      | 100.0%    | $2.734   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 260154 | 104520 | 155634 | 0      | 40.2%     | $0.013   | 🔴          |
| Morning (10:00-12:00)  | 199157 | 94721 | 104436 | 0      | 47.6%     | $0.203   | 🟢          |
| ORB (9:30-10:00)       | 49816 | 17072 | 32744  | 0      | 34.3%     | $-0.033  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 49816  | 300        | 25481      | 24035      | 0.6%      | 51.2%     | 48.2%     |
| Morning (10:00-12:00)  | 199157 | 744        | 94130      | 104283     | 0.4%      | 47.3%     | 52.4%     |
| Afternoon (12:00-16:00) | 260154 | 1291       | 123445     | 135418     | 0.5%      | 47.5%     | 52.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 512    | 405   | 107    | 0      | 79.1%     | $1.271       | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 5738   | 446   | 5292   | 0      | 7.8%      | $-1.917      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 8572   | 2794  | 5778   | 0      | 32.6%     | $0.335       | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 9213   | 3782  | 5431   | 0      | 41.1%     | $0.985       | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 21425  | 8209  | 13216  | 0      | 38.3%     | $-0.120      | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 4056   | 1400  | 2656   | 0      | 34.5%     | $-0.135      | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 300    | 36    | 264    | 0      | 12.0%     | $-0.386      | 🔴          |
| Morning (10:00-12:00)  | 5-9%       | 8      | 0     | 8      | 0      | 0.0%      | $-3.815      | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 2752   | 934   | 1818   | 0      | 33.9%     | $-0.050      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 24305  | 8137  | 16168  | 0      | 33.5%     | $-0.192      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 23988  | 9589  | 14399  | 0      | 40.0%     | $0.181       | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 53230  | 27412 | 25818  | 0      | 51.5%     | $0.420       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 77108  | 40751 | 36357  | 0      | 52.8%     | $0.221       | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 17022  | 7530  | 9492   | 0      | 44.2%     | $0.094       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 744    | 368   | 376    | 0      | 49.5%     | $0.008       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 9134   | 3380  | 5754   | 0      | 37.0%     | $-0.008      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 28660  | 9004  | 19656  | 0      | 31.4%     | $-0.109      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 30316  | 11368 | 18948  | 0      | 37.5%     | $-0.017      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 67308  | 26370 | 40938  | 0      | 39.2%     | $0.018       | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 102274 | 43729 | 58545  | 0      | 42.8%     | $0.014       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 21171  | 9973  | 11198  | 0      | 47.1%     | $0.181       | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 1291   | 696   | 595    | 0      | 53.9%     | $0.527       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 98    | 29    | 69     | 0      | 29.6%     | $-2.908  |
| SHORT        | 509029 | 216284 | 292745 | 0      | 42.5%     | $0.084   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 211879 | 80702 | 131177 | 0      | 38.1%     | $-0.040  |
| Long (30-60 min)       | 21615 | 10629 | 10986  | 0      | 49.2%     | $0.656   |
| Medium (5-15 min)      | 156642 | 77746 | 78896  | 0      | 49.6%     | $0.137   |
| Slow (15-30 min)       | 57770 | 29668 | 28102  | 0      | 51.4%     | $0.424   |
| Very Fast (<1 min)     | 53723 | 13070 | 40653  | 0      | 24.3%     | $-0.282  |
| Very Long (>1h)        | 7498  | 4498  | 3000   | 0      | 60.0%     | $0.764   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 42.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.08 — profitable even with 42.5% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (47.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 5-9% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.15) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $5.60) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (47.6% win rate) — statistically significant above overall WR.

---

### magnet_accelerate

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 180,069  |  **Win Rate:** 15.1%  |  **Avg P&L (resolved):** $-0.361  |  **Avg P&L (all):** $-0.361  |  **Avg Hold:** 5102s (85.0m)  |  **Median Hold:** 1361s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 5-9%           | 576   | 256   | 320    | 0      | 44.4%     | $0.037   | $0.037   | 11.2%    |
| 10-19%         | 3392  | 1371  | 2021   | 0      | 40.4%     | $1.375   | $1.375   | 62.1%    |
| 20-29%         | 18717 | 3341  | 15376  | 0      | 17.9%     | $0.295   | $0.295   | -27.3%   |
| 30-39%         | 33108 | 4917  | 28191  | 0      | 14.9%     | $-0.046  | $-0.046  | -38.3%   |
| 40-49%         | 46434 | 7255  | 39179  | 0      | 15.6%     | $-0.453  | $-0.453  | -62.0%   |
| 50-59%         | 45304 | 6751  | 38553  | 0      | 14.9%     | $-0.619  | $-0.619  | -63.8%   |
| 60-69%         | 21847 | 1617  | 20230  | 0      | 7.4%      | $-0.706  | $-0.706  | -79.3%   |
| 70-79%         | 8117  | 1233  | 6884   | 0      | 15.2%     | $-0.714  | $-0.714  | -57.0%   |
| 80-89%         | 2468  | 410   | 2058   | 0      | 16.6%     | $-1.280  | $-1.280  | -63.7%   |
| 90-99%         | 106   | 2     | 104    | 0      | 1.9%      | $-1.392  | $-1.392  | -95.3%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 102905 | 13327 | 89578  | 0      | 13.0%     | $-0.371  |
| Trending (Up)        | 77164 | 13826 | 63338  | 0      | 17.9%     | $-0.347  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 5396  | 1631  | 3765   | 0      | 30.2%     | $0.411   |
| Positive Gamma (Range-Bound friendly) | 174673 | 25522 | 149151 | 0      | 14.6%     | $-0.384  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 14184 | 0     | 14184  | 0      | 0.0%      | $-0.642  |
| Time Held: 30-90m      | 38792 | 4439  | 34353  | 0      | 11.4%     | $-0.292  |
| Time Held: 90-240m     | 19423 | 1738  | 17685  | 0      | 8.9%      | $-0.133  |
| Time Held: <30m        | 101638 | 20720 | 80918  | 0      | 20.4%     | $-0.315  |
| Time Held: >480m       | 6032  | 256   | 5776   | 0      | 4.2%      | $-1.643  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 113425 | 8408  | 105017 | 0      | 7.4%      | $-0.468  | 🔴          |
| Morning (10:00-12:00)  | 52260 | 10147 | 42113  | 0      | 19.4%     | $-0.393  | 🟢          |
| ORB (9:30-10:00)       | 14384 | 8598  | 5786   | 0      | 59.8%     | $0.604   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 14384  | 1464       | 6148       | 6772       | 10.2%     | 42.7%     | 47.1%     |
| Morning (10:00-12:00)  | 52260  | 4108       | 20303      | 27849      | 7.9%      | 38.8%     | 53.3%     |
| Afternoon (12:00-16:00) | 113425 | 5119       | 40700      | 67606      | 4.5%      | 35.9%     | 59.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 138    | 2     | 136    | 0      | 1.4%      | $-2.284      | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 946    | 300   | 646    | 0      | 31.7%     | $0.885       | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 2387   | 1344  | 1043   | 0      | 56.3%     | $1.505       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 3301   | 1915  | 1386   | 0      | 58.0%     | $0.468       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 4451   | 2753  | 1698   | 0      | 61.9%     | $0.155       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 1697   | 1052  | 645    | 0      | 62.0%     | $0.302       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 1344   | 1144  | 200    | 0      | 85.1%     | $1.290       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 120    | 88    | 32     | 0      | 73.3%     | $0.789       | 🟢          |
| Morning (10:00-12:00)  | 5-9%       | 64     | 0     | 64     | 0      | 0.0%      | $-1.640      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 1177   | 536   | 641    | 0      | 45.5%     | $3.347       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 6524   | 664   | 5860   | 0      | 10.2%     | $-0.062      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 7755   | 592   | 7163   | 0      | 7.6%      | $-0.568      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 12329  | 4355  | 7974   | 0      | 35.3%     | $-0.051      | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 15479  | 3462  | 12017  | 0      | 22.4%     | $-0.544      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 4824   | 408   | 4416   | 0      | 8.5%      | $-0.886      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 2726   | 2     | 2724   | 0      | 0.1%      | $-1.439      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 1318   | 128   | 1190   | 0      | 9.7%      | $-1.691      | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 64     | 0     | 64     | 0      | 0.0%      | $-1.190      | 🔴          |
| Afternoon (12:00-16:00) | 5-9%       | 512    | 256   | 256    | 0      | 50.0%     | $0.246       | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 2077   | 833   | 1244   | 0      | 40.1%     | $0.500       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 11247  | 2377  | 8870   | 0      | 21.1%     | $0.453       | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 22966  | 2981  | 19985  | 0      | 13.0%     | $-0.031      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 30804  | 985   | 29819  | 0      | 3.2%      | $-0.713      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 25374  | 536   | 24838  | 0      | 2.1%      | $-0.801      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 15326  | 157   | 15169  | 0      | 1.0%      | $-0.761      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 4047   | 87    | 3960   | 0      | 2.1%      | $-0.892      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 1030   | 194   | 836    | 0      | 18.8%     | $-0.994      | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 42     | 2     | 40     | 0      | 4.8%      | $-1.701      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 136145 | 15441 | 120704 | 0      | 11.3%     | $-0.462  |
| SHORT        | 43924 | 11712 | 32212  | 0      | 26.7%     | $-0.046  |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 24144 | 3962  | 20182  | 0      | 16.4%     | $-0.690  |
| Long (30-60 min)       | 25633 | 2871  | 22762  | 0      | 11.2%     | $-0.486  |
| Medium (5-15 min)      | 38859 | 9375  | 29484  | 0      | 24.1%     | $-0.262  |
| Slow (15-30 min)       | 31383 | 6105  | 25278  | 0      | 19.5%     | $-0.156  |
| Very Fast (<1 min)     | 7252  | 1278  | 5974   | 0      | 17.6%     | $-0.039  |
| Very Long (>1h)        | 52798 | 3562  | 49236  | 0      | 6.7%      | $-0.387  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.36 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 5-9% confidence (44.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (1.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.35) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $-0.13) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (59.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (5102s / 85.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### order_book_fragmentation

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 479,502  |  **Win Rate:** 24.9%  |  **Avg P&L (resolved):** $-0.034  |  **Avg P&L (all):** $-0.034  |  **Avg Hold:** 4752s (79.2m)  |  **Median Hold:** 800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 328   | 0     | 328    | 0      | 0.0%      | $-1.226  | $-1.226  | -100.0%  |
| 30-39%         | 3192  | 551   | 2641   | 0      | 17.3%     | $-0.381  | $-0.381  | -31.0%   |
| 40-49%         | 72439 | 17586 | 54853  | 0      | 24.3%     | $-0.016  | $-0.016  | -2.9%    |
| 50-59%         | 198356 | 51663 | 146693 | 0      | 26.0%     | $0.024   | $0.024   | 4.2%     |
| 60-69%         | 113173 | 28367 | 84806  | 0      | 25.1%     | $-0.059  | $-0.059  | 0.3%     |
| 70-79%         | 76506 | 17938 | 58568  | 0      | 23.4%     | $-0.137  | $-0.137  | -6.2%    |
| 80-89%         | 15071 | 3375  | 11696  | 0      | 22.4%     | $-0.079  | $-0.079  | -10.6%   |
| 90-99%         | 297   | 97    | 200    | 0      | 32.7%     | $0.381   | $0.381   | 29.9%    |
| 100%           | 140   | 32    | 108    | 0      | 22.9%     | $-0.539  | $-0.539  | -9.2%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 479502 | 119609 | 359893 | 0      | 24.9%     | $-0.034  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 479502 | 119609 | 359893 | 0      | 24.9%     | $-0.034  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1858  | 608   | 1250   | 0      | 32.7%     | $-0.419  |
| Time Held: 30-90m      | 93370 | 30329 | 63041  | 0      | 32.5%     | $0.202   |
| Time Held: 90-240m     | 37430 | 23286 | 14144  | 0      | 62.2%     | $0.855   |
| Time Held: <30m        | 327364 | 56082 | 271282 | 0      | 17.1%     | $-0.323  |
| Time Held: >480m       | 19480 | 9304  | 10176  | 0      | 47.8%     | $2.017   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 236320 | 57214 | 179106 | 0      | 24.2%     | $0.005   | 🔴          |
| Morning (10:00-12:00)  | 193796 | 48675 | 145121 | 0      | 25.1%     | $-0.086  | 🟢          |
| ORB (9:30-10:00)       | 49386 | 13720 | 35666  | 0      | 27.8%     | $-0.017  | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 49386  | 13290      | 29176      | 6920       | 26.9%     | 59.1%     | 14.0%     |
| Morning (10:00-12:00)  | 193796 | 39736      | 126198     | 27862      | 20.5%     | 65.1%     | 14.4%     |
| Afternoon (12:00-16:00) | 236320 | 38988      | 156155     | 41177      | 16.5%     | 66.1%     | 17.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 256    | 0     | 256    | 0      | 0.0%      | $-1.260      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 913    | 65    | 848    | 0      | 7.1%      | $-0.909      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 5751   | 1709  | 4042   | 0      | 29.7%     | $-0.041      | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 16067  | 4364  | 11703  | 0      | 27.2%     | $0.016       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 13109  | 3503  | 9606   | 0      | 26.7%     | $-0.143      | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 11238  | 3418  | 7820   | 0      | 30.4%     | $0.182       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 1983   | 628   | 1355   | 0      | 31.7%     | $0.089       | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 1      | 1     | 0      | 0      | 100.0%    | $1.450       | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 68     | 32    | 36     | 0      | 47.1%     | $-0.579      | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 72     | 0     | 72     | 0      | 0.0%      | $-1.103      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 648    | 64    | 584    | 0      | 9.9%      | $-0.958      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 27142  | 6609  | 20533  | 0      | 24.3%     | $-0.035      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 77489  | 20102 | 57387  | 0      | 25.9%     | $-0.082      | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 48709  | 13337 | 35372  | 0      | 27.4%     | $0.009       | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 32180  | 6749  | 25431  | 0      | 21.0%     | $-0.300      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 7316   | 1782  | 5534   | 0      | 24.4%     | $0.106       | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 232    | 32    | 200    | 0      | 13.8%     | $-0.486      | 🔴          |
| Morning (10:00-12:00)  | 100%       | 8      | 0     | 8      | 0      | 0.0%      | $-1.630      | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 1631   | 422   | 1209   | 0      | 25.9%     | $0.143       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 39546  | 9268  | 30278  | 0      | 23.4%     | $-0.000      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 104800 | 27197 | 77603  | 0      | 26.0%     | $0.104       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 51355  | 11527 | 39828  | 0      | 22.4%     | $-0.102      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 33088  | 7771  | 25317  | 0      | 23.5%     | $-0.085      | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 5772   | 965   | 4807   | 0      | 16.7%     | $-0.370      | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 64     | 64    | 0      | 0      | 100.0%    | $3.510       | 🟢          |
| Afternoon (12:00-16:00) | 100%       | 64     | 0     | 64     | 0      | 0.0%      | $-0.360      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 244200 | 57254 | 186946 | 0      | 23.4%     | $-0.232  |
| SHORT        | 235302 | 62355 | 172947 | 0      | 26.5%     | $0.171   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 107158 | 11999 | 95159  | 0      | 11.2%     | $-0.595  |
| Long (30-60 min)       | 63296 | 19387 | 43909  | 0      | 30.6%     | $0.132   |
| Medium (5-15 min)      | 113619 | 23359 | 90260  | 0      | 20.6%     | $-0.175  |
| Slow (15-30 min)       | 74604 | 19994 | 54610  | 0      | 26.8%     | $0.075   |
| Very Fast (<1 min)     | 31983 | 730   | 31253  | 0      | 2.3%      | $-0.862  |
| Very Long (>1h)        | 88842 | 44140 | 44702  | 0      | 49.7%     | $0.912   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.03 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 90-99% confidence (32.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.03) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $2.02) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (27.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4752s / 79.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_divergence_scalper

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 491,594  |  **Win Rate:** 40.5%  |  **Avg P&L (resolved):** $0.002  |  **Avg P&L (all):** $0.002  |  **Avg Hold:** 3115s (51.9m)  |  **Median Hold:** 499s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 1056  | 224   | 832    | 0      | 21.2%     | $-0.805  | $-0.805  | -47.0%   |
| 20-29%         | 34157 | 11350 | 22807  | 0      | 33.2%     | $-0.157  | $-0.157  | -16.9%   |
| 30-39%         | 156665 | 65221 | 91444  | 0      | 41.6%     | $0.102   | $0.102   | 4.0%     |
| 40-49%         | 204763 | 85363 | 119400 | 0      | 41.7%     | $-0.014  | $-0.014  | 4.2%     |
| 50-59%         | 87966 | 34708 | 53258  | 0      | 39.5%     | $-0.052  | $-0.052  | -1.3%    |
| 60-69%         | 6886  | 2368  | 4518   | 0      | 34.4%     | $-0.150  | $-0.150  | -14.0%   |
| 70-79%         | 101   | 1     | 100    | 0      | 1.0%      | $-0.947  | $-0.947  | -97.5%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 491594 | 199235 | 292359 | 0      | 40.5%     | $0.002   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 16537 | 7223  | 9314   | 0      | 43.7%     | $0.160   |
| Positive Gamma (Range-Bound friendly) | 475057 | 192012 | 283045 | 0      | 40.4%     | $-0.003  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1164  | 490   | 674    | 0      | 42.1%     | $0.116   |
| Time Held: 30-90m      | 72464 | 38348 | 34116  | 0      | 52.9%     | $0.230   |
| Time Held: 90-240m     | 9268  | 3702  | 5566   | 0      | 39.9%     | $-0.318  |
| Time Held: <30m        | 391866 | 148319 | 243547 | 0      | 37.8%     | $-0.056  |
| Time Held: >480m       | 16832 | 8376  | 8456   | 0      | 49.8%     | $0.553   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 247161 | 102538 | 144623 | 0      | 41.5%     | $0.023   | 🟢          |
| Morning (10:00-12:00)  | 194880 | 76416 | 118464 | 0      | 39.2%     | $-0.033  | 🔴          |
| ORB (9:30-10:00)       | 49553 | 20281 | 29272  | 0      | 40.9%     | $0.039   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 49553  | 32         | 12394      | 37127      | 0.1%      | 25.0%     | 74.9%     |
| Morning (10:00-12:00)  | 194880 | 4          | 42742      | 152134     | 0.0%      | 21.9%     | 78.1%     |
| Afternoon (12:00-16:00) | 247161 | 65         | 39716      | 207380     | 0.0%      | 16.1%     | 83.9%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 8      | 0     | 8      | 0      | 0.0%      | $-1.650      | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 2807   | 618   | 2189   | 0      | 22.0%     | $-0.390      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 14535  | 4676  | 9859   | 0      | 32.2%     | $-0.161      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 19777  | 8855  | 10922  | 0      | 44.8%     | $0.135       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 10990  | 5452  | 5538   | 0      | 49.6%     | $0.235       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 1404   | 680   | 724    | 0      | 48.4%     | $0.138       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 32     | 0     | 32     | 0      | 0.0%      | $-2.230      | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 360    | 8     | 352    | 0      | 2.2%      | $-1.566      | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 13201  | 3250  | 9951   | 0      | 24.6%     | $-0.434      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 59289  | 24382 | 34907  | 0      | 41.1%     | $0.010       | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 79284  | 32752 | 46532  | 0      | 41.3%     | $0.008       | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 39772  | 15259 | 24513  | 0      | 38.4%     | $-0.017      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 2970   | 765   | 2205   | 0      | 25.8%     | $-0.221      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 4      | 0     | 4      | 0      | 0.0%      | $-0.320      | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 688    | 216   | 472    | 0      | 31.4%     | $-0.398      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 18149  | 7482  | 10667  | 0      | 41.2%     | $0.080       | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 82841  | 36163 | 46678  | 0      | 43.7%     | $0.214       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 105702 | 43756 | 61946  | 0      | 41.4%     | $-0.059      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 37204  | 13997 | 23207  | 0      | 37.6%     | $-0.174      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 2512   | 923   | 1589   | 0      | 36.7%     | $-0.226      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 65     | 1     | 64     | 0      | 1.5%      | $-0.353      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 251353 | 102197 | 149156 | 0      | 40.7%     | $-0.060  |
| SHORT        | 240241 | 97038 | 143203 | 0      | 40.4%     | $0.068   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 138470 | 48150 | 90320  | 0      | 34.8%     | $-0.120  |
| Long (30-60 min)       | 54936 | 28972 | 25964  | 0      | 52.7%     | $0.242   |
| Medium (5-15 min)      | 139809 | 60105 | 79704  | 0      | 43.0%     | $0.060   |
| Slow (15-30 min)       | 73064 | 29399 | 43665  | 0      | 40.2%     | $-0.013  |
| Very Fast (<1 min)     | 40523 | 10665 | 29858  | 0      | 26.3%     | $-0.317  |
| Very Long (>1h)        | 44792 | 21944 | 22848  | 0      | 49.0%     | $0.220   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 40.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.00 — profitable even with 40.5% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (41.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (1.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.00) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $0.55) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (41.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3115s / 51.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_diversity_conviction

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 350,748  |  **Win Rate:** 25.2%  |  **Avg P&L (resolved):** $-0.623  |  **Avg P&L (all):** $-0.623  |  **Avg Hold:** 10191s (169.9m)  |  **Median Hold:** 2962s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 45840 | 15815 | 30025  | 0      | 34.5%     | $0.134   | $0.134   | 3.5%     |
| 40-49%         | 118827 | 31172 | 87655  | 0      | 26.2%     | $-0.485  | $-0.485  | -21.3%   |
| 50-59%         | 138140 | 28773 | 109367 | 0      | 20.8%     | $-1.033  | $-1.033  | -37.5%   |
| 60-69%         | 39140 | 9979  | 29161  | 0      | 25.5%     | $-0.586  | $-0.586  | -23.6%   |
| 70-79%         | 6799  | 1791  | 5008   | 0      | 26.3%     | $-0.185  | $-0.185  | -21.0%   |
| 80-89%         | 2002  | 779   | 1223   | 0      | 38.9%     | $-0.022  | $-0.022  | 16.5%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 350748 | 88309 | 262439 | 0      | 25.2%     | $-0.623  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 12562 | 3423  | 9139   | 0      | 27.2%     | $-0.350  |
| Positive Gamma (Range-Bound friendly) | 338186 | 84886 | 253300 | 0      | 25.1%     | $-0.633  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 13415 | 4546  | 8869   | 0      | 33.9%     | $0.223   |
| Time Held: 30-90m      | 97425 | 24492 | 72933  | 0      | 25.1%     | $-0.180  |
| Time Held: 90-240m     | 78865 | 25989 | 52876  | 0      | 33.0%     | $-0.137  |
| Time Held: <30m        | 129611 | 19498 | 110113 | 0      | 15.0%     | $-1.406  |
| Time Held: >480m       | 31432 | 13784 | 17648  | 0      | 43.9%     | $-0.344  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 149976 | 31302 | 118674 | 0      | 20.9%     | $-0.723  | 🔴          |
| Morning (10:00-12:00)  | 152437 | 39159 | 113278 | 0      | 25.7%     | $-0.767  | 🟢          |
| ORB (9:30-10:00)       | 48335 | 17848 | 30487  | 0      | 36.9%     | $0.145   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 48335  | 1213       | 22840      | 24282      | 2.5%      | 47.3%     | 50.2%     |
| Morning (10:00-12:00)  | 152437 | 4479       | 77350      | 70608      | 2.9%      | 50.7%     | 46.3%     |
| Afternoon (12:00-16:00) | 149976 | 3109       | 77090      | 69777      | 2.1%      | 51.4%     | 46.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 10201  | 2658  | 7543   | 0      | 26.1%     | $-0.746      | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 14081  | 5157  | 8924   | 0      | 36.6%     | $0.559       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 17361  | 6135  | 11226  | 0      | 35.3%     | $-0.063      | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 5479   | 2961  | 2518   | 0      | 54.0%     | $0.990       | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 629    | 393   | 236    | 0      | 62.5%     | $1.666       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 584    | 544   | 40     | 0      | 93.2%     | $2.286       | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 21717  | 7205  | 14512  | 0      | 33.2%     | $-0.119      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 48891  | 10708 | 38183  | 0      | 21.9%     | $-1.162      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 61860  | 14991 | 46869  | 0      | 24.2%     | $-0.861      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 15490  | 5498  | 9992   | 0      | 35.5%     | $-0.108      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 4002   | 693   | 3309   | 0      | 17.3%     | $-0.528      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 477    | 64    | 413    | 0      | 13.4%     | $-0.926      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 13922  | 5952  | 7970   | 0      | 42.8%     | $1.175       | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 55855  | 15307 | 40548  | 0      | 27.4%     | $-0.156      | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 58919  | 7647  | 51272  | 0      | 13.0%     | $-1.499      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 18171  | 1520  | 16651  | 0      | 8.4%      | $-1.469      | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 2168   | 705   | 1463   | 0      | 32.5%     | $-0.088      | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 941    | 171   | 770    | 0      | 18.2%     | $-0.996      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 181532 | 35666 | 145866 | 0      | 19.6%     | $-1.239  |
| SHORT        | 169216 | 52643 | 116573 | 0      | 31.1%     | $0.039   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 22651 | 1206  | 21445  | 0      | 5.3%      | $-1.978  |
| Long (30-60 min)       | 62464 | 15237 | 47227  | 0      | 24.4%     | $-0.277  |
| Medium (5-15 min)      | 49528 | 6449  | 43079  | 0      | 13.0%     | $-1.535  |
| Slow (15-30 min)       | 55738 | 11810 | 43928  | 0      | 21.2%     | $-1.050  |
| Very Fast (<1 min)     | 1694  | 33    | 1661   | 0      | 1.9%      | $-1.698  |
| Very Long (>1h)        | 158673 | 53574 | 105099 | 0      | 33.8%     | $-0.119  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.62 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (38.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (20.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.62) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $0.22) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (36.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (10191s / 169.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### prob_weighted_magnet

**Symbols:** AMD, INTC, MU, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 813,404  |  **Win Rate:** 20.0%  |  **Avg P&L (resolved):** $-0.314  |  **Avg P&L (all):** $-0.314  |  **Avg Hold:** 6995s (116.6m)  |  **Median Hold:** 1661s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 269386 | 66007 | 203379 | 0      | 24.5%     | $-0.139  | $-0.139  | -2.0%    |
| 40-49%         | 501388 | 82521 | 418867 | 0      | 16.5%     | $-0.480  | $-0.480  | -34.1%   |
| 50-59%         | 42630 | 14208 | 28422  | 0      | 33.3%     | $0.534   | $0.534   | 33.3%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 480467 | 96565 | 383902 | 0      | 20.1%     | $-0.323  |
| Trending (Up)        | 332937 | 66171 | 266766 | 0      | 19.9%     | $-0.300  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 813404 | 162736 | 650668 | 0      | 20.0%     | $-0.314  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 18754 | 6816  | 11938  | 0      | 36.3%     | $0.958   |
| Time Held: 30-90m      | 211821 | 38269 | 173552 | 0      | 18.1%     | $-0.223  |
| Time Held: 90-240m     | 115166 | 52345 | 62821  | 0      | 45.5%     | $0.778   |
| Time Held: <30m        | 423031 | 47610 | 375421 | 0      | 11.3%     | $-0.853  |
| Time Held: >480m       | 44632 | 17696 | 26936  | 0      | 39.6%     | $1.011   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 371518 | 57541 | 313977 | 0      | 15.5%     | $-0.438  | 🔴          |
| Morning (10:00-12:00)  | 345236 | 74447 | 270789 | 0      | 21.6%     | $-0.381  | 🟢          |
| ORB (9:30-10:00)       | 96650 | 30748 | 65902  | 0      | 31.8%     | $0.402   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 96650  | 0          | 5276       | 91374      | 0.0%      | 5.5%      | 94.5%     |
| Morning (10:00-12:00)  | 345236 | 0          | 17334      | 327902     | 0.0%      | 5.0%      | 95.0%     |
| Afternoon (12:00-16:00) | 371518 | 0          | 20020      | 351498     | 0.0%      | 5.4%      | 94.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 38468  | 12174 | 26294  | 0      | 31.6%     | $0.637       | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 52906  | 18182 | 34724  | 0      | 34.4%     | $0.452       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 5276   | 392   | 4884   | 0      | 7.4%      | $-1.812      | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 132279 | 31936 | 100343 | 0      | 24.1%     | $-0.370      | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 195623 | 35679 | 159944 | 0      | 18.2%     | $-0.400      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 17334  | 6832  | 10502  | 0      | 39.4%     | $-0.253      | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 98639  | 21897 | 76742  | 0      | 22.2%     | $-0.133      | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 252859 | 28660 | 224199 | 0      | 11.3%     | $-0.736      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 20020  | 6984  | 13036  | 0      | 34.9%     | $1.834       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 421915 | 73234 | 348681 | 0      | 17.4%     | $-0.614  |
| SHORT        | 391489 | 89502 | 301987 | 0      | 22.9%     | $0.010   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 104978 | 3139  | 101839 | 0      | 3.0%      | $-1.388  |
| Long (30-60 min)       | 137123 | 21355 | 115768 | 0      | 15.6%     | $-0.447  |
| Medium (5-15 min)      | 166752 | 17989 | 148763 | 0      | 10.8%     | $-0.942  |
| Slow (15-30 min)       | 136935 | 26473 | 110462 | 0      | 19.3%     | $-0.268  |
| Very Fast (<1 min)     | 14366 | 9     | 14357  | 0      | 0.1%      | $-1.490  |
| Very Long (>1h)        | 253250 | 93771 | 159479 | 0      | 37.0%     | $0.658   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 20.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.31 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (33.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (16.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.30) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $1.01) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (31.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6995s / 116.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### strike_concentration

**Symbols:** AMD, INTC, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 84,107  |  **Win Rate:** 36.5%  |  **Avg P&L (resolved):** $-0.415  |  **Avg P&L (all):** $-0.415  |  **Avg Hold:** 12797s (213.3m)  |  **Median Hold:** 2521s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 56    | 48    | 8      | 0      | 85.7%     | $1.451   | $1.451   | 38.2%    |
| 30-39%         | 2288  | 820   | 1468   | 0      | 35.8%     | $-0.637  | $-0.637  | -28.7%   |
| 40-49%         | 23056 | 7236  | 15820  | 0      | 31.4%     | $-0.665  | $-0.665  | -34.3%   |
| 50-59%         | 36599 | 12558 | 24041  | 0      | 34.3%     | $-0.381  | $-0.381  | -19.1%   |
| 60-69%         | 12744 | 6851  | 5893   | 0      | 53.8%     | $-0.096  | $-0.096  | 28.8%    |
| 70-79%         | 8240  | 3104  | 5136   | 0      | 37.7%     | $-0.109  | $-0.109  | -5.6%    |
| 80-89%         | 1124  | 96    | 1028   | 0      | 8.5%      | $-1.940  | $-1.940  | -79.6%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 49622 | 19051 | 30571  | 0      | 38.4%     | $-0.193  |
| Trending (Up)        | 34485 | 11662 | 22823  | 0      | 33.8%     | $-0.736  |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 84107 | 30713 | 53394  | 0      | 36.5%     | $-0.415  |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1858  | 64    | 1794   | 0      | 3.4%      | $-2.466  |
| Time Held: 30-90m      | 20919 | 7099  | 13820  | 0      | 33.9%     | $-0.297  |
| Time Held: 90-240m     | 12745 | 3401  | 9344   | 0      | 26.7%     | $-0.414  |
| Time Held: <30m        | 35777 | 16085 | 19692  | 0      | 45.0%     | $-0.194  |
| Time Held: >480m       | 12808 | 4064  | 8744   | 0      | 31.7%     | $-0.930  |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 50444 | 19684 | 30760  | 0      | 39.0%     | $-0.302  | 🟢          |
| Morning (10:00-12:00)  | 29141 | 8872  | 20269  | 0      | 30.4%     | $-0.723  | 🔴          |
| ORB (9:30-10:00)       | 4522  | 2157  | 2365   | 0      | 47.7%     | $0.302   | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 4522   | 1016       | 2200       | 1306       | 22.5%     | 48.7%     | 28.9%     |
| Morning (10:00-12:00)  | 29141  | 2744       | 14075      | 12322      | 9.4%      | 48.3%     | 42.3%     |
| Afternoon (12:00-16:00) | 50444  | 5604       | 33068      | 11772      | 11.1%     | 65.6%     | 23.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 332    | 160   | 172    | 0      | 48.2%     | $-0.371      | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 974    | 516   | 458    | 0      | 53.0%     | $1.578       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 1745   | 692   | 1053   | 0      | 39.7%     | $-0.708      | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 455    | 221   | 234    | 0      | 48.6%     | $-0.364      | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 760    | 472   | 288    | 0      | 62.1%     | $1.797       | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 256    | 96    | 160    | 0      | 37.5%     | $-0.048      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 1064   | 304   | 760    | 0      | 28.6%     | $-1.066      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 11258  | 2884  | 8374   | 0      | 25.6%     | $-1.133      | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 10779  | 3915  | 6864   | 0      | 36.3%     | $-0.087      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 3296   | 1441  | 1855   | 0      | 43.7%     | $-0.355      | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 2136   | 328   | 1808   | 0      | 15.4%     | $-1.661      | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 608    | 0     | 608    | 0      | 0.0%      | $-2.475      | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 56     | 48    | 8      | 0      | 85.7%     | $1.451       | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 892    | 356   | 536    | 0      | 39.9%     | $-0.223      | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 10824  | 3836  | 6988   | 0      | 35.4%     | $-0.380      | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 24075  | 7951  | 16124  | 0      | 33.0%     | $-0.488      | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 8993   | 5189  | 3804   | 0      | 57.7%     | $0.013       | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 5344   | 2304  | 3040   | 0      | 43.1%     | $0.241       | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 260    | 0     | 260    | 0      | 0.0%      | $-2.553      | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 39429 | 11660 | 27769  | 0      | 29.6%     | $-1.088  |
| SHORT        | 44678 | 19053 | 25625  | 0      | 42.6%     | $0.178   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 8894  | 3542  | 5352   | 0      | 39.8%     | $-0.426  |
| Long (30-60 min)       | 12291 | 5413  | 6878   | 0      | 44.0%     | $-0.040  |
| Medium (5-15 min)      | 15127 | 7277  | 7850   | 0      | 48.1%     | $-0.139  |
| Slow (15-30 min)       | 10005 | 4673  | 5332   | 0      | 46.7%     | $0.057   |
| Very Fast (<1 min)     | 1751  | 593   | 1158   | 0      | 33.9%     | $-0.935  |
| Very Long (>1h)        | 36039 | 9215  | 26824  | 0      | 25.6%     | $-0.763  |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.42 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (85.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (8.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.19) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-0.19) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: ORB (9:30-10:00) (47.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (12797s / 213.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### theta_burn

**Symbols:** AMD, INTC, MU, TSLA  |  **Total Signals:** 3,293  |  **Win Rate:** 19.6%  |  **Avg P&L (resolved):** $0.088  |  **Avg P&L (all):** $0.088  |  **Avg Hold:** 172s (2.9m)  |  **Median Hold:** 62s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 604   | 154   | 450    | 0      | 25.5%     | $0.010   | $0.010   | 19.7%    |
| 20-29%         | 605   | 18    | 587    | 0      | 3.0%      | $-0.201  | $-0.201  | -69.7%   |
| 30-39%         | 1750  | 283   | 1467   | 0      | 16.2%     | $0.190   | $0.190   | 37.8%    |
| 40-49%         | 334   | 192   | 142    | 0      | 57.5%     | $0.219   | $0.219   | 104.2%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2269  | 374   | 1895   | 0      | 16.5%     | $0.017   |
| Trending (Up)        | 1024  | 273   | 751    | 0      | 26.7%     | $0.247   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 3293  | 647   | 2646   | 0      | 19.6%     | $0.088   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: <30m        | 3293  | 647   | 2646   | 0      | 19.6%     | $0.088   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 3198  | 639   | 2559   | 0      | 20.0%     | $0.086   | 🟢          |
| Morning (10:00-12:00)  | 95    | 8     | 87     | 0      | 8.4%      | $0.165   | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 95     | 0          | 0          | 95         | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 3198   | 0          | 0          | 3198       | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Morning (10:00-12:00)  | 10-19%     | 18     | 3     | 15     | 0      | 16.7%     | $0.376       | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 69     | 5     | 64     | 0      | 7.2%      | $0.141       | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 8      | 0     | 8      | 0      | 0.0%      | $-0.100      | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 586    | 151   | 435    | 0      | 25.8%     | $-0.001      | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 536    | 13    | 523    | 0      | 2.4%      | $-0.245      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 1742   | 283   | 1459   | 0      | 16.2%     | $0.191       | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 334    | 192   | 142    | 0      | 57.5%     | $0.219       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| SHORT        | 3293  | 647   | 2646   | 0      | 19.6%     | $0.088   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 1012  | 263   | 749    | 0      | 26.0%     | $-0.069  |
| Medium (5-15 min)      | 611   | 231   | 380    | 0      | 37.8%     | $0.147   |
| Slow (15-30 min)       | 64    | 64    | 0      | 0      | 100.0%    | $1.175   |
| Very Fast (<1 min)     | 1606  | 89    | 1517   | 0      | 5.5%      | $0.122   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 19.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.09 — profitable even with 19.6% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (57.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (3.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.25) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.09) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (20.0% win rate) — statistically significant above overall WR.

---

### vol_compression_range

**Symbols:** AMD, INTC, NVDA, SPCX, SPY, TSLA  |  **Total Signals:** 57,977  |  **Win Rate:** 44.8%  |  **Avg P&L (resolved):** $0.164  |  **Avg P&L (all):** $0.164  |  **Avg Hold:** 15992s (266.5m)  |  **Median Hold:** 2756s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 8     | 0     | 8      | 0      | 0.0%      | $-5.050  | $-5.050  | -100.0%  |
| 20-29%         | 2742  | 888   | 1854   | 0      | 32.4%     | $-1.094  | $-1.094  | -18.9%   |
| 30-39%         | 8622  | 2742  | 5880   | 0      | 31.8%     | $-0.835  | $-0.835  | -20.5%   |
| 40-49%         | 20356 | 9183  | 11173  | 0      | 45.1%     | $0.432   | $0.432   | 12.8%    |
| 50-59%         | 13743 | 6979  | 6764   | 0      | 50.8%     | $0.112   | $0.112   | 27.0%    |
| 60-69%         | 5042  | 2102  | 2940   | 0      | 41.7%     | $-0.206  | $-0.206  | 4.2%     |
| 70-79%         | 6248  | 3296  | 2952   | 0      | 52.8%     | $1.295   | $1.295   | 31.9%    |
| 80-89%         | 1216  | 768   | 448    | 0      | 63.2%     | $1.939   | $1.939   | 57.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 34303 | 14193 | 20110  | 0      | 41.4%     | $-0.145  |
| Trending (Up)        | 23674 | 11765 | 11909  | 0      | 49.7%     | $0.612   |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 57977 | 25958 | 32019  | 0      | 44.8%     | $0.164   |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1680  | 1056  | 624    | 0      | 62.9%     | $1.316   |
| Time Held: 30-90m      | 18431 | 8916  | 9515   | 0      | 48.4%     | $0.548   |
| Time Held: 90-240m     | 8152  | 5102  | 3050   | 0      | 62.6%     | $0.972   |
| Time Held: <30m        | 19514 | 5612  | 13902  | 0      | 28.8%     | $-1.078  |
| Time Held: >480m       | 10200 | 5272  | 4928   | 0      | 51.7%     | $1.010   |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 21578 | 10862 | 10716  | 0      | 50.3%     | $0.512   | 🟢          |
| Morning (10:00-12:00)  | 30279 | 12816 | 17463  | 0      | 42.3%     | $0.036   | 🔴          |
| ORB (9:30-10:00)       | 6120  | 2280  | 3840   | 0      | 37.3%     | $-0.432  | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 6120   | 544        | 1276       | 4300       | 8.9%      | 20.8%     | 70.3%     |
| Morning (10:00-12:00)  | 30279  | 2332       | 9505       | 18442      | 7.7%      | 31.4%     | 60.9%     |
| Afternoon (12:00-16:00) | 21578  | 4588       | 8004       | 8986       | 21.3%     | 37.1%     | 41.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 10-19%     | 8      | 0     | 8      | 0      | 0.0%      | $-5.050      | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 688    | 80    | 608    | 0      | 11.6%     | $-1.585      | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 2108   | 424   | 1684   | 0      | 20.1%     | $-2.140      | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 1496   | 1108  | 388    | 0      | 74.1%     | $2.666       | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 956    | 444   | 512    | 0      | 46.4%     | $0.199       | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 320    | 128   | 192    | 0      | 40.0%     | $-0.229      | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 512    | 64    | 448    | 0      | 12.5%     | $-2.460      | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 32     | 32    | 0      | 0      | 100.0%    | $4.800       | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 1182   | 584   | 598    | 0      | 49.4%     | $-0.960      | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 4120   | 1510  | 2610   | 0      | 36.7%     | $-0.495      | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 13140  | 5641  | 7499   | 0      | 42.9%     | $0.268       | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 7367   | 3061  | 4306   | 0      | 41.6%     | $-0.155      | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 2138   | 772   | 1366   | 0      | 36.1%     | $-0.377      | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 2076   | 1024  | 1052   | 0      | 49.3%     | $0.807       | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 256    | 224   | 32     | 0      | 87.5%     | $4.022       | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 872    | 224   | 648    | 0      | 25.7%     | $-0.888      | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 2394   | 808   | 1586   | 0      | 33.8%     | $-0.273      | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 5720   | 2434  | 3286   | 0      | 42.6%     | $0.226       | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 5420   | 3474  | 1946   | 0      | 64.1%     | $0.461       | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 2584   | 1202  | 1382   | 0      | 46.5%     | $-0.061      | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 3660   | 2208  | 1452   | 0      | 60.3%     | $2.098       | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 928    | 512   | 416    | 0      | 55.2%     | $1.266       | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 30875 | 13494 | 17381  | 0      | 43.7%     | $0.029   |
| SHORT        | 27102 | 12464 | 14638  | 0      | 46.0%     | $0.318   |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 2451  | 376   | 2075   | 0      | 15.3%     | $-1.947  |
| Long (30-60 min)       | 12944 | 5962  | 6982   | 0      | 46.1%     | $0.172   |
| Medium (5-15 min)      | 7646  | 1771  | 5875   | 0      | 23.2%     | $-1.259  |
| Slow (15-30 min)       | 9329  | 3465  | 5864   | 0      | 37.1%     | $-0.682  |
| Very Fast (<1 min)     | 88    | 0     | 88     | 0      | 0.0%      | $-3.047  |
| Very Long (>1h)        | 25519 | 14384 | 11135  | 0      | 56.4%     | $1.110   |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 44.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.16 — profitable even with 44.8% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (63.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.61) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.32) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (50.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (15992s / 266.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

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
| 1783346406.271 | 832    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 18           | DOWN trend exhausted: delta declining (below av... |
| 1783001174.7   | 1098   | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 17           | Squeeze LONG: breakout through call wall at 129... |
| 1783346095.822 | 736    | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 17           | MEMX accumulation LONG: ESI=0.811 (+81.1%), dev... |
| 1783448356.581 | 640    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 17           | GEX call-heavy: call/put ratio=3.228, call_gex=... |
| 1783696508.073 | 184    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 17           | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1782894254.693 | 7968   | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 16           | Gamma squeeze: price approaching call wall at 1... |
| 1783001236.966 | 972    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 16           | ROBUST_LONG LONG: frag=0.167/0.200 decay=-0.155... |
| 1783344295.03  | 928    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, participant_divergence_scalper, prob_weighted_magnet, strike_concentration, vol_compression_range | 16           | Call flow dominant (ratio=2.3×): call score 783... |
| 1783352614.441 | 832    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, vol_compression_range | 16           | Confluence LONG at 125: 1 structural signals, t... |
| 1783363355.012 | 960    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 16           | Call flow dominant (ratio=15.2×): call score 22... |
| 1783432408.061 | 864    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 16           | Magnet pull LONG: price 413.71 below magnet 415... |
| 1784108800.43  | 80     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 16           | GEX call-heavy: call/put ratio=3.148, call_gex=... |
| 1782912594.102 | 5664   | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | GEX call-heavy: call/put ratio=7.880, call_gex=... |
| 1782918098.932 | 4120   | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 15           | Depth imbalance SHORT: IR=0.33 (+67.1%), ROC=-0... |
| 1782979261.828 | 3598   | confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Participant conviction LONG: participants=1.4, ... |
| 1782982619.675 | 1990   | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Call flow dominant (ratio=1.6×): call score 120... |
| 1782998212.652 | 965    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, strike_concentration | 15           | Participant conviction LONG: participants=3.6, ... |
| 1782998694.481 | 1161   | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, strike_concentration | 15           | Participant conviction LONG: participants=1.4, ... |
| 1783001118.81  | 779    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Participant conviction LONG: participants=1.6, ... |
| 1783006270.017 | 650    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | GEX call-heavy: call/put ratio=2.561, call_gex=... |
| 1783016113.765 | 711    | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, theta_burn | 15           | Depth imbalance SHORT: IR=0.53 (+47.1%), ROC=-0... |
| 1783021599.197 | 711    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 15           | Call wall at 119.0 rejected price, GEX=-857812,... |
| 1783338208.345 | 704    | call_put_flow_asymmetry, confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, vol_compression_range | 15           | ROBUST_SHORT SHORT: frag=0.153/0.143 decay=+0.0... |
| 1783341020.857 | 736    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 15           | Velocity-Magnet LONG: delta accelerating at 195... |
| 1783343306.708 | 768    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 15           | Squeeze LONG: breakout through call wall at 124... |
| 1783345288.67  | 608    | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 15           | Flow imbalance SHORT: AggVSI=-0.533 (+53.3%), R... |
| 1783346158.311 | 768    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 15           | Velocity-Magnet SHORT: delta accelerating at 42... |
| 1783347315.181 | 672    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | ROBUST_LONG LONG: frag=0.167/0.128 decay=-0.244... |
| 1783355044.638 | 608    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, vol_compression_range | 15           | Magnet pull LONG: price 197.06 below magnet 200... |
| 1783422963.895 | 800    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Squeeze LONG: breakout through call wall at 749... |
| 1783431861.129 | 928    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Call flow dominant (ratio=11.2×): call score 49... |
| 1783590075.689 | 136    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Depth decay SHORT: ROC=-0.3313 (-33.13%), vol/d... |
| 1783602754.027 | 160    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 15           | Depth imbalance SHORT: IR=0.27 (+73.4%), ROC=-0... |
| 1783613350.268 | 200    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 15           | ROBUST_LONG LONG: frag=0.180/0.170 decay=-0.589... |
| 1783613473.709 | 184    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | GEX call-heavy: call/put ratio=4.315, call_gex=... |
| 1783690845.731 | 184    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 15           | UP trend exhausted: delta declining (below avg)... |
| 1784102467.473 | 88     | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 15           | Call flow dominant (ratio=91.2×): call score 88... |
| 1784124116.532 | 84     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet | 15           | Depth imbalance SHORT: IR=0.52 (+48.5%), ROC=-0... |
| 1782894745.619 | 5388   | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | GEX put-heavy: call/put ratio=0.000, call_gex=1... |
| 1782894797.336 | 5640   | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | ROBUST_SHORT SHORT: frag_bid=0.278 frag_ask=0.2... |
| 1782894861.458 | 5380   | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet | 14           | Put wall at 417.5 supported price, GEX=1508173,... |
| 1782898150.86  | 5380   | confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | MEMX accumulation LONG: ESI=0.899 (+89.9%), dev... |
| 1782907521.824 | 4624   | call_put_flow_asymmetry, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | Flow imbalance LONG: AggVSI=0.923 (+92.3%), ROC... |
| 1782908533.237 | 4124   | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | Magnet pull LONG: price 419.67 below magnet 425... |
| 1782909147.28  | 4624   | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | Call flow dominant (ratio=16.8×): call score 55... |
| 1782909271.697 | 5144   | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | Participant conviction LONG: participants=1.2, ... |
| 1782913021.868 | 3356   | confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 14           | GEX call-heavy: call/put ratio=1.831, call_gex=... |
| 1782913150.4   | 3348   | confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 14           | Participant conviction SHORT: participants=3.0,... |
| 1782914756.004 | 4112   | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet | 14           | Put wall at 557.5 supported price, GEX=596523, ... |
| 1782915486.243 | 4108   | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | ROBUST_LONG LONG: frag_bid=0.143 frag_ask=0.124... |

**40028 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 226,835  | 13         | net_gamma=< 637.49     | 36.9%    | $-0.245    |
| Volume Spike                 | 41,409   | 2          | vol_ratio=0.5          | 33.2%    | $0.047     |
| IV Expansion                 | 23,162   | 2          | iv_skew=< 0.15         | 17.4%    | $-1.266    |
| Gamma Wall Support (747.0)   | 10,375   | 4          | wall_strike=747.0      | 49.1%    | $1.308     |
| Gamma Wall Support (417.5)   | 5,358    | 4          | wall_strike=417.5      | 42.8%    | $0.385     |
| Gamma Wall Support (195.0)   | 2,410    | 4          | wall_strike=195.0      | 18.7%    | $-0.561    |
| Gamma Wall Support (575.0)   | 1,849    | 4          | wall_strike=575.0      | 24.3%    | $-1.068    |
| Gamma Wall Support (545.0)   | 1,449    | 5          | wall_strike=545.0      | 25.1%    | $-0.649    |
| Gamma Wall Support (392.5)   | 906      | 5          | wall_strike=392.5      | 50.8%    | $0.889     |
| Gamma Wall Support (1017.5)  | 882      | 4          | wall_strike=1017.5     | 30.6%    | $-0.202    |
| Gamma Wall Support (109.0)   | 809      | 5          | wall_strike=109.0      | 30.8%    | $-0.060    |
| Gamma Wall Support (205.0)   | 736      | 4          | wall_strike=205.0      | 21.5%    | $-0.649    |
| Gamma Wall Support (123.0)   | 542      | 5          | wall_strike=123.0      | 20.8%    | $-0.272    |
| Gamma Wall Support (101.0)   | 349      | 4          | wall_strike=101.0      | 14.3%    | $-0.261    |
| Gamma Wall Support (131.0)   | 224      | 5          | wall_strike=131.0      | 16.1%    | $-0.461    |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 95912  | 10     | 10       | 38.0%    | $-0.196    | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 64532  | 8      | 8        | 37.6%    | $-0.486    | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 25029  | 6      | 6        | 29.2%    | $-0.702    | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 906    | 5      | 5        | 50.8%    | $0.889     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Exposur  | 41362  | 5      | 5        | 38.1%    | $0.291     | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 809    | 5      | 5        | 30.8%    | $-0.060    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 214    | 5      | 5        | 25.2%    | $-0.573    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 1449   | 5      | 5        | 25.1%    | $-0.649    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 542    | 5      | 5        | 20.8%    | $-0.272    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 224    | 5      | 5        | 16.1%    | $-0.461    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 10375  | 4      | 4        | 49.1%    | $1.308     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 5358   | 4      | 4        | 42.8%    | $0.385     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 169    | 4      | 4        | 34.3%    | $0.011     | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 882    | 4      | 4        | 30.6%    | $-0.202    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 1849   | 4      | 4        | 24.3%    | $-1.068    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 736    | 4      | 4        | 21.5%    | $-0.649    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 145    | 4      | 4        | 20.0%    | $-0.391    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 2410   | 4      | 4        | 18.7%    | $-0.561    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 124    | 4      | 4        | 15.3%    | $-0.696    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 122    | 4      | 4        | 14.8%    | $-0.562    | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |

**26 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 5-9%           | 116376   | 70956  | 45420  | 0      | 61.0%     | 24.0      |
| 10-19%         | 502765   | 273369 | 229396 | 0      | 54.4%     | 21.3      |
| 20-29%         | 646064   | 299496 | 346568 | 0      | 46.4%     | 25.7      |
| 30-39%         | 1205736  | 424450 | 781286 | 0      | 35.2%     | 15.4      |
| 40-49%         | 1563870  | 476086 | 1087784 | 0      | 30.4%     | 14.2      |
| 50-59%         | 1237983  | 418563 | 819420 | 0      | 33.8%     | 16.5      |
| 60-69%         | 732979   | 254242 | 478737 | 0      | 34.7%     | 19.3      |
| 70-79%         | 372037   | 119645 | 252392 | 0      | 32.2%     | 22.3      |
| 80-89%         | 285459   | 78291  | 207168 | 0      | 27.4%     | 16.9      |
| 90-99%         | 21617    | 12700  | 8917   | 0      | 58.8%     | 23.8      |
| 100%           | 86564    | 61150  | 25414  | 0      | 70.6%     | 33.8      |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| ORB (9:30-10:00)       | 802861   | 319032 | 483829 | 0      | 39.7%     | 9.3      |
| Morning (10:00-12:00)  | 2842148  | 1052308 | 1789840 | 0      | 37.0%     | 14.7     |
| Afternoon (12:00-16:00) | 3126441  | 1117608 | 2008833 | 0      | 35.7%     | 17.3     |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| ORB (9:30-10:00)       | 5-9%         | 14158    | 8408   | 5750   | 0      | 59.4%     |
| ORB (9:30-10:00)       | 10-19%       | 51401    | 27953  | 23448  | 0      | 54.4%     |
| ORB (9:30-10:00)       | 20-29%       | 70512    | 28815  | 41697  | 0      | 40.9%     |
| ORB (9:30-10:00)       | 30-39%       | 160177   | 58646  | 101531 | 0      | 36.6%     |
| ORB (9:30-10:00)       | 40-49%       | 167501   | 67754  | 99747  | 0      | 40.4%     |
| ORB (9:30-10:00)       | 50-59%       | 141071   | 48157  | 92914  | 0      | 34.1%     |
| ORB (9:30-10:00)       | 60-69%       | 93490    | 37103  | 56387  | 0      | 39.7%     |
| ORB (9:30-10:00)       | 70-79%       | 45186    | 18154  | 27032  | 0      | 40.2%     |
| ORB (9:30-10:00)       | 80-89%       | 52460    | 19889  | 32571  | 0      | 37.9%     |
| ORB (9:30-10:00)       | 90-99%       | 1309     | 841    | 468    | 0      | 64.2%     |
| ORB (9:30-10:00)       | 100%         | 5596     | 3312   | 2284   | 0      | 59.2%     |
| Morning (10:00-12:00)  | 5-9%         | 53007    | 31412  | 21595  | 0      | 59.3%     |
| Morning (10:00-12:00)  | 10-19%       | 219031   | 117256 | 101775 | 0      | 53.5%     |
| Morning (10:00-12:00)  | 20-29%       | 273142   | 128735 | 144407 | 0      | 47.1%     |
| Morning (10:00-12:00)  | 30-39%       | 494390   | 177519 | 316871 | 0      | 35.9%     |
| Morning (10:00-12:00)  | 40-49%       | 653834   | 209856 | 443978 | 0      | 32.1%     |
| Morning (10:00-12:00)  | 50-59%       | 517527   | 179678 | 337849 | 0      | 34.7%     |
| Morning (10:00-12:00)  | 60-69%       | 302460   | 105111 | 197349 | 0      | 34.8%     |
| Morning (10:00-12:00)  | 70-79%       | 171113   | 51690  | 119423 | 0      | 30.2%     |
| Morning (10:00-12:00)  | 80-89%       | 131636   | 35011  | 96625  | 0      | 26.6%     |
| Morning (10:00-12:00)  | 90-99%       | 7198     | 2950   | 4248   | 0      | 41.0%     |
| Morning (10:00-12:00)  | 100%         | 18810    | 13090  | 5720   | 0      | 69.6%     |
| Afternoon (12:00-16:00) | 5-9%         | 49211    | 31136  | 18075  | 0      | 63.3%     |
| Afternoon (12:00-16:00) | 10-19%       | 232333   | 128160 | 104173 | 0      | 55.2%     |
| Afternoon (12:00-16:00) | 20-29%       | 302410   | 141946 | 160464 | 0      | 46.9%     |
| Afternoon (12:00-16:00) | 30-39%       | 551169   | 188285 | 362884 | 0      | 34.2%     |
| Afternoon (12:00-16:00) | 40-49%       | 742535   | 198476 | 544059 | 0      | 26.7%     |
| Afternoon (12:00-16:00) | 50-59%       | 579385   | 190728 | 388657 | 0      | 32.9%     |
| Afternoon (12:00-16:00) | 60-69%       | 337029   | 112028 | 225001 | 0      | 33.2%     |
| Afternoon (12:00-16:00) | 70-79%       | 155738   | 49801  | 105937 | 0      | 32.0%     |
| Afternoon (12:00-16:00) | 80-89%       | 101363   | 23391  | 77972  | 0      | 23.1%     |
| Afternoon (12:00-16:00) | 90-99%       | 13110    | 8909   | 4201   | 0      | 68.0%     |
| Afternoon (12:00-16:00) | 100%         | 62158    | 44748  | 17410  | 0      | 72.0%     |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] gamma_squeeze    | 70-79%       | 100.0%    | 32.2%     | 211%     | 3.05     | 8        | 8        | 0        |
| [ALPHA] delta_volume_exhaustion | 60-69%       | 91.0%     | 34.7%     | 162%     | 2.91     | 1698     | 1546     | 152      |
| [ALPHA] delta_volume_exhaustion | 50-59%       | 86.6%     | 33.8%     | 156%     | 3.20     | 12630    | 10942    | 1688     |
| [ALPHA] delta_volume_exhaustion | 40-49%       | 72.1%     | 30.4%     | 137%     | 2.93     | 55131    | 39754    | 15377    |
| [ALPHA] vol_compression_range | 80-89%       | 63.2%     | 27.4%     | 130%     | 2.11     | 1216     | 768      | 448      |
| [ALPHA] gamma_wall_bounce | 80-89%       | 53.7%     | 27.4%     | 96%      | 1.55     | 4487     | 2410     | 2077     |
| [ALPHA] theta_burn       | 40-49%       | 57.5%     | 30.4%     | 89%      | 1.90     | 334      | 192      | 142      |
| [ALPHA] depth_decay_momentum | 80-89%       | 51.1%     | 27.4%     | 86%      | 1.40     | 16682    | 8532     | 8150     |
| [ALPHA] strike_concentration | 20-29%       | 85.7%     | 46.4%     | 85%      | 1.53     | 56       | 48       | 8        |
| [ALPHA] delta_volume_exhaustion | 30-39%       | 64.6%     | 35.2%     | 83%      | 1.90     | 169326   | 109324   | 60002    |
| [ALPHA] gamma_flip_breakout | 30-39%       | 60.2%     | 35.2%     | 71%      | 1.62     | 29868    | 17980    | 11888    |
| [ALPHA] vol_compression_range | 70-79%       | 52.8%     | 32.2%     | 64%      | 0.92     | 6248     | 3296     | 2952     |
| [ALPHA] gamma_flip_breakout | 40-49%       | 49.6%     | 30.4%     | 63%      | 1.35     | 35095    | 17415    | 17680    |
| [ALPHA] depth_decay_momentum | 40-49%       | 49.6%     | 30.4%     | 63%      | 1.35     | 395      | 196      | 199      |
| [ALPHA] gamma_wall_bounce | 40-49%       | 48.0%     | 30.4%     | 58%      | 1.24     | 19575    | 9399     | 10176    |
| [ALPHA] strike_concentration | 60-69%       | 53.8%     | 34.7%     | 55%      | 0.99     | 12744    | 6851     | 5893     |
| [ALPHA] gex_divergence   | 80-89%       | 41.3%     | 27.4%     | 51%      | 0.82     | 18421    | 7611     | 10810    |
| [ALPHA] vol_compression_range | 50-59%       | 50.8%     | 33.8%     | 50%      | 1.03     | 13743    | 6979     | 6764     |

**18 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] gamma_squeeze    | Morning (10:00-12:00) | 70-79%       | 8       | 8      | 0      | 100.0%   | 30.2%    | 231%   | 2.95    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 80-89%       | 256     | 224    | 32     | 87.5%    | 26.6%    | 229%   | 2.46    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 60-69%       | 946     | 866    | 80     | 91.5%    | 33.2%    | 175%   | 2.68    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 50-59%       | 3100    | 2924   | 176    | 94.3%    | 34.7%    | 172%   | 3.24    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 80-89%       | 32      | 32     | 0      | 100.0%   | 37.9%    | 164%   | 2.43    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 40-49%       | 35991   | 25338  | 10653  | 70.4%    | 26.7%    | 163%   | 2.44    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 60-69%       | 712     | 640    | 72     | 89.9%    | 34.8%    | 159%   | 2.70    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 50-59%       | 8806    | 7446   | 1360   | 84.6%    | 32.9%    | 157%   | 2.50    | ⚡ HIGH       |
| [ALPHA] delta_volume_exhaustion | ORB (9:30-10:00) | 60-69%       | 40      | 40     | 0      | 100.0%   | 39.7%    | 152%   | 3.05    | ⚡ HIGH       |
| [ALPHA] participant_diversity_conviction | ORB (9:30-10:00) | 80-89%       | 584     | 544    | 40     | 93.2%    | 37.9%    | 146%   | 2.16    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 80-89%       | 3892    | 2186   | 1706   | 56.2%    | 23.1%    | 143%   | 1.82    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 80-89%       | 928     | 512    | 416    | 55.2%    | 23.1%    | 139%   | 1.76    | 🔥 STRONG     |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 40-49%       | 15503   | 11699  | 3804   | 75.5%    | 32.1%    | 135%   | 2.87    | ⚡ HIGH       |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 40-49%       | 258     | 160    | 98     | 62.0%    | 26.7%    | 132%   | 1.97    | 🔥 STRONG     |
| [ALPHA] delta_volume_exhaustion | ORB (9:30-10:00) | 50-59%       | 724     | 572    | 152    | 79.0%    | 34.1%    | 131%   | 2.39    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | ORB (9:30-10:00) | 80-89%       | 160     | 136    | 24     | 85.0%    | 37.9%    | 124%   | 1.84    | 🔥 STRONG     |
| [ALPHA] theta_burn       | Afternoon (12:00-16:00) | 40-49%       | 334     | 192    | 142    | 57.5%    | 26.7%    | 115%   | 1.72    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 70-79%       | 1344    | 1144   | 200    | 85.1%    | 40.2%    | 112%   | 1.87    | 🔥 STRONG     |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 80-89%       | 8390    | 4100   | 4290   | 48.9%    | 23.1%    | 112%   | 1.42    | 🔥 STRONG     |
| [ALPHA] depth_decay_momentum | Morning (10:00-12:00) | 80-89%       | 6656    | 3680   | 2976   | 55.3%    | 26.6%    | 108%   | 1.16    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 30-39%       | 10898   | 7778   | 3120   | 71.4%    | 35.9%    | 99%    | 1.70    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 50-59%       | 516     | 344    | 172    | 66.7%    | 34.1%    | 95%    | 1.73    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 50-59%       | 5420    | 3474   | 1946   | 64.1%    | 32.9%    | 95%    | 1.51    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | Morning (10:00-12:00) | 30-39%       | 58940   | 41011  | 17929  | 69.6%    | 35.9%    | 94%    | 1.62    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 80-89%       | 120     | 88     | 32     | 73.3%    | 37.9%    | 93%    | 1.39    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 30-39%       | 5664    | 4008   | 1656   | 70.8%    | 36.6%    | 93%    | 1.70    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 30-39%       | 93918   | 60898  | 33020  | 64.8%    | 34.2%    | 90%    | 1.94    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | ORB (9:30-10:00) | 30-39%       | 1964    | 1360   | 604    | 69.2%    | 36.6%    | 89%    | 1.62    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 70-79%       | 3660    | 2208   | 1452   | 60.3%    | 32.0%    | 89%    | 1.70    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 60-69%       | 3852    | 2488   | 1364   | 64.6%    | 34.8%    | 86%    | 1.46    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 40-49%       | 10292   | 6115   | 4177   | 59.4%    | 32.1%    | 85%    | 1.81    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | ORB (9:30-10:00) | 40-49%       | 3637    | 2717   | 920    | 74.7%    | 40.4%    | 85%    | 1.83    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 40-49%       | 1496    | 1108   | 388    | 74.1%    | 40.4%    | 83%    | 1.80    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 20-29%       | 56      | 48     | 8      | 85.7%    | 46.9%    | 83%    | 1.49    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 50-59%       | 4451    | 2753   | 1698   | 61.9%    | 34.1%    | 81%    | 1.48    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 40-49%       | 14570   | 8442   | 6128   | 57.9%    | 32.1%    | 81%    | 1.71    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 40-49%       | 2760    | 1976   | 784    | 71.6%    | 40.4%    | 77%    | 1.66    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 60-69%       | 8993    | 5189   | 3804   | 57.7%    | 33.2%    | 74%    | 1.12    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 50-59%       | 11140   | 6286   | 4854   | 56.4%    | 32.9%    | 71%    | 1.14    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 70-79%       | 1291    | 696    | 595    | 53.9%    | 32.0%    | 69%    | 1.31    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | ORB (9:30-10:00) | 60-69%       | 1572    | 1040   | 532    | 66.2%    | 39.7%    | 67%    | 1.34    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Morning (10:00-12:00) | 90-99%       | 200     | 136    | 64     | 68.0%    | 41.0%    | 66%    | 1.03    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 60-69%       | 3020    | 1736   | 1284   | 57.5%    | 34.8%    | 65%    | 1.11    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 80-89%       | 1092    | 480    | 612    | 44.0%    | 26.6%    | 65%    | 0.70    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 30-39%       | 6205    | 3667   | 2538   | 59.1%    | 35.9%    | 65%    | 1.11    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 30-39%       | 989     | 593    | 396    | 60.0%    | 36.6%    | 64%    | 1.16    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 70-79%       | 744     | 368    | 376    | 49.5%    | 30.2%    | 64%    | 0.81    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 70-79%       | 2076    | 1024   | 1052   | 49.3%    | 30.2%    | 63%    | 0.81    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 80-89%       | 2448    | 920    | 1528   | 37.6%    | 23.1%    | 63%    | 0.80    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Morning (10:00-12:00) | 80-89%       | 10551   | 4564   | 5987   | 43.3%    | 26.6%    | 63%    | 0.67    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 40-49%       | 6591    | 2860   | 3731   | 43.4%    | 26.7%    | 62%    | 0.93    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 80-89%       | 840     | 512    | 328    | 61.0%    | 37.9%    | 61%    | 0.90    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 40-49%       | 53230   | 27412  | 25818  | 51.5%    | 32.1%    | 60%    | 1.28    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 40-49%       | 5720    | 2434   | 3286   | 42.6%    | 26.7%    | 59%    | 0.88    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | ORB (9:30-10:00) | 70-79%       | 308     | 196    | 112    | 63.6%    | 40.2%    | 58%    | 0.97    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | ORB (9:30-10:00) | 70-79%       | 140     | 88     | 52     | 62.9%    | 40.2%    | 56%    | 0.94    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 60-69%       | 1697    | 1052   | 645    | 62.0%    | 39.7%    | 56%    | 1.13    | ⚠ MODERATE   |
| [ALPHA] participant_diversity_conviction | ORB (9:30-10:00) | 70-79%       | 629     | 393    | 236    | 62.5%    | 40.2%    | 56%    | 0.93    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 40-49%       | 105702  | 43756  | 61946  | 41.4%    | 26.7%    | 55%    | 0.82    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | ORB (9:30-10:00) | 70-79%       | 760     | 472    | 288    | 62.1%    | 40.2%    | 55%    | 0.91    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 30-39%       | 2387    | 1344   | 1043   | 56.3%    | 36.6%    | 54%    | 0.98    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 50-59%       | 77108   | 40751  | 36357  | 52.8%    | 34.7%    | 52%    | 0.99    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | Afternoon (12:00-16:00) | 20-29%       | 133671  | 95089  | 38582  | 71.1%    | 46.9%    | 52%    | 0.93    | ⚠ MODERATE   |
| [ALPHA] delta_volume_exhaustion | ORB (9:30-10:00) | 20-29%       | 26363   | 16277  | 10086  | 61.7%    | 40.9%    | 51%    | 1.08    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 50-59%       | 23568   | 11678  | 11890  | 49.6%    | 32.9%    | 51%    | 0.81    | ⚠ MODERATE   |

**65 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | gamma_wall_bounce        | 174,075 | 57.1%    | $1.695   | 90-99%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 90-99% | Trending (Up)  | Time Held: 90-240m |
| 2     | vol_compression_range    | 57,977  | 44.8%    | $0.164   | 80-89%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 80-89% | Trending (Up)  | Time Held: 240-480m |
| 3     | theta_burn               | 3,293   | 19.6%    | $0.088   | 40-49%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 40-49% | Trending (Up)  | Time Held: <30m |
| 4     | gex_imbalance            | 509,127 | 42.5%    | $0.083   | 70-79%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 10-19% | Trending (Up)  | Time Held: 240-480m |
| 5     | depth_decay_momentum     | 403,641 | 40.6%    | $0.021   | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 90-99% | UNKNOWN        | Time Held: 90-240m |
| 6     | participant_divergence_scalper | 491,594 | 40.5%    | $0.002   | 40-49%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 50-59% | UNKNOWN        | Time Held: 30-90m |
| 7     | exchange_flow_imbalance  | 182,610 | 33.2%    | $-0.002  | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 70-79% | UNKNOWN        | Time Held: 240-480m |
| 8     | delta_volume_exhaustion  | 904,484 | 68.8%    | $-0.006  | 60-69%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 60-69% | UNKNOWN        | Time Held: <30m |
| 9     | gamma_flip_breakout      | 190,133 | 53.5%    | $-0.007  | 10-19%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 90-99% | Trending (Up)  | Time Held: <30m |
| 10    | order_book_fragmentation | 479,502 | 24.9%    | $-0.034  | 90-99%         | ORB (9:30-10:00) | Afternoon (12:00-16:00) @ 90-99% | UNKNOWN        | Time Held: 90-240m |
| 11    | gex_divergence           | 234,643 | 35.3%    | $-0.132  | 90-99%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 90-99% | Sideways       | Time Held: >480m |
| 12    | depth_imbalance_momentum | 171,677 | 28.7%    | $-0.207  | 50-59%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 30-39% | UNKNOWN        | Time Held: >480m |
| 13    | exchange_flow_concentration | 283,460 | 35.2%    | $-0.218  | 10-19%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 10-19% | UNKNOWN        | Time Held: 90-240m |
| 14    | prob_weighted_magnet     | 813,404 | 20.0%    | $-0.314  | 50-59%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 50-59% | Sideways       | Time Held: 90-240m |
| 15    | magnet_accelerate        | 180,069 | 15.1%    | $-0.361  | 5-9%           | ORB (9:30-10:00) | ORB (9:30-10:00) @ 70-79% | Trending (Up)  | Time Held: <30m |
| 16    | confluence_reversal      | 525,599 | 29.9%    | $-0.386  | 60-69%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 60-69% | Sideways       | Time Held: >480m |
| 17    | exchange_flow_asymmetry  | 185,988 | 21.2%    | $-0.406  | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 80-89% | UNKNOWN        | Time Held: >480m |
| 18    | strike_concentration     | 84,107  | 36.5%    | $-0.415  | 20-29%         | ORB (9:30-10:00) | Afternoon (12:00-16:00) @ 20-29% | Sideways       | Time Held: <30m |
| 19    | gamma_squeeze            | 126,502 | 23.9%    | $-0.518  | 70-79%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 70-79% | Trending (Up)  | Time Held: 240-480m |
| 20    | call_put_flow_asymmetry  | 418,493 | 26.7%    | $-0.562  | 40-49%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 10-19% | UNKNOWN        | Time Held: 90-240m |
| 21    | participant_diversity_conviction | 350,748 | 25.2%    | $-0.623  | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 80-89% | UNKNOWN        | Time Held: >480m |
| 22    | delta_gamma_squeeze      | 324     | 4.9%     | $-1.285  | 5-9%           | Morning (10:00-12:00) | Afternoon (12:00-16:00) @ 5-9% | Sideways       | Time Held: 90-240m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis — Regular Hours Only*