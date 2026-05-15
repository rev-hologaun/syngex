# SI Monitor Analysis Report

*Generated: 2026-05-15 10:08:06*

## A. Overview

- **Total records:** 946
- **Date range:** 2026-05-15T10:04:11.150217 to 2026-05-15T10:08:06.373018

### SI Score Statistics

| Stat | Value |
| --- | --- |
| Mean | 0.5275 |
| Median | 0.7115 |
| Std | 0.3784 |
| Min | 0.0552 |
| Max | 0.9990 |
| P25 | 0.0951 |
| P75 | 0.7775 |
| P90 | 0.9978 |
| P95 | 0.9983 |

## B. Component Breakdown

| Component | Mean | Std | Min | Max |
| --- | --- | --- | --- | --- |
| momentum | 0.7089 | 0.3878 | 0.0327 | 1.0000 |
| liquidity | 0.4099 | 0.3582 | 0.0338 | 0.9969 |
| regime_coherence | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

- **Weakest component (lowest mean):** liquidity (0.4099)
- **Most variance (highest std):** momentum (0.3878)

## C. Threshold Analysis

| Threshold | Records Above | % of Total |
| --- | --- | --- |
| > 0.5 | 561 | 59.3% |
| > 0.6 | 561 | 59.3% |
| > 0.7 | 561 | 59.3% |
| > 0.8 | 191 | 20.2% |
| > 0.9 | 191 | 20.2% |

### Average Components When SI > 0.7

| Component | Mean |
| --- | --- |
| momentum | 1.0000 |
| liquidity | 0.6643 |
| regime_coherence | 1.0000 |

## D. Regime Correlation

| Regime | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean Regime Coherence |
| --- | --- | --- | --- | --- | --- |
| NEGATIVE | 381 | 0.3846 | 0.5223 | 0.2413 | 1.0000 |
| POSITIVE | 565 | 0.6238 | 0.8347 | 0.5237 | 1.0000 |

## E. Time Series Summary

### 30-Minute Buckets

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.5275 | 946 |

- **Peak SI:** 0.5275 at 10:00
- **Trough SI:** 0.5275 at 10:00

## F. Data Quality Audit

### Flatline Detection

- **Momentum flatlined (0.01):** 0/946 (0.0%)
- **Liquidity flatlined (0.01):** 0/946 (0.0%)
- **Both flatlined:** 0/946 (0.0%)

### Symbol Coverage

| Symbol | Records | Flatline % | Mean SI |
| --- | --- | --- | --- |
| AAPL | 191 | 0.0% | 0.9977 |
| AMD | 196 | 0.0% | 0.0755 |
| INTC | 185 | 0.0% | 0.7121 |
| NVDA | 185 | 0.0% | 0.7769 |
| TSLA | 189 | 0.0% | 0.0960 |

### Field Analysis

| Field | Non-null % | Zero % | Mean |
| --- | --- | --- | --- |
| net_gamma | 100.0% | 0.0% | 1154700.8097 |
| delta_density | 100.0% | 100.0% | 0.0000 |
| distance_to_wall_pct | 100.0% | 0.8% | 0.0018 |
| wall_depth | 100.0% | 0.0% | 22221579.5016 |
| book_depth | 100.0% | 0.0% | 9822.1871 |
| volume_zscore | 100.0% | 100.0% | 0.0000 |

### Regime Distribution

| Regime | Count | % |
| --- | --- | --- |
| NEGATIVE | 381 | 40.3% |
| POSITIVE | 565 | 59.7% |

### Signal Direction Distribution

| Signal | Count | % |
| --- | --- | --- |
| long | 565 | 59.7% |
| short | 381 | 40.3% |

### Time Coverage Gaps (>5 min)

No gaps > 5 minutes detected.


## G. Per-Symbol Deep Dive

### AAPL

- **Records:** 191 | **Range:** 2026-05-15 10:04 to 2026-05-15 10:08
- **SI Score:** mean=0.9977, median=0.9978, std=0.0007, min=0.9964, max=0.9990, P25=0.9972, P75=0.9982, P90=0.9986, P95=0.9987
- **momentum:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **liquidity:** mean=0.9932, median=0.9934, std=0.0020, min=0.9894, max=0.9969, P25=0.9917, P75=0.9948, P90=0.9957, P95=0.9960
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.9977 | 191 |

