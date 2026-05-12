# Validation Round 3 — Per-Strategy Deep Analysis

**Date:** 2026-05-06 | **Total Signals Analyzed:** 17,082

---

## 📊 Overall Summary

- **Total Signals:** 17,082
- **Win Rate:** 27.2%
- **Total P&L:** $-31.52
- **Avg Win:** $1.43 | **Avg Loss:** $-1.38
- **Avg Hold Time:** 1710s (28.5 min)
- **Avg Confidence:** 66%


## 🐉 Strategy: Gamma Flip Breakout

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 3,395 |
| Win Rate | 59.1% |
| Total P&L | $103.52 |
| Avg Win | $0.78 |
| Avg Loss | $-1.46 |
| Avg Hold Time | 1136s (18.9 min) |
| Avg Confidence | 75% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 100-109% | 48 | 26 | 22 | 54% | $-0.08 |
| 30-39% | 10 | 4 | 6 | 40% | $-0.11 |
| 40-49% | 25 | 16 | 3 | 64% | $1.83 |
| 50-59% | 770 | 318 | 412 | 41% | $-0.21 |
| 60-69% | 620 | 337 | 248 | 54% | $-0.16 |
| 70-79% | 402 | 292 | 81 | 73% | $0.05 |
| 80-89% | 1098 | 709 | 84 | 65% | $0.25 |
| 90-99% | 422 | 303 | 82 | 72% | $0.06 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 621 | 386 | 174 | 62% | $0.06 |
| Trending | 2774 | 1619 | 764 | 58% | $0.02 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 742 | 375 | 214 | 51% | $0.02 |
| Mid (12:00-14:30 PT) | 641 | 334 | 211 | 52% | $-0.07 |
| ORB (9:30-10:00 PT) | 127 | 70 | 22 | 55% | $-0.21 |
| Pre-Market (<9:30 PT) | 1885 | 1226 | 491 | 65% | $0.08 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 845/1548 (55% win rate)
- SHORT: 1160/1847 (63% win rate)

