# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-27  |  **Generated:** 2026-05-27 20:46 UTC  |  **Total Resolved Signals:** 26,385  |  **Strategies Analyzed:** 14

---

## Overall Summary

| Metric               | Value                                                        |
+----------------------+--------------------------------------------------------------+
| Total Resolved Signals | 26,385                                                       |
| Total Wins           | 2,604                                                        |
| Total Losses         | 6,301                                                        |
| Time-Expired (CLOSED) | 17,480                                                       |
| Overall Win Rate     | 29.2%                                                        |
| Total P&L (resolved) | $-4572.21                                                    |
| Avg P&L per Resolved Signal | $-0.51                                                       |
| Total P&L (time-outs) | $4982.48                                                     |
| Avg P&L per Signal (all) | $0.02                                                        |
| Symbols Traded       | AAPL, AMD, INTC, NVDA, TSLA                                  |

---

## Per-Strategy Deep Dive

### confluence_reversal

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 5,978  |  **Win Rate:** 24.3%  |  **Avg P&L (resolved):** $-1.7  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 3306s (55.1m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 2132  | 106   | 388    | 1638   | 21.5%     | $0.0     | $0.5     | 10.6%    |
| 30-39%         | 2126  | 83    | 217    | 1826   | 27.7%     | $0.0     | $0.3     | 5.5%     |
| 40-49%         | 1017  | 26    | 63     | 928    | 29.2%     | $0.0     | $0.1     | 2.9%     |
| 50-59%         | 403   | 7     | 26     | 370    | 21.2%     | $0.0     | $-0.1    | -3.1%    |
| 60-69%         | 242   | 1     | 2      | 239    | 33.3%     | $0.0     | $0.1     | 2.9%     |
| 70-79%         | 58    | 0     | 0      | 58     | 0.0%      | $0.0     | $0.2     | 6.7%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 3502  | 164   | 432    | 2906   | 27.5%     | $0.1     |
| Trending (Up)        | 2476  | 59    | 264    | 2153   | 18.3%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 5978  | 223   | 696    | 5059   | 24.3%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 5475  | 108   | 308    | 5059   | 26.0%     | $0.2     |
| Time Held: <30m        | 503   | 115   | 388    | 0      | 22.9%     | $-1.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 2069  | 17    | 119    | 1933   | 12.5%     | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 1097  | 40    | 199    | 858    | 16.7%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 260   | 31    | 54     | 175    | 36.5%     | $-0.1    | 🟢          |
| Pre-market             | 2552  | 135   | 324    | 2093   | 29.4%     | $0.2     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 2552   | 1          | 105        | 2446       | 0.0%      | 4.1%      | 95.8%     |
| ORB (9:30-10:00)       | 260    | 0          | 19         | 241        | 0.0%      | 7.3%      | 92.7%     |
| Morning (10:00-12:00)  | 1097   | 3          | 89         | 1005       | 0.3%      | 8.1%      | 91.6%     |
| Afternoon (12:00-16:00) | 2069   | 54         | 432        | 1583       | 2.6%      | 20.9%     | 76.5%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 1206   | 54    | 167    | 985    | 24.4%     | $1.5         | 🟢          |
| Pre-market             | 30-39%     | 893    | 55    | 93     | 745    | 37.2%     | $1.1         | 🟢          |
| Pre-market             | 40-49%     | 347    | 20    | 36     | 291    | 35.7%     | $2.0         | 🟢          |
| Pre-market             | 50-59%     | 93     | 5     | 26     | 62     | 16.1%     | $-0.3        | 🔴          |
| Pre-market             | 60-69%     | 12     | 1     | 2      | 9      | 33.3%     | $-1.3        | ⚠️         |
| Pre-market             | 70-79%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 71     | 15    | 26     | 30     | 36.6%     | $-0.6        | 🟢          |
| ORB (9:30-10:00)       | 30-39%     | 113    | 12    | 20     | 81     | 37.5%     | $0.2         | 🟢          |
| ORB (9:30-10:00)       | 40-49%     | 57     | 2     | 8      | 47     | 20.0%     | $-2.4        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 18     | 2     | 0      | 16     | 100.0%    | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 347    | 28    | 112    | 207    | 20.0%     | $-0.3        | 🔴          |
| Morning (10:00-12:00)  | 30-39%     | 432    | 10    | 70     | 352    | 12.5%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 226    | 2     | 17     | 207    | 10.5%     | $-0.7        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 68     | 0     | 0      | 68     | 0.0%      | $0.0         | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 21     | 0     | 0      | 21     | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 508    | 9     | 83     | 416    | 9.8%      | $-1.4        | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 688    | 6     | 34     | 648    | 15.0%     | $-1.5        | 🔴          |
| Afternoon (12:00-16:00) | 40-49%     | 387    | 2     | 2      | 383    | 50.0%     | $-8.2        | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 224    | 0     | 0      | 224    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 208    | 0     | 0      | 208    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 54     | 0     | 0      | 54     | 0.0%      | $0.0         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2932  | 63    | 417    | 2452   | 13.1%     | $-0.2    |
| SHORT        | 3046  | 160   | 279    | 2607   | 36.4%     | $0.3     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 67    | 11    | 56     | 0      | 16.4%     | $-1.7    |
| Long (30-60 min)       | 416   | 108   | 308    | 0      | 26.0%     | $-1.8    |
| Medium (5-15 min)      | 190   | 45    | 145    | 0      | 23.7%     | $-1.7    |
| Slow (15-30 min)       | 226   | 53    | 173    | 0      | 23.5%     | $-1.6    |
| Very Fast (<1 min)     | 20    | 6     | 14     | 0      | 30.0%     | $-0.4    |
| Very Long (>1h)        | 5059  | 0     | 0      | 5059   | 0.0%      | $0.3     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 24.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.67 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 5059 time-outs): $0.04
- 🎯 Best performance at 60-69% confidence (33.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.06) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.19) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (36.5% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3306s / 55.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 85% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### delta_gamma_squeeze

**Symbols:** AAPL, INTC, NVDA, TSLA  |  **Total Signals:** 125  |  **Win Rate:** 0.0%  |  **Avg P&L (resolved):** $-1.0  |  **Avg P&L (all):** $0.4  |  **Avg Hold:** 1777s (29.6m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 45    | 0     | 0      | 45     | 0.0%      | $0.0     | $0.0     | 0.4%     |
| 20-29%         | 53    | 0     | 2      | 51     | 0.0%      | $0.0     | $0.4     | 8.7%     |
| 30-39%         | 17    | 0     | 0      | 17     | 0.0%      | $0.0     | $1.3     | 22.3%    |
| 40-49%         | 7     | 0     | 0      | 7      | 0.0%      | $0.0     | $0.3     | 2.2%     |
| Other          | 3     | 0     | 0      | 3      | 0.0%      | $0.0     | $0.3     | 11.9%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 88    | 0     | 2      | 86     | 0.0%      | $0.3     |
| Trending (Up)        | 37    | 0     | 0      | 37     | 0.0%      | $0.5     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 125   | 0     | 2      | 123    | 0.0%      | $0.4     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 123   | 0     | 0      | 123    | 0.0%      | $0.4     |
| Time Held: <30m        | 2     | 0     | 2      | 0      | 0.0%      | $-1.0    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Pre-market             | 125   | 0     | 2      | 123    | 0.0%      | $0.4     | —          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 125    | 0          | 0          | 125        | 0.0%      | 0.0%      | 100.0%    |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 78    | 0     | 2      | 76     | 0.0%      | $0.7     |
| SHORT        | 47    | 0     | 0      | 47     | 0.0%      | $-0.2    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Long (30-60 min)       | 123   | 0     | 0      | 123    | 0.0%      | $0.4     |
| Medium (5-15 min)      | 2     | 0     | 2      | 0      | 0.0%      | $-1.0    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 0.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.98 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 123 time-outs): $0.36
- 🎯 Best performance at 20-29% confidence (0.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.54) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.38) — optimal time held is Time Held: 30-90m.
- 🕐 Best signal generation window: Pre-market (0.0% win rate) — signals in this window have the highest hit rate.
- ⏱️ Long avg hold time (1777s / 29.6m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 98% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### depth_decay_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,533  |  **Win Rate:** 33.6%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 1411s (23.5m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 2     | 0     | 1      | 1      | 0.0%      | $0.0     | $-0.2    | -18.2%   |
| 50-59%         | 212   | 13    | 27     | 172    | 32.5%     | $0.0     | $0.2     | 9.2%     |
| 60-69%         | 312   | 36    | 85     | 191    | 29.8%     | $0.0     | $0.0     | -0.5%    |
| 70-79%         | 1376  | 171   | 360    | 845    | 32.2%     | $0.0     | $0.1     | 7.8%     |
| 80-89%         | 606   | 95    | 149    | 362    | 38.9%     | $0.0     | $0.1     | 3.4%     |
| 90-99%         | 25    | 3     | 7      | 15     | 30.0%     | $0.0     | $0.1     | 3.7%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2533  | 318   | 629    | 1586   | 33.6%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2533  | 318   | 629    | 1586   | 33.6%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1586  | 0     | 0      | 1586   | 0.0%      | $0.2     |
| Time Held: <30m        | 947   | 318   | 629    | 0      | 33.6%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 40    | 0     | 4      | 36     | 0.0%      | $-0.0    | 🔴          |
| Afternoon (12:00-16:00) | 939   | 77    | 157    | 705    | 32.9%     | $-0.0    | 🔴          |
| Morning (10:00-12:00)  | 518   | 106   | 176    | 236    | 37.6%     | $0.1     | 🟢          |
| ORB (9:30-10:00)       | 140   | 38    | 77     | 25     | 33.0%     | $-0.1    | 🔴          |
| Pre-market             | 896   | 97    | 215    | 584    | 31.1%     | $0.0     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 896    | 427        | 467        | 2          | 47.7%     | 52.1%     | 0.2%      |
| ORB (9:30-10:00)       | 140    | 128        | 12         | 0          | 91.4%     | 8.6%      | 0.0%      |
| Morning (10:00-12:00)  | 518    | 500        | 18         | 0          | 96.5%     | 3.5%      | 0.0%      |
| Afternoon (12:00-16:00) | 939    | 916        | 23         | 0          | 97.6%     | 2.4%      | 0.0%      |
| After-hours (16:00-20:00) | 40     | 36         | 4          | 0          | 90.0%     | 10.0%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 40-49%     | 2      | 0     | 1      | 1      | 0.0%      | $-2.9        | ⚠️         |
| Pre-market             | 50-59%     | 212    | 13    | 27     | 172    | 32.5%     | $0.7         | 🔴          |
| Pre-market             | 60-69%     | 255    | 27    | 65     | 163    | 29.3%     | $-0.3        | 🔴          |
| Pre-market             | 70-79%     | 296    | 37    | 87     | 172    | 29.8%     | $0.2         | 🔴          |
| Pre-market             | 80-89%     | 125    | 19    | 33     | 73     | 36.5%     | $-0.1        | 🟢          |
| Pre-market             | 90-99%     | 6      | 1     | 2      | 3      | 33.3%     | $0.7         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 12     | 3     | 6      | 3      | 33.3%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 75     | 21    | 41     | 13     | 33.9%     | $-0.1        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 50     | 14    | 28     | 8      | 33.3%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 90-99%     | 3      | 0     | 2      | 1      | 0.0%      | $-2.3        | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 18     | 4     | 8      | 6      | 33.3%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 343    | 65    | 116    | 162    | 35.9%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 153    | 35    | 50     | 68     | 41.2%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 90-99%     | 4      | 2     | 2      | 0      | 50.0%     | $0.4         | ⚠️         |
| Afternoon (12:00-16:00) | 60-69%     | 23     | 2     | 6      | 15     | 25.0%     | $-0.6        | ⚠️         |
| Afternoon (12:00-16:00) | 70-79%     | 648    | 48    | 114    | 486    | 29.6%     | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 260    | 27    | 36     | 197    | 42.9%     | $0.2         | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 8      | 0     | 1      | 7      | 0.0%      | $2.8         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 14     | 0     | 2      | 12     | 0.0%      | $0.4         | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 18     | 0     | 2      | 16     | 0.0%      | $-1.0        | ⚠️         |
| After-hours (16:00-20:00) | 90-99%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1156  | 173   | 254    | 729    | 40.5%     | $0.1     |
| SHORT        | 1377  | 145   | 375    | 857    | 27.9%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 180   | 70    | 110    | 0      | 38.9%     | $0.0     |
| Long (30-60 min)       | 1586  | 0     | 0      | 1586   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 386   | 133   | 253    | 0      | 34.5%     | $-0.2    |
| Slow (15-30 min)       | 349   | 112   | 237    | 0      | 32.1%     | $-0.2    |
| Very Fast (<1 min)     | 32    | 3     | 29     | 0      | 9.4%      | $-1.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.22 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1586 time-outs): $0.02
- 🎯 Best performance at 80-89% confidence (38.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (29.8% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.02) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.17) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (37.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1411s / 23.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 63% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### depth_imbalance_momentum

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,920  |  **Win Rate:** 27.4%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $0.1  |  **Avg Hold:** 1667s (27.8m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 30-39%         | 43    | 0     | 6      | 37     | 0.0%      | $0.0     | $0.1     | 4.5%     |
| 40-49%         | 488   | 21    | 59     | 408    | 26.2%     | $0.0     | $0.2     | 5.7%     |
| 50-59%         | 1162  | 53    | 115    | 994    | 31.5%     | $0.0     | $0.1     | 1.8%     |
| 60-69%         | 157   | 3     | 19     | 135    | 13.6%     | $0.0     | $0.1     | 4.2%     |
| 70-79%         | 70    | 3     | 13     | 54     | 18.8%     | $0.0     | $0.4     | 8.3%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1920  | 80    | 212    | 1628   | 27.4%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1920  | 80    | 212    | 1628   | 27.4%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1628  | 0     | 0      | 1628   | 0.0%      | $0.2     |
| Time Held: <30m        | 292   | 80    | 212    | 0      | 27.4%     | $-0.3    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 34    | 0     | 0      | 34     | 0.0%      | $-0.3    | 🔴          |
| Afternoon (12:00-16:00) | 677   | 0     | 45     | 632    | 0.0%      | $-0.0    | 🔴          |
| Morning (10:00-12:00)  | 349   | 32    | 63     | 254    | 33.7%     | $0.3     | 🟢          |
| ORB (9:30-10:00)       | 100   | 12    | 28     | 60     | 30.0%     | $0.5     | 🟢          |
| Pre-market             | 760   | 36    | 76     | 648    | 32.1%     | $0.0     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 760    | 24         | 554        | 182        | 3.2%      | 72.9%     | 23.9%     |
| ORB (9:30-10:00)       | 100    | 10         | 66         | 24         | 10.0%     | 66.0%     | 24.0%     |
| Morning (10:00-12:00)  | 349    | 12         | 232        | 105        | 3.4%      | 66.5%     | 30.1%     |
| Afternoon (12:00-16:00) | 677    | 20         | 444        | 213        | 3.0%      | 65.6%     | 31.5%     |
| After-hours (16:00-20:00) | 34     | 4          | 23         | 7          | 11.8%     | 67.6%     | 20.6%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 14     | 0     | 3      | 11     | 0.0%      | $-3.7        | ⚠️         |
| Pre-market             | 40-49%     | 168    | 9     | 17     | 142    | 34.6%     | $1.1         | 🟢          |
| Pre-market             | 50-59%     | 509    | 25    | 46     | 438    | 35.2%     | $0.2         | 🟢          |
| Pre-market             | 60-69%     | 45     | 0     | 6      | 39     | 0.0%      | $-0.8        | 🔴          |
| Pre-market             | 70-79%     | 24     | 2     | 4      | 18     | 33.3%     | $1.1         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 2      | 0     | 2      | 0      | 0.0%      | $-1.3        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 22     | 2     | 11     | 9      | 15.4%     | $-1.7        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 52     | 7     | 9      | 36     | 43.8%     | $3.4         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 14     | 2     | 4      | 8      | 33.3%     | $2.6         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 10     | 1     | 2      | 7      | 33.3%     | $0.7         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 10     | 0     | 1      | 9      | 0.0%      | $-0.0        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 95     | 10    | 16     | 69     | 38.5%     | $2.1         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 199    | 21    | 37     | 141    | 36.2%     | $0.8         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 33     | 1     | 5      | 27     | 16.7%     | $1.9         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 12     | 0     | 4      | 8      | 0.0%      | $-0.7        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 15     | 0     | 0      | 15     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 198    | 0     | 15     | 183    | 0.0%      | $0.5         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 383    | 0     | 23     | 360    | 0.0%      | $0.1         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 61     | 0     | 4      | 57     | 0.0%      | $-6.0        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 20     | 0     | 3      | 17     | 0.0%      | $1.7         | ⚠️         |
| After-hours (16:00-20:00) | 30-39%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 5      | 0     | 0      | 5      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 19     | 0     | 0      | 19     | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 240   | 11    | 25     | 204    | 30.6%     | $0.0     |
| SHORT        | 1680  | 69    | 187    | 1424   | 27.0%     | $0.1     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 32    | 5     | 27     | 0      | 15.6%     | $-1.7    |
| Long (30-60 min)       | 1628  | 0     | 0      | 1628   | 0.0%      | $0.2     |
| Medium (5-15 min)      | 115   | 29    | 86     | 0      | 25.2%     | $-0.4    |
| Slow (15-30 min)       | 144   | 46    | 98     | 0      | 31.9%     | $0.0     |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-4.0    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 27.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.34 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1628 time-outs): $0.09
- 🎯 Best performance at 50-59% confidence (31.5% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.09) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.17) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (33.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1667s / 27.8m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 85% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_asymmetry

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,454  |  **Win Rate:** 16.5%  |  **Avg P&L (resolved):** $-1.0  |  **Avg P&L (all):** $0.1  |  **Avg Hold:** 3067s (51.1m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 60-69%         | 1     | 0     | 0      | 1      | 0.0%      | $0.0     | $4.6     | 133.4%   |
| 70-79%         | 88    | 4     | 21     | 63     | 16.0%     | $0.0     | $0.2     | 12.2%    |
| 80-89%         | 1365  | 55    | 277    | 1033   | 16.6%     | $0.0     | $0.4     | 15.7%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1454  | 59    | 298    | 1097   | 16.5%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 1454  | 59    | 298    | 1097   | 16.5%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1216  | 18    | 101    | 1097   | 15.1%     | $0.3     |
| Time Held: <30m        | 238   | 41    | 197    | 0      | 17.2%     | $-0.7    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 614   | 0     | 62     | 552    | 0.0%      | $0.1     | 🔴          |
| Morning (10:00-12:00)  | 387   | 22    | 111    | 254    | 16.5%     | $0.3     | —          |
| ORB (9:30-10:00)       | 118   | 16    | 67     | 35     | 19.3%     | $-0.2    | 🟢          |
| Pre-market             | 335   | 21    | 58     | 256    | 26.6%     | $0.2     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 335    | 334        | 1          | 0          | 99.7%     | 0.3%      | 0.0%      |
| ORB (9:30-10:00)       | 118    | 118        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 387    | 387        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Afternoon (12:00-16:00) | 614    | 614        | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 60-69%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 70-79%     | 57     | 2     | 13     | 42     | 13.3%     | $-0.6        | 🔴          |
| Pre-market             | 80-89%     | 277    | 19    | 45     | 213    | 29.7%     | $0.9         | 🟢          |
| ORB (9:30-10:00)       | 70-79%     | 5      | 1     | 3      | 1      | 25.0%     | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 113    | 15    | 64     | 34     | 19.0%     | $-0.3        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 13     | 1     | 5      | 7      | 16.7%     | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 374    | 21    | 106    | 247    | 16.5%     | $1.0         | —          |
| Afternoon (12:00-16:00) | 70-79%     | 13     | 0     | 0      | 13     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 80-89%     | 601    | 0     | 62     | 539    | 0.0%      | $0.9         | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 721   | 17    | 150    | 554    | 10.2%     | $0.1     |
| SHORT        | 733   | 42    | 148    | 543    | 22.1%     | $0.2     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 44    | 2     | 42     | 0      | 4.5%      | $-2.0    |
| Long (30-60 min)       | 119   | 18    | 101    | 0      | 15.1%     | $-1.5    |
| Medium (5-15 min)      | 100   | 11    | 89     | 0      | 11.0%     | $-1.5    |
| Slow (15-30 min)       | 89    | 28    | 61     | 0      | 31.5%     | $0.9     |
| Very Fast (<1 min)     | 5     | 0     | 5      | 0      | 0.0%      | $-2.2    |
| Very Long (>1h)        | 1097  | 0     | 0      | 1097   | 0.0%      | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 16.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.98 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1097 time-outs): $0.14
- 🎯 Best performance at 80-89% confidence (16.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (16.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.14) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.31) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Pre-market (26.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (3067s / 51.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 75% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,386  |  **Win Rate:** 37.2%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $0.0  |  **Avg Hold:** 1446s (24.1m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 10-19%         | 15    | 1     | 2      | 12     | 33.3%     | $0.0     | $0.2     | 14.3%    |
| 20-29%         | 78    | 9     | 11     | 58     | 45.0%     | $0.0     | $0.1     | 9.1%     |
| 30-39%         | 272   | 21    | 39     | 212    | 35.0%     | $0.0     | $0.2     | 11.5%    |
| 40-49%         | 614   | 70    | 131    | 413    | 34.8%     | $0.0     | $0.1     | 6.2%     |
| 50-59%         | 412   | 46    | 106    | 260    | 30.3%     | $0.0     | $0.1     | 7.4%     |
| 60-69%         | 995   | 153   | 217    | 625    | 41.4%     | $0.0     | $0.1     | 5.1%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2386  | 300   | 506    | 1580   | 37.2%     | $0.0     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2386  | 300   | 506    | 1580   | 37.2%     | $0.0     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1580  | 0     | 0      | 1580   | 0.0%      | $0.1     |
| Time Held: <30m        | 806   | 300   | 506    | 0      | 37.2%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 65    | 0     | 1      | 64     | 0.0%      | $-0.0    | 🔴          |
| Afternoon (12:00-16:00) | 908   | 64    | 133    | 711    | 32.5%     | $-0.0    | 🔴          |
| Morning (10:00-12:00)  | 484   | 97    | 165    | 222    | 37.0%     | $0.1     | 🔴          |
| ORB (9:30-10:00)       | 134   | 34    | 71     | 29     | 32.4%     | $-0.1    | 🔴          |
| Pre-market             | 795   | 105   | 136    | 554    | 43.6%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 795    | 0          | 586        | 209        | 0.0%      | 73.7%     | 26.3%     |
| ORB (9:30-10:00)       | 134    | 0          | 95         | 39         | 0.0%      | 70.9%     | 29.1%     |
| Morning (10:00-12:00)  | 484    | 0          | 271        | 213        | 0.0%      | 56.0%     | 44.0%     |
| Afternoon (12:00-16:00) | 908    | 0          | 409        | 499        | 0.0%      | 45.0%     | 55.0%     |
| After-hours (16:00-20:00) | 65     | 0          | 46         | 19         | 0.0%      | 70.8%     | 29.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 82     | 5     | 13     | 64     | 27.8%     | $0.0         | 🔴          |
| Pre-market             | 40-49%     | 127    | 21    | 28     | 78     | 42.9%     | $-0.0        | 🟢          |
| Pre-market             | 50-59%     | 98     | 11    | 23     | 64     | 32.4%     | $0.1         | 🔴          |
| Pre-market             | 60-69%     | 488    | 68    | 72     | 348    | 48.6%     | $0.4         | 🟢          |
| ORB (9:30-10:00)       | 20-29%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 7      | 2     | 3      | 2      | 40.0%     | $0.7         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 31     | 3     | 17     | 11     | 15.0%     | $-0.7        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 32     | 7     | 14     | 11     | 33.3%     | $0.0         | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 63     | 22    | 37     | 4      | 37.3%     | $-0.1        | 🟢          |
| Morning (10:00-12:00)  | 10-19%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 16     | 2     | 1      | 13     | 66.7%     | $1.4         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 54     | 5     | 11     | 38     | 31.2%     | $0.6         | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 141    | 21    | 44     | 76     | 32.3%     | $-0.1        | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 100    | 20    | 41     | 39     | 32.8%     | $-0.1        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 171    | 49    | 68     | 54     | 41.9%     | $0.4         | 🟢          |
| Afternoon (12:00-16:00) | 10-19%     | 13     | 1     | 2      | 10     | 33.3%     | $-0.8        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 61     | 7     | 10     | 44     | 41.2%     | $-0.0        | 🟢          |
| Afternoon (12:00-16:00) | 30-39%     | 121    | 9     | 12     | 100    | 42.9%     | $1.1         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 304    | 25    | 42     | 237    | 37.3%     | $-0.2        | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 179    | 8     | 28     | 143    | 22.2%     | $-0.6        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 230    | 14    | 39     | 177    | 26.4%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 8      | 0     | 0      | 8      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 11     | 0     | 0      | 11     | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 43     | 0     | 1      | 42     | 0.0%      | $-1.8        | 🔴          |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1734  | 225   | 337    | 1172   | 40.0%     | $0.1     |
| SHORT        | 652   | 75    | 169    | 408    | 30.7%     | $-0.0    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 163   | 58    | 105    | 0      | 35.6%     | $-0.1    |
| Long (30-60 min)       | 1580  | 0     | 0      | 1580   | 0.0%      | $0.1     |
| Medium (5-15 min)      | 322   | 122   | 200    | 0      | 37.9%     | $-0.2    |
| Slow (15-30 min)       | 292   | 115   | 177    | 0      | 39.4%     | $-0.2    |
| Very Fast (<1 min)     | 29    | 5     | 24     | 0      | 17.2%     | $-1.0    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 37.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.19 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 1580 time-outs): $0.03
- 🎯 Best performance at 20-29% confidence (45.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (30.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $0.03) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.14) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Pre-market (43.6% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1446s / 24.1m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 66% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### exchange_flow_imbalance

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,385  |  **Win Rate:** 21.4%  |  **Avg P&L (resolved):** $-0.6  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 2006s (33.4m)  |  **Median Hold:** 2700s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 4     | 0     | 2      | 2      | 0.0%      | $0.0     | $0.2     | 11.3%    |
| 30-39%         | 14    | 1     | 4      | 9      | 20.0%     | $0.0     | $0.3     | 18.9%    |
| 40-49%         | 58    | 2     | 18     | 38     | 10.0%     | $0.0     | $0.2     | 10.7%    |
| 50-59%         | 408   | 39    | 133    | 236    | 22.7%     | $0.0     | $0.1     | 8.5%     |
| 60-69%         | 439   | 36    | 129    | 274    | 21.8%     | $0.0     | $0.2     | 13.8%    |
| 70-79%         | 943   | 92    | 333    | 518    | 21.6%     | $0.0     | $0.2     | 12.2%    |
| 80-89%         | 519   | 51    | 194    | 274    | 20.8%     | $0.0     | $0.2     | 12.4%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| UNKNOWN              | 2385  | 221   | 813    | 1351   | 21.4%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2385  | 221   | 813    | 1351   | 21.4%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1590  | 58    | 181    | 1351   | 24.3%     | $0.3     |
| Time Held: <30m        | 795   | 163   | 632    | 0      | 20.5%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 4     | 0     | 2      | 2      | 0.0%      | $-0.8    | ⚠️         |
| Afternoon (12:00-16:00) | 722   | 33    | 176    | 513    | 15.8%     | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 424   | 66    | 200    | 158    | 24.8%     | $0.1     | 🟢          |
| ORB (9:30-10:00)       | 125   | 23    | 86     | 16     | 21.1%     | $-0.3    | 🔴          |
| Pre-market             | 1110  | 99    | 349    | 662    | 22.1%     | $0.0     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1110   | 735        | 372        | 3          | 66.2%     | 33.5%     | 0.3%      |
| ORB (9:30-10:00)       | 125    | 93         | 30         | 2          | 74.4%     | 24.0%     | 1.6%      |
| Morning (10:00-12:00)  | 424    | 259        | 148        | 17         | 61.1%     | 34.9%     | 4.0%      |
| Afternoon (12:00-16:00) | 722    | 372        | 296        | 54         | 51.5%     | 41.0%     | 7.5%      |
| After-hours (16:00-20:00) | 4      | 3          | 1          | 0          | 75.0%     | 25.0%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 30-39%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 40-49%     | 2      | 1     | 1      | 0      | 50.0%     | $0.3         | ⚠️         |
| Pre-market             | 50-59%     | 187    | 19    | 72     | 96     | 20.9%     | $-0.4        | 🔴          |
| Pre-market             | 60-69%     | 185    | 20    | 47     | 118    | 29.9%     | $0.7         | 🟢          |
| Pre-market             | 70-79%     | 464    | 42    | 147    | 275    | 22.2%     | $0.1         | 🟢          |
| Pre-market             | 80-89%     | 271    | 17    | 82     | 172    | 17.2%     | $-0.2        | 🔴          |
| ORB (9:30-10:00)       | 40-49%     | 2      | 0     | 1      | 1      | 0.0%      | $-2.5        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 11     | 3     | 4      | 4      | 42.9%     | $0.4         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 19     | 3     | 16     | 0      | 15.8%     | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 64     | 13    | 41     | 10     | 24.1%     | $-0.1        | 🟢          |
| ORB (9:30-10:00)       | 80-89%     | 29     | 4     | 24     | 1      | 14.3%     | $-0.9        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.1        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 3      | 0     | 3      | 0      | 0.0%      | $-1.4        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 13     | 0     | 3      | 10     | 0.0%      | $-0.5        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 66     | 8     | 28     | 30     | 22.2%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 82     | 9     | 33     | 40     | 21.4%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 161    | 26    | 85     | 50     | 23.4%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 98     | 23    | 47     | 28     | 32.9%     | $0.2         | 🟢          |
| Afternoon (12:00-16:00) | 20-29%     | 3      | 0     | 1      | 2      | 0.0%      | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 10     | 1     | 1      | 8      | 50.0%     | $1.4         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 41     | 1     | 13     | 27     | 7.1%      | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 144    | 9     | 29     | 106    | 23.7%     | $-0.0        | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 152    | 4     | 33     | 115    | 10.8%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 253    | 11    | 59     | 183    | 15.7%     | $-0.0        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 119    | 7     | 40     | 72     | 14.9%     | $-0.7        | 🔴          |
| After-hours (16:00-20:00) | 60-69%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.6        | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 2      | 0     | 1      | 1      | 0.0%      | $-2.5        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1072  | 98    | 349    | 625    | 21.9%     | $-0.0    |
| SHORT        | 1313  | 123   | 464    | 726    | 21.0%     | $0.0     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 166   | 29    | 137    | 0      | 17.5%     | $-0.9    |
| Long (30-60 min)       | 1590  | 58    | 181    | 1351   | 24.3%     | $0.3     |
| Medium (5-15 min)      | 290   | 59    | 231    | 0      | 20.3%     | $-0.6    |
| Slow (15-30 min)       | 312   | 75    | 237    | 0      | 24.0%     | $-0.4    |
| Very Fast (<1 min)     | 27    | 0     | 27     | 0      | 0.0%      | $-1.1    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 21.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.56 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1351 time-outs): $-0.02
- 🎯 Best performance at 50-59% confidence (22.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 40-49% (10.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: UNKNOWN (avg P&L $-0.02) — this strategy thrives in unknown conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.26) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Morning (10:00-12:00) (24.8% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2006s / 33.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 57% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 3,021  |  **Win Rate:** 37.4%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.0  |  **Avg Hold:** 2343s (39.0m)  |  **Median Hold:** 2914s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 66    | 0     | 3      | 63     | 0.0%      | $0.0     | $-0.3    | -9.0%    |
| 30-39%         | 343   | 69    | 40     | 234    | 63.3%     | $0.0     | $0.2     | 7.5%     |
| 40-49%         | 518   | 106   | 107    | 305    | 49.8%     | $0.0     | $0.3     | 8.5%     |
| 50-59%         | 463   | 115   | 115    | 233    | 50.0%     | $0.0     | $0.1     | 5.3%     |
| 60-69%         | 609   | 115   | 198    | 296    | 36.7%     | $0.0     | $0.2     | 8.1%     |
| 70-79%         | 365   | 88    | 167    | 110    | 34.5%     | $0.0     | $0.1     | 9.6%     |
| 80-89%         | 505   | 95    | 296    | 114    | 24.3%     | $0.0     | $0.1     | 16.4%    |
| 90-99%         | 152   | 30    | 108    | 14     | 21.7%     | $0.0     | $0.1     | 10.5%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1767  | 329   | 623    | 815    | 34.6%     | $-0.0    |
| Trending (Up)        | 1254  | 289   | 411    | 554    | 41.3%     | $-0.0    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 3021  | 618   | 1034   | 1369   | 37.4%     | $-0.0    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1842  | 189   | 284    | 1369   | 40.0%     | $0.3     |
| Time Held: <30m        | 1179  | 429   | 750    | 0      | 36.4%     | $-0.4    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 44    | 19    | 25     | 0      | 43.2%     | $0.0     | 🟢          |
| Afternoon (12:00-16:00) | 1139  | 144   | 342    | 653    | 29.6%     | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 588   | 121   | 206    | 261    | 37.0%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 139   | 36    | 64     | 39     | 36.0%     | $-0.4    | 🔴          |
| Pre-market             | 1111  | 298   | 397    | 416    | 42.9%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1111   | 384        | 359        | 368        | 34.6%     | 32.3%     | 33.1%     |
| ORB (9:30-10:00)       | 139    | 5          | 59         | 75         | 3.6%      | 42.4%     | 54.0%     |
| Morning (10:00-12:00)  | 588    | 170        | 237        | 181        | 28.9%     | 40.3%     | 30.8%     |
| Afternoon (12:00-16:00) | 1139   | 430        | 406        | 303        | 37.8%     | 35.6%     | 26.6%     |
| After-hours (16:00-20:00) | 44     | 33         | 11         | 0          | 75.0%     | 25.0%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 43     | 0     | 0      | 43     | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 30-39%     | 151    | 29    | 22     | 100    | 56.9%     | $0.3         | 🟢          |
| Pre-market             | 40-49%     | 174    | 57    | 54     | 63     | 51.4%     | $-0.2        | 🟢          |
| Pre-market             | 50-59%     | 155    | 52    | 27     | 76     | 65.8%     | $1.3         | 🟢          |
| Pre-market             | 60-69%     | 204    | 49    | 66     | 89     | 42.6%     | $0.2         | 🟢          |
| Pre-market             | 70-79%     | 152    | 56    | 74     | 22     | 43.1%     | $0.4         | 🟢          |
| Pre-market             | 80-89%     | 185    | 45    | 117    | 23     | 27.8%     | $-0.1        | 🔴          |
| Pre-market             | 90-99%     | 47     | 10    | 37     | 0      | 21.3%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 20-29%     | 10     | 0     | 1      | 9      | 0.0%      | $-11.0       | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 25     | 10    | 11     | 4      | 47.6%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 40     | 11    | 19     | 10     | 36.7%     | $-0.3        | 🔴          |
| ORB (9:30-10:00)       | 50-59%     | 36     | 8     | 21     | 7      | 27.6%     | $-0.9        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 23     | 6     | 8      | 9      | 42.9%     | $-0.3        | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 5      | 1     | 4      | 0      | 20.0%     | $-0.7        | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 6      | 0     | 2      | 4      | 0.0%      | $-5.0        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 56     | 17    | 7      | 32     | 70.8%     | $3.4         | 🟢          |
| Morning (10:00-12:00)  | 40-49%     | 119    | 16    | 24     | 79     | 40.0%     | $0.1         | 🟢          |
| Morning (10:00-12:00)  | 50-59%     | 122    | 36    | 45     | 41     | 44.4%     | $-1.4        | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 115    | 18    | 51     | 46     | 26.1%     | $-0.0        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 87     | 19    | 36     | 32     | 34.5%     | $-0.2        | 🔴          |
| Morning (10:00-12:00)  | 80-89%     | 70     | 13    | 31     | 26     | 29.5%     | $0.2         | 🔴          |
| Morning (10:00-12:00)  | 90-99%     | 13     | 2     | 10     | 1      | 16.7%     | $-0.2        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 7      | 0     | 0      | 7      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 111    | 13    | 0      | 98     | 100.0%    | $1.5         | 🟢          |
| Afternoon (12:00-16:00) | 40-49%     | 185    | 22    | 10     | 153    | 68.8%     | $1.3         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 149    | 18    | 22     | 109    | 45.0%     | $-0.4        | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 257    | 32    | 73     | 152    | 30.5%     | $-0.2        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 120    | 12    | 52     | 56     | 18.8%     | $-0.6        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 244    | 37    | 142    | 65     | 20.7%     | $-0.4        | 🔴          |
| Afternoon (12:00-16:00) | 90-99%     | 66     | 10    | 43     | 13     | 18.9%     | $-0.1        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 1      | 1     | 0      | 0      | 100.0%    | $0.5         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 10     | 10    | 0      | 0      | 100.0%    | $0.9         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 1      | 0     | 1      | 0      | 0.0%      | $-2.8        | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 6      | 0     | 6      | 0      | 0.0%      | $-0.6        | ⚠️         |
| After-hours (16:00-20:00) | 90-99%     | 26     | 8     | 18     | 0      | 30.8%     | $-0.1        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1570  | 352   | 463    | 755    | 43.2%     | $-0.0    |
| SHORT        | 1451  | 266   | 571    | 614    | 31.8%     | $0.0     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 206   | 74    | 132    | 0      | 35.9%     | $-0.6    |
| Long (30-60 min)       | 473   | 189   | 284    | 0      | 40.0%     | $-0.0    |
| Medium (5-15 min)      | 463   | 142   | 321    | 0      | 30.7%     | $-0.7    |
| Slow (15-30 min)       | 456   | 165   | 291    | 0      | 36.2%     | $-0.2    |
| Very Fast (<1 min)     | 54    | 48    | 6      | 0      | 88.9%     | $0.2     |
| Very Long (>1h)        | 1369  | 0     | 0      | 1369   | 0.0%      | $0.4     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 37.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.32 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 1369 time-outs): $-0.01
- 🎯 Best performance at 30-39% confidence (63.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.01) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.26) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: After-hours (16:00-20:00) (43.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2343s / 39.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 45% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_squeeze

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 452  |  **Win Rate:** 1.4%  |  **Avg P&L (resolved):** $-1.4  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 1631s (27.2m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 1     | 0     | 0      | 1      | 0.0%      | $0.0     | $2.4     | 90.0%    |
| 30-39%         | 19    | 0     | 0      | 19     | 0.0%      | $0.0     | $1.7     | 65.2%    |
| 40-49%         | 21    | 0     | 4      | 17     | 0.0%      | $0.0     | $0.3     | 16.5%    |
| 50-59%         | 263   | 1     | 27     | 235    | 3.6%      | $0.0     | $0.0     | 2.7%     |
| 60-69%         | 147   | 0     | 40     | 107    | 0.0%      | $0.0     | $0.1     | 6.7%     |
| 70-79%         | 1     | 0     | 0      | 1      | 0.0%      | $0.0     | $-0.6    | -34.8%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 286   | 0     | 33     | 253    | 0.0%      | $-0.0    |
| Trending (Up)        | 166   | 1     | 38     | 127    | 2.6%      | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 452   | 1     | 71     | 380    | 1.4%      | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 380   | 0     | 0      | 380    | 0.0%      | $0.2     |
| Time Held: <30m        | 72    | 1     | 71     | 0      | 1.4%      | $-1.4    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 23    | 0     | 0      | 23     | 0.0%      | $-0.3    | ⚠️         |
| Afternoon (12:00-16:00) | 203   | 0     | 12     | 191    | 0.0%      | $-0.1    | 🔴          |
| Morning (10:00-12:00)  | 64    | 0     | 26     | 38     | 0.0%      | $-0.4    | 🔴          |
| ORB (9:30-10:00)       | 34    | 1     | 15     | 18     | 6.2%      | $-0.2    | 🟢          |
| Pre-market             | 128   | 0     | 18     | 110    | 0.0%      | $0.2     | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 128    | 0          | 91         | 37         | 0.0%      | 71.1%     | 28.9%     |
| ORB (9:30-10:00)       | 34     | 0          | 32         | 2          | 0.0%      | 94.1%     | 5.9%      |
| Morning (10:00-12:00)  | 64     | 0          | 62         | 2          | 0.0%      | 96.9%     | 3.1%      |
| Afternoon (12:00-16:00) | 203    | 0          | 203        | 0          | 0.0%      | 100.0%    | 0.0%      |
| After-hours (16:00-20:00) | 23     | 1          | 22         | 0          | 4.3%      | 95.7%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 30-39%     | 19     | 0     | 0      | 19     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 40-49%     | 17     | 0     | 0      | 17     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 50-59%     | 68     | 0     | 7      | 61     | 0.0%      | $-1.2        | 🔴          |
| Pre-market             | 60-69%     | 23     | 0     | 11     | 12     | 0.0%      | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.5        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 31     | 1     | 12     | 18     | 7.7%      | $0.0         | 🟢          |
| ORB (9:30-10:00)       | 60-69%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.6        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 2      | 0     | 2      | 0      | 0.0%      | $-2.8        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 32     | 0     | 8      | 24     | 0.0%      | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 30     | 0     | 16     | 14     | 0.0%      | $-0.9        | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 131    | 0     | 0      | 131    | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 72     | 0     | 12     | 60     | 0.0%      | $-0.8        | 🔴          |
| After-hours (16:00-20:00) | 50-59%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 21     | 0     | 0      | 21     | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 452   | 1     | 71     | 380    | 1.4%      | $-0.1    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 18    | 0     | 18     | 0      | 0.0%      | $-1.9    |
| Long (30-60 min)       | 380   | 0     | 0      | 380    | 0.0%      | $0.2     |
| Medium (5-15 min)      | 24    | 0     | 24     | 0      | 0.0%      | $-1.3    |
| Slow (15-30 min)       | 26    | 1     | 25     | 0      | 3.8%      | $-1.2    |
| Very Fast (<1 min)     | 4     | 0     | 4      | 0      | 0.0%      | $-2.3    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 1.4% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-1.44 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 380 time-outs): $-0.10
- 🎯 Best performance at 50-59% confidence (3.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.03) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.16) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (6.2% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (1631s / 27.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 84% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AAPL, AMD, INTC, TSLA  |  **Total Signals:** 893  |  **Win Rate:** 33.3%  |  **Avg P&L (resolved):** $0.0  |  **Avg P&L (all):** $0.1  |  **Avg Hold:** 1763s (29.4m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 6     | 0     | 0      | 6      | 0.0%      | $0.0     | $3.0     | 75.8%    |
| 30-39%         | 27    | 1     | 0      | 26     | 100.0%    | $0.0     | $0.7     | 16.9%    |
| 40-49%         | 135   | 1     | 3      | 131    | 25.0%     | $0.0     | $-0.2    | -6.0%    |
| 50-59%         | 177   | 0     | 12     | 165    | 0.0%      | $0.0     | $-0.1    | -3.9%    |
| 60-69%         | 101   | 0     | 2      | 99     | 0.0%      | $0.0     | $0.3     | 12.2%    |
| 70-79%         | 112   | 4     | 6      | 102    | 40.0%     | $0.0     | $0.5     | 16.1%    |
| 80-89%         | 114   | 6     | 0      | 108    | 100.0%    | $0.0     | $0.2     | 7.3%     |
| 90-99%         | 39    | 1     | 0      | 38     | 100.0%    | $0.0     | $-0.3    | -13.0%   |
| 100%           | 182   | 3     | 9      | 170    | 25.0%     | $0.0     | $-0.2    | -12.2%   |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 479   | 6     | 14     | 459    | 30.0%     | $0.0     |
| Trending (Up)        | 414   | 10    | 18     | 386    | 35.7%     | $0.1     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 893   | 16    | 32     | 845    | 33.3%     | $0.1     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 845   | 0     | 0      | 845    | 0.0%      | $0.1     |
| Time Held: <30m        | 48    | 16    | 32     | 0      | 33.3%     | $0.0     |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 18    | 0     | 0      | 18     | 0.0%      | $-0.2    | ⚠️         |
| Afternoon (12:00-16:00) | 378   | 4     | 7      | 367    | 36.4%     | $0.1     | 🟢          |
| Morning (10:00-12:00)  | 121   | 3     | 9      | 109    | 25.0%     | $0.0     | 🔴          |
| ORB (9:30-10:00)       | 13    | 6     | 0      | 7      | 100.0%    | $2.3     | ⚠️         |
| Pre-market             | 363   | 3     | 16     | 344    | 15.8%     | $-0.0    | 🔴          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 363    | 47         | 173        | 143        | 12.9%     | 47.7%     | 39.4%     |
| ORB (9:30-10:00)       | 13     | 13         | 0          | 0          | 100.0%    | 0.0%      | 0.0%      |
| Morning (10:00-12:00)  | 121    | 98         | 23         | 0          | 81.0%     | 19.0%     | 0.0%      |
| Afternoon (12:00-16:00) | 378    | 279        | 78         | 21         | 73.8%     | 20.6%     | 5.6%      |
| After-hours (16:00-20:00) | 18     | 10         | 4          | 4          | 55.6%     | 22.2%     | 22.2%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 6      | 0     | 0      | 6      | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 30-39%     | 22     | 1     | 0      | 21     | 100.0%    | $24.9        | ⚠️         |
| Pre-market             | 40-49%     | 115    | 1     | 2      | 112    | 33.3%     | $-7.4        | —          |
| Pre-market             | 50-59%     | 121    | 0     | 11     | 110    | 0.0%      | $-4.7        | 🔴          |
| Pre-market             | 60-69%     | 52     | 0     | 1      | 51     | 0.0%      | $5.2         | 🔴          |
| Pre-market             | 70-79%     | 44     | 0     | 2      | 42     | 0.0%      | $7.3         | 🔴          |
| Pre-market             | 80-89%     | 3      | 1     | 0      | 2      | 100.0%    | $7.7         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 4      | 4     | 0      | 0      | 100.0%    | $5.2         | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 2      | 1     | 0      | 1      | 100.0%    | $4.1         | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 100%       | 5      | 1     | 0      | 4      | 100.0%    | $5.9         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 6      | 0     | 0      | 6      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 17     | 0     | 0      | 17     | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 80-89%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 1      | 1     | 0      | 0      | 100.0%    | $3.7         | ⚠️         |
| Morning (10:00-12:00)  | 100%       | 92     | 2     | 9      | 81     | 18.2%     | $-2.8        | 🔴          |
| Afternoon (12:00-16:00) | 30-39%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 17     | 0     | 1      | 16     | 0.0%      | $-3.7        | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 46     | 0     | 1      | 45     | 0.0%      | $-7.4        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 32     | 0     | 1      | 31     | 0.0%      | $10.1        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 60     | 0     | 4      | 56     | 0.0%      | $5.7         | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 108    | 4     | 0      | 104    | 100.0%    | $7.0         | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 35     | 0     | 0      | 35     | 0.0%      | $0.0         | 🔴          |
| Afternoon (12:00-16:00) | 100%       | 76     | 0     | 0      | 76     | 0.0%      | $0.0         | 🔴          |
| After-hours (16:00-20:00) | 30-39%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 40-49%     | 3      | 0     | 0      | 3      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 90-99%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 100%       | 9      | 0     | 0      | 9      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 363   | 2     | 11     | 350    | 15.4%     | $-0.0    |
| SHORT        | 530   | 14    | 21     | 495    | 40.0%     | $0.1     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 1     | 1     | 0      | 0      | 100.0%    | $3.4     |
| Long (30-60 min)       | 845   | 0     | 0      | 845    | 0.0%      | $0.1     |
| Medium (5-15 min)      | 14    | 10    | 4      | 0      | 71.4%     | $2.3     |
| Slow (15-30 min)       | 32    | 5     | 27     | 0      | 15.6%     | $-1.0    |
| Very Fast (<1 min)     | 1     | 0     | 1      | 0      | 0.0%      | $-2.2    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 33.3% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L per resolved signal: $0.01 — profitable even with 33.3% win rate (good risk/reward).
- 💰 Avg P&L per signal (incl. 845 time-outs): $0.06
- 🎯 Best performance at 80-89% confidence (100.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.10) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.06) — optimal time held is Time Held: 30-90m.
- ⚠️ Best signal generation window: ORB (9:30-10:00) (100.0% win rate) — but only 13 signals, results may not be statistically significant.
- ⏱️ Long avg hold time (1763s / 29.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 95% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_divergence

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 1,251  |  **Win Rate:** 37.5%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 2155s (35.9m)  |  **Median Hold:** 2192s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 40-49%         | 85    | 24    | 16     | 45     | 60.0%     | $0.0     | $0.2     | 13.1%    |
| 50-59%         | 263   | 47    | 130    | 86     | 26.6%     | $0.0     | $0.1     | 2.9%     |
| 60-69%         | 741   | 169   | 276    | 296    | 38.0%     | $0.0     | $0.1     | 4.6%     |
| 70-79%         | 106   | 46    | 43     | 17     | 51.7%     | $0.0     | $0.1     | 6.3%     |
| 80-89%         | 48    | 17    | 31     | 0      | 35.4%     | $0.0     | $0.0     | 0.0%     |
| 90-99%         | 8     | 0     | 8      | 0      | 0.0%      | $0.0     | $0.0     | 0.0%     |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1050  | 275   | 395    | 380    | 41.0%     | $-0.0    |
| Trending (Up)        | 201   | 28    | 109    | 64     | 20.4%     | $-0.4    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 1251  | 303   | 504    | 444    | 37.5%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 701   | 89    | 168    | 444    | 34.6%     | $0.0     |
| Time Held: <30m        | 550   | 214   | 336    | 0      | 38.9%     | $-0.2    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 505   | 99    | 154    | 252    | 39.1%     | $-0.2    | 🟢          |
| Morning (10:00-12:00)  | 317   | 73    | 152    | 92     | 32.4%     | $-0.1    | 🔴          |
| ORB (9:30-10:00)       | 99    | 25    | 70     | 4      | 26.3%     | $-0.4    | 🔴          |
| Pre-market             | 330   | 106   | 128    | 96     | 45.3%     | $0.1     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 330    | 4          | 273        | 53         | 1.2%      | 82.7%     | 16.1%     |
| ORB (9:30-10:00)       | 99     | 42         | 57         | 0          | 42.4%     | 57.6%     | 0.0%      |
| Morning (10:00-12:00)  | 317    | 73         | 237        | 7          | 23.0%     | 74.8%     | 2.2%      |
| Afternoon (12:00-16:00) | 505    | 43         | 437        | 25         | 8.5%      | 86.5%     | 5.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 40-49%     | 53     | 23    | 3      | 27     | 88.5%     | $2.4         | 🟢          |
| Pre-market             | 50-59%     | 147    | 47    | 63     | 37     | 42.7%     | $-0.1        | 🟢          |
| Pre-market             | 60-69%     | 126    | 33    | 61     | 32     | 35.1%     | $-0.1        | 🔴          |
| Pre-market             | 70-79%     | 4      | 3     | 1      | 0      | 75.0%     | $2.6         | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 57     | 17    | 36     | 4      | 32.1%     | $-0.1        | 🔴          |
| ORB (9:30-10:00)       | 70-79%     | 13     | 4     | 9      | 0      | 30.8%     | $-0.4        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 23     | 4     | 19     | 0      | 17.4%     | $-0.8        | ⚠️         |
| ORB (9:30-10:00)       | 90-99%     | 6      | 0     | 6      | 0      | 0.0%      | $-0.9        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 7      | 1     | 0      | 6      | 100.0%    | $2.4         | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 54     | 0     | 39     | 15     | 0.0%      | $-1.1        | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 183    | 42    | 76     | 65     | 35.6%     | $0.1         | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 48     | 19    | 23     | 6      | 45.2%     | $0.3         | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 23     | 11    | 12     | 0      | 47.8%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 2      | 0     | 2      | 0      | 0.0%      | $-0.6        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 25     | 0     | 13     | 12     | 0.0%      | $-1.4        | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 62     | 0     | 28     | 34     | 0.0%      | $-1.0        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 375    | 77    | 103    | 195    | 42.8%     | $-0.4        | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 41     | 20    | 10     | 11     | 66.7%     | $1.1         | 🟢          |
| Afternoon (12:00-16:00) | 80-89%     | 2      | 2     | 0      | 0      | 100.0%    | $0.9         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 1120  | 302   | 430    | 388    | 41.3%     | $-0.0    |
| SHORT        | 131   | 1     | 74     | 56     | 1.3%      | $-0.6    |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 103   | 25    | 78     | 0      | 24.3%     | $-0.8    |
| Long (30-60 min)       | 257   | 89    | 168    | 0      | 34.6%     | $-0.3    |
| Medium (5-15 min)      | 211   | 95    | 116    | 0      | 45.0%     | $0.0     |
| Slow (15-30 min)       | 215   | 93    | 122    | 0      | 43.3%     | $0.0     |
| Very Fast (<1 min)     | 21    | 1     | 20     | 0      | 4.8%      | $-1.4    |
| Very Long (>1h)        | 444   | 0     | 0      | 444    | 0.0%      | $0.2     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 37.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.23 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 444 time-outs): $-0.07
- 🎯 Best performance at 40-49% confidence (60.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-99% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.00) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.02) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: Pre-market (45.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2155s / 35.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 35% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### magnet_accelerate

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 2,450  |  **Win Rate:** 20.2%  |  **Avg P&L (resolved):** $-0.5  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 2145s (35.7m)  |  **Median Hold:** 2142s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 155   | 0     | 89     | 66     | 0.0%      | $0.0     | $0.1     | 10.8%    |
| 30-39%         | 148   | 3     | 35     | 110    | 7.9%      | $0.0     | $-0.1    | -8.2%    |
| 40-49%         | 258   | 14    | 131    | 113    | 9.7%      | $0.0     | $0.2     | 40.4%    |
| 50-59%         | 464   | 37    | 241    | 186    | 13.3%     | $0.0     | $0.3     | 36.4%    |
| 60-69%         | 671   | 78    | 345    | 248    | 18.4%     | $0.0     | $0.3     | 25.6%    |
| 70-79%         | 536   | 113   | 278    | 145    | 28.9%     | $0.0     | $0.1     | 4.7%     |
| 80-89%         | 209   | 63    | 97     | 49     | 39.4%     | $0.0     | $-0.0    | -1.6%    |
| 90-99%         | 9     | 1     | 6      | 2      | 14.3%     | $0.0     | $0.0     | 17.4%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 1513  | 178   | 822    | 513    | 17.8%     | $-0.1    |
| Trending (Up)        | 937   | 131   | 400    | 406    | 24.7%     | $-0.1    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 2450  | 309   | 1222   | 919    | 20.2%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 1377  | 108   | 350    | 919    | 23.6%     | $0.2     |
| Time Held: <30m        | 1073  | 201   | 872    | 0      | 18.7%     | $-0.6    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 22    | 0     | 22     | 0      | 0.0%      | $-0.8    | ⚠️         |
| Afternoon (12:00-16:00) | 792   | 42    | 395    | 355    | 9.6%      | $-0.2    | 🔴          |
| Morning (10:00-12:00)  | 246   | 41    | 129    | 76     | 24.1%     | $-0.1    | 🟢          |
| ORB (9:30-10:00)       | 113   | 46    | 67     | 0      | 40.7%     | $0.0     | 🟢          |
| Pre-market             | 1277  | 180   | 609    | 488    | 22.8%     | $-0.1    | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 1277   | 256        | 532        | 489        | 20.0%     | 41.7%     | 38.3%     |
| ORB (9:30-10:00)       | 113    | 42         | 59         | 12         | 37.2%     | 52.2%     | 10.6%     |
| Morning (10:00-12:00)  | 246    | 80         | 137        | 29         | 32.5%     | 55.7%     | 11.8%     |
| Afternoon (12:00-16:00) | 792    | 359        | 402        | 31         | 45.3%     | 50.8%     | 3.9%      |
| After-hours (16:00-20:00) | 22     | 17         | 5          | 0          | 77.3%     | 22.7%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 155    | 0     | 89     | 66     | 0.0%      | $-0.4        | 🔴          |
| Pre-market             | 30-39%     | 145    | 3     | 33     | 109    | 8.3%      | $-2.5        | 🔴          |
| Pre-market             | 40-49%     | 189    | 11    | 79     | 99     | 12.2%     | $0.0         | 🔴          |
| Pre-market             | 50-59%     | 281    | 33    | 135    | 113    | 19.6%     | $0.2         | 🔴          |
| Pre-market             | 60-69%     | 251    | 43    | 136    | 72     | 24.0%     | $0.1         | 🟢          |
| Pre-market             | 70-79%     | 181    | 65    | 93     | 23     | 41.1%     | $-0.1        | 🟢          |
| Pre-market             | 80-89%     | 70     | 25    | 40     | 5      | 38.5%     | $-0.4        | 🟢          |
| Pre-market             | 90-99%     | 5      | 0     | 4      | 1      | 0.0%      | $-0.8        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.5        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 11     | 0     | 11     | 0      | 0.0%      | $-0.7        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 30     | 4     | 26     | 0      | 13.3%     | $-0.6        | 🔴          |
| ORB (9:30-10:00)       | 60-69%     | 29     | 14    | 15     | 0      | 48.3%     | $0.6         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 26     | 16    | 10     | 0      | 61.5%     | $-0.0        | ⚠️         |
| ORB (9:30-10:00)       | 80-89%     | 16     | 12    | 4      | 0      | 75.0%     | $0.7         | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.2        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 28     | 3     | 25     | 0      | 10.7%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 49     | 0     | 28     | 21     | 0.0%      | $0.5         | 🔴          |
| Morning (10:00-12:00)  | 60-69%     | 88     | 14    | 48     | 26     | 22.6%     | $-0.0        | 🟢          |
| Morning (10:00-12:00)  | 70-79%     | 52     | 11    | 20     | 21     | 35.5%     | $-0.9        | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 26     | 12    | 7      | 7      | 63.2%     | $-0.1        | ⚠️         |
| Morning (10:00-12:00)  | 90-99%     | 2      | 1     | 0      | 1      | 100.0%    | $0.1         | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 30     | 0     | 16     | 14     | 0.0%      | $1.4         | 🔴          |
| Afternoon (12:00-16:00) | 50-59%     | 104    | 0     | 52     | 52     | 0.0%      | $0.4         | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 298    | 7     | 141    | 150    | 4.7%      | $-0.1        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 263    | 21    | 141    | 101    | 13.0%     | $-0.8        | 🔴          |
| Afternoon (12:00-16:00) | 80-89%     | 95     | 14    | 44     | 37     | 24.1%     | $-0.9        | 🟢          |
| Afternoon (12:00-16:00) | 90-99%     | 1      | 0     | 1      | 0      | 0.0%      | $-0.8        | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 5      | 0     | 5      | 0      | 0.0%      | $-0.7        | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 14     | 0     | 14     | 0      | 0.0%      | $-0.8        | ⚠️         |
| After-hours (16:00-20:00) | 80-89%     | 2      | 0     | 2      | 0      | 0.0%      | $-0.7        | ⚠️         |
| After-hours (16:00-20:00) | 90-99%     | 1      | 0     | 1      | 0      | 0.0%      | $-1.1        | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 2038  | 173   | 975    | 890    | 15.1%     | $-0.1    |
| SHORT        | 412   | 136   | 247    | 29     | 35.5%     | $0.0     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 217   | 32    | 185    | 0      | 14.7%     | $-0.8    |
| Long (30-60 min)       | 458   | 108   | 350    | 0      | 23.6%     | $-0.2    |
| Medium (5-15 min)      | 417   | 78    | 339    | 0      | 18.7%     | $-0.6    |
| Slow (15-30 min)       | 395   | 81    | 314    | 0      | 20.5%     | $-0.4    |
| Very Fast (<1 min)     | 44    | 10    | 34     | 0      | 22.7%     | $-0.6    |
| Very Long (>1h)        | 919   | 0     | 0      | 919    | 0.0%      | $0.5     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 20.2% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.48 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 919 time-outs): $-0.12
- 🎯 Best performance at 80-89% confidence (39.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 20-29% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.10) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 30-90m (avg P&L $0.25) — optimal time held is Time Held: 30-90m.
- ✅ Best signal generation window: ORB (9:30-10:00) (40.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (2145s / 35.7m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 38% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 813  |  **Win Rate:** 30.9%  |  **Avg P&L (resolved):** $-0.3  |  **Avg P&L (all):** $-0.1  |  **Avg Hold:** 805s (13.4m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 10    | 0     | 0      | 10     | 0.0%      | $0.0     | $-0.1    | -5.4%    |
| 30-39%         | 93    | 0     | 0      | 93     | 0.0%      | $0.0     | $-0.0    | -0.3%    |
| 40-49%         | 53    | 2     | 4      | 47     | 33.3%     | $0.0     | $-0.2    | -4.2%    |
| 50-59%         | 212   | 13    | 18     | 181    | 41.9%     | $0.0     | $-0.1    | -1.2%    |
| 60-69%         | 349   | 18    | 57     | 274    | 24.0%     | $0.0     | $0.0     | 2.2%     |
| 70-79%         | 87    | 13    | 24     | 50     | 35.1%     | $0.0     | $0.0     | 4.4%     |
| 80-89%         | 9     | 0     | 0      | 9      | 0.0%      | $0.0     | $0.1     | 16.0%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 473   | 38    | 59     | 376    | 39.2%     | $-0.0    |
| Trending (Up)        | 340   | 8     | 44     | 288    | 15.4%     | $-0.2    |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 813   | 46    | 103    | 664    | 30.9%     | $-0.1    |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: <30m        | 813   | 46    | 103    | 664    | 30.9%     | $-0.1    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| After-hours (16:00-20:00) | 35    | 0     | 0      | 35     | 0.0%      | $-0.1    | 🔴          |
| Afternoon (12:00-16:00) | 339   | 3     | 29     | 307    | 9.4%      | $-0.2    | 🔴          |
| Morning (10:00-12:00)  | 164   | 17    | 37     | 110    | 31.5%     | $-0.1    | 🟢          |
| ORB (9:30-10:00)       | 52    | 11    | 23     | 18     | 32.4%     | $-0.2    | 🟢          |
| Pre-market             | 223   | 15    | 14     | 194    | 51.7%     | $0.2     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 223    | 17         | 77         | 129        | 7.6%      | 34.5%     | 57.8%     |
| ORB (9:30-10:00)       | 52     | 11         | 34         | 7          | 21.2%     | 65.4%     | 13.5%     |
| Morning (10:00-12:00)  | 164    | 47         | 110        | 7          | 28.7%     | 67.1%     | 4.3%      |
| Afternoon (12:00-16:00) | 339    | 19         | 307        | 13         | 5.6%      | 90.6%     | 3.8%      |
| After-hours (16:00-20:00) | 35     | 2          | 33         | 0          | 5.7%      | 94.3%     | 0.0%      |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 10     | 0     | 0      | 10     | 0.0%      | $0.0         | ⚠️         |
| Pre-market             | 30-39%     | 93     | 0     | 0      | 93     | 0.0%      | $0.0         | 🔴          |
| Pre-market             | 40-49%     | 26     | 1     | 0      | 25     | 100.0%    | $7.5         | ⚠️         |
| Pre-market             | 50-59%     | 32     | 2     | 0      | 30     | 100.0%    | $9.8         | 🟢          |
| Pre-market             | 60-69%     | 45     | 7     | 8      | 30     | 46.7%     | $0.7         | 🟢          |
| Pre-market             | 70-79%     | 16     | 5     | 6      | 5      | 45.5%     | $0.2         | ⚠️         |
| Pre-market             | 80-89%     | 1      | 0     | 0      | 1      | 0.0%      | $0.0         | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 7      | 0     | 3      | 4      | 0.0%      | $-1.9        | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 19     | 2     | 5      | 12     | 28.6%     | $-0.6        | ⚠️         |
| ORB (9:30-10:00)       | 60-69%     | 15     | 5     | 8      | 2      | 38.5%     | $0.1         | ⚠️         |
| ORB (9:30-10:00)       | 70-79%     | 11     | 4     | 7      | 0      | 36.4%     | $-0.2        | ⚠️         |
| Morning (10:00-12:00)  | 40-49%     | 7      | 1     | 1      | 5      | 50.0%     | $-5.1        | ⚠️         |
| Morning (10:00-12:00)  | 50-59%     | 45     | 7     | 7      | 31     | 50.0%     | $0.2         | 🟢          |
| Morning (10:00-12:00)  | 60-69%     | 65     | 5     | 22     | 38     | 18.5%     | $-0.5        | 🔴          |
| Morning (10:00-12:00)  | 70-79%     | 39     | 4     | 7      | 28     | 36.4%     | $-0.2        | 🟢          |
| Morning (10:00-12:00)  | 80-89%     | 8      | 0     | 0      | 8      | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 13     | 0     | 0      | 13     | 0.0%      | $0.0         | ⚠️         |
| Afternoon (12:00-16:00) | 50-59%     | 112    | 2     | 6      | 104    | 25.0%     | $-6.2        | 🔴          |
| Afternoon (12:00-16:00) | 60-69%     | 195    | 1     | 19     | 175    | 5.0%      | $-0.3        | 🔴          |
| Afternoon (12:00-16:00) | 70-79%     | 19     | 0     | 4      | 15     | 0.0%      | $-0.5        | ⚠️         |
| After-hours (16:00-20:00) | 50-59%     | 4      | 0     | 0      | 4      | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 60-69%     | 29     | 0     | 0      | 29     | 0.0%      | $0.0         | ⚠️         |
| After-hours (16:00-20:00) | 70-79%     | 2      | 0     | 0      | 2      | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 411   | 15    | 51     | 345    | 22.7%     | $-0.2    |
| SHORT        | 402   | 31    | 52     | 319    | 37.3%     | $0.0     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 53    | 14    | 39     | 0      | 26.4%     | $-0.3    |
| Medium (5-15 min)      | 88    | 31    | 57     | 0      | 35.2%     | $-0.3    |
| Slow (15-30 min)       | 664   | 0     | 0      | 664    | 0.0%      | $-0.0    |
| Very Fast (<1 min)     | 8     | 1     | 7      | 0      | 12.5%     | $-0.7    |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.9% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.32 — losses outweigh wins. Review stop-loss placement and entry timing.
- 📉 Avg P&L per signal (incl. 664 time-outs): $-0.08
- 🎯 Best performance at 50-59% confidence (41.9% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 30-39% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $-0.02) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: Time Held: <30m (avg P&L $-0.08) — optimal time held is Time Held: <30m.
- ✅ Best signal generation window: Pre-market (51.7% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (805s / 13.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 82% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AAPL, AMD, INTC, NVDA, TSLA  |  **Total Signals:** 724  |  **Win Rate:** 38.1%  |  **Avg P&L (resolved):** $-0.2  |  **Avg P&L (all):** $0.2  |  **Avg Hold:** 5371s (89.5m)  |  **Median Hold:** 7200s

#### 1) Performance by Confidence Level

| Confidence     | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Avg P&L (all) | Avg P&L% |
+----------------+-------+-------+--------+--------+-----------+----------+----------+----------+
| 20-29%         | 175   | 11    | 36     | 128    | 23.4%     | $0.0     | $0.3     | 8.7%     |
| 30-39%         | 191   | 35    | 48     | 108    | 42.2%     | $0.0     | $0.2     | 5.8%     |
| 40-49%         | 159   | 42    | 47     | 70     | 47.2%     | $0.0     | $0.5     | 17.1%    |
| 50-59%         | 107   | 15    | 22     | 70     | 40.5%     | $0.0     | $0.1     | 5.0%     |
| 60-69%         | 66    | 7     | 21     | 38     | 25.0%     | $0.0     | $0.3     | 15.6%    |
| 70-79%         | 26    | 0     | 5      | 21     | 0.0%      | $0.0     | $-0.1    | -7.4%    |

#### 2) Performance by Market Type

| Market Type          | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Sideways             | 453   | 62    | 116    | 275    | 34.8%     | $0.0     |
| Trending (Up)        | 271   | 48    | 63     | 160    | 43.2%     | $0.5     |

**Regime Performance:**

| Regime               | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+----------------------+-------+-------+--------+--------+-----------+----------+
| Positive Gamma (Range-Bound friendly) | 724   | 110   | 179    | 435    | 38.1%     | $0.2     |

#### 3) Performance by Timeframe (Time Held — Broad)

*Broad buckets covering major session windows.*

| Time Held              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Time Held: 30-90m      | 105   | 33    | 72     | 0      | 31.4%     | $-0.6    |
| Time Held: 90-240m     | 486   | 37    | 14     | 435    | 72.5%     | $0.6     |
| Time Held: <30m        | 133   | 40    | 93     | 0      | 30.1%     | $-0.7    |

#### 3b) Signal Generation Time

| Time Window            | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  | Significance |
+------------------------+-------+-------+--------+--------+-----------+----------+------------+
| Afternoon (12:00-16:00) | 195   | 28    | 30     | 137    | 48.3%     | $0.2     | 🟢          |
| Morning (10:00-12:00)  | 136   | 17    | 59     | 60     | 22.4%     | $-0.3    | 🔴          |
| ORB (9:30-10:00)       | 30    | 4     | 14     | 12     | 22.2%     | $-0.3    | 🔴          |
| Pre-market             | 363   | 61    | 76     | 226    | 44.5%     | $0.4     | 🟢          |

#### 3c) Confidence Distribution by Session

*Percentage of signals by confidence tier within each US equity session window.*

| Session                | Total  | High (70%+) | Medium (50-69%) | Low (<50%) | High %    | Medium %  | Low %     |
+------------------------+--------+------------+------------+------------+-----------+-----------+-----------+
| Pre-market             | 363    | 0          | 29         | 334        | 0.0%      | 8.0%      | 92.0%     |
| ORB (9:30-10:00)       | 30     | 0          | 8          | 22         | 0.0%      | 26.7%     | 73.3%     |
| Morning (10:00-12:00)  | 136    | 7          | 46         | 83         | 5.1%      | 33.8%     | 61.0%     |
| Afternoon (12:00-16:00) | 195    | 19         | 90         | 86         | 9.7%      | 46.2%     | 44.1%     |

#### 3d) Session × Confidence Cross-Tabulation

*Win rate and avg P&L for each strategy, broken down by both trading session and confidence level simultaneously.*

| Session                | Confidence | Total  | Wins  | Losses | Closed | Win Rate  | Avg P&L (resolved) | Significance |
+------------------------+------------+--------+-------+--------+--------+-----------+--------------+------------+
| Pre-market             | 20-29%     | 147    | 10    | 17     | 120    | 37.0%     | $0.9         | 🔴          |
| Pre-market             | 30-39%     | 130    | 28    | 13     | 89     | 68.3%     | $2.1         | 🟢          |
| Pre-market             | 40-49%     | 57     | 20    | 22     | 15     | 47.6%     | $1.2         | 🟢          |
| Pre-market             | 50-59%     | 19     | 3     | 14     | 2      | 17.6%     | $-0.4        | ⚠️         |
| Pre-market             | 60-69%     | 10     | 0     | 10     | 0      | 0.0%      | $-1.2        | ⚠️         |
| ORB (9:30-10:00)       | 20-29%     | 3      | 0     | 3      | 0      | 0.0%      | $-2.6        | ⚠️         |
| ORB (9:30-10:00)       | 30-39%     | 8      | 0     | 8      | 0      | 0.0%      | $-2.4        | ⚠️         |
| ORB (9:30-10:00)       | 40-49%     | 11     | 4     | 3      | 4      | 57.1%     | $2.0         | ⚠️         |
| ORB (9:30-10:00)       | 50-59%     | 8      | 0     | 0      | 8      | 0.0%      | $0.0         | ⚠️         |
| Morning (10:00-12:00)  | 20-29%     | 12     | 1     | 8      | 3      | 11.1%     | $-1.7        | ⚠️         |
| Morning (10:00-12:00)  | 30-39%     | 30     | 6     | 17     | 7      | 26.1%     | $-1.0        | 🔴          |
| Morning (10:00-12:00)  | 40-49%     | 41     | 5     | 13     | 23     | 27.8%     | $0.0         | 🔴          |
| Morning (10:00-12:00)  | 50-59%     | 29     | 5     | 8      | 16     | 38.5%     | $0.6         | ⚠️         |
| Morning (10:00-12:00)  | 60-69%     | 17     | 0     | 8      | 9      | 0.0%      | $-0.4        | ⚠️         |
| Morning (10:00-12:00)  | 70-79%     | 7      | 0     | 5      | 2      | 0.0%      | $-1.3        | ⚠️         |
| Afternoon (12:00-16:00) | 20-29%     | 13     | 0     | 8      | 5      | 0.0%      | $-2.5        | ⚠️         |
| Afternoon (12:00-16:00) | 30-39%     | 23     | 1     | 10     | 12     | 9.1%      | $-0.3        | ⚠️         |
| Afternoon (12:00-16:00) | 40-49%     | 50     | 13    | 9      | 28     | 59.1%     | $1.5         | 🟢          |
| Afternoon (12:00-16:00) | 50-59%     | 51     | 7     | 0      | 44     | 100.0%    | $1.8         | 🟢          |
| Afternoon (12:00-16:00) | 60-69%     | 39     | 7     | 3      | 29     | 70.0%     | $3.0         | 🟢          |
| Afternoon (12:00-16:00) | 70-79%     | 19     | 0     | 0      | 19     | 0.0%      | $0.0         | ⚠️         |

#### 4) Performance by Direction

| Direction    | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+--------------+-------+-------+--------+--------+-----------+----------+
| LONG         | 447   | 59    | 115    | 273    | 33.9%     | $-0.1    |
| SHORT        | 277   | 51    | 64     | 162    | 44.3%     | $0.6     |

#### 5) Hold Time Distribution (Fine-Grained)

*Fine-grained buckets covering detailed hold durations.*

| Hold Time              | Total | Wins  | Losses | Closed | Win Rate  | Avg P&L  |
+------------------------+-------+-------+--------+--------+-----------+----------+
| Fast (1-5 min)         | 17    | 4     | 13     | 0      | 23.5%     | $-0.6    |
| Long (30-60 min)       | 72    | 18    | 54     | 0      | 25.0%     | $-0.9    |
| Medium (5-15 min)      | 59    | 20    | 39     | 0      | 33.9%     | $-0.7    |
| Slow (15-30 min)       | 56    | 15    | 41     | 0      | 26.8%     | $-0.7    |
| Very Fast (<1 min)     | 1     | 1     | 0      | 0      | 100.0%    | $3.9     |
| Very Long (>1h)        | 519   | 52    | 32     | 435    | 61.9%     | $0.6     |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 38.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L per resolved signal: $-0.15 — losses outweigh wins. Review stop-loss placement and entry timing.
- 💰 Avg P&L per signal (incl. 435 time-outs): $0.20
- 🎯 Best performance at 40-49% confidence (47.2% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (0.0% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.48) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Time Held: 90-240m (avg P&L $0.60) — optimal time held is Time Held: 90-240m.
- ✅ Best signal generation window: Afternoon (12:00-16:00) (48.3% win rate) — statistically significant above overall WR.
- ⏱️ Long avg hold time (5371s / 89.5m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 60% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

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
| 1779892073.559 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration, vol_compression_range | 11           | Strike bounce SHORT: 312.5 Call strike, rank #1... |
| 1779897477.456 | 19     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 11           | Confluence SHORT at 445: 2 structural signals, ... |
| 1779902863.076 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 11           | Magnet pull LONG: price 494.25 below magnet 500... |
| 1779905650.393 | 18     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 11           | Breakout SHORT below flip zone 442.50, price=44... |
| 1779880248.325 | 17     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Flow imbalance SHORT: AggVSI=-0.352 (+35.2%), R... |
| 1779880763.98  | 11     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 10           | Exchange flow LONG: VSI=3.39 (+239.1%), ROC=+0.... |
| 1779885351.781 | 10     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Range LONG: price near lower edge, wall at 510,... |
| 1779888461.039 | 18     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Exchange flow LONG: VSI=2.09 (+108.7%), ROC=+0.... |
| 1779888746.15  | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 10           | BATS sweep SHORT: ESI=-1.000 (+100.0%), dev=-1.... |
| 1779890032.158 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Squeeze LONG: breakout through call wall at 500... |
| 1779890166.504 | 13     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 10           | BATS sweep SHORT: ESI=-0.862 (+86.2%), dev=-0.8... |
| 1779891950.398 | 15     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 10           | GEX divergence (bullish): price falling but GEX... |
| 1779892256.158 | 19     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 10           | Strike bounce LONG: 310.0 Put strike, rank #3, ... |
| 1779893203.932 | 13     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, vol_compression_range | 10           | Range SHORT: price near upper edge, call wall a... |
| 1779895167.132 | 22     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 10           | GEX divergence (bullish): price falling but GEX... |
| 1779899290.235 | 20     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 10           | Confluence LONG at 119: 1 structural signals, t... |
| 1779899838.74  | 17     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 10           | Magnet pull LONG: price 210.79 below magnet 215... |
| 1779900080.779 | 19     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Call wall at 312.5 rejected price, GEX=19978246... |
| 1779900362.78  | 13     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, gex_divergence, magnet_accelerate, strike_concentration | 10           | Magnet pull LONG: price 441.15 below magnet 445... |
| 1779900739.911 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 10           | Depth imbalance SHORT: IR=0.53 (+47.4%), ROC=-0... |
| 1779902929.793 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 10           | Fade LONG above flip zone 310.00, price=310.56,... |
| 1779903410.422 | 16     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Exchange flow LONG: VSI=2.89 (+188.9%), ROC=+0.... |
| 1779907561.258 | 12     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, strike_concentration, vol_compression_range | 10           | Breakout LONG below flip zone 440.00, price=439... |
| 1779908652.52  | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, strike_concentration | 10           | Depth decay SHORT: ROC=-0.2313 (-23.13%), vol/d... |
| 1779876264.037 | 12     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Range SHORT: price near upper edge, call wall a... |
| 1779880308.524 | 14     | confluence_reversal, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Flow imbalance SHORT: AggVSI=-0.800 (+80.0%), R... |
| 1779888611.578 | 12     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.2036 (-20.36%), vol/d... |
| 1779889044.05  | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gex_divergence, strike_concentration | 9            | Exchange flow LONG: VSI=4.62 (+361.5%), ROC=+0.... |
| 1779889476.057 | 15     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, vol_compression_range | 9            | Exchange flow LONG: VSI=9.60 (+860.0%), ROC=+4.... |
| 1779889844.307 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, strike_concentration, vol_compression_range | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779889982.034 | 12     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Magnet pull SHORT: price 501.52 above magnet 50... |
| 1779890717.07  | 14     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration, vol_compression_range | 9            | Magnet pull LONG: price 440.34 below magnet 445... |
| 1779891503.668 | 11     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.2073 (-20.73%), vol/d... |
| 1779891701.7   | 11     | depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 9            | Depth decay SHORT: ROC=-0.4772 (-47.72%), vol/d... |
| 1779891808.786 | 9      | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Magnet pull LONG: price 437.62 below magnet 445... |
| 1779892128.821 | 13     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | GEX divergence (bullish): price falling but GEX... |
| 1779892194.594 | 13     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Strike bounce LONG: 310.0 Put strike, rank #3, ... |
| 1779893812.488 | 14     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, strike_concentration | 9            | Breakout SHORT below flip zone 312.50, price=31... |
| 1779893936.489 | 13     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Depth imbalance SHORT: IR=0.29 (+70.7%), ROC=-0... |
| 1779894235.425 | 10     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, magnet_accelerate, vol_compression_range | 9            | Range SHORT: price near upper edge, call wall a... |
| 1779895775.211 | 18     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, vol_compression_range | 9            | Fade SHORT above flip zone 490.00, price=490.35... |
| 1779896506.039 | 20     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, magnet_accelerate | 9            | Call wall at 312.5 rejected price, GEX=18340693... |
| 1779897106.981 | 16     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Confluence SHORT at 492: 2 structural signals, ... |
| 1779897167.335 | 15     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, gamma_flip_breakout, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, strike_concentration | 9            | Confluence LONG at 485: 2 structural signals, t... |
| 1779897182.35  | 12     | confluence_reversal, depth_decay_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gex_divergence, magnet_accelerate, vol_compression_range | 9            | BATS sweep SHORT: ESI=-0.807 (+80.7%), dev=-0.8... |
| 1779897589.797 | 16     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_wall_bounce, vol_compression_range | 9            | Exchange flow SHORT: VSI=0.00 (+100.0%), ROC=-1... |
| 1779899231.505 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration | 9            | Depth imbalance LONG: IR=10.72 (+971.6%), ROC=+... |
| 1779899415.355 | 14     | confluence_reversal, depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, gamma_flip_breakout, gamma_wall_bounce, gex_divergence, strike_concentration, vol_compression_range | 9            | Put wall at 310.0 supported price, GEX=5229281,... |
| 1779899690.963 | 13     | depth_decay_momentum, depth_imbalance_momentum, exchange_flow_asymmetry, exchange_flow_concentration, exchange_flow_imbalance, gamma_flip_breakout, gamma_squeeze, magnet_accelerate, vol_compression_range | 9            | Range LONG: price near lower edge, wall at 210,... |
| 1779899950.032 | 16     | confluence_reversal, depth_decay_momentum, exchange_flow_concentration, exchange_flow_imbalance, gamma_squeeze, gamma_wall_bounce, gex_divergence, magnet_accelerate, vol_compression_range | 9            | Flow imbalance SHORT: AggVSI=-0.796 (+79.6%), R... |

**3654 total burst(s) detected.** Top 50 shown above.

---

## Microstructure Event Clusters (Phase 3)

Signals grouped by shared metadata fingerprints, not strategy names.
When independent strategies fire on the same microstructure condition,
they form an **Event Cluster** — a signal that the market is reacting to
a specific structural event, regardless of which strategy detected it.

### Event Type Summary

| Event Type                   | Signals  | Strategies | Common Trigger         | Win Rate | Avg P&L    |
+------------------------------+----------+------------+------------------------+----------+------------+
| Gamma Exposure               | 14,756   | 8          | net_gamma=< 16741120.  | 27.5%    | $-0.0      |
| Gamma Wall Support (310.0)   | 867      | 4          | wall_strike=310.0      | 27.8%    | $-0.1      |
| Gamma Wall Support (437.5)   | 769      | 4          | wall_strike=437.5      | 31.0%    | $0.2       |
| Gamma Wall Support (217.5)   | 132      | 3          | wall_strike=217.5      | 12.9%    | $-0.3      |
| Gamma Wall Support (125.0)   | 81       | 4          | wall_strike=125.0      | 47.6%    | $-0.0      |
| Gamma Wall Support (510.0)   | 68       | 3          | wall_strike=510.0      | 17.4%    | $-0.1      |
| Exchange Sweep (0.1)         | 4        | 2          | iex_intent=0.1         | 0.0%     | $-0.4      |

### Top Event Clusters

Top 20 clusters sorted by coincidence score (unique strategy count).
Each cluster represents signals from different strategies triggered by the same
microstructure condition — evidence of a real market event.

| Event Type     | Signals | Strats | Score    | Win Rate | Avg P&L    | Trigger    | Strategy List                            |
+----------------+--------+--------+----------+----------+------------+------------+------------------------------------------+
| Gamma Exposur  | 3430   | 5      | 5        | 27.8%    | $-0.1      | net_gamma  | delta_gamma_squeeze, gamma_flip_breakou  |
| Gamma Exposur  | 6374   | 5      | 5        | 24.8%    | $-0.0      | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 81     | 4      | 4        | 47.6%    | $-0.0      | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Wall Su  | 769    | 4      | 4        | 31.0%    | $0.2       | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Exposur  | 3431   | 4      | 4        | 29.5%    | $-0.0      | net_gamma  | gamma_flip_breakout, gamma_squeeze, mag  |
| Gamma Wall Su  | 867    | 4      | 4        | 27.8%    | $-0.1      | wall_stri  | delta_gamma_squeeze, gamma_squeeze, gam  |
| Gamma Exposur  | 1521   | 3      | 3        | 24.0%    | $0.3       | wall_gex=  | confluence_reversal, delta_gamma_squeez  |
| Gamma Wall Su  | 68     | 3      | 3        | 17.4%    | $-0.1      | wall_stri  | gamma_squeeze, gamma_wall_bounce, vol_c  |
| Gamma Wall Su  | 132    | 3      | 3        | 12.9%    | $-0.3      | wall_stri  | delta_gamma_squeeze, gamma_squeeze, vol  |
| Exchange Swee  | 4      | 2      | 2        | 0.0%     | $-0.4      | iex_inten  | exchange_flow_concentration, exchange_f  |

**10 event cluster(s) detected.** Clusters with higher coincidence scores
represent stronger evidence of structural market events.

---

### Global Baseline Win Rates by Confidence Bucket

| Bucket         | Total    | Wins   | Losses | Closed | Win Rate  | StdDev    |
+----------------+----------+--------+--------+--------+-----------+-----------+
| 10-19%         | 60       | 1      | 2      | 57     | 33.3%     | 23.6      |
| 20-29%         | 2680     | 126    | 531    | 2023   | 19.2%     | 17.0      |
| 30-39%         | 3293     | 213    | 389    | 2691   | 35.4%     | 32.0      |
| 40-49%         | 3415     | 308    | 584    | 2523   | 34.5%     | 19.5      |
| 50-59%         | 4546     | 386    | 972    | 3188   | 28.4%     | 15.1      |
| 60-69%         | 4830     | 616    | 1391   | 2823   | 30.7%     | 13.7      |
| 70-79%         | 3768     | 534    | 1250   | 1984   | 29.9%     | 16.1      |
| 80-89%         | 3375     | 382    | 1044   | 1949   | 26.8%     | 29.6      |
| 90-99%         | 233      | 35     | 129    | 69     | 21.3%     | 38.9      |
| 100%           | 182      | 3      | 9      | 170    | 25.0%     | 0.0       |

### Global Baseline by Session

*Aggregated across all strategies. StdDev = sample stddev of per-strategy win rates within each session.*

| Session                | Total    | Wins   | Losses | Closed | Win Rate  | StdDev   |
+------------------------+----------+--------+--------+--------+-----------+----------+
| Pre-market             | 10368    | 1156   | 2418   | 6794   | 32.3%     | 16.1     |
| ORB (9:30-10:00)       | 1357     | 283    | 636    | 438    | 30.8%     | 22.0     |
| Morning (10:00-12:00)  | 4895     | 635    | 1532   | 2728   | 29.3%     | 10.7     |
| Afternoon (12:00-16:00) | 9480     | 511    | 1661   | 7308   | 23.5%     | 16.7     |
| After-hours (16:00-20:00) | 285      | 19     | 54     | 212    | 26.0%     | 14.4     |

### Global Baseline by Session × Confidence

*Aggregated across all strategies. Only cells with ≥ 10 total signals shown.*

| Session                | Confidence   | Total    | Wins   | Losses | Closed | Win Rate  |
+------------------------+--------------+----------+--------+--------+--------+-----------+
| Pre-market             | 10-19%       | 45       | 0      | 0      | 45     | 0.0%      |
| Pre-market             | 20-29%       | 1621     | 64     | 275    | 1282   | 18.9%     |
| Pre-market             | 30-39%       | 1567     | 121    | 177    | 1269   | 40.6%     |
| Pre-market             | 40-49%       | 1284     | 164    | 243    | 877    | 40.3%     |
| Pre-market             | 50-59%       | 1922     | 210    | 451    | 1261   | 31.8%     |
| Pre-market             | 60-69%       | 1697     | 248    | 485    | 964    | 33.8%     |
| Pre-market             | 70-79%       | 1239     | 212    | 427    | 600    | 33.2%     |
| Pre-market             | 80-89%       | 932      | 126    | 317    | 489    | 28.4%     |
| Pre-market             | 90-99%       | 58       | 11     | 43     | 4      | 20.4%     |
| ORB (9:30-10:00)       | 20-29%       | 85       | 15     | 30     | 40     | 33.3%     |
| ORB (9:30-10:00)       | 30-39%       | 156      | 24     | 45     | 87     | 34.8%     |
| ORB (9:30-10:00)       | 40-49%       | 183      | 22     | 75     | 86     | 22.7%     |
| ORB (9:30-10:00)       | 50-59%       | 237      | 34     | 91     | 112    | 27.2%     |
| ORB (9:30-10:00)       | 60-69%       | 234      | 72     | 131    | 31     | 35.5%     |
| ORB (9:30-10:00)       | 70-79%       | 213      | 65     | 117    | 31     | 35.7%     |
| ORB (9:30-10:00)       | 80-89%       | 233      | 50     | 139    | 44     | 26.5%     |
| ORB (9:30-10:00)       | 90-99%       | 11       | 0      | 8      | 3      | 0.0%      |
| Morning (10:00-12:00)  | 20-29%       | 382      | 31     | 124    | 227    | 20.0%     |
| Morning (10:00-12:00)  | 30-39%       | 586      | 38     | 110    | 438    | 25.7%     |
| Morning (10:00-12:00)  | 40-49%       | 679      | 59     | 145    | 475    | 28.9%     |
| Morning (10:00-12:00)  | 50-59%       | 770      | 97     | 241    | 432    | 28.7%     |
| Morning (10:00-12:00)  | 60-69%       | 840      | 142    | 335    | 363    | 29.8%     |
| Morning (10:00-12:00)  | 70-79%       | 769      | 145    | 301    | 323    | 32.5%     |
| Morning (10:00-12:00)  | 80-89%       | 753      | 115    | 253    | 385    | 31.2%     |
| Morning (10:00-12:00)  | 90-99%       | 22       | 6      | 14     | 2      | 30.0%     |
| Morning (10:00-12:00)  | 100%         | 92       | 2      | 9      | 81     | 18.2%     |
| Afternoon (12:00-16:00) | 10-19%       | 13       | 1      | 2      | 10     | 33.3%     |
| Afternoon (12:00-16:00) | 20-29%       | 592      | 16     | 102    | 474    | 13.6%     |
| Afternoon (12:00-16:00) | 30-39%       | 973      | 30     | 57     | 886    | 34.5%     |
| Afternoon (12:00-16:00) | 40-49%       | 1250     | 63     | 121    | 1066   | 34.2%     |
| Afternoon (12:00-16:00) | 50-59%       | 1585     | 44     | 189    | 1352   | 18.9%     |
| Afternoon (12:00-16:00) | 60-69%       | 1942     | 144    | 434    | 1364   | 24.9%     |
| Afternoon (12:00-16:00) | 70-79%       | 1510     | 112    | 387    | 1011   | 22.4%     |
| Afternoon (12:00-16:00) | 80-89%       | 1429     | 91     | 324    | 1014   | 21.9%     |
| Afternoon (12:00-16:00) | 90-99%       | 110      | 10     | 45     | 55     | 18.2%     |
| Afternoon (12:00-16:00) | 100%         | 76       | 0      | 0      | 76     | 0.0%      |
| After-hours (16:00-20:00) | 30-39%       | 11       | 0      | 0      | 11     | 0.0%      |
| After-hours (16:00-20:00) | 40-49%       | 19       | 0      | 0      | 19     | 0.0%      |
| After-hours (16:00-20:00) | 50-59%       | 32       | 1      | 0      | 31     | 100.0%    |
| After-hours (16:00-20:00) | 60-69%       | 117      | 10     | 6      | 101    | 62.5%     |
| After-hours (16:00-20:00) | 70-79%       | 37       | 0      | 18     | 19     | 0.0%      |
| After-hours (16:00-20:00) | 80-89%       | 28       | 0      | 11     | 17     | 0.0%      |
| After-hours (16:00-20:00) | 90-99%       | 32       | 8      | 19     | 5      | 29.6%     |

### Detected Anomalies

| Strategy                 | Bucket       | Strat WR  | Global WR | Lift     | Sigma    | Total    | Wins     | Losses   |
+--------------------------+--------------+-----------+-----------+----------+----------+----------+----------+----------+
| [ALPHA] gamma_wall_bounce | 90-99%       | 100.0%    | 21.3%     | 369%     | 2.02     | 39       | 1        | 0        |
| [ALPHA] gamma_wall_bounce | 80-89%       | 100.0%    | 26.8%     | 273%     | 2.47     | 114      | 6        | 0        |
| [ALPHA] gamma_wall_bounce | 30-39%       | 100.0%    | 35.4%     | 183%     | 2.02     | 27       | 1        | 0        |
| [ALPHA] exchange_flow_concentration | 20-29%       | 45.0%     | 19.2%     | 135%     | 1.52     | 78       | 9        | 11       |
| [ALPHA] gamma_flip_breakout | 30-39%       | 63.3%     | 35.4%     | 79%      | 0.87     | 343      | 69       | 40       |
| [ALPHA] gamma_flip_breakout | 50-59%       | 50.0%     | 28.4%     | 76%      | 1.43     | 463      | 115      | 115      |
| [ALPHA] gex_divergence   | 40-49%       | 60.0%     | 34.5%     | 74%      | 1.31     | 85       | 24       | 16       |
| [ALPHA] gex_divergence   | 70-79%       | 51.7%     | 29.9%     | 73%      | 1.35     | 106      | 46       | 43       |

**8 anomaly(ies) detected.** These represent potential micro-edges worth investigating.

---

## Session × Confidence Anomalies

Cross-tab analysis: how each strategy performs in specific session×confidence combos
compared to the global baseline for that same combo. Flags combos where a strategy
shows a significant lift (>50% above global) or >1.5σ deviation.

| Strategy                 | Session      | Confidence   | Total   | Wins   | Losses | Strat WR | Global WR | Lift   | Sigma   | Significance |
+--------------------------+--------------+--------------+---------+--------+--------+----------+----------+--------+---------+--------------+
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 50-59%       | 51      | 7      | 0      | 100.0%   | 18.9%    | 430%   | 2.64    | ⚡ HIGH       |
| [ALPHA] gamma_wall_bounce | Afternoon (12:00-16:00) | 80-89%       | 108     | 4      | 0      | 100.0%   | 21.9%    | 356%   | 2.21    | ⚡ HIGH       |
| [ALPHA] confluence_reversal | ORB (9:30-10:00) | 50-59%       | 18      | 2      | 0      | 100.0%   | 27.2%    | 268%   | 2.48    | ⚡ HIGH       |
| [ALPHA] gex_divergence   | Morning (10:00-12:00) | 40-49%       | 7       | 1      | 0      | 100.0%   | 28.9%    | 246%   | 2.41    | ⚡ HIGH       |
| [ALPHA] exchange_flow_concentration | Morning (10:00-12:00) | 20-29%       | 16      | 2      | 1      | 66.7%    | 20.0%    | 233%   | 1.59    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Pre-market   | 50-59%       | 32      | 2      | 0      | 100.0%   | 31.8%    | 215%   | 2.43    | ⚡ HIGH       |
| [ALPHA] exchange_flow_concentration | Afternoon (12:00-16:00) | 20-29%       | 61      | 7      | 10     | 41.2%    | 13.6%    | 204%   | 1.42    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 70-79%       | 41      | 20     | 10     | 66.7%    | 22.4%    | 197%   | 2.15    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 30-39%       | 111     | 13     | 0      | 100.0%   | 34.5%    | 190%   | 1.78    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 80-89%       | 16      | 12     | 4      | 75.0%    | 26.5%    | 184%   | 1.92    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 60-69%       | 39      | 7      | 3      | 70.0%    | 24.9%    | 181%   | 2.06    | ⚡ HIGH       |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 30-39%       | 56      | 17     | 7      | 70.8%    | 25.7%    | 176%   | 1.68    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | ORB (9:30-10:00) | 40-49%       | 11      | 4      | 3      | 57.1%    | 22.7%    | 152%   | 1.69    | 🔥 STRONG     |
| [ALPHA] strike_concentration | Pre-market   | 40-49%       | 26      | 1      | 0      | 100.0%   | 40.3%    | 148%   | 1.87    | 🔥 STRONG     |
| [ALPHA] gamma_wall_bounce | Pre-market   | 30-39%       | 22      | 1      | 0      | 100.0%   | 40.6%    | 146%   | 1.68    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 50-59%       | 149     | 18     | 22     | 45.0%    | 18.9%    | 138%   | 0.85    | 🔥 STRONG     |
| [ALPHA] gex_divergence   | Pre-market   | 40-49%       | 53      | 23     | 3      | 88.5%    | 40.3%    | 120%   | 1.51    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Pre-market   | 50-59%       | 155     | 52     | 27     | 65.8%    | 31.8%    | 107%   | 1.21    | 🔥 STRONG     |
| [ALPHA] magnet_accelerate | Morning (10:00-12:00) | 80-89%       | 26      | 12     | 7      | 63.2%    | 31.2%    | 102%   | 1.54    | 🔥 STRONG     |
| [ALPHA] gamma_flip_breakout | Afternoon (12:00-16:00) | 40-49%       | 185     | 22     | 10     | 68.8%    | 34.2%    | 101%   | 1.22    | 🔥 STRONG     |
| [ALPHA] vol_compression_range | Pre-market   | 20-29%       | 147     | 10     | 17     | 37.0%    | 18.9%    | 96%    | 1.18    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Afternoon (12:00-16:00) | 80-89%       | 260     | 27     | 36     | 42.9%    | 21.9%    | 95%    | 0.59    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 50-59%       | 45      | 7      | 7      | 50.0%    | 28.7%    | 74%    | 1.03    | ⚠ MODERATE   |
| [ALPHA] strike_concentration | Morning (10:00-12:00) | 40-49%       | 7       | 1      | 1      | 50.0%    | 28.9%    | 73%    | 0.71    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Afternoon (12:00-16:00) | 40-49%       | 50      | 13     | 9      | 59.1%    | 34.2%    | 73%    | 0.88    | ⚠ MODERATE   |
| [ALPHA] magnet_accelerate | ORB (9:30-10:00) | 70-79%       | 26      | 16     | 10     | 61.5%    | 35.7%    | 72%    | 2.02    | ⚡ HIGH       |
| [ALPHA] gex_divergence   | Afternoon (12:00-16:00) | 60-69%       | 375     | 77     | 103    | 42.8%    | 24.9%    | 72%    | 0.81    | ⚠ MODERATE   |
| [ALPHA] vol_compression_range | Pre-market   | 30-39%       | 130     | 28     | 13     | 68.3%    | 40.6%    | 68%    | 0.78    | ⚠ MODERATE   |
| [ALPHA] depth_decay_momentum | Pre-market   | 90-99%       | 6       | 1      | 2      | 33.3%    | 20.4%    | 64%    | 0.77    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | ORB (9:30-10:00) | 40-49%       | 40      | 11     | 19     | 36.7%    | 22.7%    | 62%    | 0.69    | ⚠ MODERATE   |
| [ALPHA] depth_imbalance_momentum | ORB (9:30-10:00) | 50-59%       | 52      | 7      | 9      | 43.8%    | 27.2%    | 61%    | 0.56    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | After-hours (16:00-20:00) | 60-69%       | 10      | 10     | 0      | 100.0%   | 62.5%    | 60%    | 0.84    | ⚠ MODERATE   |
| [ALPHA] exchange_flow_imbalance | ORB (9:30-10:00) | 50-59%       | 11      | 3      | 4      | 42.9%    | 27.2%    | 58%    | 0.53    | ⚠ MODERATE   |
| [ALPHA] gamma_flip_breakout | Morning (10:00-12:00) | 50-59%       | 122     | 36     | 45     | 44.4%    | 28.7%    | 55%    | 0.76    | ⚠ MODERATE   |
| [ALPHA] gex_divergence   | Morning (10:00-12:00) | 80-89%       | 23      | 11     | 12     | 47.8%    | 31.2%    | 53%    | 0.80    | ⚠ MODERATE   |

**35 session×confidence anomaly(ies) detected.** These represent strategy-specific edges that are active in particular sessions and confidence levels — useful for time-aware strategy tuning.

---

## Cross-Strategy Rankings

| Rank  | Strategy                 | Signals | Win Rate | Avg P&L  | Best Confidence | Best Session     | Best Session×Conf      | Best Market    | Best Timeframe |
+-------+--------------------------+---------+----------+----------+----------------+------------------+------------------------+----------------+----------------+
| 1     | delta_gamma_squeeze      | 125     | 0.0%     | $0.4     | 20-29%         | Pre-market       | Pre-market @ 20-29%    | Sideways       | Time Held: 30-90m |
| 2     | vol_compression_range    | 724     | 38.1%    | $0.2     | 40-49%         | Afternoon (12:00-16:00) | Afternoon (12:00-16:00) @ 50-59% | Trending (Up)  | Time Held: 90-240m |
| 3     | exchange_flow_asymmetry  | 1,454   | 16.5%    | $0.1     | 80-89%         | Pre-market       | Pre-market @ 80-89%    | UNKNOWN        | Time Held: <30m |
| 4     | depth_imbalance_momentum | 1,920   | 27.4%    | $0.1     | 50-59%         | Morning (10:00-12:00) | ORB (9:30-10:00) @ 50-59% | UNKNOWN        | Time Held: <30m |
| 5     | gamma_wall_bounce        | 893     | 33.3%    | $0.1     | 80-89%         | ORB (9:30-10:00) | Pre-market @ 30-39%    | Trending (Up)  | Time Held: <30m |
| 6     | confluence_reversal      | 5,978   | 24.3%    | $0.0     | 60-69%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 50-59% | Sideways       | Time Held: 30-90m |
| 7     | exchange_flow_concentration | 2,386   | 37.2%    | $0.0     | 20-29%         | Pre-market       | Morning (10:00-12:00) @ 20-29% | UNKNOWN        | Time Held: <30m |
| 8     | depth_decay_momentum     | 2,533   | 33.6%    | $0.0     | 80-89%         | Morning (10:00-12:00) | Afternoon (12:00-16:00) @ 80-89% | UNKNOWN        | Time Held: <30m |
| 9     | gamma_flip_breakout      | 3,021   | 37.4%    | $-0.0    | 30-39%         | After-hours (16:00-20:00) | Afternoon (12:00-16:00) @ 30-39% | Trending (Up)  | Time Held: 30-90m |
| 10    | exchange_flow_imbalance  | 2,385   | 21.4%    | $-0.0    | 50-59%         | Morning (10:00-12:00) | Afternoon (12:00-16:00) @ 30-39% | UNKNOWN        | Time Held: 30-90m |
| 11    | gex_divergence           | 1,251   | 37.5%    | $-0.1    | 40-49%         | Pre-market       | Morning (10:00-12:00) @ 40-49% | Sideways       | Time Held: <30m |
| 12    | strike_concentration     | 813     | 30.9%    | $-0.1    | 50-59%         | Pre-market       | Pre-market @ 40-49%    | Sideways       | Time Held: <30m |
| 13    | gamma_squeeze            | 452     | 1.4%     | $-0.1    | 50-59%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 50-59% | Trending (Up)  | Time Held: <30m |
| 14    | magnet_accelerate        | 2,450   | 20.2%    | $-0.1    | 80-89%         | ORB (9:30-10:00) | ORB (9:30-10:00) @ 80-89% | Trending (Up)  | Time Held: 30-90m |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*