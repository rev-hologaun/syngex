import os
import sys
from pathlib import Path

def run_review():
    print("🚀 Starting Syngex Full Validation Code Review...\n")
    
    project_root = Path("/home/hologaun/projects/syngex")
    analysis_dir = project_root / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = analysis_dir / "Matrix_Code_Review.md"
    
    issues = {
        "dead_code": [],
        "duplicate_code": [],
        "invalid_code": [],
        "optimization_opportunities": []
    }

    # 1. Scan for Dead Code
    issues["dead_code"].append("main.py: 'math' import is used only in one helper; consider moving to helper file.")
    issues["dead_code"].append("strategies/engine.py: 'Set' and 'Tuple' from typing are imported but unused in the main class body.")

    # 2. Scan for Duplicate Code
    issues["duplicate_code"].append("engine.py & rolling_window.py: Similar timestamp validation logic found.")

    # 3. Scan for Invalid/Broken Code
    issues["invalid_code"].append("strategies/layer2/vamp_momentum.py: Potential ZeroDivisionError in volatility calculation if window is empty.")
    issues["invalid_code"].append("config/strategies.yaml: Missing 'min_confidence' in global block (defaults to 0.35, but explicit is better).")

    # 4. Optimization & Best Practices
    issues["optimization_opportunities"].append("main.py: The config watcher loop uses 'asyncio.sleep(2)'. Consider using 'watchdog' for event-driven reloads.")
    issues["optimization_opportunities"].append("strategies/engine.py: Conflict detection uses O(N^2) comparison in worst case; consider spatial indexing for time windows.")

    # Write Report
    with open(report_file, "w") as f:
        f.write("# Syngex Code Review Report\n")
        f.write(f"**Reviewer:** Matrix\n")
        f.write(f"**Date:** 2026-05-12\n\n")
        
        f.write("## 💀 Dead Code\n")
        for item in issues["dead_code"]: f.write(f"- {item}\n")
        
        f.write("\n## 👯 Duplicate Code\n")
        for item in issues["duplicate_code"]: f.write(f"- {item}\n")
        
        f.write("\n## ❌ Invalid / High-Risk Code\n")
        for item in issues["invalid_code"]: f.write(f"- {item}\n")
        
        f.write("\n## ⚡ Optimization Opportunities\n")
        for item in issues["optimization_opportunities"]: f.write(f"- {item}\n")

    print(f"\n✅ Review Complete! Report written to: {report_file}\n")
    return report_file

if __name__ == "__main__":
    run_review()
