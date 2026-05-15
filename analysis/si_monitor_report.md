# SI Monitor Analysis Report

*Generated: 2026-05-15 08:22:53*

## A. Overview

- **Total records:** 206
- **Date range:** 2026-05-15T08:19:58.799830 to 2026-05-15T08:22:53.587382

### SI Score Statistics

| Stat | Value |
| --- | --- |
| Mean | 0.5442 |
| Median | 0.5136 |
| Std | 0.3629 |
| Min | 0.0202 |
| Max | 0.9558 |
| P25 | 0.1769 |
| P75 | 0.9499 |
| P90 | 0.9519 |
| P95 | 0.9532 |

## B. Component Breakdown

| Component | Mean | Std | Min | Max |
| --- | --- | --- | --- | --- |
| momentum | 0.6796 | 0.3816 | 0.0100 | 1.0000 |
| liquidity | 0.5018 | 0.3791 | 0.0210 | 0.9389 |
| regime_coherence | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

- **Weakest component (lowest mean):** liquidity (0.5018)
- **Most variance (highest std):** momentum (0.3816)

## C. Threshold Analysis

| Threshold | Records Above | % of Total |
| --- | --- | --- |
| > 0.5 | 105 | 51.0% |
| > 0.6 | 92 | 44.7% |
| > 0.7 | 89 | 43.2% |
| > 0.8 | 84 | 40.8% |
| > 0.9 | 78 | 37.9% |

### Average Components When SI > 0.7

| Component | Mean |
| --- | --- |
| momentum | 0.9528 |
| liquidity | 0.8693 |
| regime_coherence | 1.0000 |

## D. Regime Correlation

| Regime | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean Regime Coherence |
| --- | --- | --- | --- | --- | --- |
| NEGATIVE | 56 | 0.2962 | 0.7313 | 0.1698 | 1.0000 |
| POSITIVE | 150 | 0.6367 | 0.6604 | 0.6257 | 1.0000 |

## E. Time Series Summary

### 30-Minute Buckets

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.5442 | 206 |

- **Peak SI:** 0.5442 at 08:00
- **Trough SI:** 0.5442 at 08:00

## F. Data Quality Audit

### Flatline Detection

- **Momentum flatlined (0.01):** 6/206 (2.9%)
- **Liquidity flatlined (0.01):** 0/206 (0.0%)
- **Both flatlined:** 0/206 (0.0%)

### Symbol Coverage

| Symbol | Records | Flatline % | Mean SI |
| --- | --- | --- | --- |
| AAPL | 103 | 0.0% | 0.8622 |
| AMD | 6 | 0.0% | 0.0239 |
| INTC | 50 | 0.0% | 0.3289 |
| NVDA | 2 | 0.0% | 0.1646 |
| TSLA | 45 | 0.0% | 0.1416 |

### Field Analysis

| Field | Non-null % | Zero % | Mean |
| --- | --- | --- | --- |
| net_gamma | 100.0% | 0.0% | 624379.8104 |
| delta_density | 100.0% | 100.0% | 0.0000 |
| distance_to_wall_pct | 100.0% | 1.0% | 0.0016 |
| wall_depth | 100.0% | 0.0% | 25279158.0174 |
| book_depth | 100.0% | 0.0% | 10213.2573 |
| volume_zscore | 100.0% | 100.0% | 0.0000 |

### Regime Distribution

| Regime | Count | % |
| --- | --- | --- |
| NEGATIVE | 56 | 27.2% |
| POSITIVE | 150 | 72.8% |

### Signal Direction Distribution

| Signal | Count | % |
| --- | --- | --- |
| long | 150 | 72.8% |
| short | 56 | 27.2% |

### Time Coverage Gaps (>5 min)

No gaps > 5 minutes detected.


## G. Per-Symbol Deep Dive

### AAPL

- **Records:** 103 | **Range:** 2026-05-15 08:19 to 2026-05-15 08:22
- **SI Score:** mean=0.8622, median=0.9499, std=0.1992, min=0.0363, max=0.9558, P25=0.9216, P75=0.9514, P90=0.9533, P95=0.9549
- **momentum:** mean=0.8533, median=1.0000, std=0.2816, min=0.0124, max=1.0000, P25=0.8866, P75=1.0000, P90=1.0000, P95=1.0000
- **liquidity:** mean=0.8731, median=0.8671, std=0.0159, min=0.8471, max=0.9389, P25=0.8635, P75=0.8798, P90=0.8888, P95=0.9052
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.8622 | 103 |

