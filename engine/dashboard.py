from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from engine.gex_calculator import GEXCalculator

class SyngexDashboard:
    """
    A Rich-based Terminal UI for Project Syngex.
    """

    def __init__(self, orchestrator: Any) -> None:
        self.orchestrator = orchestrator
        self.console = Console()
        self.layout = Layout()
        self._last_update_time = time.monotonic()
        
        # Initialize layout structure
        self._setup_layout()

    def _setup_layout(self) -> None:
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        self.layout["main"].split(
            Layout(name="left_panel", ratio=2),
            Layout(name="right_panel", ratio=1),
        )

    def _make_header(self) -> Panel:
        sym = self.orchestrator.symbol
        price = self.orchestrator._calculator.underlying_price
        status = "[green]RUNNING[/green]" if self.orchestrator._running else "[red]STOPPED[/red]"
        
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        grid.add_row(
            f"[bold cyan]SYNGEX PIPELINE[/bold cyan]",
            f"[bold white]{sym}[/bold white]",
            f"{status} | {time.strftime('%H:%M:%S')}",
        )
        
        return Panel(grid, style="white on blue")

    def _make_left_panel(self) -> Panel:
        # This panel will show the Gamma Walls and Top Strikes
        calc = self.orchestrator._calculator
        summary = calc.get_summary()
        
        # Gamma Walls
        walls = calc.get_gamma_walls(threshold=500000)
        wall_table = Table(title="[bold red]GAMMA WALLS[/bold red]", expand=True)
        wall_table.add_column("Strike", style="cyan")
        wall_table.add_column("Side", style="magenta")
        wall_table.add_column("GEX", justify="right")

        for w in walls[:10]:
            side_color = "green" if w["side"] == "call" else "red"
            wall_table.add_row(
                f"${w['strike']:.0f}",
                f"[{side_color}]{w['side'].upper()}[/{side_color}]",
                f"${abs(w['gex']):,.0f}",
            )

        # Top Strikes
        top_table = Table(title="[bold yellow]TOP STRIKES[/bold yellow]", expand=True)
        top_table.add_column("Strike", style="cyan")
        top_table.add_column("Net Gamma", justify="right")

        profile = calc.get_gamma_profile()
        top_list = sorted(
            profile["strikes"].items(),
            key=lambda x: abs(x[1]["net_gamma"]),
            reverse=True,
        )[:10]

        for strike, bucket in top_list:
            ng = bucket["net_gamma"]
            ng_color = "green" if ng >= 0 else "red"
            top_table.add_row(f"${strike:.0f}", f"[{ng_color}]{ng:,.2f}[/{ng_color}]")

        # Combine into a single panel or split further
        content = Text()
        content.append("--- GAMMA WALLS ---\n", style="dim")
        # Since we can't easily nest tables in a single Text object for layout, 
        # we'll use the layout structure better.
        
        # Re-purposing: Left panel shows Walls, Right panel shows Top Strikes
        return Panel(wall_table, title="Active Walls")

    def _make_right_panel(self) -> Panel:
        calc = self.orchestrator._calculator
        summary = calc.get_summary()
        
        table = Table(show_header=False, expand=True)
        table.add_row("Net Gamma", f"[bold]{summary['net_gamma']:+.2f}[/bold]")
        table.add_row("Price", f"${summary['underlying_price']:.2f}")
        table.add_row("Messages", str(summary['total_messages']))
        
        return Panel(table, title="Summary")

    def _make_footer(self) -> Panel:
        return Panel(Align.center("[dim]Press Ctrl+C to exit | Real-time GEX Stream[/dim]"), style="dim")

    async def run_live(self) -> None:
        """The loop that drives the UI updates."""
        with Live(self.layout, refresh_per_second=4, screen=True) as live:
            while self.orchestrator._running:
                # Update Header
                self.layout["header"].update(self._make_header())
                
                # Update Panels
                # Left side: Walls
                self.layout["left_panel"].update(self._make_left_panel())
                
                # Right side: Summary/Top Strikes
                # Let's make the right panel show the top strikes instead
                top_table = Table(title="[bold yellow]TOP STRIKES[/bold yellow]", expand=True)
                top_table.add_column("Strike", style="cyan")
                top_table.add_column("Net Gamma", justify="right")
                
                profile = self.orchestrator._calculator.get_gamma_profile()
                top_list = sorted(
                    profile["strikes"].items(),
                    key=lambda x: abs(x[1]["net_gamma"]),
                    reverse=True,
                )[:15]

                for strike, bucket in top_list:
                    ng = bucket["net_gamma"]
                    ng_color = "green" if ng >= 0 else "red"
                    top_table.add_row(f"${strike:.0f}", f"[{ng_color}]{ng:,.2f}[/{ng_color}]")
                
                self.layout["right_panel"].update(Panel(top_table, title="Top Strikes"))
                
                # Update Footer
                self.layout["footer"].update(self._make_footer())

                await asyncio.sleep(0.25)
