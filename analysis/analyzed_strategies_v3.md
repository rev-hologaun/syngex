# Strategy Performance Analysis — Round 3 Validation (Regular Hours)

**Date:** 2026-06-24  |  **Generated:** 2026-06-24 00:01 UTC  |  **Total Resolved Signals:** 240,054  |  **Strategies Analyzed:** 22  |  **Confidence ≥ 20%**  |  **Regular Hours**

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 240,054                                                      |
| Total Wins           | 19,800                                                       |
| Total Losses         | 62,660                                                       |
| Time-Expired (CLOSED) | 0                                                            |
| Overall Win Rate     | 24.0%                                                        |
| Total P&L (resolved) | $8134.28                                                     |
| Avg P&L per Resolved Signal | $0.10                                                        |
| Symbols Traded       | AMD, INTC, NVDA, SPCX, TSLA                                  |

---

## Per-Strategy Deep Dive

### call_put_flow_asymmetry

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 4,648  |  **Win Rate:** 23.5%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 4658s (77.6m)  |  **Median Hold:** 3093s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 3037  | 886   | 2151   | 0      | 29.2%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 786   | 184   | 602    | 0      | 23.4%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 817   | 20    | 797    | 0      | 2.4%      | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 8     | 0     | 8      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 4648  | 1090  | 3558   | 0      | 23.5%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 427   | 332   | 95     | 0      | 77.8%     | $2.4     |
| Positive Gamma (Range-Bound friendly) | 4221  | 758   | 3463   | 0      | 18.0%     | $-0.4    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 202   | 0     | 202    | 0      | 0.0%      | $-1.3    |
| Time Held: 30-90m      | 925   | 287   | 638    | 0      | 31.0%     | $0.1     |
| Time Held: 90-240m     | 1582  | 389   | 1193   | 0      | 24.6%     | $0.4     |
| Time Held: <30m        | 1939  | 414   | 1525   | 0      | 21.4%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 2357  | 696   | 1661   | 0      | 29.5%     | $0.3     | 🟢          |
| Morning (10:00-12:00)  | 1844  | 222   | 1622   | 0      | 12.0%     | $-1.0    | 🔴          |
| ORB (9:30-10:00)       | 447   | 172   | 275    | 0      | 38.5%     | $0.5     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 447    | 0          | 0          | 447        | 0.0%      | 0.0%      | 100.0%    |
| Morning (10:00-12:00)  | 1844   | 0          | 360        | 1484       | 0.0%      | 19.5%     | 80.5%     |
| Afternoon (12:00-16:00) | 2357   | 0          | 465        | 1892       | 0.0%      | 19.7%     | 80.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 447    | 172   | 275    | 0      | 38.5%     | $0.5         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 1048   | 142   | 906    | 0      | 13.5%     | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 436    | 60    | 376    | 0      | 13.8%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 352    | 20    | 332    | 0      | 5.7%      | $-1.4        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 8      | 0     | 8      | 0      | 0.0%      | $-1.3        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 1542   | 572   | 970    | 0      | 37.1%     | $1.1         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 350    | 124   | 226    | 0      | 35.4%     | $0.9         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 465    | 0     | 465    | 0      | 0.0%      | $-2.4        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4232  | 768   | 3464   | 0      | 18.1%     | $-0.4    |
| SHORT        | 416   | 322   | 94     | 0      | 77.4%     | $2.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 446   | 110   | 336    | 0      | 24.7%     | $-0.3    |
| Long (30-60 min)       | 534   | 172   | 362    | 0      | 32.2%     | $-0.1    |
| Medium (5-15 min)      | 864   | 197   | 667    | 0      | 22.8%     | $-0.7    |
| Slow (15-30 min)       | 570   | 106   | 464    | 0      | 18.6%     | $-0.8    |
| Very Fast (<1 min)     | 59    | 1     | 58     | 0      | 1.7%      | $-1.6    |
| Very Long (>1h)        | 2175  | 504   | 1671   | 0      | 23.2%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 23.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.18 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (29.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.18) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.37) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (38.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4658s / 77.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### confluence_reversal

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 3,166  |  **Win Rate:** 15.9%  |  **Avg P&L (resolved):** $-1.4  |  **Avg P&L (all):** $-1.4  |  **Avg Hold:** 4154s (69.2m)  |  **Median Hold:** 2210s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 1474  | 333   | 1141   | 0      | 22.6%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 883   | 115   | 768    | 0      | 13.0%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 519   | 29    | 490    | 0      | 5.6%      | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 213   | 18    | 195    | 0      | 8.5%      | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 53    | 0     | 53     | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 24    | 8     | 16     | 0      | 33.3%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1893  | 309   | 1584   | 0      | 16.3%     | $-1.4    |
| Trending (Up)        | 1273  | 194   | 1079   | 0      | 15.2%     | $-1.5    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1105  | 169   | 936    | 0      | 15.3%     | $-2.0    |
| Positive Gamma (Range-Bound friendly) | 2061  | 334   | 1727   | 0      | 16.2%     | $-1.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 174   | 35    | 139    | 0      | 20.1%     | $-1.5    |
| Time Held: 30-90m      | 762   | 145   | 617    | 0      | 19.0%     | $-1.3    |
| Time Held: 90-240m     | 799   | 72    | 727    | 0      | 9.0%      | $-1.7    |
| Time Held: <30m        | 1431  | 251   | 1180   | 0      | 17.5%     | $-1.3    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1066  | 188   | 878    | 0      | 17.6%     | $-1.4    | 🟢          |
| Morning (10:00-12:00)  | 1616  | 192   | 1424   | 0      | 11.9%     | $-1.6    | 🔴          |
| ORB (9:30-10:00)       | 484   | 123   | 361    | 0      | 25.4%     | $-0.7    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 484    | 0          | 42         | 442        | 0.0%      | 8.7%      | 91.3%     |
| Morning (10:00-12:00)  | 1616   | 24         | 207        | 1385       | 1.5%      | 12.8%     | 85.7%     |
| Afternoon (12:00-16:00) | 1066   | 0          | 17         | 1049       | 0.0%      | 1.6%      | 98.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 253    | 75    | 178    | 0      | 29.6%     | $-0.6        | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 111    | 30    | 81     | 0      | 27.0%     | $-0.7        | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 78     | 18    | 60     | 0      | 23.1%     | $-0.5        | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 40     | 0     | 40     | 0      | 0.0%      | $-2.1        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.9        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 588    | 122   | 466    | 0      | 20.7%     | $-1.2        | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 453    | 42    | 411    | 0      | 9.3%      | $-2.0        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 344    | 4     | 340    | 0      | 1.2%      | $-2.1        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 157    | 16    | 141    | 0      | 10.2%     | $-1.2        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 50     | 0     | 50     | 0      | 0.0%      | $-1.7        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 24     | 8     | 16     | 0      | 33.3%     | $0.5         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 633    | 136   | 497    | 0      | 21.5%     | $-1.2        | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 319    | 43    | 276    | 0      | 13.5%     | $-1.5        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 97     | 7     | 90     | 0      | 7.2%      | $-1.8        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 16     | 2     | 14     | 0      | 12.5%     | $-1.5        | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-2.5        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2189  | 248   | 1941   | 0      | 11.3%     | $-1.7    |
| SHORT        | 977   | 255   | 722    | 0      | 26.1%     | $-0.7    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 327   | 56    | 271    | 0      | 17.1%     | $-1.2    |
| Long (30-60 min)       | 536   | 109   | 427    | 0      | 20.3%     | $-1.0    |
| Medium (5-15 min)      | 492   | 104   | 388    | 0      | 21.1%     | $-1.3    |
| Slow (15-30 min)       | 528   | 69    | 459    | 0      | 13.1%     | $-1.5    |
| Very Fast (<1 min)     | 84    | 22    | 62     | 0      | 26.2%     | $-0.1    |
| Very Long (>1h)        | 1199  | 143   | 1056   | 0      | 11.9%     | $-1.8    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.41 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (33.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-1.36) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $-1.27) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (25.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4154s / 69.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_gamma_squeeze

**Symbols:** INTC, NVDA, TSLA  |  **Total Signals:** 40  |  **Win Rate:** 0.0%  |  **Avg P&L (resolved):** $-2.9  |  **Avg P&L (all):** $-2.9  |  **Avg Hold:** 1988s (33.1m)  |  **Median Hold:** 1564s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 2     | 0     | 2      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 30    | 0     | 30     | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 8     | 0     | 8      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 10    | 0     | 10     | 0      | 0.0%      | $-3.0    |
| Trending (Up)        | 30    | 0     | 30     | 0      | 0.0%      | $-2.8    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 40    | 0     | 40     | 0      | 0.0%      | $-2.9    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 6     | 0     | 6      | 0      | 0.0%      | $-4.9    |
| Time Held: 90-240m     | 2     | 0     | 2      | 0      | 0.0%      | $-1.7    |
| Time Held: <30m        | 32    | 0     | 32     | 0      | 0.0%      | $-2.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Morning (10:00-12:00)  | 40    | 0     | 40     | 0      | 0.0%      | $-2.9    | —          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 40     | 0          | 0          | 40         | 0.0%      | 0.0%      | 100.0%    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 40    | 0     | 40     | 0      | 0.0%      | $-2.9    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Long (30-60 min)       | 6     | 0     | 6      | 0      | 0.0%      | $-4.9    |
| Slow (15-30 min)       | 32    | 0     | 32     | 0      | 0.0%      | $-2.6    |
| Very Long (>1h)        | 2     | 0     | 2      | 0      | 0.0%      | $-1.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 0.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-2.87 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (0.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-2.81) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-2.56) — optimal time held is Time Held: <30m.
- 🕐 Best signal generation window: Morning (10:00-12:00) (0.0% win rate) — signals in this window have the highest hit rate.
- ⏱️ Long avg hold time (1988s / 33.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_volume_exhaustion

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 11,883  |  **Win Rate:** 0.0%  |  **Avg P&L (resolved):** $2.0  |  **Avg P&L (all):** $2.0  |  **Avg Hold:** 1s (0.0m)  |  **Median Hold:** 1s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 8785  | 0     | 8785   | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 2339  | 0     | 2339   | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 677   | 0     | 677    | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 82    | 0     | 82     | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 11883 | 0     | 11883  | 0      | 0.0%      | $2.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1581  | 0     | 1581   | 0      | 0.0%      | $2.2     |
| Positive Gamma (Range-Bound friendly) | 10302 | 0     | 10302  | 0      | 0.0%      | $2.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: <30m        | 11883 | 0     | 11883  | 0      | 0.0%      | $2.0     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 6831  | 0     | 6831   | 0      | 0.0%      | $2.0     | —          |
| Morning (10:00-12:00)  | 3711  | 0     | 3711   | 0      | 0.0%      | $2.1     | —          |
| ORB (9:30-10:00)       | 1341  | 0     | 1341   | 0      | 0.0%      | $2.0     | —          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 1341   | 0          | 8          | 1333       | 0.0%      | 0.6%      | 99.4%     |
| Morning (10:00-12:00)  | 3711   | 0          | 38         | 3673       | 0.0%      | 1.0%      | 99.0%     |
| Afternoon (12:00-16:00) | 6831   | 0          | 36         | 6795       | 0.0%      | 0.5%      | 99.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 968    | 0     | 968    | 0      | 0.0%      | $2.1         | —          |
| ORB (9:30-10:00)       | 30-39%     | 309    | 0     | 309    | 0      | 0.0%      | $1.9         | —          |
| ORB (9:30-10:00)       | 40-49%     | 56     | 0     | 56     | 0      | 0.0%      | $1.9         | —          |
| ORB (9:30-10:00)       | 50-59%     | 8      | 0     | 8      | 0      | 0.0%      | $1.1         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 2798   | 0     | 2798   | 0      | 0.0%      | $2.1         | —          |
| Morning (10:00-12:00)  | 30-39%     | 651    | 0     | 651    | 0      | 0.0%      | $1.9         | —          |
| Morning (10:00-12:00)  | 40-49%     | 224    | 0     | 224    | 0      | 0.0%      | $1.7         | —          |
| Morning (10:00-12:00)  | 50-59%     | 38     | 0     | 38     | 0      | 0.0%      | $1.6         | —          |
| Afternoon (12:00-16:00) | 20-29%     | 5019   | 0     | 5019   | 0      | 0.0%      | $2.1         | —          |
| Afternoon (12:00-16:00) | 30-39%     | 1379   | 0     | 1379   | 0      | 0.0%      | $1.9         | —          |
| Afternoon (12:00-16:00) | 40-49%     | 397    | 0     | 397    | 0      | 0.0%      | $1.8         | —          |
| Afternoon (12:00-16:00) | 50-59%     | 36     | 0     | 36     | 0      | 0.0%      | $1.5         | —          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 5632  | 0     | 5632   | 0      | 0.0%      | $2.0     |
| SHORT        | 6251  | 0     | 6251   | 0      | 0.0%      | $2.1     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Very Fast (<1 min)     | 11883 | 0     | 11883  | 0      | 0.0%      | $2.0     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 0.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $2.04 — profitable even with 0.0% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (0.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $2.04) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $2.04) — optimal time held is Time Held: <30m.
- 🕐 Best signal generation window: ORB (9:30-10:00) (0.0% win rate) — signals in this window have the highest hit rate.
- ⚡ Very fast avg hold time (1s) — strategy captures quick moves. Ensure slippage/commissions don't eat into thin margins.

---

