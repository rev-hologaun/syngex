# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 19,312  |  **Strategies Analyzed:** 11

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 19,312                                                       |
| Total Wins           | 3,508                                                        |
| Total Losses         | 5,346                                                        |
| Time-Expired (CLOSED) | 10,458                                                       |
| Overall Win Rate     | 39.6%                                                        |
| Total P&L            | $65.74                                                       |
| Avg P&L per Signal   | $0.00                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,356  |  **Win Rate:** 29.6%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1290s (21.5m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 4     | 0     | 0      | 4      | 0.0%      | $1.1     | 48.5%    |
| 50-59%         | 276   | 56    | 124    | 96     | 31.1%     | $-0.2    | -9.4%    |
| 60-69%         | 296   | 56    | 108    | 132    | 34.1%     | $-0.0    | -4.1%    |
| 70-79%         | 1186  | 140   | 352    | 694    | 28.5%     | $-0.0    | -5.2%    |
| 80-89%         | 558   | 78    | 188    | 292    | 29.3%     | $-0.1    | -7.8%    |
| 90-99%         | 36    | 2     | 18     | 16     | 10.0%     | $-0.8    | -36.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2356  | 332   | 790    | 1234   | 29.6%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 422   | 102   | 254    | 66     | 28.7%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 1934  | 230   | 536    | 1168   | 30.0%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1234  | 0     | 0      | 1234   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 1122  | 332   | 790    | 0      | 29.6%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1182  | 232   | 470    | 480    | 33.0%     | $-0.1    |
| SHORT        | 1174  | 100   | 320    | 754    | 23.8%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 256   | 84    | 172    | 0      | 32.8%     | $-0.3    |
| Long (30-60 min)       | 1234  | 0     | 0      | 1234   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 388   | 114   | 274    | 0      | 29.4%     | $-0.4    |
| Slow (15-30 min)       | 426   | 118   | 308    | 0      | 27.7%     | $-0.3    |
| Very Fast (<1 min)     | 52    | 16    | 36     | 0      | 30.8%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.07 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (34.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.07) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.17) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1290s / 21.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 52% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 986  |  **Win Rate:** 8.2%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 2851s (47.5m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 60-69%         | 2     | 0     | 0      | 2      | 0.0%      | $2.0     | 57.3%    |
| 70-79%         | 106   | 2     | 46     | 58     | 4.2%      | $-0.3    | -24.2%   |
| 80-89%         | 878   | 24    | 246    | 608    | 8.9%      | $0.2     | -0.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 986   | 26    | 292    | 668    | 8.2%      | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 986   | 26    | 292    | 668    | 8.2%      | $0.1     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 758   | 10    | 80     | 668    | 11.1%     | $0.7     |
| ORB / Early (0-30 min) | 228   | 16    | 212    | 0      | 7.0%      | $-1.7    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 486   | 26    | 180    | 280    | 12.6%     | $-0.1    |
| SHORT        | 500   | 0     | 112    | 388    | 0.0%      | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 50    | 4     | 46     | 0      | 8.0%      | $-2.2    |
| Long (30-60 min)       | 90    | 10    | 80     | 0      | 11.1%     | $-1.0    |
| Medium (5-15 min)      | 82    | 12    | 70     | 0      | 14.6%     | $-0.8    |
| Slow (15-30 min)       | 84    | 0     | 84     | 0      | 0.0%      | $-2.1    |
| Very Fast (<1 min)     | 12    | 0     | 12     | 0      | 0.0%      | $-2.1    |
| Very Long (>1h)        | 668   | 0     | 0      | 668    | 0.0%      | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 8.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.13 per signal — profitable even with 8.2% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (8.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (4.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.13) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.67) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2851s / 47.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 68% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,236  |  **Win Rate:** 36.0%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1288s (21.5m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 22    | 2     | 8      | 12     | 20.0%     | $-0.5    | -35.8%   |
| 30-39%         | 190   | 34    | 82     | 74     | 29.3%     | $-0.2    | -12.5%   |
| 40-49%         | 360   | 76    | 134    | 150    | 36.2%     | $0.0     | 1.6%     |
| 50-59%         | 344   | 78    | 124    | 142    | 38.6%     | $-0.1    | -1.4%    |
| 60-69%         | 1320  | 194   | 334    | 792    | 36.7%     | $0.1     | 0.1%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2236  | 384   | 682    | 1170   | 36.0%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 566   | 138   | 328    | 100    | 29.6%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 1670  | 246   | 354    | 1070   | 41.0%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1170  | 0     | 0      | 1170   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1066  | 384   | 682    | 0      | 36.0%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1792  | 306   | 582    | 904    | 34.5%     | $-0.1    |
| SHORT        | 444   | 78    | 100    | 266    | 43.8%     | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 240   | 72    | 168    | 0      | 30.0%     | $-0.3    |
| Long (30-60 min)       | 1170  | 0     | 0      | 1170   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 372   | 144   | 228    | 0      | 38.7%     | $0.0     |
| Slow (15-30 min)       | 402   | 164   | 238    | 0      | 40.8%     | $0.1     |
| Very Fast (<1 min)     | 52    | 4     | 48     | 0      | 7.7%      | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.00 per signal — profitable even with 36.0% win rate (good risk/reward).
- 🎯 Best performance at 50-59% confidence (38.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (20.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.00) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.07) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1288s / 21.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 52% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,390  |  **Win Rate:** 24.0%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1897s (31.6m)  |  **Median Hold:** 2700s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 2     | 0     | 0      | 2      | 0.0%      | $1.1     | 70.5%    |
| 30-39%         | 14    | 0     | 0      | 14     | 0.0%      | $-0.1    | -2.0%    |
| 40-49%         | 34    | 4     | 12     | 18     | 25.0%     | $-0.3    | -12.6%   |
| 50-59%         | 316   | 26    | 110    | 180    | 19.1%     | $0.0     | -4.5%    |
| 60-69%         | 330   | 46    | 132    | 152    | 25.8%     | $0.1     | 1.2%     |
| 70-79%         | 1000  | 110   | 388    | 502    | 22.1%     | $0.1     | -1.1%    |
| 80-89%         | 694   | 96    | 252    | 346    | 27.6%     | $0.1     | 3.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2390  | 282   | 894    | 1214   | 24.0%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 454   | 64    | 344    | 46     | 15.7%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 1936  | 218   | 550    | 1168   | 28.4%     | $0.2     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1468  | 86    | 168    | 1214   | 33.9%     | $0.4     |
| ORB / Early (0-30 min) | 922   | 196   | 726    | 0      | 21.3%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1420  | 178   | 646    | 596    | 21.6%     | $-0.1    |
| SHORT        | 970   | 104   | 248    | 618    | 29.5%     | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 212   | 36    | 176    | 0      | 17.0%     | $-0.7    |
| Long (30-60 min)       | 1468  | 86    | 168    | 1214   | 33.9%     | $0.4     |
| Medium (5-15 min)      | 290   | 56    | 234    | 0      | 19.3%     | $-0.4    |
| Slow (15-30 min)       | 372   | 98    | 274    | 0      | 26.3%     | $-0.1    |
| Very Fast (<1 min)     | 48    | 6     | 42     | 0      | 12.5%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.09 per signal — profitable even with 24.0% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (27.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.09) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.38) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1897s / 31.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 51% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,390  |  **Win Rate:** 74.2%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1698s (28.3m)  |  **Median Hold:** 1178s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 24    | 14    | 0      | 10     | 100.0%    | $0.5     | 14.1%    |
| 30-39%         | 196   | 76    | 12     | 108    | 86.4%     | $0.2     | 7.7%     |
| 40-49%         | 456   | 110   | 24     | 322    | 82.1%     | $-0.0    | 0.7%     |
| 50-59%         | 448   | 378   | 14     | 56     | 96.4%     | $0.1     | 3.8%     |
| 60-69%         | 406   | 254   | 64     | 88     | 79.9%     | $0.1     | 3.8%     |
| 70-79%         | 128   | 68    | 50     | 10     | 57.6%     | $-0.1    | -8.4%    |
| 80-89%         | 378   | 166   | 154    | 58     | 51.9%     | $0.1     | 6.7%     |
| 90-99%         | 246   | 112   | 130    | 4      | 46.3%     | $0.0     | 10.6%    |
| 100%           | 108   | 108   | 0      | 0      | 100.0%    | $0.5     | 10.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1514  | 700   | 316    | 498    | 68.9%     | $0.0     |
| Trending (Up)        | 876   | 586   | 132    | 158    | 81.6%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 108   | 108   | 0      | 0      | 100.0%    | $0.5     |
| Positive Gamma (Range-Bound friendly) | 2282  | 1178  | 448    | 656    | 72.4%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1016  | 218   | 142    | 656    | 60.6%     | $-0.2    |
| ORB / Early (0-30 min) | 1374  | 1068  | 306    | 0      | 77.7%     | $0.3     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1230  | 610   | 158    | 462    | 79.4%     | $0.1     |
| SHORT        | 1160  | 676   | 290    | 194    | 70.0%     | $0.1     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 364   | 294   | 70     | 0      | 80.8%     | $0.4     |
| Long (30-60 min)       | 360   | 218   | 142    | 0      | 60.6%     | $0.2     |
| Medium (5-15 min)      | 460   | 342   | 118    | 0      | 74.3%     | $0.3     |
| Slow (15-30 min)       | 308   | 200   | 108    | 0      | 64.9%     | $0.1     |
| Very Fast (<1 min)     | 242   | 232   | 10     | 0      | 95.9%     | $0.2     |
| Very Long (>1h)        | 656   | 0     | 0      | 656    | 0.0%      | $-0.4    |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 74.2% — this strategy consistently picks directional moves.
- 💰 Positive avg P&L of $0.07 per signal — profitable even with 74.2% win rate (good risk/reward).
- 🎯 Best performance at 100% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (46.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.10) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.29) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1698s / 28.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 1,060  |  **Win Rate:** 32.5%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 1636s (27.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 72    | 0     | 12     | 60     | 0.0%      | $-0.1    | -16.7%   |
| 40-49%         | 136   | 12    | 10     | 114    | 54.5%     | $0.0     | 10.2%    |
| 50-59%         | 196   | 8     | 18     | 170    | 30.8%     | $-0.2    | -9.5%    |
| 60-69%         | 642   | 30    | 62     | 550    | 32.6%     | $0.0     | 2.1%     |
| 70-79%         | 12    | 0     | 6      | 6      | 0.0%      | $-0.6    | -57.1%   |
| 80-89%         | 2     | 2     | 0      | 0      | 100.0%    | $0.8     | 200.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 730   | 28    | 68     | 634    | 29.2%     | $-0.0    |
| Trending (Up)        | 330   | 24    | 40     | 266    | 37.5%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1060  | 52    | 108    | 900    | 32.5%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 900   | 0     | 0      | 900    | 0.0%      | $0.0     |
| ORB / Early (0-30 min) | 160   | 52    | 108    | 0      | 32.5%     | $-0.2    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1060  | 52    | 108    | 900    | 32.5%     | $-0.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 44    | 2     | 42     | 0      | 4.5%      | $-1.5    |
| Long (30-60 min)       | 900   | 0     | 0      | 900    | 0.0%      | $0.0     |
| Medium (5-15 min)      | 40    | 18    | 22     | 0      | 45.0%     | $0.5     |
| Slow (15-30 min)       | 60    | 26    | 34     | 0      | 43.3%     | $0.4     |
| Very Fast (<1 min)     | 16    | 6     | 10     | 0      | 37.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 32.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.02 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (54.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.00) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.00) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1636s / 27.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 85% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,584  |  **Win Rate:** 26.9%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1520s (25.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 2      | 0      | 0.0%      | $-3.8    | -100.0%  |
| 20-29%         | 40    | 8     | 10     | 22     | 44.4%     | $1.1     | 34.2%    |
| 30-39%         | 84    | 10    | 26     | 48     | 27.8%     | $0.4     | 2.9%     |
| 40-49%         | 158   | 30    | 80     | 48     | 27.3%     | $0.2     | -18.5%   |
| 50-59%         | 182   | 26    | 90     | 66     | 22.4%     | $-0.3    | -21.6%   |
| 60-69%         | 166   | 22    | 104    | 40     | 17.5%     | $-0.3    | -35.6%   |
| 70-79%         | 674   | 22    | 154    | 498    | 12.5%     | $-0.2    | -12.8%   |
| 80-89%         | 522   | 30    | 60     | 432    | 33.3%     | $0.0     | 0.0%     |
| 90-99%         | 142   | 6     | 46     | 90     | 11.5%     | $-0.4    | -23.2%   |
| 100%           | 1614  | 110   | 144    | 1360   | 43.3%     | $-0.0    | -0.8%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2576  | 170   | 466    | 1940   | 26.7%     | $-0.1    |
| Trending (Up)        | 1008  | 94    | 250    | 664    | 27.3%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 468   | 42    | 316    | 110    | 11.7%     | $-0.4    |
| Positive Gamma (Range-Bound friendly) | 3116  | 222   | 400    | 2494   | 35.7%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2604  | 0     | 0      | 2604   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 980   | 264   | 716    | 0      | 26.9%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2580  | 202   | 462    | 1916   | 30.4%     | $-0.1    |
| SHORT        | 1004  | 62    | 254    | 688    | 19.6%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 210   | 46    | 164    | 0      | 21.9%     | $-0.7    |
| Long (30-60 min)       | 2604  | 0     | 0      | 2604   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 354   | 96    | 258    | 0      | 27.1%     | $-0.5    |
| Slow (15-30 min)       | 382   | 116   | 266    | 0      | 30.4%     | $-0.1    |
| Very Fast (<1 min)     | 34    | 6     | 28     | 0      | 17.6%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 26.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.06 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (44.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (11.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.03) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.08) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1520s / 25.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 73% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 686  |  **Win Rate:** 42.6%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 2290s (38.2m)  |  **Median Hold:** 2447s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 124   | 22    | 26     | 76     | 45.8%     | $0.3     | 8.1%     |
| 50-59%         | 144   | 2     | 78     | 64     | 2.5%      | $-0.9    | -45.3%   |
| 60-69%         | 374   | 138   | 118    | 118    | 53.9%     | $0.1     | 26.9%    |
| 70-79%         | 36    | 16    | 10     | 10     | 61.5%     | $0.5     | 35.7%    |
| 80-89%         | 8     | 0     | 8      | 0      | 0.0%      | $-2.2    | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 634   | 170   | 210    | 254    | 44.7%     | $0.0     |
| Trending (Up)        | 52    | 8     | 30     | 14     | 21.1%     | $-0.8    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 686   | 178   | 240    | 268    | 42.6%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 406   | 46    | 92     | 268    | 33.3%     | $-0.1    |
| ORB / Early (0-30 min) | 280   | 132   | 148    | 0      | 47.1%     | $0.0     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 686   | 178   | 240    | 268    | 42.6%     | $-0.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 56    | 24    | 32     | 0      | 42.9%     | $-0.3    |
| Long (30-60 min)       | 138   | 46    | 92     | 0      | 33.3%     | $-0.6    |
| Medium (5-15 min)      | 80    | 58    | 22     | 0      | 72.5%     | $1.3     |
| Slow (15-30 min)       | 138   | 44    | 94     | 0      | 31.9%     | $-0.6    |
| Very Fast (<1 min)     | 6     | 6     | 0      | 0      | 100.0%    | $2.3     |
| Very Long (>1h)        | 268   | 0     | 0      | 268    | 0.0%      | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 42.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.05 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (61.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.01) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.04) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (2290s / 38.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 39% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, NVDA, TSLA  |  **Total Signals:** 2,214  |  **Win Rate:** 36.5%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 2338s (39.0m)  |  **Median Hold:** 2660s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 340   | 0     | 120    | 220    | 0.0%      | $-0.2    | -35.3%   |
| 40-49%         | 700   | 0     | 250    | 450    | 0.0%      | $-0.3    | -35.7%   |
| 50-59%         | 58    | 0     | 46     | 12     | 0.0%      | $-1.0    | -65.4%   |
| 60-69%         | 316   | 88    | 158    | 70     | 35.8%     | $-0.0    | 27.2%    |
| 70-79%         | 532   | 264   | 158    | 110    | 62.6%     | $0.4     | 61.9%    |
| 80-89%         | 266   | 122   | 90     | 54     | 57.5%     | $0.3     | 49.5%    |
| 90-99%         | 2     | 0     | 2      | 0      | 0.0%      | $-0.4    | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1778  | 314   | 646    | 818    | 32.7%     | $-0.0    |
| Trending (Up)        | 436   | 160   | 178    | 98     | 47.3%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2214  | 474   | 824    | 916    | 36.5%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1358  | 184   | 258    | 916    | 41.6%     | $0.2     |
| ORB / Early (0-30 min) | 856   | 290   | 566    | 0      | 33.9%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1522  | 292   | 548    | 682    | 34.8%     | $-0.0    |
| SHORT        | 692   | 182   | 276    | 234    | 39.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 138   | 32    | 106    | 0      | 23.2%     | $-0.5    |
| Long (30-60 min)       | 442   | 184   | 258    | 0      | 41.6%     | $0.2     |
| Medium (5-15 min)      | 290   | 90    | 200    | 0      | 31.0%     | $-0.4    |
| Slow (15-30 min)       | 396   | 164   | 232    | 0      | 41.4%     | $-0.1    |
| Very Fast (<1 min)     | 32    | 4     | 28     | 0      | 12.5%     | $-0.5    |
| Very Long (>1h)        | 916   | 0     | 0      | 916    | 0.0%      | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.00 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (62.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.16) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.19) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2338s / 39.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 41% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, TSLA  |  **Total Signals:** 590  |  **Win Rate:** 15.4%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 870s (14.5m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 8     | 2     | 0      | 6      | 100.0%    | $2.1     | 63.3%    |
| 40-49%         | 8     | 0     | 2      | 6      | 0.0%      | $0.3     | -0.6%    |
| 50-59%         | 34    | 0     | 4      | 30     | 0.0%      | $-0.3    | -14.6%   |
| 60-69%         | 166   | 0     | 6      | 160    | 0.0%      | $-0.1    | -5.4%    |
| 70-79%         | 330   | 2     | 10     | 318    | 16.7%     | $-0.1    | -5.7%    |
| 80-89%         | 44    | 0     | 0      | 44     | 0.0%      | $0.2     | 9.8%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 392   | 0     | 16     | 376    | 0.0%      | $-0.0    |
| Trending (Up)        | 198   | 4     | 6      | 188    | 40.0%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 590   | 4     | 22     | 564    | 15.4%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| ORB / Early (0-30 min) | 590   | 4     | 22     | 564    | 15.4%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 232   | 0     | 10     | 222    | 0.0%      | $-0.3    |
| SHORT        | 358   | 4     | 12     | 342    | 25.0%     | $0.1     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 16    | 4     | 12     | 0      | 25.0%     | $-0.8    |
| Medium (5-15 min)      | 6     | 0     | 6      | 0      | 0.0%      | $-1.7    |
| Slow (15-30 min)       | 564   | 0     | 0      | 564    | 0.0%      | $-0.0    |
| Very Fast (<1 min)     | 4     | 0     | 4      | 0      | 0.0%      | $-1.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.06 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.04) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.06) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (870s / 14.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 96% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 820  |  **Win Rate:** 40.6%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 4413s (73.5m)  |  **Median Hold:** 4613s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 10    | 10    | 0      | 0      | 100.0%    | $5.1     | 149.9%   |
| 20-29%         | 44    | 18    | 12     | 14     | 60.0%     | $1.6     | 60.2%    |
| 30-39%         | 152   | 20    | 86     | 46     | 18.9%     | $-0.6    | -25.9%   |
| 40-49%         | 216   | 48    | 64     | 104    | 42.9%     | $-0.0    | 6.4%     |
| 50-59%         | 284   | 94    | 100    | 90     | 48.5%     | $0.1     | 4.4%     |
| 60-69%         | 102   | 32    | 60     | 10     | 34.8%     | $-0.0    | -9.8%    |
| 70-79%         | 12    | 4     | 8      | 0      | 33.3%     | $-0.4    | -17.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 560   | 180   | 186    | 194    | 49.2%     | $0.3     |
| Trending (Up)        | 260   | 46    | 144    | 70     | 24.2%     | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 820   | 226   | 330    | 264    | 40.6%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 304   | 126   | 178    | 0      | 41.4%     | $-0.0    |
| Mid-day (90-240 min)   | 342   | 44    | 34     | 264    | 56.4%     | $0.4     |
| ORB / Early (0-30 min) | 174   | 56    | 118    | 0      | 32.2%     | $-0.6    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 470   | 162   | 96     | 212    | 62.8%     | $0.7     |
| SHORT        | 350   | 64    | 234    | 52     | 21.5%     | $-0.8    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 30    | 10    | 20     | 0      | 33.3%     | $-0.5    |
| Long (30-60 min)       | 154   | 74    | 80     | 0      | 48.1%     | $0.2     |
| Medium (5-15 min)      | 80    | 30    | 50     | 0      | 37.5%     | $-0.4    |
| Slow (15-30 min)       | 62    | 16    | 46     | 0      | 25.8%     | $-0.8    |
| Very Fast (<1 min)     | 2     | 0     | 2      | 0      | 0.0%      | $-1.8    |
| Very Long (>1h)        | 492   | 96    | 132    | 264    | 42.1%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 40.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.04 per signal — profitable even with 40.6% win rate (good risk/reward).
- 🎯 Best performance at 10-19% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (18.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.35) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Mid-day (90-240 min) (avg P&L $0.42) — optimal hold duration is Mid-day (90-240 min).
- ⏱️ Long avg hold time (4413s / 73.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 32% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence  | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+------------------+----------------+----------------+
| 1     | exchange_flow_asymmetry  | 986     | 8.2%     | $0.1     | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 2     | exchange_flow_imbalance  | 2,390   | 24.0%    | $0.1     | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 3     | gamma_flip_breakout      | 2,390   | 74.2%    | $0.1     | 100%             | Trending (Up)  | ORB / Early (0-30 min) |
| 4     | vol_compression_range    | 820     | 40.6%    | $0.0     | 10-19%           | Sideways       | Mid-day (90-240 min) |
| 5     | exchange_flow_concentration | 2,236   | 36.0%    | $0.0     | 50-59%           | UNKNOWN        | ORB / Early (0-30 min) |
| 6     | magnet_accelerate        | 2,214   | 36.5%    | $-0.0    | 70-79%           | Trending (Up)  | Early (30-90 min) |
| 7     | gamma_squeeze            | 1,060   | 32.5%    | $-0.0    | 40-49%           | Trending (Up)  | ORB / Early (0-30 min) |
| 8     | gex_divergence           | 686     | 42.6%    | $-0.0    | 70-79%           | Sideways       | ORB / Early (0-30 min) |
| 9     | gamma_wall_bounce        | 3,584   | 26.9%    | $-0.1    | 20-29%           | Trending (Up)  | ORB / Early (0-30 min) |
| 10    | strike_concentration     | 590     | 15.4%    | $-0.1    | 30-39%           | Trending (Up)  | ORB / Early (0-30 min) |
| 11    | depth_decay_momentum     | 2,356   | 29.6%    | $-0.1    | 60-69%           | UNKNOWN        | ORB / Early (0-30 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*