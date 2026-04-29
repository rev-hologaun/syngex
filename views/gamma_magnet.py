"""
Gamma Magnet View
─────────────────
Displays a real-time Gamma Profile heatmap with price overlay.

Uses the GEXCalculator to process option chain data and renders:
  - A color-coded gamma profile heatmap (bars per strike)
  - Current price indicator with distance to key gamma levels
  - GEX regime summary (positive/negative/neutral)

Designed as a modular view component — accepts data via `update()`.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich import box

from engine.gex_calculator import GEXResult, OptionExposure, analyze_gex

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONTRACT_MULTIPLIER = 100
HEATMAP_WIDTH = 60
HEATMAP_HEIGHT = 12
BAR_CHAR = "█"
PRICE_MARKER = "▸"
HEAT_COLORS = {
    "strong_positive": "#22c55e",  # green-500
    "positive":       "#86efac",  # green-300
    "neutral":        "#94a3b8",  # slate-400
    "negative":       "#fca5a5",  # red-300
    "strong_negative":"#ef4444",  # red-500
}

# ---------------------------------------------------------------------------
# Data pipeline
# ---------------------------------------------------------------------------

@dataclass
class GammaProfileData:
    """Raw data for the gamma magnet view."""
    symbol: str = ""
    current_price: float = 0.0
    gex_result: GEXResult | None = None
    timestamp: float = field(default_factory=time.time)
    update_count: int = 0

    @property
    def regime(self) -> str:
        if self.gex_result is None:
            return "NO DATA"
        analysis = analyze_gex(self.gex_result)
        return analysis["regime"]

    @property
    def total_gex(self) -> float:
        if self.gex_result is None:
            return 0.0
        return self.gex_result.total_gex

    @property
    def call_gex(self) -> float:
        if self.gex_result is None:
            return 0.0
        return self.gex_result.call_gex

    @property
    def put_gex(self) -> float:
        if self.gex_result is None:
            return 0.0
        return self.gex_result.put_gex

    @property
    def top_strikes(self) -> list[tuple[float, float]]:
        if self.gex_result is None:
            return []
        return self.gex_result.top_strikes


# ---------------------------------------------------------------------------
# Heatmap builder
# ---------------------------------------------------------------------------

def _build_heatmap(
    by_strike: dict[float, float],
    current_price: float,
    width: int = HEATMAP_WIDTH,
    height: int = HEATMAP_HEIGHT,
) -> Panel:
    """Build a gamma profile heatmap panel.

    Strikes are mapped to grid columns. Gamma magnitude maps to bar length.
    Color encodes sign: green = positive GEX, red = negative GEX.
    A price marker shows the current price position.
    """
    if not by_strike:
        return Panel(
            Text("No gamma data available", style="dim italic"),
            title="Gamma Profile Heatmap",
            subtitle="Waiting for option chain data…",
            box=box.ROUNDED,
        )

    strikes = sorted(by_strike.keys())
    gex_values = [by_strike[s] for s in strikes]
    min_gex = min(gex_values)
    max_gex = max(gex_values)
    gex_range = max_gex - min_gex if max_gex != min_gex else 1.0

    # Determine visible range (±20% around current price, or full range if price missing)
    if current_price > 0:
        price_span = current_price * 0.25
        lo, hi = current_price - price_span, current_price + price_span
    else:
        lo, hi = min(strikes) - 5, max(strikes) + 5

    visible = [(s, g) for s, g in zip(strikes, gex_values) if lo <= s <= hi]
    if not visible:
        visible = list(zip(strikes, gex_values))[:20]

    visible_strikes = [s for s, _ in visible]
    visible_gex = [g for _, g in visible]

    # Map strikes to column indices
    strike_min = min(visible_strikes)
    strike_max = max(visible_strikes)
    strike_span = strike_max - strike_min if strike_max != strike_min else 1.0

    # Build grid
    grid_lines: list[str] = []
    for row in range(height):
        line_parts: list[str] = []
        for col in range(width):
            # Map column to strike
            frac = col / (width - 1) if width > 1 else 0.5
            mapped_strike = strike_min + frac * strike_span

            # Find closest visible strike
            closest = min(visible_strikes, key=lambda s: abs(s - mapped_strike))
            idx = visible_strikes.index(closest)
            gex_val = visible_gex[idx]

            # Determine bar length (proportional to magnitude)
            if gex_val >= 0:
                bar_len = int((gex_val / gex_range) * (width // 2))
                bar_len = max(0, min(bar_len, width // 2))
            else:
                bar_len = int((abs(gex_val) / gex_range) * (width // 2))
                bar_len = max(0, min(bar_len, width // 2))

            # Determine color
            if gex_val > gex_range * 0.5:
                color = HEAT_COLORS["strong_positive"]
            elif gex_val > 0:
                color = HEAT_COLORS["positive"]
            elif gex_val < -gex_range * 0.5:
                color = HEAT_COLORS["strong_negative"]
            elif gex_val < 0:
                color = HEAT_COLORS["negative"]
            else:
                color = HEAT_COLORS["neutral"]

            # Check if this is the price marker column
            is_price = abs(mapped_strike - current_price) < strike_span * 0.05 if current_price > 0 else False

            if is_price and row == height // 2:
                line_parts.append(f"[bold yellow]{PRICE_MARKER}[/]")
            elif row == height // 2 and gex_val != 0:
                # Price row — draw the bar
                if gex_val >= 0:
                    line_parts.append(f"[{color}]{BAR_CHAR * bar_len}[/]")
                else:
                    line_parts.append(f"[{color}]{BAR_CHAR * bar_len}[/]")
            elif gex_val != 0:
                if gex_val >= 0:
                    line_parts.append(f"[{color}]{BAR_CHAR * bar_len}[/]")
                else:
                    line_parts.append(f"[{color}]{BAR_CHAR * bar_len}[/]")
            else:
                line_parts.append(" ")
        grid_lines.append("".join(line_parts))

    # Strike labels
    label_row = " " * (width // 4)
    label_row += f"[dim]${strike_min:.0f}[/]"
    label_row += " " * (width // 2 - 6)
    label_row += f"[dim]${strike_max:.0f}[/]"

    title = f"  Gamma Profile Heatmap — {width} strikes visible"
    if current_price > 0:
        title += f"  |  Price: [bold yellow]${current_price:.2f}[/]"

    return Panel(
        "\n".join(grid_lines) + "\n" + label_row,
        title=title,
        subtitle=f"Scale: left=put GEX  |  right=call GEX  |  center=current price",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# Price overlay panel
# ---------------------------------------------------------------------------

def _build_price_overlay(data: GammaProfileData) -> Panel:
    """Build a price overlay panel showing key gamma levels relative to current price."""
    if data.gex_result is None:
        return Panel(
            Text("Waiting for data…", style="dim"),
            title="Price Overlay",
            box=box.ROUNDED,
        )

    lines: list[str] = []
    price = data.current_price

    # Key levels from top strikes
    lines.append("[bold]Key Gamma Levels:[/bold]")
    lines.append("")

    for strike, gex in data.top_strikes[:8]:
        diff = strike - price
        pct = (diff / price * 100) if price > 0 else 0
        direction = "▲" if diff > 0 else "▼" if diff < 0 else "●"
        gex_sign = "+" if gex > 0 else ""

        # Color code the level
        if abs(pct) < 1:
            style = "bold yellow"
        elif abs(pct) < 3:
            style = "cyan"
        else:
            style = "dim"

        lines.append(
            f"  {direction}  [bold]{gex_sign}${strike:.0f}[/]  "
            f"GEX: {gex:+,.0f}  |  [{style}]({pct:+.1f}%) from price[/]"
        )

    # Regime box
    regime = data.regime
    regime_color = {
        "POSITIVE GAMMA": "green",
        "NEGATIVE GAMMA": "red",
        "NEUTRAL GAMMA": "yellow",
        "NO DATA": "dim",
    }.get(regime, "white")

    lines.append("")
    lines.append(f"[bold {regime_color}]▸ REGIME: {regime}[/]")

    analysis = analyze_gex(data.gex_result) if data.gex_result else {}
    if analysis:
        lines.append(f"  {analysis.get('behavior', '')}")

    return Panel(
        "\n".join(lines),
        title="Price Overlay & Key Levels",
        subtitle=f"Updated: {time.strftime('%H:%M:%S')}",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# Summary stats panel
# ---------------------------------------------------------------------------

def _build_summary_panel(data: GammaProfileData) -> Panel:
    """Build a summary stats panel."""
    lines: list[str] = []
    lines.append("[bold]GEX Summary[/bold]")
    lines.append("─" * 30)

    if data.gex_result is None:
        lines.append("[dim]No data yet…[/]")
    else:
        lines.append(f"  Total GEX:    [bold]{data.total_gex:+,.0f}[/]")
        lines.append(f"  Call GEX:     [green]{data.call_gex:+,.0f}[/]")
        lines.append(f"  Put GEX:      [red]{data.put_gex:+,.0f}[/]")
        lines.append(f"  Options:      {len(data.gex_result.options)}")
        lines.append(f"  Strikes:      {len(data.gex_result.by_strike)}")
        lines.append(f"  Expirations:  {len(data.gex_result.by_expiration)}")

    lines.append("")
    lines.append(f"  Updates: {data.update_count}")
    lines.append(f"  Last:    {time.strftime('%H:%M:%S')}")

    return Panel(
        "\n".join(lines),
        title=f"SYNGEX — {data.symbol or 'SYMBOL'}",
        subtitle="Gamma Magnet View",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# View renderer
# ---------------------------------------------------------------------------

class GammaMagnetView:
    """A modular dashboard view that renders the gamma profile heatmap.

    Usage:
        view = GammaMagnetView()
        view.update(GammaProfileData(symbol="SPY", current_price=550.0, gex_result=...))
        # Then use view.render() or view.start_live() for real-time updates
    """

    def __init__(self, console: Console | None = None):
        self._console = console or Console()
        self._data = GammaProfileData()
        self._live: Live | None = None

    @property
    def data(self) -> GammaProfileData:
        return self._data

    def update(self, gex_result: GEXResult, current_price: float = 0.0) -> None:
        """Update view data from a GEXResult and current price."""
        self._data.symbol = gex_result.symbol or self._data.symbol
        self._data.current_price = current_price or self._data.current_price
        self._data.gex_result = gex_result
        self._data.timestamp = time.time()
        self._data.update_count += 1

    def update_from_events(
        self,
        events: list[dict[str, Any]],
        current_price: float = 0.0,
    ) -> None:
        """Convenience: process raw option chain events into GEX and update."""
        from engine.gex_calculator import calculate_gex
        gex_result = calculate_gex(events)
        gex_result.symbol = self._data.symbol
        self.update(gex_result, current_price)

    def render(self) -> Panel:
        """Render the full view as a Rich Panel."""
        heatmap = _build_heatmap(
            self._data.gex_result.by_strike if self._data.gex_result else {},
            self._data.current_price,
        )
        price_overlay = _build_price_overlay(self._data)
        summary = _build_summary_panel(self._data)

        # Layout: heatmap on top, price overlay + summary side by side
        layout = Layout(name="root")
        layout.split(
            Layout(heatmap, ratio=2, name="heatmap"),
            Layout(name="bottom"),
        )
        layout["bottom"].split_row(
            Layout(price_overlay, ratio=1, name="price"),
            Layout(summary, ratio=1, name="summary"),
        )

        return Panel(
            layout,
            title=f"  🐙 SYNGEX Gamma Magnet — {self._data.symbol}  ",
            subtitle=f"Updated {time.strftime('%H:%M:%S')}  |  "
                     f"Regime: {self._data.regime}  |  "
                     f"Total GEX: {self._data.total_gex:+,.0f}",
            box=box.DOUBLE,
        )

    def start_live(self, fps: int = 1) -> None:
        """Start a live-updating terminal view (blocking)."""
        with Live(
            self.render(),
            console=self._console,
            refresh_per_second=fps,
            screen=False,
        ) as live:
            self._live = live
            try:
                while True:
                    live.update(self.render(), refresh=True)
                    time.sleep(1.0 / fps)
            except KeyboardInterrupt:
                pass
            finally:
                self._live = None

    def stop_live(self) -> None:
        """Stop the live view."""
        if self._live:
            self._live.stop()
            self._live = None
