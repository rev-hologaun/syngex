# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-06-02  |  **Generated:** 2026-06-02 14:48 UTC  |  **Total Resolved Signals:** 37,402  |  **Strategies Analyzed:** 15

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 37,402                                                       |
| Total Wins           | 13,685                                                       |
| Total Losses         | 23,717                                                       |
| Time-Expired (CLOSED) | 0                                                            |
| Overall Win Rate     | 36.6%                                                        |
| Total P&L (resolved) | $8162.55                                                     |
| Avg P&L per Resolved Signal | $0.22                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### confluence_reversal

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,589  |  **Win Rate:** 35.7%  |  **Avg P&L (resolved):** $0.2  |  **Avg P&L (all):** $0.2  |  **Avg Hold:** 22603s (376.7m)  |  **Median Hold:** 13720s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 2304  | 698   | 1606   | 0      | 30.3%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 1399  | 405   | 994    | 0      | 28.9%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 1143  | 511   | 632    | 0      | 44.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 619   | 313   | 306    | 0      | 50.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 124   | 68    | 56     | 0      | 54.8%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 3294  | 1201  | 2093   | 0      | 36.5%     | $0.2     |
| Trending (Up)        | 2295  | 794   | 1501   | 0      | 34.6%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1473  | 149   | 1324   | 0      | 10.1%     | $-2.8    |
| Positive Gamma (Range-Bound friendly) | 4116  | 1846  | 2270   | 0      | 44.8%     | $1.2     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 842   | 426   | 416    | 0      | 50.6%     | $1.8     |
| Time Held: 30-90m      | 941   | 230   | 711    | 0      | 24.4%     | $-0.6    |
| Time Held: 90-240m     | 1397  | 429   | 968    | 0      | 30.7%     | $-0.2    |
| Time Held: <30m        | 528   | 86    | 442    | 0      | 16.3%     | $-1.2    |
| Time Held: >480m       | 1881  | 824   | 1057   | 0      | 43.8%     | $0.5     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 778   | 297   | 481    | 0      | 38.2%     | $0.6     | 🟢          |
| Afternoon (12:00-16:00) | 914   | 315   | 599    | 0      | 34.5%     | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 459   | 160   | 299    | 0      | 34.9%     | $0.0     | 🔴          |
| ORB (9:30-10:00)       | 233   | 54    | 179    | 0      | 23.2%     | $-1.1    | 🔴          |
| Overnight              | 511   | 207   | 304    | 0      | 40.5%     | $-1.1    | 🟢          |
| Pre-market             | 2694  | 962   | 1732   | 0      | 35.7%     | $0.5     | —          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 2694   | 0          | 247        | 2447       | 0.0%      | 9.2%      | 90.8%     |
| ORB (9:30-10:00)       | 233    | 0          | 26         | 207        | 0.0%      | 11.2%     | 88.8%     |
| Morning (10:00-12:00)  | 459    | 0          | 99         | 360        | 0.0%      | 21.6%     | 78.4%     |
| Afternoon (12:00-16:00) | 914    | 0          | 174        | 740        | 0.0%      | 19.0%     | 81.0%     |
| After-hours (16:00-20:00) | 778    | 0          | 184        | 594        | 0.0%      | 23.7%     | 76.3%     |
| Overnight              | 511    | 0          | 13         | 498        | 0.0%      | 2.5%      | 97.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 1249   | 446   | 803    | 0      | 35.7%     | $0.9         | —          |
| Pre-market             | 30-39%     | 776    | 224   | 552    | 0      | 28.9%     | $-0.2        | 🔴          |
| Pre-market             | 40-49%     | 422    | 165   | 257    | 0      | 39.1%     | $0.1         | 🟢          |
| Pre-market             | 50-59%     | 191    | 97    | 94     | 0      | 50.8%     | $1.0         | 🟢          |
| Pre-market             | 60-69%     | 56     | 30    | 26     | 0      | 53.6%     | $1.3         | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 79     | 13    | 66     | 0      | 16.5%     | $-1.7        | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 67     | 8     | 59     | 0      | 11.9%     | $-2.2        | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 61     | 20    | 41     | 0      | 32.8%     | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 24     | 12    | 12     | 0      | 50.0%     | $1.8         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 2      | 1     | 1      | 0      | 50.0%     | $2.9         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 130    | 27    | 103    | 0      | 20.8%     | $-0.7        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 111    | 10    | 101    | 0      | 9.0%      | $-2.5        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 119    | 59    | 60     | 0      | 49.6%     | $1.0         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 79     | 51    | 28     | 0      | 64.6%     | $2.7         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 20     | 13    | 7      | 0      | 65.0%     | $3.3         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 300    | 45    | 255    | 0      | 15.0%     | $-1.9        | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 171    | 35    | 136    | 0      | 20.5%     | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 269    | 127   | 142    | 0      | 47.2%     | $1.4         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 153    | 94    | 59     | 0      | 61.4%     | $2.7         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 21     | 14    | 7      | 0      | 66.7%     | $2.8         | ⚠️         |
| After-hours (16:00-20:00) | 20-29%     | 255    | 70    | 185    | 0      | 27.5%     | $-0.7        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 80     | 31    | 49     | 0      | 38.8%     | $-0.8        | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 259    | 127   | 132    | 0      | 49.0%     | $1.9         | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 159    | 59    | 100    | 0      | 37.1%     | $1.0         | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 25     | 10    | 15     | 0      | 40.0%     | $1.3         | ⚠️         |
| Overnight              | 20-29%     | 291    | 97    | 194    | 0      | 33.3%     | $-2.1        | 🔴          |
| Overnight              | 30-39%     | 194    | 97    | 97     | 0      | 50.0%     | $0.0         | 🟢          |
| Overnight              | 40-49%     | 13     | 13    | 0      | 0      | 100.0%    | $5.6         | ⚠️         |
| Overnight              | 50-59%     | 13     | 0     | 13     | 0      | 0.0%      | $-2.4        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 3236  | 1424  | 1812   | 0      | 44.0%     | $0.9     |
| SHORT        | 2353  | 571   | 1782   | 0      | 24.3%     | $-0.8    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 64    | 7     | 57     | 0      | 10.9%     | $-2.0    |
| Long (30-60 min)       | 457   | 94    | 363    | 0      | 20.6%     | $-0.7    |
| Medium (5-15 min)      | 157   | 22    | 135    | 0      | 14.0%     | $-1.6    |
| Slow (15-30 min)       | 278   | 50    | 228    | 0      | 18.0%     | $-0.8    |
| Very Fast (<1 min)     | 29    | 7     | 22     | 0      | 24.1%     | $-0.8    |
| Very Long (>1h)        | 4604  | 1815  | 2789   | 0      | 39.4%     | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 35.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.19 — profitable even with 35.7% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (54.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (28.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.20) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.80) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Overnight (40.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (22603s / 376.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### delta_gamma_squeeze

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 222  |  **Win Rate:** 48.2%  |  **Avg P&L (resolved):** $1.6  |  **Avg P&L (all):** $1.6  |  **Avg Hold:** 21644s (360.7m)  |  **Median Hold:** 23018s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 105   | 42    | 63     | 0      | 40.0%     | $0.0     | $0.0     | 0.0%     |
| 20-29%         | 84    | 35    | 49     | 0      | 41.7%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 29    | 28    | 1      | 0      | 96.6%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 3     | 1     | 2      | 0      | 33.3%     | $0.0     | $0.0     | 0.0%     |
| Other          | 1     | 1     | 0      | 0      | 100.0%    | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 213   | 103   | 110    | 0      | 48.4%     | $1.6     |
| Trending (Up)        | 9     | 4     | 5      | 0      | 44.4%     | $2.6     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 222   | 107   | 115    | 0      | 48.2%     | $1.6     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 60    | 19    | 41     | 0      | 31.7%     | $-0.6    |
| Time Held: 30-90m      | 21    | 11    | 10     | 0      | 52.4%     | $2.9     |
| Time Held: 90-240m     | 45    | 16    | 29     | 0      | 35.6%     | $0.4     |
| Time Held: <30m        | 19    | 13    | 6      | 0      | 68.4%     | $4.9     |
| Time Held: >480m       | 77    | 48    | 29     | 0      | 62.3%     | $2.9     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 5     | 2     | 3      | 0      | 40.0%     | $0.6     | ⚠️         |
| Afternoon (12:00-16:00) | 6     | 3     | 3      | 0      | 50.0%     | $3.1     | ⚠️         |
| Overnight              | 37    | 17    | 20     | 0      | 45.9%     | $1.5     | 🔴          |
| Pre-market             | 174   | 85    | 89     | 0      | 48.9%     | $1.7     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 174    | 0          | 0          | 174        | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 6      | 0          | 0          | 6          | 0.0%      | 0.0%      | 100.0%    |
| After-hours (16:00-20:00) | 5      | 0          | 0          | 5          | 0.0%      | 0.0%      | 100.0%    |
| Overnight              | 37     | 0          | 0          | 37         | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 10-19%     | 89     | 35    | 54     | 0      | 39.3%     | $1.0         | 🔴          |
| Pre-market             | 20-29%     | 57     | 25    | 32     | 0      | 43.9%     | $1.5         | 🔴          |
| Pre-market             | 30-39%     | 25     | 24    | 1      | 0      | 96.0%     | $4.8         | ⚠️         |
| Pre-market             | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-3.7        | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 2      | 2     | 0      | 0      | 100.0%    | $12.3        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 4      | 1     | 3      | 0      | 25.0%     | $-1.5        | ⚠️         |
| After-hours (16:00-20:00) | 10-19%     | 4      | 1     | 3      | 0      | 25.0%     | $-0.5        | ⚠️         |
| After-hours (16:00-20:00) | 20-29%     | 1      | 1     | 0      | 0      | 100.0%    | $5.1         | ⚠️         |
| Overnight              | 10-19%     | 10     | 4     | 6      | 0      | 40.0%     | $0.8         | ⚠️         |
| Overnight              | 20-29%     | 22     | 8     | 14     | 0      | 36.4%     | $1.1         | ⚠️         |
| Overnight              | 30-39%     | 4      | 4     | 0      | 0      | 100.0%    | $4.2         | ⚠️         |
| Overnight              | 40-49%     | 1      | 1     | 0      | 0      | 100.0%    | $5.1         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 116   | 32    | 84     | 0      | 27.6%     | $-1.7    |
| SHORT        | 106   | 75    | 31     | 0      | 70.8%     | $5.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 8     | 3     | 5      | 0      | 37.5%     | $-0.2    |
| Long (30-60 min)       | 7     | 3     | 4      | 0      | 42.9%     | $0.7     |
| Medium (5-15 min)      | 6     | 5     | 1      | 0      | 83.3%     | $5.8     |
| Slow (15-30 min)       | 5     | 5     | 0      | 0      | 100.0%    | $12.2    |
| Very Long (>1h)        | 196   | 91    | 105    | 0      | 46.4%     | $1.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 48.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $1.64 — profitable even with 48.2% win rate (good risk/reward).
- 🎯 Best performance at 30-39% confidence (96.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 10-19% (40.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $2.58) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $4.95) — optimal time held is Time Held: <30m.
- ⚠️ Best signal generation window: Afternoon (12:00-16:00) (50.0% win rate) — but only 6 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (21644s / 360.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,781  |  **Win Rate:** 42.2%  |  **Avg P&L (resolved):** $0.2  |  **Avg P&L (all):** $0.2  |  **Avg Hold:** 8486s (141.4m)  |  **Median Hold:** 2906s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 6     | 4     | 2      | 0      | 66.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 471   | 191   | 280    | 0      | 40.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 699   | 260   | 439    | 0      | 37.2%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 1778  | 767   | 1011   | 0      | 43.1%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 767   | 352   | 415    | 0      | 45.9%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 60    | 20    | 40     | 0      | 33.3%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 3781  | 1594  | 2187   | 0      | 42.2%     | $0.2     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1479  | 666   | 813    | 0      | 45.0%     | $0.5     |
| Positive Gamma (Range-Bound friendly) | 2302  | 928   | 1374   | 0      | 40.3%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 135   | 86    | 49     | 0      | 63.7%     | $1.1     |
| Time Held: 30-90m      | 992   | 447   | 545    | 0      | 45.1%     | $0.2     |
| Time Held: 90-240m     | 682   | 349   | 333    | 0      | 51.2%     | $0.6     |
| Time Held: <30m        | 1498  | 495   | 1003   | 0      | 33.0%     | $-0.2    |
| Time Held: >480m       | 474   | 217   | 257    | 0      | 45.8%     | $0.5     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 462   | 191   | 271    | 0      | 41.3%     | $0.3     | 🔴          |
| Afternoon (12:00-16:00) | 935   | 494   | 441    | 0      | 52.8%     | $0.7     | 🟢          |
| Morning (10:00-12:00)  | 589   | 235   | 354    | 0      | 39.9%     | $0.0     | 🔴          |
| ORB (9:30-10:00)       | 247   | 58    | 189    | 0      | 23.5%     | $-0.6    | 🔴          |
| Pre-market             | 1548  | 616   | 932    | 0      | 39.8%     | $0.1     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1548   | 872        | 671        | 5          | 56.3%     | 43.3%     | 0.3%      |
| ORB (9:30-10:00)       | 247    | 177        | 70         | 0          | 71.7%     | 28.3%     | 0.0%      |
| Morning (10:00-12:00)  | 589    | 442        | 147        | 0          | 75.0%     | 25.0%     | 0.0%      |
| Afternoon (12:00-16:00) | 935    | 736        | 198        | 1          | 78.7%     | 21.2%     | 0.1%      |
| After-hours (16:00-20:00) | 462    | 378        | 84         | 0          | 81.8%     | 18.2%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 40-49%     | 5      | 3     | 2      | 0      | 60.0%     | $1.1         | ⚠️         |
| Pre-market             | 50-59%     | 314    | 123   | 191    | 0      | 39.2%     | $0.1         | 🔴          |
| Pre-market             | 60-69%     | 357    | 125   | 232    | 0      | 35.0%     | $-0.1        | 🔴          |
| Pre-market             | 70-79%     | 564    | 258   | 306    | 0      | 45.7%     | $0.3         | 🟢          |
| Pre-market             | 80-89%     | 274    | 101   | 173    | 0      | 36.9%     | $-0.1        | 🔴          |
| Pre-market             | 90-99%     | 34     | 6     | 28     | 0      | 17.6%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 17     | 3     | 14     | 0      | 17.6%     | $-1.1        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 53     | 15    | 38     | 0      | 28.3%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 112    | 21    | 91     | 0      | 18.8%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 59     | 17    | 42     | 0      | 28.8%     | $-0.4        | 🔴          |
| ORB (9:30-10:00)       | 90-99%     | 6      | 2     | 4      | 0      | 33.3%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 28     | 16    | 12     | 0      | 57.1%     | $1.1         | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 119    | 46    | 73     | 0      | 38.7%     | $0.0         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 319    | 129   | 190    | 0      | 40.4%     | $-0.0        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 121    | 43    | 78     | 0      | 35.5%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 2      | 1     | 1      | 0      | 50.0%     | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 1      | 1     | 0      | 0      | 100.0%    | $3.8         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 99     | 43    | 56     | 0      | 43.4%     | $0.2         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 99     | 47    | 52     | 0      | 47.5%     | $0.4         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 533    | 274   | 259    | 0      | 51.4%     | $0.6         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 192    | 122   | 70     | 0      | 63.5%     | $1.2         | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 11     | 7     | 4      | 0      | 63.6%     | $1.3         | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 13     | 6     | 7      | 0      | 46.2%     | $0.4         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 71     | 27    | 44     | 0      | 38.0%     | $0.1         | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 250    | 85    | 165    | 0      | 34.0%     | $0.1         | 🔴          |
| After-hours (16:00-20:00) | 80-89%     | 121    | 69    | 52     | 0      | 57.0%     | $0.7         | 🟢          |
| After-hours (16:00-20:00) | 90-99%     | 7      | 4     | 3      | 0      | 57.1%     | $0.6         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1861  | 753   | 1108   | 0      | 40.5%     | $-0.0    |
| SHORT        | 1920  | 841   | 1079   | 0      | 43.8%     | $0.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 310   | 77    | 233    | 0      | 24.8%     | $-0.4    |
| Long (30-60 min)       | 582   | 251   | 331    | 0      | 43.1%     | $0.1     |
| Medium (5-15 min)      | 588   | 223   | 365    | 0      | 37.9%     | $-0.0    |
| Slow (15-30 min)       | 525   | 181   | 344    | 0      | 34.5%     | $-0.2    |
| Very Fast (<1 min)     | 75    | 14    | 61     | 0      | 18.7%     | $-0.5    |
| Very Long (>1h)        | 1701  | 848   | 853    | 0      | 49.9%     | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 42.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.19 — profitable even with 42.2% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (66.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (33.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.19) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.07) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (52.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (8486s / 141.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### depth_imbalance_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,457  |  **Win Rate:** 24.1%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.3  |  **Avg Hold:** 20699s (345.0m)  |  **Median Hold:** 11299s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 85    | 23    | 62     | 0      | 27.1%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 641   | 152   | 489    | 0      | 23.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1456  | 334   | 1122   | 0      | 22.9%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 177   | 50    | 127    | 0      | 28.2%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 98    | 34    | 64     | 0      | 34.7%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2457  | 593   | 1864   | 0      | 24.1%     | $-0.3    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 767   | 175   | 592    | 0      | 22.8%     | $-0.8    |
| Positive Gamma (Range-Bound friendly) | 1690  | 418   | 1272   | 0      | 24.7%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 361   | 174   | 187    | 0      | 48.2%     | $1.6     |
| Time Held: 30-90m      | 433   | 45    | 388    | 0      | 10.4%     | $-1.7    |
| Time Held: 90-240m     | 607   | 137   | 470    | 0      | 22.6%     | $-0.5    |
| Time Held: <30m        | 343   | 40    | 303    | 0      | 11.7%     | $-1.4    |
| Time Held: >480m       | 713   | 197   | 516    | 0      | 27.6%     | $0.1     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 339   | 48    | 291    | 0      | 14.2%     | $-1.2    | 🔴          |
| Afternoon (12:00-16:00) | 530   | 191   | 339    | 0      | 36.0%     | $1.0     | 🟢          |
| Morning (10:00-12:00)  | 259   | 87    | 172    | 0      | 33.6%     | $0.6     | 🟢          |
| ORB (9:30-10:00)       | 135   | 31    | 104    | 0      | 23.0%     | $-0.9    | 🔴          |
| Pre-market             | 1194  | 236   | 958    | 0      | 19.8%     | $-0.8    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1194   | 24         | 775        | 395        | 2.0%      | 64.9%     | 33.1%     |
| ORB (9:30-10:00)       | 135    | 16         | 95         | 24         | 11.9%     | 70.4%     | 17.8%     |
| Morning (10:00-12:00)  | 259    | 19         | 168        | 72         | 7.3%      | 64.9%     | 27.8%     |
| Afternoon (12:00-16:00) | 530    | 28         | 358        | 144        | 5.3%      | 67.5%     | 27.2%     |
| After-hours (16:00-20:00) | 339    | 11         | 237        | 91         | 3.2%      | 69.9%     | 26.8%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 56     | 10    | 46     | 0      | 17.9%     | $-1.3        | 🔴          |
| Pre-market             | 40-49%     | 339    | 65    | 274    | 0      | 19.2%     | $-0.9        | 🔴          |
| Pre-market             | 50-59%     | 708    | 138   | 570    | 0      | 19.5%     | $-0.8        | 🔴          |
| Pre-market             | 60-69%     | 67     | 13    | 54     | 0      | 19.4%     | $-0.8        | 🔴          |
| Pre-market             | 70-79%     | 24     | 10    | 14     | 0      | 41.7%     | $1.0         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 4      | 2     | 2      | 0      | 50.0%     | $2.0         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 20     | 7     | 13     | 0      | 35.0%     | $-0.2        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 79     | 15    | 64     | 0      | 19.0%     | $-1.2        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 16     | 4     | 12     | 0      | 25.0%     | $-1.0        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 16     | 3     | 13     | 0      | 18.8%     | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 7      | 3     | 4      | 0      | 42.9%     | $0.5         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 65     | 22    | 43     | 0      | 33.8%     | $0.4         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 147    | 48    | 99     | 0      | 32.7%     | $0.6         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 21     | 5     | 16     | 0      | 23.8%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 19     | 9     | 10     | 0      | 47.4%     | $2.3         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 10     | 6     | 4      | 0      | 60.0%     | $2.1         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 134    | 46    | 88     | 0      | 34.3%     | $0.8         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 306    | 102   | 204    | 0      | 33.3%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 52     | 26    | 26     | 0      | 50.0%     | $2.3         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 28     | 11    | 17     | 0      | 39.3%     | $1.1         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 8      | 2     | 6      | 0      | 25.0%     | $-1.9        | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 83     | 12    | 71     | 0      | 14.5%     | $-1.0        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 216    | 31    | 185    | 0      | 14.4%     | $-1.2        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 21     | 2     | 19     | 0      | 9.5%      | $-1.4        | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 11     | 1     | 10     | 0      | 9.1%      | $-1.2        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 396   | 115   | 281    | 0      | 29.0%     | $-0.3    |
| SHORT        | 2061  | 478   | 1583   | 0      | 23.2%     | $-0.3    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 45    | 2     | 43     | 0      | 4.4%      | $-1.9    |
| Long (30-60 min)       | 233   | 26    | 207    | 0      | 11.2%     | $-1.7    |
| Medium (5-15 min)      | 116   | 18    | 98     | 0      | 15.5%     | $-1.0    |
| Slow (15-30 min)       | 174   | 19    | 155    | 0      | 10.9%     | $-1.6    |
| Very Fast (<1 min)     | 8     | 1     | 7      | 0      | 12.5%     | $-1.6    |
| Very Long (>1h)        | 1881  | 527   | 1354   | 0      | 28.0%     | $0.0     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.35 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (34.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (22.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.35) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.61) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (36.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (20699s / 345.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,824  |  **Win Rate:** 22.8%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.2  |  **Avg Hold:** 18359s (306.0m)  |  **Median Hold:** 8663s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 60-69%         | 1     | 0     | 1      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 75    | 4     | 71     | 0      | 5.3%      | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 1748  | 411   | 1337   | 0      | 23.5%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1824  | 415   | 1409   | 0      | 22.8%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1824  | 415   | 1409   | 0      | 22.8%     | $-0.2    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 148   | 61    | 87     | 0      | 41.2%     | $1.4     |
| Time Held: 30-90m      | 367   | 44    | 323    | 0      | 12.0%     | $-1.3    |
| Time Held: 90-240m     | 426   | 76    | 350    | 0      | 17.8%     | $-0.8    |
| Time Held: <30m        | 370   | 48    | 322    | 0      | 13.0%     | $-1.2    |
| Time Held: >480m       | 513   | 186   | 327    | 0      | 36.3%     | $1.3     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 183   | 42    | 141    | 0      | 23.0%     | $-0.1    | 🟢          |
| Afternoon (12:00-16:00) | 514   | 120   | 394    | 0      | 23.3%     | $0.1     | 🟢          |
| Morning (10:00-12:00)  | 333   | 110   | 223    | 0      | 33.0%     | $0.6     | 🟢          |
| ORB (9:30-10:00)       | 158   | 31    | 127    | 0      | 19.6%     | $-0.9    | 🔴          |
| Pre-market             | 636   | 112   | 524    | 0      | 17.6%     | $-0.7    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 636    | 635        | 1          | 0          | 99.8%     | 0.2%      | 0.0%      |
| ORB (9:30-10:00)       | 158    | 158        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 333    | 333        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 514    | 514        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| After-hours (16:00-20:00) | 183    | 183        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.8        | ⚠️         |
| Pre-market             | 70-79%     | 50     | 3     | 47     | 0      | 6.0%      | $-1.1        | 🔴          |
| Pre-market             | 80-89%     | 585    | 109   | 476    | 0      | 18.6%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 3      | 0     | 3      | 0      | 0.0%      | $-3.6        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 155    | 31    | 124    | 0      | 20.0%     | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 3      | 0     | 3      | 0      | 0.0%      | $-3.4        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 330    | 110   | 220    | 0      | 33.3%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-3.3        | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 513    | 120   | 393    | 0      | 23.4%     | $0.1         | 🟢          |
| After-hours (16:00-20:00) | 70-79%     | 18     | 1     | 17     | 0      | 5.6%      | $-0.9        | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 165    | 41    | 124    | 0      | 24.8%     | $-0.0        | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 871   | 182   | 689    | 0      | 20.9%     | $-0.8    |
| SHORT        | 953   | 233   | 720    | 0      | 24.4%     | $0.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 44    | 0     | 44     | 0      | 0.0%      | $-2.1    |
| Long (30-60 min)       | 220   | 32    | 188    | 0      | 14.5%     | $-1.1    |
| Medium (5-15 min)      | 139   | 18    | 121    | 0      | 12.9%     | $-1.2    |
| Slow (15-30 min)       | 181   | 29    | 152    | 0      | 16.0%     | $-0.8    |
| Very Fast (<1 min)     | 6     | 1     | 5      | 0      | 16.7%     | $-1.6    |
| Very Long (>1h)        | 1234  | 335   | 899    | 0      | 27.1%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 22.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.21 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 80-89% confidence (23.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (5.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.21) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $1.41) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Morning (10:00-12:00) (33.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (18359s / 306.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,276  |  **Win Rate:** 39.5%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 10756s (179.3m)  |  **Median Hold:** 4128s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 14    | 7     | 7      | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 20-29%         | 52    | 26    | 26     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 299   | 133   | 166    | 0      | 44.5%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 655   | 262   | 393    | 0      | 40.0%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 403   | 169   | 234    | 0      | 41.9%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 1853  | 696   | 1157   | 0      | 37.6%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 3276  | 1293  | 1983   | 0      | 39.5%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1119  | 410   | 709    | 0      | 36.6%     | $0.3     |
| Positive Gamma (Range-Bound friendly) | 2157  | 883   | 1274   | 0      | 40.9%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 285   | 84    | 201    | 0      | 29.5%     | $-0.4    |
| Time Held: 30-90m      | 771   | 310   | 461    | 0      | 40.2%     | $-0.0    |
| Time Held: 90-240m     | 620   | 305   | 315    | 0      | 49.2%     | $0.4     |
| Time Held: <30m        | 1089  | 351   | 738    | 0      | 32.2%     | $-0.2    |
| Time Held: >480m       | 511   | 243   | 268    | 0      | 47.6%     | $0.5     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 552   | 210   | 342    | 0      | 38.0%     | $0.1     | 🔴          |
| Afternoon (12:00-16:00) | 467   | 240   | 227    | 0      | 51.4%     | $0.6     | 🟢          |
| Morning (10:00-12:00)  | 372   | 131   | 241    | 0      | 35.2%     | $-0.2    | 🔴          |
| ORB (9:30-10:00)       | 189   | 60    | 129    | 0      | 31.7%     | $-0.4    | 🔴          |
| Overnight              | 76    | 26    | 50     | 0      | 34.2%     | $-0.5    | 🔴          |
| Pre-market             | 1620  | 626   | 994    | 0      | 38.6%     | $-0.0    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1620   | 0          | 1281       | 339        | 0.0%      | 79.1%     | 20.9%     |
| ORB (9:30-10:00)       | 189    | 0          | 118        | 71         | 0.0%      | 62.4%     | 37.6%     |
| Morning (10:00-12:00)  | 372    | 0          | 171        | 201        | 0.0%      | 46.0%     | 54.0%     |
| Afternoon (12:00-16:00) | 467    | 0          | 181        | 286        | 0.0%      | 38.8%     | 61.2%     |
| After-hours (16:00-20:00) | 552    | 0          | 429        | 123        | 0.0%      | 77.7%     | 22.3%     |
| Overnight              | 76     | 0          | 76         | 0          | 0.0%      | 100.0%    | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 1      | 1     | 0      | 0      | 100.0%    | $3.1         | ⚠️         |
| Pre-market             | 30-39%     | 116    | 43    | 73     | 0      | 37.1%     | $-0.1        | 🔴          |
| Pre-market             | 40-49%     | 222    | 92    | 130    | 0      | 41.4%     | $0.1         | 🟢          |
| Pre-market             | 50-59%     | 153    | 72    | 81     | 0      | 47.1%     | $0.4         | 🟢          |
| Pre-market             | 60-69%     | 1128   | 418   | 710    | 0      | 37.1%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.6        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 20     | 9     | 11     | 0      | 45.0%     | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 50     | 14    | 36     | 0      | 28.0%     | $-0.4        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 43     | 12    | 31     | 0      | 27.9%     | $-0.6        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 75     | 25    | 50     | 0      | 33.3%     | $-0.4        | 🔴          |
| Morning (10:00-12:00)  | 10-19%     | 5      | 3     | 2      | 0      | 60.0%     | $0.4         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 26     | 11    | 15     | 0      | 42.3%     | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 47     | 17    | 30     | 0      | 36.2%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 123    | 42    | 81     | 0      | 34.1%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 70     | 13    | 57     | 0      | 18.6%     | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 101    | 45    | 56     | 0      | 44.6%     | $0.5         | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 9      | 4     | 5      | 0      | 44.4%     | $-0.1        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 24     | 14    | 10     | 0      | 58.3%     | $0.8         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 76     | 36    | 40     | 0      | 47.4%     | $0.1         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 177    | 90    | 87     | 0      | 50.8%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 98     | 56    | 42     | 0      | 57.1%     | $0.9         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 83     | 40    | 43     | 0      | 48.2%     | $0.5         | 🟢          |
| After-hours (16:00-20:00) | 30-39%     | 40     | 28    | 12     | 0      | 70.0%     | $1.1         | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 83     | 24    | 59     | 0      | 28.9%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 39     | 16    | 23     | 0      | 41.0%     | $0.2         | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 390    | 142   | 248    | 0      | 36.4%     | $0.0         | 🔴          |
| Overnight              | 60-69%     | 76     | 26    | 50     | 0      | 34.2%     | $-0.5        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2365  | 920   | 1445   | 0      | 38.9%     | $-0.1    |
| SHORT        | 911   | 373   | 538    | 0      | 40.9%     | $0.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 232   | 69    | 163    | 0      | 29.7%     | $-0.2    |
| Long (30-60 min)       | 437   | 161   | 276    | 0      | 36.8%     | $-0.2    |
| Medium (5-15 min)      | 433   | 139   | 294    | 0      | 32.1%     | $-0.2    |
| Slow (15-30 min)       | 365   | 130   | 235    | 0      | 35.6%     | $-0.1    |
| Very Fast (<1 min)     | 59    | 13    | 46     | 0      | 22.0%     | $-0.5    |
| Very Long (>1h)        | 1750  | 781   | 969    | 0      | 44.6%     | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 39.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.03 — profitable even with 39.5% win rate (good risk/reward).
- 🎯 Best performance at 10-19% confidence (50.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (37.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.04) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $0.48) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (51.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (10756s / 179.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,285  |  **Win Rate:** 30.9%  |  **Avg P&L (resolved):** $-0.0  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 12623s (210.4m)  |  **Median Hold:** 5112s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 1     | 0     | 1      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 20    | 9     | 11     | 0      | 45.0%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 60    | 19    | 41     | 0      | 31.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 521   | 146   | 375    | 0      | 28.0%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 514   | 165   | 349    | 0      | 32.1%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 1297  | 409   | 888    | 0      | 31.5%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 872   | 266   | 606    | 0      | 30.5%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 3285  | 1014  | 2271   | 0      | 30.9%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1038  | 281   | 757    | 0      | 27.1%     | $-0.0    |
| Positive Gamma (Range-Bound friendly) | 2247  | 733   | 1514   | 0      | 32.6%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 237   | 92    | 145    | 0      | 38.8%     | $0.4     |
| Time Held: 30-90m      | 731   | 191   | 540    | 0      | 26.1%     | $-0.3    |
| Time Held: 90-240m     | 678   | 289   | 389    | 0      | 42.6%     | $0.6     |
| Time Held: <30m        | 971   | 209   | 762    | 0      | 21.5%     | $-0.5    |
| Time Held: >480m       | 668   | 233   | 435    | 0      | 34.9%     | $0.1     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 681   | 199   | 482    | 0      | 29.2%     | $-0.2    | 🔴          |
| Afternoon (12:00-16:00) | 330   | 162   | 168    | 0      | 49.1%     | $1.1     | 🟢          |
| Morning (10:00-12:00)  | 283   | 83    | 200    | 0      | 29.3%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 184   | 44    | 140    | 0      | 23.9%     | $-0.6    | 🔴          |
| Overnight              | 8     | 8     | 0      | 0      | 100.0%    | $3.1     | ⚠️         |
| Pre-market             | 1799  | 518   | 1281   | 0      | 28.8%     | $-0.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1799   | 1201       | 568        | 30         | 66.8%     | 31.6%     | 1.7%      |
| ORB (9:30-10:00)       | 184    | 127        | 53         | 4          | 69.0%     | 28.8%     | 2.2%      |
| Morning (10:00-12:00)  | 283    | 186        | 87         | 10         | 65.7%     | 30.7%     | 3.5%      |
| Afternoon (12:00-16:00) | 330    | 162        | 133        | 35         | 49.1%     | 40.3%     | 10.6%     |
| After-hours (16:00-20:00) | 681    | 485        | 194        | 2          | 71.2%     | 28.5%     | 0.3%      |
| Overnight              | 8      | 8          | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 9      | 5     | 4      | 0      | 55.6%     | $1.3         | ⚠️         |
| Pre-market             | 40-49%     | 21     | 8     | 13     | 0      | 38.1%     | $0.4         | ⚠️         |
| Pre-market             | 50-59%     | 266    | 72    | 194    | 0      | 27.1%     | $-0.2        | 🔴          |
| Pre-market             | 60-69%     | 302    | 95    | 207    | 0      | 31.5%     | $0.1         | 🟢          |
| Pre-market             | 70-79%     | 698    | 195   | 503    | 0      | 27.9%     | $-0.2        | 🔴          |
| Pre-market             | 80-89%     | 503    | 143   | 360    | 0      | 28.4%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 2      | 1     | 1      | 0      | 50.0%     | $1.5         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 2      | 1     | 1      | 0      | 50.0%     | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 25     | 4     | 21     | 0      | 16.0%     | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 28     | 9     | 19     | 0      | 32.1%     | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 87     | 20    | 67     | 0      | 23.0%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 80-89%     | 40     | 9     | 31     | 0      | 22.5%     | $-0.8        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 3      | 0     | 3      | 0      | 0.0%      | $-1.5        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 7      | 1     | 6      | 0      | 14.3%     | $-1.1        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 42     | 12    | 30     | 0      | 28.6%     | $-0.0        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 45     | 6     | 39     | 0      | 13.3%     | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 119    | 41    | 78     | 0      | 34.5%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 67     | 23    | 44     | 0      | 34.3%     | $0.3         | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.1        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 6      | 3     | 3      | 0      | 50.0%     | $0.9         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 28     | 9     | 19     | 0      | 32.1%     | $0.2         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 73     | 27    | 46     | 0      | 37.0%     | $0.3         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 60     | 34    | 26     | 0      | 56.7%     | $1.6         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 111    | 62    | 49     | 0      | 55.9%     | $1.6         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 51     | 27    | 24     | 0      | 52.9%     | $1.4         | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.3        | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 115    | 31    | 84     | 0      | 27.0%     | $-0.4        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 79     | 21    | 58     | 0      | 26.6%     | $-0.3        | 🔴          |
| After-hours (16:00-20:00) | 70-79%     | 274    | 83    | 191    | 0      | 30.3%     | $-0.0        | 🔴          |
| After-hours (16:00-20:00) | 80-89%     | 211    | 64    | 147    | 0      | 30.3%     | $-0.2        | 🔴          |
| Overnight              | 70-79%     | 8      | 8     | 0      | 0      | 100.0%    | $3.1         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1647  | 549   | 1098   | 0      | 33.3%     | $-0.0    |
| SHORT        | 1638  | 465   | 1173   | 0      | 28.4%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 206   | 27    | 179    | 0      | 13.1%     | $-1.0    |
| Long (30-60 min)       | 425   | 94    | 331    | 0      | 22.1%     | $-0.5    |
| Medium (5-15 min)      | 380   | 104   | 276    | 0      | 27.4%     | $-0.2    |
| Slow (15-30 min)       | 338   | 72    | 266    | 0      | 21.3%     | $-0.5    |
| Very Fast (<1 min)     | 47    | 6     | 41     | 0      | 12.8%     | $-0.9    |
| Very Long (>1h)        | 1889  | 711   | 1178   | 0      | 37.6%     | $0.3     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.01 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (45.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (28.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.01) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.63) — optimal time held is Time Held: 90-240m.
- ⚠️ Best signal generation window: Overnight (100.0% win rate) — but only 8 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (12623s / 210.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 4,884  |  **Win Rate:** 42.9%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.3  |  **Avg Hold:** 14543s (242.4m)  |  **Median Hold:** 3950s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 80    | 52    | 28     | 0      | 65.0%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 344   | 234   | 110    | 0      | 68.0%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 490   | 375   | 115    | 0      | 76.5%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 348   | 218   | 130    | 0      | 62.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 812   | 327   | 485    | 0      | 40.3%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 706   | 369   | 337    | 0      | 52.3%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 880   | 269   | 611    | 0      | 30.6%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 675   | 214   | 461    | 0      | 31.7%     | $0.0     | $0.0     | 0.0%     |
| 100%           | 549   | 36    | 513    | 0      | 6.6%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 3190  | 1410  | 1780   | 0      | 44.2%     | $-0.2    |
| Trending (Up)        | 1694  | 684   | 1010   | 0      | 40.4%     | $-0.6    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1469  | 439   | 1030   | 0      | 29.9%     | $-1.4    |
| Positive Gamma (Range-Bound friendly) | 3415  | 1655  | 1760   | 0      | 48.5%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 444   | 175   | 269    | 0      | 39.4%     | $0.6     |
| Time Held: 30-90m      | 940   | 403   | 537    | 0      | 42.9%     | $-0.1    |
| Time Held: 90-240m     | 682   | 308   | 374    | 0      | 45.2%     | $0.1     |
| Time Held: <30m        | 1747  | 855   | 892    | 0      | 48.9%     | $-0.3    |
| Time Held: >480m       | 1071  | 353   | 718    | 0      | 33.0%     | $-1.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 1000  | 326   | 674    | 0      | 32.6%     | $-0.8    | 🔴          |
| Afternoon (12:00-16:00) | 926   | 485   | 441    | 0      | 52.4%     | $-0.2    | 🟢          |
| Morning (10:00-12:00)  | 414   | 208   | 206    | 0      | 50.2%     | $-0.6    | 🟢          |
| ORB (9:30-10:00)       | 176   | 97    | 79     | 0      | 55.1%     | $-0.6    | 🟢          |
| Overnight              | 399   | 110   | 289    | 0      | 27.6%     | $-0.4    | 🔴          |
| Pre-market             | 1969  | 868   | 1101   | 0      | 44.1%     | $-0.0    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1969   | 1036       | 503        | 430        | 52.6%     | 25.5%     | 21.8%     |
| ORB (9:30-10:00)       | 176    | 93         | 61         | 22         | 52.8%     | 34.7%     | 12.5%     |
| Morning (10:00-12:00)  | 414    | 322        | 57         | 35         | 77.8%     | 13.8%     | 8.5%      |
| Afternoon (12:00-16:00) | 926    | 551        | 219        | 156        | 59.5%     | 23.7%     | 16.8%     |
| After-hours (16:00-20:00) | 1000   | 603        | 224        | 173        | 60.3%     | 22.4%     | 17.3%     |
| Overnight              | 399    | 205        | 96         | 98         | 51.4%     | 24.1%     | 24.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 48     | 27    | 21     | 0      | 56.2%     | $-0.6        | 🟢          |
| Pre-market             | 30-39%     | 179    | 125   | 54     | 0      | 69.8%     | $0.3         | 🟢          |
| Pre-market             | 40-49%     | 203    | 145   | 58     | 0      | 71.4%     | $3.9         | 🟢          |
| Pre-market             | 50-59%     | 166    | 87    | 79     | 0      | 52.4%     | $-0.8        | 🟢          |
| Pre-market             | 60-69%     | 337    | 133   | 204    | 0      | 39.5%     | $-0.6        | 🔴          |
| Pre-market             | 70-79%     | 279    | 105   | 174    | 0      | 37.6%     | $-0.5        | 🔴          |
| Pre-market             | 80-89%     | 355    | 133   | 222    | 0      | 37.5%     | $-0.1        | 🔴          |
| Pre-market             | 90-99%     | 311    | 91    | 220    | 0      | 29.3%     | $-0.3        | 🔴          |
| Pre-market             | 100%       | 91     | 22    | 69     | 0      | 24.2%     | $-2.5        | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 11     | 10    | 1      | 0      | 90.9%     | $1.2         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 11     | 4     | 7      | 0      | 36.4%     | $-2.4        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 34     | 23    | 11     | 0      | 67.6%     | $0.5         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 27     | 13    | 14     | 0      | 48.1%     | $-0.8        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 34     | 19    | 15     | 0      | 55.9%     | $-0.1        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 19     | 10    | 9      | 0      | 52.6%     | $-0.9        | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 17     | 7     | 10     | 0      | 41.2%     | $-1.6        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 23     | 11    | 12     | 0      | 47.8%     | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 3      | 2     | 1      | 0      | 66.7%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 10     | 8     | 2      | 0      | 80.0%     | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 22     | 14    | 8      | 0      | 63.6%     | $-0.0        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 32     | 29    | 3      | 0      | 90.6%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 25     | 16    | 9      | 0      | 64.0%     | $0.1         | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 119    | 75    | 44     | 0      | 63.0%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 117    | 43    | 74     | 0      | 36.8%     | $-0.4        | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 41     | 18    | 23     | 0      | 43.9%     | $-0.9        | 🟢          |
| Morning (10:00-12:00)  | 100%       | 45     | 3     | 42     | 0      | 6.7%      | $-3.8        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 20     | 14    | 6      | 0      | 70.0%     | $-0.8        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 51     | 42    | 9      | 0      | 82.4%     | $0.7         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 85     | 78    | 7      | 0      | 91.8%     | $2.2         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 90     | 72    | 18     | 0      | 80.0%     | $1.0         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 129    | 60    | 69     | 0      | 46.5%     | $0.1         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 223    | 144   | 79     | 0      | 64.6%     | $0.3         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 142    | 56    | 86     | 0      | 39.4%     | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 46     | 19    | 27     | 0      | 41.3%     | $0.5         | 🔴          |
| Afternoon (12:00-16:00) | 100%       | 140    | 0     | 140    | 0      | 0.0%      | $-3.7        | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 9      | 9     | 0      | 0      | 100.0%    | $1.3         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 93     | 49    | 44     | 0      | 52.7%     | $-2.1        | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 71     | 36    | 35     | 0      | 50.7%     | $-1.9        | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 26     | 7     | 19     | 0      | 26.9%     | $-2.0        | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 198    | 105   | 93     | 0      | 53.0%     | $0.4         | 🟢          |
| After-hours (16:00-20:00) | 70-79%     | 51     | 26    | 25     | 0      | 51.0%     | $0.2         | 🟢          |
| After-hours (16:00-20:00) | 80-89%     | 150    | 27    | 123    | 0      | 18.0%     | $-0.4        | 🔴          |
| After-hours (16:00-20:00) | 90-99%     | 248    | 67    | 181    | 0      | 27.0%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 100%       | 154    | 0     | 154    | 0      | 0.0%      | $-3.0        | 🔴          |
| Overnight              | 40-49%     | 98     | 98    | 0      | 0      | 100.0%    | $2.2         | 🟢          |
| Overnight              | 60-69%     | 96     | 0     | 96     | 0      | 0.0%      | $-0.4        | 🔴          |
| Overnight              | 80-89%     | 97     | 0     | 97     | 0      | 0.0%      | $-1.1        | 🔴          |
| Overnight              | 90-99%     | 12     | 12    | 0      | 0      | 100.0%    | $0.5         | ⚠️         |
| Overnight              | 100%       | 96     | 0     | 96     | 0      | 0.0%      | $-2.7        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2541  | 1009  | 1532   | 0      | 39.7%     | $-0.6    |
| SHORT        | 2343  | 1085  | 1258   | 0      | 46.3%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 411   | 227   | 184    | 0      | 55.2%     | $-0.2    |
| Long (30-60 min)       | 618   | 258   | 360    | 0      | 41.7%     | $0.0     |
| Medium (5-15 min)      | 648   | 265   | 383    | 0      | 40.9%     | $-0.4    |
| Slow (15-30 min)       | 526   | 226   | 300    | 0      | 43.0%     | $-0.3    |
| Very Fast (<1 min)     | 162   | 137   | 25     | 0      | 84.6%     | $0.0     |
| Very Long (>1h)        | 2519  | 981   | 1538   | 0      | 38.9%     | $-0.4    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 42.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.31 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (76.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 100% (6.6% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.17) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $0.62) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: ORB (9:30-10:00) (55.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (14543s / 242.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_squeeze

**Symbols:** INTC, NVDA, TSLA  |  **Total Signals:** 493  |  **Win Rate:** 40.6%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 10478s (174.6m)  |  **Median Hold:** 3914s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 270   | 56    | 214    | 0      | 20.7%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 77    | 29    | 48     | 0      | 37.7%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 50    | 40    | 10     | 0      | 80.0%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 95    | 74    | 21     | 0      | 77.9%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 1     | 1     | 0      | 0      | 100.0%    | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 288   | 116   | 172    | 0      | 40.3%     | $0.0     |
| Trending (Up)        | 205   | 84    | 121    | 0      | 41.0%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 347   | 85    | 262    | 0      | 24.5%     | $-0.5    |
| Positive Gamma (Range-Bound friendly) | 146   | 115   | 31     | 0      | 78.8%     | $1.3     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 33    | 15    | 18     | 0      | 45.5%     | $-0.3    |
| Time Held: 30-90m      | 101   | 48    | 53     | 0      | 47.5%     | $0.4     |
| Time Held: 90-240m     | 118   | 73    | 45     | 0      | 61.9%     | $1.1     |
| Time Held: <30m        | 166   | 38    | 128    | 0      | 22.9%     | $-0.7    |
| Time Held: >480m       | 75    | 26    | 49     | 0      | 34.7%     | $-0.5    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 48    | 5     | 43     | 0      | 10.4%     | $-1.9    | 🔴          |
| Afternoon (12:00-16:00) | 151   | 95    | 56     | 0      | 62.9%     | $1.5     | 🟢          |
| Morning (10:00-12:00)  | 105   | 32    | 73     | 0      | 30.5%     | $-0.3    | 🔴          |
| ORB (9:30-10:00)       | 42    | 9     | 33     | 0      | 21.4%     | $-0.6    | 🔴          |
| Pre-market             | 147   | 59    | 88     | 0      | 40.1%     | $-0.5    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 147    | 0          | 62         | 85         | 0.0%      | 42.2%     | 57.8%     |
| ORB (9:30-10:00)       | 42     | 0          | 16         | 26         | 0.0%      | 38.1%     | 61.9%     |
| Morning (10:00-12:00)  | 105    | 0          | 36         | 69         | 0.0%      | 34.3%     | 65.7%     |
| Afternoon (12:00-16:00) | 151    | 1          | 31         | 119        | 0.7%      | 20.5%     | 78.8%     |
| After-hours (16:00-20:00) | 48     | 0          | 0          | 48         | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 82     | 4     | 78     | 0      | 4.9%      | $-2.0        | 🔴          |
| Pre-market             | 30-39%     | 3      | 0     | 3      | 0      | 0.0%      | $-2.7        | ⚠️         |
| Pre-market             | 50-59%     | 27     | 26    | 1      | 0      | 96.3%     | $2.1         | ⚠️         |
| Pre-market             | 60-69%     | 35     | 29    | 6      | 0      | 82.9%     | $1.3         | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 26     | 1     | 25     | 0      | 3.8%      | $-1.4        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 3      | 2     | 1      | 0      | 66.7%     | $1.3         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 13     | 6     | 7      | 0      | 46.2%     | $0.6         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 58     | 12    | 46     | 0      | 20.7%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 11     | 0     | 11     | 0      | 0.0%      | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 10     | 2     | 8      | 0      | 20.0%     | $-0.6        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 26     | 18    | 8      | 0      | 69.2%     | $0.8         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 61     | 36    | 25     | 0      | 59.0%     | $1.7         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 58     | 27    | 31     | 0      | 46.6%     | $0.9         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 10     | 10    | 0      | 0      | 100.0%    | $2.4         | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 21     | 21    | 0      | 0      | 100.0%    | $2.0         | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 1      | 1     | 0      | 0      | 100.0%    | $2.5         | ⚠️         |
| After-hours (16:00-20:00) | 20-29%     | 43     | 3     | 40     | 0      | 7.0%      | $-2.2        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 5      | 2     | 3      | 0      | 40.0%     | $0.6         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 146   | 115   | 31     | 0      | 78.8%     | $1.3     |
| SHORT        | 347   | 85    | 262    | 0      | 24.5%     | $-0.5    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 36    | 5     | 31     | 0      | 13.9%     | $-0.7    |
| Long (30-60 min)       | 68    | 22    | 46     | 0      | 32.4%     | $-0.3    |
| Medium (5-15 min)      | 69    | 16    | 53     | 0      | 23.2%     | $-0.7    |
| Slow (15-30 min)       | 53    | 14    | 39     | 0      | 26.4%     | $-0.6    |
| Very Fast (<1 min)     | 8     | 3     | 5      | 0      | 37.5%     | $-0.0    |
| Very Long (>1h)        | 259   | 140   | 119    | 0      | 54.1%     | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 40.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.02 — profitable even with 40.6% win rate (good risk/reward).
- 🎯 Best performance at 50-59% confidence (80.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (20.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.03) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $1.10) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (62.9% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (10478s / 174.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,465  |  **Win Rate:** 47.8%  |  **Avg P&L (resolved):** $0.3  |  **Avg P&L (all):** $0.3  |  **Avg Hold:** 19928s (332.1m)  |  **Median Hold:** 10350s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 220   | 69    | 151    | 0      | 31.4%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 378   | 150   | 228    | 0      | 39.7%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 393   | 233   | 160    | 0      | 59.3%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 375   | 156   | 219    | 0      | 41.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 477   | 389   | 88     | 0      | 81.6%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 90    | 46    | 44     | 0      | 51.1%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 51    | 23    | 28     | 0      | 45.1%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 30    | 9     | 21     | 0      | 30.0%     | $0.0     | $0.0     | 0.0%     |
| 100%           | 451   | 104   | 347    | 0      | 23.1%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1665  | 879   | 786    | 0      | 52.8%     | $0.5     |
| Trending (Up)        | 800   | 300   | 500    | 0      | 37.5%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 412   | 141   | 271    | 0      | 34.2%     | $-0.4    |
| Positive Gamma (Range-Bound friendly) | 2053  | 1038  | 1015   | 0      | 50.6%     | $0.5     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 320   | 211   | 109    | 0      | 65.9%     | $0.9     |
| Time Held: 30-90m      | 469   | 211   | 258    | 0      | 45.0%     | $0.3     |
| Time Held: 90-240m     | 616   | 401   | 215    | 0      | 65.1%     | $1.2     |
| Time Held: <30m        | 385   | 120   | 265    | 0      | 31.2%     | $-0.5    |
| Time Held: >480m       | 675   | 236   | 439    | 0      | 35.0%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 456   | 155   | 301    | 0      | 34.0%     | $-0.3    | 🔴          |
| Afternoon (12:00-16:00) | 374   | 207   | 167    | 0      | 55.3%     | $0.9     | 🟢          |
| Morning (10:00-12:00)  | 316   | 86    | 230    | 0      | 27.2%     | $-0.5    | 🔴          |
| ORB (9:30-10:00)       | 106   | 16    | 90     | 0      | 15.1%     | $-1.2    | 🔴          |
| Overnight              | 167   | 167   | 0      | 0      | 100.0%    | $2.2     | 🟢          |
| Pre-market             | 1046  | 548   | 498    | 0      | 52.4%     | $0.5     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1046   | 161        | 453        | 432        | 15.4%     | 43.3%     | 41.3%     |
| ORB (9:30-10:00)       | 106    | 40         | 22         | 44         | 37.7%     | 20.8%     | 41.5%     |
| Morning (10:00-12:00)  | 316    | 109        | 62         | 145        | 34.5%     | 19.6%     | 45.9%     |
| Afternoon (12:00-16:00) | 374    | 163        | 67         | 144        | 43.6%     | 17.9%     | 38.5%     |
| After-hours (16:00-20:00) | 456    | 149        | 81         | 226        | 32.7%     | 17.8%     | 49.6%     |
| Overnight              | 167    | 0          | 167        | 0          | 0.0%      | 100.0%    | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 59     | 1     | 58     | 0      | 1.7%      | $-2.5        | 🔴          |
| Pre-market             | 30-39%     | 152    | 65    | 87     | 0      | 42.8%     | $0.1         | 🔴          |
| Pre-market             | 40-49%     | 221    | 145   | 76     | 0      | 65.6%     | $1.4         | 🟢          |
| Pre-market             | 50-59%     | 197    | 65    | 132    | 0      | 33.0%     | $-0.1        | 🔴          |
| Pre-market             | 60-69%     | 256    | 186   | 70     | 0      | 72.7%     | $1.3         | 🟢          |
| Pre-market             | 70-79%     | 64     | 34    | 30     | 0      | 53.1%     | $0.4         | 🟢          |
| Pre-market             | 80-89%     | 12     | 11    | 1      | 0      | 91.7%     | $1.4         | ⚠️         |
| Pre-market             | 90-99%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.7        | ⚠️         |
| Pre-market             | 100%       | 83     | 41    | 42     | 0      | 49.4%     | $0.3         | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 8      | 1     | 7      | 0      | 12.5%     | $-1.7        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 19     | 1     | 18     | 0      | 5.3%      | $-1.7        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 17     | 1     | 16     | 0      | 5.9%      | $-1.9        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 14     | 1     | 13     | 0      | 7.1%      | $-1.7        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 8      | 3     | 5      | 0      | 37.5%     | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 6      | 1     | 5      | 0      | 16.7%     | $-1.4        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.2        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 33     | 8     | 25     | 0      | 24.2%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 20-29%     | 35     | 21    | 14     | 0      | 60.0%     | $1.5         | 🟢          |
| Morning (10:00-12:00)  | 30-39%     | 54     | 14    | 40     | 0      | 25.9%     | $-0.6        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 56     | 7     | 49     | 0      | 12.5%     | $-1.3        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 35     | 0     | 35     | 0      | 0.0%      | $-1.8        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 27     | 14    | 13     | 0      | 51.9%     | $0.2         | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 14     | 9     | 5      | 0      | 64.3%     | $0.8         | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 3      | 3     | 0      | 0      | 100.0%    | $1.9         | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 1      | 1     | 0      | 0      | 100.0%    | $1.6         | ⚠️         |
| Morning (10:00-12:00)  | 100%       | 91     | 17    | 74     | 0      | 18.7%     | $-0.8        | 🔴          |
| Afternoon (12:00-16:00) | 20-29%     | 45     | 42    | 3      | 0      | 93.3%     | $3.4         | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 51     | 48    | 3      | 0      | 94.1%     | $2.8         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 48     | 32    | 16     | 0      | 66.7%     | $1.5         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 57     | 18    | 39     | 0      | 31.6%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 10     | 10    | 0      | 0      | 100.0%    | $2.4         | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 6      | 2     | 4      | 0      | 33.3%     | $-0.3        | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 35     | 9     | 26     | 0      | 25.7%     | $-0.6        | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 27     | 8     | 19     | 0      | 29.6%     | $-0.4        | ⚠️         |
| Afternoon (12:00-16:00) | 100%       | 95     | 38    | 57     | 0      | 40.0%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 20-29%     | 73     | 4     | 69     | 0      | 5.5%      | $-2.4        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 102    | 22    | 80     | 0      | 21.6%     | $-1.1        | 🔴          |
| After-hours (16:00-20:00) | 40-49%     | 51     | 48    | 3      | 0      | 94.1%     | $2.9         | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 72     | 72    | 0      | 0      | 100.0%    | $2.8         | 🟢          |
| After-hours (16:00-20:00) | 60-69%     | 9      | 9     | 0      | 0      | 100.0%    | $2.4         | ⚠️         |
| After-hours (16:00-20:00) | 100%       | 149    | 0     | 149    | 0      | 0.0%      | $-1.5        | 🔴          |
| Overnight              | 60-69%     | 167    | 167   | 0      | 0      | 100.0%    | $2.2         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1198  | 890   | 308    | 0      | 74.3%     | $1.5     |
| SHORT        | 1267  | 289   | 978    | 0      | 22.8%     | $-0.7    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 49    | 15    | 34     | 0      | 30.6%     | $-0.3    |
| Long (30-60 min)       | 271   | 110   | 161    | 0      | 40.6%     | $0.2     |
| Medium (5-15 min)      | 136   | 37    | 99     | 0      | 27.2%     | $-0.8    |
| Slow (15-30 min)       | 192   | 64    | 128    | 0      | 33.3%     | $-0.5    |
| Very Fast (<1 min)     | 8     | 4     | 4      | 0      | 50.0%     | $0.7     |
| Very Long (>1h)        | 1809  | 949   | 860    | 0      | 52.5%     | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 47.8% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.34 — profitable even with 47.8% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (81.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 100% (23.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.53) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $1.16) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Overnight (100.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (19928s / 332.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### gex_divergence

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,113  |  **Win Rate:** 43.2%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 5963s (99.4m)  |  **Median Hold:** 3147s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 15    | 1     | 14     | 0      | 6.7%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 35    | 11    | 24     | 0      | 31.4%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 129   | 71    | 58     | 0      | 55.0%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 301   | 92    | 209    | 0      | 30.6%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 561   | 278   | 283    | 0      | 49.6%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 60    | 26    | 34     | 0      | 43.3%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 7     | 1     | 6      | 0      | 14.3%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 5     | 1     | 4      | 0      | 20.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 828   | 351   | 477    | 0      | 42.4%     | $-0.1    |
| Trending (Up)        | 285   | 130   | 155    | 0      | 45.6%     | $0.3     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 233   | 145   | 88     | 0      | 62.2%     | $1.3     |
| Positive Gamma (Range-Bound friendly) | 880   | 336   | 544    | 0      | 38.2%     | $-0.3    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 34    | 34    | 0      | 0      | 100.0%    | $2.5     |
| Time Held: 30-90m      | 367   | 159   | 208    | 0      | 43.3%     | $-0.0    |
| Time Held: 90-240m     | 247   | 146   | 101    | 0      | 59.1%     | $0.7     |
| Time Held: <30m        | 412   | 127   | 285    | 0      | 30.8%     | $-0.4    |
| Time Held: >480m       | 53    | 15    | 38     | 0      | 28.3%     | $-1.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 63    | 3     | 60     | 0      | 4.8%      | $-2.2    | 🔴          |
| Afternoon (12:00-16:00) | 316   | 159   | 157    | 0      | 50.3%     | $0.5     | 🟢          |
| Morning (10:00-12:00)  | 275   | 85    | 190    | 0      | 30.9%     | $-0.4    | 🔴          |
| ORB (9:30-10:00)       | 70    | 30    | 40     | 0      | 42.9%     | $0.2     | 🔴          |
| Pre-market             | 389   | 204   | 185    | 0      | 52.4%     | $0.3     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 389    | 4          | 241        | 144        | 1.0%      | 62.0%     | 37.0%     |
| ORB (9:30-10:00)       | 70     | 19         | 49         | 2          | 27.1%     | 70.0%     | 2.9%      |
| Morning (10:00-12:00)  | 275    | 34         | 240        | 1          | 12.4%     | 87.3%     | 0.4%      |
| Afternoon (12:00-16:00) | 316    | 12         | 284        | 20         | 3.8%      | 89.9%     | 6.3%      |
| After-hours (16:00-20:00) | 63     | 3          | 48         | 12         | 4.8%      | 76.2%     | 19.0%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 15     | 1     | 14     | 0      | 6.7%      | $-2.1        | ⚠️         |
| Pre-market             | 30-39%     | 34     | 11    | 23     | 0      | 32.4%     | $-0.8        | 🔴          |
| Pre-market             | 40-49%     | 95     | 61    | 34     | 0      | 64.2%     | $0.9         | 🟢          |
| Pre-market             | 50-59%     | 144    | 66    | 78     | 0      | 45.8%     | $0.1         | 🟢          |
| Pre-market             | 60-69%     | 97     | 63    | 34     | 0      | 64.9%     | $0.7         | 🟢          |
| Pre-market             | 70-79%     | 4      | 2     | 2      | 0      | 50.0%     | $0.2         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 2      | 1     | 1      | 0      | 50.0%     | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 9      | 5     | 4      | 0      | 55.6%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 40     | 13    | 27     | 0      | 32.5%     | $-0.3        | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 14     | 9     | 5      | 0      | 64.3%     | $1.5         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 2      | 1     | 1      | 0      | 50.0%     | $1.6         | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 3      | 1     | 2      | 0      | 33.3%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 1      | 1     | 0      | 0      | 100.0%    | $3.8         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 62     | 18    | 44     | 0      | 29.0%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 178    | 59    | 119    | 0      | 33.1%     | $-0.4        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 27     | 7     | 20     | 0      | 25.9%     | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 5      | 0     | 5      | 0      | 0.0%      | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.5        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 20     | 8     | 12     | 0      | 40.0%     | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 53     | 1     | 52     | 0      | 1.9%      | $-1.5        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 231    | 142   | 89     | 0      | 61.5%     | $0.9         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 12     | 8     | 4      | 0      | 66.7%     | $0.5         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-2.5        | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 11     | 0     | 11     | 0      | 0.0%      | $-2.4        | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 33     | 2     | 31     | 0      | 6.1%      | $-2.2        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 15     | 1     | 14     | 0      | 6.7%      | $-2.2        | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 3      | 0     | 3      | 0      | 0.0%      | $-2.5        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 822   | 340   | 482    | 0      | 41.4%     | $-0.2    |
| SHORT        | 291   | 141   | 150    | 0      | 48.5%     | $0.5     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 74    | 23    | 51     | 0      | 31.1%     | $-0.4    |
| Long (30-60 min)       | 203   | 93    | 110    | 0      | 45.8%     | $0.0     |
| Medium (5-15 min)      | 156   | 53    | 103    | 0      | 34.0%     | $-0.2    |
| Slow (15-30 min)       | 172   | 48    | 124    | 0      | 27.9%     | $-0.6    |
| Very Fast (<1 min)     | 10    | 3     | 7      | 0      | 30.0%     | $-0.3    |
| Very Long (>1h)        | 498   | 261   | 237    | 0      | 52.4%     | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 43.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.02 — profitable even with 43.2% win rate (good risk/reward).
- 🎯 Best performance at 40-49% confidence (55.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (6.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.31) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $2.49) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Pre-market (52.4% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (5963s / 99.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### magnet_accelerate

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 6,704  |  **Win Rate:** 31.1%  |  **Avg P&L (resolved):** $1.1  |  **Avg P&L (all):** $1.1  |  **Avg Hold:** 11285s (188.1m)  |  **Median Hold:** 4744s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 41    | 1     | 40     | 0      | 2.4%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 1098  | 508   | 590    | 0      | 46.3%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 514   | 138   | 376    | 0      | 26.8%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 1650  | 562   | 1088   | 0      | 34.1%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 1310  | 652   | 658    | 0      | 49.8%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 716   | 110   | 606    | 0      | 15.4%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 259   | 42    | 217    | 0      | 16.2%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 192   | 68    | 124    | 0      | 35.4%     | $0.0     | $0.0     | 0.0%     |
| 100%           | 924   | 2     | 922    | 0      | 0.2%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 5049  | 1746  | 3303   | 0      | 34.6%     | $1.2     |
| Trending (Up)        | 1655  | 337   | 1318   | 0      | 20.4%     | $0.5     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 1441  | 135   | 1306   | 0      | 9.4%      | $0.6     |
| Positive Gamma (Range-Bound friendly) | 5263  | 1948  | 3315   | 0      | 37.0%     | $1.2     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 1121  | 609   | 512    | 0      | 54.3%     | $2.3     |
| Time Held: 30-90m      | 1048  | 168   | 880    | 0      | 16.0%     | $-0.2    |
| Time Held: 90-240m     | 1239  | 432   | 807    | 0      | 34.9%     | $1.1     |
| Time Held: <30m        | 2422  | 233   | 2189   | 0      | 9.6%      | $0.1     |
| Time Held: >480m       | 874   | 641   | 233    | 0      | 73.3%     | $3.6     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 932   | 249   | 683    | 0      | 26.7%     | $0.9     | 🔴          |
| Afternoon (12:00-16:00) | 660   | 76    | 584    | 0      | 11.5%     | $0.4     | 🔴          |
| Morning (10:00-12:00)  | 230   | 29    | 201    | 0      | 12.6%     | $0.1     | 🔴          |
| ORB (9:30-10:00)       | 144   | 30    | 114    | 0      | 20.8%     | $-0.4    | 🔴          |
| Overnight              | 1427  | 715   | 712    | 0      | 50.1%     | $2.3     | 🟢          |
| Pre-market             | 3311  | 984   | 2327   | 0      | 29.7%     | $0.8     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 3311   | 1088       | 1431       | 792        | 32.9%     | 43.2%     | 23.9%     |
| ORB (9:30-10:00)       | 144    | 84         | 45         | 15         | 58.3%     | 31.2%     | 10.4%     |
| Morning (10:00-12:00)  | 230    | 86         | 95         | 49         | 37.4%     | 41.3%     | 21.3%     |
| Afternoon (12:00-16:00) | 660    | 335        | 264        | 61         | 50.8%     | 40.0%     | 9.2%      |
| After-hours (16:00-20:00) | 932    | 261        | 509        | 162        | 28.0%     | 54.6%     | 17.4%     |
| Overnight              | 1427   | 237        | 616        | 574        | 16.6%     | 43.2%     | 40.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 41     | 1     | 40     | 0      | 2.4%      | $-1.7        | 🔴          |
| Pre-market             | 30-39%     | 565    | 250   | 315    | 0      | 44.2%     | $0.7         | 🟢          |
| Pre-market             | 40-49%     | 186    | 20    | 166    | 0      | 10.8%     | $-0.5        | 🔴          |
| Pre-market             | 50-59%     | 777    | 314   | 463    | 0      | 40.4%     | $1.4         | 🟢          |
| Pre-market             | 60-69%     | 654    | 316   | 338    | 0      | 48.3%     | $2.4         | 🟢          |
| Pre-market             | 70-79%     | 433    | 31    | 402    | 0      | 7.2%      | $-0.7        | 🔴          |
| Pre-market             | 80-89%     | 155    | 20    | 135    | 0      | 12.9%     | $-0.8        | 🔴          |
| Pre-market             | 90-99%     | 73     | 31    | 42     | 0      | 42.5%     | $0.2         | 🟢          |
| Pre-market             | 100%       | 427    | 1     | 426    | 0      | 0.2%      | $0.5         | 🔴          |
| ORB (9:30-10:00)       | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.9        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 14     | 0     | 14     | 0      | 0.0%      | $-2.2        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 19     | 0     | 19     | 0      | 0.0%      | $-2.6        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 26     | 6     | 20     | 0      | 23.1%     | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 33     | 11    | 22     | 0      | 33.3%     | $-0.1        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 22     | 11    | 11     | 0      | 50.0%     | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 7      | 1     | 6      | 0      | 14.3%     | $-0.0        | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 22     | 1     | 21     | 0      | 4.5%      | $2.0         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 4      | 0     | 4      | 0      | 0.0%      | $-0.9        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 45     | 0     | 45     | 0      | 0.0%      | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 58     | 0     | 58     | 0      | 0.0%      | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 37     | 2     | 35     | 0      | 5.4%      | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 30     | 20    | 10     | 0      | 66.7%     | $0.7         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 5      | 5     | 0      | 0      | 100.0%    | $1.9         | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 2      | 2     | 0      | 0      | 100.0%    | $0.4         | ⚠️         |
| Morning (10:00-12:00)  | 100%       | 49     | 0     | 49     | 0      | 0.0%      | $2.5         | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 3      | 0     | 3      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 58     | 7     | 51     | 0      | 12.1%     | $0.1         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 119    | 16    | 103    | 0      | 13.4%     | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 145    | 11    | 134    | 0      | 7.6%      | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 184    | 33    | 151    | 0      | 17.9%     | $0.6         | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 50     | 6     | 44     | 0      | 12.0%     | $0.3         | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 25     | 3     | 22     | 0      | 12.0%     | $0.8         | ⚠️         |
| Afternoon (12:00-16:00) | 100%       | 76     | 0     | 76     | 0      | 0.0%      | $1.9         | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 49     | 20    | 29     | 0      | 40.8%     | $0.6         | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 113    | 13    | 100    | 0      | 11.5%     | $0.3         | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 311    | 90    | 221    | 0      | 28.9%     | $1.1         | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 198    | 80    | 118    | 0      | 40.4%     | $1.9         | 🟢          |
| After-hours (16:00-20:00) | 70-79%     | 36     | 15    | 21     | 0      | 41.7%     | $1.7         | 🟢          |
| After-hours (16:00-20:00) | 80-89%     | 27     | 0     | 27     | 0      | 0.0%      | $-0.4        | ⚠️         |
| After-hours (16:00-20:00) | 90-99%     | 85     | 31    | 54     | 0      | 36.5%     | $-0.1        | 🟢          |
| After-hours (16:00-20:00) | 100%       | 113    | 0     | 113    | 0      | 0.0%      | $0.2         | 🔴          |
| Overnight              | 30-39%     | 476    | 238   | 238    | 0      | 50.0%     | $0.9         | 🟢          |
| Overnight              | 40-49%     | 98     | 98    | 0      | 0      | 100.0%    | $4.8         | 🟢          |
| Overnight              | 50-59%     | 366    | 142   | 224    | 0      | 38.8%     | $1.6         | 🟢          |
| Overnight              | 60-69%     | 250    | 237   | 13     | 0      | 94.8%     | $6.6         | 🟢          |
| Overnight              | 100%       | 237    | 0     | 237    | 0      | 0.0%      | $0.3         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 4398  | 1426  | 2972   | 0      | 32.4%     | $0.9     |
| SHORT        | 2306  | 657   | 1649   | 0      | 28.5%     | $1.4     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 292   | 49    | 243    | 0      | 16.8%     | $-0.5    |
| Long (30-60 min)       | 645   | 85    | 560    | 0      | 13.2%     | $-0.4    |
| Medium (5-15 min)      | 506   | 72    | 434    | 0      | 14.2%     | $-0.6    |
| Slow (15-30 min)       | 448   | 57    | 391    | 0      | 12.7%     | $-0.5    |
| Very Fast (<1 min)     | 1176  | 55    | 1121   | 0      | 4.7%      | $0.8     |
| Very Long (>1h)        | 3637  | 1765  | 1872   | 0      | 48.5%     | $1.9     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 31.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $1.05 — profitable even with 31.1% win rate (good risk/reward).
- 🎯 Best performance at 60-69% confidence (49.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 100% (0.2% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $1.23) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: >480m (avg P&L $3.56) — optimal time held is Time Held: >480m.
- ✅ Best signal generation window: Overnight (50.1% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (11285s / 188.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### strike_concentration

**Symbols:** AAPL, AMD, NVDA  |  **Total Signals:** 443  |  **Win Rate:** 39.5%  |  **Avg P&L (resolved):** $-0.0  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 4825s (80.4m)  |  **Median Hold:** 3011s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 1     | 0     | 1      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 30    | 15    | 15     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 275   | 89    | 186    | 0      | 32.4%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 92    | 46    | 46     | 0      | 50.0%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 41    | 25    | 16     | 0      | 61.0%     | $0.0     | $0.0     | 0.0%     |
| 80-89%         | 4     | 0     | 4      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 259   | 95    | 164    | 0      | 36.7%     | $-0.1    |
| Trending (Up)        | 184   | 80    | 104    | 0      | 43.5%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 443   | 175   | 268    | 0      | 39.5%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 23    | 5     | 18     | 0      | 21.7%     | $-0.6    |
| Time Held: 30-90m      | 158   | 61    | 97     | 0      | 38.6%     | $0.1     |
| Time Held: 90-240m     | 112   | 60    | 52     | 0      | 53.6%     | $0.6     |
| Time Held: <30m        | 148   | 47    | 101    | 0      | 31.8%     | $-0.5    |
| Time Held: >480m       | 2     | 2     | 0      | 0      | 100.0%    | $4.4     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 19    | 19    | 0      | 0      | 100.0%    | $2.0     | ⚠️         |
| Morning (10:00-12:00)  | 82    | 37    | 45     | 0      | 45.1%     | $0.1     | 🟢          |
| ORB (9:30-10:00)       | 49    | 14    | 35     | 0      | 28.6%     | $-0.4    | 🔴          |
| Pre-market             | 293   | 105   | 188    | 0      | 35.8%     | $-0.1    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 293    | 3          | 269        | 21         | 1.0%      | 91.8%     | 7.2%      |
| ORB (9:30-10:00)       | 49     | 27         | 20         | 2          | 55.1%     | 40.8%     | 4.1%      |
| Morning (10:00-12:00)  | 82     | 15         | 64         | 3          | 18.3%     | 78.0%     | 3.7%      |
| Afternoon (12:00-16:00) | 19     | 0          | 14         | 5          | 0.0%      | 73.7%     | 26.3%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Pre-market             | 40-49%     | 20     | 9     | 11     | 0      | 45.0%     | $0.4         | ⚠️         |
| Pre-market             | 50-59%     | 221    | 75    | 146    | 0      | 33.9%     | $-0.2        | 🔴          |
| Pre-market             | 60-69%     | 48     | 21    | 27     | 0      | 43.8%     | $0.1         | 🟢          |
| Pre-market             | 70-79%     | 3      | 0     | 3      | 0      | 0.0%      | $-1.3        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.6        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 12     | 0     | 12     | 0      | 0.0%      | $-1.3        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 8      | 2     | 6      | 0      | 25.0%     | $-0.3        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 23     | 12    | 11     | 0      | 52.2%     | $0.2         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 4      | 0     | 4      | 0      | 0.0%      | $-1.0        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 3      | 1     | 2      | 0      | 33.3%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 33     | 5     | 28     | 0      | 15.2%     | $-0.9        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 31     | 18    | 13     | 0      | 58.1%     | $0.6         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 15     | 13    | 2      | 0      | 86.7%     | $1.6         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 5      | 5     | 0      | 0      | 100.0%    | $2.7         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 9      | 9     | 0      | 0      | 100.0%    | $1.9         | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 5      | 5     | 0      | 0      | 100.0%    | $1.4         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 235   | 135   | 100    | 0      | 57.4%     | $0.5     |
| SHORT        | 208   | 40    | 168    | 0      | 19.2%     | $-0.6    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 21    | 6     | 15     | 0      | 28.6%     | $-0.5    |
| Long (30-60 min)       | 95    | 37    | 58     | 0      | 38.9%     | $0.1     |
| Medium (5-15 min)      | 58    | 17    | 41     | 0      | 29.3%     | $-0.9    |
| Slow (15-30 min)       | 63    | 22    | 41     | 0      | 34.9%     | $-0.2    |
| Very Fast (<1 min)     | 6     | 2     | 4      | 0      | 33.3%     | $-0.7    |
| Very Long (>1h)        | 200   | 91    | 109    | 0      | 45.5%     | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 39.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.00 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 70-79% confidence (61.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (32.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.14) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.64) — optimal time held is Time Held: 90-240m.
- ⚠️ Best signal generation window: Afternoon (12:00-16:00) (100.0% win rate) — but only 19 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (4825s / 80.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### theta_burn

**Symbols:** AMD, INTC, TSLA  |  **Total Signals:** 142  |  **Win Rate:** 5.6%  |  **Avg P&L (resolved):** $-0.0  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 643s (10.7m)  |  **Median Hold:** 1s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 50    | 2     | 48     | 0      | 4.0%      | $0.0     | $0.0     | 0.0%     |
| 20-29%         | 78    | 3     | 75     | 0      | 3.8%      | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 14    | 3     | 11     | 0      | 21.4%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 89    | 6     | 83     | 0      | 6.7%      | $-0.0    |
| Trending (Up)        | 53    | 2     | 51     | 0      | 3.8%      | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Negative Gamma (Volatile/Breakout friendly) | 142   | 8     | 134    | 0      | 5.6%      | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 19    | 3     | 16     | 0      | 15.8%     | $-0.2    |
| Time Held: <30m        | 123   | 5     | 118    | 0      | 4.1%      | $0.0     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 5     | 0     | 5      | 0      | 0.0%      | $0.0     | ⚠️         |
| Afternoon (12:00-16:00) | 20    | 3     | 17     | 0      | 15.0%     | $0.6     | ⚠️         |
| Morning (10:00-12:00)  | 25    | 1     | 24     | 0      | 4.0%      | $0.1     | ⚠️         |
| ORB (9:30-10:00)       | 22    | 2     | 20     | 0      | 9.1%      | $-0.2    | ⚠️         |
| Pre-market             | 70    | 2     | 68     | 0      | 2.9%      | $-0.2    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 70     | 0          | 0          | 70         | 0.0%      | 0.0%      | 100.0%    |
| ORB (9:30-10:00)       | 22     | 0          | 0          | 22         | 0.0%      | 0.0%      | 100.0%    |
| Morning (10:00-12:00)  | 25     | 0          | 0          | 25         | 0.0%      | 0.0%      | 100.0%    |
| Afternoon (12:00-16:00) | 20     | 0          | 0          | 20         | 0.0%      | 0.0%      | 100.0%    |
| After-hours (16:00-20:00) | 5      | 0          | 0          | 5          | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 10-19%     | 11     | 0     | 11     | 0      | 0.0%      | $-0.2        | ⚠️         |
| Pre-market             | 20-29%     | 59     | 2     | 57     | 0      | 3.4%      | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 10-19%     | 11     | 1     | 10     | 0      | 9.1%      | $-0.1        | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 11     | 1     | 10     | 0      | 9.1%      | $-0.3        | ⚠️         |
| Morning (10:00-12:00)  | 10-19%     | 23     | 1     | 22     | 0      | 4.3%      | $0.1         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 2      | 0     | 2      | 0      | 0.0%      | $0.3         | ⚠️         |
| Afternoon (12:00-16:00) | 10-19%     | 2      | 0     | 2      | 0      | 0.0%      | $0.4         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 4      | 0     | 4      | 0      | 0.0%      | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 14     | 3     | 11     | 0      | 21.4%     | $0.7         | ⚠️         |
| After-hours (16:00-20:00) | 10-19%     | 3      | 0     | 3      | 0      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 20-29%     | 2      | 0     | 2      | 0      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| SHORT        | 142   | 8     | 134    | 0      | 5.6%      | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 11    | 0     | 11     | 0      | 0.0%      | $-1.0    |
| Long (30-60 min)       | 4     | 3     | 1      | 0      | 75.0%     | $0.7     |
| Medium (5-15 min)      | 12    | 0     | 12     | 0      | 0.0%      | $-0.9    |
| Slow (15-30 min)       | 7     | 2     | 5      | 0      | 28.6%     | $-0.3    |
| Very Fast (<1 min)     | 93    | 3     | 90     | 0      | 3.2%      | $0.3     |
| Very Long (>1h)        | 15    | 0     | 15     | 0      | 0.0%      | $-0.5    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 5.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.02 — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (21.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (3.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.00) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $0.02) — optimal time held is Time Held: <30m.
- ⚠️ Best signal generation window: Afternoon (12:00-16:00) (15.0% win rate) — but only 20 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (643s / 10.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### vol_compression_range

**Symbols:** AAPL, AMD, NVDA, TSLA  |  **Total Signals:** 724  |  **Win Rate:** 62.7%  |  **Avg P&L (resolved):** $1.1  |  **Avg P&L (all):** $1.1  |  **Avg Hold:** 23873s (397.9m)  |  **Median Hold:** 10163s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 58    | 43    | 15     | 0      | 74.1%     | $0.0     | $0.0     | 0.0%     |
| 30-39%         | 193   | 155   | 38     | 0      | 80.3%     | $0.0     | $0.0     | 0.0%     |
| 40-49%         | 258   | 176   | 82     | 0      | 68.2%     | $0.0     | $0.0     | 0.0%     |
| 50-59%         | 167   | 58    | 109    | 0      | 34.7%     | $0.0     | $0.0     | 0.0%     |
| 60-69%         | 44    | 19    | 25     | 0      | 43.2%     | $0.0     | $0.0     | 0.0%     |
| 70-79%         | 4     | 3     | 1      | 0      | 75.0%     | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 531   | 383   | 148    | 0      | 72.1%     | $1.5     |
| Trending (Up)        | 193   | 71    | 122    | 0      | 36.8%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 724   | 454   | 270    | 0      | 62.7%     | $1.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 240-480m    | 13    | 13    | 0      | 0      | 100.0%    | $2.8     |
| Time Held: 30-90m      | 165   | 64    | 101    | 0      | 38.8%     | $0.1     |
| Time Held: 90-240m     | 144   | 100   | 44     | 0      | 69.4%     | $1.6     |
| Time Held: <30m        | 95    | 39    | 56     | 0      | 41.1%     | $-0.0    |
| Time Held: >480m       | 307   | 238   | 69     | 0      | 77.5%     | $1.8     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 156   | 113   | 43     | 0      | 72.4%     | $1.8     | 🟢          |
| Afternoon (12:00-16:00) | 116   | 47    | 69     | 0      | 40.5%     | $0.2     | 🔴          |
| Morning (10:00-12:00)  | 63    | 15    | 48     | 0      | 23.8%     | $-0.6    | 🔴          |
| ORB (9:30-10:00)       | 13    | 7     | 6      | 0      | 53.8%     | $0.5     | ⚠️         |
| Overnight              | 98    | 98    | 0      | 0      | 100.0%    | $2.3     | 🟢          |
| Pre-market             | 278   | 174   | 104    | 0      | 62.6%     | $1.2     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 278    | 0          | 57         | 221        | 0.0%      | 20.5%     | 79.5%     |
| ORB (9:30-10:00)       | 13     | 0          | 6          | 7          | 0.0%      | 46.2%     | 53.8%     |
| Morning (10:00-12:00)  | 63     | 3          | 37         | 23         | 4.8%      | 58.7%     | 36.5%     |
| Afternoon (12:00-16:00) | 116    | 1          | 82         | 33         | 0.9%      | 70.7%     | 28.4%     |
| After-hours (16:00-20:00) | 156    | 0          | 29         | 127        | 0.0%      | 18.6%     | 81.4%     |
| Overnight              | 98     | 0          | 0          | 98         | 0.0%      | 0.0%      | 100.0%    |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 48     | 33    | 15     | 0      | 68.8%     | $1.7         | 🟢          |
| Pre-market             | 30-39%     | 105    | 75    | 30     | 0      | 71.4%     | $1.7         | 🟢          |
| Pre-market             | 40-49%     | 68     | 29    | 39     | 0      | 42.6%     | $0.3         | 🔴          |
| Pre-market             | 50-59%     | 52     | 33    | 19     | 0      | 63.5%     | $0.9         | 🟢          |
| Pre-market             | 60-69%     | 5      | 4     | 1      | 0      | 80.0%     | $0.9         | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 1      | 1     | 0      | 0      | 100.0%    | $2.8         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 2      | 1     | 1      | 0      | 50.0%     | $0.2         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 4      | 2     | 2      | 0      | 50.0%     | $0.4         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 5      | 3     | 2      | 0      | 60.0%     | $0.7         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 7      | 1     | 6      | 0      | 14.3%     | $-1.2        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 16     | 4     | 12     | 0      | 25.0%     | $-0.7        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 25     | 3     | 22     | 0      | 12.0%     | $-1.0        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 12     | 4     | 8      | 0      | 33.3%     | $-0.0        | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 3      | 3     | 0      | 0      | 100.0%    | $1.5         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 6      | 5     | 1      | 0      | 83.3%     | $2.7         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 27     | 12    | 15     | 0      | 44.4%     | $0.3         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 58     | 19    | 39     | 0      | 32.8%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 24     | 11    | 13     | 0      | 45.8%     | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.1        | ⚠️         |
| After-hours (16:00-20:00) | 20-29%     | 9      | 9     | 0      | 0      | 100.0%    | $3.1         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 73     | 73    | 0      | 0      | 100.0%    | $3.1         | 🟢          |
| After-hours (16:00-20:00) | 40-49%     | 45     | 31    | 14     | 0      | 68.9%     | $1.5         | 🟢          |
| After-hours (16:00-20:00) | 50-59%     | 27     | 0     | 27     | 0      | 0.0%      | $-1.4        | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Overnight              | 40-49%     | 98     | 98    | 0      | 0      | 100.0%    | $2.3         | 🟢          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 521   | 414   | 107    | 0      | 79.5%     | $1.8     |
| SHORT        | 203   | 40    | 163    | 0      | 19.7%     | $-0.7    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 5     | 3     | 2      | 0      | 60.0%     | $0.5     |
| Long (30-60 min)       | 82    | 31    | 51     | 0      | 37.8%     | $0.1     |
| Medium (5-15 min)      | 28    | 9     | 19     | 0      | 32.1%     | $-0.5    |
| Slow (15-30 min)       | 60    | 25    | 35     | 0      | 41.7%     | $0.1     |
| Very Fast (<1 min)     | 2     | 2     | 0      | 0      | 100.0%    | $1.5     |
| Very Long (>1h)        | 547   | 384   | 163    | 0      | 70.2%     | $1.5     |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 62.7% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 💰 Positive avg P&L per resolved signal: $1.14 — profitable even with 62.7% win rate (good risk/reward).
- 🎯 Best performance at 30-39% confidence (80.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (34.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $1.54) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 240-480m (avg P&L $2.79) — optimal time held is Time Held: 240-480m.
- ✅ Best signal generation window: Overnight (100.0% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (23873s / 397.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

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
| 1780334986.924 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 10           | Magnet pull SHORT: price 221.70 above magnet 22... |
| 1780407905.964 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, theta_burn | 10           | Depth imbalance SHORT: IR=0.21 (+79.0%), ROC=-0... |
| 1780300800.251 | 28     | confluence_reversal, delta_gamma_squeeze, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, strike_concentration | 9            | Flow imbalance LONG: AggVSI=0.333 (+33.3%), ROC... |
| 1780300862.496 | 19     | confluence_reversal, delta_gamma_squeeze, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, strike_concentration | 9            | Gamma squeeze: price approaching put wall at 21... |
| 1780302542.12  | 9      | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate, strike_concentration | 9            | Flow imbalance SHORT: AggVSI=-0.463 (+46.3%), R... |
| 1780319584.736 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Breakout SHORT below flip zone 108.00, price=10... |
| 1780322540.31  | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Depth decay LONG: ROC=-0.3755 (-37.55%), vol/de... |
| 1780322645.056 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 9            | GEX divergence (bullish): price falling but GEX... |
| 1780326692.381 | 10     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, strike_concentration | 9            | Fade LONG above flip zone 108.00, price=110.45,... |
| 1780327817.755 | 11     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 9            | Confluence LONG at 112: 1 structural signals, t... |
| 1780330931.155 | 10     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth imbalance SHORT: IR=0.51 (+48.7%), ROC=-0... |
| 1780333663.818 | 11     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | GEX divergence (bearish): price rising but GEX ... |
| 1780336169.443 | 13     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | GEX divergence (bullish): price falling but GEX... |
| 1780342828.763 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, vol_compression_range | 9            | Confluence SHORT at 225: 2 structural signals, ... |
| 1780349730.03  | 11     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Magnet pull LONG: price 306.36 below magnet 310... |
| 1780354399.771 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate | 9            | Exchange flow LONG: VSI=5.00 (+400.0%), ROC=+0.... |
| 1780354540.515 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1780354785.703 | 10     | confluence_reversal, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Exchange flow SHORT: VSI=0.23 (+77.1%), ROC=-0.... |
| 1780356339.512 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | MEMX accumulation LONG: ESI=1.000 (+100.0%), de... |
| 1780387200.558 | 24     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration | 9            | Flow imbalance LONG: AggVSI=0.600 (+60.0%), ROC... |
| 1780388226.882 | 13     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1780389213.65  | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, theta_burn | 9            | Exchange flow LONG: VSI=9.55 (+854.5%), ROC=+8.... |
| 1780407452.401 | 10     | depth_decay_momentum, depth_imbalance_momentum, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, theta_burn, vol_compression_range | 9            | Call wall at 227.5 rejected price, GEX=2271065,... |
| 1780303023.382 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate | 8            | Fade SHORT above flip zone 310.00, price=310.09... |
| 1780304902.184 | 8      | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate | 8            | Depth imbalance SHORT: IR=0.40 (+60.3%), ROC=-0... |
| 1780307811.309 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, strike_concentration, vol_compression_range | 8            | Confluence LONG at 425: 2 structural signals, t... |
| 1780308174.794 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration | 8            | Exchange flow LONG: VSI=2.19 (+119.0%), ROC=+1.... |
| 1780309408.276 | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Range LONG: price near lower edge, wall at 430,... |
| 1780309470.334 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate | 8            | GEX divergence (bullish): price falling but GEX... |
| 1780312508.488 | 8      | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate | 8            | Call wall at 430.0 rejected price, GEX=-1510760... |
| 1780313252.669 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate | 8            | Confluence LONG at 308: 2 structural signals, t... |
| 1780318933.989 | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate | 8            | Exchange flow LONG: VSI=2.17 (+117.4%), ROC=+1.... |
| 1780319523.373 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate | 8            | Depth decay SHORT: ROC=-0.1954 (-19.54%), vol/d... |
| 1780319630.004 | 8      | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Magnet pull SHORT: price 215.67 above magnet 21... |
| 1780319815.866 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, strike_concentration | 8            | GEX divergence (bullish): price falling but GEX... |
| 1780320083.017 | 8      | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate | 8            | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1780320865.874 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, magnet_accelerate | 8            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1780321086.208 | 8      | exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Exchange flow LONG: VSI=999.00 (+99800.0%), ROC... |
| 1780321120.022 | 9      | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 8            | Flow imbalance LONG: AggVSI=0.333 (+33.3%), ROC... |
| 1780321252.332 | 14     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 8            | Confluence LONG at 425: 2 structural signals, t... |
| 1780321372.65  | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 8            | Confluence LONG at 425: 2 structural signals, t... |
| 1780321676.832 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Exchange flow LONG: VSI=5.57 (+456.5%), ROC=+1.... |
| 1780321739.093 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Exchange flow LONG: VSI=4.85 (+384.6%), ROC=+3.... |
| 1780322179.053 | 9      | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration | 8            | Put wall at 422.5 supported price, GEX=730428, ... |
| 1780322706.66  | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate | 8            | GEX divergence (bullish): price falling but GEX... |
| 1780323423.199 | 9      | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, strike_concentration | 8            | Confluence LONG at 493: 1 structural signals, t... |
| 1780323798.546 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, magnet_accelerate | 8            | Depth decay SHORT: ROC=-0.5601 (-56.01%), vol/d... |
| 1780323854.053 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_wall_bounce, gex_divergence, magnet_accelerate | 8            | Depth imbalance LONG: IR=3.21 (+220.7%), ROC=+0... |
| 1780324165.584 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce | 8            | Confluence SHORT at 222: 2 structural signals, ... |
| 1780324670.542 | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce | 8            | Squeeze LONG: breakout through call wall at 220... |

**6924 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 22,320   | 9          | wall_gex=< 500000.00   | 38.4%    | $0.4       |
| Gamma Wall Support (310.0)   | 1,536    | 3          | wall_strike=310.0      | 73.6%    | $1.5       |
| Gamma Wall Support (220.0)   | 878      | 3          | wall_strike=220.0      | 28.1%    | $-0.5      |
| Gamma Wall Support (420.0)   | 704      | 3          | wall_strike=420.0      | 20.2%    | $-0.8      |
| Gamma Wall Support (442.5)   | 341      | 4          | wall_strike=442.5      | 47.2%    | $0.6       |
| Gamma Wall Support (207.5)   | 257      | 4          | wall_strike=207.5      | 67.7%    | $1.1       |
| Gamma Wall Support (525.0)   | 64       | 3          | wall_strike=525.0      | 57.8%    | $3.9       |
| Gamma Wall Support (110.0)   | 55       | 3          | wall_strike=110.0      | 23.6%    | $-0.0      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 5905   | 6      | 6        | 43.5%    | $0.4       | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Exposur  | 6444   | 6      | 6        | 26.5%    | $-0.1      | net_gamma  | delta_gamma_squeeze, gamma_flip_breakou  |
| Gamma Exposur  | 3527   | 5      | 5        | 37.9%    | $0.2       | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 257    | 4      | 4        | 67.7%    | $1.1       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 341    | 4      | 4        | 47.2%    | $0.6       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Exposur  | 6444   | 4      | 4        | 46.0%    | $1.0       | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Wall Su  | 1536   | 3      | 3        | 73.6%    | $1.5       | wall_stri  | delta_gamma_squeeze, gamma_wall_bounce,  |
| Gamma Wall Su  | 64     | 3      | 3        | 57.8%    | $3.9       | wall_stri  | delta_gamma_squeeze, gamma_wall_bounce,  |
| Gamma Wall Su  | 878    | 3      | 3        | 28.1%    | $-0.5      | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 55     | 3      | 3        | 23.6%    | $-0.0      | wall_stri  | gamma_squeeze, gamma_wall_bounce, theta  |
| Gamma Wall Su  | 704    | 3      | 3        | 20.2%    | $-0.8      | wall_stri  | gamma_squeeze, gamma_wall_bounce, theta  |

**11 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 169      | 51     | 118    | 0      | 30.2%     | 24.2      |
| 20-29%         | 3203     | 984    | 2219   | 0      | 30.7%     | 25.2      |
| 30-39%         | 3972     | 1688   | 2284   | 0      | 42.5%     | 22.9      |
| 40-49%         | 4322     | 1957   | 2365   | 0      | 45.3%     | 17.6      |
| 50-59%         | 6636     | 2368   | 4268   | 0      | 35.7%     | 16.1      |
| 60-69%         | 6759     | 3024   | 3735   | 0      | 44.7%     | 16.6      |
| 70-79%         | 4866     | 1794   | 3072   | 0      | 36.9%     | 18.0      |
| 80-89%         | 4588     | 1364   | 3224   | 0      | 29.7%     | 12.6      |
| 90-99%         | 962      | 312    | 650    | 0      | 32.4%     | 6.0       |
| 100%           | 1924     | 142    | 1782   | 0      | 7.4%      | 11.8      |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| Pre-market             | 17168    | 6099   | 11069  | 0      | 35.5%     | 15.4     |
| ORB (9:30-10:00)       | 1768     | 483    | 1285   | 0      | 27.3%     | 13.6     |
| Morning (10:00-12:00)  | 3805     | 1299   | 2506   | 0      | 34.1%     | 11.9     |
| Afternoon (12:00-16:00) | 6278     | 2616   | 3662   | 0      | 41.7%     | 21.3     |
| After-hours (16:00-20:00) | 5660     | 1840   | 3820   | 0      | 32.5%     | 18.4     |
| Overnight              | 2723     | 1348   | 1375   | 0      | 49.5%     | 32.0     |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| Pre-market             | 10-19%       | 100      | 35     | 65     | 0      | 35.0%     |
| Pre-market             | 20-29%       | 1659     | 541    | 1118   | 0      | 32.6%     |
| Pre-market             | 30-39%       | 2021     | 832    | 1189   | 0      | 41.2%     |
| Pre-market             | 40-49%       | 1804     | 742    | 1062   | 0      | 41.1%     |
| Pre-market             | 50-59%       | 3216     | 1168   | 2048   | 0      | 36.3%     |
| Pre-market             | 60-69%       | 3343     | 1433   | 1910   | 0      | 42.9%     |
| Pre-market             | 70-79%       | 2119     | 638    | 1481   | 0      | 30.1%     |
| Pre-market             | 80-89%       | 1884     | 517    | 1367   | 0      | 27.4%     |
| Pre-market             | 90-99%       | 420      | 128    | 292    | 0      | 30.5%     |
| Pre-market             | 100%         | 601      | 64     | 537    | 0      | 10.6%     |
| ORB (9:30-10:00)       | 10-19%       | 11       | 1      | 10     | 0      | 9.1%      |
| ORB (9:30-10:00)       | 20-29%       | 126      | 17     | 109    | 0      | 13.5%     |
| ORB (9:30-10:00)       | 30-39%       | 126      | 32     | 94     | 0      | 25.4%     |
| ORB (9:30-10:00)       | 40-49%       | 183      | 50     | 133    | 0      | 27.3%     |
| ORB (9:30-10:00)       | 50-59%       | 284      | 80     | 204    | 0      | 28.2%     |
| ORB (9:30-10:00)       | 60-69%       | 297      | 97     | 200    | 0      | 32.7%     |
| ORB (9:30-10:00)       | 70-79%       | 328      | 96     | 232    | 0      | 29.3%     |
| ORB (9:30-10:00)       | 80-89%       | 302      | 79     | 223    | 0      | 26.2%     |
| ORB (9:30-10:00)       | 90-99%       | 33       | 11     | 22     | 0      | 33.3%     |
| ORB (9:30-10:00)       | 100%         | 78       | 20     | 58     | 0      | 25.6%     |
| Morning (10:00-12:00)  | 10-19%       | 28       | 4      | 24     | 0      | 14.3%     |
| Morning (10:00-12:00)  | 20-29%       | 254      | 73     | 181    | 0      | 28.7%     |
| Morning (10:00-12:00)  | 30-39%       | 254      | 53     | 201    | 0      | 20.9%     |
| Morning (10:00-12:00)  | 40-49%       | 457      | 151    | 306    | 0      | 33.0%     |
| Morning (10:00-12:00)  | 50-59%       | 621      | 197    | 424    | 0      | 31.7%     |
| Morning (10:00-12:00)  | 60-69%       | 642      | 246    | 396    | 0      | 38.3%     |
| Morning (10:00-12:00)  | 70-79%       | 668      | 306    | 362    | 0      | 45.8%     |
| Morning (10:00-12:00)  | 80-89%       | 648      | 227    | 421    | 0      | 35.0%     |
| Morning (10:00-12:00)  | 90-99%       | 48       | 22     | 26     | 0      | 45.8%     |
| Morning (10:00-12:00)  | 100%         | 185      | 20     | 165    | 0      | 10.8%     |
| Afternoon (12:00-16:00) | 10-19%       | 13       | 6      | 7      | 0      | 46.2%     |
| Afternoon (12:00-16:00) | 20-29%       | 459      | 152    | 307    | 0      | 33.1%     |
| Afternoon (12:00-16:00) | 30-39%       | 446      | 205    | 241    | 0      | 46.0%     |
| Afternoon (12:00-16:00) | 40-49%       | 852      | 415    | 437    | 0      | 48.7%     |
| Afternoon (12:00-16:00) | 50-59%       | 1125     | 467    | 658    | 0      | 41.5%     |
| Afternoon (12:00-16:00) | 60-69%       | 880      | 421    | 459    | 0      | 47.8%     |
| Afternoon (12:00-16:00) | 70-79%       | 1100     | 535    | 565    | 0      | 48.6%     |
| Afternoon (12:00-16:00) | 80-89%       | 983      | 340    | 643    | 0      | 34.6%     |
| Afternoon (12:00-16:00) | 90-99%       | 109      | 37     | 72     | 0      | 33.9%     |
| Afternoon (12:00-16:00) | 100%         | 311      | 38     | 273    | 0      | 12.2%     |
| After-hours (16:00-20:00) | 20-29%       | 392      | 96     | 296    | 0      | 24.5%     |
| After-hours (16:00-20:00) | 30-39%       | 451      | 227    | 224    | 0      | 50.3%     |
| After-hours (16:00-20:00) | 40-49%       | 718      | 291    | 427    | 0      | 40.5%     |
| After-hours (16:00-20:00) | 50-59%       | 1011     | 314    | 697    | 0      | 31.1%     |
| After-hours (16:00-20:00) | 60-69%       | 1008     | 397    | 611    | 0      | 39.4%     |
| After-hours (16:00-20:00) | 70-79%       | 643      | 211    | 432    | 0      | 32.8%     |
| After-hours (16:00-20:00) | 80-89%       | 674      | 201    | 473    | 0      | 29.8%     |
| After-hours (16:00-20:00) | 90-99%       | 340      | 102    | 238    | 0      | 30.0%     |
| After-hours (16:00-20:00) | 100%         | 416      | 0      | 416    | 0      | 0.0%      |
| Overnight              | 10-19%       | 10       | 4      | 6      | 0      | 40.0%     |
| Overnight              | 20-29%       | 313      | 105    | 208    | 0      | 33.5%     |
| Overnight              | 30-39%       | 674      | 339    | 335    | 0      | 50.3%     |
| Overnight              | 40-49%       | 308      | 308    | 0      | 0      | 100.0%    |
| Overnight              | 50-59%       | 379      | 142    | 237    | 0      | 37.5%     |
| Overnight              | 60-69%       | 589      | 430    | 159    | 0      | 73.0%     |
| Overnight              | 80-89%       | 97       | 0      | 97     | 0      | 0.0%      |
| Overnight              | 90-99%       | 12       | 12     | 0      | 0      | 100.0%    |
| Overnight              | 100%         | 333      | 0      | 333    | 0      | 0.0%      |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] gamma_wall_bounce | 100%         | 23.1%     | 7.4%      | 212%     | 1.33     | 451      | 104      | 347      |
| [ALPHA] vol_compression_range | 20-29%       | 74.1%     | 30.7%     | 141%     | 1.72     | 58       | 43       | 15       |
| [ALPHA] delta_gamma_squeeze | 30-39%       | 96.6%     | 42.5%     | 127%     | 2.36     | 29       | 28       | 1        |
| [ALPHA] gamma_squeeze    | 50-59%       | 80.0%     | 35.7%     | 124%     | 2.76     | 50       | 40       | 10       |
| [ALPHA] gamma_flip_breakout | 20-29%       | 65.0%     | 30.7%     | 112%     | 1.36     | 80       | 52       | 28       |
| [ALPHA] vol_compression_range | 30-39%       | 80.3%     | 42.5%     | 89%      | 1.65     | 193      | 155      | 38       |
| [ALPHA] gamma_wall_bounce | 60-69%       | 81.6%     | 44.7%     | 82%      | 2.22     | 477      | 389      | 88       |
| [ALPHA] gamma_flip_breakout | 50-59%       | 62.6%     | 35.7%     | 76%      | 1.68     | 348      | 218      | 130      |
| [ALPHA] gamma_squeeze    | 60-69%       | 77.9%     | 44.7%     | 74%      | 2.00     | 95       | 74       | 21       |
| [ALPHA] gamma_flip_breakout | 40-49%       | 76.5%     | 45.3%     | 69%      | 1.77     | 490      | 375      | 115      |
| [ALPHA] exchange_flow_concentration | 10-19%       | 50.0%     | 30.2%     | 66%      | 0.82     | 14       | 7        | 7        |
| [ALPHA] strike_concentration | 70-79%       | 61.0%     | 36.9%     | 65%      | 1.34     | 41       | 25       | 16       |
| [ALPHA] exchange_flow_concentration | 20-29%       | 50.0%     | 30.7%     | 63%      | 0.76     | 52       | 26       | 26       |
| [ALPHA] gamma_flip_breakout | 30-39%       | 68.0%     | 42.5%     | 60%      | 1.11     | 344      | 234      | 110      |
| [ALPHA] depth_decay_momentum | 80-89%       | 45.9%     | 29.7%     | 54%      | 1.28     | 767      | 352      | 415      |
| [ALPHA] gamma_wall_bounce | 80-89%       | 45.1%     | 29.7%     | 52%      | 1.22     | 51       | 23       | 28       |
| [ALPHA] vol_compression_range | 40-49%       | 68.2%     | 45.3%     | 51%      | 1.30     | 258      | 176      | 82       |

**17 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] gamma_wall_bounce | Pre-market   | 100%         | 83      | 41     | 42     | 49.4%    | 10.6%    | 364%   | 1.58    | 🔥 STRONG     |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 10-19%       | 5       | 3      | 2      | 60.0%    | 14.3%    | 320%   | 1.16    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 20-29%       | 9       | 9      | 0      | 100.0%   | 24.5%    | 308%   | 1.56    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 20-29%       | 9       | 9      | 0      | 100.0%   | 24.5%    | 308%   | 1.56    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 30-39%       | 10      | 8      | 2      | 80.0%    | 20.9%    | 283%   | 2.21    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 30-39%       | 11      | 10     | 1      | 90.9%    | 25.4%    | 258%   | 1.67    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Pre-market   | 80-89%       | 12      | 11     | 1      | 91.7%    | 27.4%    | 234%   | 2.28    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 100%         | 95      | 38     | 57     | 40.0%    | 12.2%    | 227%   | 1.20    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | After-hours (16:00-20:00) | 50-59%       | 72      | 72     | 0      | 100.0%   | 31.1%    | 222%   | 2.47    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 50-59%       | 32      | 29     | 3      | 90.6%    | 31.7%    | 186%   | 2.16    | ⚡ HIGH       |
| [ALPHA] magnet_accelerate | Morning (10:00-12:00) | 80-89%       | 5       | 5      | 0      | 100.0%   | 35.0%    | 185%   | 1.99    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 20-29%       | 45      | 42     | 3      | 93.3%    | 33.1%    | 182%   | 2.12    | ⚡ HIGH       |
| [ALPHA] gamma_squeeze    | Pre-market   | 50-59%       | 27      | 26     | 1      | 96.3%    | 36.3%    | 165%   | 3.02    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | After-hours (16:00-20:00) | 60-69%       | 9       | 9      | 0      | 100.0%   | 39.4%    | 154%   | 2.21    | ⚡ HIGH       |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 50-59%       | 9       | 9      | 0      | 100.0%   | 41.5%    | 141%   | 1.86    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 50-59%       | 10      | 10     | 0      | 100.0%   | 41.5%    | 141%   | 1.86    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 50-59%       | 34      | 23     | 11     | 67.6%    | 28.2%    | 140%   | 1.59    | 🔥 STRONG     |
| [ALPHA] delta_gamma_squeeze | Pre-market   | 30-39%       | 25      | 24     | 1      | 96.0%    | 41.2%    | 133%   | 2.32    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | After-hours (16:00-20:00) | 40-49%       | 51      | 48     | 3      | 94.1%    | 40.5%    | 132%   | 1.68    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Pre-market   | 100%         | 91      | 22     | 69     | 24.2%    | 10.6%    | 127%   | 0.55    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 70-79%       | 14      | 9      | 5      | 64.3%    | 29.3%    | 120%   | 1.82    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 50-59%       | 5       | 3      | 2      | 60.0%    | 28.2%    | 113%   | 1.28    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 20-29%       | 20      | 14     | 6      | 70.0%    | 33.1%    | 111%   | 1.30    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Pre-market   | 20-29%       | 48      | 33     | 15     | 68.8%    | 32.6%    | 111%   | 1.36    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 60-69%       | 10      | 10     | 0      | 100.0%   | 47.8%    | 109%   | 1.89    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 60-69%       | 5       | 5      | 0      | 100.0%   | 47.8%    | 109%   | 1.89    | 🔥 STRONG     |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 60-69%       | 21      | 21     | 0      | 100.0%   | 47.8%    | 109%   | 1.89    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 20-29%       | 35      | 21     | 14     | 60.0%    | 28.7%    | 109%   | 1.65    | 🔥 STRONG     |
| [ALPHA] depth_imbalance_momentum | Morning (10:00-12:00) | 30-39%       | 7       | 3      | 4      | 42.9%    | 20.9%    | 105%   | 0.82    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Afternoon (12:00-16:00) | 40-49%       | 5       | 5      | 0      | 100.0%   | 48.7%    | 105%   | 1.89    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 30-39%       | 51      | 48     | 3      | 94.1%    | 46.0%    | 105%   | 1.83    | 🔥 STRONG     |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 50-59%       | 79      | 51     | 28     | 64.6%    | 31.7%    | 104%   | 1.20    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 80-89%       | 19      | 10     | 9      | 52.6%    | 26.2%    | 101%   | 1.71    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 30-39%       | 73      | 73     | 0      | 100.0%   | 50.3%    | 99%    | 1.93    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | ORB (9:30-10:00) | 50-59%       | 9       | 5      | 4      | 55.6%    | 28.2%    | 97%    | 1.10    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | Pre-market   | 60-69%       | 35      | 29     | 6      | 82.9%    | 42.9%    | 93%    | 1.97    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 50-59%       | 90      | 72     | 18     | 80.0%    | 41.5%    | 93%    | 1.23    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 40-49%       | 22      | 14     | 8      | 63.6%    | 33.0%    | 93%    | 1.47    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | After-hours (16:00-20:00) | 80-89%       | 121     | 69     | 52     | 57.0%    | 29.8%    | 91%    | 1.31    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 80-89%       | 22      | 11     | 11     | 50.0%    | 26.2%    | 91%    | 1.54    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 70-79%       | 34      | 19     | 15     | 55.9%    | 29.3%    | 91%    | 1.38    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | After-hours (16:00-20:00) | 90-99%       | 7       | 4      | 3      | 57.1%    | 30.0%    | 90%    | 1.76    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 70-79%       | 15      | 13     | 2      | 86.7%    | 45.8%    | 89%    | 2.04    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 40-49%       | 85      | 78     | 7      | 91.8%    | 48.7%    | 88%    | 1.59    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 90-99%       | 11      | 7      | 4      | 63.6%    | 33.9%    | 87%    | 1.37    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Pre-market   | 60-69%       | 5       | 4      | 1      | 80.0%    | 42.9%    | 87%    | 1.83    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 100%         | 23      | 11     | 12     | 47.8%    | 25.6%    | 87%    | 1.02    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 80-89%       | 192     | 122    | 70     | 63.5%    | 34.6%    | 84%    | 1.49    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 30-39%       | 6       | 5      | 1      | 83.3%    | 46.0%    | 81%    | 1.42    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | Morning (10:00-12:00) | 60-69%       | 26      | 18     | 8      | 69.2%    | 38.3%    | 81%    | 1.48    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Morning (10:00-12:00) | 50-59%       | 28      | 16     | 12     | 57.1%    | 31.7%    | 80%    | 0.93    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 30-39%       | 51      | 42     | 9      | 82.4%    | 46.0%    | 79%    | 1.38    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | ORB (9:30-10:00) | 70-79%       | 23      | 12     | 11     | 52.2%    | 29.3%    | 78%    | 1.19    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | Afternoon (12:00-16:00) | 20-29%       | 61      | 36     | 25     | 59.0%    | 33.1%    | 78%    | 0.91    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | ORB (9:30-10:00) | 50-59%       | 24      | 12     | 12     | 50.0%    | 28.2%    | 77%    | 0.88    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | ORB (9:30-10:00) | 30-39%       | 20      | 9      | 11     | 45.0%    | 25.4%    | 77%    | 0.50    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Pre-market   | 70-79%       | 64      | 34     | 30     | 53.1%    | 30.1%    | 76%    | 1.24    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Afternoon (12:00-16:00) | 20-29%       | 24      | 14     | 10     | 58.3%    | 33.1%    | 76%    | 0.89    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Pre-market   | 50-59%       | 52      | 33     | 19     | 63.5%    | 36.3%    | 75%    | 1.36    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 40-49%       | 203     | 145    | 58     | 71.4%    | 41.1%    | 74%    | 1.58    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Pre-market   | 30-39%       | 105     | 75     | 30     | 71.4%    | 41.2%    | 74%    | 1.28    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 30-39%       | 47      | 17     | 30     | 36.2%    | 20.9%    | 73%    | 0.57    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Morning (10:00-12:00) | 100%         | 91      | 17     | 74     | 18.7%    | 10.8%    | 73%    | 0.83    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 20-29%       | 48      | 27     | 21     | 56.2%    | 32.6%    | 72%    | 0.89    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | After-hours (16:00-20:00) | 40-49%       | 45      | 31     | 14     | 68.9%    | 40.5%    | 70%    | 0.89    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 60-69%       | 20      | 13     | 7      | 65.0%    | 38.3%    | 70%    | 1.28    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Pre-market   | 30-39%       | 179     | 125    | 54     | 69.8%    | 41.2%    | 70%    | 1.21    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Pre-market   | 60-69%       | 256     | 186    | 70     | 72.7%    | 42.9%    | 69%    | 1.47    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 60-69%       | 25      | 16     | 9      | 64.0%    | 38.3%    | 67%    | 1.23    | ⚠ MODERATE   |
| [ALPHA] gamma_wall_bounce | Pre-market   | 40-49%       | 221     | 145    | 76     | 65.6%    | 41.1%    | 60%    | 1.28    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Pre-market   | 40-49%       | 95      | 61     | 34     | 64.2%    | 41.1%    | 56%    | 1.21    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 70-79%       | 51      | 26     | 25     | 51.0%    | 32.8%    | 55%    | 1.01    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | Afternoon (12:00-16:00) | 80-89%       | 51      | 27     | 24     | 52.9%    | 34.6%    | 53%    | 0.94    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Pre-market   | 70-79%       | 564     | 258    | 306    | 45.7%    | 30.1%    | 52%    | 0.84    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 60-69%       | 31      | 18     | 13     | 58.1%    | 38.3%    | 52%    | 0.95    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Pre-market   | 60-69%       | 97      | 63     | 34     | 64.9%    | 42.9%    | 52%    | 1.09    | ⚠ MODERATE   |
| [ALPHA] confluence_reversal | Morning (10:00-12:00) | 40-49%       | 119     | 59     | 60     | 49.6%    | 33.0%    | 50%    | 0.80    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 60-69%       | 27      | 13     | 14     | 48.1%    | 32.7%    | 47%    | 1.79    | ⚠ MODERATE   |
| [ALPHA] gamma_squeeze    | ORB (9:30-10:00) | 60-69%       | 13      | 6      | 7      | 46.2%    | 32.7%    | 41%    | 1.56    | ⚠ MODERATE   |

**79 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | delta_gamma_squeeze      | 222     | 48.2%    | $1.6     | 30-39%         | Afternoon (12:00-16:00) | Pre-market @ 30-39%    | Sideways       | Time Held: <30m |
| 2     | vol_compression_range    | 724     | 62.7%    | $1.1     | 30-39%         | Overnight        | Overnight @ 40-49%     | Sideways       | Time Held: 240-480m |
| 3     | magnet_accelerate        | 6,704   | 31.1%    | $1.1     | 60-69%         | Overnight        | Overnight @ 40-49%     | Sideways       | Time Held: >480m |
| 4     | gamma_wall_bounce        | 2,465   | 47.8%    | $0.3     | 60-69%         | Overnight        | Afternoon (12:00-16:00) @ 60-69% | Sideways       | Time Held: 240-480m |
| 5     | confluence_reversal      | 5,589   | 35.7%    | $0.2     | 60-69%         | Overnight        | Overnight @ 40-49%     | Sideways       | Time Held: 240-480m |
| 6     | depth_decay_momentum     | 3,781   | 42.2%    | $0.2     | 40-49%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 90-99% | UNKNOWN        | Time Held: 240-480m |
| 7     | exchange_flow_concentration | 3,276   | 39.5%    | $0.0     | 10-19%         | Afternoon (12:00-16:00) | After-hours (16:00-20:00) @ 30-39% | UNKNOWN        | Time Held: 90-240m |
| 8     | gex_divergence           | 1,113   | 43.2%    | $0.0     | 40-49%         | Pre-market       | Afternoon (12:00-16:00) @ 70-79% | Trending (Up)  | Time Held: 240-480m |
| 9     | gamma_squeeze            | 493     | 40.6%    | $0.0     | 50-59%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 60-69% | Trending (Up)  | Time Held: 90-240m |
| 10    | strike_concentration     | 443     | 39.5%    | $-0.0    | 70-79%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 60-69% | Trending (Up)  | Time Held: 90-240m |
| 11    | exchange_flow_imbalance  | 3,285   | 30.9%    | $-0.0    | 30-39%         | Overnight        | Overnight @ 70-79%     | UNKNOWN        | Time Held: 90-240m |
| 12    | theta_burn               | 142     | 5.6%     | $-0.0    | 30-39%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 30-39% | Sideways       | Time Held: 30-90m |
| 13    | exchange_flow_asymmetry  | 1,824   | 22.8%    | $-0.2    | 80-89%         | Morning (10:00-12:00) | Morning (10:00-12:00) @ 80-89% | UNKNOWN        | Time Held: 240-480m |
| 14    | gamma_flip_breakout      | 4,884   | 42.9%    | $-0.3    | 40-49%         | ORB (9:30-10:00) | After-hours (16:00-20:00) @ 20-29% | Sideways       | Time Held: <30m |
| 15    | depth_imbalance_momentum | 2,457   | 24.1%    | $-0.3    | 70-79%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 30-39% | UNKNOWN        | Time Held: 240-480m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*