### depth_decay_momentum

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 5,533  |  **Win Rate:** 36.5%  |  **Avg P&L (resolved):** $-0.1  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 2572s (42.9m)  |  **Median Hold:** 981s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 36    | 18    | 18     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1739  | 675   | 1064   | 0      | 38.8%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 2900  | 1017  | 1883   | 0      | 35.1%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 786   | 268   | 518    | 0      | 34.1%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 72    | 40    | 32     | 0      | 55.6%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 5533  | 2018  | 3515   | 0      | 36.5%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1696  | 651   | 1045   | 0      | 38.4%     | $0.1     |
| Positive Gamma (Range-Bound friendly) | 3837  | 1367  | 2470   | 0      | 35.6%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 40    | 8     | 32     | 0      | 20.0%     | $-0.5    |
| Time Held: 30-90m      | 1046  | 347   | 699    | 0      | 33.2%     | $-0.0    |
| Time Held: 90-240m     | 961   | 432   | 529    | 0      | 45.0%     | $0.3     |
| Time Held: <30m        | 3486  | 1231  | 2255   | 0      | 35.3%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 2590  | 852   | 1738   | 0      | 32.9%     | $-0.2    | 🔴          |
| Morning (10:00-12:00)  | 2173  | 823   | 1350   | 0      | 37.9%     | $-0.0    | 🟢          |
| ORB (9:30-10:00)       | 770   | 343   | 427    | 0      | 44.5%     | $0.2     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 770    | 78         | 684        | 8          | 10.1%     | 88.8%     | 1.0%      |
| Morning (10:00-12:00)  | 2173   | 503        | 1658       | 12         | 23.1%     | 76.3%     | 0.6%      |
| Afternoon (12:00-16:00) | 2590   | 277        | 2297       | 16         | 10.7%     | 88.7%     | 0.6%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 40-49%     | 8      | 4     | 4      | 0      | 50.0%     | $0.5         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 259    | 120   | 139    | 0      | 46.3%     | $0.3         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 425    | 189   | 236    | 0      | 44.5%     | $0.2         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 78     | 30    | 48     | 0      | 38.5%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 12     | 6     | 6      | 0      | 50.0%     | $0.4         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 596    | 222   | 374    | 0      | 37.2%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 1062   | 412   | 650    | 0      | 38.8%     | $0.0         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 431    | 143   | 288    | 0      | 33.2%     | $-0.1        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 72     | 40    | 32     | 0      | 55.6%     | $0.4         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 16     | 8     | 8      | 0      | 50.0%     | $0.2         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 884    | 333   | 551    | 0      | 37.7%     | $-0.0        | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 1413   | 416   | 997    | 0      | 29.4%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 277    | 95    | 182    | 0      | 34.3%     | $-0.1        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3261  | 827   | 2434   | 0      | 25.4%     | $-0.3    |
| SHORT        | 2272  | 1191  | 1081   | 0      | 52.4%     | $0.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 1002  | 310   | 692    | 0      | 30.9%     | $-0.3    |
| Long (30-60 min)       | 714   | 255   | 459    | 0      | 35.7%     | $-0.0    |
| Medium (5-15 min)      | 1465  | 579   | 886    | 0      | 39.5%     | $-0.1    |
| Slow (15-30 min)       | 826   | 296   | 530    | 0      | 35.8%     | $-0.0    |
| Very Fast (<1 min)     | 193   | 46    | 147    | 0      | 23.8%     | $-0.3    |
| Very Long (>1h)        | 1333  | 532   | 801    | 0      | 39.9%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.06 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (55.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (34.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.06) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.32) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (44.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2572s / 42.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_imbalance_momentum

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 1,756  |  **Win Rate:** 34.0%  |  **Avg P&L (resolved):** $-0.1  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 3653s (60.9m)  |  **Median Hold:** 1845s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 90    | 19    | 71     | 0      | 21.1%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 460   | 116   | 344    | 0      | 25.2%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 935   | 370   | 565    | 0      | 39.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 165   | 58    | 107    | 0      | 35.2%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 106   | 34    | 72     | 0      | 32.1%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1756  | 597   | 1159   | 0      | 34.0%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 513   | 164   | 349    | 0      | 32.0%     | $0.2     |
| Positive Gamma (Range-Bound friendly) | 1243  | 433   | 810    | 0      | 34.8%     | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 88    | 50    | 38     | 0      | 56.8%     | $1.4     |
| Time Held: 30-90m      | 485   | 176   | 309    | 0      | 36.3%     | $-0.1    |
| Time Held: 90-240m     | 317   | 115   | 202    | 0      | 36.3%     | $0.2     |
| Time Held: <30m        | 866   | 256   | 610    | 0      | 29.6%     | $-0.4    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 658   | 136   | 522    | 0      | 20.7%     | $-1.6    | 🔴          |
| Morning (10:00-12:00)  | 810   | 405   | 405    | 0      | 50.0%     | $1.5     | 🟢          |
| ORB (9:30-10:00)       | 288   | 56    | 232    | 0      | 19.4%     | $-1.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 288    | 29         | 213        | 46         | 10.1%     | 74.0%     | 16.0%     |
| Morning (10:00-12:00)  | 810    | 47         | 524        | 239        | 5.8%      | 64.7%     | 29.5%     |
| Afternoon (12:00-16:00) | 658    | 30         | 363        | 265        | 4.6%      | 55.2%     | 40.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 5      | 4     | 1      | 0      | 80.0%     | $4.8         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 41     | 8     | 33     | 0      | 19.5%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 193    | 38    | 155    | 0      | 19.7%     | $-1.2        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 20     | 4     | 16     | 0      | 20.0%     | $-1.2        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 29     | 2     | 27     | 0      | 6.9%      | $-1.7        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 37     | 9     | 28     | 0      | 24.3%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 202    | 72    | 130    | 0      | 35.6%     | $0.6         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 447    | 266   | 181    | 0      | 59.5%     | $2.1         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 77     | 35    | 42     | 0      | 45.5%     | $1.6         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 47     | 23    | 24     | 0      | 48.9%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 48     | 6     | 42     | 0      | 12.5%     | $-0.8        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 217    | 36    | 181    | 0      | 16.6%     | $-1.8        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 295    | 66    | 229    | 0      | 22.4%     | $-1.8        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 68     | 19    | 49     | 0      | 27.9%     | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 30     | 9     | 21     | 0      | 30.0%     | $-1.3        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 597   | 113   | 484    | 0      | 18.9%     | $-0.6    |
| SHORT        | 1159  | 484   | 675    | 0      | 41.8%     | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 246   | 36    | 210    | 0      | 14.6%     | $-1.4    |
| Long (30-60 min)       | 330   | 124   | 206    | 0      | 37.6%     | $0.4     |
| Medium (5-15 min)      | 280   | 63    | 217    | 0      | 22.5%     | $-0.8    |
| Slow (15-30 min)       | 327   | 156   | 171    | 0      | 47.7%     | $0.8     |
| Very Fast (<1 min)     | 13    | 1     | 12     | 0      | 7.7%      | $-0.9    |
| Very Long (>1h)        | 560   | 217   | 343    | 0      | 38.8%     | $-0.0    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 34.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.10 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (39.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (21.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.10) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.40) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (50.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3653s / 60.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_asymmetry

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 2,603  |  **Win Rate:** 14.5%  |  **Avg P&L (resolved):** $-1.1  |  **Avg P&L (all):** $-1.1  |  **Avg Hold:** 4929s (82.2m)  |  **Median Hold:** 2255s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 70-79%         | 42    | 13    | 29     | 0      | 31.0%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 2561  | 365   | 2196   | 0      | 14.3%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2603  | 378   | 2225   | 0      | 14.5%     | $-1.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2603  | 378   | 2225   | 0      | 14.5%     | $-1.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 242   | 43    | 199    | 0      | 17.8%     | $-0.6    |
| Time Held: 30-90m      | 502   | 77    | 425    | 0      | 15.3%     | $-1.5    |
| Time Held: 90-240m     | 648   | 70    | 578    | 0      | 10.8%     | $-1.3    |
| Time Held: <30m        | 1211  | 188   | 1023   | 0      | 15.5%     | $-1.0    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 980   | 86    | 894    | 0      | 8.8%      | $-1.8    | 🔴          |
| Morning (10:00-12:00)  | 1224  | 195   | 1029   | 0      | 15.9%     | $-0.9    | 🟢          |
| ORB (9:30-10:00)       | 399   | 97    | 302    | 0      | 24.3%     | $-0.1    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 399    | 399        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 1224   | 1224       | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 980    | 980        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 70-79%     | 15     | 12    | 3      | 0      | 80.0%     | $5.5         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 384    | 85    | 299    | 0      | 22.1%     | $-0.3        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 26     | 1     | 25     | 0      | 3.8%      | $-1.3        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 1198   | 194   | 1004   | 0      | 16.2%     | $-0.9        | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.1        | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 979    | 86    | 893    | 0      | 8.8%      | $-1.8        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1879  | 209   | 1670   | 0      | 11.1%     | $-1.0    |
| SHORT        | 724   | 169   | 555    | 0      | 23.3%     | $-1.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 273   | 20    | 253    | 0      | 7.3%      | $-1.6    |
| Long (30-60 min)       | 325   | 58    | 267    | 0      | 17.8%     | $-1.0    |
| Medium (5-15 min)      | 498   | 74    | 424    | 0      | 14.9%     | $-1.0    |
| Slow (15-30 min)       | 409   | 93    | 316    | 0      | 22.7%     | $-0.5    |
| Very Fast (<1 min)     | 31    | 1     | 30     | 0      | 3.2%      | $-1.9    |
| Very Long (>1h)        | 1067  | 132   | 935    | 0      | 12.4%     | $-1.3    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 14.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.12 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (31.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (14.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-1.12) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $-0.61) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (24.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4929s / 82.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_concentration

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 2,588  |  **Win Rate:** 34.0%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 1487s (24.8m)  |  **Median Hold:** 505s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 159   | 26    | 133    | 0      | 16.4%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 277   | 86    | 191    | 0      | 31.0%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 892   | 261   | 631    | 0      | 29.3%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 615   | 235   | 380    | 0      | 38.2%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 645   | 271   | 374    | 0      | 42.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2588  | 879   | 1709   | 0      | 34.0%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1082  | 368   | 714    | 0      | 34.0%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 1506  | 511   | 995    | 0      | 33.9%     | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 16    | 0     | 16     | 0      | 0.0%      | $-1.1    |
| Time Held: 30-90m      | 291   | 89    | 202    | 0      | 30.6%     | $-0.2    |
| Time Held: 90-240m     | 220   | 29    | 191    | 0      | 13.2%     | $-0.7    |
| Time Held: <30m        | 2061  | 761   | 1300   | 0      | 36.9%     | $-0.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 997   | 267   | 730    | 0      | 26.8%     | $-0.4    | 🔴          |
| Morning (10:00-12:00)  | 965   | 299   | 666    | 0      | 31.0%     | $-0.3    | 🔴          |
| ORB (9:30-10:00)       | 626   | 313   | 313    | 0      | 50.0%     | $0.4     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 626    | 0          | 371        | 255        | 0.0%      | 59.3%     | 40.7%     |
| Morning (10:00-12:00)  | 965    | 0          | 503        | 462        | 0.0%      | 52.1%     | 47.9%     |
| Afternoon (12:00-16:00) | 997    | 0          | 386        | 611        | 0.0%      | 38.7%     | 61.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 9      | 5     | 4      | 0      | 55.6%     | $0.2         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 46     | 25    | 21     | 0      | 54.3%     | $0.9         | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 200    | 66    | 134    | 0      | 33.0%     | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 164    | 95    | 69     | 0      | 57.9%     | $0.6         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 207    | 122   | 85     | 0      | 58.9%     | $0.7         | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 60     | 7     | 53     | 0      | 11.7%     | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 111    | 39    | 72     | 0      | 35.1%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 291    | 90    | 201    | 0      | 30.9%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 259    | 85    | 174    | 0      | 32.8%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 244    | 78    | 166    | 0      | 32.0%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 90     | 14    | 76     | 0      | 15.6%     | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 120    | 22    | 98     | 0      | 18.3%     | $-0.8        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 401    | 105   | 296    | 0      | 26.2%     | $-0.5        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 192    | 55    | 137    | 0      | 28.6%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 194    | 71    | 123    | 0      | 36.6%     | $0.1         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2162  | 635   | 1527   | 0      | 29.4%     | $-0.3    |
| SHORT        | 426   | 244   | 182    | 0      | 57.3%     | $0.5     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 759   | 303   | 456    | 0      | 39.9%     | $-0.0    |
| Long (30-60 min)       | 219   | 67    | 152    | 0      | 30.6%     | $-0.2    |
| Medium (5-15 min)      | 813   | 304   | 509    | 0      | 37.4%     | $-0.1    |
| Slow (15-30 min)       | 349   | 117   | 232    | 0      | 33.5%     | $-0.1    |
| Very Fast (<1 min)     | 140   | 37    | 103    | 0      | 26.4%     | $-0.4    |
| Very Long (>1h)        | 308   | 51    | 257    | 0      | 16.6%     | $-0.6    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 34.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.17 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (42.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (16.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.17) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-0.09) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: ORB (9:30-10:00) (50.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1487s / 24.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_imbalance

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 1,774  |  **Win Rate:** 31.4%  |  **Avg P&L (resolved):** $-0.1  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 1240s (20.7m)  |  **Median Hold:** 441s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 4     | 0     | 4      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 29    | 5     | 24     | 0      | 17.2%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 62    | 7     | 55     | 0      | 11.3%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 188   | 65    | 123    | 0      | 34.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 301   | 104   | 197    | 0      | 34.6%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 724   | 217   | 507    | 0      | 30.0%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 466   | 159   | 307    | 0      | 34.1%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1774  | 557   | 1217   | 0      | 31.4%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 827   | 241   | 586    | 0      | 29.1%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 947   | 316   | 631    | 0      | 33.4%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 2     | 0     | 2      | 0      | 0.0%      | $-1.0    |
| Time Held: 30-90m      | 191   | 70    | 121    | 0      | 36.6%     | $0.4     |
| Time Held: 90-240m     | 114   | 37    | 77     | 0      | 32.5%     | $0.6     |
| Time Held: <30m        | 1467  | 450   | 1017   | 0      | 30.7%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 605   | 176   | 429    | 0      | 29.1%     | $-0.2    | 🔴          |
| Morning (10:00-12:00)  | 658   | 198   | 460    | 0      | 30.1%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 511   | 183   | 328    | 0      | 35.8%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 511    | 372        | 108        | 31         | 72.8%     | 21.1%     | 6.1%      |
| Morning (10:00-12:00)  | 658    | 443        | 192        | 23         | 67.3%     | 29.2%     | 3.5%      |
| Afternoon (12:00-16:00) | 605    | 375        | 189        | 41         | 62.0%     | 31.2%     | 6.8%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 10     | 1     | 9      | 0      | 10.0%     | $-1.8        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 20     | 0     | 20     | 0      | 0.0%      | $-1.4        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 20     | 5     | 15     | 0      | 25.0%     | $-0.8        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 88     | 36    | 52     | 0      | 40.9%     | $0.3         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 198    | 68    | 130    | 0      | 34.3%     | $0.1         | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 174    | 73    | 101    | 0      | 42.0%     | $0.4         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 7      | 1     | 6      | 0      | 14.3%     | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 16     | 4     | 12     | 0      | 25.0%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 82     | 36    | 46     | 0      | 43.9%     | $0.7         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 110    | 43    | 67     | 0      | 39.1%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 282    | 70    | 212    | 0      | 24.8%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 161    | 44    | 117    | 0      | 27.3%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 3      | 0     | 3      | 0      | 0.0%      | $-0.8        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 12     | 3     | 9      | 0      | 25.0%     | $-0.2        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 26     | 3     | 23     | 0      | 11.5%     | $-0.8        | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 86     | 24    | 62     | 0      | 27.9%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 103    | 25    | 78     | 0      | 24.3%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 244    | 79    | 165    | 0      | 32.4%     | $-0.1        | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 131    | 42    | 89     | 0      | 32.1%     | $0.1         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1199  | 324   | 875    | 0      | 27.0%     | $-0.2    |
| SHORT        | 575   | 233   | 342    | 0      | 40.5%     | $0.1     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 593   | 149   | 444    | 0      | 25.1%     | $-0.4    |
| Long (30-60 min)       | 137   | 49    | 88     | 0      | 35.8%     | $0.3     |
| Medium (5-15 min)      | 544   | 205   | 339    | 0      | 37.7%     | $0.0     |
| Slow (15-30 min)       | 219   | 85    | 134    | 0      | 38.8%     | $0.3     |
| Very Fast (<1 min)     | 111   | 11    | 100    | 0      | 9.9%      | $-0.9    |
| Very Long (>1h)        | 170   | 58    | 112    | 0      | 34.1%     | $0.6     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.07 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (34.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (11.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.07) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.58) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (35.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1240s / 20.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_flip_breakout

**Symbols:** INTC, NVDA, TSLA  |  **Total Signals:** 1,933  |  **Win Rate:** 36.3%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 2975s (49.6m)  |  **Median Hold:** 1172s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 240   | 101   | 139    | 0      | 42.1%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 197   | 96    | 101    | 0      | 48.7%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 96    | 40    | 56     | 0      | 41.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 680   | 224   | 456    | 0      | 32.9%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 712   | 232   | 480    | 0      | 32.6%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 8     | 8     | 0      | 0      | 100.0%    | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1024  | 401   | 623    | 0      | 39.2%     | $-0.1    |
| Trending (Up)        | 909   | 300   | 609    | 0      | 33.0%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 51    | 35    | 16     | 0      | 68.6%     | $0.4     |
| Positive Gamma (Range-Bound friendly) | 1882  | 666   | 1216   | 0      | 35.4%     | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 40    | 0     | 40     | 0      | 0.0%      | $-2.4    |
| Time Held: 30-90m      | 451   | 92    | 359    | 0      | 20.4%     | $-0.3    |
| Time Held: 90-240m     | 288   | 208   | 80     | 0      | 72.2%     | $0.6     |
| Time Held: <30m        | 1154  | 401   | 753    | 0      | 34.7%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1066  | 288   | 778    | 0      | 27.0%     | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 867   | 413   | 454    | 0      | 47.6%     | $-0.3    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Morning (10:00-12:00)  | 867    | 8          | 448        | 411        | 0.9%      | 51.7%     | 47.4%     |
| Afternoon (12:00-16:00) | 1066   | 0          | 944        | 122        | 0.0%      | 88.6%     | 11.4%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Morning (10:00-12:00)  | 20-29%     | 170    | 61    | 109    | 0      | 35.9%     | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 177    | 80    | 97     | 0      | 45.2%     | $-1.0        | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 64     | 40    | 24     | 0      | 62.5%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 312    | 160   | 152    | 0      | 51.3%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 136    | 64    | 72     | 0      | 47.1%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 8      | 8     | 0      | 0      | 100.0%    | $1.9         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 70     | 40    | 30     | 0      | 57.1%     | $0.6         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 20     | 16    | 4      | 0      | 80.0%     | $0.7         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 32     | 0     | 32     | 0      | 0.0%      | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 368    | 64    | 304    | 0      | 17.4%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 576    | 168   | 408    | 0      | 29.2%     | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1024  | 120   | 904    | 0      | 11.7%     | $-0.8    |
| SHORT        | 909   | 581   | 328    | 0      | 63.9%     | $0.5     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 183   | 71    | 112    | 0      | 38.8%     | $-0.2    |
| Long (30-60 min)       | 250   | 45    | 205    | 0      | 18.0%     | $-0.4    |
| Medium (5-15 min)      | 484   | 190   | 294    | 0      | 39.3%     | $-0.0    |
| Slow (15-30 min)       | 402   | 65    | 337    | 0      | 16.2%     | $-0.5    |
| Very Fast (<1 min)     | 85    | 75    | 10     | 0      | 88.2%     | $0.0     |
| Very Long (>1h)        | 529   | 255   | 274    | 0      | 48.2%     | $0.1     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 36.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.16 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (32.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.14) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.61) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Morning (10:00-12:00) (47.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2975s / 49.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 1,792  |  **Win Rate:** 33.4%  |  **Avg P&L (resolved):** $0.4  |  **Avg P&L (all):** $0.4  |  **Avg Hold:** 1847s (30.8m)  |  **Median Hold:** 799s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 277   | 195   | 82     | 0      | 70.4%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 1050  | 358   | 692    | 0      | 34.1%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 457   | 46    | 411    | 0      | 10.1%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 8     | 0     | 8      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1073  | 372   | 701    | 0      | 34.7%     | $0.4     |
| Trending (Up)        | 719   | 227   | 492    | 0      | 31.6%     | $0.4     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 163   | 129   | 34     | 0      | 79.1%     | $2.3     |
| Positive Gamma (Range-Bound friendly) | 1629  | 470   | 1159   | 0      | 28.9%     | $0.2     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 345   | 131   | 214    | 0      | 38.0%     | $0.5     |
| Time Held: 90-240m     | 178   | 170   | 8      | 0      | 95.5%     | $4.7     |
| Time Held: <30m        | 1269  | 298   | 971    | 0      | 23.5%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 647   | 330   | 317    | 0      | 51.0%     | $1.5     | 🟢          |
| Morning (10:00-12:00)  | 830   | 129   | 701    | 0      | 15.5%     | $-0.7    | 🔴          |
| ORB (9:30-10:00)       | 315   | 140   | 175    | 0      | 44.4%     | $0.9     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 315    | 0          | 56         | 259        | 0.0%      | 17.8%     | 82.2%     |
| Morning (10:00-12:00)  | 830    | 0          | 338        | 492        | 0.0%      | 40.7%     | 59.3%     |
| Afternoon (12:00-16:00) | 647    | 0          | 71         | 576        | 0.0%      | 11.0%     | 89.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 49     | 35    | 14     | 0      | 71.4%     | $2.9         | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 210    | 81    | 129    | 0      | 38.6%     | $0.6         | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 56     | 24    | 32     | 0      | 42.9%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 93     | 33    | 60     | 0      | 35.5%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 399    | 82    | 317    | 0      | 20.6%     | $-0.7        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 330    | 14    | 316    | 0      | 4.2%      | $-0.8        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 8      | 0     | 8      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 135    | 127   | 8      | 0      | 94.1%     | $5.1         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 441    | 195   | 246    | 0      | 44.2%     | $0.8         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 71     | 8     | 63     | 0      | 11.3%     | $-0.8        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1627  | 470   | 1157   | 0      | 28.9%     | $0.2     |
| SHORT        | 165   | 129   | 36     | 0      | 78.2%     | $2.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 350   | 81    | 269    | 0      | 23.1%     | $-0.2    |
| Long (30-60 min)       | 248   | 81    | 167    | 0      | 32.7%     | $0.3     |
| Medium (5-15 min)      | 555   | 138   | 417    | 0      | 24.9%     | $-0.3    |
| Slow (15-30 min)       | 300   | 67    | 233    | 0      | 22.3%     | $-0.2    |
| Very Fast (<1 min)     | 64    | 12    | 52     | 0      | 18.8%     | $-0.6    |
| Very Long (>1h)        | 275   | 220   | 55     | 0      | 80.0%     | $3.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.39 — profitable even with 33.4% win rate (good risk/reward).
- 🎯 Best performance at 30-39% confidence (70.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.41) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $4.68) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (51.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1847s / 30.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_wall_bounce

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 2,127  |  **Win Rate:** 31.3%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 4002s (66.7m)  |  **Median Hold:** 2852s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 81    | 71    | 10     | 0      | 87.7%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 118   | 48    | 70     | 0      | 40.7%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 252   | 85    | 167    | 0      | 33.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 211   | 36    | 175    | 0      | 17.1%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 313   | 47    | 266    | 0      | 15.0%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 312   | 34    | 278    | 0      | 10.9%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 414   | 112   | 302    | 0      | 27.1%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 126   | 32    | 94     | 0      | 25.4%     | $0.0     | $0.0     | 0.0%     |
| 100%           | 300   | 200   | 100    | 0      | 66.7%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1203  | 354   | 849    | 0      | 29.4%     | $-0.4    |
| Trending (Up)        | 924   | 311   | 613    | 0      | 33.7%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 331   | 129   | 202    | 0      | 39.0%     | $0.4     |
| Positive Gamma (Range-Bound friendly) | 1796  | 536   | 1260   | 0      | 29.8%     | $-0.3    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 4     | 4     | 0      | 0      | 100.0%    | $4.1     |
| Time Held: 30-90m      | 789   | 148   | 641    | 0      | 18.8%     | $-0.7    |
| Time Held: 90-240m     | 598   | 344   | 254    | 0      | 57.5%     | $0.9     |
| Time Held: <30m        | 736   | 169   | 567    | 0      | 23.0%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 917   | 371   | 546    | 0      | 40.5%     | $-0.1    | 🟢          |
| Morning (10:00-12:00)  | 1122  | 257   | 865    | 0      | 22.9%     | $-0.4    | 🔴          |
| ORB (9:30-10:00)       | 88    | 37    | 51     | 0      | 42.0%     | $0.9     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 88     | 26         | 25         | 37         | 29.5%     | 28.4%     | 42.0%     |
| Morning (10:00-12:00)  | 1122   | 722        | 253        | 147        | 64.3%     | 22.5%     | 13.1%     |
| Afternoon (12:00-16:00) | 917    | 404        | 246        | 267        | 44.1%     | 26.8%     | 29.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 10     | 9     | 1      | 0      | 90.0%     | $2.5         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 1      | 1     | 0      | 0      | 100.0%    | $6.2         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 26     | 17    | 9      | 0      | 65.4%     | $2.8         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 13     | 4     | 9      | 0      | 30.8%     | $0.4         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 12     | 6     | 6      | 0      | 50.0%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 8      | 0     | 8      | 0      | 0.0%      | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 9      | 0     | 9      | 0      | 0.0%      | $-1.5        | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 6      | 0     | 6      | 0      | 0.0%      | $-1.5        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 3      | 0     | 3      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 32     | 23    | 9      | 0      | 71.9%     | $1.6         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 30     | 10    | 20     | 0      | 33.3%     | $-0.8        | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 85     | 33    | 52     | 0      | 38.8%     | $0.5         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 78     | 16    | 62     | 0      | 20.5%     | $-0.6        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 175    | 33    | 142    | 0      | 18.9%     | $-0.6        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 218    | 26    | 192    | 0      | 11.9%     | $-0.8        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 281    | 60    | 221    | 0      | 21.4%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 80     | 0     | 80     | 0      | 0.0%      | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 100%       | 143    | 56    | 87     | 0      | 39.2%     | $-0.0        | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 39     | 39    | 0      | 0      | 100.0%    | $4.8         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 87     | 37    | 50     | 0      | 42.5%     | $0.5         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 141    | 35    | 106    | 0      | 24.8%     | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 120    | 16    | 104    | 0      | 13.3%     | $-1.6        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 126    | 8     | 118    | 0      | 6.3%      | $-1.8        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 86     | 8     | 78     | 0      | 9.3%      | $-1.4        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 124    | 52    | 72     | 0      | 41.9%     | $0.3         | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 40     | 32    | 8      | 0      | 80.0%     | $1.2         | 🟢          |
| Afternoon (12:00-16:00) | 100%       | 154    | 144   | 10     | 0      | 93.5%     | $1.5         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 960   | 95    | 865    | 0      | 9.9%      | $-1.2    |
| SHORT        | 1167  | 570   | 597    | 0      | 48.8%     | $0.6     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 103   | 26    | 77     | 0      | 25.2%     | $-0.3    |
| Long (30-60 min)       | 518   | 86    | 432    | 0      | 16.6%     | $-0.8    |
| Medium (5-15 min)      | 266   | 55    | 211    | 0      | 20.7%     | $-1.0    |
| Slow (15-30 min)       | 352   | 88    | 264    | 0      | 25.0%     | $-0.3    |
| Very Fast (<1 min)     | 15    | 0     | 15     | 0      | 0.0%      | $-0.8    |
| Very Long (>1h)        | 873   | 410   | 463    | 0      | 47.0%     | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.21 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (87.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (10.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.01) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.86) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (42.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4002s / 66.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_divergence

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 2,794  |  **Win Rate:** 27.8%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.3  |  **Avg Hold:** 3120s (52.0m)  |  **Median Hold:** 1241s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 50-59%         | 59    | 10    | 49     | 0      | 16.9%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 1587  | 365   | 1222   | 0      | 23.0%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 1036  | 344   | 692    | 0      | 33.2%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 87    | 42    | 45     | 0      | 48.3%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 25    | 16    | 9      | 0      | 64.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2290  | 598   | 1692   | 0      | 26.1%     | $-0.3    |
| Trending (Up)        | 504   | 179   | 325    | 0      | 35.5%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 295   | 162   | 133    | 0      | 54.9%     | $0.5     |
| Positive Gamma (Range-Bound friendly) | 2499  | 615   | 1884   | 0      | 24.6%     | $-0.3    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 56    | 0     | 56     | 0      | 0.0%      | $-1.0    |
| Time Held: 30-90m      | 557   | 209   | 348    | 0      | 37.5%     | $0.4     |
| Time Held: 90-240m     | 642   | 77    | 565    | 0      | 12.0%     | $-0.6    |
| Time Held: <30m        | 1539  | 491   | 1048   | 0      | 31.9%     | $-0.3    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1354  | 403   | 951    | 0      | 29.8%     | $-0.0    | 🟢          |
| Morning (10:00-12:00)  | 1137  | 207   | 930    | 0      | 18.2%     | $-0.8    | 🔴          |
| ORB (9:30-10:00)       | 303   | 167   | 136    | 0      | 55.1%     | $0.7     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 303    | 132        | 171        | 0          | 43.6%     | 56.4%     | 0.0%      |
| Morning (10:00-12:00)  | 1137   | 556        | 581        | 0          | 48.9%     | 51.1%     | 0.0%      |
| Afternoon (12:00-16:00) | 1354   | 460        | 894        | 0          | 34.0%     | 66.0%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 50-59%     | 6      | 6     | 0      | 0      | 100.0%    | $3.3         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 165    | 77    | 88     | 0      | 46.7%     | $0.5         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 84     | 56    | 28     | 0      | 66.7%     | $1.0         | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 28     | 16    | 12     | 0      | 57.1%     | $0.9         | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 20     | 12    | 8      | 0      | 60.0%     | $0.3         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 24     | 2     | 22     | 0      | 8.3%      | $-1.6        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 557    | 82    | 475    | 0      | 14.7%     | $-0.8        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 525    | 115   | 410    | 0      | 21.9%     | $-0.7        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 31     | 8     | 23     | 0      | 25.8%     | $-0.7        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 29     | 2     | 27     | 0      | 6.9%      | $-1.9        | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 865    | 206   | 659    | 0      | 23.8%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 427    | 173   | 254    | 0      | 40.5%     | $0.4         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 28     | 18    | 10     | 0      | 64.3%     | $0.6         | ⚠️         |
| Afternoon (12:00-16:00) | 90-99%     | 5      | 4     | 1      | 0      | 80.0%     | $0.7         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2628  | 651   | 1977   | 0      | 24.8%     | $-0.4    |
| SHORT        | 166   | 126   | 40     | 0      | 75.9%     | $1.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 440   | 158   | 282    | 0      | 35.9%     | $-0.2    |
| Long (30-60 min)       | 378   | 148   | 230    | 0      | 39.2%     | $0.3     |
| Medium (5-15 min)      | 645   | 189   | 456    | 0      | 29.3%     | $-0.4    |
| Slow (15-30 min)       | 367   | 127   | 240    | 0      | 34.6%     | $-0.1    |
| Very Fast (<1 min)     | 87    | 17    | 70     | 0      | 19.5%     | $-0.5    |
| Very Long (>1h)        | 877   | 138   | 739    | 0      | 15.7%     | $-0.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 27.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.25 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 90-99% confidence (64.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (16.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.01) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.36) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (55.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3120s / 52.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_imbalance

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,822  |  **Win Rate:** 45.9%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 570s (9.5m)  |  **Median Hold:** 252s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 55    | 9     | 46     | 0      | 16.4%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 53    | 13    | 40     | 0      | 24.5%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 1945  | 904   | 1041   | 0      | 46.5%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 3039  | 1373  | 1666   | 0      | 45.2%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 720   | 372   | 348    | 0      | 51.7%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 10    | 2     | 8      | 0      | 20.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 3605  | 1641  | 1964   | 0      | 45.5%     | $0.0     |
| Trending (Up)        | 2217  | 1032  | 1185   | 0      | 46.5%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 7     | 1     | 6      | 0      | 14.3%     | $-1.0    |
| Positive Gamma (Range-Bound friendly) | 5815  | 2672  | 3143   | 0      | 46.0%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 12    | 12    | 0      | 0      | 100.0%    | $3.0     |
| Time Held: 30-90m      | 229   | 158   | 71     | 0      | 69.0%     | $0.4     |
| Time Held: 90-240m     | 60    | 46    | 14     | 0      | 76.7%     | $0.7     |
| Time Held: <30m        | 5521  | 2457  | 3064   | 0      | 44.5%     | $-0.0    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 3526  | 1587  | 1939   | 0      | 45.0%     | $-0.0    | 🔴          |
| Morning (10:00-12:00)  | 1749  | 917   | 832    | 0      | 52.4%     | $0.3     | 🟢          |
| ORB (9:30-10:00)       | 547   | 169   | 378    | 0      | 30.9%     | $-0.7    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 547    | 0          | 436        | 111        | 0.0%      | 79.7%     | 20.3%     |
| Morning (10:00-12:00)  | 1749   | 6          | 1008       | 735        | 0.3%      | 57.6%     | 42.0%     |
| Afternoon (12:00-16:00) | 3526   | 4          | 2315       | 1207       | 0.1%      | 65.7%     | 34.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 51     | 8     | 43     | 0      | 15.7%     | $-1.2        | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 20     | 1     | 19     | 0      | 5.0%      | $-1.4        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 40     | 12    | 28     | 0      | 30.0%     | $-2.2        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 360    | 104   | 256    | 0      | 28.9%     | $-0.6        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 76     | 44    | 32     | 0      | 57.9%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.6        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 33     | 12    | 21     | 0      | 36.4%     | $-0.1        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 701    | 404   | 297    | 0      | 57.6%     | $0.4         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 811    | 395   | 416    | 0      | 48.7%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 197    | 104   | 93     | 0      | 52.8%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 6      | 2     | 4      | 0      | 33.3%     | $-0.2        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 3      | 1     | 2      | 0      | 33.3%     | $-0.0        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 1204   | 488   | 716    | 0      | 40.5%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 1868   | 874   | 994    | 0      | 46.8%     | $0.0         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 447    | 224   | 223    | 0      | 50.1%     | $0.1         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 4      | 0     | 4      | 0      | 0.0%      | $-0.7        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3     | 1     | 2      | 0      | 33.3%     | $-0.0    |
| SHORT        | 5819  | 2672  | 3147   | 0      | 45.9%     | $0.0     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 2641  | 1094  | 1547   | 0      | 41.4%     | $-0.0    |
| Long (30-60 min)       | 167   | 102   | 65     | 0      | 61.1%     | $0.3     |
| Medium (5-15 min)      | 1767  | 955   | 812    | 0      | 54.0%     | $0.0     |
| Slow (15-30 min)       | 471   | 244   | 227    | 0      | 51.8%     | $0.2     |
| Very Fast (<1 min)     | 642   | 164   | 478    | 0      | 25.5%     | $-0.2    |
| Very Long (>1h)        | 134   | 114   | 20     | 0      | 85.1%     | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 45.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.01 — profitable even with 45.9% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (51.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (16.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.03) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $3.00) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (52.4% win rate) — statistically significant above overall WR.

---

### magnet_accelerate

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 4,518  |  **Win Rate:** 15.3%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 2603s (43.4m)  |  **Median Hold:** 1664s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 447   | 110   | 337    | 0      | 24.6%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 1028  | 180   | 848    | 0      | 17.5%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 1401  | 161   | 1240   | 0      | 11.5%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1106  | 161   | 945    | 0      | 14.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 481   | 67    | 414    | 0      | 13.9%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 55    | 10    | 45     | 0      | 18.2%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 2758  | 370   | 2388   | 0      | 13.4%     | $-0.2    |
| Trending (Up)        | 1760  | 319   | 1441   | 0      | 18.1%     | $-0.3    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 127   | 29    | 98     | 0      | 22.8%     | $-0.2    |
| Positive Gamma (Range-Bound friendly) | 4391  | 660   | 3731   | 0      | 15.0%     | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 54    | 0     | 54     | 0      | 0.0%      | $-1.3    |
| Time Held: 30-90m      | 1486  | 196   | 1290   | 0      | 13.2%     | $-0.4    |
| Time Held: 90-240m     | 560   | 180   | 380    | 0      | 32.1%     | $1.6     |
| Time Held: <30m        | 2418  | 313   | 2105   | 0      | 12.9%     | $-0.5    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 2774  | 492   | 2282   | 0      | 17.7%     | $0.1     | 🟢          |
| Morning (10:00-12:00)  | 1450  | 123   | 1327   | 0      | 8.5%      | $-0.9    | 🔴          |
| ORB (9:30-10:00)       | 294   | 74    | 220    | 0      | 25.2%     | $0.6     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 294    | 5          | 109        | 180        | 1.7%      | 37.1%     | 61.2%     |
| Morning (10:00-12:00)  | 1450   | 46         | 446        | 958        | 3.2%      | 30.8%     | 66.1%     |
| Afternoon (12:00-16:00) | 2774   | 4          | 1032       | 1738       | 0.1%      | 37.2%     | 62.7%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 84     | 16    | 68     | 0      | 19.0%     | $0.9         | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 60     | 20    | 40     | 0      | 33.3%     | $1.2         | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 36     | 5     | 31     | 0      | 13.9%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 69     | 28    | 41     | 0      | 40.6%     | $0.2         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 40     | 0     | 40     | 0      | 0.0%      | $0.7         | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 5      | 5     | 0      | 0      | 100.0%    | $0.4         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 133    | 6     | 127    | 0      | 4.5%      | $-1.3        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 364    | 26    | 338    | 0      | 7.1%      | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 461    | 34    | 427    | 0      | 7.4%      | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 345    | 27    | 318    | 0      | 7.8%      | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 101    | 27    | 74     | 0      | 26.7%     | $-0.4        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 46     | 3     | 43     | 0      | 6.5%      | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 230    | 88    | 142    | 0      | 38.3%     | $2.1         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 604    | 134   | 470    | 0      | 22.2%     | $0.6         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 904    | 122   | 782    | 0      | 13.5%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 692    | 106   | 586    | 0      | 15.3%     | $-0.5        | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 340    | 40    | 300    | 0      | 11.8%     | $-0.5        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 4      | 2     | 2      | 0      | 50.0%     | $0.5         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4280  | 545   | 3735   | 0      | 12.7%     | $-0.3    |
| SHORT        | 238   | 144   | 94     | 0      | 60.5%     | $0.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 606   | 85    | 521    | 0      | 14.0%     | $-0.6    |
| Long (30-60 min)       | 1030  | 150   | 880    | 0      | 14.6%     | $-0.4    |
| Medium (5-15 min)      | 975   | 116   | 859    | 0      | 11.9%     | $-0.5    |
| Slow (15-30 min)       | 684   | 89    | 595    | 0      | 13.0%     | $-0.5    |
| Very Fast (<1 min)     | 153   | 23    | 130    | 0      | 15.0%     | $-0.1    |
| Very Long (>1h)        | 1070  | 226   | 844    | 0      | 21.1%     | $0.6     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 15.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.23 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 20-29% confidence (24.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (11.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.21) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $1.62) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (25.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2603s / 43.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### order_book_fragmentation

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 6,905  |  **Win Rate:** 19.9%  |  **Avg P&L (resolved):** $-0.1  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 1661s (27.7m)  |  **Median Hold:** 670s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 37    | 8     | 29     | 0      | 21.6%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 853   | 194   | 659    | 0      | 22.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 2728  | 548   | 2180   | 0      | 20.1%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 1802  | 351   | 1451   | 0      | 19.5%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 1091  | 192   | 899    | 0      | 17.6%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 336   | 79    | 257    | 0      | 23.5%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 48    | 1     | 47     | 0      | 2.1%      | $0.0     | $0.0     | 0.0%     |
| 100%           | 10    | 0     | 10     | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 6905  | 1373  | 5532   | 0      | 19.9%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 6905  | 1373  | 5532   | 0      | 19.9%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 8     | 8     | 0      | 0      | 100.0%    | $1.9     |
| Time Held: 30-90m      | 1244  | 234   | 1010   | 0      | 18.8%     | $0.0     |
| Time Held: 90-240m     | 604   | 281   | 323    | 0      | 46.5%     | $0.9     |
| Time Held: <30m        | 5049  | 850   | 4199   | 0      | 16.8%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 3602  | 538   | 3064   | 0      | 14.9%     | $-0.3    | 🔴          |
| Morning (10:00-12:00)  | 2387  | 611   | 1776   | 0      | 25.6%     | $0.1     | 🟢          |
| ORB (9:30-10:00)       | 916   | 224   | 692    | 0      | 24.5%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 916    | 311        | 514        | 91         | 34.0%     | 56.1%     | 9.9%      |
| Morning (10:00-12:00)  | 2387   | 519        | 1560       | 308        | 21.7%     | 65.4%     | 12.9%     |
| Afternoon (12:00-16:00) | 3602   | 655        | 2456       | 491        | 18.2%     | 68.2%     | 13.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 4      | 0     | 4      | 0      | 0.0%      | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 87     | 13    | 74     | 0      | 14.9%     | $-0.3        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 287    | 62    | 225    | 0      | 21.6%     | $-0.2        | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 227    | 60    | 167    | 0      | 26.4%     | $0.3         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 210    | 51    | 159    | 0      | 24.3%     | $0.2         | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 76     | 38    | 38     | 0      | 50.0%     | $1.1         | 🟢          |
| ORB (9:30-10:00)       | 90-99%     | 21     | 0     | 21     | 0      | 0.0%      | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 4      | 0     | 4      | 0      | 0.0%      | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 6      | 0     | 6      | 0      | 0.0%      | $-1.0        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 302    | 106   | 196    | 0      | 35.1%     | $0.4         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 931    | 259   | 672    | 0      | 27.8%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 629    | 145   | 484    | 0      | 23.1%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 385    | 79    | 306    | 0      | 20.5%     | $-0.1        | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 118    | 22    | 96     | 0      | 18.6%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 16     | 0     | 16     | 0      | 0.0%      | $-0.7        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 27     | 8     | 19     | 0      | 29.6%     | $-0.0        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 464    | 75    | 389    | 0      | 16.2%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 1510   | 227   | 1283   | 0      | 15.0%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 946    | 146   | 800    | 0      | 15.4%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 496    | 62    | 434    | 0      | 12.5%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 142    | 19    | 123    | 0      | 13.4%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 11     | 1     | 10     | 0      | 9.1%      | $-0.4        | ⚠️         |
| Afternoon (12:00-16:00) | 100%       | 6      | 0     | 6      | 0      | 0.0%      | $-0.5        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4250  | 554   | 3696   | 0      | 13.0%     | $-0.3    |
| SHORT        | 2655  | 819   | 1836   | 0      | 30.8%     | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 1628  | 213   | 1415   | 0      | 13.1%     | $-0.4    |
| Long (30-60 min)       | 870   | 168   | 702    | 0      | 19.3%     | $-0.0    |
| Medium (5-15 min)      | 1772  | 387   | 1385   | 0      | 21.8%     | $-0.2    |
| Slow (15-30 min)       | 1079  | 212   | 867    | 0      | 19.6%     | $-0.0    |
| Very Fast (<1 min)     | 570   | 38    | 532    | 0      | 6.7%      | $-0.5    |
| Very Long (>1h)        | 986   | 355   | 631    | 0      | 36.0%     | $0.6     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 19.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.10 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (23.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 100% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.10) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.89) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (25.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1661s / 27.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_divergence_scalper

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 7,670  |  **Win Rate:** 38.1%  |  **Avg P&L (resolved):** $-0.0  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 1297s (21.6m)  |  **Median Hold:** 518s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 628   | 259   | 369    | 0      | 41.2%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 2338  | 1061  | 1277   | 0      | 45.4%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 3185  | 1050  | 2135   | 0      | 33.0%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1400  | 486   | 914    | 0      | 34.7%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 119   | 65    | 54     | 0      | 54.6%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 7670  | 2921  | 4749   | 0      | 38.1%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 2087  | 853   | 1234   | 0      | 40.9%     | $0.1     |
| Positive Gamma (Range-Bound friendly) | 5583  | 2068  | 3515   | 0      | 37.0%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1399  | 574   | 825    | 0      | 41.0%     | $0.1     |
| Time Held: 90-240m     | 420   | 279   | 141    | 0      | 66.4%     | $0.5     |
| Time Held: <30m        | 5851  | 2068  | 3783   | 0      | 35.3%     | $-0.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 4303  | 1642  | 2661   | 0      | 38.2%     | $-0.0    | 🟢          |
| Morning (10:00-12:00)  | 2365  | 959   | 1406   | 0      | 40.5%     | $0.0     | 🟢          |
| ORB (9:30-10:00)       | 1002  | 320   | 682    | 0      | 31.9%     | $-0.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 1002   | 0          | 238        | 764        | 0.0%      | 23.8%     | 76.2%     |
| Morning (10:00-12:00)  | 2365   | 0          | 453        | 1912       | 0.0%      | 19.2%     | 80.8%     |
| Afternoon (12:00-16:00) | 4303   | 0          | 828        | 3475       | 0.0%      | 19.2%     | 80.8%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 51     | 9     | 42     | 0      | 17.6%     | $-0.4        | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 325    | 107   | 218    | 0      | 32.9%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 388    | 121   | 267    | 0      | 31.2%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 216    | 67    | 149    | 0      | 31.0%     | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 22     | 16    | 6      | 0      | 72.7%     | $0.5         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 192    | 77    | 115    | 0      | 40.1%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 683    | 354   | 329    | 0      | 51.8%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 1037   | 388   | 649    | 0      | 37.4%     | $-0.0        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 401    | 128   | 273    | 0      | 31.9%     | $-0.1        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 52     | 12    | 40     | 0      | 23.1%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 385    | 173   | 212    | 0      | 44.9%     | $-0.1        | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 1330   | 600   | 730    | 0      | 45.1%     | $0.0         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 1760   | 541   | 1219   | 0      | 30.7%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 783    | 291   | 492    | 0      | 37.2%     | $-0.0        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 45     | 37    | 8      | 0      | 82.2%     | $0.7         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4415  | 1147  | 3268   | 0      | 26.0%     | $-0.2    |
| SHORT        | 3255  | 1774  | 1481   | 0      | 54.5%     | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 2075  | 780   | 1295   | 0      | 37.6%     | $-0.1    |
| Long (30-60 min)       | 1024  | 374   | 650    | 0      | 36.5%     | $-0.0    |
| Medium (5-15 min)      | 1993  | 745   | 1248   | 0      | 37.4%     | $-0.0    |
| Slow (15-30 min)       | 1039  | 364   | 675    | 0      | 35.0%     | $-0.1    |
| Very Fast (<1 min)     | 744   | 179   | 565    | 0      | 24.1%     | $-0.3    |
| Very Long (>1h)        | 795   | 479   | 316    | 0      | 60.3%     | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 38.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.03 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 60-69% confidence (54.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (33.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.03) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.46) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Morning (10:00-12:00) (40.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1297s / 21.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### participant_diversity_conviction

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 4,310  |  **Win Rate:** 26.2%  |  **Avg P&L (resolved):** $-0.4  |  **Avg P&L (all):** $-0.4  |  **Avg Hold:** 4394s (73.2m)  |  **Median Hold:** 2199s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 664   | 222   | 442    | 0      | 33.4%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 1555  | 409   | 1146   | 0      | 26.3%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1438  | 382   | 1056   | 0      | 26.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 426   | 91    | 335    | 0      | 21.4%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 201   | 27    | 174    | 0      | 13.4%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 26    | 0     | 26     | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 4310  | 1131  | 3179   | 0      | 26.2%     | $-0.4    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1663  | 471   | 1192   | 0      | 28.3%     | $-0.1    |
| Positive Gamma (Range-Bound friendly) | 2647  | 660   | 1987   | 0      | 24.9%     | $-0.6    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 226   | 57    | 169    | 0      | 25.2%     | $-0.4    |
| Time Held: 30-90m      | 998   | 284   | 714    | 0      | 28.5%     | $-0.6    |
| Time Held: 90-240m     | 1115  | 294   | 821    | 0      | 26.4%     | $0.0     |
| Time Held: <30m        | 1971  | 496   | 1475   | 0      | 25.2%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 1837  | 401   | 1436   | 0      | 21.8%     | $-0.9    | 🔴          |
| Morning (10:00-12:00)  | 1963  | 528   | 1435   | 0      | 26.9%     | $-0.2    | 🟢          |
| ORB (9:30-10:00)       | 510   | 202   | 308    | 0      | 39.6%     | $0.6     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 510    | 18         | 142        | 350        | 3.5%      | 27.8%     | 68.6%     |
| Morning (10:00-12:00)  | 1963   | 130        | 898        | 935        | 6.6%      | 45.7%     | 47.6%     |
| Afternoon (12:00-16:00) | 1837   | 79         | 824        | 934        | 4.3%      | 44.9%     | 50.8%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 146    | 67    | 79     | 0      | 45.9%     | $0.7         | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 204    | 79    | 125    | 0      | 38.7%     | $0.9         | 🟢          |
| ORB (9:30-10:00)       | 50-59%     | 112    | 43    | 69     | 0      | 38.4%     | $0.6         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 30     | 13    | 17     | 0      | 43.3%     | $0.1         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 18     | 0     | 18     | 0      | 0.0%      | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 291    | 143   | 148    | 0      | 49.1%     | $1.8         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 644    | 211   | 433    | 0      | 32.8%     | $0.0         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 668    | 126   | 542    | 0      | 18.9%     | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 230    | 34    | 196    | 0      | 14.8%     | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 106    | 14    | 92     | 0      | 13.2%     | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 24     | 0     | 24     | 0      | 0.0%      | $-1.7        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 227    | 12    | 215    | 0      | 5.3%      | $-3.1        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 707    | 119   | 588    | 0      | 16.8%     | $-1.4        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 658    | 213   | 445    | 0      | 32.4%     | $0.1         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 166    | 44    | 122    | 0      | 26.5%     | $-0.3        | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 77     | 13    | 64     | 0      | 16.9%     | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.2        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2971  | 520   | 2451   | 0      | 17.5%     | $-0.8    |
| SHORT        | 1339  | 611   | 728    | 0      | 45.6%     | $0.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 393   | 67    | 326    | 0      | 17.0%     | $-1.1    |
| Long (30-60 min)       | 684   | 180   | 504    | 0      | 26.3%     | $-0.6    |
| Medium (5-15 min)      | 768   | 156   | 612    | 0      | 20.3%     | $-0.9    |
| Slow (15-30 min)       | 772   | 268   | 504    | 0      | 34.7%     | $-0.0    |
| Very Fast (<1 min)     | 38    | 5     | 33     | 0      | 13.2%     | $-0.9    |
| Very Long (>1h)        | 1655  | 455   | 1200   | 0      | 27.5%     | $-0.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 26.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.42 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (33.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.42) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.05) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (39.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (4394s / 73.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### prob_weighted_magnet

**Symbols:** AMD, INTC, NVDA, SPCX, TSLA  |  **Total Signals:** 9,181  |  **Win Rate:** 17.4%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.3  |  **Avg Hold:** 3097s (51.6m)  |  **Median Hold:** 1490s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 2413  | 559   | 1854   | 0      | 23.2%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 6702  | 990   | 5712   | 0      | 14.8%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 66    | 48    | 18     | 0      | 72.7%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 5751  | 960   | 4791   | 0      | 16.7%     | $-0.4    |
| Trending (Up)        | 3430  | 637   | 2793   | 0      | 18.6%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 9181  | 1597  | 7584   | 0      | 17.4%     | $-0.3    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 204   | 56    | 148    | 0      | 27.5%     | $0.2     |
| Time Held: 30-90m      | 2299  | 394   | 1905   | 0      | 17.1%     | $-0.5    |
| Time Held: 90-240m     | 1729  | 405   | 1324   | 0      | 23.4%     | $0.6     |
| Time Held: <30m        | 4949  | 742   | 4207   | 0      | 15.0%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 4406  | 582   | 3824   | 0      | 13.2%     | $-0.6    | 🔴          |
| Morning (10:00-12:00)  | 3680  | 755   | 2925   | 0      | 20.5%     | $-0.1    | 🟢          |
| ORB (9:30-10:00)       | 1095  | 260   | 835    | 0      | 23.7%     | $0.2     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 1095   | 0          | 0          | 1095       | 0.0%      | 0.0%      | 100.0%    |
| Morning (10:00-12:00)  | 3680   | 0          | 66         | 3614       | 0.0%      | 1.8%      | 98.2%     |
| Afternoon (12:00-16:00) | 4406   | 0          | 0          | 4406       | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 495    | 100   | 395    | 0      | 20.2%     | $-0.3        | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 600    | 160   | 440    | 0      | 26.7%     | $0.6         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 839    | 184   | 655    | 0      | 21.9%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 2775   | 523   | 2252   | 0      | 18.8%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 66     | 48    | 18     | 0      | 72.7%     | $2.0         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 1079   | 275   | 804    | 0      | 25.5%     | $-0.2        | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 3327   | 307   | 3020   | 0      | 9.2%      | $-0.7        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 6019  | 680   | 5339   | 0      | 11.3%     | $-0.5    |
| SHORT        | 3162  | 917   | 2245   | 0      | 29.0%     | $0.1     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 1396  | 121   | 1275   | 0      | 8.7%      | $-0.8    |
| Long (30-60 min)       | 1515  | 276   | 1239   | 0      | 18.2%     | $-0.4    |
| Medium (5-15 min)      | 1885  | 230   | 1655   | 0      | 12.2%     | $-0.8    |
| Slow (15-30 min)       | 1447  | 390   | 1057   | 0      | 27.0%     | $0.0     |
| Very Fast (<1 min)     | 221   | 1     | 220    | 0      | 0.5%      | $-1.2    |
| Very Long (>1h)        | 2717  | 579   | 2138   | 0      | 21.3%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 17.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.30 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (72.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (14.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.20) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.62) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: ORB (9:30-10:00) (23.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3097s / 51.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### strike_concentration

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 842  |  **Win Rate:** 48.2%  |  **Avg P&L (resolved):** $0.4  |  **Avg P&L (all):** $0.4  |  **Avg Hold:** 3108s (51.8m)  |  **Median Hold:** 1703s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 4     | 4     | 0      | 0      | 100.0%    | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 54    | 38    | 16     | 0      | 70.4%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 92    | 82    | 10     | 0      | 89.1%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 322   | 130   | 192    | 0      | 40.4%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 346   | 140   | 206    | 0      | 40.5%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 24    | 12    | 12     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 548   | 294   | 254    | 0      | 53.6%     | $0.3     |
| Trending (Up)        | 294   | 112   | 182    | 0      | 38.1%     | $0.5     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 842   | 406   | 436    | 0      | 48.2%     | $0.4     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 234   | 64    | 170    | 0      | 27.4%     | $-0.3    |
| Time Held: 90-240m     | 168   | 168   | 0      | 0      | 100.0%    | $2.1     |
| Time Held: <30m        | 440   | 174   | 266    | 0      | 39.5%     | $0.1     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 276   | 216   | 60     | 0      | 78.3%     | $1.3     | 🟢          |
| Morning (10:00-12:00)  | 506   | 154   | 352    | 0      | 30.4%     | $-0.2    | 🔴          |
| ORB (9:30-10:00)       | 60    | 36    | 24     | 0      | 60.0%     | $1.6     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 60     | 4          | 40         | 16         | 6.7%      | 66.7%     | 26.7%     |
| Morning (10:00-12:00)  | 506    | 6          | 468        | 32         | 1.2%      | 92.5%     | 6.3%      |
| Afternoon (12:00-16:00) | 276    | 14         | 160        | 102        | 5.1%      | 58.0%     | 37.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 30-39%     | 4      | 4     | 0      | 0      | 100.0%    | $3.5         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 12     | 12    | 0      | 0      | 100.0%    | $4.0         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 28     | 12    | 16     | 0      | 42.9%     | $1.4         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 12     | 4     | 8      | 0      | 33.3%     | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 4      | 4     | 0      | 0      | 100.0%    | $0.8         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 4      | 0     | 4      | 0      | 0.0%      | $-3.7        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 28     | 18    | 10     | 0      | 64.3%     | $1.6         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 188    | 32    | 156    | 0      | 17.0%     | $-0.6        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 280    | 100   | 180    | 0      | 35.7%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 6      | 4     | 2      | 0      | 66.7%     | $0.4         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 4      | 4     | 0      | 0      | 100.0%    | $1.8         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 46     | 34    | 12     | 0      | 73.9%     | $2.5         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 52     | 52    | 0      | 0      | 100.0%    | $2.4         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 106    | 86    | 20     | 0      | 81.1%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 54     | 36    | 18     | 0      | 66.7%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 14     | 4     | 10     | 0      | 28.6%     | $-0.1        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 290   | 126   | 164    | 0      | 43.4%     | $0.8     |
| SHORT        | 552   | 280   | 272    | 0      | 50.7%     | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 54    | 24    | 30     | 0      | 44.4%     | $0.7     |
| Long (30-60 min)       | 172   | 18    | 154    | 0      | 10.5%     | $-0.8    |
| Medium (5-15 min)      | 166   | 76    | 90     | 0      | 45.8%     | $0.2     |
| Slow (15-30 min)       | 186   | 56    | 130    | 0      | 30.1%     | $-0.2    |
| Very Fast (<1 min)     | 34    | 18    | 16     | 0      | 52.9%     | $0.2     |
| Very Long (>1h)        | 230   | 214   | 16     | 0      | 93.0%     | $1.8     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 48.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.39 — profitable even with 48.2% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (89.1% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (40.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.48) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $2.07) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (78.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3108s / 51.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### theta_burn

**Symbols:** TSLA  |  **Total Signals:** 12  |  **Win Rate:** 0.0%  |  **Avg P&L (resolved):** $0.2  |  **Avg P&L (all):** $0.2  |  **Avg Hold:** 97s (1.6m)  |  **Median Hold:** 1s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 8     | 0     | 8      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 4     | 0     | 4      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 8     | 0     | 8      | 0      | 0.0%      | $0.1     |
| Trending (Up)        | 4     | 0     | 4      | 0      | 0.0%      | $0.4     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 12    | 0     | 12     | 0      | 0.0%      | $0.2     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: <30m        | 12    | 0     | 12     | 0      | 0.0%      | $0.2     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 12    | 0     | 12     | 0      | 0.0%      | $0.2     | ⚠️         |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Afternoon (12:00-16:00) | 12     | 0          | 0          | 12         | 0.0%      | 0.0%      | 100.0%    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| SHORT        | 12    | 0     | 12     | 0      | 0.0%      | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 2     | 0     | 2      | 0      | 0.0%      | $-0.7    |
| Medium (5-15 min)      | 2     | 0     | 2      | 0      | 0.0%      | $-0.5    |
| Very Fast (<1 min)     | 8     | 0     | 8      | 0      | 0.0%      | $0.6     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 0.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.21 — profitable even with 0.0% win rate (good risk/reward).
- 🎯 Best performance at 20-29% confidence (0.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.10) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.21) — optimal time held is Time Held: <30m.
- ⚠️ Best signal generation window: Afternoon (12:00-16:00) (0.0% win rate) — but only 12 signals, results may not be statistically significant.

---

### vol_compression_range

**Symbols:** AMD, INTC, NVDA, TSLA  |  **Total Signals:** 563  |  **Win Rate:** 43.7%  |  **Avg P&L (resolved):** $0.3  |  **Avg P&L (all):** $0.3  |  **Avg Hold:** 5005s (83.4m)  |  **Median Hold:** 3356s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 52    | 15    | 37     | 0      | 28.8%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 116   | 56    | 60     | 0      | 48.3%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 95    | 29    | 66     | 0      | 30.5%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 168   | 84    | 84     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 116   | 54    | 62     | 0      | 46.6%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 16    | 8     | 8      | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 312   | 120   | 192    | 0      | 38.5%     | $0.1     |
| Trending (Up)        | 251   | 126   | 125    | 0      | 50.2%     | $0.6     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 563   | 246   | 317    | 0      | 43.7%     | $0.3     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 26    | 26    | 0      | 0      | 100.0%    | $2.1     |
| Time Held: 30-90m      | 126   | 49    | 77     | 0      | 38.9%     | $0.5     |
| Time Held: 90-240m     | 185   | 120   | 65     | 0      | 64.9%     | $1.3     |
| Time Held: <30m        | 226   | 51    | 175    | 0      | 22.6%     | $-0.8    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 188   | 119   | 69     | 0      | 63.3%     | $1.4     | 🟢          |
| Morning (10:00-12:00)  | 307   | 107   | 200    | 0      | 34.9%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 68    | 20    | 48     | 0      | 29.4%     | $-0.8    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each regular hours session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| ORB (9:30-10:00)       | 68     | 0          | 0          | 68         | 0.0%      | 0.0%      | 100.0%    |
| Morning (10:00-12:00)  | 307    | 16         | 174        | 117        | 5.2%      | 56.7%     | 38.1%     |
| Afternoon (12:00-16:00) | 188    | 0          | 110        | 78         | 0.0%      | 58.5%     | 41.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| ORB (9:30-10:00)       | 20-29%     | 16     | 0     | 16     | 0      | 0.0%      | $-1.8        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 28     | 16    | 12     | 0      | 57.1%     | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 24     | 4     | 20     | 0      | 16.7%     | $-1.1        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 27     | 8     | 19     | 0      | 29.6%     | $-0.7        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 54     | 21    | 33     | 0      | 38.9%     | $0.3         | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 36     | 10    | 26     | 0      | 27.8%     | $-0.7        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 110    | 44    | 66     | 0      | 40.0%     | $0.2         | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 64     | 16    | 48     | 0      | 25.0%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 16     | 8     | 8      | 0      | 50.0%     | $0.3         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 9      | 7     | 2      | 0      | 77.8%     | $4.4         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 34     | 19    | 15     | 0      | 55.9%     | $2.7         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 35     | 15    | 20     | 0      | 42.9%     | $0.4         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 58     | 40    | 18     | 0      | 69.0%     | $1.2         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 52     | 38    | 14     | 0      | 73.1%     | $1.1         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 304   | 53    | 251    | 0      | 17.4%     | $-0.9    |
| SHORT        | 259   | 193   | 66     | 0      | 74.5%     | $1.7     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 68    | 16    | 52     | 0      | 23.5%     | $-0.9    |
| Long (30-60 min)       | 60    | 32    | 28     | 0      | 53.3%     | $1.7     |
| Medium (5-15 min)      | 93    | 22    | 71     | 0      | 23.7%     | $-0.9    |
| Slow (15-30 min)       | 65    | 13    | 52     | 0      | 20.0%     | $-0.6    |
| Very Long (>1h)        | 277   | 163   | 114    | 0      | 58.8%     | $0.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 43.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.33 — profitable even with 43.7% win rate (good risk/reward).
- 🎯 Best performance at 50-59% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (28.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.56) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $2.08) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (63.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (5005s / 83.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

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
| 1782137925.921 | 132    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 17           | Velocity-Magnet LONG: delta accelerating at 400... |
| 1782144919.389 | 92     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 16           | Magnet pull LONG: price 540.78 below magnet 550... |
| 1782137076.639 | 182    | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Participant conviction SHORT: participants=2.4,... |
| 1782137136.009 | 166    | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Gamma squeeze: price approaching call wall at 4... |
| 1782137863.188 | 134    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Call flow dominant (ratio=26.4×): call score 70... |
| 1782144131.287 | 66     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | Put wall at 407.5 supported price, GEX=1954360,... |
| 1782151603.964 | 68     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 15           | UP trend exhausted: delta declining (below avg)... |
| 1782132643.716 | 112    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 14           | DOWN trend exhausted: delta declining (below av... |
| 1782137009.913 | 98     | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | UP trend exhausted: delta declining (below avg)... |
| 1782138107.881 | 108    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | Velocity-Magnet LONG: delta accelerating at 400... |
| 1782138363.6   | 64     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, vol_compression_range | 14           | GEX call-heavy: call/put ratio=192.309, call_ge... |
| 1782142490.401 | 60     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 14           | Participant conviction LONG: participants=1.6, ... |
| 1782142975.958 | 84     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 14           | Flow imbalance SHORT: AggVSI=-0.960 (+96.0%), R... |
| 1782115196.881 | 520    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Call flow dominant (ratio=1.3×): call score 364... |
| 1782117607.337 | 140    | call_put_flow_asymmetry, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | Participant conviction SHORT: participants=1.4,... |
| 1782124920.341 | 100    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, vol_compression_range | 13           | Put wall at 392.5 supported price, GEX=619129, ... |
| 1782125559.578 | 104    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | ROBUST_LONG LONG: frag_bid=0.160 frag_ask=0.200... |
| 1782128288.208 | 104    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | ROBUST_LONG LONG: frag=0.150/0.121 decay=-0.711... |
| 1782131627.586 | 148    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 13           | ROBUST_SHORT SHORT: frag=0.167/0.167 decay=+0.0... |
| 1782135080.731 | 136    | delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration, vol_compression_range | 13           | Magnet pull LONG: price 548.22 below magnet 550... |
| 1782137020.152 | 134    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet | 13           | Velocity-Magnet LONG: delta accelerating at 550... |
| 1782137192.598 | 110    | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 13           | Squeeze LONG: breakout through call wall at 552... |
| 1782137806.19  | 118    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Velocity-Magnet LONG: delta accelerating at 535... |
| 1782141875.582 | 76     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Depth decay SHORT: ROC=-0.1612 (-16.12%), vol/d... |
| 1782141954.193 | 52     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | MEMX accumulation LONG: ESI=1.000 (+100.0%), de... |
| 1782142195.165 | 32     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet | 13           | Depth imbalance SHORT: IR=0.60 (+40.3%), ROC=-0... |
| 1782142258.918 | 34     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | ROBUST_LONG LONG: frag=0.078/0.065 decay=-0.012... |
| 1782144672.963 | 52     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 13           | Magnet pull LONG: price 540.50 below magnet 550... |
| 1782144978.628 | 62     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Magnet pull LONG: price 407.83 below magnet 415... |
| 1782145095.411 | 52     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_squeeze, gex_imbalance, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration, vol_compression_range | 13           | UP trend exhausted: delta declining (below avg)... |
| 1782145222.287 | 58     | call_put_flow_asymmetry, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 13           | UP trend exhausted: delta declining (below avg)... |
| 1782213244.723 | 23     | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | Velocity-Magnet LONG: delta accelerating at 500... |
| 1782227847.814 | 17     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_squeeze, gex_divergence, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, vol_compression_range | 13           | Participant conviction SHORT: participants=3.6,... |
| 1782235718.48  | 13     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 13           | DOWN trend exhausted: delta declining (below av... |
| 1782118027.585 | 140    | call_put_flow_asymmetry, confluence_reversal, delta_gamma_squeeze, depth_decay_momentum, depth_imbalance_momentum, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 12           | ROBUST_LONG LONG: frag=0.138/0.212 decay=-0.425... |
| 1782118779.323 | 116    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, strike_concentration | 12           | Confluence LONG at 178: 1 structural signals, t... |
| 1782120166.531 | 128    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, strike_concentration | 12           | Confluence SHORT at 400: 2 structural signals, ... |
| 1782120222.262 | 116    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 12           | Magnet pull SHORT: price 395.16 above magnet 39... |
| 1782121125.563 | 92     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction | 12           | Participant conviction LONG: participants=1.0, ... |
| 1782121679.72  | 168    | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 12           | ROBUST_LONG LONG: frag_bid=0.129 frag_ask=0.150... |
| 1782121982.715 | 108    | call_put_flow_asymmetry, confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction | 12           | Confluence LONG at 139: 1 structural signals, t... |
| 1782122388.144 | 120    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 12           | Participant conviction LONG: participants=1.4, ... |
| 1782122916.242 | 76     | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, gex_imbalance, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 12           | Depth imbalance SHORT: IR=0.25 (+75.1%), ROC=-0... |
| 1782123037.259 | 108    | call_put_flow_asymmetry, confluence_reversal, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 12           | Strike bounce SHORT: 210.0 Call strike, rank #2... |
| 1782123430.801 | 132    | call_put_flow_asymmetry, confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, order_book_fragmentation, participant_divergence_scalper, prob_weighted_magnet, vol_compression_range | 12           | Velocity-Magnet SHORT: delta accelerating at 40... |
| 1782123954.191 | 108    | confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, participant_diversity_conviction, strike_concentration | 12           | Participant conviction LONG: participants=1.8, ... |
| 1782124794.483 | 96     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_imbalance, magnet_accelerate, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 12           | ROBUST_LONG LONG: frag=0.133/0.180 decay=-0.387... |
| 1782126287.712 | 108    | call_put_flow_asymmetry, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 12           | GEX divergence (bullish): price falling but GEX... |
| 1782126408.295 | 104    | call_put_flow_asymmetry, confluence_reversal, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet, strike_concentration | 12           | ROBUST_SHORT SHORT: frag=0.129/0.150 decay=+0.0... |
| 1782126706.439 | 92     | call_put_flow_asymmetry, confluence_reversal, delta_volume_exhaustion, depth_decay_momentum, exchange_flow_imbalance, gex_divergence, gex_imbalance, magnet_accelerate, order_book_fragmentation, participant_divergence_scalper, participant_diversity_conviction, prob_weighted_magnet | 12           | Participant conviction LONG: participants=13.2,... |

**8721 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 34,372   | 12         | net_gamma=< 480.37     | 21.8%    | $0.4       |
| Volume Spike                 | 11,599   | 2          | vol_ratio=0.5          | 31.4%    | $-0.0      |
| Gamma Wall Support (405.0)   | 1,095    | 4          | wall_strike=405.0      | 40.8%    | $0.0       |
| Gamma Wall Support (210.0)   | 651      | 4          | wall_strike=210.0      | 24.1%    | $-0.4      |
| Gamma Wall Support (537.5)   | 586      | 4          | wall_strike=537.5      | 63.0%    | $2.7       |
| Gamma Wall Support (134.0)   | 580      | 4          | wall_strike=134.0      | 37.8%    | $0.1       |
| Gamma Wall Support (382.5)   | 90       | 3          | wall_strike=382.5      | 3.3%     | $-0.1      |
| Gamma Wall Support (170.0)   | 58       | 2          | wall_strike=170.0      | 19.0%    | $-0.7      |
| Gamma Wall Support (507.5)   | 31       | 2          | wall_strike=507.5      | 6.5%     | $-2.2      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 16901  | 9      | 9        | 22.5%    | $0.9       | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 9598   | 8      | 8        | 15.6%    | $0.3       | net_gamma  | call_put_flow_asymmetry, delta_gamma_sq  |
| Gamma Exposur  | 4977   | 6      | 6        | 29.8%    | $-0.6      | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Exposur  | 2896   | 5      | 5        | 24.7%    | $-0.9      | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 586    | 4      | 4        | 63.0%    | $2.7       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 1095   | 4      | 4        | 40.8%    | $0.0       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 580    | 4      | 4        | 37.8%    | $0.1       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 651    | 4      | 4        | 24.1%    | $-0.4      | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 90     | 3      | 3        | 3.3%     | $-0.1      | wall_stri  | gamma_squeeze, gamma_wall_bounce, theta  |
| Volume Spike   | 11599  | 2      | 2        | 31.4%    | $-0.0      | vol_ratio  | order_book_fragmentation, participant_d  |
| Gamma Wall Su  | 58     | 2      | 2        | 19.0%    | $-0.7      | wall_stri  | gamma_squeeze, gamma_wall_bounce         |
| Gamma Wall Su  | 31     | 2      | 2        | 6.5%     | $-2.2      | wall_stri  | gamma_squeeze, gamma_wall_bounce         |

**12 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 20-29%         | 11939    | 928    | 11011  | 0      | 7.8%      | 25.4      |
| 30-39%         | 13984    | 3587   | 10397  | 0      | 25.7%     | 20.2      |
| 40-49%         | 20666    | 4917   | 15749  | 0      | 23.8%     | 20.7      |
| 50-59%         | 16263    | 4911   | 11352  | 0      | 30.2%     | 18.3      |
| 60-69%         | 10702    | 3234   | 7468   | 0      | 30.2%     | 17.6      |
| 70-79%         | 4435     | 1177   | 3258   | 0      | 26.5%     | 22.5      |
| 80-89%         | 3962     | 797    | 3165   | 0      | 20.1%     | 19.1      |
| 90-99%         | 199      | 49     | 150    | 0      | 24.6%     | 31.3      |
| 100%           | 310      | 200    | 110    | 0      | 64.5%     | 47.1      |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| ORB (9:30-10:00)       | 10064    | 2936   | 7128   | 0      | 29.2%     | 14.1     |
| Morning (10:00-12:00)  | 31404    | 7494   | 23910  | 0      | 23.9%     | 15.2     |
| Afternoon (12:00-16:00) | 40992    | 9370   | 31622  | 0      | 22.9%     | 19.4     |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| ORB (9:30-10:00)       | 20-29%       | 1443     | 122    | 1321   | 0      | 8.5%      |
| ORB (9:30-10:00)       | 30-39%       | 2060     | 583    | 1477   | 0      | 28.3%     |
| ORB (9:30-10:00)       | 40-49%       | 2030     | 600    | 1430   | 0      | 29.6%     |
| ORB (9:30-10:00)       | 50-59%       | 1831     | 608    | 1223   | 0      | 33.2%     |
| ORB (9:30-10:00)       | 60-69%       | 1326     | 571    | 755    | 0      | 43.1%     |
| ORB (9:30-10:00)       | 70-79%       | 649      | 228    | 421    | 0      | 35.1%     |
| ORB (9:30-10:00)       | 80-89%       | 671      | 212    | 459    | 0      | 31.6%     |
| ORB (9:30-10:00)       | 90-99%       | 47       | 12     | 35     | 0      | 25.5%     |
| Morning (10:00-12:00)  | 20-29%       | 4003     | 304    | 3699   | 0      | 7.6%      |
| Morning (10:00-12:00)  | 30-39%       | 4911     | 1096   | 3815   | 0      | 22.3%     |
| Morning (10:00-12:00)  | 40-49%       | 8065     | 2085   | 5980   | 0      | 25.9%     |
| Morning (10:00-12:00)  | 50-59%       | 6195     | 1896   | 4299   | 0      | 30.6%     |
| Morning (10:00-12:00)  | 60-69%       | 3980     | 1185   | 2795   | 0      | 29.8%     |
| Morning (10:00-12:00)  | 70-79%       | 2126     | 504    | 1622   | 0      | 23.7%     |
| Morning (10:00-12:00)  | 80-89%       | 1885     | 368    | 1517   | 0      | 19.5%     |
| Morning (10:00-12:00)  | 90-99%       | 96       | 0      | 96     | 0      | 0.0%      |
| Morning (10:00-12:00)  | 100%         | 143      | 56     | 87     | 0      | 39.2%     |
| Afternoon (12:00-16:00) | 20-29%       | 6493     | 502    | 5991   | 0      | 7.7%      |
| Afternoon (12:00-16:00) | 30-39%       | 7013     | 1908   | 5105   | 0      | 27.2%     |
| Afternoon (12:00-16:00) | 40-49%       | 10571    | 2232   | 8339   | 0      | 21.1%     |
| Afternoon (12:00-16:00) | 50-59%       | 8237     | 2407   | 5830   | 0      | 29.2%     |
| Afternoon (12:00-16:00) | 60-69%       | 5396     | 1478   | 3918   | 0      | 27.4%     |
| Afternoon (12:00-16:00) | 70-79%       | 1660     | 445    | 1215   | 0      | 26.8%     |
| Afternoon (12:00-16:00) | 80-89%       | 1406     | 217    | 1189   | 0      | 15.4%     |
| Afternoon (12:00-16:00) | 90-99%       | 56       | 37     | 19     | 0      | 66.1%     |
| Afternoon (12:00-16:00) | 100%         | 160      | 144    | 16     | 0      | 90.0%     |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] gamma_wall_bounce | 20-29%       | 87.7%     | 7.8%      | 1028%    | 3.14     | 81       | 71       | 10       |
| [ALPHA] gamma_flip_breakout | 20-29%       | 42.1%     | 7.8%      | 441%     | 1.35     | 240      | 101      | 139      |
| [ALPHA] participant_divergence_scalper | 20-29%       | 41.2%     | 7.8%      | 431%     | 1.32     | 628      | 259      | 369      |
| [ALPHA] gamma_flip_breakout | 70-79%       | 100.0%    | 26.5%     | 277%     | 3.27     | 8        | 8        | 0        |
| [ALPHA] strike_concentration | 40-49%       | 89.1%     | 23.8%     | 275%     | 3.16     | 92       | 82       | 10       |
| [ALPHA] vol_compression_range | 20-29%       | 28.8%     | 7.8%      | 271%     | 0.83     | 52       | 15       | 37       |
| [ALPHA] magnet_accelerate | 20-29%       | 24.6%     | 7.8%      | 217%     | 0.66     | 447      | 110      | 337      |
| [ALPHA] confluence_reversal | 20-29%       | 22.6%     | 7.8%      | 191%     | 0.58     | 1474     | 333      | 1141     |
| [ALPHA] depth_decay_momentum | 80-89%       | 55.6%     | 20.1%     | 176%     | 1.85     | 72       | 40       | 32       |
| [ALPHA] gamma_squeeze    | 30-39%       | 70.4%     | 25.7%     | 174%     | 2.22     | 277      | 195      | 82       |
| [ALPHA] strike_concentration | 30-39%       | 70.4%     | 25.7%     | 174%     | 2.21     | 54       | 38       | 16       |
| [ALPHA] gex_divergence   | 90-99%       | 64.0%     | 24.6%     | 160%     | 1.26     | 25       | 16       | 9        |
| [ALPHA] prob_weighted_magnet | 50-59%       | 72.7%     | 30.2%     | 141%     | 2.33     | 66       | 48       | 18       |
| [ALPHA] gex_divergence   | 80-89%       | 48.3%     | 20.1%     | 140%     | 1.47     | 87       | 42       | 45       |
| [ALPHA] gex_imbalance    | 20-29%       | 16.4%     | 7.8%      | 111%     | 0.34     | 55       | 9        | 46       |
| [ALPHA] exchange_flow_concentration | 20-29%       | 16.4%     | 7.8%      | 110%     | 0.34     | 159      | 26       | 133      |
| [ALPHA] depth_decay_momentum | 40-49%       | 50.0%     | 23.8%     | 110%     | 1.27     | 36       | 18       | 18       |
| [ALPHA] gex_imbalance    | 40-49%       | 46.5%     | 23.8%     | 95%      | 1.10     | 1945     | 904      | 1041     |
| [ALPHA] gamma_flip_breakout | 30-39%       | 48.7%     | 25.7%     | 90%      | 1.14     | 197      | 96       | 101      |
| [ALPHA] strike_concentration | 70-79%       | 50.0%     | 26.5%     | 88%      | 1.04     | 24       | 12       | 12       |
| [ALPHA] vol_compression_range | 70-79%       | 50.0%     | 26.5%     | 88%      | 1.04     | 16       | 8        | 8        |
| [ALPHA] vol_compression_range | 30-39%       | 48.3%     | 25.7%     | 88%      | 1.12     | 116      | 56       | 60       |
| [ALPHA] participant_divergence_scalper | 60-69%       | 54.6%     | 30.2%     | 81%      | 1.38     | 119      | 65       | 54       |
| [ALPHA] participant_divergence_scalper | 30-39%       | 45.4%     | 25.7%     | 77%      | 0.98     | 2338     | 1061     | 1277     |
| [ALPHA] gamma_flip_breakout | 40-49%       | 41.7%     | 23.8%     | 75%      | 0.86     | 96       | 40       | 56       |
| [ALPHA] gex_imbalance    | 60-69%       | 51.7%     | 30.2%     | 71%      | 1.22     | 720      | 372      | 348      |
| [ALPHA] exchange_flow_imbalance | 80-89%       | 34.1%     | 20.1%     | 70%      | 0.73     | 466      | 159      | 307      |
| [ALPHA] vol_compression_range | 50-59%       | 50.0%     | 30.2%     | 66%      | 1.08     | 168      | 84       | 84       |
| [ALPHA] gamma_wall_bounce | 30-39%       | 40.7%     | 25.7%     | 59%      | 0.74     | 118      | 48       | 70       |
| [ALPHA] vol_compression_range | 60-69%       | 46.6%     | 30.2%     | 54%      | 0.93     | 116      | 54       | 62       |

**30 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 20-29%       | 39      | 39     | 0      | 100.0%   | 7.7%     | 1193%  | 2.68    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | ORB (9:30-10:00) | 20-29%       | 10      | 9      | 1      | 90.0%    | 8.5%     | 965%   | 2.67    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 20-29%       | 9       | 7      | 2      | 77.8%    | 7.7%     | 906%   | 2.03    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 20-29%       | 32      | 23     | 9      | 71.9%    | 7.6%     | 846%   | 2.77    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 20-29%       | 70      | 40     | 30     | 57.1%    | 7.7%     | 639%   | 1.43    | 🔥 STRONG     |
| [ALPHA] exchange_flow_concentration | ORB (9:30-10:00) | 20-29%       | 9       | 5      | 4      | 55.6%    | 8.5%     | 557%   | 1.54    | 🔥 STRONG     |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 20-29%       | 385     | 173    | 212    | 44.9%    | 7.7%     | 481%   | 1.08    | 🔥 STRONG     |
| [ALPHA] participant_divergence_scalper | Morning (10:00-12:00) | 20-29%       | 192     | 77     | 115    | 40.1%    | 7.6%     | 428%   | 1.40    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | Afternoon (12:00-16:00) | 20-29%       | 230     | 88     | 142    | 38.3%    | 7.7%     | 395%   | 0.89    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 40-49%       | 52      | 52     | 0      | 100.0%   | 21.1%    | 374%   | 3.32    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 20-29%       | 170     | 61     | 109    | 35.9%    | 7.6%     | 372%   | 1.22    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 70-79%       | 8       | 8      | 0      | 100.0%   | 23.7%    | 322%   | 2.92    | ⚡ HIGH       |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 80-89%       | 28      | 18     | 10     | 64.3%    | 15.4%    | 317%   | 2.17    | ⚡ HIGH       |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 20-29%       | 27      | 8      | 19     | 29.6%    | 7.6%     | 290%   | 0.95    | 🔥 STRONG     |
| [ALPHA] confluence_reversal | ORB (9:30-10:00) | 20-29%       | 253     | 75     | 178    | 29.6%    | 8.5%     | 251%   | 0.69    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 30-39%       | 135     | 127    | 8      | 94.1%    | 27.2%    | 246%   | 2.43    | ⚡ HIGH       |
| [ALPHA] strike_concentration | ORB (9:30-10:00) | 40-49%       | 12      | 12     | 0      | 100.0%   | 29.6%    | 238%   | 2.83    | ⚡ HIGH       |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 50-59%       | 6       | 6      | 0      | 100.0%   | 33.2%    | 201%   | 2.78    | ⚡ HIGH       |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 60-69%       | 45      | 37     | 8      | 82.2%    | 27.4%    | 200%   | 2.35    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 30-39%       | 20      | 16     | 4      | 80.0%    | 27.2%    | 194%   | 1.92    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 70-79%       | 5       | 5      | 0      | 100.0%   | 35.1%    | 185%   | 1.79    | 🔥 STRONG     |
| [ALPHA] depth_decay_momentum | Morning (10:00-12:00) | 80-89%       | 72      | 40     | 32     | 55.6%    | 19.5%    | 185%   | 2.15    | ⚡ HIGH       |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 30-39%       | 5       | 4      | 1      | 80.0%    | 28.3%    | 183%   | 2.09    | ⚡ HIGH       |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 70-79%       | 6       | 4      | 2      | 66.7%    | 23.7%    | 181%   | 1.64    | 🔥 STRONG     |
| [ALPHA] confluence_reversal | Afternoon (12:00-16:00) | 20-29%       | 633     | 136    | 497    | 21.5%    | 7.7%     | 178%   | 0.40    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 50-59%       | 106     | 86     | 20     | 81.1%    | 29.2%    | 178%   | 2.36    | ⚡ HIGH       |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 20-29%       | 588     | 122    | 466    | 20.7%    | 7.6%     | 173%   | 0.57    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 80-89%       | 124     | 52     | 72     | 41.9%    | 15.4%    | 172%   | 1.18    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 30-39%       | 46      | 34     | 12     | 73.9%    | 27.2%    | 172%   | 1.70    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 60-69%       | 52      | 38     | 14     | 73.1%    | 27.4%    | 167%   | 1.96    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | ORB (9:30-10:00) | 30-39%       | 49      | 35     | 14     | 71.4%    | 28.3%    | 152%   | 1.74    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 40-49%       | 28      | 18     | 10     | 64.3%    | 25.9%    | 149%   | 1.92    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 60-69%       | 54      | 36     | 18     | 66.7%    | 27.4%    | 143%   | 1.68    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 40-49%       | 64      | 40     | 24     | 62.5%    | 25.9%    | 142%   | 1.83    | 🔥 STRONG     |
| [ALPHA] prob_weighted_magnet | Morning (10:00-12:00) | 50-59%       | 66      | 48     | 18     | 72.7%    | 30.6%    | 138%   | 2.04    | ⚡ HIGH       |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 40-49%       | 16      | 8      | 8      | 50.0%    | 21.1%    | 137%   | 1.22    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 50-59%       | 58      | 40     | 18     | 69.0%    | 29.2%    | 136%   | 1.81    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 90-99%       | 20      | 12     | 8      | 60.0%    | 25.5%    | 135%   | 1.00    | 🔥 STRONG     |
| [ALPHA] participant_divergence_scalper | Morning (10:00-12:00) | 30-39%       | 683     | 354    | 329    | 51.8%    | 22.3%    | 132%   | 1.67    | 🔥 STRONG     |
| [ALPHA] exchange_flow_asymmetry | ORB (9:30-10:00) | 70-79%       | 15      | 12     | 3      | 80.0%    | 35.1%    | 128%   | 1.24    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 20-29%       | 84      | 16     | 68     | 19.0%    | 8.5%     | 125%   | 0.35    | 🔥 STRONG     |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 40-49%       | 701     | 404    | 297    | 57.6%    | 25.9%    | 123%   | 1.58    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | ORB (9:30-10:00) | 40-49%       | 26      | 17     | 9      | 65.4%    | 29.6%    | 121%   | 1.44    | 🔥 STRONG     |
| [ALPHA] participant_diversity_conviction | Morning (10:00-12:00) | 30-39%       | 291     | 143    | 148    | 49.1%    | 22.3%    | 120%   | 1.52    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 70-79%       | 16      | 8      | 8      | 50.0%    | 23.7%    | 111%   | 1.01    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 40-49%       | 441     | 195    | 246    | 44.2%    | 21.1%    | 109%   | 0.97    | 🔥 STRONG     |
| [ALPHA] participant_divergence_scalper | ORB (9:30-10:00) | 20-29%       | 51      | 9      | 42     | 17.6%    | 8.5%     | 109%   | 0.30    | 🔥 STRONG     |
| [ALPHA] exchange_flow_imbalance | Afternoon (12:00-16:00) | 80-89%       | 131     | 42     | 89     | 32.1%    | 15.4%    | 108%   | 0.74    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 70-79%       | 47      | 23     | 24     | 48.9%    | 23.7%    | 106%   | 0.96    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 30-39%       | 34      | 19     | 15     | 55.9%    | 27.2%    | 105%   | 1.04    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 40-49%       | 35      | 15     | 20     | 42.9%    | 21.1%    | 103%   | 0.92    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 30-39%       | 177     | 80     | 97     | 45.2%    | 22.3%    | 103%   | 1.29    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 30-39%       | 28      | 16     | 12     | 57.1%    | 28.3%    | 102%   | 1.17    | 🔥 STRONG     |
| [ALPHA] exchange_flow_concentration | Afternoon (12:00-16:00) | 20-29%       | 90      | 14     | 76     | 15.6%    | 7.7%     | 101%   | 0.23    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 50-59%       | 447     | 266    | 181    | 59.5%    | 30.6%    | 94%    | 1.40    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Morning (10:00-12:00) | 40-49%       | 12      | 6      | 6      | 50.0%    | 25.9%    | 93%    | 1.20    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | ORB (9:30-10:00) | 30-39%       | 46      | 25     | 21     | 54.3%    | 28.3%    | 92%    | 1.05    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 40-49%       | 1204    | 488    | 716    | 40.5%    | 21.1%    | 92%    | 0.82    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 70-79%       | 84      | 56     | 28     | 66.7%    | 35.1%    | 90%    | 0.87    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | ORB (9:30-10:00) | 20-29%       | 51      | 8      | 43     | 15.7%    | 8.5%     | 86%    | 0.24    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 60-69%       | 447     | 224    | 223    | 50.1%    | 27.4%    | 83%    | 0.97    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 80-89%       | 28      | 16     | 12     | 57.1%    | 31.6%    | 81%    | 1.10    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 60-69%       | 197     | 104    | 93     | 52.8%    | 29.8%    | 77%    | 1.40    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | ORB (9:30-10:00) | 50-59%       | 164     | 95     | 69     | 57.9%    | 33.2%    | 74%    | 1.03    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Morning (10:00-12:00) | 30-39%       | 54      | 21     | 33     | 38.9%    | 22.3%    | 74%    | 0.94    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | ORB (9:30-10:00) | 40-49%       | 8       | 4      | 4      | 50.0%    | 29.6%    | 69%    | 0.82    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | ORB (9:30-10:00) | 60-69%       | 22      | 16     | 6      | 72.7%    | 43.1%    | 69%    | 1.53    | ⚠ MODERATE   |
| [ALPHA] call_put_flow_asymmetry | Afternoon (12:00-16:00) | 40-49%       | 350     | 124    | 226    | 35.4%    | 21.1%    | 68%    | 0.60    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 50-59%       | 312     | 160    | 152    | 51.3%    | 30.6%    | 68%    | 1.00    | ⚠ MODERATE   |
| [ALPHA] participant_divergence_scalper | Afternoon (12:00-16:00) | 30-39%       | 1330    | 600    | 730    | 45.1%    | 27.2%    | 66%    | 0.65    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 30-39%       | 33      | 12     | 21     | 36.4%    | 22.3%    | 63%    | 0.79    | ⚠ MODERATE   |
| [ALPHA] participant_diversity_conviction | ORB (9:30-10:00) | 30-39%       | 146     | 67     | 79     | 45.9%    | 28.3%    | 62%    | 0.71    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Afternoon (12:00-16:00) | 50-59%       | 1868    | 874    | 994    | 46.8%    | 29.2%    | 60%    | 0.80    | ⚠ MODERATE   |
| [ALPHA] gex_imbalance    | Morning (10:00-12:00) | 50-59%       | 811     | 395    | 416    | 48.7%    | 30.6%    | 59%    | 0.88    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | Morning (10:00-12:00) | 30-39%       | 93      | 33     | 60     | 35.5%    | 22.3%    | 59%    | 0.74    | ⚠ MODERATE   |
| [ALPHA] order_book_fragmentation | ORB (9:30-10:00) | 80-89%       | 76      | 38     | 38     | 50.0%    | 31.6%    | 58%    | 0.79    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 60-69%       | 136     | 64     | 72     | 47.1%    | 29.8%    | 58%    | 1.05    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 30-39%       | 111     | 39     | 72     | 35.1%    | 22.3%    | 57%    | 0.72    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 30-39%       | 87      | 37     | 50     | 42.5%    | 27.2%    | 56%    | 0.56    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 20-29%       | 60      | 7      | 53     | 11.7%    | 7.6%     | 54%    | 0.18    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 60-69%       | 77      | 35     | 42     | 45.5%    | 29.8%    | 53%    | 0.95    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 70-79%       | 427     | 173    | 254    | 40.5%    | 26.8%    | 51%    | 1.22    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 40-49%       | 85      | 33     | 52     | 38.8%    | 25.9%    | 50%    | 0.65    | ⚠ MODERATE   |

**83 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | delta_volume_exhaustion  | 11,883  | 0.0%     | $2.0     | 40-49%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 40-49% | UNKNOWN        | Time Held: <30m |
| 2     | gamma_squeeze            | 1,792   | 33.4%    | $0.4     | 30-39%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 30-39% | Sideways       | Time Held: 90-240m |
| 3     | strike_concentration     | 842     | 48.2%    | $0.4     | 40-49%         | Afternoon (12:00-16:00) | ORB (9:30-10:00) @ 40-49% | Sideways       | Time Held: 90-240m |
| 4     | vol_compression_range    | 563     | 43.7%    | $0.3     | 50-59%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 20-29% | Trending (Up)  | Time Held: 240-480m |
| 5     | theta_burn               | 12      | 0.0%     | $0.2     | 20-29%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 20-29% | Sideways       | Time Held: <30m |
| 6     | gex_imbalance            | 5,822   | 45.9%    | $0.0     | 60-69%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 60-69% | Trending (Up)  | Time Held: 240-480m |
| 7     | participant_divergence_scalper | 7,670   | 38.1%    | $-0.0    | 60-69%         | Morning (10:00-12:00) | Afternoon (12:00-16:00) @ 60-69% | UNKNOWN        | Time Held: 90-240m |
| 8     | depth_decay_momentum     | 5,533   | 36.5%    | $-0.1    | 80-89%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 80-89% | UNKNOWN        | Time Held: 90-240m |
| 9     | exchange_flow_imbalance  | 1,774   | 31.4%    | $-0.1    | 50-59%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 50-59% | UNKNOWN        | Time Held: 30-90m |
| 10    | order_book_fragmentation | 6,905   | 19.9%    | $-0.1    | 80-89%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 80-89% | UNKNOWN        | Time Held: 240-480m |
| 11    | depth_imbalance_momentum | 1,756   | 34.0%    | $-0.1    | 50-59%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 30-39% | UNKNOWN        | Time Held: 240-480m |
| 12    | gamma_flip_breakout      | 1,933   | 36.3%    | $-0.2    | 70-79%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 70-79% | Sideways       | Time Held: 90-240m |
| 13    | exchange_flow_concentration | 2,588   | 34.0%    | $-0.2    | 60-69%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 60-69% | UNKNOWN        | Time Held: <30m |
| 14    | call_put_flow_asymmetry  | 4,648   | 23.5%    | $-0.2    | 30-39%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 30-39% | UNKNOWN        | Time Held: 30-90m |
| 15    | gamma_wall_bounce        | 2,127   | 31.3%    | $-0.2    | 20-29%         | ORB (9:30-10:00) | Afternoon (12:00-16:00) @ 20-29% | Trending (Up)  | Time Held: 90-240m |
| 16    | magnet_accelerate        | 4,518   | 15.3%    | $-0.2    | 20-29%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 70-79% | Trending (Up)  | Time Held: 90-240m |
| 17    | gex_divergence           | 2,794   | 27.8%    | $-0.3    | 90-99%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 50-59% | Trending (Up)  | Time Held: 30-90m |
| 18    | prob_weighted_magnet     | 9,181   | 17.4%    | $-0.3    | 50-59%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 50-59% | Trending (Up)  | Time Held: 240-480m |
| 19    | participant_diversity_conviction | 4,310   | 26.2%    | $-0.4    | 30-39%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 30-39% | UNKNOWN        | Time Held: 30-90m |
| 20    | exchange_flow_asymmetry  | 2,603   | 14.5%    | $-1.1    | 70-79%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 70-79% | UNKNOWN        | Time Held: 240-480m |
| 21    | confluence_reversal      | 3,166   | 15.9%    | $-1.4    | 70-79%         | ORB (9:30-10:00) | Morning (10:00-12:00) @ 70-79% | Sideways       | Time Held: 240-480m |
| 22    | delta_gamma_squeeze      | 40      | 0.0%     | $-2.9    | 30-39%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 30-39% | Trending (Up)  | Time Held: <30m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis — Regular Hours Only*