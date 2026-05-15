# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 19,472  |  **Strategies Analyzed:** 10

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 19,472                                                       |
| Total Wins           | 1,806                                                        |
| Total Losses         | 10,322                                                       |
| Time-Expired (CLOSED) | 7,344                                                        |
| Overall Win Rate     | 14.9%                                                        |
| Total P&L            | $-9177.60                                                    |
| Avg P&L per Signal   | $-0.47                                                       |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,022  |  **Win Rate:** 29.3%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1182s (19.7m)  |  **Median Hold:** 1570s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 36    | 0     | 18     | 18     | 0.0%      | $-1.1    | -47.7%   |
| 50-59%         | 810   | 208   | 290    | 312    | 41.8%     | $0.1     | 4.2%     |
| 60-69%         | 712   | 102   | 160    | 450    | 38.9%     | $0.0     | 5.1%     |
| 70-79%         | 1056  | 132   | 442    | 482    | 23.0%     | $-0.1    | -12.7%   |
| 80-89%         | 406   | 34    | 242    | 130    | 12.3%     | $-0.4    | -39.0%   |
| 90-99%         | 2     | 2     | 0      | 0      | 100.0%    | $1.7     | 148.7%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 3022  | 478   | 1152   | 1392   | 29.3%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 606   | 78    | 404    | 124    | 16.2%     | $-0.5    |
| Positive Gamma (Range-Bound friendly) | 2416  | 400   | 748    | 1268   | 34.8%     | $0.0     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1392  | 0     | 0      | 1392   | 0.0%      | $0.2     |
| ORB / Early (0-30 min) | 1630  | 478   | 1152   | 0      | 29.3%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1650  | 206   | 822    | 622    | 20.0%     | $-0.4    |
| SHORT        | 1372  | 272   | 330    | 770    | 45.2%     | $0.4     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 254   | 82    | 172    | 0      | 32.3%     | $-0.3    |
| Long (30-60 min)       | 1392  | 0     | 0      | 1392   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 576   | 112   | 464    | 0      | 19.4%     | $-0.8    |
| Slow (15-30 min)       | 538   | 168   | 370    | 0      | 31.2%     | $0.1     |
| Very Fast (<1 min)     | 262   | 116   | 146    | 0      | 44.3%     | $0.0     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 29.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.07 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (41.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.07) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.20) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1182s / 19.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 46% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 732  |  **Win Rate:** 0.0%  |  **Avg P&L:** $-0.3  |  **Avg Hold:** 2775s (46.3m)  |  **Median Hold:** 3577s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 60-69%         | 2     | 0     | 0      | 2      | 0.0%      | $2.3     | 65.5%    |
| 70-79%         | 28    | 0     | 24     | 4      | 0.0%      | $-0.9    | -95.9%   |
| 80-89%         | 702   | 0     | 356    | 346    | 0.0%      | $-0.3    | -13.1%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 732   | 0     | 380    | 352    | 0.0%      | $-0.3    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 732   | 0     | 380    | 352    | 0.0%      | $-0.3    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 562   | 0     | 210    | 352    | 0.0%      | $0.1     |
| ORB / Early (0-30 min) | 170   | 0     | 170    | 0      | 0.0%      | $-1.8    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 410   | 0     | 348    | 62     | 0.0%      | $-2.1    |
| SHORT        | 322   | 0     | 32     | 290    | 0.0%      | $1.8     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 14    | 0     | 14     | 0      | 0.0%      | $-2.8    |
| Long (30-60 min)       | 210   | 0     | 210    | 0      | 0.0%      | $-2.6    |
| Medium (5-15 min)      | 20    | 0     | 20     | 0      | 0.0%      | $-3.0    |
| Slow (15-30 min)       | 102   | 0     | 102    | 0      | 0.0%      | $-1.7    |
| Very Fast (<1 min)     | 34    | 0     | 34     | 0      | 0.0%      | $-1.0    |
| Very Long (>1h)        | 352   | 0     | 0      | 352    | 0.0%      | $1.7     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 0.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.35 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (0.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.35) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.10) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2775s / 46.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 48% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,886  |  **Win Rate:** 18.0%  |  **Avg P&L:** $-0.5  |  **Avg Hold:** 1028s (17.1m)  |  **Median Hold:** 1135s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 0      | 2      | 0.0%      | $-0.5    | -44.7%   |
| 20-29%         | 6     | 0     | 4      | 2      | 0.0%      | $-0.9    | -79.4%   |
| 30-39%         | 92    | 20    | 50     | 22     | 28.6%     | $-0.5    | -30.3%   |
| 40-49%         | 342   | 66    | 178    | 98     | 27.0%     | $-0.3    | -23.2%   |
| 50-59%         | 122   | 10    | 76     | 36     | 11.6%     | $-0.6    | -57.4%   |
| 60-69%         | 1322  | 144   | 786    | 392    | 15.5%     | $-0.6    | -49.1%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1886  | 240   | 1094   | 552    | 18.0%     | $-0.5    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 534   | 104   | 348    | 82     | 23.0%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 1352  | 136   | 746    | 470    | 15.4%     | $-0.7    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 552   | 0     | 0      | 552    | 0.0%      | $-0.2    |
| ORB / Early (0-30 min) | 1334  | 240   | 1094   | 0      | 18.0%     | $-0.7    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1566  | 168   | 982    | 416    | 14.6%     | $-0.6    |
| SHORT        | 320   | 72    | 112    | 136    | 39.1%     | $-0.0    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 210   | 76    | 134    | 0      | 36.2%     | $-0.1    |
| Long (30-60 min)       | 552   | 0     | 0      | 552    | 0.0%      | $-0.2    |
| Medium (5-15 min)      | 456   | 76    | 380    | 0      | 16.7%     | $-0.6    |
| Slow (15-30 min)       | 482   | 36    | 446    | 0      | 7.5%      | $-0.9    |
| Very Fast (<1 min)     | 186   | 52    | 134    | 0      | 28.0%     | $-0.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 18.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.52 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (28.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.52) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $-0.20) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1028s / 17.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,140  |  **Win Rate:** 7.4%  |  **Avg P&L:** $-0.6  |  **Avg Hold:** 1558s (26.0m)  |  **Median Hold:** 1459s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 8     | 2     | 2      | 4      | 50.0%     | $0.1     | 9.9%     |
| 40-49%         | 64    | 4     | 22     | 38     | 15.4%     | $0.4     | 34.0%    |
| 50-59%         | 512   | 36    | 310    | 166    | 10.4%     | $-0.2    | -37.1%   |
| 60-69%         | 444   | 40    | 250    | 154    | 13.8%     | $-0.4    | -25.8%   |
| 70-79%         | 1078  | 52    | 688    | 338    | 7.0%      | $-0.5    | -42.7%   |
| 80-89%         | 1034  | 24    | 716    | 294    | 3.2%      | $-1.1    | -61.4%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 3140  | 158   | 1988   | 994    | 7.4%      | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 872   | 60    | 724    | 88     | 7.7%      | $-0.9    |
| Positive Gamma (Range-Bound friendly) | 2268  | 98    | 1264   | 906    | 7.2%      | $-0.5    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 1440  | 46    | 400    | 994    | 10.3%     | $0.1     |
| ORB / Early (0-30 min) | 1700  | 112   | 1588   | 0      | 6.6%      | $-1.2    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2272  | 80    | 1694   | 498    | 4.5%      | $-1.0    |
| SHORT        | 868   | 78    | 294    | 496    | 21.0%     | $0.2     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 224   | 6     | 218    | 0      | 2.7%      | $-1.4    |
| Long (30-60 min)       | 1440  | 46    | 400    | 994    | 10.3%     | $0.1     |
| Medium (5-15 min)      | 628   | 42    | 586    | 0      | 6.7%      | $-1.3    |
| Slow (15-30 min)       | 648   | 28    | 620    | 0      | 4.3%      | $-1.2    |
| Very Fast (<1 min)     | 200   | 36    | 164    | 0      | 18.0%     | $-0.9    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 7.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.63 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (3.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.63) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.06) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1558s / 26.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 32% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_squeeze

