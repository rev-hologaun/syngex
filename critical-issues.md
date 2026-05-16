# Critical Issues Log — v2.21 Series

**Purpose:** Track critical bugs found during strategy audit that require Hologaun review
**Created:** Sat 2026-05-16 02:11 PDT
**Last Updated:** Sat 2026-05-16 02:15 PDT (Batch 2)

---

## Critical Issues Found

| Strategy | Issue | Severity | Status | Recommendation |
|----------|-------|----------|--------|----------------|
| **STACKING** | `_compute_confidence()` uses undefined variables: `top_wall_size`, `decay` | Critical | 🔴 **Pending Fix** | Code does not compile - needs immediate fix |

---

## Critical Issue Definition

A **critical issue** is any bug that could cause:
- Wrong trade direction (LONG vs SHORT)
- Incorrect gamma regime requirements
- Position sizing errors
- Stop/target miscalculations
- **Code that doesn't compile**
- Data corruption or crashes

**Non-critical issues** (auto-fixed, logged here for reference):
- Unused parameters (`depth_score`, etc.)
- MIN_CONFIDENCE threshold (0.15 → 0.10)
- Docstring mismatches
- Missing bonus integrations

---

**Last Updated by:** Archon