### AMD

- **Records:** 196 | **Range:** 2026-05-15 10:04 to 2026-05-15 10:08
- **SI Score:** mean=0.0755, median=0.0775, std=0.0095, min=0.0552, max=0.0879, P25=0.0686, P75=0.0834, P90=0.0865, P95=0.0874
- **momentum:** mean=0.0713, median=0.0736, std=0.0229, min=0.0327, max=0.1123, P25=0.0507, P75=0.0904, P90=0.1008, P95=0.1059
- **liquidity:** mean=0.0424, median=0.0422, std=0.0010, min=0.0408, max=0.0458, P25=0.0416, P75=0.0430, P90=0.0439, P95=0.0443
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 0%, NEGATIVE 100%, OTHER 0%
- **Direction:** long 0%, short 100%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.0755 | 196 |

### INTC

- **Records:** 185 | **Range:** 2026-05-15 10:04 to 2026-05-15 10:08
- **SI Score:** mean=0.7121, median=0.7119, std=0.0031, min=0.7046, max=0.7179, P25=0.7101, P75=0.7149, P90=0.7159, P95=0.7163
- **momentum:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **liquidity:** mean=0.4519, median=0.4516, std=0.0037, min=0.4429, max=0.4589, P25=0.4495, P75=0.4553, P90=0.4565, P95=0.4570
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 0%, NEGATIVE 100%, OTHER 0%
- **Direction:** long 0%, short 100%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.7121 | 185 |

### NVDA

- **Records:** 185 | **Range:** 2026-05-15 10:04 to 2026-05-15 10:08
- **SI Score:** mean=0.7769, median=0.7769, std=0.0010, min=0.7744, max=0.7796, P25=0.7765, P75=0.7775, P90=0.7782, P95=0.7785
- **momentum:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **liquidity:** mean=0.5372, median=0.5372, std=0.0014, min=0.5336, max=0.5410, P25=0.5366, P75=0.5380, P90=0.5390, P95=0.5395
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.7769 | 185 |

### TSLA

- **Records:** 189 | **Range:** 2026-05-15 10:04 to 2026-05-15 10:08
- **SI Score:** mean=0.0960, median=0.0962, std=0.0019, min=0.0912, max=0.1001, P25=0.0957, P75=0.0966, P90=0.0985, P95=0.0997
- **momentum:** mean=0.5060, median=0.4941, std=0.1930, min=0.1936, max=0.8466, P25=0.3381, P75=0.6749, P90=0.7770, P95=0.8126
- **liquidity:** mean=0.0359, median=0.0352, std=0.0014, min=0.0338, max=0.0380, P25=0.0347, P75=0.0375, P90=0.0377, P95=0.0378
- **regime_coherence:** mean=1.0000, median=1.0000, std=0.0000, min=1.0000, max=1.0000, P25=1.0000, P75=1.0000, P90=1.0000, P95=1.0000
- **Regime:** POSITIVE 100%, NEGATIVE 0%, OTHER 0%
- **Direction:** long 100%, short 0%

#### Time Series (30-min buckets)

| Bucket | Mean SI | Records |
| --- | --- | --- |
| 10:00 | 0.0960 | 189 |


## H. Component Correlations & Regime Cross-Tab

### Correlation Matrix

| Pair | Correlation |
| --- | --- |
| si_score vs momentum | 0.8842 |
| si_score vs liquidity | 0.9585 |
| si_score vs regime_coherence | 0.0000 |
| momentum vs liquidity | 0.7754 |
| momentum vs regime_coherence | 0.0000 |
| liquidity vs regime_coherence | 0.0000 |

### Regime × Direction Cross-Tab

| Regime | Direction | Count | Mean SI | Mean Momentum | Mean Liquidity | Mean RegimeCoherence |
| --- | --- | --- | --- | --- | --- | --- |
| NEGATIVE | short | 381 | 0.3846 | 0.5223 | 0.2413 | 1.0000 |
| POSITIVE | long | 565 | 0.6238 | 0.8347 | 0.5237 | 1.0000 |

### SI Score Distribution