**Symbols:** AAPL, INTC, NVDA  |  **Total Signals:** 842  |  **Win Rate:** 8.1%  |  **Avg P&L:** $-0.6  |  **Avg Hold:** 1304s (21.7m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 30-39%         | 2     | 0     | 2      | 0      | 0.0%      | $-0.5    | -100.0%  |
| 40-49%         | 216   | 0     | 136    | 80     | 0.0%      | $-1.5    | -94.8%   |
| 50-59%         | 240   | 0     | 80     | 160    | 0.0%      | $-0.6    | -45.0%   |
| 60-69%         | 368   | 32    | 128    | 208    | 20.0%     | $-0.1    | -20.3%   |
| 70-79%         | 16    | 0     | 16     | 0      | 0.0%      | $-0.7    | -100.0%  |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 728   | 32    | 312    | 384    | 9.3%      | $-0.6    |
| Trending (Up)        | 114   | 0     | 50     | 64     | 0.0%      | $-0.5    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 26    | 0     | 26     | 0      | 0.0%      | $-0.5    |
| Positive Gamma (Range-Bound friendly) | 816   | 32    | 336    | 448    | 8.7%      | $-0.6    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 448   | 0     | 0      | 448    | 0.0%      | $-0.4    |
| ORB / Early (0-30 min) | 394   | 32    | 362    | 0      | 8.1%      | $-0.9    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 816   | 32    | 336    | 448    | 8.7%      | $-0.6    |
| SHORT        | 26    | 0     | 26     | 0      | 0.0%      | $-0.5    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 38    | 0     | 38     | 0      | 0.0%      | $-0.9    |
| Long (30-60 min)       | 448   | 0     | 0      | 448    | 0.0%      | $-0.4    |
| Medium (5-15 min)      | 160   | 0     | 160    | 0      | 0.0%      | $-1.2    |
| Slow (15-30 min)       | 144   | 0     | 144    | 0      | 0.0%      | $-1.1    |
| Very Fast (<1 min)     | 52    | 32    | 20     | 0      | 61.5%     | $0.7     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 8.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.63 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (20.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.53) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $-0.41) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1304s / 21.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 53% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,058  |  **Win Rate:** 15.8%  |  **Avg P&L:** $-0.5  |  **Avg Hold:** 1356s (22.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 88    | 2     | 6      | 80     | 25.0%     | $0.6     | 22.1%    |
| 20-29%         | 256   | 20    | 36     | 200    | 35.7%     | $0.6     | 19.3%    |
| 30-39%         | 362   | 22    | 114    | 226    | 16.2%     | $-0.5    | -16.7%   |
| 40-49%         | 352   | 38    | 116    | 198    | 24.7%     | $-0.7    | -22.2%   |
| 50-59%         | 378   | 88    | 116    | 174    | 43.1%     | $-0.0    | 8.5%     |
| 60-69%         | 602   | 8     | 282    | 312    | 2.8%      | $-1.1    | -39.3%   |
| 70-79%         | 606   | 40    | 242    | 324    | 14.2%     | $-0.7    | -21.3%   |
| 80-89%         | 242   | 2     | 62     | 178    | 3.1%      | $-0.9    | -39.4%   |
| 90-99%         | 492   | 16    | 242    | 234    | 6.2%      | $-0.7    | -47.3%   |
| 100%           | 1680  | 110   | 630    | 940    | 14.9%     | $-0.4    | -35.0%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 3640  | 238   | 1448   | 1954   | 14.1%     | $-0.5    |
| Trending (Up)        | 1418  | 108   | 398    | 912    | 21.3%     | $-0.5    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 922   | 80    | 482    | 360    | 14.2%     | $-0.8    |
| Positive Gamma (Range-Bound friendly) | 4136  | 266   | 1364   | 2506   | 16.3%     | $-0.4    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 2866  | 0     | 0      | 2866   | 0.0%      | $0.0     |
| ORB / Early (0-30 min) | 2192  | 346   | 1846   | 0      | 15.8%     | $-1.2    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3702  | 162   | 1562   | 1978   | 9.4%      | $-0.9    |
| SHORT        | 1356  | 184   | 284    | 888    | 39.3%     | $0.5     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 358   | 48    | 310    | 0      | 13.4%     | $-1.0    |
| Long (30-60 min)       | 2866  | 0     | 0      | 2866   | 0.0%      | $0.0     |
| Medium (5-15 min)      | 662   | 76    | 586    | 0      | 11.5%     | $-1.4    |
| Slow (15-30 min)       | 958   | 142   | 816    | 0      | 14.8%     | $-1.4    |
| Very Fast (<1 min)     | 214   | 80    | 134    | 0      | 37.4%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.51 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (43.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (2.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.49) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.04) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1356s / 22.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 57% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 980  |  **Win Rate:** 23.6%  |  **Avg P&L:** $-0.5  |  **Avg Hold:** 1599s (26.6m)  |  **Median Hold:** 1255s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 40-49%         | 142   | 22    | 50     | 70     | 30.6%     | $-0.3    | -24.6%   |
| 50-59%         | 314   | 62    | 194    | 58     | 24.2%     | $-0.6    | -36.3%   |
| 60-69%         | 442   | 82    | 346    | 14     | 19.2%     | $-0.6    | -52.4%   |
| 70-79%         | 72    | 32    | 40     | 0      | 44.4%     | $0.3     | 11.4%    |
| 80-89%         | 10    | 0     | 10     | 0      | 0.0%      | $-1.7    | -100.0%  |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 904   | 190   | 576    | 138    | 24.8%     | $-0.5    |
| Trending (Up)        | 76    | 8     | 64     | 4      | 11.1%     | $-1.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 6     | 6     | 0      | 0      | 100.0%    | $0.8     |
| Positive Gamma (Range-Bound friendly) | 974   | 192   | 640    | 142    | 23.1%     | $-0.5    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 368   | 26    | 200    | 142    | 11.5%     | $-0.8    |
| ORB / Early (0-30 min) | 612   | 172   | 440    | 0      | 28.1%     | $-0.3    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 974   | 192   | 640    | 142    | 23.1%     | $-0.5    |
| SHORT        | 6     | 6     | 0      | 0      | 100.0%    | $0.8     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 90    | 52    | 38     | 0      | 57.8%     | $0.5     |
| Long (30-60 min)       | 226   | 26    | 200    | 0      | 11.5%     | $-1.0    |
| Medium (5-15 min)      | 270   | 70    | 200    | 0      | 25.9%     | $-0.3    |
| Slow (15-30 min)       | 200   | 18    | 182    | 0      | 9.0%      | $-0.9    |
| Very Fast (<1 min)     | 52    | 32    | 20     | 0      | 61.5%     | $0.8     |
| Very Long (>1h)        | 142   | 0     | 0      | 142    | 0.0%      | $-0.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 23.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.51 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (44.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.46) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.33) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1599s / 26.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### magnet_accelerate

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,838  |  **Win Rate:** 10.0%  |  **Avg P&L:** $-0.6  |  **Avg Hold:** 890s (14.8m)  |  **Median Hold:** 515s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 10-19%         | 2     | 0     | 0      | 2      | 0.0%      | $-0.3    | -34.6%   |
| 20-29%         | 234   | 0     | 226    | 8      | 0.0%      | $-0.9    | -96.2%   |
| 30-39%         | 536   | 16    | 512    | 8      | 3.0%      | $-0.5    | -88.4%   |
| 40-49%         | 308   | 28    | 248    | 32     | 10.1%     | $-0.1    | -44.3%   |
| 50-59%         | 842   | 54    | 744    | 44     | 6.8%      | $-0.6    | -71.0%   |
| 60-69%         | 434   | 24    | 376    | 34     | 6.0%      | $-0.9    | -65.7%   |
| 70-79%         | 268   | 62    | 184    | 22     | 25.2%     | $-0.8    | -30.7%   |
| 80-89%         | 194   | 82    | 112    | 0      | 42.3%     | $0.1     | 3.8%     |
| 90-99%         | 8     | 4     | 4      | 0      | 50.0%     | $0.4     | 25.1%    |
| 100%           | 12    | 0     | 12     | 0      | 0.0%      | $1.7     | 100.0%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2282  | 202   | 1988   | 92     | 9.2%      | $-0.6    |
| Trending (Up)        | 556   | 68    | 430    | 58     | 13.7%     | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 400   | 142   | 194    | 64     | 42.3%     | $0.2     |
| Positive Gamma (Range-Bound friendly) | 2438  | 128   | 2224   | 86     | 5.4%      | $-0.7    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 490   | 88    | 252    | 150    | 25.9%     | $-0.2    |
| ORB / Early (0-30 min) | 2348  | 182   | 2166   | 0      | 7.8%      | $-0.6    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2478  | 190   | 2152   | 136    | 8.1%      | $-0.6    |
| SHORT        | 360   | 80    | 266    | 14     | 23.1%     | $-0.4    |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 680   | 58    | 622    | 0      | 8.5%      | $-0.6    |
| Long (30-60 min)       | 340   | 88    | 252    | 0      | 25.9%     | $-0.6    |
| Medium (5-15 min)      | 1222  | 44    | 1178   | 0      | 3.6%      | $-0.8    |
| Slow (15-30 min)       | 230   | 42    | 188    | 0      | 18.3%     | $-0.3    |
| Very Fast (<1 min)     | 216   | 38    | 178    | 0      | 17.6%     | $-0.3    |
| Very Long (>1h)        | 150   | 0     | 0      | 150    | 0.0%      | $0.8     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 10.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.56 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 90-99% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.55) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $-0.20) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (890s / 14.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### strike_concentration

**Symbols:** AAPL, NVDA, TSLA  |  **Total Signals:** 560  |  **Win Rate:** 35.7%  |  **Avg P&L:** $0.2  |  **Avg Hold:** 806s (13.4m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 8     | 0     | 0      | 8      | 0.0%      | $1.3     | 45.9%    |
| 30-39%         | 56    | 0     | 0      | 56     | 0.0%      | $0.2     | 4.6%     |
| 40-49%         | 40    | 0     | 0      | 40     | 0.0%      | $0.2     | 5.5%     |
| 50-59%         | 120   | 24    | 0      | 96     | 100.0%    | $0.7     | 39.3%    |
| 60-69%         | 192   | 16    | 24     | 152    | 40.0%     | $-0.1    | -8.5%    |
| 70-79%         | 144   | 0     | 48     | 96     | 0.0%      | $0.1     | 12.7%    |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 416   | 24    | 48     | 344    | 33.3%     | $0.2     |
| Trending (Up)        | 144   | 16    | 24     | 104    | 40.0%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 560   | 40    | 72     | 448    | 35.7%     | $0.2     |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| ORB / Early (0-30 min) | 560   | 40    | 72     | 448    | 35.7%     | $0.2     |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 304   | 0     | 56     | 248    | 0.0%      | $-0.1    |
| SHORT        | 256   | 40    | 16     | 200    | 71.4%     | $0.5     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 16    | 0     | 16     | 0      | 0.0%      | $-0.8    |
| Medium (5-15 min)      | 80    | 24    | 56     | 0      | 30.0%     | $-0.2    |
| Slow (15-30 min)       | 448   | 0     | 0      | 448    | 0.0%      | $0.2     |
| Very Fast (<1 min)     | 16    | 16    | 0      | 0      | 100.0%    | $2.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 35.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.20 per signal — profitable even with 35.7% win rate (good risk/reward).
- 🎯 Best performance at 50-59% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.25) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.20) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (806s / 13.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 80% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 414  |  **Win Rate:** 10.6%  |  **Avg P&L:** $-1.6  |  **Avg Hold:** 2209s (36.8m)  |  **Median Hold:** 2093s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+
| 20-29%         | 50    | 32    | 18     | 0      | 64.0%     | $1.0     | 59.7%    |
| 30-39%         | 152   | 0     | 152    | 0      | 0.0%      | $-2.8    | -100.0%  |
| 40-49%         | 140   | 6     | 134    | 0      | 4.3%      | $-1.5    | -89.3%   |
| 50-59%         | 72    | 6     | 66     | 0      | 8.3%      | $-1.1    | -79.2%   |

#### SI Score Analysis

**No SI score data available for this strategy.**

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 334   | 6     | 328    | 0      | 1.8%      | $-2.1    |
| Trending (Up)        | 80    | 38    | 42     | 0      | 47.5%     | $0.4     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 414   | 44    | 370    | 0      | 10.6%     | $-1.6    |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Early (30-90 min)      | 230   | 32    | 198    | 0      | 13.9%     | $-1.1    |
| Mid-day (90-240 min)   | 2     | 0     | 2      | 0      | 0.0%      | $-3.5    |
| ORB / Early (0-30 min) | 182   | 12    | 170    | 0      | 6.6%      | $-2.2    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 366   | 12    | 354    | 0      | 3.3%      | $-2.0    |
| SHORT        | 48    | 32    | 16     | 0      | 66.7%     | $1.3     |

#### 5) Hold Time Distribution

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 18    | 2     | 16     | 0      | 11.1%     | $-1.2    |
| Long (30-60 min)       | 208   | 32    | 176    | 0      | 15.4%     | $-0.9    |
| Medium (5-15 min)      | 12    | 8     | 4      | 0      | 66.7%     | $0.7     |
| Slow (15-30 min)       | 152   | 2     | 150    | 0      | 1.3%      | $-2.6    |
| Very Long (>1h)        | 24    | 0     | 24     | 0      | 0.0%      | $-2.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 10.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-1.61 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (64.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.36) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $-1.10) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (2209s / 36.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

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
| 1778834127.425 | 112    | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 7            | Magnet pull LONG: price 230.41 below magnet 235... |
| 1778831998.736 | 304    | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 6            | Magnet pull LONG: price 237.87 below magnet 240... |
| 1778832059.421 | 192    | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 6            | Magnet pull LONG: price 232.73 below magnet 235... |
| 1778832657.065 | 112    | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 6            | GEX divergence (bullish): price falling but GEX... |
| 1778834042.083 | 128    | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, magnet_accelerate | 6            | Put wall at 295.0 supported price, GEX=8564062,... |
| 1778845291.235 | 14     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, vol_compression_range | 6            | Put wall at 230.0 supported price, GEX=21288008... |
| 1778846752.92  | 12     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate | 6            | Flow imbalance LONG: AggVSI=1.000 (+100.0%), RO... |
| 1778847972.947 | 14     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, magnet_accelerate | 6            | GEX divergence (bullish): price falling but GEX... |
| 1778848550.263 | 14     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, vol_compression_range | 6            | Depth decay SHORT: ROC=-0.1533 (-15.33%), vol/d... |
| 1778849544.902 | 14     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 6            | Exchange flow LONG: VSI=5.43 (+443.5%), ROC=+0.... |
| 1778850353.01  | 12     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 6            | GEX divergence (bullish): price falling but GEX... |
| 1778850788.848 | 14     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, vol_compression_range | 6            | Depth decay SHORT: ROC=-0.2539 (-25.39%), vol/d... |
| 1778851286.912 | 12     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 6            | Put wall at 295.0 supported price, GEX=19486703... |
| 1778832235.48  | 96     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Flow imbalance SHORT: AggVSI=-0.354 (+35.4%), R... |
| 1778832296.938 | 128    | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Flow imbalance SHORT: AggVSI=-0.373 (+37.3%), R... |
| 1778832325.779 | 112    | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence | 5            | GEX divergence (bullish): price falling but GEX... |
| 1778832390.987 | 96     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1778832718.354 | 96     | exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 5            | Call wall at 232.5 rejected price, GEX=3831692,... |
| 1778832947.935 | 80     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gex_divergence, vol_compression_range | 5            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1778833050.127 | 112    | depth_decay_momentum, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, vol_compression_range | 5            | Flow imbalance LONG: AggVSI=0.483 (+48.3%), ROC... |
| 1778833124.35  | 112    | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | GEX divergence (bullish): price falling but GEX... |
| 1778833172.688 | 80     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | Depth decay SHORT: ROC=-0.2964 (-29.64%), vol/d... |
| 1778833187.098 | 112    | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | Call wall at 435.0 rejected price, GEX=-2694721... |
| 1778833671.387 | 96     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce | 5            | Flow imbalance SHORT: AggVSI=-0.672 (+67.2%), R... |
| 1778833735.497 | 80     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce | 5            | Depth decay SHORT: ROC=-0.1693 (-16.93%), vol/d... |
| 1778834203.762 | 80     | depth_decay_momentum, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, strike_concentration | 5            | Put wall at 432.5 supported price, GEX=1091786,... |
| 1778834433.128 | 80     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Put wall at 435.0 supported price, GEX=3186396,... |
| 1778834760.664 | 80     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce | 5            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1778836881.99  | 56     | depth_decay_momentum, exchange_flow_concentration, gamma_wall_bounce, magnet_accelerate, strike_concentration | 5            | Put wall at 295.0 supported price, GEX=4137832,... |
| 1778841513.687 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1778841577.579 | 20     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Flow imbalance SHORT: AggVSI=-0.311 (+31.1%), R... |
| 1778844836.424 | 12     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, magnet_accelerate | 5            | Depth decay SHORT: ROC=-0.7049 (-70.49%), vol/d... |
| 1778844897.25  | 10     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Flow imbalance SHORT: AggVSI=-0.585 (+58.5%), R... |
| 1778845120.59  | 12     | depth_decay_momentum, exchange_flow_asymmetry, gamma_wall_bounce, gex_divergence, magnet_accelerate | 5            | Depth decay SHORT: ROC=-0.7265 (-72.65%), vol/d... |
| 1778845145.764 | 12     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, vol_compression_range | 5            | Exchange flow LONG: VSI=24.05 (+2304.5%), ROC=+... |
| 1778845229.625 | 12     | depth_decay_momentum, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, vol_compression_range | 5            | Depth decay SHORT: ROC=-0.2083 (-20.83%), vol/d... |
| 1778845873.485 | 14     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Put wall at 435.0 supported price, GEX=3763551,... |
| 1778846391.722 | 12     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate | 5            | GEX divergence (bullish): price falling but GEX... |
| 1778846636.292 | 10     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate | 5            | GEX divergence (bullish): price falling but GEX... |
| 1778846974.155 | 10     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | Put wall at 432.5 supported price, GEX=1335501,... |
| 1778847187.152 | 12     | exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 5            | Put wall at 432.5 supported price, GEX=1352780,... |
| 1778848086.809 | 12     | exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 5            | Flow imbalance LONG: AggVSI=0.411 (+41.1%), ROC... |
| 1778848338.854 | 10     | depth_decay_momentum, exchange_flow_asymmetry, gex_divergence, magnet_accelerate, vol_compression_range | 5            | Magnet breakout: price 433.00 past magnet 435.0... |
| 1778848397.845 | 12     | depth_decay_momentum, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 5            | Magnet pull LONG: price 294.21 below magnet 300... |
| 1778848463.919 | 10     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence | 5            | Flow imbalance LONG: AggVSI=0.639 (+63.9%), ROC... |
| 1778848580.585 | 14     | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate | 5            | Magnet pull LONG: price 294.54 below magnet 300... |
| 1778848629.492 | 10     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Exchange flow LONG: VSI=20.00 (+1900.0%), ROC=+... |
| 1778848641.1   | 12     | exchange_flow_asymmetry, exchange_flow_imbalance, gex_divergence, magnet_accelerate, vol_compression_range | 5            | Magnet pull LONG: price 294.89 below magnet 300... |
| 1778849082.572 | 14     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence | 5            | GEX divergence (bullish): price falling but GEX... |
| 1778849687.76  | 14     | depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 5            | Put wall at 295.0 supported price, GEX=22941266... |

**718 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 2,472    | 5          | net_gamma=>= 2603478.  | 23.4%    | $-0.4      |
| Gamma Wall Support (440.0)   | 788      | 2          | wall_strike=440.0      | 17.6%    | $-0.8      |
| Gamma Wall Support (237.5)   | 346      | 3          | wall_strike=237.5      | 11.4%    | $-0.6      |
| Gamma Wall Support (297.5)   | 276      | 3          | wall_strike=297.5      | 56.0%    | $0.1       |
| Gamma Wall Support (111.0)   | 56       | 2          | wall_strike=111.0      | 8.0%     | $-0.5      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Wall Su  | 276    | 3      | 3        | 56.0%    | $0.1       | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 424    | 3      | 3        | 28.4%    | $0.1       | net_gamma  | gamma_squeeze, magnet_accelerate, strik  |
| Gamma Exposur  | 1064   | 3      | 3        | 24.5%    | $-0.6      | wall_gex=  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 582    | 3      | 3        | 24.0%    | $-0.2      | net_gamma  | gamma_squeeze, magnet_accelerate, strik  |
| Gamma Wall Su  | 346    | 3      | 3        | 11.4%    | $-0.6      | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Exposur  | 402    | 3      | 3        | 10.0%    | $-0.4      | wall_gex=  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 788    | 2      | 2        | 17.6%    | $-0.8      | wall_stri  | gamma_wall_bounce, vol_compression_rang  |
| Gamma Wall Su  | 56     | 2      | 2        | 8.0%     | $-0.5      | wall_stri  | gamma_squeeze, gamma_wall_bounce         |

**8 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 92       | 2      | 6      | 84     | 25.0%     | 0.0       |
| 20-29%         | 554      | 52     | 284    | 218    | 15.5%     | 29.1      |
| 30-39%         | 1208     | 60     | 832    | 316    | 6.7%      | 20.0      |
| 40-49%         | 1640     | 164    | 902    | 574    | 15.4%     | 12.4      |
| 50-59%         | 3410     | 488    | 1876   | 1046   | 20.6%     | 31.3      |
| 60-69%         | 4518     | 448    | 2352   | 1718   | 16.0%     | 13.7      |
| 70-79%         | 3268     | 318    | 1684   | 1266   | 15.9%     | 15.9      |
| 80-89%         | 2588     | 142    | 1498   | 948    | 8.7%      | 16.4      |
| 90-99%         | 502      | 22     | 246    | 234    | 8.2%      | 31.0      |
| 100%           | 1692     | 110    | 642    | 940    | 14.6%     | 10.5      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] exchange_flow_imbalance | 30-39%       | 50.0%     | 6.7%      | 643%     | 2.17     | 8        | 2        | 2        |
| [ALPHA] magnet_accelerate | 90-99%       | 50.0%     | 8.2%      | 509%     | 1.35     | 8        | 4        | 4        |
| [ALPHA] magnet_accelerate | 80-89%       | 42.3%     | 8.7%      | 388%     | 2.05     | 194      | 82       | 112      |
| [ALPHA] strike_concentration | 50-59%       | 100.0%    | 20.6%     | 384%     | 2.54     | 120      | 24       | 0        |
| [ALPHA] exchange_flow_concentration | 30-39%       | 28.6%     | 6.7%      | 325%     | 1.09     | 92       | 20       | 50       |
| [ALPHA] vol_compression_range | 20-29%       | 64.0%     | 15.5%     | 314%     | 1.67     | 50       | 32       | 18       |
| [ALPHA] gex_divergence   | 70-79%       | 44.4%     | 15.9%     | 180%     | 1.80     | 72       | 32       | 40       |
| [ALPHA] strike_concentration | 60-69%       | 40.0%     | 16.0%     | 150%     | 1.75     | 192      | 16       | 24       |
| [ALPHA] depth_decay_momentum | 60-69%       | 38.9%     | 16.0%     | 143%     | 1.68     | 712      | 102      | 160      |
| [ALPHA] gamma_wall_bounce | 30-39%       | 16.2%     | 6.7%      | 140%     | 0.47     | 362      | 22       | 114      |
| [ALPHA] gamma_wall_bounce | 20-29%       | 35.7%     | 15.5%     | 131%     | 0.70     | 256      | 20       | 36       |
| [ALPHA] gamma_wall_bounce | 50-59%       | 43.1%     | 20.6%     | 109%     | 0.72     | 378      | 88       | 116      |
| [ALPHA] depth_decay_momentum | 50-59%       | 41.8%     | 20.6%     | 102%     | 0.68     | 810      | 208      | 290      |
| [ALPHA] gex_divergence   | 40-49%       | 30.6%     | 15.4%     | 99%      | 1.22     | 142      | 22       | 50       |
| [ALPHA] exchange_flow_concentration | 40-49%       | 27.0%     | 15.4%     | 76%      | 0.94     | 342      | 66       | 178      |
| [ALPHA] gamma_wall_bounce | 40-49%       | 24.7%     | 15.4%     | 60%      | 0.75     | 352      | 38       | 116      |
| [ALPHA] magnet_accelerate | 70-79%       | 25.2%     | 15.9%     | 59%      | 0.59     | 268      | 62       | 184      |

