"""
config/trade_guard.py — Safety guard for live environments

READ_ONLY = True  → blocks all order placement (live env safety)
READ_ONLY = False → allows live order placement (dev/test only)
"""

READ_ONLY = True  # KEEP TRUE IN LIVE ENVIRONMENTS