### AMD

- **Records:** 6 | **Range:** 2026-05-15 08:20 to 2026-05-15 08:22
- **SI Score:** mean=0.0239, median=0.0225, std=0.0033, min=0.0202, max=0.0283, P25=0.0221, P75=0.0264, P90=0.0280, P95=0.0282
- **momentum:** mean=0.0111, median=0.0100, std=0.0017, min=0.0100, max=0.0136, P25=0.0100, P75=0.0123, P90=0.0133, P95=0.0134
- **liquidity:** mean=0.0294, median=0.0309, std=0.0044, min=0.0210, max=0.0328, P25=0.0286, P75=0.0322, P90=0.0326, P95=0.0327
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 0%, NEGATIVE 100%, OTHER 0%
- **Direction:** long 0%, short 100%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.0239 | 6 |

### INTC

- **Records:** 50 | **Range:** 2026-05-15 08:20 to 2026-05-15 08:22
- **SI Score:** mean=0.3289, median=0.2690, std=0.1357, min=0.0264, max=0.5725, P25=0.2560, P75=0.4455, P90=0.5493, P95=0.5689
- **momentum:** mean=0.8177, median=1.0000, std=0.3100, min=0.0100, max=1.0000, P25=0.7194, P75=1.0000, P90=1.0000, P95=1.0000
- **liquidity:** mean=0.1867, median=0.1095, std=0.1078, min=0.0781, max=0.4406, P25=0.1036, P75=0.3088, P90=0.3170, P95=0.3233
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 0%, NEGATIVE 100%, OTHER 0%
- **Direction:** long 0%, short 100%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.3289 | 50 |

### NVDA

- **Records:** 2 | **Range:** 2026-05-15 08:22 to 2026-05-15 08:22
- **SI Score:** mean=0.1646, median=0.1646, std=0.1770, min=0.0395, max=0.2898, P25=0.1021, P75=0.2272, P90=0.2648, P95=0.2773
- **momentum:** mean=0.0867, median=0.0867, std=0.1030, min=0.0138, max=0.1595, P25=0.0502, P75=0.1231, P90=0.1449, P95=0.1522
- **liquidity:** mean=0.3443, median=0.3443, std=0.0284, min=0.3243, max=0.3644, P25=0.3343, P75=0.3544, P90=0.3604, P95=0.3624
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.1646 | 2 |

### TSLA

- **Records:** 45 | **Range:** 2026-05-15 08:20 to 2026-05-15 08:22
- **SI Score:** mean=0.1416, median=0.1565, std=0.0403, min=0.0261, max=0.1793, P25=0.1262, P75=0.1708, P90=0.1772, P95=0.1784
- **momentum:** mean=0.2442, median=0.2306, std=0.1563, min=0.0100, max=0.5509, P25=0.1140, P75=0.3630, P90=0.4636, P95=0.5060
- **liquidity:** mean=0.0720, median=0.0721, std=0.0007, min=0.0703, max=0.0734, P25=0.0717, P75=0.0724, P90=0.0731, P95=0.0732
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 08:00 | 0.1416 | 45 |


## H. Component Correlations & Regime Cross-Tab

### Correlation Matrix

| Pair | Correlation |
| --- | --- |
| si_score vs momentum | 0.7211 |
| si_score vs liquidity | 0.8940 |
| si_score vs regime_coherence | 0.0000 |
| momentum vs liquidity | 0.4579 |
| momentum vs regime_coherence | 0.0000 |
| liquidity vs regime_coherence | 0.0000 |

### Regime × Direction Cross-Tab

| Regime | Direction | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean RegimeCoherence |
| --- | --- | --- | --- | --- | --- | --- |
| NEGATIVE | short | 56 | 0.2962 | 0.7313 | 0.1698 | 1.0000 |
| POSITIVE | long | 150 | 0.6367 | 0.6604 | 0.6257 | 1.0000 |

### SI Score Distribution

