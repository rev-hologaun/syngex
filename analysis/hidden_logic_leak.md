# The Hidden Logic Leak in Syngex

## Overview
The "Hidden Logic Leak" is a systemic issue across the Syngex dealler-strategy suite where raw market data (strings) are treated as quantitative values (floats) without consistent casting. This results in "silent failures" where calculations are performed on descriptive "labels" rather than precise numbers.

## The "Symptom"
A signal may fail to fire not because the market logic is wrong, but because a mathematical operation is being performed on a string. This manifests as:
- **Label Overlap:** Subtracting two strings (e.g., "200" - "40") without casting, resulting in a "hidden" drift.
- **Precision Decay:** Multiplying a dealler's "size" (string) by a dealler's "gamma" (float), causing the signal to leak value if the string isn't cast.

## Examples from Analyzed Strategies
- **OBI_AF (`obi_aggression_flow`):** The epicenter. Calculates `(bid_size - ask_size) / total_depth`. If sizes are strings, this is essentially "Labels minus Labels divided by Label."
- **DELTA_VOL (`delta_volume_exhaustion`):** Occurs during the "Liquidity Vacuum" check. `bid_size / total` becomes a string-division problem.
- **CALL_PUT_FLOW (`call_put_flow_asymmetry`):** Summation of `OI * Gamma * Delta`. If $OI$ is a string, the product is a floating-point value masquerading as a dealler's total.
- **FLIP_BREAKOUT (`gamma_flip_breakout`):** The `flip_mid` is often a string `"420.5"`. Calculating the $\pm 1.5\%$ flip zone without casting results in a "fuzzy" boundary.

## The Solution: Three-Tier Casting Strategy
To eliminate the leak and orchestrate a fix, agent **Archon** should implement the following three-tier casting approach:

1. **The Immediate Cast (The Gatekeeper):** 
   Convert raw stream strings to floats immediately upon entry into the `rolling_data` window (e.g., `float(quote.bid_size)`).
2. **The Aggregation Cast (The Summary):** 
   Cast the result of summations (like Total GEX) back to floats to ensure that `sum(string_list)` doesn't lead to precision decay.
3. **The Final Polish (The Result):** 
   Convert the final `Signal` metadata back to a formatted string or float for human/agent interpretation.

**Goal:** Transition the system from a world of descriptive prose (strings) to a world of quantitative precision (floats).
