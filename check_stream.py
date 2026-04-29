#!/usr/bin/env python3
"""Check what the TradeStation option chain stream actually returns."""
import asyncio
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.expanduser("~/projects/tfresh2/token.json")

async def main():
    # Load token
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
    
    print(f"Connecting to: {url}")
    print(f"Params: {params}")
    print()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            print(f"Status: {resp.status}")
            count = 0
            buffer = ""
            async for line in resp.content:
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue
                count += 1
                try:
                    obj = json.loads(line_str)
                    print(f"[{count}] {json.dumps(obj, default=str)[:400]}")
                except json.JSONDecodeError:
                    print(f"[{count}] RAW: {line_str[:200]}")
                if count >= 5:
                    break
            
            if count == 0:
                print("No lines received from stream.")
                # Try reading as one-shot
                body = await resp.read()
                print(f"\nFull body ({len(body)} bytes):")
                print(body.decode("utf-8", errors="replace")[:2000])


if __name__ == "__main__":
    asyncio.run(main())
