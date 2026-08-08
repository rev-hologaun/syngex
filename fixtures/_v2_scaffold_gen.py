#!/usr/bin/env python3
"""
_generate_v2_scaffold.py — Generate _v2 copies of all strategy modules.

For each strategy .py in strategies/layer1, layer2, layer3, full_data:
  1. Copy the file as <name>_v2.py
  2. Rename the class: GammaWallBounce -> GammaWallBounceV2
  3. Change strategy_id: "gamma_wall_bounce" -> "gamma_wall_bounce_v2"
  4. Update logger name to include V2
  5. Keep layer attribute unchanged

Does NOT modify originals.
"""

import os
import re
import sys
from pathlib import Path

STRATEGIES_ROOT = Path(__file__).parent.parent / "strategies"
LAYERS = ["layer1", "layer2", "layer3", "full_data"]

# Exclude non-strategy files (including previously generated _v2 files)
EXCLUDE = {"__init__.py", "engine.py", "signal.py", "signal_tracker.py",
           "analyzer.py", "rolling_keys.py", "volume_filter.py",
           "rolling_window.py"}


def find_strategy_files():
    """Find all strategy .py files across all layers, excluding _v2 files."""
    files = []
    for layer in LAYERS:
        layer_dir = STRATEGIES_ROOT / layer
        if not layer_dir.exists():
            print(f"WARNING: Layer directory not found: {layer_dir}", file=sys.stderr)
            continue
        for f in sorted(layer_dir.glob("*.py")):
            if f.name not in EXCLUDE and not f.name.endswith("_v2.py"):
                files.append(f)
    return files


def transform_line(line):
    """Apply all v2 transformations to a single line."""
    # 1. class ClassName( -> class ClassNameV2(
    m = re.match(r'^(\s*class\s+)([A-Za-z_]\w*)(\s*\()', line)
    if m:
        cls_name = m.group(2)
        if not cls_name.endswith("V2"):
            return m.group(1) + cls_name + "V2" + m.group(3)

    # 2. strategy_id = "foo" -> strategy_id = "foo_v2"
    m = re.match(r'^(\s*strategy_id\s*=\s")([A-Za-z_]\w*)(")', line)
    if m:
        name = m.group(2)
        if not name.endswith("_v2"):
            return m.group(1) + name + "_v2" + m.group(3)

    # 3. getLogger("Syngex.Strategies.ClassName")
    m = re.search(r'(logging\.getLogger\("Syngex\.Strategies\.)([A-Za-z_]\w*)(")', line)
    if m:
        name = m.group(2)
        if not name.endswith("V2"):
            return line[:m.start()] + m.group(1) + name + "V2" + m.group(3) + line[m.end():]

    return line


def generate_v2_file(src_path: Path) -> Path:
    """Read source file, apply transformations, write _v2 copy."""
    content = src_path.read_text()
    lines = content.split('\n')
    out_lines = [transform_line(l) for l in lines]
    out_content = '\n'.join(out_lines)

    # Determine output path
    layer_dir = src_path.parent
    stem = src_path.stem
    out_name = f"{stem}_v2.py"
    out_path = layer_dir / out_name

    out_path.write_text(out_content)
    return out_path


def main():
    strategy_files = find_strategy_files()
    print(f"Found {len(strategy_files)} strategy files to process.")

    created = []
    for src in strategy_files:
        out = generate_v2_file(src)
        created.append(out)
        print(f"  {src.name} -> {out.name}")

    print(f"\nGenerated {len(created)} _v2 strategy files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
