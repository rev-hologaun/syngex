# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 20,744  |  **Strategies Analyzed:** 11

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 20,744                                                       |
| Total Wins           | 3,912                                                        |
| Total Losses         | 5,784                                                        |
| Time-Expired (CLOSED) | 11,048                                                       |
| Overall Win Rate     | 40.3%                                                        |
| Total P&L            | $424.86                                                      |
| Avg P&L per Signal   | $0.02                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,570  |  **Win Rate:** 29.5%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1265s (21.1m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 4     | 0     | 0      | 4      | 0.0%      | $1.1     | 48.5%    |
| 50-59%         | 276   | 56    | 124    | 96     | 31.1%     | $-0.2    | -9.4%    |
| 60-69%         | 316   | 62    | 122    | 132    | 33.7%     | $-0.1    | -5.5%    |
| 70-79%         | 1304  | 158   | 408    | 738    | 27.9%     | $-0.1    | -7.8%    |
| 80-89%         | 634   | 94    | 216    | 324    | 30.3%     | $-0.1    | -7.2%    |
| 90-99%         | 36    | 2     | 18     | 16     | 10.0%     | $-0.8    | -36.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2570  | 372   | 888    | 1310   | 29.5%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 464   | 124   | 274    | 66     | 31.2%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 2106  | 248   | 614    | 1244   | 28.8%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1310  | 0     | 0      | 1310   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1260  | 372   | 888    | 0      | 29.5%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1298  | 270   | 520    | 508    | 34.2%     | $-0.1    |
| SHORT        | 1272  | 102   | 368    | 802    | 21.7%     | $-0.2    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 290   | 88    | 202    | 0      | 30.3%     | $-0.4    |
| Long (30-60 min)       | 1310  | 0     | 0      | 1310   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 472   | 140   | 332    | 0      | 29.7%     | $-0.5    |
| Slow (15-30 min)       | 444   | 128   | 316    | 0      | 28.8%     | $-0.3    |
| Very Fast (<1 min)     | 54    | 16    | 38     | 0      | 29.6%     | $-0.3    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.11 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (33.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.11) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.15) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1265s / 21.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 51% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,170  |  **Win Rate:** 16.5%  |  **Avg P&L:** $0.3  |  **Avg Hold:** 2851s (47.5m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 60-69%         | 2     | 0     | 0      | 2      | 0.0%      | $2.0     | 57.3%    |
| 70-79%         | 112   | 2     | 46     | 64     | 4.2%      | $-0.2    | -18.0%   |
| 80-89%         | 1056  | 64    | 288    | 704    | 18.2%     | $0.3     | 9.6%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1170  | 66    | 334    | 770    | 16.5%     | $0.3     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1170  | 66    | 334    | 770    | 16.5%     | $0.3     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 904   | 38    | 96     | 770    | 28.4%     | $0.8     |
| ORB / Early (0-30 min) | 266   | 28    | 238    | 0      | 10.5%     | $-1.6    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 596   | 66    | 184    | 346    | 26.4%     | $0.5     |
| SHORT        | 574   | 0     | 150    | 424    | 0.0%      | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 50    | 4     | 46     | 0      | 8.0%      | $-2.2    |
| Long (30-60 min)       | 134   | 38    | 96     | 0      | 28.4%     | $0.1     |
| Medium (5-15 min)      | 96    | 12    | 84     | 0      | 12.5%     | $-1.1    |
| Slow (15-30 min)       | 108   | 12    | 96     | 0      | 11.1%     | $-1.7    |
| Very Fast (<1 min)     | 12    | 0     | 12     | 0      | 0.0%      | $-2.1    |
| Very Long (>1h)        | 770   | 0     | 0      | 770    | 0.0%      | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 16.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.27 per signal — profitable even with 16.5% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (18.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (4.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.27) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.82) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2851s / 47.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 66% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,404  |  **Win Rate:** 36.6%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1271s (21.2m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 2      | 0      | 0.0%      | $-0.6    | -100.0%  |
| 20-29%         | 26    | 2     | 8      | 16     | 20.0%     | $-0.4    | -27.4%   |
| 30-39%         | 212   | 42    | 90     | 80     | 31.8%     | $-0.1    | -7.8%    |
| 40-49%         | 434   | 96    | 152    | 186    | 38.7%     | $0.1     | 7.1%     |
| 50-59%         | 370   | 84    | 134    | 152    | 38.5%     | $-0.1    | -1.5%    |
| 60-69%         | 1360  | 204   | 356    | 800    | 36.4%     | $0.0     | -0.3%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2404  | 428   | 742    | 1234   | 36.6%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 608   | 162   | 346    | 100    | 31.9%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 1796  | 266   | 396    | 1134   | 40.2%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1234  | 0     | 0      | 1234   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1170  | 428   | 742    | 0      | 36.6%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1926  | 350   | 624    | 952    | 35.9%     | $-0.0    |
| SHORT        | 478   | 78    | 118    | 282    | 39.8%     | $0.2     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 266   | 78    | 188    | 0      | 29.3%     | $-0.4    |
| Long (30-60 min)       | 1234  | 0     | 0      | 1234   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 432   | 168   | 264    | 0      | 38.9%     | $-0.0    |
| Slow (15-30 min)       | 420   | 178   | 242    | 0      | 42.4%     | $0.2     |
| Very Fast (<1 min)     | 52    | 4     | 48     | 0      | 7.7%      | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.01 per signal — profitable even with 36.6% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (38.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (20.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.01) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.09) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1271s / 21.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 51% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,504  |  **Win Rate:** 25.2%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1874s (31.2m)  |  **Median Hold:** 2680s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 2     | 0     | 0      | 2      | 0.0%      | $1.1     | 70.5%    |
| 30-39%         | 14    | 0     | 0      | 14     | 0.0%      | $-0.1    | -2.0%    |
| 40-49%         | 34    | 4     | 12     | 18     | 25.0%     | $-0.3    | -12.6%   |
| 50-59%         | 330   | 32    | 112    | 186    | 22.2%     | $0.1     | -1.2%    |
| 60-69%         | 352   | 58    | 138    | 156    | 29.6%     | $0.2     | 6.7%     |
| 70-79%         | 1036  | 116   | 404    | 516    | 22.3%     | $0.1     | -0.9%    |
| 80-89%         | 736   | 108   | 278    | 350    | 28.0%     | $0.1     | 2.9%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2504  | 318   | 944    | 1242   | 25.2%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 466   | 76    | 344    | 46     | 18.1%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 2038  | 242   | 600    | 1196   | 28.7%     | $0.2     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1514  | 94    | 178    | 1242   | 34.6%     | $0.4     |
| ORB / Early (0-30 min) | 990   | 224   | 766    | 0      | 22.6%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1490  | 214   | 660    | 616    | 24.5%     | $-0.0    |
| SHORT        | 1014  | 104   | 284    | 626    | 26.8%     | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 228   | 36    | 192    | 0      | 15.8%     | $-0.8    |
| Long (30-60 min)       | 1514  | 94    | 178    | 1242   | 34.6%     | $0.4     |
| Medium (5-15 min)      | 320   | 70    | 250    | 0      | 21.9%     | $-0.4    |
| Slow (15-30 min)       | 392   | 112   | 280    | 0      | 28.6%     | $0.0     |
| Very Fast (<1 min)     | 50    | 6     | 44     | 0      | 12.0%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.09 per signal — profitable even with 25.2% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (29.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.09) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.39) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1874s / 31.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 50% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,580  |  **Win Rate:** 74.5%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1658s (27.6m)  |  **Median Hold:** 1103s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 24    | 14    | 0      | 10     | 100.0%    | $0.5     | 14.1%    |
| 30-39%         | 208   | 84    | 12     | 112    | 87.5%     | $0.3     | 8.3%     |
| 40-49%         | 494   | 126   | 26     | 342    | 82.9%     | $-0.0    | 1.5%     |
| 50-59%         | 524   | 430   | 28     | 66     | 93.9%     | $-0.0    | 1.0%     |
| 60-69%         | 440   | 278   | 70     | 92     | 79.9%     | $0.1     | 3.5%     |
| 70-79%         | 150   | 76    | 60     | 14     | 55.9%     | $-0.2    | -13.7%   |
| 80-89%         | 386   | 174   | 154    | 58     | 53.0%     | $0.1     | 6.7%     |
| 90-99%         | 246   | 112   | 130    | 4      | 46.3%     | $0.0     | 10.6%    |
| 100%           | 108   | 108   | 0      | 0      | 100.0%    | $0.5     | 10.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1608  | 750   | 334    | 524    | 69.2%     | $0.0     |
| Trending (Up)        | 972   | 652   | 146    | 174    | 81.7%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 108   | 108   | 0      | 0      | 100.0%    | $0.5     |
| Positive Gamma (Range-Bound friendly) | 2472  | 1294  | 480    | 698    | 72.9%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1070  | 218   | 154    | 698    | 58.6%     | $-0.3    |
| ORB / Early (0-30 min) | 1510  | 1184  | 326    | 0      | 78.4%     | $0.3     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1314  | 674   | 158    | 482    | 81.0%     | $0.1     |
| SHORT        | 1266  | 728   | 322    | 216    | 69.3%     | $-0.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 406   | 334   | 72     | 0      | 82.3%     | $0.5     |
| Long (30-60 min)       | 372   | 218   | 154    | 0      | 58.6%     | $0.1     |
| Medium (5-15 min)      | 498   | 368   | 130    | 0      | 73.9%     | $0.3     |
| Slow (15-30 min)       | 318   | 204   | 114    | 0      | 64.2%     | $0.1     |
| Very Fast (<1 min)     | 288   | 278   | 10     | 0      | 96.5%     | $0.2     |
| Very Long (>1h)        | 698   | 0     | 0      | 698    | 0.0%      | $-0.5    |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 74.5% — this strategy consistently picks directional moves.
- 💰 Positive avg P&L of $0.05 per signal — profitable even with 74.5% win rate (good risk/reward).
- 🎯 Best performance at 100% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (46.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.07) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.28) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1658s / 27.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 1,152  |  **Win Rate:** 32.7%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1609s (26.8m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 72    | 0     | 12     | 60     | 0.0%      | $-0.1    | -16.7%   |
| 40-49%         | 136   | 12    | 10     | 114    | 54.5%     | $0.0     | 10.2%    |
| 50-59%         | 238   | 18    | 22     | 198    | 45.0%     | $0.0     | 3.0%     |
| 60-69%         | 688   | 36    | 86     | 566    | 29.5%     | $0.0     | 1.7%     |
| 70-79%         | 16    | 0     | 10     | 6      | 0.0%      | $-0.7    | -67.8%   |
| 80-89%         | 2     | 2     | 0      | 0      | 100.0%    | $0.8     | 200.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 782   | 36    | 82     | 664    | 30.5%     | $0.0     |
| Trending (Up)        | 370   | 32    | 58     | 280    | 35.6%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1152  | 68    | 140    | 944    | 32.7%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 944   | 0     | 0      | 944    | 0.0%      | $0.0     |
| ORB / Early (0-30 min) | 208   | 68    | 140    | 0      | 32.7%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1152  | 68    | 140    | 944    | 32.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 48    | 2     | 46     | 0      | 4.2%      | $-1.4    |
| Long (30-60 min)       | 944   | 0     | 0      | 944    | 0.0%      | $0.0     |
| Medium (5-15 min)      | 60    | 20    | 40     | 0      | 33.3%     | $0.0     |
| Slow (15-30 min)       | 84    | 40    | 44     | 0      | 47.6%     | $0.6     |
| Very Fast (<1 min)     | 16    | 6     | 10     | 0      | 37.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 32.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.01 per signal — profitable even with 32.7% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (54.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.03) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.03) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1609s / 26.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 82% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,792  |  **Win Rate:** 29.4%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 1511s (25.2m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 2      | 0      | 0.0%      | $-3.8    | -100.0%  |
| 20-29%         | 50    | 14    | 10     | 26     | 58.3%     | $1.7     | 50.0%    |
| 30-39%         | 94    | 14    | 26     | 54     | 35.0%     | $0.6     | 13.0%    |
| 40-49%         | 178   | 34    | 80     | 64     | 29.8%     | $0.4     | -6.6%    |
| 50-59%         | 198   | 34    | 94     | 70     | 26.6%     | $-0.2    | -14.3%   |
| 60-69%         | 194   | 42    | 110    | 42     | 27.6%     | $-0.0    | -17.4%   |
| 70-79%         | 696   | 30    | 158    | 508    | 16.0%     | $-0.1    | -11.3%   |
| 80-89%         | 564   | 32    | 62     | 470    | 34.0%     | $-0.0    | -0.4%    |
| 90-99%         | 174   | 6     | 54     | 114    | 10.0%     | $-0.4    | -20.0%   |
| 100%           | 1642  | 110   | 162    | 1370   | 40.4%     | $-0.0    | -1.6%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2674  | 200   | 480    | 1994   | 29.4%     | $-0.0    |
| Trending (Up)        | 1118  | 116   | 278    | 724    | 29.4%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 504   | 60    | 330    | 114    | 15.4%     | $-0.3    |
| Positive Gamma (Range-Bound friendly) | 3288  | 256   | 428    | 2604   | 37.4%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2718  | 0     | 0      | 2718   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1074  | 316   | 758    | 0      | 29.4%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2742  | 254   | 476    | 2012   | 34.8%     | $0.0     |
| SHORT        | 1050  | 62    | 282    | 706    | 18.0%     | $-0.2    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 224   | 50    | 174    | 0      | 22.3%     | $-0.7    |
| Long (30-60 min)       | 2718  | 0     | 0      | 2718   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 398   | 114   | 284    | 0      | 28.6%     | $-0.5    |
| Slow (15-30 min)       | 418   | 146   | 272    | 0      | 34.9%     | $0.1     |
| Very Fast (<1 min)     | 34    | 6     | 28     | 0      | 17.6%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.02 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (58.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.01) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.10) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1511s / 25.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 72% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 762  |  **Win Rate:** 46.2%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 2272s (37.9m)  |  **Median Hold:** 2476s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 124   | 22    | 26     | 76     | 45.8%     | $0.3     | 8.1%     |
| 50-59%         | 144   | 2     | 78     | 64     | 2.5%      | $-0.9    | -45.3%   |
| 60-69%         | 436   | 162   | 130    | 144    | 55.5%     | $0.3     | 32.0%    |
| 70-79%         | 48    | 28    | 10     | 10     | 73.7%     | $1.2     | 64.3%    |
| 80-89%         | 10    | 2     | 8      | 0      | 20.0%     | $-1.1    | -50.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 708   | 208   | 222    | 278    | 48.4%     | $0.2     |
| Trending (Up)        | 54    | 8     | 30     | 16     | 21.1%     | $-0.7    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 762   | 216   | 252    | 294    | 46.2%     | $0.1     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 446   | 60    | 92     | 294    | 39.5%     | $0.1     |
| ORB / Early (0-30 min) | 316   | 156   | 160    | 0      | 49.4%     | $0.2     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 762   | 216   | 252    | 294    | 46.2%     | $0.1     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 66    | 30    | 36     | 0      | 45.5%     | $-0.1    |
| Long (30-60 min)       | 152   | 60    | 92     | 0      | 39.5%     | $-0.2    |
| Medium (5-15 min)      | 96    | 66    | 30     | 0      | 68.8%     | $1.2     |
| Slow (15-30 min)       | 148   | 54    | 94     | 0      | 36.5%     | $-0.4    |
| Very Fast (<1 min)     | 6     | 6     | 0      | 0      | 100.0%    | $2.3     |
| Very Long (>1h)        | 294   | 0     | 0      | 294    | 0.0%      | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 46.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.13 per signal — profitable even with 46.2% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (73.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (2.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.19) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.22) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (2272s / 37.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 39% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, NVDA, TSLA  |  **Total Signals:** 2,282  |  **Win Rate:** 36.4%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 2370s (39.5m)  |  **Median Hold:** 2781s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 340   | 0     | 120    | 220    | 0.0%      | $-0.2    | -35.3%   |
| 40-49%         | 702   | 0     | 250    | 452    | 0.0%      | $-0.3    | -34.5%   |
| 50-59%         | 70    | 0     | 48     | 22     | 0.0%      | $-0.5    | -29.8%   |
| 60-69%         | 336   | 88    | 160    | 88     | 35.5%     | $0.1     | 30.5%    |
| 70-79%         | 550   | 264   | 158    | 128    | 62.6%     | $0.4     | 61.6%    |
| 80-89%         | 282   | 122   | 90     | 70     | 57.5%     | $0.3     | 49.3%    |
| 90-99%         | 2     | 0     | 2      | 0      | 0.0%      | $-0.4    | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1808  | 314   | 648    | 846    | 32.6%     | $-0.0    |
| Trending (Up)        | 474   | 160   | 180    | 134    | 47.1%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2282  | 474   | 828    | 980    | 36.4%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1422  | 184   | 258    | 980    | 41.6%     | $0.2     |
| ORB / Early (0-30 min) | 860   | 290   | 570    | 0      | 33.7%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1590  | 292   | 552    | 746    | 34.6%     | $0.0     |
| SHORT        | 692   | 182   | 276    | 234    | 39.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 140   | 32    | 108    | 0      | 22.9%     | $-0.5    |
| Long (30-60 min)       | 442   | 184   | 258    | 0      | 41.6%     | $0.2     |
| Medium (5-15 min)      | 292   | 90    | 202    | 0      | 30.8%     | $-0.4    |
| Slow (15-30 min)       | 396   | 164   | 232    | 0      | 41.4%     | $-0.1    |
| Very Fast (<1 min)     | 32    | 4     | 28     | 0      | 12.5%     | $-0.5    |
| Very Long (>1h)        | 980   | 0     | 0      | 980    | 0.0%      | $0.3     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.03 per signal — profitable even with 36.4% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (62.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.23) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.24) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2370s / 39.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 43% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, TSLA  |  **Total Signals:** 632  |  **Win Rate:** 12.0%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 846s (14.1m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 8     | 2     | 0      | 6      | 100.0%    | $2.1     | 63.3%    |
| 40-49%         | 8     | 0     | 2      | 6      | 0.0%      | $0.3     | -0.6%    |
| 50-59%         | 46    | 0     | 6      | 40     | 0.0%      | $-0.4    | -17.6%   |
| 60-69%         | 190   | 2     | 20     | 168    | 9.1%      | $-0.3    | -10.2%   |
| 70-79%         | 336   | 2     | 16     | 318    | 11.1%     | $-0.1    | -7.3%    |
| 80-89%         | 44    | 0     | 0      | 44     | 0.0%      | $0.2     | 9.8%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 410   | 2     | 28     | 380    | 6.7%      | $-0.1    |
| Trending (Up)        | 222   | 4     | 16     | 202    | 20.0%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 632   | 6     | 44     | 582    | 12.0%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| ORB / Early (0-30 min) | 632   | 6     | 44     | 582    | 12.0%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 256   | 2     | 18     | 236    | 10.0%     | $-0.3    |
| SHORT        | 376   | 4     | 26     | 346    | 13.3%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 30    | 6     | 24     | 0      | 20.0%     | $-1.1    |
| Medium (5-15 min)      | 14    | 0     | 14     | 0      | 0.0%      | $-2.0    |
| Slow (15-30 min)       | 582   | 0     | 0      | 582    | 0.0%      | $-0.0    |
| Very Fast (<1 min)     | 6     | 0     | 6      | 0      | 0.0%      | $-1.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 12.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.13 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.09) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.13) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (846s / 14.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 92% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 896  |  **Win Rate:** 39.7%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 4293s (71.5m)  |  **Median Hold:** 4428s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 10    | 10    | 0      | 0      | 100.0%    | $5.1     | 149.9%   |
| 20-29%         | 44    | 18    | 12     | 14     | 60.0%     | $1.6     | 60.2%    |
| 30-39%         | 160   | 26    | 88     | 46     | 22.8%     | $-0.5    | -20.3%   |
| 40-49%         | 258   | 58    | 84     | 116    | 40.8%     | $-0.1    | 5.1%     |
| 50-59%         | 302   | 98    | 114    | 90     | 46.2%     | $-0.0    | 1.4%     |
| 60-69%         | 108   | 32    | 66     | 10     | 32.7%     | $-0.1    | -14.8%   |
| 70-79%         | 14    | 4     | 10     | 0      | 28.6%     | $-0.6    | -28.8%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 610   | 196   | 210    | 204    | 48.3%     | $0.3     |
| Trending (Up)        | 286   | 50    | 164    | 72     | 23.4%     | $-0.7    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 896   | 246   | 374    | 276    | 39.7%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 338   | 134   | 204    | 0      | 39.6%     | $-0.2    |
| Mid-day (90-240 min)   | 354   | 44    | 34     | 276    | 56.4%     | $0.4     |
| ORB / Early (0-30 min) | 204   | 68    | 136    | 0      | 33.3%     | $-0.5    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 490   | 182   | 96     | 212    | 65.5%     | $0.8     |
| SHORT        | 406   | 64    | 278    | 64     | 18.7%     | $-1.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 36    | 12    | 24     | 0      | 33.3%     | $-0.4    |
| Long (30-60 min)       | 176   | 78    | 98     | 0      | 44.3%     | $-0.1    |
| Medium (5-15 min)      | 92    | 32    | 60     | 0      | 34.8%     | $-0.5    |
| Slow (15-30 min)       | 74    | 24    | 50     | 0      | 32.4%     | $-0.5    |
| Very Fast (<1 min)     | 2     | 0     | 2      | 0      | 0.0%      | $-1.8    |
| Very Long (>1h)        | 516   | 100   | 140    | 276    | 41.7%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 39.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.01 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (22.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.31) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Mid-day (90-240 min) (avg P&L $0.43) — optimal hold duration is Mid-day (90-240 min).
- ⏱️ Long avg hold time (4293s / 71.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 31% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

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
| 1778763422.762 | 26     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Flow imbalance SHORT: AggVSI=-0.389 (+38.9%), R... |
| 1778748200.749 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Put wall at 297.5 supported price, GEX=6832567,... |
| 1778748926.058 | 20     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Fade SHORT above flip zone 447.50, price=448.50... |
| 1778748984.929 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Depth decay LONG: ROC=-0.5919 (-59.19%), vol/de... |
| 1778758143.659 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 9            | Call wall at 230.0 rejected price, GEX=80704963... |
| 1778762200.177 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 9            | Exchange flow SHORT: VSI=0.00 (+100.0%), ROC=-1... |
| 1778747495.622 | 20     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Call wall at 450.0 rejected price, GEX=16066771... |
| 1778756392.522 | 24     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 8            | Exchange flow SHORT: VSI=0.00 (+100.0%), ROC=-1... |
| 1778757232.234 | 16     | exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | GEX divergence (bullish): price falling but GEX... |
| 1778757612.248 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, vol_compression_range | 8            | Put wall at 450.0 supported price, GEX=15804842... |
| 1778763489.315 | 22     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Breakout LONG below flip zone 300.00, price=299... |
| 1778765395.169 | 28     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 8            | Put wall at 445.0 supported price, GEX=5867628,... |
| 1778765464.573 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 8            | Flow imbalance LONG: AggVSI=0.525 (+52.5%), ROC... |
| 1778765769.337 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 8            | Exchange flow LONG: VSI=4.17 (+316.7%), ROC=+3.... |
| 1778766614.91  | 20     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Strike bounce LONG: 450.0 Put strike, rank #3, ... |
| 1778766671.294 | 20     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Magnet pull LONG: price 298.31 below magnet 300... |
| 1778766738.518 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Magnet pull LONG: price 444.18 below magnet 450... |
| 1778767105.972 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range SHORT: price near upper edge, call wall a... |
| 1778745851.13  | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence | 7            | Fade LONG above flip zone 297.50, price=297.83,... |
| 1778746267.103 | 14     | depth_decay_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 7            | Fade SHORT above flip zone 297.50, price=298.45... |
| 1778747138.502 | 20     | depth_decay_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate | 7            | GEX divergence (bullish): price falling but GEX... |
| 1778747150.207 | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 7            | Depth decay SHORT: ROC=-0.1524 (-15.24%), vol/d... |
| 1778747202.003 | 16     | depth_decay_momentum, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 7            | Put wall at 297.5 supported price, GEX=6822552,... |
| 1778747250.258 | 18     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration | 7            | GEX divergence (bullish): price falling but GEX... |
| 1778747391.368 | 16     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 7            | Call wall at 232.5 rejected price, GEX=5712506,... |
| 1778747793.716 | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 7            | Magnet pull LONG: price 448.53 below magnet 450... |
| 1778747899.356 | 16     | depth_decay_momentum, exchange_flow_asymmetry, gamma_squeeze, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 7            | Range SHORT: price near upper edge, call wall a... |
| 1778748682.554 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 7            | Range SHORT: price near upper edge, call wall a... |
| 1778749005.56  | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, strike_concentration, vol_compression_range | 7            | Exchange flow SHORT: VSI=0.25 (+75.0%), ROC=-0.... |
| 1778749674.973 | 18     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, vol_compression_range | 7            | Call wall at 450.0 rejected price, GEX=15987956... |
| 1778749748.913 | 20     | exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 7            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1778749812.171 | 20     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 7            | Flow imbalance SHORT: AggVSI=-0.769 (+76.9%), R... |
| 1778749935.073 | 14     | depth_decay_momentum, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 7            | Put wall at 116.0 supported price, GEX=819680, ... |
| 1778750007.364 | 16     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, strike_concentration, vol_compression_range | 7            | Depth decay SHORT: ROC=-0.2846 (-28.46%), vol/d... |
| 1778750702.831 | 18     | exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, strike_concentration, vol_compression_range | 7            | Strike bounce SHORT: 300.0 Call strike, rank #1... |
| 1778750867.497 | 14     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 7            | Magnet pull LONG: price 447.06 below magnet 450... |
| 1778752929.042 | 16     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 7            | Range SHORT: price near upper edge, call wall a... |
| 1778753778.827 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, strike_concentration | 7            | Depth decay LONG: ROC=-0.1878 (-18.78%), vol/de... |
| 1778754614.845 | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, strike_concentration | 7            | Depth decay SHORT: ROC=-0.1538 (-15.38%), vol/d... |
| 1778754676.687 | 18     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 7            | Flow imbalance LONG: AggVSI=1.000 (+100.0%), RO... |
| 1778756212.936 | 14     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 7            | Flow imbalance LONG: AggVSI=0.759 (+75.9%), ROC... |
| 1778756634.2   | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate, strike_concentration | 7            | Exchange flow SHORT: VSI=0.00 (+100.0%), ROC=-1... |
| 1778756704.378 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate, vol_compression_range | 7            | Exchange flow SHORT: VSI=0.44 (+56.0%), ROC=-0.... |
| 1778757697.841 | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gex_divergence, strike_concentration, vol_compression_range | 7            | Range LONG: price near lower edge, wall at 450,... |
| 1778757800.449 | 16     | exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, vol_compression_range | 7            | Call wall at 450.0 rejected price, GEX=15803241... |
| 1778759563.296 | 18     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence | 7            | Squeeze LONG: breakout through call wall at 300... |
| 1778759625.845 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence | 7            | Put wall at 450.0 supported price, GEX=16107720... |
| 1778759685.848 | 16     | depth_decay_momentum, exchange_flow_asymmetry, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 7            | Put wall at 450.0 supported price, GEX=16117006... |
| 1778759696.003 | 20     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, vol_compression_range | 7            | Flow imbalance SHORT: AggVSI=-0.397 (+39.7%), R... |
| 1778759981.775 | 18     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence | 7            | Put wall at 115.0 supported price, GEX=3994339,... |

**2243 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 12,080   | 6          | net_gamma=>= 14515872  | 50.3%    | $0.0       |
| Gamma Wall Support (445.0)   | 1,944    | 3          | wall_strike=445.0      | 39.4%    | $0.1       |
| Gamma Wall Support (297.5)   | 1,582    | 3          | wall_strike=297.5      | 27.9%    | $0.1       |
| Gamma Wall Support (227.5)   | 1,332    | 3          | wall_strike=227.5      | 54.9%    | $0.1       |
| Gamma Wall Support (120.0)   | 576      | 2          | wall_strike=120.0      | 14.9%    | $-0.3      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 3324   | 4      | 4        | 60.1%    | $-0.0      | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Exposur  | 3322   | 4      | 4        | 52.0%    | $0.1       | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Wall Su  | 1332   | 3      | 3        | 54.9%    | $0.1       | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 4714   | 3      | 3        | 41.0%    | $0.0       | wall_gex=  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 1944   | 3      | 3        | 39.4%    | $0.1       | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 1582   | 3      | 3        | 27.9%    | $0.1       | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 720    | 2      | 2        | 26.7%    | $0.2       | wall_gex=  | gamma_wall_bounce, vol_compression_rang  |
| Gamma Wall Su  | 576    | 2      | 2        | 14.9%    | $-0.3      | wall_stri  | gamma_squeeze, gamma_wall_bounce         |

**8 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 14       | 10     | 4      | 0      | 71.4%     | 0.0       |
| 20-29%         | 146      | 48     | 30     | 68     | 61.5%     | 32.7      |
| 30-39%         | 1108     | 168    | 348    | 592    | 32.6%     | 39.3      |
| 40-49%         | 2372     | 352    | 642    | 1378   | 35.4%     | 26.0      |
| 50-59%         | 2498     | 754    | 760    | 984    | 49.8%     | 28.4      |
| 60-69%         | 4422     | 964    | 1258   | 2200   | 43.4%     | 18.8      |
| 70-79%         | 4262     | 680    | 1280   | 2302   | 34.7%     | 25.4      |
| 80-89%         | 3714     | 598    | 1096   | 2020   | 35.3%     | 18.7      |
| 90-99%         | 458      | 120    | 204    | 134    | 37.0%     | 20.9      |
| 100%           | 1750     | 218    | 162    | 1370   | 57.4%     | 42.1      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] strike_concentration | 30-39%       | 100.0%    | 32.6%     | 207%     | 1.72     | 8        | 2        | 0        |
| [ALPHA] gamma_flip_breakout | 30-39%       | 87.5%     | 32.6%     | 169%     | 1.40     | 208      | 84       | 12       |
| [ALPHA] gamma_flip_breakout | 40-49%       | 82.9%     | 35.4%     | 134%     | 1.82     | 494      | 126      | 26       |
| [ALPHA] gex_divergence   | 70-79%       | 73.7%     | 34.7%     | 112%     | 1.53     | 48       | 28       | 10       |
| [ALPHA] gamma_flip_breakout | 50-59%       | 93.9%     | 49.8%     | 89%      | 1.55     | 524      | 430      | 28       |
| [ALPHA] gamma_flip_breakout | 60-69%       | 79.9%     | 43.4%     | 84%      | 1.94     | 440      | 278      | 70       |
| [ALPHA] magnet_accelerate | 70-79%       | 62.6%     | 34.7%     | 80%      | 1.10     | 550      | 264      | 158      |
| [ALPHA] gamma_flip_breakout | 100%         | 100.0%    | 57.4%     | 74%      | 1.01     | 108      | 108      | 0        |
| [ALPHA] magnet_accelerate | 80-89%       | 57.5%     | 35.3%     | 63%      | 1.19     | 282      | 122      | 90       |
| [ALPHA] gamma_flip_breakout | 20-29%       | 100.0%    | 61.5%     | 62%      | 1.18     | 24       | 14       | 0        |
| [ALPHA] gamma_flip_breakout | 70-79%       | 55.9%     | 34.7%     | 61%      | 0.83     | 150      | 76       | 60       |
| [ALPHA] gamma_squeeze    | 40-49%       | 54.5%     | 35.4%     | 54%      | 0.74     | 136      | 12       | 10       |
| [ALPHA] gamma_flip_breakout | 80-89%       | 53.0%     | 35.3%     | 50%      | 0.95     | 386      | 174      | 154      |

**13 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence  | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+------------------+----------------+----------------+
| 1     | exchange_flow_asymmetry  | 1,170   | 16.5%    | $0.3     | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 2     | gex_divergence           | 762     | 46.2%    | $0.1     | 70-79%           | Sideways       | ORB / Early (0-30 min) |
| 3     | exchange_flow_imbalance  | 2,504   | 25.2%    | $0.1     | 60-69%           | UNKNOWN        | Early (30-90 min) |
| 4     | gamma_flip_breakout      | 2,580   | 74.5%    | $0.0     | 100%             | Trending (Up)  | ORB / Early (0-30 min) |
| 5     | magnet_accelerate        | 2,282   | 36.4%    | $0.0     | 70-79%           | Trending (Up)  | Early (30-90 min) |
| 6     | exchange_flow_concentration | 2,404   | 36.6%    | $0.0     | 40-49%           | UNKNOWN        | ORB / Early (0-30 min) |
| 7     | gamma_squeeze            | 1,152   | 32.7%    | $0.0     | 40-49%           | Trending (Up)  | ORB / Early (0-30 min) |
| 8     | vol_compression_range    | 896     | 39.7%    | $-0.0    | 10-19%           | Sideways       | Mid-day (90-240 min) |
| 9     | gamma_wall_bounce        | 3,792   | 29.4%    | $-0.0    | 20-29%           | Trending (Up)  | ORB / Early (0-30 min) |
| 10    | depth_decay_momentum     | 2,570   | 29.5%    | $-0.1    | 60-69%           | UNKNOWN        | ORB / Early (0-30 min) |
| 11    | strike_concentration     | 632     | 12.0%    | $-0.1    | 30-39%           | Trending (Up)  | ORB / Early (0-30 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*