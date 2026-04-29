#!/usr/bin/env python3
"""Dump full structure of first few option chain messages."""
import asyncio
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.expanduser("~/projects/tfresh2/token.json")

async def main():
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    token = token_data["access_token"]
    
    import aiohttp
    
    base_url = "https://sim-api.tradestation.com/v3"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    url = f"{base_url}/marketdata/stream/options/chains/TSLA"
    params = {"strikeProximity": 24}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            count = 0
            buffer = ""
            async for line in resp.content:
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue
                count += 1
                try:
                    obj = json.loads(line_str)
                    print(f"=== Message {count} ===")
                    print(json.dumps(obj, indent=2, default=str))
                    print()
                except json.JSONDecodeError:
                    print(f"RAW: {line_str[:200]}")
                if count >= 3:
                    break


if __name__ == "__main__":
    asyncio.run(main())
