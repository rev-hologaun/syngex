Loading all signal outcomes...
Loaded 34,602 resolved signals
Analyzing strategies...
Found 9 unique strategies
Generating report...

✅ Report written to /home/hologaun/projects/syngex/log/strategy_analysis_report.md

================================================================================
# Strategy Performance Analysis — Round 3 Validation

**Date:** 2026-05-06  |  **Total Resolved Signals:** 34,602  |  **Strategies Analyzed:** 9

---

## 📊 Overall Summary

| Metric | Value |
|--------|-------|
| Total Resolved Signals | 34,602 |
| Total Wins | 7,988 |
| Total Losses | 7,725 |
| Time-Expired (CLOSED) | 18,889 |
| Overall Win Rate (excl. CLOSED) | 50.8% |
| Total P&L | $-402.86 |
| Avg P&L per Signal | $-0.01 |
| Symbols Traded | AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA, TSLL |

---

## 🔬 Per-Strategy Deep Dive

### confluence_reversal

**Symbols:** AMD, AMZN, INTC, META, NVDA, SPY, TSLA  |  **Total Signals:** 3,657  |  **Win Rate:** 20.6%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 3353s (55.9m)  |  **Median Hold:** 3600s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 60-69% | 302 | 10 | 59 | 233 | 14.5% | $0.4 | 1.6% |
| 70-79% | 2652 | 80 | 274 | 2298 | 22.6% | $-0.0 | -4.5% |
| 80-89% | 703 | 11 | 57 | 635 | 16.2% | $-0.0 | -3.7% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 918 | 21 | 101 | 796 | 17.2% | $-0.1 |
| Trending (Down) | 1400 | 24 | 117 | 1259 | 17.0% | $0.1 |
| Trending (Up) | 1339 | 56 | 172 | 1111 | 24.6% | $0.0 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 3657 | 101 | 390 | 3166 | 20.6% | $0.0 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 3368 | 31 | 171 | 3166 | 15.3% | $0.1 |
| ORB / Early (0-30 min) | 289 | 70 | 219 | 0 | 24.2% | $-0.9 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 3657 | 101 | 390 | 3166 | 20.6% | $0.0 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 10 | 0 | 10 | 0 | 0.0% | $-2.0 |
| Long (30-60 min) | 202 | 31 | 171 | 0 | 15.3% | $-1.1 |
| Medium (5-15 min) | 87 | 16 | 71 | 0 | 18.4% | $-1.2 |
| Slow (15-30 min) | 190 | 54 | 136 | 0 | 28.4% | $-0.8 |
| Very Fast (<1 min) | 2 | 0 | 2 | 0 | 0.0% | $-0.9 |
| Very Long (>1h) | 3166 | 0 | 0 | 3166 | 0.0% | $0.2 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 20.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.01 per signal — profitable even with 20.6% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (22.6% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (14.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Down) (avg P&L $0.08) — this strategy thrives in trending (down) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.09) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (3353s / 55.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 87% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_flip_breakout

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA  |  **Total Signals:** 5,430  |  **Win Rate:** 86.5%  |  **Avg P&L:** $0.1  |  **Avg Hold:** 1818s (30.3m)  |  **Median Hold:** 1340s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 60-69% | 700 | 406 | 120 | 174 | 77.2% | $0.0 | 7.7% |
| 70-79% | 563 | 320 | 104 | 139 | 75.5% | $-0.0 | -1.2% |
| 80-89% | 3149 | 1608 | 114 | 1427 | 93.4% | $0.1 | 2.2% |
| 90-100% | 1018 | 655 | 128 | 235 | 83.7% | $0.3 | 27.0% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 1124 | 587 | 62 | 475 | 90.4% | $0.2 |
| Trending (Down) | 2207 | 967 | 218 | 1022 | 81.6% | $0.1 |
| Trending (Up) | 2099 | 1435 | 186 | 478 | 88.5% | $0.1 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 5430 | 2989 | 466 | 1975 | 86.5% | $0.1 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 2485 | 439 | 71 | 1975 | 86.1% | $-0.1 |
| ORB / Early (0-30 min) | 2945 | 2550 | 395 | 0 | 86.6% | $0.3 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 2770 | 1185 | 155 | 1430 | 88.4% | $0.1 |
| SHORT | 2660 | 1804 | 311 | 545 | 85.3% | $0.1 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 750 | 664 | 86 | 0 | 88.5% | $0.4 |
| Long (30-60 min) | 510 | 439 | 71 | 0 | 86.1% | $0.5 |
| Medium (5-15 min) | 958 | 808 | 150 | 0 | 84.3% | $0.5 |
| Slow (15-30 min) | 619 | 461 | 158 | 0 | 74.5% | $0.1 |
| Very Fast (<1 min) | 618 | 617 | 1 | 0 | 99.8% | $0.3 |
| Very Long (>1h) | 1975 | 0 | 0 | 1975 | 0.0% | $-0.3 |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 86.5% — this strategy consistently picks directional moves.
- 💰 Positive avg P&L of $0.13 per signal — profitable even with 86.5% win rate (good risk/reward).
- 🎯 Best performance at 80-89% confidence (93.4% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (75.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.18) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $0.33) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1818s / 30.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 36% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_squeeze

**Symbols:** AMZN, INTC, META, NVDA, SOFI, SPY, TSLA, TSLL  |  **Total Signals:** 2,906  |  **Win Rate:** 46.6%  |  **Avg P&L:** $0.2  |  **Avg Hold:** 1763s (29.4m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 50-59% | 205 | 4 | 1 | 200 | 80.0% | $-0.4 | -9.4% |
| 60-69% | 2701 | 71 | 85 | 2545 | 45.5% | $0.2 | 5.3% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 491 | 14 | 9 | 468 | 60.9% | $0.2 |
| Trending (Down) | 1234 | 21 | 25 | 1188 | 45.7% | $0.2 |
| Trending (Up) | 1181 | 40 | 52 | 1089 | 43.5% | $0.1 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 2906 | 75 | 86 | 2745 | 46.6% | $0.2 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 2745 | 0 | 0 | 2745 | 0.0% | $0.1 |
| ORB / Early (0-30 min) | 161 | 75 | 86 | 0 | 46.6% | $1.3 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 2906 | 75 | 86 | 2745 | 46.6% | $0.2 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 8 | 0 | 8 | 0 | 0.0% | $-3.1 |
| Long (30-60 min) | 2745 | 0 | 0 | 2745 | 0.0% | $0.1 |
| Medium (5-15 min) | 36 | 18 | 18 | 0 | 50.0% | $2.3 |
| Slow (15-30 min) | 117 | 57 | 60 | 0 | 48.7% | $1.3 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 46.6% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.16 per signal — profitable even with 46.6% win rate (good risk/reward).
- 🎯 Best performance at 50-59% confidence (80.0% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (45.5% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Sideways (avg P&L $0.17) — this strategy thrives in sideways conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $1.32) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (1763s / 29.4m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 94% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gamma_wall_bounce

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA, TSLL  |  **Total Signals:** 6,756  |  **Win Rate:** 27.7%  |  **Avg P&L:** $-0.1  |  **Avg Hold:** 1572s (26.2m)  |  **Median Hold:** 1800s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 30-39% | 188 | 32 | 98 | 58 | 24.6% | $-0.1 | -20.3% |
| 40-49% | 707 | 51 | 151 | 505 | 25.2% | $-0.1 | -12.0% |
| 50-59% | 1305 | 85 | 159 | 1061 | 34.8% | $-0.1 | -7.6% |
| 60-69% | 1700 | 128 | 275 | 1297 | 31.8% | $-0.0 | -0.3% |
| 70-79% | 1386 | 108 | 228 | 1050 | 32.1% | $-0.0 | 3.3% |
| 80-89% | 1470 | 40 | 248 | 1182 | 13.9% | $-0.2 | -11.4% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 1553 | 70 | 218 | 1265 | 24.3% | $-0.1 |
| Trending (Down) | 2609 | 155 | 490 | 1964 | 24.0% | $-0.1 |
| Trending (Up) | 2594 | 219 | 451 | 1924 | 32.7% | $-0.0 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Negative Gamma (Volatile/Breakout friendly) | 92 | 10 | 41 | 41 | 19.6% | $-0.2 |
| Positive Gamma (Range-Bound friendly) | 6664 | 434 | 1118 | 5112 | 28.0% | $-0.1 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 5153 | 0 | 0 | 5153 | 0.0% | $0.0 |
| ORB / Early (0-30 min) | 1603 | 444 | 1159 | 0 | 27.7% | $-0.4 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 2516 | 185 | 583 | 1748 | 24.1% | $-0.1 |
| SHORT | 4240 | 259 | 576 | 3405 | 31.0% | $-0.1 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 271 | 41 | 230 | 0 | 15.1% | $-0.9 |
| Long (30-60 min) | 5153 | 0 | 0 | 5153 | 0.0% | $0.0 |
| Medium (5-15 min) | 591 | 159 | 432 | 0 | 26.9% | $-0.5 |
| Slow (15-30 min) | 714 | 239 | 475 | 0 | 33.5% | $-0.1 |
| Very Fast (<1 min) | 27 | 5 | 22 | 0 | 18.5% | $-0.7 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 27.7% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.09 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 50-59% confidence (34.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (13.9% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.03) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.01) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1572s / 26.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 76% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### gex_imbalance

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA  |  **Total Signals:** 7,214  |  **Win Rate:** 44.1%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 717s (11.9m)  |  **Median Hold:** 332s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 50-59% | 818 | 254 | 317 | 247 | 44.5% | $0.0 | 12.6% |
| 60-69% | 422 | 166 | 235 | 21 | 41.4% | $-0.0 | 6.2% |
| 70-79% | 5790 | 2339 | 2885 | 566 | 44.8% | $0.0 | 10.8% |
| 90-100% | 184 | 56 | 128 | 0 | 30.4% | $-0.3 | -23.9% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 1887 | 666 | 844 | 377 | 44.1% | $-0.0 |
| Trending (Down) | 1886 | 830 | 943 | 113 | 46.8% | $0.0 |
| Trending (Up) | 3441 | 1319 | 1778 | 344 | 42.6% | $0.0 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 7214 | 2815 | 3565 | 834 | 44.1% | $0.0 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 1064 | 137 | 93 | 834 | 59.6% | $0.0 |
| ORB / Early (0-30 min) | 6150 | 2678 | 3472 | 0 | 43.5% | $0.0 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 184 | 56 | 128 | 0 | 30.4% | $-0.3 |
| SHORT | 7030 | 2759 | 3437 | 834 | 44.5% | $0.0 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 2665 | 1143 | 1522 | 0 | 42.9% | $-0.0 |
| Long (30-60 min) | 1064 | 137 | 93 | 834 | 59.6% | $0.0 |
| Medium (5-15 min) | 2119 | 1019 | 1100 | 0 | 48.1% | $0.1 |
| Slow (15-30 min) | 661 | 288 | 373 | 0 | 43.6% | $0.0 |
| Very Fast (<1 min) | 705 | 228 | 477 | 0 | 32.3% | $-0.1 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 44.1% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.01 per signal — profitable even with 44.1% win rate (good risk/reward).
- 🎯 Best performance at 70-79% confidence (44.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 90-100% (30.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Down) (avg P&L $0.03) — this strategy thrives in trending (down) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.04) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (717s / 11.9m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.

---

### magnet_accelerate

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA  |  **Total Signals:** 1,962  |  **Win Rate:** 32.5%  |  **Avg P&L:** $0.0  |  **Avg Hold:** 1876s (31.3m)  |  **Median Hold:** 1499s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 60-69% | 947 | 147 | 434 | 366 | 25.3% | $0.0 | -0.7% |
| 70-79% | 813 | 201 | 324 | 288 | 38.3% | $0.1 | 11.8% |
| 80-89% | 183 | 51 | 90 | 42 | 36.2% | $-0.2 | -8.2% |
| 90-100% | 19 | 11 | 5 | 3 | 68.8% | $0.5 | 70.4% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 424 | 80 | 195 | 149 | 29.1% | $-0.0 |
| Trending (Down) | 644 | 165 | 310 | 169 | 34.7% | $-0.1 |
| Trending (Up) | 894 | 165 | 348 | 381 | 32.2% | $0.1 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Negative Gamma (Volatile/Breakout friendly) | 55 | 0 | 0 | 55 | 0.0% | $0.0 |
| Positive Gamma (Range-Bound friendly) | 1907 | 410 | 853 | 644 | 32.5% | $0.0 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 915 | 63 | 153 | 699 | 29.2% | $0.1 |
| ORB / Early (0-30 min) | 1047 | 347 | 700 | 0 | 33.1% | $-0.1 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 1388 | 176 | 536 | 676 | 24.7% | $-0.0 |
| SHORT | 574 | 234 | 317 | 23 | 42.5% | $0.2 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 275 | 77 | 198 | 0 | 28.0% | $-0.2 |
| Long (30-60 min) | 216 | 63 | 153 | 0 | 29.2% | $0.0 |
| Medium (5-15 min) | 464 | 149 | 315 | 0 | 32.1% | $-0.1 |
| Slow (15-30 min) | 254 | 104 | 150 | 0 | 40.9% | $0.2 |
| Very Fast (<1 min) | 54 | 17 | 37 | 0 | 31.5% | $-0.2 |
| Very Long (>1h) | 699 | 0 | 0 | 699 | 0.0% | $0.2 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 32.5% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 💰 Positive avg P&L of $0.04 per signal — profitable even with 32.5% win rate (good risk/reward).
- 🎯 Best performance at 90-100% confidence (68.8% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 60-69% (25.3% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.14) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $0.15) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (1876s / 31.3m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 36% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### strike_concentration

**Symbols:** AMD, AMZN, INTC, META, NVDA, SPY, TSLA, TSLL  |  **Total Signals:** 2,006  |  **Win Rate:** 52.6%  |  **Avg P&L:** $-0.3  |  **Avg Hold:** 733s (12.2m)  |  **Median Hold:** 900s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 30-39% | 36 | 4 | 4 | 28 | 50.0% | $-0.7 | -30.3% |
| 40-49% | 406 | 86 | 33 | 287 | 72.3% | $-0.7 | -26.3% |
| 50-59% | 796 | 102 | 94 | 600 | 52.0% | $-0.3 | -11.4% |
| 60-69% | 461 | 67 | 82 | 312 | 45.0% | $-0.1 | -5.6% |
| 70-79% | 307 | 37 | 54 | 216 | 40.7% | $-0.1 | -8.8% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 416 | 50 | 62 | 304 | 44.6% | $-0.2 |
| Trending (Down) | 750 | 153 | 107 | 490 | 58.8% | $-0.5 |
| Trending (Up) | 840 | 93 | 98 | 649 | 48.7% | $-0.2 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 2006 | 296 | 267 | 1443 | 52.6% | $-0.3 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| ORB / Early (0-30 min) | 2006 | 296 | 267 | 1443 | 52.6% | $-0.3 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 1092 | 85 | 134 | 873 | 38.8% | $-0.1 |
| SHORT | 914 | 211 | 133 | 570 | 61.3% | $-0.5 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 142 | 55 | 87 | 0 | 38.7% | $-0.5 |
| Medium (5-15 min) | 250 | 81 | 169 | 0 | 32.4% | $-0.4 |
| Slow (15-30 min) | 1443 | 0 | 0 | 1443 | 0.0% | $0.0 |
| Very Fast (<1 min) | 171 | 160 | 11 | 0 | 93.6% | $-2.9 |

#### 6) Insights & Recommendations

- ⚖️ Moderate win rate of 52.6% — strategy works but needs tighter entry/exit or higher confidence thresholds.
- 📉 Negative avg P&L of $-0.31 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (72.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 70-79% (40.7% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.16) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.31) — optimal hold duration is ORB / Early (0-30 min).
- ⏱️ Long avg hold time (733s / 12.2m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 72% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### theta_burn

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA  |  **Total Signals:** 2,319  |  **Win Rate:** 70.4%  |  **Avg P&L:** $-0.0  |  **Avg Hold:** 390s (6.5m)  |  **Median Hold:** 480s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 30-39% | 1070 | 303 | 94 | 673 | 76.3% | $0.0 | 0.5% |
| 40-49% | 864 | 168 | 87 | 609 | 65.9% | $-0.0 | -3.1% |
| 50-59% | 283 | 64 | 42 | 177 | 60.4% | $-0.1 | -6.9% |
| 60-69% | 91 | 18 | 10 | 63 | 64.3% | $-0.1 | -4.8% |
| 70-79% | 11 | 3 | 1 | 7 | 75.0% | $-0.3 | -4.0% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 624 | 136 | 49 | 439 | 73.5% | $-0.0 |
| Trending (Down) | 791 | 211 | 96 | 484 | 68.7% | $-0.1 |
| Trending (Up) | 904 | 209 | 89 | 606 | 70.1% | $-0.0 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 2319 | 556 | 234 | 1529 | 70.4% | $-0.0 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| ORB / Early (0-30 min) | 2319 | 556 | 234 | 1529 | 70.4% | $-0.0 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 450 | 66 | 58 | 326 | 53.2% | $-0.2 |
| SHORT | 1869 | 490 | 176 | 1203 | 73.6% | $0.0 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 445 | 296 | 149 | 0 | 66.5% | $0.1 |
| Medium (5-15 min) | 1766 | 166 | 71 | 1529 | 70.0% | $-0.1 |
| Very Fast (<1 min) | 108 | 94 | 14 | 0 | 87.0% | $0.4 |

#### 6) Insights & Recommendations

- ✅ Strong win rate of 70.4% — this strategy consistently picks directional moves.
- 📉 Negative avg P&L of $-0.03 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 30-39% confidence (76.3% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 50-59% (60.4% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $-0.02) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: ORB / Early (0-30 min) (avg P&L $-0.03) — optimal hold duration is ORB / Early (0-30 min).
- ⏳ 66% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

### vol_compression_range

**Symbols:** AMD, AMZN, INTC, META, NVDA, SOFI, SPY, TSLA  |  **Total Signals:** 2,352  |  **Win Rate:** 30.0%  |  **Avg P&L:** $-0.2  |  **Avg Hold:** 5163s (86.0m)  |  **Median Hold:** 7200s

#### 1) Performance by Confidence Level

| Confidence Bucket | Total | Wins | Losses | Closed | Win Rate | Avg P&L | Avg P&L% |
|---|---|---|---|---|---|---|---|
| 40-49% | 240 | 43 | 71 | 126 | 37.7% | $-0.1 | 1.9% |
| 50-59% | 768 | 113 | 302 | 353 | 27.2% | $-0.5 | -13.9% |
| 60-69% | 712 | 108 | 227 | 377 | 32.2% | $0.0 | -3.0% |
| 70-79% | 479 | 31 | 83 | 365 | 27.2% | $-0.1 | -6.4% |
| 80-89% | 152 | 7 | 22 | 123 | 24.1% | $-0.5 | -12.0% |
| 90-100% | 1 | 0 | 0 | 1 | 0.0% | $-1.6 | -35.4% |

#### 2) Performance by Market Type

| Market Type | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Sideways | 485 | 67 | 159 | 259 | 29.6% | $-0.3 |
| Trending (Down) | 1022 | 94 | 329 | 599 | 22.2% | $-0.4 |
| Trending (Up) | 845 | 141 | 217 | 487 | 39.4% | $0.0 |

**Regime Performance:**

| Regime | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Positive Gamma (Range-Bound friendly) | 2352 | 302 | 705 | 1345 | 30.0% | $-0.2 |

#### 3) Performance by Timeframe (Hold Duration)

| Timeframe | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Early (30-90 min) | 376 | 141 | 235 | 0 | 37.5% | $-0.0 |
| Mid-day (90-240 min) | 1473 | 30 | 98 | 1345 | 23.4% | $-0.1 |
| ORB / Early (0-30 min) | 503 | 131 | 372 | 0 | 26.0% | $-0.8 |

#### 4) Performance by Direction

| Direction | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| LONG | 1197 | 114 | 478 | 605 | 19.3% | $-0.5 |
| SHORT | 1155 | 188 | 227 | 740 | 45.3% | $0.1 |

#### 5) Hold Time Distribution

| Hold Time | Total | Wins | Losses | Closed | Win Rate | Avg P&L |
|---|---|---|---|---|---|---|
| Fast (1-5 min) | 31 | 7 | 24 | 0 | 22.6% | $-0.5 |
| Long (30-60 min) | 237 | 93 | 144 | 0 | 39.2% | $0.3 |
| Medium (5-15 min) | 225 | 54 | 171 | 0 | 24.0% | $-1.0 |
| Slow (15-30 min) | 244 | 70 | 174 | 0 | 28.7% | $-0.7 |
| Very Fast (<1 min) | 3 | 0 | 3 | 0 | 0.0% | $-0.7 |
| Very Long (>1h) | 1612 | 78 | 189 | 1345 | 29.2% | $-0.1 |

#### 6) Insights & Recommendations

- ⚠️ Low win rate of 30.0% — strategy needs significant tuning. Consider raising minimum confidence or adding filters.
- 📉 Negative avg P&L of $-0.21 per signal — losses outweigh wins. Review stop-loss placement and entry timing.
- 🎯 Best performance at 40-49% confidence (37.7% win rate) — consider raising minimum confidence threshold.
- 🚫 Worst at 80-89% (24.1% win rate) — signals in this range may be noise. Consider filtering them out.
- 📈 Best market type: Trending (Up) (avg P&L $0.01) — this strategy thrives in trending (up) conditions.
- ⏰ Best timeframe: Early (30-90 min) (avg P&L $-0.01) — optimal hold duration is Early (30-90 min).
- ⏱️ Long avg hold time (5163s / 86.0m) — consider adding a max-hold filter or time-based exit to reduce capital lockup.
- ⏳ 57% of signals time out (CLOSED) — consider tightening max hold time or adding a momentum filter.

---

## 🏆 Cross-Strategy Rankings

| Rank | Strategy | Signals | Win Rate | Avg P&L | Best Confidence | Best Market Type | Best Timeframe |
|---|---|---|---|---|---|---|---|
| 1 | gamma_squeeze | 2,906 | 46.6% | $0.2 | 50-59% | Sideways | ORB / Early (0-30 min) |
| 2 | gamma_flip_breakout | 5,430 | 86.5% | $0.1 | 80-89% | Sideways | ORB / Early (0-30 min) |
| 3 | magnet_accelerate | 1,962 | 32.5% | $0.0 | 90-100% | Trending (Down) | ORB / Early (0-30 min) |
| 4 | gex_imbalance | 7,214 | 44.1% | $0.0 | 70-79% | Trending (Down) | Early (30-90 min) |
| 5 | confluence_reversal | 3,657 | 20.6% | $0.0 | 70-79% | Trending (Up) | ORB / Early (0-30 min) |
| 6 | theta_burn | 2,319 | 70.4% | $-0.0 | 30-39% | Sideways | ORB / Early (0-30 min) |
| 7 | gamma_wall_bounce | 6,756 | 27.7% | $-0.1 | 50-59% | Trending (Up) | ORB / Early (0-30 min) |
| 8 | vol_compression_range | 2,352 | 30.0% | $-0.2 | 40-49% | Trending (Up) | Early (30-90 min) |
| 9 | strike_concentration | 2,006 | 52.6% | $-0.3 | 40-49% | Trending (Down) | ORB / Early (0-30 min) |

---

*Report generated by Forge 🐙 — Round 3 Validation Analysis*
