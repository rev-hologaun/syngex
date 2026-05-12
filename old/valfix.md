 Issues Found

1. NetGammaFilter is a NO-OP (Medium), The evaluate_signal() method in net_gamma_filter.py always returns True. The comments describe elaborate logic ("LONG signals allowed when price > flip", "SHORT signals allowed when price < flip"), but the actual implementation just returns True for both directions in both regimes. The transitioning flag does block signals, but the directional logic (price vs flip) is never actually used. This means the filter currently only blocks during transition — it doesn't actually filter by direction.


2. views/gamma_magnet.py Missing (Low), views/__init__.py imports GammaMagnetView and GammaProfileData from .gamma_magnet, but the file doesn't exist in the views/ directory. This is a broken import — from views import GammaMagnetView will raise ModuleNotFoundError.


3. Signal Symbol Assignment is Fragile (Low), In engine.py, the symbol assignment creates a new Signal object to add the symbol (because the dataclass is frozen):
signal = Signal(
    direction=signal.direction,
    confidence=signal.confidence,
    ...
)
This works but creates a new object each time. The id() used in conflict detection (_filter_signals uses id(s)) means the original and copy are different objects. If a signal handler holds a reference to the original signal, the conflict detection won't match it. Minor but worth noting.


4. RollingWindow Keys Are Hardcoded (Low), Strategy code references rolling window keys by string literal ("total_delta_5m", "volume_5m", "price_5m", "iv_skew_5m"). If a key is misspelled, it silently creates a new window instead of using the existing one. Consider a constants module.


5. TokenManager Path is Hardcoded (Low), token_manager.py defaults to ~/projects/tfresh2/token.json. This works for your setup but would break if tfresh2 is installed elsewhere or if the project is moved.


6. Layer 2 Strategy Count Mismatch (Very Low), SYNGEXStrats.md lists 5 Layer 2 strategies, but layer2/__init__.py exports only 4 (DeltaGammaSqueeze, DeltaVolumeExhaustion, CallPutFlowAsymmetry, IVGEXDivergence). The 5th — DeltaIVDivergence — is referenced in main.py's imports but may not be registered in the config-driven registration. Need to verify it's in strategies.yaml under layer2.


7. GEXCalculator OI is Relative (Noted, Not a Bug),The docstring notes that OI values are relative (default 1.0 per message), not absolute contract counts. This means GEX values are relative, not dollar-absolute. The set_open_interest() method exists for when real OI is fetched, but it's not currently called. For most strategies this is fine (ratios and thresholds still work), but the get_gamma_walls() threshold of $500K is applied to normalized GEX which may not be exactly $500K in dollar terms.


8. SignalTracker max_hold_seconds is Fixed (Very Low), The max_hold_seconds=900 (15 min) is hardcoded. Different strategies have different hold times (3-8 min for Theta-Burn, 1-4 hours for IV Skew Squeeze). A per-strategy hold time config would be more precise.

───

 Recommendations (Priority Order)

1. Fix NetGammaFilter — Implement the actual directional filtering logic (price vs flip, direction alignment). This is the master filter — it should actually filter.
2. Fix views/gamma_magnet.py — Either create the missing file or remove the broken import, then verify gamma_magnet is working as intended.
3. Add strategy constants — Extract hardcoded rolling window keys ("total_delta_5m", "volume_5m", etc.) into a constants module.
4. Per-strategy hold times — Move max_hold_seconds from a global to per-strategy config.
5. Verify DeltaIVDivergence registration — Confirm it's in strategies.yaml and registered by the config-driven system.
6. Use Real OI integration — When you add periodic OI fetching from the REST API, the set_open_interest() method is ready.