| 0.00-0.10 |  383 |  40.5% | ████████████████████████████████████████
| 0.10-0.20 |    2 |   0.2% | 
| 0.20-0.30 |    0 |   0.0% | 
| 0.30-0.40 |    0 |   0.0% | 
| 0.40-0.50 |    0 |   0.0% | 
| 0.50-0.60 |    0 |   0.0% | 
| 0.60-0.70 |    0 |   0.0% | 
| 0.70-0.80 |  370 |  39.1% | ██████████████████████████████████████
| 0.80-0.90 |    0 |   0.0% | 
| 0.90-1.00 |  191 |  20.2% | ███████████████████
| --- | --- | --- | --- |

### SI Score Distribution (High-Resolution: 0.00–0.10)

| 0.0100-0.0120 |    0 |   0.0% | 
| 0.0120-0.0140 |    0 |   0.0% | 
| 0.0140-0.0160 |    0 |   0.0% | 
| 0.0160-0.0180 |    0 |   0.0% | 
| 0.0180-0.0200 |    0 |   0.0% | 
| 0.0200-0.0250 |    0 |   0.0% | 
| 0.0250-0.0300 |    0 |   0.0% | 
| 0.0300-0.0500 |    0 |   0.0% | 
| 0.0500-0.1000 |  383 |  40.5% | ████████████████████████████████████████
| --- | --- | --- | --- |

### Top 20 Lowest SI Scores

| Timestamp | Symbol | Regime | Direction | SI Score | Momentum | Liquidity | Regime Coherence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10:04:11 | AMD | NEGATIVE | short | 0.055200 | 0.0329 | 0.0437 | 1.0000 |
| 10:04:12 | AMD | NEGATIVE | short | 0.055400 | 0.0327 | 0.0444 | 1.0000 |
| 10:04:13 | AMD | NEGATIVE | short | 0.055500 | 0.0332 | 0.0436 | 1.0000 |
| 10:04:14 | AMD | NEGATIVE | short | 0.055900 | 0.0336 | 0.0437 | 1.0000 |
| 10:04:15 | AMD | NEGATIVE | short | 0.055900 | 0.0341 | 0.0429 | 1.0000 |
| 10:04:16 | AMD | NEGATIVE | short | 0.056600 | 0.0347 | 0.0431 | 1.0000 |
| 10:04:17 | AMD | NEGATIVE | short | 0.056600 | 0.0353 | 0.0424 | 1.0000 |
| 10:04:18 | AMD | NEGATIVE | short | 0.056900 | 0.0355 | 0.0425 | 1.0000 |
| 10:04:19 | AMD | NEGATIVE | short | 0.057600 | 0.0357 | 0.0432 | 1.0000 |
| 10:04:20 | AMD | NEGATIVE | short | 0.058000 | 0.0362 | 0.0433 | 1.0000 |
| 10:04:21 | AMD | NEGATIVE | short | 0.058200 | 0.0364 | 0.0433 | 1.0000 |
| 10:04:22 | AMD | NEGATIVE | short | 0.058600 | 0.0368 | 0.0435 | 1.0000 |
| 10:04:23 | AMD | NEGATIVE | short | 0.058800 | 0.0370 | 0.0436 | 1.0000 |
| 10:04:24 | AMD | NEGATIVE | short | 0.059200 | 0.0374 | 0.0436 | 1.0000 |
| 10:04:25 | AMD | NEGATIVE | short | 0.059600 | 0.0378 | 0.0437 | 1.0000 |
| 10:04:27 | AMD | NEGATIVE | short | 0.060300 | 0.0382 | 0.0443 | 1.0000 |
| 10:04:28 | AMD | NEGATIVE | short | 0.060400 | 0.0387 | 0.0437 | 1.0000 |
| 10:04:29 | AMD | NEGATIVE | short | 0.060400 | 0.0393 | 0.0430 | 1.0000 |
| 10:04:30 | AMD | NEGATIVE | short | 0.060400 | 0.0393 | 0.0432 | 1.0000 |
| 10:04:31 | AMD | NEGATIVE | short | 0.060600 | 0.0394 | 0.0433 | 1.0000 |


### Net Gamma Distribution

| Net Gamma Bin | Count | Mean SI | % of Total |
| --- | --- | --- | --- |
| < 0 |  381 | 0.3846 |  40.3% |
| 0 – 1K |    0 | 0.0000 |   0.0% |
| 1K – 10K |    0 | 0.0000 |   0.0% |
| 10K – 100K |    0 | 0.0000 |   0.0% |
| > 100K |  565 | 0.6238 |  59.7% |
