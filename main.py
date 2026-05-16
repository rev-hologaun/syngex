#!/usr/bin/env python3
"""
main.py — Syngex Orchestrator Entry Point

Clean, robust entry point for Project Syngex.
Delegates to orchestrator/lifecycle.py for the main orchestration logic.

Usage:
    python3 main.py TSLA              # stream mode (terminal logging)
    python3 main.py TSLA dashboard    # dashboard mode (starts Streamlit)
"""

from __future__ import annotations

import asyncio
import sys

from orchestrator.lifecycle import SyngexOrchestrator, main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
