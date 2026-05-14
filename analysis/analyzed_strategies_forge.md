# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 19,850  |  **Strategies Analyzed:** 11

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 19,850                                                       |
| Total Wins           | 3,750                                                        |
| Total Losses         | 5,480                                                        |
| Time-Expired (CLOSED) | 10,620                                                       |
| Overall Win Rate     | 40.6%                                                        |
| Total P&L            | $378.00                                                      |
| Avg P&L per Signal   | $0.02                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,444  |  **Win Rate:** 30.4%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1277s (21.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 4     | 0     | 0      | 4      | 0.0%      | $1.1     | 48.5%    |
| 50-59%         | 276   | 56    | 124    | 96     | 31.1%     | $-0.2    | -9.4%    |
| 60-69%         | 310   | 60    | 118    | 132    | 33.7%     | $-0.1    | -5.2%    |
| 70-79%         | 1226  | 150   | 370    | 706    | 28.8%     | $-0.0    | -5.5%    |
| 80-89%         | 592   | 92    | 194    | 306    | 32.2%     | $-0.1    | -5.3%    |
| 90-99%         | 36    | 2     | 18     | 16     | 10.0%     | $-0.8    | -36.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2444  | 360   | 824    | 1260   | 30.4%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 438   | 118   | 254    | 66     | 31.7%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 2006  | 242   | 570    | 1194   | 29.8%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1260  | 0     | 0      | 1260   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 1184  | 360   | 824    | 0      | 30.4%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1226  | 260   | 474    | 492    | 35.4%     | $-0.0    |
| SHORT        | 1218  | 100   | 350    | 768    | 22.2%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 268   | 88    | 180    | 0      | 32.8%     | $-0.3    |
| Long (30-60 min)       | 1260  | 0     | 0      | 1260   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 430   | 132   | 298    | 0      | 30.7%     | $-0.4    |
| Slow (15-30 min)       | 434   | 124   | 310    | 0      | 28.6%     | $-0.3    |
| Very Fast (<1 min)     | 52    | 16    | 36     | 0      | 30.8%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.08 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (33.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.08) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.16) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1277s / 21.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 52% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,076  |  **Win Rate:** 16.5%  |  **Avg P&L:** $0.2  |  **Avg Hold:** 2823s (47.0m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 60-69%         | 2     | 0     | 0      | 2      | 0.0%      | $2.0     | 57.3%    |
| 70-79%         | 108   | 2     | 46     | 60     | 4.2%      | $-0.3    | -24.0%   |
| 80-89%         | 966   | 60    | 268    | 638    | 18.3%     | $0.3     | 7.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1076  | 62    | 314    | 700    | 16.5%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1076  | 62    | 314    | 700    | 16.5%     | $0.2     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 822   | 34    | 88     | 700    | 27.9%     | $0.8     |
| ORB / Early (0-30 min) | 254   | 28    | 226    | 0      | 11.0%     | $-1.5    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 536   | 62    | 180    | 294    | 25.6%     | $0.3     |
| SHORT        | 540   | 0     | 134    | 406    | 0.0%      | $0.2     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 50    | 4     | 46     | 0      | 8.0%      | $-2.2    |
| Long (30-60 min)       | 122   | 34    | 88     | 0      | 27.9%     | $0.2     |
| Medium (5-15 min)      | 92    | 12    | 80     | 0      | 13.0%     | $-1.1    |
| Slow (15-30 min)       | 100   | 12    | 88     | 0      | 12.0%     | $-1.6    |
| Very Fast (<1 min)     | 12    | 0     | 12     | 0      | 0.0%      | $-2.1    |
| Very Long (>1h)        | 700   | 0     | 0      | 700    | 0.0%      | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 16.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.22 per signal — profitable even with 16.5% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (18.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (4.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.22) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.77) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2823s / 47.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 65% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,300  |  **Win Rate:** 37.1%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1280s (21.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 22    | 2     | 8      | 12     | 20.0%     | $-0.5    | -35.8%   |
| 30-39%         | 194   | 38    | 82     | 74     | 31.7%     | $-0.1    | -9.1%    |
| 40-49%         | 392   | 88    | 138    | 166    | 38.9%     | $0.0     | 6.0%     |
| 50-59%         | 356   | 80    | 128    | 148    | 38.5%     | $-0.1    | -2.0%    |
| 60-69%         | 1336  | 202   | 340    | 794    | 37.3%     | $0.1     | 0.5%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2300  | 410   | 696    | 1194   | 37.1%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 584   | 156   | 328    | 100    | 32.2%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 1716  | 254   | 368    | 1094   | 40.8%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1194  | 0     | 0      | 1194   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1106  | 410   | 696    | 0      | 37.1%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1836  | 332   | 584    | 920    | 36.2%     | $-0.0    |
| SHORT        | 464   | 78    | 112    | 274    | 41.1%     | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 248   | 78    | 170    | 0      | 31.5%     | $-0.3    |
| Long (30-60 min)       | 1194  | 0     | 0      | 1194   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 400   | 160   | 240    | 0      | 40.0%     | $0.0     |
| Slow (15-30 min)       | 406   | 168   | 238    | 0      | 41.4%     | $0.1     |
| Very Fast (<1 min)     | 52    | 4     | 48     | 0      | 7.7%      | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 37.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.01 per signal — profitable even with 37.1% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (38.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (20.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.01) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.07) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1280s / 21.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 52% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,446  |  **Win Rate:** 25.1%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1876s (31.3m)  |  **Median Hold:** 2689s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 2     | 0     | 0      | 2      | 0.0%      | $1.1     | 70.5%    |
| 30-39%         | 14    | 0     | 0      | 14     | 0.0%      | $-0.1    | -2.0%    |
| 40-49%         | 34    | 4     | 12     | 18     | 25.0%     | $-0.3    | -12.6%   |
| 50-59%         | 322   | 30    | 112    | 180    | 21.1%     | $0.1     | -2.6%    |
| 60-69%         | 344   | 54    | 136    | 154    | 28.4%     | $0.1     | 5.0%     |
| 70-79%         | 1018  | 116   | 396    | 506    | 22.7%     | $0.1     | -0.4%    |
| 80-89%         | 712   | 104   | 262    | 346    | 28.4%     | $0.1     | 3.8%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2446  | 308   | 918    | 1220   | 25.1%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 466   | 76    | 344    | 46     | 18.1%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 1980  | 232   | 574    | 1174   | 28.8%     | $0.2     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1478  | 86    | 172    | 1220   | 33.3%     | $0.4     |
| ORB / Early (0-30 min) | 968   | 222   | 746    | 0      | 22.9%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1456  | 204   | 650    | 602    | 23.9%     | $-0.0    |
| SHORT        | 990   | 104   | 268    | 618    | 28.0%     | $0.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 222   | 36    | 186    | 0      | 16.2%     | $-0.8    |
| Long (30-60 min)       | 1478  | 86    | 172    | 1220   | 33.3%     | $0.4     |
| Medium (5-15 min)      | 312   | 70    | 242    | 0      | 22.4%     | $-0.4    |
| Slow (15-30 min)       | 384   | 110   | 274    | 0      | 28.6%     | $0.0     |
| Very Fast (<1 min)     | 50    | 6     | 44     | 0      | 12.0%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 25.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.09 per signal — profitable even with 25.1% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (28.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.09) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.38) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1876s / 31.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 50% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,450  |  **Win Rate:** 74.3%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1674s (27.9m)  |  **Median Hold:** 1130s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 24    | 14    | 0      | 10     | 100.0%    | $0.5     | 14.1%    |
| 30-39%         | 204   | 82    | 12     | 110    | 87.2%     | $0.2     | 8.2%     |
| 40-49%         | 466   | 116   | 24     | 326    | 82.9%     | $-0.0    | 1.4%     |
| 50-59%         | 470   | 396   | 18     | 56     | 95.7%     | $0.0     | 3.1%     |
| 60-69%         | 416   | 260   | 68     | 88     | 79.3%     | $0.1     | 3.0%     |
| 70-79%         | 138   | 74    | 54     | 10     | 57.8%     | $-0.1    | -8.7%    |
| 80-89%         | 378   | 166   | 154    | 58     | 51.9%     | $0.1     | 6.7%     |
| 90-99%         | 246   | 112   | 130    | 4      | 46.3%     | $0.0     | 10.6%    |
| 100%           | 108   | 108   | 0      | 0      | 100.0%    | $0.5     | 10.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1536  | 714   | 320    | 502    | 69.1%     | $0.1     |
| Trending (Up)        | 914   | 614   | 140    | 160    | 81.4%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 108   | 108   | 0      | 0      | 100.0%    | $0.5     |
| Positive Gamma (Range-Bound friendly) | 2342  | 1220  | 460    | 662    | 72.6%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1024  | 218   | 144    | 662    | 60.2%     | $-0.2    |
| ORB / Early (0-30 min) | 1426  | 1110  | 316    | 0      | 77.8%     | $0.3     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1264  | 638   | 158    | 468    | 80.2%     | $0.1     |
| SHORT        | 1186  | 690   | 302    | 194    | 69.6%     | $0.1     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 380   | 308   | 72     | 0      | 81.1%     | $0.4     |
| Long (30-60 min)       | 362   | 218   | 144    | 0      | 60.2%     | $0.2     |
| Medium (5-15 min)      | 470   | 346   | 124    | 0      | 73.6%     | $0.3     |
| Slow (15-30 min)       | 314   | 204   | 110    | 0      | 65.0%     | $0.1     |
| Very Fast (<1 min)     | 262   | 252   | 10     | 0      | 96.2%     | $0.2     |
| Very Long (>1h)        | 662   | 0     | 0      | 662    | 0.0%      | $-0.4    |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 74.3% — this strategy consistently picks directional moves.
- 💰 Positive avg P&L of $0.07 per signal — profitable even with 74.3% win rate (good risk/reward).
- 🎯 Best performance at 100% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (46.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.09) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.28) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1674s / 27.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 1,082  |  **Win Rate:** 38.6%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1630s (27.2m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 72    | 0     | 12     | 60     | 0.0%      | $-0.1    | -16.7%   |
| 40-49%         | 136   | 12    | 10     | 114    | 54.5%     | $0.0     | 10.2%    |
| 50-59%         | 212   | 18    | 18     | 176    | 50.0%     | $-0.0    | 0.8%     |
| 60-69%         | 648   | 36    | 62     | 550    | 36.7%     | $0.0     | 3.9%     |
| 70-79%         | 12    | 0     | 6      | 6      | 0.0%      | $-0.6    | -57.1%   |
| 80-89%         | 2     | 2     | 0      | 0      | 100.0%    | $0.8     | 200.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 740   | 36    | 68     | 636    | 34.6%     | $0.0     |
| Trending (Up)        | 342   | 32    | 40     | 270    | 44.4%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1082  | 68    | 108    | 906    | 38.6%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 906   | 0     | 0      | 906    | 0.0%      | $0.0     |
| ORB / Early (0-30 min) | 176   | 68    | 108    | 0      | 38.6%     | $0.1     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1082  | 68    | 108    | 906    | 38.6%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 44    | 2     | 42     | 0      | 4.5%      | $-1.5    |
| Long (30-60 min)       | 906   | 0     | 0      | 906    | 0.0%      | $0.0     |
| Medium (5-15 min)      | 42    | 20    | 22     | 0      | 47.6%     | $0.6     |
| Slow (15-30 min)       | 74    | 40    | 34     | 0      | 54.1%     | $0.8     |
| Very Fast (<1 min)     | 16    | 6     | 10     | 0      | 37.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 38.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.02 per signal — profitable even with 38.6% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (54.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.03) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.09) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1630s / 27.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 84% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,668  |  **Win Rate:** 29.5%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 1515s (25.3m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 2      | 0      | 0.0%      | $-3.8    | -100.0%  |
| 20-29%         | 46    | 14    | 10     | 22     | 58.3%     | $1.6     | 49.3%    |
| 30-39%         | 86    | 10    | 26     | 50     | 27.8%     | $0.4     | 3.8%     |
| 40-49%         | 168   | 34    | 80     | 54     | 29.8%     | $0.3     | -11.1%   |
| 50-59%         | 188   | 30    | 90     | 68     | 25.0%     | $-0.2    | -16.9%   |
| 60-69%         | 182   | 36    | 104    | 42     | 25.7%     | $-0.1    | -20.2%   |
| 70-79%         | 692   | 30    | 154    | 508    | 16.3%     | $-0.1    | -10.8%   |
| 80-89%         | 540   | 32    | 60     | 448    | 34.8%     | $0.0     | -0.1%    |
| 90-99%         | 144   | 6     | 46     | 92     | 11.5%     | $-0.4    | -23.5%   |
| 100%           | 1620  | 110   | 150    | 1360   | 42.3%     | $-0.0    | -1.1%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2606  | 188   | 466    | 1952   | 28.7%     | $-0.0    |
| Trending (Up)        | 1062  | 114   | 256    | 692    | 30.8%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 482   | 56    | 316    | 110    | 15.1%     | $-0.3    |
| Positive Gamma (Range-Bound friendly) | 3186  | 246   | 406    | 2534   | 37.7%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2644  | 0     | 0      | 2644   | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 1024  | 302   | 722    | 0      | 29.5%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2648  | 240   | 462    | 1946   | 34.2%     | $-0.0    |
| SHORT        | 1020  | 62    | 260    | 698    | 19.3%     | $-0.1    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 214   | 50    | 164    | 0      | 23.4%     | $-0.7    |
| Long (30-60 min)       | 2644  | 0     | 0      | 2644   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 374   | 110   | 264    | 0      | 29.4%     | $-0.5    |
| Slow (15-30 min)       | 402   | 136   | 266    | 0      | 33.8%     | $0.0     |
| Very Fast (<1 min)     | 34    | 6     | 28     | 0      | 17.6%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.03 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (58.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (11.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.01) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.08) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1515s / 25.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 72% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 704  |  **Win Rate:** 44.7%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 2266s (37.8m)  |  **Median Hold:** 2390s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 124   | 22    | 26     | 76     | 45.8%     | $0.3     | 8.1%     |
| 50-59%         | 144   | 2     | 78     | 64     | 2.5%      | $-0.9    | -45.3%   |
| 60-69%         | 382   | 144   | 118    | 120    | 55.0%     | $0.2     | 28.9%    |
| 70-79%         | 44    | 24    | 10     | 10     | 70.6%     | $1.0     | 56.5%    |
| 80-89%         | 10    | 2     | 8      | 0      | 20.0%     | $-1.1    | -50.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 652   | 186   | 210    | 256    | 47.0%     | $0.1     |
| Trending (Up)        | 52    | 8     | 30     | 14     | 21.1%     | $-0.8    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 704   | 194   | 240    | 270    | 44.7%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 412   | 50    | 92     | 270    | 35.2%     | $-0.1    |
| ORB / Early (0-30 min) | 292   | 144   | 148    | 0      | 49.3%     | $0.2     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 704   | 194   | 240    | 270    | 44.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 58    | 26    | 32     | 0      | 44.8%     | $-0.2    |
| Long (30-60 min)       | 142   | 50    | 92     | 0      | 35.2%     | $-0.4    |
| Medium (5-15 min)      | 88    | 66    | 22     | 0      | 75.0%     | $1.5     |
| Slow (15-30 min)       | 140   | 46    | 94     | 0      | 32.9%     | $-0.6    |
| Very Fast (<1 min)     | 6     | 6     | 0      | 0      | 100.0%    | $2.3     |
| Very Long (>1h)        | 270   | 0     | 0      | 270    | 0.0%      | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 44.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.03 per signal — profitable even with 44.7% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (70.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (2.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.10) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.17) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (2266s / 37.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 38% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, NVDA, TSLA  |  **Total Signals:** 2,230  |  **Win Rate:** 36.5%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 2347s (39.1m)  |  **Median Hold:** 2691s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 340   | 0     | 120    | 220    | 0.0%      | $-0.2    | -35.3%   |
| 40-49%         | 700   | 0     | 250    | 450    | 0.0%      | $-0.3    | -35.7%   |
| 50-59%         | 58    | 0     | 46     | 12     | 0.0%      | $-1.0    | -65.4%   |
| 60-69%         | 320   | 88    | 158    | 74     | 35.8%     | $0.0     | 27.7%    |
| 70-79%         | 538   | 264   | 158    | 116    | 62.6%     | $0.4     | 61.5%    |
| 80-89%         | 272   | 122   | 90     | 60     | 57.5%     | $0.3     | 48.6%    |
| 90-99%         | 2     | 0     | 2      | 0      | 0.0%      | $-0.4    | -100.0%  |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1782  | 314   | 646    | 822    | 32.7%     | $-0.0    |
| Trending (Up)        | 448   | 160   | 178    | 110    | 47.3%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2230  | 474   | 824    | 932    | 36.5%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1374  | 184   | 258    | 932    | 41.6%     | $0.2     |
| ORB / Early (0-30 min) | 856   | 290   | 566    | 0      | 33.9%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1538  | 292   | 548    | 698    | 34.8%     | $-0.0    |
| SHORT        | 692   | 182   | 276    | 234    | 39.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 138   | 32    | 106    | 0      | 23.2%     | $-0.5    |
| Long (30-60 min)       | 442   | 184   | 258    | 0      | 41.6%     | $0.2     |
| Medium (5-15 min)      | 290   | 90    | 200    | 0      | 31.0%     | $-0.4    |
| Slow (15-30 min)       | 396   | 164   | 232    | 0      | 41.4%     | $-0.1    |
| Very Fast (<1 min)     | 32    | 4     | 28     | 0      | 12.5%     | $-0.5    |
| Very Long (>1h)        | 932   | 0     | 0      | 932    | 0.0%      | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.00 per signal — profitable even with 36.5% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (62.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.17) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.19) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2347s / 39.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 42% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, TSLA  |  **Total Signals:** 608  |  **Win Rate:** 13.6%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 852s (14.2m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 8     | 2     | 0      | 6      | 100.0%    | $2.1     | 63.3%    |
| 40-49%         | 8     | 0     | 2      | 6      | 0.0%      | $0.3     | -0.6%    |
| 50-59%         | 36    | 0     | 6      | 30     | 0.0%      | $-0.4    | -19.4%   |
| 60-69%         | 182   | 2     | 20     | 160    | 9.1%      | $-0.3    | -11.4%   |
| 70-79%         | 330   | 2     | 10     | 318    | 16.7%     | $-0.1    | -5.7%    |
| 80-89%         | 44    | 0     | 0      | 44     | 0.0%      | $0.2     | 9.8%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 402   | 2     | 24     | 376    | 7.7%      | $-0.1    |
| Trending (Up)        | 206   | 4     | 14     | 188    | 22.2%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 608   | 6     | 38     | 564    | 13.6%     | $-0.1    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| ORB / Early (0-30 min) | 608   | 6     | 38     | 564    | 13.6%     | $-0.1    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 242   | 2     | 18     | 222    | 10.0%     | $-0.4    |
| SHORT        | 366   | 4     | 20     | 342    | 16.7%     | $0.0     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 26    | 6     | 20     | 0      | 23.1%     | $-1.1    |
| Medium (5-15 min)      | 14    | 0     | 14     | 0      | 0.0%      | $-2.0    |
| Slow (15-30 min)       | 564   | 0     | 0      | 564    | 0.0%      | $-0.0    |
| Very Fast (<1 min)     | 4     | 0     | 4      | 0      | 0.0%      | $-1.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 13.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.11 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.08) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.11) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (852s / 14.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 93% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 842  |  **Win Rate:** 41.5%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 4349s (72.5m)  |  **Median Hold:** 4517s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 10    | 10    | 0      | 0      | 100.0%    | $5.1     | 149.9%   |
| 20-29%         | 44    | 18    | 12     | 14     | 60.0%     | $1.6     | 60.2%    |
| 30-39%         | 158   | 24    | 88     | 46     | 21.4%     | $-0.5    | -22.4%   |
| 40-49%         | 226   | 52    | 66     | 108    | 44.1%     | $0.0     | 8.7%     |
| 50-59%         | 290   | 98    | 102    | 90     | 49.0%     | $0.1     | 5.6%     |
| 60-69%         | 102   | 32    | 60     | 10     | 34.8%     | $-0.0    | -9.8%    |
| 70-79%         | 12    | 4     | 8      | 0      | 33.3%     | $-0.4    | -17.0%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 572   | 188   | 186    | 198    | 50.3%     | $0.4     |
| Trending (Up)        | 270   | 50    | 150    | 70     | 25.0%     | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 842   | 238   | 336    | 268    | 41.5%     | $0.1     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 304   | 126   | 178    | 0      | 41.4%     | $-0.0    |
| Mid-day (90-240 min)   | 346   | 44    | 34     | 268    | 56.4%     | $0.4     |
| ORB / Early (0-30 min) | 192   | 68    | 124    | 0      | 35.4%     | $-0.4    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 482   | 174   | 96     | 212    | 64.4%     | $0.8     |
| SHORT        | 360   | 64    | 240    | 56     | 21.1%     | $-0.8    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 32    | 12    | 20     | 0      | 37.5%     | $-0.2    |
| Long (30-60 min)       | 154   | 74    | 80     | 0      | 48.1%     | $0.2     |
| Medium (5-15 min)      | 88    | 32    | 56     | 0      | 36.4%     | $-0.4    |
| Slow (15-30 min)       | 70    | 24    | 46     | 0      | 34.3%     | $-0.4    |
| Very Fast (<1 min)     | 2     | 0     | 2      | 0      | 0.0%      | $-1.8    |
| Very Long (>1h)        | 496   | 96    | 132    | 268    | 42.1%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 41.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.08 per signal — profitable even with 41.5% win rate (good risk/reward).
- 🎯 Best performance at 10-19% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (21.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.39) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Mid-day (90-240 min) (avg P&L $0.42) — optimal hold duration is Mid-day (90-240 min).
- ⏱️ Long avg hold time (4349s / 72.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 32% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

---

## Statistical Edge Anomalies (Phase 1)

Strategies that statistically deviate from the global win-rate baseline within
specific confidence buckets. Flagged when lift > 50% above global OR > 1.5 sigma.

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 12       | 10     | 2      | 0      | 83.3%     | 0.0       |
| 20-29%         | 138      | 48     | 30     | 60     | 61.5%     | 32.7      |
| 30-39%         | 1076     | 156    | 340    | 580    | 31.5%     | 39.4      |
| 40-49%         | 2258     | 328    | 608    | 1322   | 35.0%     | 26.1      |
| 50-59%         | 2352     | 710    | 722    | 920    | 49.6%     | 29.4      |
| 60-69%         | 4224     | 914    | 1184   | 2126   | 43.6%     | 18.6      |
| 70-79%         | 4118     | 666    | 1212   | 2240   | 35.5%     | 24.6      |
| 80-89%         | 3516     | 580    | 1036   | 1900   | 35.9%     | 18.5      |
| 90-99%         | 428      | 120    | 196    | 112    | 38.0%     | 20.5      |
| 100%           | 1728     | 218    | 150    | 1360   | 59.2%     | 40.8      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] strike_concentration | 30-39%       | 100.0%    | 31.5%     | 218%     | 1.74     | 8        | 2        | 0        |
| [ALPHA] gamma_flip_breakout | 30-39%       | 87.2%     | 31.5%     | 177%     | 1.42     | 204      | 82       | 12       |
| [ALPHA] gamma_flip_breakout | 40-49%       | 82.9%     | 35.0%     | 136%     | 1.83     | 466      | 116      | 24       |
| [ALPHA] gex_divergence   | 70-79%       | 70.6%     | 35.5%     | 99%      | 1.43     | 44       | 24       | 10       |
| [ALPHA] gamma_flip_breakout | 50-59%       | 95.7%     | 49.6%     | 93%      | 1.57     | 470      | 396      | 18       |
| [ALPHA] gamma_flip_breakout | 60-69%       | 79.3%     | 43.6%     | 82%      | 1.92     | 416      | 260      | 68       |
| [ALPHA] magnet_accelerate | 70-79%       | 62.6%     | 35.5%     | 76%      | 1.10     | 538      | 264      | 158      |
| [ALPHA] gamma_flip_breakout | 100%         | 100.0%    | 59.2%     | 69%      | 1.00     | 108      | 108      | 0        |
| [ALPHA] gamma_flip_breakout | 70-79%       | 57.8%     | 35.5%     | 63%      | 0.91     | 138      | 74       | 54       |
| [ALPHA] gamma_flip_breakout | 20-29%       | 100.0%    | 61.5%     | 62%      | 1.18     | 24       | 14       | 0        |
| [ALPHA] magnet_accelerate | 80-89%       | 57.5%     | 35.9%     | 60%      | 1.17     | 272      | 122      | 90       |
| [ALPHA] gamma_squeeze    | 40-49%       | 54.5%     | 35.0%     | 56%      | 0.75     | 136      | 12       | 10       |

**12 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence  | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+------------------+----------------+----------------+
| 1     | exchange_flow_asymmetry  | 1,076   | 16.5%    | $0.2     | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 2     | exchange_flow_imbalance  | 2,446   | 25.1%    | $0.1     | 60-69%           | UNKNOWN        | Early (30-90 min) |
| 3     | vol_compression_range    | 842     | 41.5%    | $0.1     | 10-19%           | Sideways       | Mid-day (90-240 min) |
| 4     | gamma_flip_breakout      | 2,450   | 74.3%    | $0.1     | 100%             | Trending (Up)  | ORB / Early (0-30 min) |
| 5     | gex_divergence           | 704     | 44.7%    | $0.0     | 70-79%           | Sideways       | ORB / Early (0-30 min) |
| 6     | gamma_squeeze            | 1,082   | 38.6%    | $0.0     | 40-49%           | Trending (Up)  | ORB / Early (0-30 min) |
| 7     | exchange_flow_concentration | 2,300   | 37.1%    | $0.0     | 40-49%           | UNKNOWN        | ORB / Early (0-30 min) |
| 8     | magnet_accelerate        | 2,230   | 36.5%    | $0.0     | 70-79%           | Trending (Up)  | Early (30-90 min) |
| 9     | gamma_wall_bounce        | 3,668   | 29.5%    | $-0.0    | 20-29%           | Trending (Up)  | ORB / Early (0-30 min) |
| 10    | depth_decay_momentum     | 2,444   | 30.4%    | $-0.1    | 60-69%           | UNKNOWN        | ORB / Early (0-30 min) |
| 11    | strike_concentration     | 608     | 13.6%    | $-0.1    | 30-39%           | Trending (Up)  | ORB / Early (0-30 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*