**Signal Strength:**
- UNKNOWN: 2005/3395 (59% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 481/497 (97% win rate)
- Long (>15 min): 527/1359 (39% win rate)
- Medium (5-15 min): 445/796 (56% win rate)
- Short (1-5 min): 552/743 (74% win rate)

**Symbol Distribution:**
- AMD: 461/620 (74% win rate)
- AMZN: 239/488 (49% win rate)
- INTC: 391/651 (60% win rate)
- META: 266/432 (62% win rate)
- NVDA: 307/564 (54% win rate)
- SOFI: 53/170 (31% win rate)
- TSLA: 279/448 (62% win rate)
- TSLL: 9/22 (41% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 70-79% bucket perform best (292/402 = 73% WR). Consider raising minimum confidence from 0.30 to 70/100.
- **Market Type Fit:** Best in Sideways (WR: 62%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Pre-Market (<9:30 PT) shows strongest results (1226/1885 = 65% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Fast (<1 min) (481/497 = 97% WR). Consider implementing dynamic exit based on hold time.


## 🐉 Strategy: Confluence Reversal

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 3,325 |
| Win Rate | 8.6% |
| Total P&L | $116.21 |
| Avg Win | $3.68 |
| Avg Loss | $-1.68 |
| Avg Hold Time | 2727s (45.5 min) |
| Avg Confidence | 58% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 30-39% | 52 | 7 | 18 | 13% | $1.13 |
| 40-49% | 163 | 15 | 83 | 9% | $-1.11 |
| 50-59% | 2314 | 224 | 833 | 10% | $0.05 |
| 60-69% | 134 | 12 | 71 | 9% | $-0.14 |
| 70-79% | 558 | 25 | 83 | 4% | $0.22 |
| 80-89% | 104 | 3 | 14 | 3% | $0.23 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 591 | 57 | 179 | 10% | $0.15 |
| Trending | 2734 | 229 | 923 | 8% | $0.01 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 798 | 66 | 60 | 8% | $0.41 |
| Mid (12:00-14:30 PT) | 783 | 24 | 157 | 3% | $-0.07 |
| ORB (9:30-10:00 PT) | 153 | 2 | 15 | 1% | $0.47 |
| Pre-Market (<9:30 PT) | 1591 | 194 | 870 | 12% | $-0.15 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 235/2343 (10% win rate)
- SHORT: 51/982 (5% win rate)

**Signal Strength:**
- UNKNOWN: 286/3325 (9% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 1/19 (5% win rate)
- Long (>15 min): 210/2829 (7% win rate)
- Medium (5-15 min): 58/335 (17% win rate)
- Short (1-5 min): 17/142 (12% win rate)

**Symbol Distribution:**
- AMD: 105/524 (20% win rate)
- AMZN: 0/412 (0% win rate)
- INTC: 53/560 (9% win rate)
- META: 14/410 (3% win rate)
- NVDA: 19/431 (4% win rate)
- SOFI: 6/163 (4% win rate)
- TSLA: 4/413 (1% win rate)
- TSLL: 85/412 (21% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 30-39% bucket perform best (7/52 = 13% WR). Consider raising minimum confidence from 0.30 to 30/100.
- **Market Type Fit:** Best in Sideways (WR: 10%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Pre-Market (<9:30 PT) shows strongest results (194/1591 = 12% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Medium (5-15 min) (58/335 = 17% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 9%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.


## 🐉 Strategy: Gamma Wall Bounce

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 2,727 |
| Win Rate | 10.2% |
| Total P&L | $-193.52 |
| Avg Win | $2.90 |
| Avg Loss | $-1.86 |
| Avg Hold Time | 1417s (23.6 min) |
| Avg Confidence | 66% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 30-39% | 168 | 11 | 58 | 7% | $-0.33 |
| 40-49% | 295 | 32 | 109 | 11% | $-0.37 |
| 50-59% | 460 | 59 | 149 | 13% | $-0.18 |
| 60-69% | 517 | 85 | 129 | 16% | $0.08 |
| 70-79% | 749 | 64 | 128 | 9% | $0.03 |
| 80-89% | 538 | 26 | 98 | 5% | $-0.01 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 503 | 46 | 128 | 9% | $-0.06 |
| Trending | 2124 | 231 | 543 | 11% | $-0.08 |
| Volatile/Breakout | 100 | 0 | 0 | 0% | $0.09 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 567 | 15 | 89 | 3% | $-0.24 |
| Mid (12:00-14:30 PT) | 503 | 7 | 78 | 1% | $-0.11 |
| ORB (9:30-10:00 PT) | 147 | 7 | 37 | 5% | $-0.23 |
| Pre-Market (<9:30 PT) | 1510 | 248 | 467 | 16% | $0.02 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 90/1105 (8% win rate)
- SHORT: 187/1622 (12% win rate)

**Signal Strength:**
- UNKNOWN: 277/2727 (10% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 6/39 (15% win rate)
- Long (>15 min): 87/2093 (4% win rate)
- Medium (5-15 min): 132/375 (35% win rate)
- Short (1-5 min): 52/220 (24% win rate)

**Symbol Distribution:**
- AMD: 140/448 (31% win rate)
- AMZN: 17/412 (4% win rate)
- INTC: 42/222 (19% win rate)
- META: 6/485 (1% win rate)
- NVDA: 18/524 (3% win rate)
- SOFI: 7/106 (7% win rate)
- TSLA: 41/463 (9% win rate)
- TSLL: 6/67 (9% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 60-69% bucket perform best (85/517 = 16% WR). Consider raising minimum confidence from 0.30 to 60/100.
- **Market Type Fit:** Best in Trending (WR: 11%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Pre-Market (<9:30 PT) shows strongest results (248/1510 = 16% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Medium (5-15 min) (132/375 = 35% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 10%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.
- **P&L Negative:** Total P&L is $-193.52. Review if large losses are outliers or systemic. Consider tighter stops or adding a max-loss-per-day rule.


## 🐉 Strategy: Gex Imbalance

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 2,719 |
| Win Rate | 48.8% |
| Total P&L | $389.30 |
| Avg Win | $0.96 |
| Avg Loss | $-0.70 |
| Avg Hold Time | 486s (8.1 min) |
| Avg Confidence | 76% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 100-109% | 254 | 119 | 129 | 47% | $0.18 |
| 40-49% | 4 | 0 | 0 | 0% | $0.64 |
| 50-59% | 116 | 48 | 68 | 41% | $-0.37 |
| 60-69% | 163 | 96 | 65 | 59% | $-0.18 |
| 70-79% | 2182 | 1065 | 1062 | 49% | $0.19 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 526 | 256 | 268 | 49% | $0.12 |
| Trending | 2193 | 1072 | 1056 | 49% | $0.15 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 492 | 159 | 319 | 32% | $0.02 |
| Mid (12:00-14:30 PT) | 425 | 183 | 233 | 43% | $0.04 |
| ORB (9:30-10:00 PT) | 126 | 80 | 44 | 63% | $0.36 |
| Pre-Market (<9:30 PT) | 1676 | 906 | 728 | 54% | $0.19 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 119/254 (47% win rate)
- SHORT: 1209/2465 (49% win rate)

**Signal Strength:**
- UNKNOWN: 1328/2719 (49% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 94/312 (30% win rate)
- Long (>15 min): 238/422 (56% win rate)
- Medium (5-15 min): 440/800 (55% win rate)
- Short (1-5 min): 556/1185 (47% win rate)

**Symbol Distribution:**
- AMD: 211/398 (53% win rate)
- AMZN: 171/395 (43% win rate)
- INTC: 236/486 (49% win rate)
- META: 158/388 (41% win rate)
- NVDA: 251/489 (51% win rate)
- SOFI: 110/144 (76% win rate)
- TSLA: 190/398 (48% win rate)
- TSLL: 1/21 (5% win rate)

### Q5: Recommended Enhancements

- **Market Type Fit:** Best in Trending (WR: 49%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** ORB (9:30-10:00 PT) shows strongest results (80/126 = 63% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Long (>15 min) (238/422 = 56% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 49%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.


## 🐉 Strategy: Magnet Accelerate

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 2,196 |
| Win Rate | 19.4% |
| Total P&L | $-446.90 |
| Avg Win | $1.73 |
| Avg Loss | $-0.94 |
| Avg Hold Time | 1273s (21.2 min) |
| Avg Confidence | 65% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 30-39% | 123 | 10 | 109 | 8% | $-1.01 |
| 40-49% | 153 | 19 | 115 | 12% | $-0.59 |
| 50-59% | 393 | 36 | 307 | 9% | $-0.41 |
| 60-69% | 666 | 82 | 469 | 12% | $-0.23 |
| 70-79% | 597 | 169 | 352 | 28% | $0.14 |
| 80-89% | 244 | 104 | 121 | 43% | $-0.00 |
| 90-99% | 20 | 5 | 13 | 25% | $-0.30 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 437 | 65 | 322 | 15% | $-0.35 |
| Trending | 1758 | 359 | 1164 | 20% | $-0.17 |
| Volatile/Breakout | 1 | 1 | 0 | 100% | $6.67 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 454 | 68 | 273 | 15% | $0.25 |
| Mid (12:00-14:30 PT) | 341 | 89 | 185 | 26% | $0.06 |
| ORB (9:30-10:00 PT) | 80 | 0 | 72 | 0% | $-0.94 |
| Pre-Market (<9:30 PT) | 1321 | 268 | 956 | 20% | $-0.38 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 243/1161 (21% win rate)
- SHORT: 182/1035 (18% win rate)

**Signal Strength:**
- UNKNOWN: 425/2196 (19% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 24/117 (21% win rate)
- Long (>15 min): 211/1024 (21% win rate)
- Medium (5-15 min): 121/639 (19% win rate)
- Short (1-5 min): 69/416 (17% win rate)

**Symbol Distribution:**
- AMD: 21/259 (8% win rate)
- AMZN: 119/350 (34% win rate)
- INTC: 51/415 (12% win rate)
- META: 110/343 (32% win rate)
- NVDA: 51/357 (14% win rate)
- SOFI: 30/225 (13% win rate)
- TSLA: 43/229 (19% win rate)
- TSLL: 0/18 (0% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 80-89% bucket perform best (104/244 = 43% WR). Consider raising minimum confidence from 0.30 to 80/100.
- **Market Type Fit:** Best in Volatile/Breakout (WR: 100%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Mid (12:00-14:30 PT) shows strongest results (89/341 = 26% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Long (>15 min) (211/1024 = 21% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 19%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.
- **P&L Negative:** Total P&L is $-446.90. Review if large losses are outliers or systemic. Consider tighter stops or adding a max-loss-per-day rule.


## 🐉 Strategy: Gamma Squeeze

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 1,490 |
| Win Rate | 2.0% |
| Total P&L | $-336.93 |
| Avg Win | $4.04 |
| Avg Loss | $-3.64 |
| Avg Hold Time | 1682s (28.0 min) |
| Avg Confidence | 59% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 30-39% | 10 | 4 | 4 | 40% | $1.02 |
| 40-49% | 165 | 7 | 61 | 4% | $-0.80 |
| 50-59% | 246 | 5 | 44 | 2% | $-0.38 |
| 60-69% | 1069 | 14 | 12 | 1% | $-0.11 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 293 | 8 | 31 | 3% | $-0.37 |
| Trending | 1197 | 22 | 90 | 2% | $-0.19 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 366 | 4 | 0 | 1% | $0.39 |
| Mid (12:00-14:30 PT) | 402 | 0 | 3 | 0% | $-0.36 |
| ORB (9:30-10:00 PT) | 95 | 0 | 1 | 0% | $0.09 |
| Pre-Market (<9:30 PT) | 627 | 26 | 117 | 4% | $-0.55 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 30/1490 (2% win rate)

**Signal Strength:**
- UNKNOWN: 30/1490 (2% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 0/1 (0% win rate)
- Long (>15 min): 18/1375 (1% win rate)
- Medium (5-15 min): 5/87 (6% win rate)
- Short (1-5 min): 7/27 (26% win rate)

**Symbol Distribution:**
- AMD: 6/102 (6% win rate)
- AMZN: 0/298 (0% win rate)
- INTC: 5/32 (16% win rate)
- META: 0/317 (0% win rate)
- NVDA: 15/467 (3% win rate)
- TSLA: 0/194 (0% win rate)
- TSLL: 4/80 (5% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 30-39% bucket perform best (4/10 = 40% WR). Consider raising minimum confidence from 0.30 to 30/100.
- **Market Type Fit:** Best in Sideways (WR: 3%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Pre-Market (<9:30 PT) shows strongest results (26/627 = 4% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Short (1-5 min) (7/27 = 26% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 2%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.
- **P&L Negative:** Total P&L is $-336.93. Review if large losses are outliers or systemic. Consider tighter stops or adding a max-loss-per-day rule.


## 🐉 Strategy: Vol Compression Range

### Overview
| Metric | Value |
|--------|-------|
| Total Signals | 1,230 |
| Win Rate | 24.1% |
| Total P&L | $336.80 |
| Avg Win | $3.70 |
| Avg Loss | $-2.81 |
| Avg Hold Time | 4711s (78.5 min) |
| Avg Confidence | 59% |

### Q1: Performance by Confidence Level

| Confidence | Total | Wins | Losses | Win Rate | Avg P&L |
|------------|-------|------|--------|----------|---------|
| 30-39% | 56 | 18 | 29 | 32% | $0.93 |
| 40-49% | 234 | 59 | 118 | 25% | $-0.25 |
| 50-59% | 348 | 114 | 109 | 33% | $0.36 |
| 60-69% | 374 | 68 | 70 | 18% | $0.42 |
| 70-79% | 203 | 33 | 60 | 16% | $0.31 |
| 80-89% | 15 | 4 | 10 | 27% | $-0.10 |

### Q2: Market Type Performance

| Market Type | Total | Wins | Losses | Win Rate | Avg P&L |
|-------------|-------|------|--------|----------|---------|
| Sideways | 253 | 66 | 71 | 26% | $0.47 |
| Trending | 977 | 230 | 325 | 24% | $0.22 |

### Q3: Timeframe Performance

| Timeframe | Total | Wins | Losses | Win Rate | Avg P&L |
|-----------|-------|------|--------|----------|---------|
| Early (10:00-12:00 PT) | 387 | 79 | 88 | 20% | $0.72 |
| Mid (12:00-14:30 PT) | 354 | 30 | 91 | 8% | $-0.28 |
| ORB (9:30-10:00 PT) | 45 | 6 | 14 | 13% | $-0.69 |
| Pre-Market (<9:30 PT) | 444 | 181 | 203 | 41% | $0.42 |

### Q4: Additional Insights

**Direction Breakdown:**
- LONG: 173/576 (30% win rate)
- SHORT: 123/654 (19% win rate)

**Signal Strength:**
- UNKNOWN: 296/1230 (24% win rate)

**Hold Time Distribution:**
- Fast (<1 min): 2/3 (67% win rate)
- Long (>15 min): 229/1062 (22% win rate)
- Medium (5-15 min): 58/143 (41% win rate)
- Short (1-5 min): 7/22 (32% win rate)

**Symbol Distribution:**
- AMD: 102/240 (42% win rate)
- AMZN: 21/197 (11% win rate)
- INTC: 41/91 (45% win rate)
- META: 18/296 (6% win rate)
- NVDA: 25/145 (17% win rate)
- SOFI: 2/2 (100% win rate)
- TSLA: 70/242 (29% win rate)
- TSLL: 17/17 (100% win rate)

### Q5: Recommended Enhancements

- **Confidence Threshold:** Signals in 50-59% bucket perform best (114/348 = 33% WR). Consider raising minimum confidence from 0.30 to 50/100.
- **Market Type Fit:** Best in Sideways (WR: 26%). Consider adding a regime filter to avoid trading in non-optimal regimes.
- **Timeframe Optimization:** Pre-Market (<9:30 PT) shows strongest results (181/444 = 41% WR). Consider weighting signals from this period higher.
- **Hold Time:** Optimal hold range is Fast (<1 min) (2/3 = 67% WR). Consider implementing dynamic exit based on hold time.
- **Win Rate:** At 24%, consider adding a secondary confirmation filter (e.g., volume spike, RSI confirmation) to improve signal quality.


---

## 📋 Cross-Strategy Comparison


| Strategy | Signals | Win Rate | Total P&L | Avg Hold | Best Timeframe | Best Market |
|----------|---------|----------|-----------|----------|----------------|-------------|
| Gamma Flip Breakout | 3395 | 59% | $104 | 18.9m | Pre-Market | Sideways |
| Confluence Reversal | 3325 | 9% | $116 | 45.5m | Pre-Market | Sideways |
| Gamma Wall Bounce | 2727 | 10% | $-194 | 23.6m | Pre-Market | Trending |
| Gex Imbalance | 2719 | 49% | $389 | 8.1m | ORB | Trending |
| Magnet Accelerate | 2196 | 19% | $-447 | 21.2m | Mid | Volatile/Breakout |
| Gamma Squeeze | 1490 | 2% | $-337 | 28.0m | Pre-Market | Sideways |
| Vol Compression Range | 1230 | 24% | $337 | 78.5m | Pre-Market | Sideways |

---

*Analysis generated by Archon for Validation Round 3.*