| 0.00-0.10 |   17 |   8.3% | ████████
| 0.10-0.20 |   40 |  19.4% | ████████████████████
| 0.20-0.30 |   34 |  16.5% | █████████████████
| 0.30-0.40 |    4 |   1.9% | ██
| 0.40-0.50 |    6 |   2.9% | ███
| 0.50-0.60 |   13 |   6.3% | ██████
| 0.60-0.70 |    3 |   1.5% | █
| 0.70-0.80 |    5 |   2.4% | ██
| 0.80-0.90 |    6 |   2.9% | ███
| 0.90-1.00 |   78 |  37.9% | ████████████████████████████████████████
| --- | --- | --- | --- |

### SI Score Distribution (High-Resolution: 0.00–0.10)

| 0.0100-0.0120 |    0 |   0.0% | 
| 0.0120-0.0140 |    0 |   0.0% | 
| 0.0140-0.0160 |    0 |   0.0% | 
| 0.0160-0.0180 |    0 |   0.0% | 
| 0.0180-0.0200 |    0 |   0.0% | 
| 0.0200-0.0250 |    4 |   1.9% | ██████████████████████████
| 0.0250-0.0300 |    4 |   1.9% | ██████████████████████████
| 0.0300-0.0500 |    3 |   1.5% | ████████████████████
| 0.0500-0.1000 |    6 |   2.9% | ████████████████████████████████████████
| --- | --- | --- | --- |

### Top 20 Lowest SI Scores

| Timestamp | Symbol | Regime | Direction | SI Score | Momentum | Liquidity | Regime Coherence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 08:21:56 | AMD | NEGATIVE | short | 0.020200 | 0.0100 | 0.0210 | 1.0000 |
| 08:20:41 | AMD | NEGATIVE | short | 0.022000 | 0.0100 | 0.0282 | 1.0000 |
| 08:21:37 | AMD | NEGATIVE | short | 0.022300 | 0.0100 | 0.0299 | 1.0000 |
| 08:22:15 | AMD | NEGATIVE | short | 0.022700 | 0.0100 | 0.0323 | 1.0000 |
| 08:20:04 | TSLA | POSITIVE | long | 0.026100 | 0.0100 | 0.0718 | 1.0000 |
| 08:20:01 | INTC | NEGATIVE | short | 0.026400 | 0.0100 | 0.0781 | 1.0000 |
| 08:22:35 | AMD | NEGATIVE | short | 0.027700 | 0.0130 | 0.0328 | 1.0000 |
| 08:22:53 | AMD | NEGATIVE | short | 0.028300 | 0.0136 | 0.0319 | 1.0000 |
| 08:19:58 | AAPL | POSITIVE | long | 0.036300 | 0.0124 | 0.8471 | 1.0000 |
| 08:20:07 | TSLA | POSITIVE | long | 0.037100 | 0.0152 | 0.0711 | 1.0000 |
| 08:22:06 | NVDA | POSITIVE | long | 0.039500 | 0.0138 | 0.3644 | 1.0000 |
| 08:20:10 | TSLA | POSITIVE | long | 0.053700 | 0.0246 | 0.0704 | 1.0000 |
| 08:20:04 | INTC | NEGATIVE | short | 0.064000 | 0.0229 | 0.4406 | 1.0000 |
| 08:20:12 | TSLA | POSITIVE | long | 0.064100 | 0.0317 | 0.0703 | 1.0000 |
| 08:20:15 | TSLA | POSITIVE | long | 0.076600 | 0.0416 | 0.0706 | 1.0000 |
| 08:20:18 | TSLA | POSITIVE | long | 0.087400 | 0.0520 | 0.0709 | 1.0000 |
| 08:20:21 | TSLA | POSITIVE | long | 0.096300 | 0.0622 | 0.0711 | 1.0000 |
| 08:20:00 | AAPL | POSITIVE | long | 0.100500 | 0.0361 | 0.8481 | 1.0000 |
| 08:20:24 | TSLA | POSITIVE | long | 0.103500 | 0.0717 | 0.0712 | 1.0000 |
| 08:20:27 | TSLA | POSITIVE | long | 0.110600 | 0.0824 | 0.0714 | 1.0000 |


### Net Gamma Distribution

| Net Gamma Bin | Count | Mean SI | % of Total |
| --- | --- | --- | --- |
| < 0 |   56 | 0.2962 |  27.2% |
| 0 – 1K |    0 | 0.0000 |   0.0% |
| 1K – 10K |    1 | 0.0261 |   0.5% |
| 10K – 100K |   13 | 0.0864 |   6.3% |
| > 100K |  136 | 0.6938 |  66.0% |
