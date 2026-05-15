# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 37,180  |  **Strategies Analyzed:** 11

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 37,180                                                       |
| Total Wins           | 6,230                                                        |
| Total Losses         | 10,822                                                       |
| Time-Expired (CLOSED) | 20,128                                                       |
| Overall Win Rate     | 36.5%                                                        |
| Total P&L            | $-762.48                                                     |
| Avg P&L per Signal   | $-0.02                                                       |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,012  |  **Win Rate:** 28.6%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1354s (22.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 4     | 0     | 0      | 4      | 0.0%      | $1.1     | 48.5%    |
| 50-59%         | 276   | 56    | 124    | 96     | 31.1%     | $-0.2    | -9.4%    |
| 60-69%         | 392   | 76    | 150    | 166    | 33.6%     | $-0.0    | -4.1%    |
| 70-79%         | 2898  | 324   | 850    | 1724   | 27.6%     | $-0.0    | -5.7%    |
| 80-89%         | 1376  | 174   | 434    | 768    | 28.6%     | $-0.1    | -4.9%    |
| 90-99%         | 66    | 4     | 22     | 40     | 15.4%     | $-0.4    | -19.5%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 5012  | 634   | 1580   | 2798   | 28.6%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 860   | 214   | 520    | 126    | 29.2%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 4152  | 420   | 1060   | 2672   | 28.4%     | $-0.0    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2798  | 0     | 0      | 2798   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 2214  | 634   | 1580   | 0      | 28.6%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2706  | 416   | 1016   | 1274   | 29.1%     | $-0.1    |
| SHORT        | 2306  | 218   | 564    | 1524   | 27.9%     | $-0.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 414   | 106   | 308    | 0      | 25.6%     | $-0.5    |
| Long (30-60 min)       | 2798  | 0     | 0      | 2798   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 824   | 224   | 600    | 0      | 27.2%     | $-0.5    |
| Slow (15-30 min)       | 918   | 284   | 634    | 0      | 30.9%     | $-0.3    |
| Very Fast (<1 min)     | 58    | 20    | 38     | 0      | 34.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 28.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.06 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (33.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (15.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.06) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.22) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1354s / 22.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 56% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,896  |  **Win Rate:** 11.3%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 3050s (50.8m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 60-69%         | 2     | 0     | 0      | 2      | 0.0%      | $2.0     | 57.3%    |
| 70-79%         | 134   | 2     | 50     | 82     | 3.8%      | $-0.2    | -16.4%   |
| 80-89%         | 2760  | 94    | 706    | 1960   | 11.8%     | $0.1     | 3.8%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2896  | 96    | 756    | 2044   | 11.3%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2896  | 96    | 756    | 2044   | 11.3%     | $0.1     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2452  | 54    | 354    | 2044   | 13.2%     | $0.4     |
| ORB / Early (0-30 min) | 444   | 42    | 402    | 0      | 9.5%      | $-1.7    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1532  | 96    | 462    | 974    | 17.2%     | $0.2     |
| SHORT        | 1364  | 0     | 294    | 1070   | 0.0%      | $0.1     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 62    | 8     | 54     | 0      | 12.9%     | $-1.8    |
| Long (30-60 min)       | 408   | 54    | 354    | 0      | 13.2%     | $-1.7    |
| Medium (5-15 min)      | 172   | 16    | 156    | 0      | 9.3%      | $-1.3    |
| Slow (15-30 min)       | 196   | 16    | 180    | 0      | 8.2%      | $-2.0    |
| Very Fast (<1 min)     | 14    | 2     | 12     | 0      | 14.3%     | $-1.5    |
| Very Long (>1h)        | 2044  | 0     | 0      | 2044   | 0.0%      | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 11.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.11 per signal — profitable even with 11.3% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (11.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (3.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.11) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.44) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (3050s / 50.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 71% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 4,494  |  **Win Rate:** 31.3%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 1356s (22.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 68    | 6     | 26     | 36     | 18.8%     | $-0.3    | -21.2%   |
| 20-29%         | 148   | 6     | 48     | 94     | 11.1%     | $-0.3    | -25.4%   |
| 30-39%         | 534   | 62    | 202    | 270    | 23.5%     | $-0.1    | -14.4%   |
| 40-49%         | 1066  | 144   | 306    | 616    | 32.0%     | $-0.0    | -0.5%    |
| 50-59%         | 778   | 140   | 246    | 392    | 36.3%     | $-0.0    | 0.6%     |
| 60-69%         | 1900  | 256   | 520    | 1124   | 33.0%     | $0.0     | -0.8%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 4494  | 614   | 1348   | 2532   | 31.3%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 976   | 242   | 584    | 150    | 29.3%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 3518  | 372   | 764    | 2382   | 32.7%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2532  | 0     | 0      | 2532   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 1962  | 614   | 1348   | 0      | 31.3%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3504  | 484   | 1148   | 1872   | 29.7%     | $-0.1    |
| SHORT        | 990   | 130   | 200    | 660    | 39.4%     | $0.2     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 384   | 92    | 292    | 0      | 24.0%     | $-0.5    |
| Long (30-60 min)       | 2532  | 0     | 0      | 2532   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 708   | 218   | 490    | 0      | 30.8%     | $-0.3    |
| Slow (15-30 min)       | 804   | 294   | 510    | 0      | 36.6%     | $-0.1    |
| Very Fast (<1 min)     | 66    | 10    | 56     | 0      | 15.2%     | $-0.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.02 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (36.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (11.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.02) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.17) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1356s / 22.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 56% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 4,048  |  **Win Rate:** 23.8%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1956s (32.6m)  |  **Median Hold:** 2700s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 2     | 0     | 0      | 2      | 0.0%      | $1.1     | 70.5%    |
| 30-39%         | 36    | 2     | 4      | 30     | 33.3%     | $0.3     | 15.1%    |
| 40-49%         | 110   | 6     | 32     | 72     | 15.8%     | $-0.0    | -3.3%    |
| 50-59%         | 560   | 62    | 170    | 328    | 26.7%     | $0.1     | 4.7%     |
| 60-69%         | 642   | 76    | 238    | 328    | 24.2%     | $0.1     | 1.7%     |
| 70-79%         | 1554  | 154   | 612    | 788    | 20.1%     | $0.0     | -3.9%    |
| 80-89%         | 1144  | 160   | 418    | 566    | 27.7%     | $0.1     | 5.6%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 4048  | 460   | 1474   | 2114   | 23.8%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 616   | 110   | 442    | 64     | 19.9%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 3432  | 350   | 1032   | 2050   | 25.3%     | $0.1     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2580  | 154   | 312    | 2114   | 33.0%     | $0.4     |
| ORB / Early (0-30 min) | 1468  | 306   | 1162   | 0      | 20.8%     | $-0.5    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2262  | 298   | 970    | 994    | 23.5%     | $-0.0    |
| SHORT        | 1786  | 162   | 504    | 1120   | 24.3%     | $0.2     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 280   | 40    | 240    | 0      | 14.3%     | $-0.9    |
| Long (30-60 min)       | 2580  | 154   | 312    | 2114   | 33.0%     | $0.4     |
| Medium (5-15 min)      | 508   | 88    | 420    | 0      | 17.3%     | $-0.7    |
| Slow (15-30 min)       | 622   | 170   | 452    | 0      | 27.3%     | $-0.2    |
| Very Fast (<1 min)     | 58    | 8     | 50     | 0      | 13.8%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 23.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.07 per signal — profitable even with 23.8% win rate (good risk/reward).
- 🎯 Best performance at 30-39% confidence (33.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (15.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.07) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.43) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1956s / 32.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 52% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 4,894  |  **Win Rate:** 73.3%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1712s (28.5m)  |  **Median Hold:** 1194s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 58    | 20    | 0      | 38     | 100.0%    | $0.1     | 5.0%     |
| 30-39%         | 424   | 142   | 16     | 266    | 89.9%     | $0.2     | 5.5%     |
| 40-49%         | 798   | 186   | 48     | 564    | 79.5%     | $-0.1    | -1.8%    |
| 50-59%         | 948   | 774   | 42     | 132    | 94.9%     | $0.0     | 1.8%     |
| 60-69%         | 924   | 536   | 108    | 280    | 83.2%     | $0.2     | 6.4%     |
| 70-79%         | 432   | 256   | 146    | 30     | 63.7%     | $-0.2    | -7.5%    |
| 80-89%         | 812   | 362   | 342    | 108    | 51.4%     | $0.0     | 1.5%     |
| 90-99%         | 390   | 156   | 222    | 12     | 41.3%     | $0.1     | 12.1%    |
| 100%           | 108   | 108   | 0      | 0      | 100.0%    | $0.5     | 10.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2956  | 1352  | 602    | 1002   | 69.2%     | $0.0     |
| Trending (Up)        | 1938  | 1188  | 322    | 428    | 78.7%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 108   | 108   | 0      | 0      | 100.0%    | $0.5     |
| Positive Gamma (Range-Bound friendly) | 4786  | 2432  | 924    | 1430   | 72.5%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2094  | 394   | 270    | 1430   | 59.3%     | $-0.3    |
| ORB / Early (0-30 min) | 2800  | 2146  | 654    | 0      | 76.6%     | $0.3     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2410  | 1140  | 388    | 882    | 74.6%     | $0.0     |
| SHORT        | 2484  | 1400  | 536    | 548    | 72.3%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 768   | 632   | 136    | 0      | 82.3%     | $0.4     |
| Long (30-60 min)       | 664   | 394   | 270    | 0      | 59.3%     | $0.0     |
| Medium (5-15 min)      | 940   | 660   | 280    | 0      | 70.2%     | $0.3     |
| Slow (15-30 min)       | 628   | 400   | 228    | 0      | 63.7%     | $0.1     |
| Very Fast (<1 min)     | 464   | 454   | 10     | 0      | 97.8%     | $0.3     |
| Very Long (>1h)        | 1430  | 0     | 0      | 1430   | 0.0%      | $-0.4    |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 73.3% — this strategy consistently picks directional moves.
- 💰 Positive avg P&L of $0.05 per signal — profitable even with 73.3% win rate (good risk/reward).
- 🎯 Best performance at 20-29% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (41.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.05) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.27) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1712s / 28.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 1,760  |  **Win Rate:** 17.1%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1582s (26.4m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 72    | 0     | 12     | 60     | 0.0%      | $-0.1    | -16.7%   |
| 40-49%         | 136   | 12    | 10     | 114    | 54.5%     | $0.0     | 10.2%    |
| 50-59%         | 450   | 18    | 78     | 354    | 18.8%     | $-0.1    | -3.9%    |
| 60-69%         | 1074  | 36    | 226    | 812    | 13.7%     | $-0.1    | -6.9%    |
| 70-79%         | 26    | 2     | 14     | 10     | 12.5%     | $-0.2    | -21.4%   |
| 80-89%         | 2     | 2     | 0      | 0      | 100.0%    | $0.8     | 200.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1124  | 38    | 202    | 884    | 15.8%     | $-0.1    |
| Trending (Up)        | 636   | 32    | 138    | 466    | 18.8%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1760  | 70    | 340    | 1350   | 17.1%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1350  | 0     | 0      | 1350   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 410   | 70    | 340    | 0      | 17.1%     | $-0.8    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1760  | 70    | 340    | 1350   | 17.1%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 56    | 2     | 54     | 0      | 3.6%      | $-1.4    |
| Long (30-60 min)       | 1350  | 0     | 0      | 1350   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 148   | 22    | 126    | 0      | 14.9%     | $-0.9    |
| Slow (15-30 min)       | 190   | 40    | 150    | 0      | 21.1%     | $-0.6    |
| Very Fast (<1 min)     | 16    | 6     | 10     | 0      | 37.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 17.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.10 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (54.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.09) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.11) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1582s / 26.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 77% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 6,046  |  **Win Rate:** 24.3%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1536s (25.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 2      | 0      | 0.0%      | $-3.8    | -100.0%  |
| 20-29%         | 130   | 14    | 32     | 84     | 30.4%     | $0.2     | 6.7%     |
| 30-39%         | 212   | 18    | 48     | 146    | 27.3%     | $0.1     | 3.3%     |
| 40-49%         | 334   | 38    | 110    | 186    | 25.7%     | $0.1     | -9.8%    |
| 50-59%         | 360   | 46    | 144    | 170    | 24.2%     | $-0.1    | -7.2%    |
| 60-69%         | 326   | 48    | 176    | 102    | 21.4%     | $-0.2    | -23.2%   |
| 70-79%         | 948   | 40    | 246    | 662    | 14.0%     | $-0.2    | -13.5%   |
| 80-89%         | 908   | 68    | 126    | 714    | 35.1%     | $0.0     | 4.9%     |
| 90-99%         | 368   | 18    | 94     | 256    | 16.1%     | $-0.2    | -7.9%    |
| 100%           | 2458  | 118   | 294    | 2046   | 28.6%     | $-0.1    | -4.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 4054  | 266   | 782    | 3006   | 25.4%     | $-0.1    |
| Trending (Up)        | 1992  | 142   | 490    | 1360   | 22.5%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 708   | 114   | 436    | 158    | 20.7%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 5338  | 294   | 836    | 4208   | 26.0%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 4366  | 0     | 0      | 4366   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 1680  | 408   | 1272   | 0      | 24.3%     | $-0.7    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4118  | 316   | 790    | 3012   | 28.6%     | $-0.0    |
| SHORT        | 1928  | 92    | 482    | 1354   | 16.0%     | $-0.2    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 272   | 54    | 218    | 0      | 19.9%     | $-0.8    |
| Long (30-60 min)       | 4366  | 0     | 0      | 4366   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 624   | 156   | 468    | 0      | 25.0%     | $-0.8    |
| Slow (15-30 min)       | 748   | 192   | 556    | 0      | 25.7%     | $-0.6    |
| Very Fast (<1 min)     | 36    | 6     | 30     | 0      | 16.7%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.08 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (35.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (14.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.08) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.16) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1536s / 25.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 72% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 1,734  |  **Win Rate:** 36.1%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 2393s (39.9m)  |  **Median Hold:** 2718s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 124   | 22    | 26     | 76     | 45.8%     | $0.3     | 8.1%     |
| 50-59%         | 144   | 2     | 78     | 64     | 2.5%      | $-0.9    | -45.3%   |
| 60-69%         | 1312  | 306   | 522    | 484    | 37.0%     | $-0.1    | 0.3%     |
| 70-79%         | 132   | 44    | 50     | 38     | 46.8%     | $0.2     | 17.8%    |
| 80-89%         | 22    | 12    | 8      | 2      | 60.0%     | $1.0     | 50.0%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1596  | 362   | 624    | 610    | 36.7%     | $-0.1    |
| Trending (Up)        | 138   | 24    | 60     | 54     | 28.6%     | $-0.3    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1734  | 386   | 684    | 664    | 36.1%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1118  | 168   | 286    | 664    | 37.0%     | $0.0     |
| ORB / Early (0-30 min) | 616   | 218   | 398    | 0      | 35.4%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1734  | 386   | 684    | 664    | 36.1%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 94    | 30    | 64     | 0      | 31.9%     | $-0.7    |
| Long (30-60 min)       | 454   | 168   | 286    | 0      | 37.0%     | $-0.2    |
| Medium (5-15 min)      | 212   | 90    | 122    | 0      | 42.5%     | $0.1     |
| Slow (15-30 min)       | 302   | 92    | 210    | 0      | 30.5%     | $-0.6    |
| Very Fast (<1 min)     | 8     | 6     | 2      | 0      | 75.0%     | $1.3     |
| Very Long (>1h)        | 664   | 0     | 0      | 664    | 0.0%      | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.10 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (60.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (2.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.08) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.03) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2393s / 39.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 38% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, NVDA, TSLA  |  **Total Signals:** 3,608  |  **Win Rate:** 28.2%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 2314s (38.6m)  |  **Median Hold:** 2551s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 350   | 0     | 128    | 222    | 0.0%      | $-0.2    | -36.2%   |
| 40-49%         | 780   | 0     | 308    | 472    | 0.0%      | $-0.3    | -35.2%   |
| 50-59%         | 278   | 12    | 196    | 70     | 5.8%      | $-0.2    | -23.7%   |
| 60-69%         | 728   | 130   | 376    | 222    | 25.7%     | $0.1     | 13.4%    |
| 70-79%         | 1004  | 312   | 360    | 332    | 46.4%     | $0.2     | 31.0%    |
| 80-89%         | 454   | 144   | 150    | 160    | 49.0%     | $0.2     | 27.8%    |
| 90-99%         | 14    | 2     | 8      | 4      | 20.0%     | $-0.2    | -34.1%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2596  | 374   | 1102   | 1120   | 25.3%     | $-0.0    |
| Trending (Up)        | 1012  | 226   | 424    | 362    | 34.8%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 3608  | 600   | 1526   | 1482   | 28.2%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2156  | 240   | 434    | 1482   | 35.6%     | $0.3     |
| ORB / Early (0-30 min) | 1452  | 360   | 1092   | 0      | 24.8%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2746  | 410   | 1104   | 1232   | 27.1%     | $0.1     |
| SHORT        | 862   | 190   | 422    | 250    | 31.0%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 196   | 40    | 156    | 0      | 20.4%     | $-0.5    |
| Long (30-60 min)       | 674   | 240   | 434    | 0      | 35.6%     | $0.2     |
| Medium (5-15 min)      | 548   | 124   | 424    | 0      | 22.6%     | $-0.5    |
| Slow (15-30 min)       | 674   | 192   | 482    | 0      | 28.5%     | $-0.3    |
| Very Fast (<1 min)     | 34    | 4     | 30     | 0      | 11.8%     | $-0.4    |
| Very Long (>1h)        | 1482  | 0     | 0      | 1482   | 0.0%      | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 28.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.02 per signal — profitable even with 28.2% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (49.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.16) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.33) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2314s / 38.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 41% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, TSLA  |  **Total Signals:** 1,070  |  **Win Rate:** 15.9%  |  **Avg P&L:** $-0.2  |  **Avg Hold:** 824s (13.7m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 8     | 2     | 0      | 6      | 100.0%    | $2.1     | 63.3%    |
| 40-49%         | 8     | 0     | 2      | 6      | 0.0%      | $0.3     | -0.6%    |
| 50-59%         | 88    | 4     | 8      | 76     | 33.3%     | $-0.4    | -15.1%   |
| 60-69%         | 444   | 10    | 74     | 360    | 11.9%     | $-0.3    | -11.2%   |
| 70-79%         | 468   | 6     | 52     | 410    | 10.3%     | $-0.1    | -9.7%    |
| 80-89%         | 54    | 4     | 2      | 48     | 66.7%     | $0.3     | 17.6%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 720   | 16    | 88     | 616    | 15.4%     | $-0.1    |
| Trending (Up)        | 350   | 10    | 50     | 290    | 16.7%     | $-0.4    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1070  | 26    | 138    | 906    | 15.9%     | $-0.2    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| ORB / Early (0-30 min) | 1070  | 26    | 138    | 906    | 15.9%     | $-0.2    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 388   | 6     | 68     | 314    | 8.1%      | $-0.5    |
| SHORT        | 682   | 20    | 70     | 592    | 22.2%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 52    | 16    | 36     | 0      | 30.8%     | $-0.7    |
| Medium (5-15 min)      | 102   | 10    | 92     | 0      | 9.8%      | $-1.6    |
| Slow (15-30 min)       | 906   | 0     | 0      | 906    | 0.0%      | $0.0     |
| Very Fast (<1 min)     | 10    | 0     | 10     | 0      | 0.0%      | $-1.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.18 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.10) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.18) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (824s / 13.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 85% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 1,618  |  **Win Rate:** 33.7%  |  **Avg P&L:** $-0.2  |  **Avg Hold:** 4153s (69.2m)  |  **Median Hold:** 4184s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 10    | 10    | 0      | 0      | 100.0%    | $5.1     | 149.9%   |
| 20-29%         | 86    | 24    | 42     | 20     | 36.4%     | $-0.0    | 6.5%     |
| 30-39%         | 258   | 60    | 142    | 56     | 29.7%     | $-0.3    | -12.8%   |
| 40-49%         | 424   | 96    | 170    | 158    | 36.1%     | $-0.2    | -2.1%    |
| 50-59%         | 468   | 128   | 210    | 130    | 37.9%     | $-0.2    | -8.4%    |
| 60-69%         | 298   | 70    | 176    | 52     | 28.5%     | $-0.2    | -17.6%   |
| 70-79%         | 74    | 8     | 40     | 26     | 16.7%     | $-0.3    | -8.2%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1064  | 288   | 452    | 324    | 38.9%     | $0.0     |
| Trending (Up)        | 554   | 108   | 328    | 118    | 24.8%     | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1618  | 396   | 780    | 442    | 33.7%     | $-0.2    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 628   | 236   | 392    | 0      | 37.6%     | $-0.2    |
| Mid-day (90-240 min)   | 596   | 72    | 82     | 442    | 46.8%     | $0.4     |
| ORB / Early (0-30 min) | 394   | 88    | 306    | 0      | 22.3%     | $-1.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 896   | 258   | 302    | 336    | 46.1%     | $0.3     |
| SHORT        | 722   | 138   | 478    | 106    | 22.4%     | $-0.7    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 56    | 14    | 42     | 0      | 25.0%     | $-0.9    |
| Long (30-60 min)       | 334   | 130   | 204    | 0      | 38.9%     | $-0.2    |
| Medium (5-15 min)      | 142   | 34    | 108    | 0      | 23.9%     | $-1.1    |
| Slow (15-30 min)       | 194   | 40    | 154    | 0      | 20.6%     | $-1.1    |
| Very Fast (<1 min)     | 2     | 0     | 2      | 0      | 0.0%      | $-1.8    |
| Very Long (>1h)        | 890   | 178   | 270    | 442    | 39.7%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.17 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 10-19% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (16.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.04) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Mid-day (90-240 min) (avg P&L $0.42) — optimal hold duration is Mid-day (90-240 min).
- ⏱️ Long avg hold time (4153s / 69.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

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
| 1778766671.294 | 22     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Magnet pull LONG: price 298.31 below magnet 300... |
| 1778772416.146 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | MEMX accumulation LONG: ESI=1.000 (+100.0%), de... |
| 1778772725.827 | 30     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | GEX divergence (bullish): price falling but GEX... |
| 1778777131.838 | 30     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Exchange flow LONG: VSI=9.72 (+872.0%), ROC=+0.... |
| 1778778944.343 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Fade LONG above flip zone 232.50, price=233.64,... |
| 1778781621.547 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Fade LONG above flip zone 297.50, price=297.96,... |
| 1778747495.622 | 20     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Call wall at 450.0 rejected price, GEX=16066771... |
| 1778756392.522 | 24     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 8            | Exchange flow SHORT: VSI=0.00 (+100.0%), ROC=-1... |
| 1778757232.234 | 16     | exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | GEX divergence (bullish): price falling but GEX... |
| 1778757612.248 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, vol_compression_range | 8            | Put wall at 450.0 supported price, GEX=15804842... |
| 1778763489.315 | 22     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Breakout LONG below flip zone 300.00, price=299... |
| 1778765395.169 | 28     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 8            | Put wall at 445.0 supported price, GEX=5867628,... |
| 1778765464.573 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 8            | Flow imbalance LONG: AggVSI=0.525 (+52.5%), ROC... |
| 1778765769.337 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 8            | Exchange flow LONG: VSI=4.17 (+316.7%), ROC=+3.... |
| 1778765873.082 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, vol_compression_range | 8            | Squeeze LONG: breakout through call wall at 445... |
| 1778766614.91  | 20     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Strike bounce LONG: 450.0 Put strike, rank #3, ... |
| 1778766738.518 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Magnet pull LONG: price 444.18 below magnet 450... |
| 1778766799.579 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 8            | Strike bounce SHORT: 450.0 Call strike, rank #3... |
| 1778767105.972 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range SHORT: price near upper edge, call wall a... |
| 1778768668.069 | 26     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range LONG: price near lower edge, wall at 232,... |
| 1778768771.508 | 20     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range LONG: price near lower edge, wall at 232,... |
| 1778769765.195 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration, vol_compression_range | 8            | Strike bounce SHORT: 450.0 Call strike, rank #2... |
| 1778769874.518 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 8            | Flow imbalance LONG: AggVSI=0.729 (+72.9%), ROC... |
| 1778772535.554 | 26     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence | 8            | Flow imbalance LONG: AggVSI=0.516 (+51.6%), ROC... |
| 1778772546.168 | 24     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 8            | Magnet pull LONG: price 447.10 below magnet 450... |
| 1778773586.297 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 8            | Call wall at 450.0 rejected price, GEX=13295892... |
| 1778775097.859 | 16     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, strike_concentration, vol_compression_range | 8            | Range LONG: price near lower edge, wall at 450,... |
| 1778776370.893 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 8            | Flow imbalance LONG: AggVSI=0.627 (+62.7%), ROC... |
| 1778776521.939 | 26     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range LONG: price near lower edge, wall at 298,... |
| 1778777479.273 | 16     | exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Squeeze LONG: breakout through call wall at 235... |
| 1778778790.904 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 8            | Flow imbalance SHORT: AggVSI=-1.000 (+100.0%), ... |
| 1778778850.096 | 22     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 8            | Depth decay LONG: ROC=-0.1829 (-18.29%), vol/de... |
| 1778778995.631 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Exchange flow LONG: VSI=2.80 (+180.0%), ROC=+4.... |
| 1778782201.572 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate | 8            | Put wall at 445.0 supported price, GEX=811532, ... |
| 1778782428.506 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 8            | Breakout LONG below flip zone 447.50, price=446... |
| 1778783279.394 | 26     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence | 8            | Fade SHORT above flip zone 235.00, price=235.34... |
| 1778783960.534 | 18     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Put wall at 297.5 supported price, GEX=7153744,... |
| 1778745851.13  | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence | 7            | Fade LONG above flip zone 297.50, price=297.83,... |
| 1778746267.103 | 14     | depth_decay_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 7            | Fade SHORT above flip zone 297.50, price=298.45... |
| 1778747138.502 | 20     | depth_decay_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate | 7            | GEX divergence (bullish): price falling but GEX... |
| 1778747150.207 | 16     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 7            | Depth decay SHORT: ROC=-0.1524 (-15.24%), vol/d... |
| 1778747202.003 | 16     | depth_decay_momentum, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 7            | Put wall at 297.5 supported price, GEX=6822552,... |
| 1778747250.258 | 18     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration | 7            | GEX divergence (bullish): price falling but GEX... |
| 1778747391.368 | 16     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 7            | Call wall at 232.5 rejected price, GEX=5712506,... |

**3670 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 20,034   | 6          | net_gamma=< 41003238.  | 45.1%    | $-0.0      |
| Gamma Wall Support (445.0)   | 3,450    | 3          | wall_strike=445.0      | 27.6%    | $-0.1      |
| Gamma Wall Support (297.5)   | 2,400    | 3          | wall_strike=297.5      | 15.7%    | $0.1       |
| Gamma Wall Support (227.5)   | 2,072    | 3          | wall_strike=227.5      | 39.3%    | $-0.0      |
| Gamma Wall Support (120.0)   | 780      | 2          | wall_strike=120.0      | 20.3%    | $-0.2      |
| Exchange Sweep (0.1)         | 16       | 2          | iex_intent=0.1         | 40.0%    | $-0.1      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 5666   | 4      | 4        | 58.6%    | $0.0       | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Exposur  | 5666   | 4      | 4        | 47.3%    | $-0.0      | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Wall Su  | 2072   | 3      | 3        | 39.3%    | $-0.0      | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 7778   | 3      | 3        | 27.6%    | $-0.1      | wall_gex=  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 3450   | 3      | 3        | 27.6%    | $-0.1      | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 2400   | 3      | 3        | 15.7%    | $0.1       | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Exchange Swee  | 16     | 2      | 2        | 40.0%    | $-0.1      | iex_inten  | exchange_flow_concentration, exchange_f  |
| Gamma Exposur  | 924    | 2      | 2        | 28.4%    | $0.2       | wall_gex=  | gamma_wall_bounce, vol_compression_rang  |
| Gamma Wall Su  | 780    | 2      | 2        | 20.3%    | $-0.2      | wall_stri  | gamma_squeeze, gamma_wall_bounce         |

**9 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 80       | 16     | 28     | 36     | 36.4%     | 57.5      |
| 20-29%         | 424      | 64     | 122    | 238    | 34.4%     | 38.6      |
| 30-39%         | 1894     | 286    | 552    | 1056   | 34.1%     | 37.5      |
| 40-49%         | 3784     | 504    | 1012   | 2268   | 33.2%     | 25.8      |
| 50-59%         | 4350     | 1242   | 1296   | 1812   | 48.9%     | 25.4      |
| 60-69%         | 8042     | 1544   | 2566   | 3932   | 37.6%     | 20.0      |
| 70-79%         | 7670     | 1148   | 2420   | 4102   | 32.2%     | 19.6      |
| 80-89%         | 7532     | 1020   | 2186   | 4326   | 31.8%     | 18.6      |
| 90-99%         | 838      | 180    | 346    | 312    | 34.2%     | 12.2      |
| 100%           | 2566     | 226    | 294    | 2046   | 43.5%     | 50.5      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] strike_concentration | 30-39%       | 100.0%    | 34.1%     | 193%     | 1.76     | 8        | 2        | 0        |
| [ALPHA] gamma_flip_breakout | 20-29%       | 100.0%    | 34.4%     | 191%     | 1.70     | 58       | 20       | 0        |
| [ALPHA] vol_compression_range | 10-19%       | 100.0%    | 36.4%     | 175%     | 1.11     | 10       | 10       | 0        |
| [ALPHA] gamma_flip_breakout | 30-39%       | 89.9%     | 34.1%     | 163%     | 1.49     | 424      | 142      | 16       |
| [ALPHA] gamma_flip_breakout | 40-49%       | 79.5%     | 33.2%     | 139%     | 1.79     | 798      | 186      | 48       |
| [ALPHA] gamma_flip_breakout | 100%         | 100.0%    | 43.5%     | 130%     | 1.12     | 108      | 108      | 0        |
| [ALPHA] gamma_flip_breakout | 60-69%       | 83.2%     | 37.6%     | 122%     | 2.28     | 924      | 536      | 108      |
| [ALPHA] strike_concentration | 80-89%       | 66.7%     | 31.8%     | 110%     | 1.88     | 54       | 4        | 2        |
| [ALPHA] gamma_flip_breakout | 70-79%       | 63.7%     | 32.2%     | 98%      | 1.61     | 432      | 256      | 146      |
| [ALPHA] gamma_flip_breakout | 50-59%       | 94.9%     | 48.9%     | 94%      | 1.81     | 948      | 774      | 42       |
| [ALPHA] gex_divergence   | 80-89%       | 60.0%     | 31.8%     | 89%      | 1.52     | 22       | 12       | 8        |
| [ALPHA] gamma_squeeze    | 40-49%       | 54.5%     | 33.2%     | 64%      | 0.83     | 136      | 12       | 10       |
| [ALPHA] gamma_flip_breakout | 80-89%       | 51.4%     | 31.8%     | 62%      | 1.06     | 812      | 362      | 342      |
| [ALPHA] magnet_accelerate | 80-89%       | 49.0%     | 31.8%     | 54%      | 0.92     | 454      | 144      | 150      |

**14 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence  | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+------------------+----------------+----------------+
| 1     | exchange_flow_asymmetry  | 2,896   | 11.3%    | $0.1     | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 2     | exchange_flow_imbalance  | 4,048   | 23.8%    | $0.1     | 30-39%           | UNKNOWN        | Early (30-90 min) |
| 3     | gamma_flip_breakout      | 4,894   | 73.3%    | $0.0     | 20-29%           | Trending (Up)  | ORB / Early (0-30 min) |
| 4     | magnet_accelerate        | 3,608   | 28.2%    | $0.0     | 80-89%           | Trending (Up)  | Early (30-90 min) |
| 5     | exchange_flow_concentration | 4,494   | 31.3%    | $-0.0    | 50-59%           | UNKNOWN        | ORB / Early (0-30 min) |
| 6     | depth_decay_momentum     | 5,012   | 28.6%    | $-0.1    | 60-69%           | UNKNOWN        | ORB / Early (0-30 min) |
| 7     | gamma_wall_bounce        | 6,046   | 24.3%    | $-0.1    | 80-89%           | Sideways       | ORB / Early (0-30 min) |
| 8     | gex_divergence           | 1,734   | 36.1%    | $-0.1    | 80-89%           | Sideways       | Early (30-90 min) |
| 9     | gamma_squeeze            | 1,760   | 17.1%    | $-0.1    | 40-49%           | Trending (Up)  | ORB / Early (0-30 min) |
| 10    | vol_compression_range    | 1,618   | 33.7%    | $-0.2    | 10-19%           | Sideways       | Mid-day (90-240 min) |
| 11    | strike_concentration     | 1,070   | 15.9%    | $-0.2    | 30-39%           | Trending (Up)  | ORB / Early (0-30 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*