**17 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence  | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+------------------+----------------+----------------+
| 1     | strike_concentration     | 560     | 35.7%    | $0.2     | 50-59%           | Trending (Up)  | ORB / Early (0-30 min) |
| 2     | depth_decay_momentum     | 3,022   | 29.3%    | $-0.1    | 50-59%           | UNKNOWN        | ORB / Early (0-30 min) |
| 3     | exchange_flow_asymmetry  | 732     | 0.0%     | $-0.3    | 80-89%           | UNKNOWN        | Early (30-90 min) |
| 4     | gamma_wall_bounce        | 5,058   | 15.8%    | $-0.5    | 50-59%           | Trending (Up)  | ORB / Early (0-30 min) |
| 5     | gex_divergence           | 980     | 23.6%    | $-0.5    | 70-79%           | Sideways       | ORB / Early (0-30 min) |
| 6     | exchange_flow_concentration | 1,886   | 18.0%    | $-0.5    | 30-39%           | UNKNOWN        | ORB / Early (0-30 min) |
| 7     | magnet_accelerate        | 2,838   | 10.0%    | $-0.6    | 90-99%           | Trending (Up)  | Early (30-90 min) |
| 8     | exchange_flow_imbalance  | 3,140   | 7.4%     | $-0.6    | 30-39%           | UNKNOWN        | Early (30-90 min) |
| 9     | gamma_squeeze            | 842     | 8.1%     | $-0.6    | 60-69%           | Sideways       | ORB / Early (0-30 min) |
| 10    | vol_compression_range    | 414     | 10.6%    | $-1.6    | 20-29%           | Trending (Up)  | Early (30-90 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*