#!/usr/bin/env python3
"""
Parameter Diff Analyzer for Syngex Strategies

Scans plan/ files for V1/original parameters and compares against current
strategy .py files to generate a comprehensive diff report.

Usage:
    python3 scripts/param_diff_analyzer.py
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Parameter:
    """Represents a single parameter with its value and metadata."""
    name: str
    value: Any
    source_file: str
    description: str = ""
    is_v1: bool = False  # True if from plan file (V1), False if from strategy file (V2.41)


@dataclass
class StrategyParams:
    """Parameters for a single strategy."""
    strategy_name: str
    layer: str
    v1_params: Dict[str, Parameter] = field(default_factory=dict)
    v2_params: Dict[str, Parameter] = field(default_factory=dict)
    plan_file: Optional[str] = None
    strategy_file: Optional[str] = None


def extract_yaml_params(content: str, source_file: str) -> Dict[str, Parameter]:
    """Extract parameters from YAML config blocks in plan files."""
    params = {}
    
    # Find YAML code blocks
    yaml_pattern = r'```yaml\s*\n(.*?)\n```'
    yaml_blocks = re.findall(yaml_pattern, content, re.DOTALL)
    
    for block in yaml_blocks:
        try:
            # Parse YAML
            data = yaml.safe_load(block)
            if isinstance(data, dict):
                # Flatten nested dicts (e.g., params: {param_name: value})
                if 'params' in data and isinstance(data['params'], dict):
                    for key, value in data['params'].items():
                        if not key.startswith('_') and value is not None:
                            # Skip MIN_CONFIDENCE as per user request
                            if key.upper() == 'MIN_CONFIDENCE':
                                continue
                            # Extract inline comment as description
                            match = re.search(rf'{re.escape(str(key))}:\s*(.+?)(?:\s*#\s*(.+))?$', block, re.MULTILINE)
                            desc = match.group(2).strip() if match and match.group(2) else ""
                            params[key] = Parameter(
                                name=key,
                                value=value,
                                source_file=source_file,
                                description=desc,
                                is_v1=True
                            )
                else:
                    # Top-level params
                    for key, value in data.items():
                        if not key.startswith('_') and value is not None:
                            # Skip MIN_CONFIDENCE as per user request
                            if key.upper() == 'MIN_CONFIDENCE':
                                continue
                            # Skip nested structures we can't handle
                            if isinstance(value, (dict, list)):
                                continue
                            # Extract inline comment as description
                            match = re.search(rf'{re.escape(str(key))}:\s*(.+?)(?:\s*#\s*(.+))?$', block, re.MULTILINE)
                            desc = match.group(2).strip() if match and match.group(2) else ""
                            params[key] = Parameter(
                                name=key,
                                value=value,
                                source_file=source_file,
                                description=desc,
                                is_v1=True
                            )
        except yaml.YAMLError:
            continue
    
    return params


def extract_inline_params(content: str, source_file: str) -> Dict[str, Parameter]:
    """Extract parameters from inline code blocks and constant definitions."""
    params = {}
    
    # Pattern 1: CONSTANT = value (Python-style constants)
    const_pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*([0-9.]+|"[^"]*"|\'[^\']*\')\s*(?:#\s*(.+))?$'
    for match in re.finditer(const_pattern, content, re.MULTILINE):
        name = match.group(1)
        value_str = match.group(2)
        desc = match.group(3).strip() if match.group(3) else ""
        
        # Skip MIN_CONFIDENCE
        if name.upper() == 'MIN_CONFIDENCE':
            continue
            
        # Skip KEY_ constants (rolling data keys)
        if name.startswith('KEY_'):
            continue
            
        # Parse value
        try:
            if value_str.startswith('"') or value_str.startswith("'"):
                value = value_str.strip('"\'')
            else:
                value = float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            continue
            
        params[name] = Parameter(
            name=name,
            value=value,
            source_file=source_file,
            description=desc,
            is_v1=False
        )
    
    # Pattern 2: Config-style params (param_name: value) - for plan files
    config_pattern = r'^\s+([a-z_][a-z0-9_]*):\s*([0-9.]+)\s*(?:#\s*(.+))?$'
    for match in re.finditer(config_pattern, content, re.MULTILINE):
        name = match.group(1)
        value_str = match.group(2)
        desc = match.group(3).strip() if match.group(3) else ""
        
        # Skip MIN_CONFIDENCE
        if name.upper() == 'MIN_CONFIDENCE':
            continue
            
        try:
            value = float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            continue
            
        params[name] = Parameter(
            name=name,
            value=value,
            source_file=source_file,
            description=desc,
            is_v1=True
        )
    
    return params


def scan_plan_files(plan_dir: Path) -> Dict[str, StrategyParams]:
    """Scan all plan files and extract V1 parameters."""
    strategies = {}
    
    for plan_file in plan_dir.glob('*.md'):
        with open(plan_file, 'r') as f:
            content = f.read()
        
        # Extract strategy name from filename
        filename = plan_file.stem
        strategy_name = None
        layer = None
        
        # Try to match strategy name from file content
        strategy_match = re.search(r'\*\*Strategy:\*\* `strategies/([^/]+)/([^`]+)\.py`', content)
        if strategy_match:
            layer = strategy_match.group(1)
            strategy_name = strategy_match.group(2)
        else:
            # Fallback: infer from filename
            # Remove version suffixes like _v2, _v3, etc.
            base_name = re.sub(r'_v\d+$', '', filename)
            strategy_name = base_name
        
        if not strategy_name:
            continue
        
        # Create or get strategy params
        key = strategy_name
        if key not in strategies:
            strategies[key] = StrategyParams(
                strategy_name=strategy_name,
                layer=layer or "unknown"
            )
        
        strategies[key].plan_file = str(plan_file)
        
        # Extract YAML params
        yaml_params = extract_yaml_params(content, str(plan_file))
        for name, param in yaml_params.items():
            strategies[key].v1_params[name] = param
        
        # Extract inline params
        inline_params = extract_inline_params(content, str(plan_file))
        for name, param in inline_params.items():
            # Only add if not already in YAML params
            if name not in strategies[key].v1_params:
                strategies[key].v1_params[name] = param
    
    return strategies


def scan_strategy_files(strategies_dir: Path, strategies: Dict[str, StrategyParams]) -> None:
    """Scan strategy Python files and extract current (V2.41) parameters."""
    
    layers = ['layer1', 'layer2', 'layer3', 'full_data']
    
    for layer in layers:
        layer_dir = strategies_dir / layer
        if not layer_dir.exists():
            continue
        
        for strategy_file in layer_dir.glob('*.py'):
            if strategy_file.name.startswith('__'):
                continue
                
            strategy_name = strategy_file.stem
            
            # Check if we have this strategy
            if strategy_name not in strategies:
                # Create entry for strategies without plan files
                strategies[strategy_name] = StrategyParams(
                    strategy_name=strategy_name,
                    layer=layer
                )
            
            strategies[strategy_name].layer = layer
            strategies[strategy_name].strategy_file = str(strategy_file)
            
            # Read strategy file
            with open(strategy_file, 'r') as f:
                content = f.read()
            
            # Extract constants
            const_params = extract_inline_params(content, str(strategy_file))
            for name, param in const_params.items():
                strategies[strategy_name].v2_params[name] = param


def calculate_change(v1_value: Any, v2_value: Any) -> Tuple[str, str]:
    """Calculate the change between V1 and V2 values."""
    try:
        v1_num = float(v1_value) if v1_value is not None else 0
        v2_num = float(v2_value) if v2_value is not None else 0
        
        if v1_num == 0 and v2_num == 0:
            return "0.00%", "same"
        elif v1_num == 0:
            return "N/A", "increased"
        elif v2_num == 0:
            return "N/A", "decreased"
        
        pct_change = ((v2_num - v1_num) / abs(v1_num)) * 100
        
        # Determine direction
        if pct_change > 5:
            direction = "more restrictive" if pct_change > 0 else "less restrictive"
        elif pct_change < -5:
            direction = "less restrictive" if pct_change < 0 else "more restrictive"
        else:
            direction = "similar"
        
        return f"{pct_change:+.1f}%", direction
        
    except (ValueError, TypeError):
        if str(v1_value) == str(v2_value):
            return "0.00%", "same"
        return "N/A", "changed"


def normalize_param_name(name: str) -> str:
    """Normalize parameter name for comparison (e.g., FLOW_THRESHOLD vs flow_threshold)."""
    # Convert to lowercase and replace common patterns
    name = name.lower()
    # Handle common naming patterns
    name = name.replace('_', '-')
    return name


def param_name_matches(name1: str, name2: str) -> bool:
    """Check if two parameter names match (handles case and underscore differences)."""
    # Direct match
    if name1.lower() == name2.lower():
        return True
    
    # Normalize both names
    n1 = name1.lower().replace('_', '-')
    n2 = name2.lower().replace('_', '-')
    
    if n1 == n2:
        return True
    
    # Handle common naming conventions
    # e.g., FLOW_THRESHOLD vs flow_threshold vs flow-threshold
    # e.g., STOP_PCT vs stop_pct vs stop-pct
    return False


def generate_report(strategies: Dict[str, StrategyParams], output_path: Path) -> None:
    """Generate the parameter diff report."""
    
    # Group strategies by layer
    by_layer = {
        'layer1': [],
        'layer2': [],
        'layer3': [],
        'full_data': [],
        'unknown': []
    }
    
    for strategy_name, params in strategies.items():
        layer = params.layer if params.layer in by_layer else 'unknown'
        by_layer[layer].append((strategy_name, params))
    
    # Sort strategies within each layer
    for layer in by_layer:
        by_layer[layer].sort(key=lambda x: x[0])
    
    # Calculate overall statistics
    total_v1 = 0
    total_v2 = 0
    total_added = 0
    total_removed = 0
    total_changed = 0
    strategies_with_changes = 0
    
    for strategy_name, params in strategies.items():
        v1_count = len(params.v1_params)
        v2_count = len(params.v2_params)
        
        # Filter out MIN_CONFIDENCE and KEY_ params
        v1_filtered = [k for k in params.v1_params.keys() 
                      if k.upper() != 'MIN_CONFIDENCE' and not k.startswith('KEY_')]
        v2_filtered = [k for k in params.v2_params.keys() 
                      if k.upper() != 'MIN_CONFIDENCE' and not k.startswith('KEY_')]
        
        v1_count = len(v1_filtered)
        v2_count = len(v2_filtered)
        
        added = len([k for k in v2_filtered if k not in params.v1_params])
        removed = len([k for k in v1_filtered if k not in params.v2_params])
        changed = len([k for k in v1_filtered if k in params.v2_params 
                      and params.v1_params[k].value != params.v2_params[k].value])
        
        total_v1 += v1_count
        total_v2 += v2_count
        total_added += added
        total_removed += removed
        total_changed += changed
        
        if added > 0 or removed > 0 or changed > 0:
            strategies_with_changes += 1
    
    report = []
    report.append("# Syngex Strategy Parameter Diff Report\n")
    report.append("**V1 (Original)** vs **V2.41 (Current)** Parameter Comparison\n")
    report.append(f"Generated: {Path(output_path).parent.absolute()}\n")
    report.append("\n## Overview\n")
    report.append(f"- **Total Strategies Analyzed:** {len(strategies)}\n")
    report.append(f"- **Strategies with Parameter Changes:** {strategies_with_changes}\n")
    report.append(f"- **Total V1 Parameters:** {total_v1}\n")
    report.append(f"- **Total V2.41 Parameters:** {total_v2}\n")
    report.append(f"- **Parameters Added:** +{total_added}\n")
    report.append(f"- **Parameters Removed:** {-total_removed if total_removed else 0}\n")
    report.append(f"- **Parameters Changed:** {total_changed}\n")
    report.append("\n---\n")
    
    layer_titles = {
        'layer1': 'Layer 1 (L1) - Foundation Strategies',
        'layer2': 'Layer 2 (L2) - Flow & Momentum Strategies',
        'layer3': 'Layer 3 (L3) - Advanced Convergence Strategies',
        'full_data': 'Full Data - Composite Strategies',
        'unknown': 'Unknown Layer'
    }
    
    for layer in ['layer1', 'layer2', 'layer3', 'full_data', 'unknown']:
        strategies_in_layer = by_layer[layer]
        if not strategies_in_layer:
            continue
        
        report.append(f"\n## {layer_titles.get(layer, layer)}\n")
        
        for strategy_name, params in strategies_in_layer:
            report.append(f"\n### {strategy_name}\n")
            
            if params.plan_file:
                report.append(f"**Plan File:** `{Path(params.plan_file).name}`\n")
            if params.strategy_file:
                report.append(f"**Strategy File:** `{Path(params.strategy_file).name}`\n")
            
            # Build mapping of normalized names to actual names
            v1_normalized = {normalize_param_name(k): k for k in params.v1_params.keys()}
            v2_normalized = {normalize_param_name(k): k for k in params.v2_params.keys()}
            
            # Combine all parameter names (using normalized for matching)
            all_normalized = set(v1_normalized.keys()) | set(v2_normalized.keys())
            
            # Filter out MIN_CONFIDENCE and KEY_ parameters
            all_normalized = {p for p in all_normalized 
                            if p != 'min-confidence' and not p.startswith('key-')}
            
            if not all_normalized:
                report.append("*No trading parameters found*\n")
                continue
            
            # Create table
            report.append("\n| Parameter | V1 (Original) | V2.41 (Current) | Change | Direction |\n")
            report.append("|-----------|---------------|-----------------|--------|-----------|\n")
            
            for norm_name in sorted(all_normalized):
                actual_v1_name = v1_normalized.get(norm_name)
                actual_v2_name = v2_normalized.get(norm_name)
                
                v1_param = params.v1_params.get(actual_v1_name) if actual_v1_name else None
                v2_param = params.v2_params.get(actual_v2_name) if actual_v2_name else None
                
                v1_val = v1_param.value if v1_param else "N/A"
                v2_val = v2_param.value if v2_param else "N/A"
                
                # Use the V2 name for display if available, otherwise V1
                display_name = actual_v2_name or actual_v1_name or norm_name
                
                # Calculate change
                if v1_param and v2_param:
                    change, direction = calculate_change(v1_param.value, v2_param.value)
                elif v1_param:
                    change, direction = "N/A", "removed"
                else:
                    change, direction = "N/A", "added"
                
                # Format values
                v1_str = str(v1_val) if v1_val != "N/A" else "_new_"
                v2_str = str(v2_val) if v2_val != "N/A" else "_removed_"
                
                # Highlight changes
                if change != "0.00%" and change != "N/A":
                    v1_str = f"**{v1_str}**"
                    v2_str = f"**{v2_str}**"
                
                report.append(f"| {display_name} | {v1_str} | {v2_str} | {change} | {direction} |\n")
            
            # Summary
            v1_count = len([p for p in all_normalized if p in v1_normalized])
            v2_count = len([p for p in all_normalized if p in v2_normalized])
            added = len([p for p in all_normalized if p not in v1_normalized])
            removed = len([p for p in all_normalized if p not in v2_normalized])
            changed = len([p for p in all_normalized 
                          if p in v1_normalized and p in v2_normalized 
                          and params.v1_params[v1_normalized[p]].value != params.v2_params[v2_normalized[p]].value])
            
            report.append(f"\n**Summary:** {v1_count} V1 params → {v2_count} V2 params | ")
            report.append(f"+{added} added | {-removed if removed else 0} removed | {changed} changed\n")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    # Add quick reference section
    report.append("\n---\n")
    report.append("\n## Quick Reference: Strategies with Parameter Changes\n")
    report.append("\n| Strategy | Layer | V1 → V2 | Added | Removed | Changed |\n")
    report.append("|----------|-------|---------|-------|---------|---------|\n")
    
    for strategy_name, params in sorted(strategies.items()):
        # Filter out MIN_CONFIDENCE and KEY_ params
        v1_filtered = [k for k in params.v1_params.keys() 
                      if k.upper() != 'MIN_CONFIDENCE' and not k.startswith('KEY_')]
        v2_filtered = [k for k in params.v2_params.keys() 
                      if k.upper() != 'MIN_CONFIDENCE' and not k.startswith('KEY_')]
        
        v1_count = len(v1_filtered)
        v2_count = len(v2_filtered)
        
        added = len([k for k in v2_filtered if k not in params.v1_params])
        removed = len([k for k in v1_filtered if k not in params.v2_params])
        changed = len([k for k in v1_filtered if k in params.v2_params 
                      and params.v1_params[k].value != params.v2_params[k].value])
        
        if added > 0 or removed > 0 or changed > 0:
            layer = params.layer or 'unknown'
            v1_str = str(v1_count) if v1_count > 0 else '_0_'
            v2_str = str(v2_count) if v2_count > 0 else '_0_'
            report.append(f"| {strategy_name} | {layer} | {v1_str} → {v2_str} | +{added} | {-removed if removed else 0} | {changed} |\n")
    
    # Rewrite the file with the quick reference
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    print(f"Report written to: {output_path}")


def main():
    """Main entry point."""
    # Paths
    syngex_dir = Path.home() / "projects" / "syngex"
    plan_dir = syngex_dir / "plan"
    strategies_dir = syngex_dir / "strategies"
    output_path = syngex_dir / "param_diff_report.md"
    
    print("Scanning plan files for V1 parameters...")
    strategies = scan_plan_files(plan_dir)
    print(f"Found {len(strategies)} strategies with plan files")
    
    print("Scanning strategy files for V2.41 parameters...")
    scan_strategy_files(strategies_dir, strategies)
    print(f"Total strategies analyzed: {len(strategies)}")
    
    print("Generating diff report...")
    generate_report(strategies, output_path)
    
    print("Done!")


if __name__ == "__main__":
    main()
