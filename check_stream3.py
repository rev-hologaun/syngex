#!/usr/bin/env python3
"""Compare request between check_stream and tradestation_client."""
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
    url = f"{base_url}/marketdata/stream/options/chains/TSLA"
    params = {"strikeProximity": 24}
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    # Test with same headers as tradestation_client
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    async with aiohttp.ClientSession() as session:
        print("Making request...")
        async with session.get(url, headers=headers, params=params, 
                               timeout=aiohttp.ClientTimeout(total=10)) as resp:
            print(f"Status: {resp.status}")
            print(f"Headers: {dict(resp.headers)}")
            print()
            
            count = 0
            async for line in resp.content:
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue
                count += 1
                if count <= 2:
                    obj = json.loads(line_str)
                    print(f"[{count}] Strikes: {obj.get('Strikes')}, Side: {obj.get('Side')}, Gamma: {obj.get('Gamma')}, OI: {obj.get('DailyOpenInterest')}")
            
            print(f"\nTotal lines: {count}")


if __name__ == "__main__":
    asyncio.run(main())
