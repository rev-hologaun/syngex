# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-29  |  **Generated:** 2026-05-29 10:15 UTC  |  **Total Resolved Signals:** 35,402  |  **Strategies Analyzed:** 14

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 35,402                                                       |
| Total Wins           | 2,318                                                        |
| Total Losses         | 4,613                                                        |
| Time-Expired (CLOSED) | 28,471                                                       |
| Overall Win Rate     | 33.4%                                                        |
| Total P&L (resolved) | $-2219.27                                                    |
| Avg P&L per Resolved Signal | $-0.32                                                       |
| Total P&L (time-outs) | $2546.79                                                     |
| Avg P&L per Signal (all) | $0.01                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### confluence_reversal

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 10,910  |  **Win Rate:** 25.9%  |  **Avg P&L (resolved):** $-0.9  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 3474s (57.9m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 2229  | 93    | 180    | 1956   | 34.1%     | $0.0     | $0.1     | 2.5%     |
| 30-39%         | 2444  | 63    | 229    | 2152   | 21.6%     | $0.0     | $0.1     | 4.0%     |
| 40-49%         | 3049  | 15    | 79     | 2955   | 16.0%     | $0.0     | $0.0     | 1.7%     |
| 50-59%         | 2045  | 1     | 7      | 2037   | 12.5%     | $0.0     | $-0.0    | 0.4%     |
| 60-69%         | 977   | 2     | 3      | 972    | 40.0%     | $0.0     | $-0.0    | 0.5%     |
| 70-79%         | 166   | 0     | 0      | 166    | 0.0%      | $0.0     | $-0.1    | -1.0%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 6273  | 87    | 235    | 5951   | 27.0%     | $-0.0    |
| Trending (Up)        | 4637  | 87    | 263    | 4287   | 24.9%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 10910 | 174   | 498    | 10238  | 25.9%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 10496 | 86    | 172    | 10238  | 33.3%     | $0.1     |
| Time Held: <30m        | 414   | 88    | 326    | 0      | 21.3%     | $-1.7    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 2321  | 2     | 54     | 2265   | 3.6%      | $-0.1    | 🔴          |
| Afternoon (12:00-16:00) | 2353  | 2     | 45     | 2306   | 4.3%      | $-0.0    | 🔴          |
| Morning (10:00-12:00)  | 1153  | 88    | 182    | 883    | 32.6%     | $0.2     | 🟢          |
| ORB (9:30-10:00)       | 269   | 22    | 64     | 183    | 25.6%     | $-0.1    | 🔴          |
| Overnight              | 2372  | 0     | 0      | 2372   | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 2442  | 60    | 153    | 2229   | 28.2%     | $-0.0    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 2442   | 33         | 690        | 1719       | 1.4%      | 28.3%     | 70.4%     |
| ORB (9:30-10:00)       | 269    | 21         | 78         | 170        | 7.8%      | 29.0%     | 63.2%     |
| Morning (10:00-12:00)  | 1153   | 34         | 366        | 753        | 2.9%      | 31.7%     | 65.3%     |
| Afternoon (12:00-16:00) | 2353   | 49         | 687        | 1617       | 2.1%      | 29.2%     | 68.7%     |
| After-hours (16:00-20:00) | 2321   | 29         | 490        | 1802       | 1.2%      | 21.1%     | 77.6%     |
| Overnight              | 2372   | 0          | 711        | 1661       | 0.0%      | 30.0%     | 70.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 528    | 39    | 63     | 426    | 38.2%     | $1.3         | 🟢          |
| Pre-market             | 30-39%     | 545    | 19    | 63     | 463    | 23.2%     | $-1.2        | 🔴          |
| Pre-market             | 40-49%     | 646    | 2     | 24     | 620    | 7.7%      | $-2.3        | 🔴          |
| Pre-market             | 50-59%     | 438    | 0     | 3      | 435    | 0.0%      | $-1.9        | 🔴          |
| Pre-market             | 60-69%     | 252    | 0     | 0      | 252    | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 70-79%     | 33     | 0     | 0      | 33     | 0.0%      | $0.0         | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 56     | 11    | 25     | 20     | 30.6%     | $0.5         | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 80     | 11    | 26     | 43     | 29.7%     | $-0.3        | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 34     | 0     | 8      | 26     | 0.0%      | $-5.6        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 43     | 0     | 2      | 41     | 0.0%      | $-1.5        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 35     | 0     | 3      | 32     | 0.0%      | $1.4         | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 21     | 0     | 0      | 21     | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 198    | 43    | 78     | 77     | 35.5%     | $0.9         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 269    | 31    | 85     | 153    | 26.7%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 286    | 13    | 19     | 254    | 40.6%     | $3.5         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 263    | 1     | 0      | 262    | 100.0%    | $-6.8        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 103    | 0     | 0      | 103    | 0.0%      | $0.0         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 34     | 0     | 0      | 34     | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 408    | 0     | 14     | 394    | 0.0%      | $-2.5        | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 536    | 2     | 21     | 513    | 8.7%      | $1.3         | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 673    | 0     | 10     | 663    | 0.0%      | $0.5         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 484    | 0     | 0      | 484    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 203    | 0     | 0      | 203    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 49     | 0     | 0      | 49     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 565    | 0     | 0      | 565    | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 538    | 0     | 34     | 504    | 0.0%      | $-3.6        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 699    | 0     | 18     | 681    | 0.0%      | $-3.9        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 343    | 0     | 2      | 341    | 0.0%      | $4.8         | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 147    | 2     | 0      | 145    | 100.0%    | $6.0         | 🟢          |
| After-hours (16:00-20:00) | 70-79%     | 29     | 0     | 0      | 29     | 0.0%      | $0.0         | ⚠️         |
| Overnight              | 20-29%     | 474    | 0     | 0      | 474    | 0.0%      | $0.0         | 🔴          |
| Overnight              | 30-39%     | 476    | 0     | 0      | 476    | 0.0%      | $0.0         | 🔴          |
| Overnight              | 40-49%     | 711    | 0     | 0      | 711    | 0.0%      | $0.0         | 🔴          |
| Overnight              | 50-59%     | 474    | 0     | 0      | 474    | 0.0%      | $0.0         | 🔴          |
| Overnight              | 60-69%     | 237    | 0     | 0      | 237    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 5463  | 146   | 201    | 5116   | 42.1%     | $0.3     |
| SHORT        | 5447  | 28    | 297    | 5122   | 8.6%      | $-0.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 41    | 5     | 36     | 0      | 12.2%     | $-1.8    |
| Long (30-60 min)       | 258   | 86    | 172    | 0      | 33.3%     | $0.3     |
| Medium (5-15 min)      | 173   | 32    | 141    | 0      | 18.5%     | $-1.8    |
| Slow (15-30 min)       | 190   | 50    | 140    | 0      | 26.3%     | $-1.6    |
| Very Fast (<1 min)     | 10    | 1     | 9      | 0      | 10.0%     | $-1.0    |
| Very Long (>1h)        | 10238 | 0     | 0      | 10238  | 0.0%      | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.93 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 10238 time-outs): $-0.00
- 🎯 Best performance at 60-69% confidence (40.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.00) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.06) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (32.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3474s / 57.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 94% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### delta_gamma_squeeze

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 134  |  **Win Rate:** 3.7%  |  **Avg P&L (resolved):** $-3.0  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 1675s (27.9m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 82    | 1     | 26     | 55     | 3.7%      | $0.0     | $0.1     | 0.2%     |
| 20-29%         | 33    | 0     | 0      | 33     | 0.0%      | $0.0     | $1.7     | 33.1%    |
| 30-39%         | 15    | 0     | 0      | 15     | 0.0%      | $0.0     | $1.2     | 23.8%    |
| 40-49%         | 4     | 0     | 0      | 4      | 0.0%      | $0.0     | $0.4     | 5.1%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 59    | 1     | 11     | 47     | 8.3%      | $0.0     |
| Trending (Up)        | 75    | 0     | 15     | 60     | 0.0%      | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 134   | 1     | 26     | 107    | 3.7%      | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 107   | 0     | 0      | 107    | 0.0%      | $0.8     |
| Time Held: <30m        | 27    | 1     | 26     | 0      | 3.7%      | $-3.0    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Pre-market             | 134   | 1     | 26     | 107    | 3.7%      | $0.0     | —          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 134    | 0          | 0          | 134        | 0.0%      | 0.0%      | 100.0%    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 61    | 1     | 0      | 60     | 100.0%    | $2.3     |
| SHORT        | 73    | 0     | 26     | 47     | 0.0%      | $-1.9    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Long (30-60 min)       | 107   | 0     | 0      | 107    | 0.0%      | $0.8     |
| Medium (5-15 min)      | 4     | 0     | 4      | 0      | 0.0%      | $-4.4    |
| Slow (15-30 min)       | 23    | 1     | 22     | 0      | 4.3%      | $-2.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 3.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-2.98 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 107 time-outs): $0.01
- 🎯 Best performance at 10-19% confidence (3.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.02) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.77) — optimal time held is Time Held: 30-90m.
- 🕐 Best signal generation window: Pre-market (3.7% win rate) — signals in this window have the highest hit rate.
- ⏱️ Long avg hold time (1675s / 27.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 80% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,425  |  **Win Rate:** 31.9%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 1462s (24.4m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 50-59%         | 76    | 24    | 33     | 19     | 42.1%     | $0.0     | $0.0     | 3.2%     |
| 60-69%         | 201   | 37    | 70     | 94     | 34.6%     | $0.0     | $0.1     | 5.4%     |
| 70-79%         | 1443  | 113   | 284    | 1046   | 28.5%     | $0.0     | $0.1     | 5.5%     |
| 80-89%         | 664   | 62    | 109    | 493    | 36.3%     | $0.0     | $0.1     | 5.9%     |
| 90-99%         | 41    | 3     | 15     | 23     | 16.7%     | $0.0     | $0.2     | 11.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2425  | 239   | 511    | 1675   | 31.9%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2425  | 239   | 511    | 1675   | 31.9%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1675  | 0     | 0      | 1675   | 0.0%      | $0.1     |
| Time Held: <30m        | 750   | 239   | 511    | 0      | 31.9%     | $-0.3    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 420   | 19    | 36     | 365    | 34.5%     | $0.0     | 🟢          |
| Afternoon (12:00-16:00) | 924   | 39    | 141    | 744    | 21.7%     | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 505   | 82    | 148    | 275    | 35.7%     | $0.1     | 🟢          |
| ORB (9:30-10:00)       | 137   | 47    | 63     | 27     | 42.7%     | $0.2     | 🟢          |
| Pre-market             | 439   | 52    | 123    | 264    | 29.7%     | $-0.0    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 439    | 279        | 160        | 0          | 63.6%     | 36.4%     | 0.0%      |
| ORB (9:30-10:00)       | 137    | 107        | 30         | 0          | 78.1%     | 21.9%     | 0.0%      |
| Morning (10:00-12:00)  | 505    | 466        | 39         | 0          | 92.3%     | 7.7%      | 0.0%      |
| Afternoon (12:00-16:00) | 924    | 901        | 23         | 0          | 97.5%     | 2.5%      | 0.0%      |
| After-hours (16:00-20:00) | 420    | 395        | 25         | 0          | 94.0%     | 6.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 50-59%     | 72     | 22    | 31     | 19     | 41.5%     | $0.2         | 🟢          |
| Pre-market             | 60-69%     | 88     | 10    | 31     | 47     | 24.4%     | $-0.3        | 🔴          |
| Pre-market             | 70-79%     | 182    | 15    | 39     | 128    | 27.8%     | $-0.1        | 🔴          |
| Pre-market             | 80-89%     | 93     | 5     | 18     | 70     | 21.7%     | $0.1         | 🔴          |
| Pre-market             | 90-99%     | 4      | 0     | 4      | 0      | 0.0%      | $-1.3        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 4      | 2     | 2      | 0      | 50.0%     | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 26     | 13    | 13     | 0      | 50.0%     | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 60     | 15    | 29     | 16     | 34.1%     | $-0.2        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 40     | 14    | 16     | 10     | 46.7%     | $0.3         | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 7      | 3     | 3      | 1      | 50.0%     | $0.4         | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 39     | 14    | 18     | 7      | 43.8%     | $0.4         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 315    | 51    | 94     | 170    | 35.2%     | $0.0         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 142    | 17    | 33     | 92     | 34.0%     | $0.5         | 🟢          |
| Morning (10:00-12:00)  | 90-99%     | 9      | 0     | 3      | 6      | 0.0%      | $-1.4        | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 23     | 0     | 7      | 16     | 0.0%      | $-1.4        | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 637    | 23    | 98     | 516    | 19.0%     | $-0.5        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 254    | 16    | 32     | 206    | 33.3%     | $0.2         | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 10     | 0     | 4      | 6      | 0.0%      | $-0.9        | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 25     | 0     | 1      | 24     | 0.0%      | $6.1         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 249    | 9     | 24     | 216    | 27.3%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 80-89%     | 135    | 10    | 10     | 115    | 50.0%     | $0.5         | 🟢          |
| After-hours (16:00-20:00) | 90-99%     | 11     | 0     | 1      | 10     | 0.0%      | $-0.1        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1188  | 154   | 182    | 852    | 45.8%     | $0.2     |
| SHORT        | 1237  | 85    | 329    | 823    | 20.5%     | $-0.2    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 164   | 51    | 113    | 0      | 31.1%     | $-0.2    |
| Long (30-60 min)       | 1675  | 0     | 0      | 1675   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 311   | 109   | 202    | 0      | 35.0%     | $-0.1    |
| Slow (15-30 min)       | 252   | 76    | 176    | 0      | 30.2%     | $-0.4    |
| Very Fast (<1 min)     | 23    | 3     | 20     | 0      | 13.0%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.27 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1675 time-outs): $-0.00
- 🎯 Best performance at 50-59% confidence (42.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (16.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.00) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.12) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (42.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1462s / 24.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 69% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### depth_imbalance_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,811  |  **Win Rate:** 9.0%  |  **Avg P&L (resolved):** $-1.6  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 1640s (27.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 39    | 2     | 2      | 35     | 50.0%     | $0.0     | $0.2     | 13.7%    |
| 40-49%         | 546   | 8     | 62     | 476    | 11.4%     | $0.0     | $0.1     | 4.1%     |
| 50-59%         | 1016  | 14    | 155    | 847    | 8.3%      | $0.0     | $0.0     | 3.3%     |
| 60-69%         | 144   | 1     | 31     | 112    | 3.1%      | $0.0     | $0.1     | 3.8%     |
| 70-79%         | 66    | 1     | 12     | 53     | 7.7%      | $0.0     | $0.1     | 6.2%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1811  | 26    | 262    | 1523   | 9.0%      | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1811  | 26    | 262    | 1523   | 9.0%      | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1523  | 0     | 0      | 1523   | 0.0%      | $0.1     |
| Time Held: <30m        | 288   | 26    | 262    | 0      | 9.0%      | $-1.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 410   | 0     | 24     | 386    | 0.0%      | $-0.1    | 🔴          |
| Afternoon (12:00-16:00) | 598   | 0     | 24     | 574    | 0.0%      | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 358   | 10    | 98     | 250    | 9.3%      | $-0.4    | 🟢          |
| ORB (9:30-10:00)       | 104   | 16    | 39     | 49     | 29.1%     | $-0.3    | 🟢          |
| Pre-market             | 341   | 0     | 77     | 264    | 0.0%      | $-0.5    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 341    | 6          | 231        | 104        | 1.8%      | 67.7%     | 30.5%     |
| ORB (9:30-10:00)       | 104    | 13         | 67         | 24         | 12.5%     | 64.4%     | 23.1%     |
| Morning (10:00-12:00)  | 358    | 15         | 252        | 91         | 4.2%      | 70.4%     | 25.4%     |
| Afternoon (12:00-16:00) | 598    | 26         | 373        | 199        | 4.3%      | 62.4%     | 33.3%     |
| After-hours (16:00-20:00) | 410    | 6          | 237        | 167        | 1.5%      | 57.8%     | 40.7%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 5      | 0     | 0      | 5      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 40-49%     | 99     | 0     | 20     | 79     | 0.0%      | $-1.2        | 🔴          |
| Pre-market             | 50-59%     | 212    | 0     | 51     | 161    | 0.0%      | $-2.4        | 🔴          |
| Pre-market             | 60-69%     | 19     | 0     | 4      | 15     | 0.0%      | $-2.0        | ⚠️         |
| Pre-market             | 70-79%     | 6      | 0     | 2      | 4      | 0.0%      | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.9        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 23     | 5     | 7      | 11     | 41.7%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 50     | 10    | 20     | 20     | 33.3%     | $-0.5        | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 17     | 0     | 8      | 9      | 0.0%      | $-2.3        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 13     | 1     | 3      | 9      | 25.0%     | $-0.8        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 5      | 2     | 0      | 3      | 100.0%    | $8.4         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 86     | 3     | 23     | 60     | 11.5%     | $-1.1        | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 215    | 4     | 58     | 153    | 6.5%      | $-1.8        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 37     | 1     | 12     | 24     | 7.7%      | $-2.7        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 15     | 0     | 5      | 10     | 0.0%      | $-0.9        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 14     | 0     | 0      | 14     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 185    | 0     | 5      | 180    | 0.0%      | $0.8         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 322    | 0     | 15     | 307    | 0.0%      | $2.4         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 51     | 0     | 3      | 48     | 0.0%      | $3.5         | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 26     | 0     | 1      | 25     | 0.0%      | $2.9         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 14     | 0     | 1      | 13     | 0.0%      | $-1.1        | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 153    | 0     | 7      | 146    | 0.0%      | $-1.1        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 217    | 0     | 11     | 206    | 0.0%      | $-3.4        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 20     | 0     | 4      | 16     | 0.0%      | $-2.4        | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 6      | 0     | 1      | 5      | 0.0%      | $-2.9        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 288   | 10    | 28     | 250    | 26.3%     | $0.3     |
| SHORT        | 1523  | 16    | 234    | 1273   | 6.4%      | $-0.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 36    | 2     | 34     | 0      | 5.6%      | $-2.0    |
| Long (30-60 min)       | 1523  | 0     | 0      | 1523   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 145   | 17    | 128    | 0      | 11.7%     | $-1.5    |
| Slow (15-30 min)       | 102   | 7     | 95     | 0      | 6.9%      | $-1.5    |
| Very Fast (<1 min)     | 5     | 0     | 5      | 0      | 0.0%      | $-1.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 9.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.57 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1523 time-outs): $-0.19
- 🎯 Best performance at 30-39% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (3.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.19) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.07) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (29.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1640s / 27.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 84% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,365  |  **Win Rate:** 24.7%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $0.1  |  **Avg Hold:** 3128s (52.1m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 60-69%         | 1     | 0     | 0      | 1      | 0.0%      | $0.0     | $2.9     | 83.0%    |
| 70-79%         | 64    | 4     | 5      | 55     | 44.4%     | $0.0     | $0.1     | 0.4%     |
| 80-89%         | 1300  | 67    | 211    | 1022   | 24.1%     | $0.0     | $0.2     | 8.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1365  | 71    | 216    | 1078   | 24.7%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1365  | 71    | 216    | 1078   | 24.7%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1168  | 34    | 56     | 1078   | 37.8%     | $0.3     |
| Time Held: <30m        | 197   | 37    | 160    | 0      | 18.8%     | $-0.7    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 176   | 0     | 18     | 158    | 0.0%      | $0.0     | 🔴          |
| Afternoon (12:00-16:00) | 552   | 0     | 33     | 519    | 0.0%      | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 350   | 48    | 67     | 235    | 41.7%     | $0.4     | 🟢          |
| ORB (9:30-10:00)       | 109   | 10    | 55     | 44     | 15.4%     | $-0.1    | 🔴          |
| Overnight              | 1     | 0     | 0      | 1      | 0.0%      | $0.0     | ⚠️         |
| Pre-market             | 177   | 13    | 43     | 121    | 23.2%     | $0.0     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 177    | 176        | 1          | 0          | 99.4%     | 0.6%      | 0.0%      |
| ORB (9:30-10:00)       | 109    | 109        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 350    | 350        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 552    | 552        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| After-hours (16:00-20:00) | 176    | 176        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Overnight              | 1      | 1          | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 60-69%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 70-79%     | 21     | 2     | 1      | 18     | 66.7%     | $1.8         | ⚠️         |
| Pre-market             | 80-89%     | 155    | 11    | 42     | 102    | 20.8%     | $-0.0        | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 2      | 1     | 0      | 1      | 100.0%    | $6.9         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 107    | 9     | 55     | 43     | 14.1%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 6      | 1     | 1      | 4      | 50.0%     | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 344    | 47    | 66     | 231    | 41.6%     | $1.4         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 7      | 0     | 0      | 7      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 545    | 0     | 33     | 512    | 0.0%      | $0.8         | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 28     | 0     | 3      | 25     | 0.0%      | $-1.4        | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 148    | 0     | 15     | 133    | 0.0%      | $0.6         | 🔴          |
| Overnight              | 80-89%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 678   | 66    | 77     | 535    | 46.2%     | $0.8     |
| SHORT        | 687   | 5     | 139    | 543    | 3.5%      | $-0.5    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 34    | 0     | 34     | 0      | 0.0%      | $-2.5    |
| Long (30-60 min)       | 90    | 34    | 56     | 0      | 37.8%     | $0.5     |
| Medium (5-15 min)      | 82    | 7     | 75     | 0      | 8.5%      | $-1.7    |
| Slow (15-30 min)       | 78    | 30    | 48     | 0      | 38.5%     | $1.1     |
| Very Fast (<1 min)     | 3     | 0     | 3      | 0      | 0.0%      | $-1.2    |
| Very Long (>1h)        | 1078  | 0     | 0      | 1078   | 0.0%      | $0.3     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.32 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1078 time-outs): $0.13
- 🎯 Best performance at 70-79% confidence (44.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (24.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.13) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.28) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (41.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3128s / 52.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 79% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,551  |  **Win Rate:** 41.5%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.1  |  **Avg Hold:** 1538s (25.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 33    | 5     | 3      | 25     | 62.5%     | $0.0     | $0.1     | 9.5%     |
| 20-29%         | 70    | 5     | 10     | 55     | 33.3%     | $0.0     | $0.1     | 9.6%     |
| 30-39%         | 271   | 41    | 35     | 195    | 53.9%     | $0.0     | $0.1     | 5.7%     |
| 40-49%         | 594   | 72    | 99     | 423    | 42.1%     | $0.0     | $0.1     | 6.4%     |
| 50-59%         | 333   | 38    | 61     | 234    | 38.4%     | $0.0     | $0.1     | 4.8%     |
| 60-69%         | 1250  | 97    | 155    | 998    | 38.5%     | $0.0     | $0.0     | 1.1%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2551  | 258   | 363    | 1930   | 41.5%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2551  | 258   | 363    | 1930   | 41.5%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1930  | 0     | 0      | 1930   | 0.0%      | $0.1     |
| Time Held: <30m        | 621   | 258   | 363    | 0      | 41.5%     | $0.0     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 779   | 28    | 49     | 702    | 36.4%     | $-0.1    | 🔴          |
| Afternoon (12:00-16:00) | 735   | 40    | 77     | 618    | 34.2%     | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 409   | 108   | 96     | 205    | 52.9%     | $0.3     | 🟢          |
| ORB (9:30-10:00)       | 112   | 26    | 64     | 22     | 28.9%     | $-0.0    | 🔴          |
| Overnight              | 45    | 0     | 0      | 45     | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 471   | 56    | 77     | 338    | 42.1%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 471    | 0          | 391        | 80         | 0.0%      | 83.0%     | 17.0%     |
| ORB (9:30-10:00)       | 112    | 0          | 65         | 47         | 0.0%      | 58.0%     | 42.0%     |
| Morning (10:00-12:00)  | 409    | 0          | 161        | 248        | 0.0%      | 39.4%     | 60.6%     |
| Afternoon (12:00-16:00) | 735    | 0          | 288        | 447        | 0.0%      | 39.2%     | 60.8%     |
| After-hours (16:00-20:00) | 779    | 0          | 633        | 146        | 0.0%      | 81.3%     | 18.7%     |
| Overnight              | 45     | 0          | 45         | 0          | 0.0%      | 100.0%    | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 33     | 6     | 5      | 22     | 54.5%     | $0.7         | 🟢          |
| Pre-market             | 40-49%     | 47     | 13    | 10     | 24     | 56.5%     | $0.4         | 🟢          |
| Pre-market             | 50-59%     | 32     | 4     | 4      | 24     | 50.0%     | $0.0         | 🟢          |
| Pre-market             | 60-69%     | 359    | 33    | 58     | 268    | 36.3%     | $0.1         | 🔴          |
| ORB (9:30-10:00)       | 10-19%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 3      | 0     | 1      | 2      | 0.0%      | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 10     | 1     | 4      | 5      | 20.0%     | $0.7         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 32     | 7     | 18     | 7      | 28.0%     | $0.0         | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 29     | 7     | 18     | 4      | 28.0%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 36     | 11    | 23     | 2      | 32.4%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 11     | 4     | 0      | 7      | 100.0%    | $0.3         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 24     | 4     | 5      | 15     | 44.4%     | $0.3         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 69     | 17    | 10     | 42     | 63.0%     | $0.9         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 144    | 32    | 34     | 78     | 48.5%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 74     | 20    | 20     | 34     | 50.0%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 87     | 31    | 27     | 29     | 53.4%     | $1.1         | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 20     | 1     | 3      | 16     | 25.0%     | $0.6         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 43     | 1     | 4      | 38     | 20.0%     | $1.6         | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 119    | 14    | 9      | 96     | 60.9%     | $0.9         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 265    | 18    | 27     | 220    | 40.0%     | $0.3         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 170    | 5     | 16     | 149    | 23.8%     | $0.7         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 118    | 1     | 18     | 99     | 5.3%      | $-1.1        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 40     | 3     | 7      | 30     | 30.0%     | $-0.3        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 106    | 2     | 10     | 94     | 16.7%     | $-0.6        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 28     | 2     | 3      | 23     | 40.0%     | $0.2         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 605    | 21    | 29     | 555    | 42.0%     | $-0.6        | 🟢          |
| Overnight              | 60-69%     | 45     | 0     | 0      | 45     | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2000  | 225   | 247    | 1528   | 47.7%     | $0.1     |
| SHORT        | 551   | 33    | 116    | 402    | 22.1%     | $-0.1    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 142   | 50    | 92     | 0      | 35.2%     | $-0.2    |
| Long (30-60 min)       | 1930  | 0     | 0      | 1930   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 245   | 120   | 125    | 0      | 49.0%     | $0.3     |
| Slow (15-30 min)       | 214   | 86    | 128    | 0      | 40.2%     | $-0.1    |
| Very Fast (<1 min)     | 20    | 2     | 18     | 0      | 10.0%     | $-0.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 41.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.00 — profitable even with 41.5% win rate (good risk/reward).
- 💰 Avg P&L per signal (incl. 1930 time-outs): $0.05
- 🎯 Best performance at 10-19% confidence (62.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (33.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.05) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.07) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (52.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1538s / 25.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 76% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,160  |  **Win Rate:** 22.1%  |  **Avg P&L (resolved):** $-0.6  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 2226s (37.1m)  |  **Median Hold:** 2700s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 2     | 0     | 0      | 2      | 0.0%      | $0.0     | $0.5     | 53.0%    |
| 30-39%         | 10    | 0     | 2      | 8      | 0.0%      | $0.0     | $0.1     | 3.4%     |
| 40-49%         | 65    | 4     | 11     | 50     | 26.7%     | $0.0     | $0.1     | 5.5%     |
| 50-59%         | 390   | 25    | 97     | 268    | 20.5%     | $0.0     | $0.1     | 7.0%     |
| 60-69%         | 366   | 34    | 74     | 258    | 31.5%     | $0.0     | $0.1     | 5.3%     |
| 70-79%         | 841   | 54    | 209    | 578    | 20.5%     | $0.0     | $0.1     | 8.7%     |
| 80-89%         | 486   | 20    | 90     | 376    | 18.2%     | $0.0     | $0.2     | 8.3%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2160  | 137   | 483    | 1540   | 22.1%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2160  | 137   | 483    | 1540   | 22.1%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1656  | 22    | 94     | 1540   | 19.0%     | $0.1     |
| Time Held: <30m        | 504   | 115   | 389    | 0      | 22.8%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 745   | 7     | 71     | 667    | 9.0%      | $-0.0    | 🔴          |
| Afternoon (12:00-16:00) | 502   | 6     | 87     | 409    | 6.5%      | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 278   | 47    | 102    | 129    | 31.5%     | $-0.0    | 🟢          |
| ORB (9:30-10:00)       | 92    | 31    | 50     | 11     | 38.3%     | $0.5     | 🟢          |
| Pre-market             | 543   | 46    | 173    | 324    | 21.0%     | $-0.2    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 543    | 372        | 170        | 1          | 68.5%     | 31.3%     | 0.2%      |
| ORB (9:30-10:00)       | 92     | 57         | 31         | 4          | 62.0%     | 33.7%     | 4.3%      |
| Morning (10:00-12:00)  | 278    | 146        | 115        | 17         | 52.5%     | 41.4%     | 6.1%      |
| Afternoon (12:00-16:00) | 502    | 220        | 233        | 49         | 43.8%     | 46.4%     | 9.8%      |
| After-hours (16:00-20:00) | 745    | 532        | 207        | 6          | 71.4%     | 27.8%     | 0.8%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 40-49%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 50-59%     | 107    | 8     | 48     | 51     | 14.3%     | $-0.7        | 🔴          |
| Pre-market             | 60-69%     | 63     | 10    | 18     | 35     | 35.7%     | $-0.5        | 🟢          |
| Pre-market             | 70-79%     | 215    | 22    | 64     | 129    | 25.6%     | $-0.1        | 🟢          |
| Pre-market             | 80-89%     | 157    | 6     | 43     | 108    | 12.2%     | $-0.6        | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 4      | 1     | 3      | 0      | 25.0%     | $-0.2        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 15     | 6     | 4      | 5      | 60.0%     | $1.6         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 16     | 8     | 7      | 1      | 53.3%     | $1.7         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 38     | 10    | 24     | 4      | 29.4%     | $-0.1        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 19     | 6     | 12     | 1      | 33.3%     | $0.5         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 4      | 0     | 1      | 3      | 0.0%      | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 13     | 2     | 1      | 10     | 66.7%     | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 53     | 8     | 17     | 28     | 32.0%     | $-0.4        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 62     | 11    | 18     | 33     | 37.9%     | $-0.3        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 107    | 19    | 49     | 39     | 27.9%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 39     | 7     | 16     | 16     | 30.4%     | $0.5         | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 6      | 0     | 1      | 5      | 0.0%      | $-1.2        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 41     | 1     | 4      | 36     | 20.0%     | $0.3         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 119    | 2     | 16     | 101    | 11.1%     | $0.3         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 114    | 2     | 18     | 94     | 10.0%     | $-0.8        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 163    | 1     | 39     | 123    | 2.5%      | $-1.0        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 57     | 0     | 9      | 48     | 0.0%      | $-0.3        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 6      | 0     | 3      | 3      | 0.0%      | $-1.1        | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 96     | 1     | 12     | 83     | 7.7%      | $-1.3        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 111    | 3     | 13     | 95     | 18.8%     | $-0.2        | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 318    | 2     | 33     | 283    | 5.7%      | $-0.4        | 🔴          |
| After-hours (16:00-20:00) | 80-89%     | 214    | 1     | 10     | 203    | 9.1%      | $1.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1024  | 100   | 177    | 747    | 36.1%     | $0.2     |
| SHORT        | 1136  | 37    | 306    | 793    | 10.8%     | $-0.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 114   | 21    | 93     | 0      | 18.4%     | $-0.7    |
| Long (30-60 min)       | 1656  | 22    | 94     | 1540   | 19.0%     | $0.1     |
| Medium (5-15 min)      | 176   | 49    | 127    | 0      | 27.8%     | $-0.3    |
| Slow (15-30 min)       | 200   | 43    | 157    | 0      | 21.5%     | $-0.7    |
| Very Fast (<1 min)     | 14    | 2     | 12     | 0      | 14.3%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 22.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.65 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1540 time-outs): $-0.06
- 🎯 Best performance at 60-69% confidence (31.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.06) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.10) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (38.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2226s / 37.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 71% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,128  |  **Win Rate:** 40.6%  |  **Avg P&L (resolved):** $-0.1  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 2642s (44.0m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 30    | 1     | 2      | 27     | 33.3%     | $0.0     | $0.6     | 19.0%    |
| 30-39%         | 333   | 44    | 19     | 270    | 69.8%     | $0.0     | $0.3     | 9.2%     |
| 40-49%         | 465   | 120   | 40     | 305    | 75.0%     | $0.0     | $0.2     | 5.3%     |
| 50-59%         | 567   | 201   | 86     | 280    | 70.0%     | $0.0     | $0.0     | 2.7%     |
| 60-69%         | 483   | 96    | 125    | 262    | 43.4%     | $0.0     | $0.0     | 3.8%     |
| 70-79%         | 277   | 76    | 94     | 107    | 44.7%     | $0.0     | $0.1     | 9.7%     |
| 80-89%         | 721   | 143   | 304    | 274    | 32.0%     | $0.0     | $0.0     | 6.3%     |
| 90-99%         | 2252  | 100   | 473    | 1679   | 17.5%     | $0.0     | $0.0     | 1.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2810  | 393   | 648    | 1769   | 37.8%     | $0.0     |
| Trending (Up)        | 2318  | 388   | 495    | 1435   | 43.9%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 5128  | 781   | 1143   | 3204   | 40.6%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 3611  | 126   | 281    | 3204   | 31.0%     | $0.1     |
| Time Held: <30m        | 1517  | 655   | 862    | 0      | 43.2%     | $-0.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 1114  | 142   | 341    | 631    | 29.4%     | $0.0     | 🔴          |
| Afternoon (12:00-16:00) | 1177  | 256   | 328    | 593    | 43.8%     | $0.1     | 🟢          |
| Morning (10:00-12:00)  | 587   | 132   | 161    | 294    | 45.1%     | $-0.2    | 🟢          |
| ORB (9:30-10:00)       | 147   | 36    | 55     | 56     | 39.6%     | $0.1     | 🔴          |
| Overnight              | 949   | 0     | 0      | 949    | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 1154  | 215   | 258    | 681    | 45.5%     | $-0.0    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1154   | 766        | 215        | 173        | 66.4%     | 18.6%     | 15.0%     |
| ORB (9:30-10:00)       | 147    | 14         | 77         | 56         | 9.5%      | 52.4%     | 38.1%     |
| Morning (10:00-12:00)  | 587    | 197        | 258        | 132        | 33.6%     | 44.0%     | 22.5%     |
| Afternoon (12:00-16:00) | 1177   | 559        | 357        | 261        | 47.5%     | 30.3%     | 22.2%     |
| After-hours (16:00-20:00) | 1114   | 765        | 143        | 206        | 68.7%     | 12.8%     | 18.5%     |
| Overnight              | 949    | 949        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 8      | 0     | 2      | 6      | 0.0%      | $0.3         | ⚠️         |
| Pre-market             | 30-39%     | 82     | 17    | 9      | 56     | 65.4%     | $1.1         | 🟢          |
| Pre-market             | 40-49%     | 83     | 15    | 14     | 54     | 51.7%     | $0.6         | 🟢          |
| Pre-market             | 50-59%     | 155    | 86    | 28     | 41     | 75.4%     | $0.2         | 🟢          |
| Pre-market             | 60-69%     | 60     | 15    | 21     | 24     | 41.7%     | $-0.2        | 🟢          |
| Pre-market             | 70-79%     | 54     | 18    | 24     | 12     | 42.9%     | $-0.6        | 🟢          |
| Pre-market             | 80-89%     | 152    | 49    | 81     | 22     | 37.7%     | $-0.1        | 🔴          |
| Pre-market             | 90-99%     | 560    | 15    | 79     | 466    | 16.0%     | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 3      | 1     | 0      | 2      | 100.0%    | $-2.6        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 19     | 5     | 6      | 8      | 45.5%     | $-1.3        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 34     | 13    | 14     | 7      | 48.1%     | $1.2         | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 41     | 8     | 19     | 14     | 29.6%     | $-1.0        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 36     | 8     | 9      | 19     | 47.1%     | $1.4         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 13     | 1     | 7      | 5      | 12.5%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 50     | 8     | 4      | 38     | 66.7%     | $-0.5        | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 81     | 20    | 12     | 49     | 62.5%     | $1.1         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 134    | 48    | 39     | 47     | 55.2%     | $-1.2        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 124    | 35    | 33     | 56     | 51.5%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 45     | 9     | 16     | 20     | 36.0%     | $-0.4        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 114    | 3     | 39     | 72     | 7.1%      | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 38     | 9     | 18     | 11     | 33.3%     | $0.3         | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 13     | 0     | 0      | 13     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 123    | 4     | 0      | 119    | 100.0%    | $15.8        | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 125    | 45    | 0      | 80     | 100.0%    | $2.1         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 142    | 53    | 0      | 89     | 100.0%    | $0.8         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 215    | 36    | 57     | 122    | 38.7%     | $-0.6        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 122    | 38    | 39     | 45     | 49.4%     | $0.1         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 297    | 55    | 145    | 97     | 27.5%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 140    | 25    | 87     | 28     | 22.3%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 5      | 0     | 0      | 5      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 59     | 10    | 0      | 49     | 100.0%    | $1.8         | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 142    | 27    | 0      | 115    | 100.0%    | $1.9         | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 95     | 6     | 0      | 89     | 100.0%    | $-0.9        | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 48     | 2     | 5      | 41     | 28.6%     | $1.0         | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 43     | 10    | 8      | 25     | 55.6%     | $0.5         | 🟢          |
| After-hours (16:00-20:00) | 80-89%     | 157    | 36    | 39     | 82     | 48.0%     | $0.1         | 🟢          |
| After-hours (16:00-20:00) | 90-99%     | 565    | 51    | 289    | 225    | 15.0%     | $-0.1        | 🔴          |
| Overnight              | 90-99%     | 949    | 0     | 0      | 949    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2592  | 444   | 490    | 1658   | 47.5%     | $0.2     |
| SHORT        | 2536  | 337   | 653    | 1546   | 34.0%     | $-0.2    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 350   | 173   | 177    | 0      | 49.4%     | $-0.1    |
| Long (30-60 min)       | 407   | 126   | 281    | 0      | 31.0%     | $-0.1    |
| Medium (5-15 min)      | 569   | 216   | 353    | 0      | 38.0%     | $-0.2    |
| Slow (15-30 min)       | 453   | 144   | 309    | 0      | 31.8%     | $-0.2    |
| Very Fast (<1 min)     | 145   | 122   | 23     | 0      | 84.1%     | $0.2     |
| Very Long (>1h)        | 3204  | 0     | 0      | 3204   | 0.0%      | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 40.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.11 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 3204 time-outs): $0.02
- 🎯 Best performance at 40-49% confidence (75.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (17.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.04) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.07) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Pre-market (45.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2642s / 44.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 62% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_squeeze

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 586  |  **Win Rate:** 21.1%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 1726s (28.8m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 8     | 2     | 2      | 4      | 50.0%     | $0.0     | $-0.2    | -9.1%    |
| 50-59%         | 148   | 3     | 1      | 144    | 75.0%     | $0.0     | $0.2     | 8.4%     |
| 60-69%         | 376   | 3     | 23     | 350    | 11.5%     | $0.0     | $-0.1    | -2.0%    |
| 70-79%         | 54    | 0     | 4      | 50     | 0.0%      | $0.0     | $-0.2    | -15.5%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 400   | 1     | 10     | 389    | 9.1%      | $-0.0    |
| Trending (Up)        | 186   | 7     | 20     | 159    | 25.9%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 586   | 8     | 30     | 548    | 21.1%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 548   | 0     | 0      | 548    | 0.0%      | $-0.0    |
| Time Held: <30m        | 38    | 8     | 30     | 0      | 21.1%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 85    | 0     | 0      | 85     | 0.0%      | $-0.3    | 🔴          |
| Afternoon (12:00-16:00) | 152   | 0     | 19     | 133    | 0.0%      | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 47    | 4     | 7      | 36     | 36.4%     | $0.6     | 🟢          |
| ORB (9:30-10:00)       | 19    | 4     | 3      | 12     | 57.1%     | $1.0     | ⚠️         |
| Overnight              | 45    | 0     | 0      | 45     | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 238   | 0     | 1      | 237    | 0.0%      | $-0.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 238    | 48         | 186        | 4          | 20.2%     | 78.2%     | 1.7%      |
| ORB (9:30-10:00)       | 19     | 0          | 16         | 3          | 0.0%      | 84.2%     | 15.8%     |
| Morning (10:00-12:00)  | 47     | 1          | 45         | 1          | 2.1%      | 95.7%     | 2.1%      |
| Afternoon (12:00-16:00) | 152    | 5          | 147        | 0          | 3.3%      | 96.7%     | 0.0%      |
| After-hours (16:00-20:00) | 85     | 0          | 85         | 0          | 0.0%      | 100.0%    | 0.0%      |
| Overnight              | 45     | 0          | 45         | 0          | 0.0%      | 100.0%    | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 40-49%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 50-59%     | 10     | 0     | 0      | 10     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 60-69%     | 176    | 0     | 1      | 175    | 0.0%      | $-20.7       | 🔴          |
| Pre-market             | 70-79%     | 48     | 0     | 0      | 48     | 0.0%      | $0.0         | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 3      | 1     | 2      | 0      | 33.3%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 10     | 1     | 1      | 8      | 50.0%     | $5.3         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 6      | 2     | 0      | 4      | 100.0%    | $4.0         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 1      | 1     | 0      | 0      | 100.0%    | $4.8         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 27     | 2     | 0      | 25     | 100.0%    | $11.1        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 18     | 1     | 6      | 11     | 14.3%     | $0.2         | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.0        | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 92     | 0     | 0      | 92     | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 55     | 0     | 16     | 39     | 0.0%      | $-1.4        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 5      | 0     | 3      | 2      | 0.0%      | $-1.1        | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 9      | 0     | 0      | 9      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 76     | 0     | 0      | 76     | 0.0%      | $0.0         | 🔴          |
| Overnight              | 60-69%     | 45     | 0     | 0      | 45     | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 586   | 8     | 30     | 548    | 21.1%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 8     | 4     | 4      | 0      | 50.0%     | $1.2     |
| Long (30-60 min)       | 548   | 0     | 0      | 548    | 0.0%      | $-0.0    |
| Medium (5-15 min)      | 17    | 2     | 15     | 0      | 11.8%     | $-0.6    |
| Slow (15-30 min)       | 12    | 2     | 10     | 0      | 16.7%     | $-0.5    |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-0.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 21.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.22 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 548 time-outs): $-0.05
- 🎯 Best performance at 50-59% confidence (75.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.04) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $-0.03) — optimal time held is Time Held: 30-90m.
- ⚠️ Best signal generation window: ORB (9:30-10:00) (57.1% win rate) — but only 19 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (1726s / 28.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 94% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,794  |  **Win Rate:** 27.8%  |  **Avg P&L (resolved):** $-0.7  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 1684s (28.1m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 36    | 6     | 11     | 19     | 35.3%     | $0.0     | $0.3     | 7.8%     |
| 30-39%         | 544   | 5     | 13     | 526    | 27.8%     | $0.0     | $0.1     | 7.3%     |
| 40-49%         | 219   | 18    | 29     | 172    | 38.3%     | $0.0     | $-0.1    | 7.5%     |
| 50-59%         | 203   | 20    | 38     | 145    | 34.5%     | $0.0     | $0.1     | 5.6%     |
| 60-69%         | 147   | 6     | 32     | 109    | 15.8%     | $0.0     | $0.2     | 17.1%    |
| 70-79%         | 94    | 2     | 10     | 82     | 16.7%     | $0.0     | $0.0     | 4.5%     |
| 80-89%         | 10    | 0     | 3      | 7      | 0.0%      | $0.0     | $-0.7    | -27.6%   |
| 90-99%         | 126   | 0     | 0      | 126    | 0.0%      | $0.0     | $-0.1    | -5.2%    |
| 100%           | 415   | 0     | 12     | 403    | 0.0%      | $0.0     | $0.1     | 6.2%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 973   | 24    | 70     | 879    | 25.5%     | $0.0     |
| Trending (Up)        | 821   | 33    | 78     | 710    | 29.7%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1794  | 57    | 148    | 1589   | 27.8%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1589  | 0     | 0      | 1589   | 0.0%      | $0.1     |
| Time Held: <30m        | 205   | 57    | 148    | 0      | 27.8%     | $-0.7    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 259   | 1     | 0      | 258    | 100.0%    | $-0.1    | 🟢          |
| Afternoon (12:00-16:00) | 469   | 9     | 47     | 413    | 16.1%     | $-0.2    | 🔴          |
| Morning (10:00-12:00)  | 192   | 41    | 86     | 65     | 32.3%     | $-0.1    | 🟢          |
| ORB (9:30-10:00)       | 40    | 5     | 10     | 25     | 33.3%     | $0.9     | 🟢          |
| Overnight              | 198   | 0     | 0      | 198    | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 636   | 1     | 5      | 630    | 16.7%     | $0.1     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 636    | 293        | 88         | 255        | 46.1%     | 13.8%     | 40.1%     |
| ORB (9:30-10:00)       | 40     | 24         | 4          | 12         | 60.0%     | 10.0%     | 30.0%     |
| Morning (10:00-12:00)  | 192    | 56         | 59         | 77         | 29.2%     | 30.7%     | 40.1%     |
| Afternoon (12:00-16:00) | 469    | 233        | 116        | 120        | 49.7%     | 24.7%     | 25.6%     |
| After-hours (16:00-20:00) | 259    | 39         | 83         | 137        | 15.1%     | 32.0%     | 52.9%     |
| Overnight              | 198    | 0          | 0          | 198        | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 30-39%     | 222    | 0     | 0      | 222    | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 40-49%     | 32     | 0     | 0      | 32     | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 50-59%     | 42     | 0     | 1      | 41     | 0.0%      | $17.6        | 🔴          |
| Pre-market             | 60-69%     | 46     | 1     | 1      | 44     | 50.0%     | $15.0        | 🟢          |
| Pre-market             | 70-79%     | 14     | 0     | 0      | 14     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 80-89%     | 7      | 0     | 0      | 7      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 90-99%     | 117    | 0     | 0      | 117    | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 100%       | 155    | 0     | 3      | 152    | 0.0%      | $-3.1        | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.9        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 3      | 0     | 2      | 1      | 0.0%      | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 8      | 3     | 3      | 2      | 50.0%     | $2.9         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 3      | 2     | 1      | 0      | 66.7%     | $0.8         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 24     | 0     | 2      | 22     | 0.0%      | $8.9         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 17     | 6     | 10     | 1      | 37.5%     | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 21     | 5     | 11     | 5      | 31.2%     | $1.0         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 39     | 14    | 21     | 4      | 40.0%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 39     | 12    | 22     | 5      | 35.3%     | $-0.3        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 20     | 2     | 14     | 4      | 12.5%     | $-0.8        | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 13     | 2     | 5      | 6      | 28.6%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 3      | 0     | 3      | 0      | 0.0%      | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 100%       | 40     | 0     | 0      | 40     | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 15     | 0     | 0      | 15     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 32     | 0     | 0      | 32     | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 73     | 0     | 5      | 68     | 0.0%      | $-7.7        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 67     | 6     | 14     | 47     | 30.0%     | $-1.9        | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 49     | 3     | 16     | 30     | 15.8%     | $-1.9        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 37     | 0     | 5      | 32     | 0.0%      | $1.0         | 🔴          |
| Afternoon (12:00-16:00) | 100%       | 196    | 0     | 7      | 189    | 0.0%      | $1.4         | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 68     | 0     | 0      | 68     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 67     | 1     | 0      | 66     | 100.0%    | $-7.3        | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 52     | 0     | 0      | 52     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 31     | 0     | 0      | 31     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 30     | 0     | 0      | 30     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 90-99%     | 9      | 0     | 0      | 9      | 0.0%      | $0.0         | ⚠️         |
| Overnight              | 30-39%     | 198    | 0     | 0      | 198    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1334  | 40    | 55     | 1239   | 42.1%     | $0.1     |
| SHORT        | 460   | 17    | 93     | 350    | 15.5%     | $-0.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 31    | 4     | 27     | 0      | 12.9%     | $-1.4    |
| Long (30-60 min)       | 1589  | 0     | 0      | 1589   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 97    | 34    | 63     | 0      | 35.1%     | $-0.4    |
| Slow (15-30 min)       | 73    | 18    | 55     | 0      | 24.7%     | $-1.0    |
| Very Fast (<1 min)     | 4     | 1     | 3      | 0      | 25.0%     | $-0.0    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 27.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.75 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1589 time-outs): $-0.00
- 🎯 Best performance at 40-49% confidence (38.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 100% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.00) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.10) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: After-hours (16:00-20:00) (100.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1684s / 28.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 89% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,157  |  **Win Rate:** 55.1%  |  **Avg P&L (resolved):** $0.6  |  **Avg P&L (all):** $0.4  |  **Avg Hold:** 2692s (44.9m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 79    | 6     | 8      | 65     | 42.9%     | $0.0     | $-0.1    | -2.4%    |
| 40-49%         | 164   | 12    | 20     | 132    | 37.5%     | $0.0     | $0.2     | 9.1%     |
| 50-59%         | 66    | 29    | 5      | 32     | 85.3%     | $0.0     | $0.1     | 3.8%     |
| 60-69%         | 753   | 171   | 127    | 455    | 57.4%     | $0.0     | $0.2     | 12.1%    |
| 70-79%         | 76    | 25    | 30     | 21     | 45.5%     | $0.0     | $0.2     | 9.1%     |
| 80-89%         | 19    | 5     | 12     | 2      | 29.4%     | $0.0     | $0.0     | 3.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1040  | 221   | 175    | 644    | 55.8%     | $0.4     |
| Trending (Up)        | 117   | 27    | 27     | 63     | 50.0%     | $0.3     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1157  | 248   | 202    | 707    | 55.1%     | $0.4     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 839   | 86    | 46     | 707    | 65.2%     | $0.4     |
| Time Held: <30m        | 318   | 162   | 156    | 0      | 50.9%     | $0.4     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 209   | 8     | 27     | 174    | 22.9%     | $0.0     | 🔴          |
| Afternoon (12:00-16:00) | 475   | 101   | 67     | 307    | 60.1%     | $0.3     | 🟢          |
| Morning (10:00-12:00)  | 248   | 58    | 47     | 143    | 55.2%     | $0.5     | 🟢          |
| ORB (9:30-10:00)       | 84    | 35    | 43     | 6      | 44.9%     | $0.5     | 🔴          |
| Pre-market             | 141   | 46    | 18     | 77     | 71.9%     | $0.8     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 141    | 1          | 57         | 83         | 0.7%      | 40.4%     | 58.9%     |
| ORB (9:30-10:00)       | 84     | 27         | 57         | 0          | 32.1%     | 67.9%     | 0.0%      |
| Morning (10:00-12:00)  | 248    | 37         | 211        | 0          | 14.9%     | 85.1%     | 0.0%      |
| Afternoon (12:00-16:00) | 475    | 26         | 449        | 0          | 5.5%      | 94.5%     | 0.0%      |
| After-hours (16:00-20:00) | 209    | 4          | 45         | 160        | 1.9%      | 21.5%     | 76.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 21     | 1     | 2      | 18     | 33.3%     | $-0.9        | ⚠️         |
| Pre-market             | 40-49%     | 62     | 11    | 8      | 43     | 57.9%     | $1.5         | 🟢          |
| Pre-market             | 50-59%     | 38     | 26    | 1      | 11     | 96.3%     | $2.6         | 🟢          |
| Pre-market             | 60-69%     | 19     | 7     | 7      | 5      | 50.0%     | $0.7         | ⚠️         |
| Pre-market             | 70-79%     | 1      | 1     | 0      | 0      | 100.0%    | $1.6         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 1      | 1     | 0      | 0      | 100.0%    | $2.3         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 56     | 28    | 22     | 6      | 56.0%     | $0.9         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 16     | 5     | 11     | 0      | 31.2%     | $-0.2        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 11     | 1     | 10     | 0      | 9.1%      | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 211    | 40    | 33     | 138    | 54.8%     | $1.4         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 33     | 15    | 13     | 5      | 53.6%     | $1.0         | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 4      | 3     | 1      | 0      | 75.0%     | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 449    | 96    | 61     | 292    | 61.1%     | $1.0         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 22     | 4     | 5      | 13     | 44.4%     | $1.1         | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 4      | 1     | 1      | 2      | 50.0%     | $0.3         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 58     | 5     | 6      | 47     | 45.5%     | $-0.4        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 102    | 1     | 12     | 89     | 7.7%      | $-0.0        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 27     | 2     | 4      | 21     | 33.3%     | $0.8         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 18     | 0     | 4      | 14     | 0.0%      | $0.8         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 4      | 0     | 1      | 3      | 0.0%      | $-1.1        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1157  | 248   | 202    | 707    | 55.1%     | $0.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 73    | 22    | 51     | 0      | 30.1%     | $-0.3    |
| Long (30-60 min)       | 132   | 86    | 46     | 0      | 65.2%     | $0.9     |
| Medium (5-15 min)      | 129   | 63    | 66     | 0      | 48.8%     | $0.5     |
| Slow (15-30 min)       | 103   | 72    | 31     | 0      | 69.9%     | $0.8     |
| Very Fast (<1 min)     | 13    | 5     | 8      | 0      | 38.5%     | $0.4     |
| Very Long (>1h)        | 707   | 0     | 0      | 707    | 0.0%      | $0.3     |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 55.1% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 💰 Positive avg P&L per resolved signal: $0.56 — profitable even with 55.1% win rate (good risk/reward).
- 💰 Avg P&L per signal (incl. 707 time-outs): $0.38
- 🎯 Best performance at 50-59% confidence (85.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (29.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.39) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.40) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: Pre-market (71.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2692s / 44.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 61% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,769  |  **Win Rate:** 22.8%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 3032s (50.5m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 9     | 0     | 6      | 3      | 0.0%      | $0.0     | $-0.1    | -13.8%   |
| 30-39%         | 35    | 4     | 19     | 12     | 17.4%     | $0.0     | $0.1     | 16.5%    |
| 40-49%         | 210   | 13    | 42     | 155    | 23.6%     | $0.0     | $0.2     | 22.5%    |
| 50-59%         | 486   | 13    | 128    | 345    | 9.2%      | $0.0     | $0.2     | 25.4%    |
| 60-69%         | 702   | 27    | 225    | 450    | 10.7%     | $0.0     | $0.1     | 9.2%     |
| 70-79%         | 1206  | 93    | 101    | 1012   | 47.9%     | $0.0     | $0.0     | 0.6%     |
| 80-89%         | 116   | 11    | 28     | 77     | 28.2%     | $0.0     | $-0.0    | -0.5%    |
| 90-99%         | 5     | 1     | 1      | 3      | 50.0%     | $0.0     | $-0.0    | -0.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1625  | 113   | 327    | 1185   | 25.7%     | $0.0     |
| Trending (Up)        | 1144  | 49    | 223    | 872    | 18.0%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2769  | 162   | 550    | 2057   | 22.8%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 2295  | 63    | 175    | 2057   | 26.5%     | $0.1     |
| Time Held: <30m        | 474   | 99    | 375    | 0      | 20.9%     | $-0.4    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 586   | 0     | 42     | 544    | 0.0%      | $-0.1    | 🔴          |
| Afternoon (12:00-16:00) | 642   | 46    | 200    | 396    | 18.7%     | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 293   | 7     | 149    | 137    | 4.5%      | $-0.5    | 🔴          |
| ORB (9:30-10:00)       | 61    | 16    | 15     | 30     | 51.6%     | $1.0     | 🟢          |
| Overnight              | 474   | 0     | 0      | 474    | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 713   | 93    | 144    | 476    | 39.2%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 713    | 376        | 277        | 60         | 52.7%     | 38.8%     | 8.4%      |
| ORB (9:30-10:00)       | 61     | 19         | 39         | 3          | 31.1%     | 63.9%     | 4.9%      |
| Morning (10:00-12:00)  | 293    | 60         | 204        | 29         | 20.5%     | 69.6%     | 9.9%      |
| Afternoon (12:00-16:00) | 642    | 149        | 401        | 92         | 23.2%     | 62.5%     | 14.3%     |
| After-hours (16:00-20:00) | 586    | 249        | 267        | 70         | 42.5%     | 45.6%     | 11.9%     |
| Overnight              | 474    | 474        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 9      | 0     | 6      | 3      | 0.0%      | $-1.5        | ⚠️         |
| Pre-market             | 30-39%     | 23     | 4     | 16     | 3      | 20.0%     | $0.3         | ⚠️         |
| Pre-market             | 40-49%     | 28     | 13    | 8      | 7      | 61.9%     | $3.2         | ⚠️         |
| Pre-market             | 50-59%     | 95     | 9     | 19     | 67     | 32.1%     | $1.3         | 🟢          |
| Pre-market             | 60-69%     | 182    | 3     | 77     | 102    | 3.8%      | $-0.8        | 🔴          |
| Pre-market             | 70-79%     | 371    | 63    | 14     | 294    | 81.8%     | $0.6         | 🟢          |
| Pre-market             | 80-89%     | 5      | 1     | 4      | 0      | 20.0%     | $0.3         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 15     | 1     | 4      | 10     | 20.0%     | $1.7         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 24     | 6     | 6      | 12     | 50.0%     | $2.7         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 16     | 7     | 4      | 5      | 63.6%     | $1.2         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 3      | 2     | 1      | 0      | 66.7%     | $0.1         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.9        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 28     | 0     | 10     | 18     | 0.0%      | $-0.8        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 94     | 1     | 43     | 50     | 2.3%      | $-0.8        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 110    | 3     | 61     | 46     | 4.7%      | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 54     | 1     | 30     | 23     | 3.2%      | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 5      | 1     | 4      | 0      | 20.0%     | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 1      | 1     | 0      | 0      | 100.0%    | $2.5         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 6      | 0     | 1      | 5      | 0.0%      | $1.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 86     | 0     | 19     | 67     | 0.0%      | $0.5         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 193    | 2     | 52     | 139    | 3.7%      | $0.5         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 208    | 15    | 75     | 118    | 16.7%     | $-0.0        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 120    | 22    | 38     | 60     | 36.7%     | $0.4         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 28     | 7     | 14     | 7      | 33.3%     | $-0.1        | ⚠️         |
| Afternoon (12:00-16:00) | 90-99%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.7        | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 5      | 0     | 1      | 4      | 0.0%      | $0.7         | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 65     | 0     | 5      | 60     | 0.0%      | $-4.1        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 89     | 0     | 10     | 79     | 0.0%      | $-2.7        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 178    | 0     | 6      | 172    | 0.0%      | $-1.2        | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 171    | 0     | 15     | 156    | 0.0%      | $-1.7        | 🔴          |
| After-hours (16:00-20:00) | 80-89%     | 75     | 0     | 5      | 70     | 0.0%      | $-0.9        | 🔴          |
| After-hours (16:00-20:00) | 90-99%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| Overnight              | 70-79%     | 474    | 0     | 0      | 474    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2675  | 153   | 465    | 2057   | 24.8%     | $0.0     |
| SHORT        | 94    | 9     | 85     | 0      | 9.6%      | $-1.1    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 97    | 20    | 77     | 0      | 20.6%     | $-0.7    |
| Long (30-60 min)       | 238   | 63    | 175    | 0      | 26.5%     | $-0.0    |
| Medium (5-15 min)      | 178   | 38    | 140    | 0      | 21.3%     | $-0.2    |
| Slow (15-30 min)       | 180   | 37    | 143    | 0      | 20.6%     | $-0.5    |
| Very Fast (<1 min)     | 19    | 4     | 15     | 0      | 21.1%     | $-0.7    |
| Very Long (>1h)        | 2057  | 0     | 0      | 2057   | 0.0%      | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 22.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.29 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 2057 time-outs): $-0.01
- 🎯 Best performance at 90-99% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.02) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.07) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (51.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3032s / 50.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 74% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,203  |  **Win Rate:** 50.0%  |  **Avg P&L (resolved):** $0.1  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 876s (14.6m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 3     | 0     | 0      | 3      | 0.0%      | $0.0     | $-0.0    | -9.5%    |
| 40-49%         | 59    | 2     | 1      | 56     | 66.7%     | $0.0     | $-0.0    | -2.8%    |
| 50-59%         | 333   | 5     | 4      | 324    | 55.6%     | $0.0     | $0.0     | 0.6%     |
| 60-69%         | 735   | 20    | 22     | 693    | 47.6%     | $0.0     | $-0.0    | -0.2%    |
| 70-79%         | 73    | 2     | 2      | 69     | 50.0%     | $0.0     | $-0.0    | -2.0%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 797   | 17    | 25     | 755    | 40.5%     | $-0.0    |
| Trending (Up)        | 406   | 12    | 4      | 390    | 75.0%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1203  | 29    | 29     | 1145   | 50.0%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: <30m        | 1203  | 29    | 29     | 1145   | 50.0%     | $0.0     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 203   | 9     | 0      | 194    | 100.0%    | $-0.0    | 🟢          |
| Afternoon (12:00-16:00) | 290   | 6     | 4      | 280    | 60.0%     | $0.1     | 🟢          |
| Morning (10:00-12:00)  | 97    | 8     | 15     | 74     | 34.8%     | $0.0     | 🔴          |
| ORB (9:30-10:00)       | 33    | 6     | 9      | 18     | 40.0%     | $0.2     | 🔴          |
| Overnight              | 237   | 0     | 0      | 237    | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 343   | 0     | 1      | 342    | 0.0%      | $-0.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 343    | 56         | 269        | 18         | 16.3%     | 78.4%     | 5.2%      |
| ORB (9:30-10:00)       | 33     | 0          | 30         | 3          | 0.0%      | 90.9%     | 9.1%      |
| Morning (10:00-12:00)  | 97     | 1          | 93         | 3          | 1.0%      | 95.9%     | 3.1%      |
| Afternoon (12:00-16:00) | 290    | 16         | 249        | 25         | 5.5%      | 85.9%     | 8.6%      |
| After-hours (16:00-20:00) | 203    | 0          | 190        | 13         | 0.0%      | 93.6%     | 6.4%      |
| Overnight              | 237    | 0          | 237        | 0          | 0.0%      | 100.0%    | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 40-49%     | 15     | 0     | 0      | 15     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 50-59%     | 45     | 0     | 0      | 45     | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 60-69%     | 224    | 0     | 1      | 223    | 0.0%      | $-17.8       | 🔴          |
| Pre-market             | 70-79%     | 56     | 0     | 0      | 56     | 0.0%      | $0.0         | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 10     | 2     | 0      | 8      | 100.0%    | $5.0         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 20     | 4     | 9      | 7      | 30.8%     | $-0.3        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 3      | 0     | 1      | 2      | 0.0%      | $-4.6        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 57     | 2     | 4      | 51     | 33.3%     | $-1.2        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 36     | 5     | 10     | 21     | 33.3%     | $0.8         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 1      | 1     | 0      | 0      | 100.0%    | $3.9         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 25     | 2     | 0      | 23     | 100.0%    | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 125    | 0     | 0      | 125    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 124    | 3     | 2      | 119    | 60.0%     | $-0.5        | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 16     | 1     | 2      | 13     | 33.3%     | $0.9         | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 13     | 0     | 0      | 13     | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 96     | 1     | 0      | 95     | 100.0%    | $-15.7       | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 94     | 8     | 0      | 86     | 100.0%    | $1.5         | 🟢          |
| Overnight              | 60-69%     | 237    | 0     | 0      | 237    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 523   | 13    | 8      | 502    | 61.9%     | $0.0     |
| SHORT        | 680   | 16    | 21     | 643    | 43.2%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 17    | 11    | 6      | 0      | 64.7%     | $1.0     |
| Medium (5-15 min)      | 34    | 13    | 21     | 0      | 38.2%     | $-0.5    |
| Slow (15-30 min)       | 1145  | 0     | 0      | 1145   | 0.0%      | $0.0     |
| Very Fast (<1 min)     | 7     | 5     | 2      | 0      | 71.4%     | $0.9     |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 50.0% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 💰 Positive avg P&L per resolved signal: $0.09 — profitable even with 50.0% win rate (good risk/reward).
- 💰 Avg P&L per signal (incl. 1145 time-outs): $0.01
- 🎯 Best performance at 40-49% confidence (66.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (47.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.08) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.01) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: After-hours (16:00-20:00) (100.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (876s / 14.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 95% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,409  |  **Win Rate:** 45.5%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 6323s (105.4m)  |  **Median Hold:** 7200s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 59    | 16    | 15     | 28     | 51.6%     | $0.0     | $0.4     | 19.1%    |
| 30-39%         | 181   | 25    | 63     | 93     | 28.4%     | $0.0     | $0.0     | 2.0%     |
| 40-49%         | 620   | 33    | 49     | 538    | 40.2%     | $0.0     | $-0.0    | -0.6%    |
| 50-59%         | 296   | 42    | 12     | 242    | 77.8%     | $0.0     | $0.1     | 7.4%     |
| 60-69%         | 206   | 11    | 9      | 186    | 55.0%     | $0.0     | $0.3     | 15.5%    |
| 70-79%         | 47    | 0     | 4      | 43     | 0.0%      | $0.0     | $0.4     | 20.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 924   | 79    | 57     | 788    | 58.1%     | $0.1     |
| Trending (Up)        | 485   | 48    | 95     | 342    | 33.6%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1409  | 127   | 152    | 1130   | 45.5%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 126   | 62    | 64     | 0      | 49.2%     | $-0.1    |
| Time Held: 90-240m     | 1169  | 14    | 25     | 1130   | 35.9%     | $0.1     |
| Time Held: <30m        | 114   | 51    | 63     | 0      | 44.7%     | $-0.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 463   | 19    | 53     | 391    | 26.4%     | $-0.2    | 🔴          |
| Afternoon (12:00-16:00) | 327   | 46    | 28     | 253    | 62.2%     | $0.2     | 🟢          |
| Morning (10:00-12:00)  | 178   | 18    | 45     | 115    | 28.6%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 29    | 10    | 15     | 4      | 40.0%     | $0.3     | ⚠️         |
| Overnight              | 237   | 0     | 0      | 237    | 0.0%      | $0.0     | 🔴          |
| Pre-market             | 175   | 34    | 11     | 130    | 75.6%     | $0.5     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 175    | 0          | 27         | 148        | 0.0%      | 15.4%     | 84.6%     |
| ORB (9:30-10:00)       | 29     | 1          | 6          | 22         | 3.4%      | 20.7%     | 75.9%     |
| Morning (10:00-12:00)  | 178    | 4          | 103        | 71         | 2.2%      | 57.9%     | 39.9%     |
| Afternoon (12:00-16:00) | 327    | 42         | 185        | 100        | 12.8%     | 56.6%     | 30.6%     |
| After-hours (16:00-20:00) | 463    | 0          | 181        | 282        | 0.0%      | 39.1%     | 60.9%     |
| Overnight              | 237    | 0          | 0          | 237        | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 12     | 12    | 0      | 0      | 100.0%    | $3.6         | ⚠️         |
| Pre-market             | 30-39%     | 22     | 3     | 5      | 14     | 37.5%     | $1.1         | ⚠️         |
| Pre-market             | 40-49%     | 114    | 0     | 3      | 111    | 0.0%      | $-2.4        | 🔴          |
| Pre-market             | 50-59%     | 20     | 14    | 3      | 3      | 82.4%     | $1.5         | ⚠️         |
| Pre-market             | 60-69%     | 7      | 5     | 0      | 2      | 100.0%    | $2.0         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 11     | 7     | 4      | 0      | 63.6%     | $2.0         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 11     | 3     | 6      | 2      | 33.3%     | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 6      | 0     | 4      | 2      | 0.0%      | $-1.8        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.3        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 7      | 0     | 5      | 2      | 0.0%      | $-3.1        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 15     | 6     | 9      | 0      | 40.0%     | $0.1         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 49     | 7     | 21     | 21     | 25.0%     | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 58     | 4     | 4      | 50     | 50.0%     | $1.8         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 45     | 1     | 5      | 39     | 16.7%     | $3.2         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 4      | 0     | 1      | 3      | 0.0%      | $-0.5        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 7      | 2     | 0      | 5      | 100.0%    | $5.5         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 35     | 8     | 4      | 23     | 66.7%     | $-1.3        | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 58     | 14    | 17     | 27     | 45.2%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 75     | 18    | 1      | 56     | 94.7%     | $2.7         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 110    | 4     | 4      | 102    | 50.0%     | $3.6         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 42     | 0     | 2      | 40     | 0.0%      | $6.6         | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 33     | 2     | 10     | 21     | 16.7%     | $-1.2        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 98     | 1     | 41     | 56     | 2.4%      | $-2.3        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 151    | 9     | 2      | 140    | 81.8%     | $-1.6        | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 137    | 6     | 0      | 131    | 100.0%    | $4.3         | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 44     | 1     | 0      | 43     | 100.0%    | $15.2        | 🟢          |
| Overnight              | 40-49%     | 237    | 0     | 0      | 237    | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 448   | 68    | 21     | 359    | 76.4%     | $0.4     |
| SHORT        | 961   | 59    | 131    | 771    | 31.1%     | $-0.1    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 12    | 4     | 8      | 0      | 33.3%     | $-1.1    |
| Long (30-60 min)       | 70    | 40    | 30     | 0      | 57.1%     | $0.3     |
| Medium (5-15 min)      | 48    | 18    | 30     | 0      | 37.5%     | $-0.3    |
| Slow (15-30 min)       | 53    | 28    | 25     | 0      | 52.8%     | $0.3     |
| Very Fast (<1 min)     | 1     | 1     | 0      | 0      | 100.0%    | $3.9     |
| Very Long (>1h)        | 1225  | 36    | 59     | 1130   | 37.9%     | $0.0     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 45.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.17 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1130 time-outs): $0.05
- 🎯 Best performance at 50-59% confidence (77.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.14) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.07) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Pre-market (75.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (6323s / 105.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 80% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

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
| 1779989458.224 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 11           | Depth imbalance SHORT: IR=0.60 (+40.1%), ROC=-0... |
| 1779975001.528 | 17     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration | 10           | Depth imbalance SHORT: IR=0.36 (+63.7%), ROC=-0... |
| 1779975124.122 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration | 10           | Depth decay SHORT: ROC=-0.3158 (-31.58%), vol/d... |
| 1779976695.801 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 10           | Depth decay LONG: ROC=-0.1668 (-16.68%), vol/de... |
| 1779976998.536 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, strike_concentration | 10           | Squeeze LONG: breakout through call wall at 310... |
| 1779981349.221 | 17     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 10           | Depth decay SHORT: ROC=-0.1618 (-16.18%), vol/d... |
| 1779983466.178 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 10           | Flow imbalance LONG: AggVSI=0.917 (+91.7%), ROC... |
| 1779993484.315 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 10           | Call wall at 520.0 rejected price, GEX=1346695,... |
| 1779995263.129 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, vol_compression_range | 10           | Depth imbalance LONG: IR=3.85 (+285.2%), ROC=+0... |
| 1779995932.725 | 17     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Magnet pull LONG: price 214.13 below magnet 215... |
| 1780001633.259 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration, vol_compression_range | 10           | Flow imbalance SHORT: AggVSI=-0.840 (+84.0%), R... |
| 1779974867.45  | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779975063.865 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate, strike_concentration | 9            | Depth decay SHORT: ROC=-0.4828 (-48.28%), vol/d... |
| 1779975183.581 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779975310.399 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Magnet pull LONG: price 309.79 below magnet 315... |
| 1779975586.357 | 12     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, vol_compression_range | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779975612.21  | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 9            | Magnet pull LONG: price 310.07 below magnet 315... |
| 1779977399.963 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.1542 (-15.42%), vol/d... |
| 1779979712.88  | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.4437 (-44.37%), vol/d... |
| 1779980651.441 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth imbalance SHORT: IR=0.11 (+89.1%), ROC=-0... |
| 1779980769.863 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779980913.279 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth imbalance SHORT: IR=0.55 (+44.6%), ROC=-0... |
| 1779981293.711 | 15     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Breakout SHORT below flip zone 212.50, price=21... |
| 1779981868.916 | 10     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Breakout LONG below flip zone 312.50, price=311... |
| 1779984820.238 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Fade LONG above flip zone 310.00, price=310.71,... |
| 1779985948.796 | 13     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Call wall at 520.0 rejected price, GEX=1243221,... |
| 1779986173.941 | 10     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate | 9            | Depth imbalance LONG: IR=4.48 (+348.3%), ROC=+0... |
| 1779986188.557 | 13     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth decay LONG: ROC=-0.1785 (-17.85%), vol/de... |
| 1779987302.19  | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration | 9            | MEMX accumulation LONG: ESI=0.867 (+86.7%), dev... |
| 1779987957.108 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, vol_compression_range | 9            | Fade LONG above flip zone 520.00, price=520.89,... |
| 1779989199.951 | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration | 9            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1779989439.044 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.2558 (-25.58%), vol/d... |
| 1779989530.833 | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Range LONG: price near lower edge, wall at 440,... |
| 1779990255.723 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration, vol_compression_range | 9            | Strike bounce LONG: 440.0 Put strike, rank #3, ... |
| 1779990559.553 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence | 9            | Confluence SHORT at 215: 2 structural signals, ... |
| 1779992099.408 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_squeeze, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Depth imbalance SHORT: IR=0.34 (+65.7%), ROC=-0... |
| 1779993547.402 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.2120 (-21.20%), vol/d... |
| 1779995201.62  | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate, vol_compression_range | 9            | Range SHORT: price near upper edge, call wall a... |
| 1779995642.357 | 11     | confluence_reversal, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, strike_concentration | 9            | Breakout SHORT below flip zone 121.00, price=12... |
| 1779995762.409 | 14     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, strike_concentration | 9            | Depth decay LONG: ROC=-0.1900 (-19.00%), vol/de... |
| 1779995872.178 | 13     | confluence_reversal, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Magnet pull LONG: price 214.07 below magnet 215... |
| 1779996974.651 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate | 9            | Confluence SHORT at 215: 2 structural signals, ... |
| 1779997510.002 | 14     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Call wall at 520.0 rejected price, GEX=1394000,... |
| 1780001514.18  | 12     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Depth decay LONG: ROC=-0.2897 (-28.97%), vol/de... |
| 1780002114.071 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration | 9            | Strike bounce SHORT: 215.0 Call strike, rank #2... |
| 1780002304.931 | 10     | confluence_reversal, depth_imbalance_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Call wall at 520.0 rejected price, GEX=1416414,... |
| 1780003000.68  | 17     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Breakout SHORT below flip zone 121.00, price=12... |
| 1780006211.874 | 11     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Range LONG: price near lower edge, wall at 520,... |
| 1780007195.147 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence | 9            | Depth decay SHORT: ROC=-0.1738 (-17.38%), vol/d... |
| 1780008281.0   | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate | 9            | Depth decay LONG: ROC=-0.2237 (-22.37%), vol/de... |

**5524 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 23,692   | 8          | net_gamma=< 131890030  | 34.0%    | $0.0       |
| Gamma Wall Support (510.0)   | 1,034    | 2          | wall_strike=510.0      | 24.3%    | $-0.0      |
| Gamma Wall Support (310.0)   | 786      | 4          | wall_strike=310.0      | 60.0%    | $0.1       |
| Gamma Wall Support (435.0)   | 684      | 4          | wall_strike=435.0      | 50.0%    | $-0.1      |
| Gamma Wall Support (118.0)   | 295      | 3          | wall_strike=118.0      | 42.6%    | $0.2       |
| Gamma Wall Support (210.0)   | 96       | 4          | wall_strike=210.0      | 32.3%    | $0.2       |
| Gamma Wall Support (485.0)   | 67       | 4          | wall_strike=485.0      | 36.7%    | $0.8       |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 4910   | 5      | 5        | 41.1%    | $0.0       | net_gamma  | delta_gamma_squeeze, gamma_flip_breakou  |
| Gamma Exposur  | 13267  | 5      | 5        | 31.4%    | $0.0       | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 786    | 4      | 4        | 60.0%    | $0.1       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 684    | 4      | 4        | 50.0%    | $-0.1      | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 67     | 4      | 4        | 36.7%    | $0.8       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 96     | 4      | 4        | 32.3%    | $0.2       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Exposur  | 605    | 4      | 4        | 24.8%    | $0.1       | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Exposur  | 4910   | 4      | 4        | 21.9%    | $-0.0      | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Wall Su  | 295    | 3      | 3        | 42.6%    | $0.2       | wall_stri  | delta_gamma_squeeze, gamma_wall_bounce,  |
| Gamma Wall Su  | 1034   | 2      | 2        | 24.3%    | $-0.0      | wall_stri  | gamma_wall_bounce, vol_compression_rang  |

**10 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 115      | 6      | 29     | 80     | 17.1%     | 41.6      |
| 20-29%         | 2468     | 121    | 224    | 2123   | 35.1%     | 19.4      |
| 30-39%         | 3954     | 190    | 390    | 3374   | 32.8%     | 23.0      |
| 40-49%         | 6003     | 299    | 434    | 5270   | 40.8%     | 19.7      |
| 50-59%         | 5959     | 415    | 627    | 4917   | 39.8%     | 28.2      |
| 60-69%         | 6341     | 505    | 896    | 4940   | 36.0%     | 18.2      |
| 70-79%         | 4407     | 370    | 755    | 3282   | 32.9%     | 20.5      |
| 80-89%         | 3316     | 308    | 757    | 2251   | 28.9%     | 12.0      |
| 90-99%         | 2424     | 104    | 489    | 1831   | 17.5%     | 20.9      |
| 100%           | 415      | 0      | 12     | 403    | 0.0%      | 0.0       |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| Pre-market             | 7947     | 617    | 1110   | 6220   | 35.7%     | 24.7     |
| ORB (9:30-10:00)       | 1236     | 264    | 485    | 487    | 35.2%     | 11.1     |
| Morning (10:00-12:00)  | 4695     | 651    | 1203   | 2841   | 35.1%     | 14.5     |
| Afternoon (12:00-16:00) | 9196     | 551    | 1100   | 7545   | 33.4%     | 24.3     |
| After-hours (16:00-20:00) | 7770     | 235    | 715    | 6820   | 24.7%     | 34.9     |
| Overnight              | 4558     | 0      | 0      | 4558   | 0.0%      | 0.0      |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| Pre-market             | 10-19%       | 82       | 1      | 26     | 55     | 3.7%      |
| Pre-market             | 20-29%       | 591      | 51     | 71     | 469    | 41.8%     |
| Pre-market             | 30-39%       | 971      | 50     | 100    | 821    | 33.3%     |
| Pre-market             | 40-49%       | 1135     | 54     | 87     | 994    | 38.3%     |
| Pre-market             | 50-59%       | 1266     | 169    | 189    | 908    | 47.2%     |
| Pre-market             | 60-69%       | 1496     | 84     | 219    | 1193   | 27.7%     |
| Pre-market             | 70-79%       | 1001     | 121    | 144    | 736    | 45.7%     |
| Pre-market             | 80-89%       | 569      | 72     | 188    | 309    | 27.7%     |
| Pre-market             | 90-99%       | 681      | 15     | 83     | 583    | 15.3%     |
| Pre-market             | 100%         | 155      | 0      | 3      | 152    | 0.0%      |
| ORB (9:30-10:00)       | 20-29%       | 63       | 12     | 27     | 24     | 30.8%     |
| ORB (9:30-10:00)       | 30-39%       | 124      | 24     | 43     | 57     | 35.8%     |
| ORB (9:30-10:00)       | 40-49%       | 155      | 33     | 61     | 61     | 35.1%     |
| ORB (9:30-10:00)       | 50-59%       | 227      | 40     | 75     | 112    | 34.8%     |
| ORB (9:30-10:00)       | 60-69%       | 273      | 80     | 101    | 92     | 44.2%     |
| ORB (9:30-10:00)       | 70-79%       | 180      | 40     | 79     | 61     | 33.6%     |
| ORB (9:30-10:00)       | 80-89%       | 181      | 32     | 94     | 55     | 25.4%     |
| ORB (9:30-10:00)       | 100%         | 24       | 0      | 2      | 22     | 0.0%      |
| Morning (10:00-12:00)  | 10-19%       | 11       | 4      | 0      | 7      | 100.0%    |
| Morning (10:00-12:00)  | 20-29%       | 247      | 53     | 98     | 96     | 35.1%     |
| Morning (10:00-12:00)  | 30-39%       | 434      | 69     | 121    | 244    | 36.3%     |
| Morning (10:00-12:00)  | 40-49%       | 730      | 92     | 142    | 496    | 39.3%     |
| Morning (10:00-12:00)  | 50-59%       | 1014     | 102    | 207    | 705    | 33.0%     |
| Morning (10:00-12:00)  | 60-69%       | 892      | 144    | 237    | 511    | 37.8%     |
| Morning (10:00-12:00)  | 70-79%       | 628      | 99     | 215    | 314    | 31.5%     |
| Morning (10:00-12:00)  | 80-89%       | 651      | 78     | 162    | 411    | 32.5%     |
| Morning (10:00-12:00)  | 90-99%       | 48       | 10     | 21     | 17     | 32.3%     |
| Morning (10:00-12:00)  | 100%         | 40       | 0      | 0      | 40     | 0.0%      |
| Afternoon (12:00-16:00) | 10-19%       | 20       | 1      | 3      | 16     | 25.0%     |
| Afternoon (12:00-16:00) | 20-29%       | 488      | 3      | 18     | 467    | 14.3%     |
| Afternoon (12:00-16:00) | 30-39%       | 871      | 28     | 36     | 807    | 43.8%     |
| Afternoon (12:00-16:00) | 40-49%       | 1531     | 80     | 87     | 1364   | 47.9%     |
| Afternoon (12:00-16:00) | 50-59%       | 1789     | 86     | 114    | 1589   | 43.0%     |
| Afternoon (12:00-16:00) | 60-69%       | 1719     | 160    | 277    | 1282   | 36.6%     |
| Afternoon (12:00-16:00) | 70-79%       | 1246     | 89     | 232    | 925    | 27.7%     |
| Afternoon (12:00-16:00) | 80-89%       | 1185     | 79     | 234    | 872    | 25.2%     |
| Afternoon (12:00-16:00) | 90-99%       | 151      | 25     | 92     | 34     | 21.4%     |
| Afternoon (12:00-16:00) | 100%         | 196      | 0      | 7      | 189    | 0.0%      |
| After-hours (16:00-20:00) | 20-29%       | 605      | 2      | 10     | 593    | 16.7%     |
| After-hours (16:00-20:00) | 30-39%       | 880      | 19     | 90     | 771    | 17.4%     |
| After-hours (16:00-20:00) | 40-49%       | 1504     | 40     | 57     | 1407   | 41.2%     |
| After-hours (16:00-20:00) | 50-59%       | 1189     | 18     | 42     | 1129   | 30.0%     |
| After-hours (16:00-20:00) | 60-69%       | 1397     | 37     | 62     | 1298   | 37.4%     |
| After-hours (16:00-20:00) | 70-79%       | 878      | 21     | 85     | 772    | 19.8%     |
| After-hours (16:00-20:00) | 80-89%       | 729      | 47     | 79     | 603    | 37.3%     |
| After-hours (16:00-20:00) | 90-99%       | 588      | 51     | 290    | 247    | 15.0%     |
| Overnight              | 20-29%       | 474      | 0      | 0      | 474    | 0.0%      |
| Overnight              | 30-39%       | 674      | 0      | 0      | 674    | 0.0%      |
| Overnight              | 40-49%       | 948      | 0      | 0      | 948    | 0.0%      |
| Overnight              | 50-59%       | 474      | 0      | 0      | 474    | 0.0%      |
| Overnight              | 60-69%       | 564      | 0      | 0      | 564    | 0.0%      |
| Overnight              | 70-79%       | 474      | 0      | 0      | 474    | 0.0%      |
| Overnight              | 90-99%       | 949      | 0      | 0      | 949    | 0.0%      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] exchange_flow_concentration | 10-19%       | 62.5%     | 17.1%     | 265%     | 1.09     | 33       | 5        | 3        |
| [ALPHA] magnet_accelerate | 90-99%       | 50.0%     | 17.5%     | 185%     | 1.55     | 5        | 1        | 1        |
| [ALPHA] gex_divergence   | 50-59%       | 85.3%     | 39.8%     | 114%     | 1.61     | 66       | 29       | 5        |
| [ALPHA] gamma_flip_breakout | 30-39%       | 69.8%     | 32.8%     | 113%     | 1.61     | 333      | 44       | 19       |
| [ALPHA] vol_compression_range | 50-59%       | 77.8%     | 39.8%     | 95%      | 1.34     | 296      | 42       | 12       |
| [ALPHA] gamma_squeeze    | 50-59%       | 75.0%     | 39.8%     | 88%      | 1.25     | 148      | 3        | 1        |
| [ALPHA] gamma_flip_breakout | 40-49%       | 75.0%     | 40.8%     | 84%      | 1.74     | 465      | 120      | 40       |
| [ALPHA] gamma_flip_breakout | 50-59%       | 70.0%     | 39.8%     | 76%      | 1.07     | 567      | 201      | 86       |
| [ALPHA] exchange_flow_concentration | 30-39%       | 53.9%     | 32.8%     | 65%      | 0.92     | 271      | 41       | 35       |
| [ALPHA] strike_concentration | 40-49%       | 66.7%     | 40.8%     | 63%      | 1.31     | 59       | 2        | 1        |
| [ALPHA] gex_divergence   | 60-69%       | 57.4%     | 36.0%     | 59%      | 1.18     | 753      | 171      | 127      |
| [ALPHA] depth_imbalance_momentum | 30-39%       | 50.0%     | 32.8%     | 53%      | 0.75     | 39       | 2        | 2        |
| [ALPHA] vol_compression_range | 60-69%       | 55.0%     | 36.0%     | 53%      | 1.04     | 206      | 11       | 9        |
| [ALPHA] strike_concentration | 70-79%       | 50.0%     | 32.9%     | 52%      | 0.84     | 73       | 2        | 2        |

**14 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 20-29%       | 7       | 2      | 0      | 100.0%   | 14.3%    | 600%   | 1.98    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 30-39%       | 59      | 10     | 0      | 100.0%   | 17.4%    | 474%   | 2.30    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | Pre-market   | 60-69%       | 7       | 5      | 0      | 100.0%   | 27.7%    | 261%   | 2.37    | ⚡ HIGH       |
| [ALPHA] strike_concentration | After-hours (16:00-20:00) | 50-59%       | 96      | 1      | 0      | 100.0%   | 30.0%    | 233%   | 1.58    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 50-59%       | 95      | 6      | 0      | 100.0%   | 30.0%    | 233%   | 1.58    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 50-59%       | 137     | 6      | 0      | 100.0%   | 30.0%    | 233%   | 1.58    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | Morning (10:00-12:00) | 50-59%       | 27      | 2      | 0      | 100.0%   | 33.0%    | 203%   | 2.02    | ⚡ HIGH       |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 50-59%       | 263     | 1      | 0      | 100.0%   | 33.0%    | 203%   | 2.02    | ⚡ HIGH       |
| [ALPHA] strike_concentration | ORB (9:30-10:00) | 50-59%       | 10      | 2      | 0      | 100.0%   | 34.8%    | 188%   | 2.09    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 70-79%       | 43      | 10     | 8      | 55.6%    | 19.8%    | 180%   | 1.76    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 30-39%       | 5       | 2      | 0      | 100.0%   | 36.3%    | 175%   | 2.31    | ⚡ HIGH       |
| [ALPHA] strike_concentration | After-hours (16:00-20:00) | 60-69%       | 94      | 8      | 0      | 100.0%   | 37.4%    | 168%   | 1.46    | 🔥 STRONG     |
| [ALPHA] confluence_reversal | After-hours (16:00-20:00) | 60-69%       | 147     | 2      | 0      | 100.0%   | 37.4%    | 168%   | 1.46    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 60-69%       | 44      | 1      | 0      | 100.0%   | 37.4%    | 168%   | 1.46    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | After-hours (16:00-20:00) | 30-39%       | 58      | 5      | 6      | 45.5%    | 17.4%    | 161%   | 0.78    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 40-49%       | 142     | 27     | 0      | 100.0%   | 41.2%    | 143%   | 1.33    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | After-hours (16:00-20:00) | 40-49%       | 67      | 1      | 0      | 100.0%   | 41.2%    | 143%   | 1.33    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Pre-market   | 20-29%       | 12      | 12     | 0      | 100.0%   | 41.8%    | 139%   | 1.33    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 50-59%       | 142     | 53     | 0      | 100.0%   | 43.0%    | 133%   | 1.46    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 30-39%       | 123     | 4      | 0      | 100.0%   | 43.8%    | 129%   | 1.40    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | ORB (9:30-10:00) | 60-69%       | 6       | 2      | 0      | 100.0%   | 44.2%    | 126%   | 1.92    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 50-59%       | 75      | 18     | 1      | 94.7%    | 43.0%    | 120%   | 1.33    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 40-49%       | 25      | 2      | 0      | 100.0%   | 47.9%    | 109%   | 1.26    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 40-49%       | 125     | 45     | 0      | 100.0%   | 47.9%    | 109%   | 1.26    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | Pre-market   | 50-59%       | 38      | 26     | 1      | 96.3%    | 47.2%    | 104%   | 1.36    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 40-49%       | 151     | 9      | 2      | 81.8%    | 41.2%    | 98%    | 0.92    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 30-39%       | 82      | 17     | 9      | 65.4%    | 33.3%    | 96%    | 1.33    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 70-79%       | 16      | 7      | 4      | 63.6%    | 33.6%    | 89%    | 1.52    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | ORB (9:30-10:00) | 80-89%       | 40      | 14     | 16     | 46.7%    | 25.4%    | 84%    | 1.22    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 30-39%       | 50      | 8      | 4      | 66.7%    | 36.3%    | 84%    | 1.10    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Pre-market   | 60-69%       | 46      | 1      | 1      | 50.0%    | 27.7%    | 80%    | 0.73    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Pre-market   | 60-69%       | 19      | 7      | 7      | 50.0%    | 27.7%    | 80%    | 0.73    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | Pre-market   | 70-79%       | 371     | 63     | 14     | 81.8%    | 45.7%    | 79%    | 1.18    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 70-79%       | 122     | 38     | 39     | 49.4%    | 27.7%    | 78%    | 1.08    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 30-39%       | 11      | 7      | 4      | 63.6%    | 35.8%    | 78%    | 1.46    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Pre-market   | 50-59%       | 20      | 14     | 3      | 82.4%    | 47.2%    | 74%    | 0.97    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 30-39%       | 69      | 17     | 10     | 63.0%    | 36.3%    | 73%    | 0.97    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | ORB (9:30-10:00) | 50-59%       | 15      | 6      | 4      | 60.0%    | 34.8%    | 73%    | 0.81    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | After-hours (16:00-20:00) | 30-39%       | 40      | 3      | 7      | 30.0%    | 17.4%    | 72%    | 0.35    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Morning (10:00-12:00) | 70-79%       | 33      | 15     | 13     | 53.6%    | 31.5%    | 70%    | 1.07    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | Morning (10:00-12:00) | 40-49%       | 13      | 2      | 1      | 66.7%    | 39.3%    | 70%    | 1.17    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 50-59%       | 134     | 48     | 39     | 55.2%    | 33.0%    | 67%    | 0.67    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 60-69%       | 449     | 96     | 61     | 61.1%    | 36.6%    | 67%    | 1.01    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 60-69%       | 124     | 3      | 2      | 60.0%    | 36.6%    | 64%    | 0.96    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Pre-market   | 30-39%       | 33      | 6      | 5      | 54.5%    | 33.3%    | 64%    | 0.88    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | Pre-market   | 40-49%       | 28      | 13     | 8      | 61.9%    | 38.3%    | 62%    | 0.80    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 70-79%       | 22      | 4      | 5      | 44.4%    | 27.7%    | 60%    | 0.84    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 50-59%       | 155     | 86     | 28     | 75.4%    | 47.2%    | 60%    | 0.78    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 40-49%       | 81      | 20     | 12     | 62.5%    | 39.3%    | 59%    | 0.99    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_asymmetry | Morning (10:00-12:00) | 70-79%       | 6       | 1      | 1      | 50.0%    | 31.5%    | 59%    | 0.90    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 30-39%       | 35      | 8      | 4      | 66.7%    | 43.8%    | 52%    | 0.57    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 50-59%       | 74      | 20     | 20     | 50.0%    | 33.0%    | 51%    | 0.51    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 50-59%       | 58      | 4      | 4      | 50.0%    | 33.0%    | 51%    | 0.51    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Pre-market   | 40-49%       | 62      | 11     | 8      | 57.9%    | 38.3%    | 51%    | 0.67    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 60-69%       | 60      | 15     | 21     | 41.7%    | 27.7%    | 50%    | 0.46    | ⚠ MODERATE   |

**55 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | gex_divergence           | 1,157   | 55.1%    | $0.4     | 50-59%         | Pre-market       | Pre-market @ 50-59%    | Sideways       | Time Held: 30-90m |
| 2     | exchange_flow_asymmetry  | 1,365   | 24.7%    | $0.1     | 70-79%         | Morning (10:00-12:00) | Pre-market @ 70-79%    | UNKNOWN        | Time Held: 30-90m |
| 3     | exchange_flow_concentration | 2,551   | 41.5%    | $0.1     | 10-19%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 10-19% | UNKNOWN        | Time Held: <30m |
| 4     | vol_compression_range    | 1,409   | 45.5%    | $0.0     | 50-59%         | Pre-market       | Pre-market @ 60-69%    | Sideways       | Time Held: 30-90m |
| 5     | gamma_flip_breakout      | 5,128   | 40.6%    | $0.0     | 40-49%         | Pre-market       | Afternoon (12:00-16:00) @ 50-59% | Trending (Up)  | Time Held: <30m |
| 6     | delta_gamma_squeeze      | 134     | 3.7%     | $0.0     | 10-19%         | Pre-market       | Pre-market @ 10-19%    | Sideways       | Time Held: <30m |
| 7     | strike_concentration     | 1,203   | 50.0%    | $0.0     | 40-49%         | After-hours (16:00-20:00) | ORB (9:30-10:00) @ 50-59% | Trending (Up)  | Time Held: <30m |
| 8     | depth_decay_momentum     | 2,425   | 31.9%    | $-0.0    | 50-59%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 60-69% | UNKNOWN        | Time Held: <30m |
| 9     | gamma_wall_bounce        | 1,794   | 27.8%    | $-0.0    | 40-49%         | After-hours (16:00-20:00) | After-hours (16:00-20:00) @ 40-49% | Trending (Up)  | Time Held: <30m |
| 10    | confluence_reversal      | 10,910  | 25.9%    | $-0.0    | 60-69%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 50-59% | Sideways       | Time Held: 30-90m |
| 11    | magnet_accelerate        | 2,769   | 22.8%    | $-0.0    | 90-99%         | ORB (9:30-10:00) | Pre-market @ 70-79%    | Sideways       | Time Held: 30-90m |
| 12    | gamma_squeeze            | 586     | 21.1%    | $-0.0    | 50-59%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 60-69% | Trending (Up)  | Time Held: <30m |
| 13    | exchange_flow_imbalance  | 2,160   | 22.1%    | $-0.1    | 60-69%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 40-49% | UNKNOWN        | Time Held: <30m |
| 14    | depth_imbalance_momentum | 1,811   | 9.0%     | $-0.2    | 30-39%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 30-39% | UNKNOWN        | Time Held: <30m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*