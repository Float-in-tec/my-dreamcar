"""
# Minimal. Adapting base class to be able to apply in our case.
# Author: Yara
# Created On: Sep 20205
"""
from __future__ import annotations
import argparse, asyncio, json
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.vendor.mcp_client_base import Server

CONFIG_PATH = Path(__file__).resolve().parent / "vendor" / "servers_config.json"

class CarClient:
    """
    Start Server via STDIO using config JSON.
    Expses search_cars(**filters) e normalizes returno to List[dict].
    """
    def __init__(self, server_name: str = "python", config_path: Path = CONFIG_PATH) -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            all_cfg = json.load(f)
        try:
            cfg = all_cfg["mcpServers"][server_name]
        except Exception as e:
            raise RuntimeError(f"Config inválida em {config_path}: {e}")
        self.server = Server(server_name, cfg)  # <- classe do vendor

    async def initialize(self) -> None:
        await self.server.initialize()

    async def close(self) -> None:
        await self.server.cleanup()

    async def list_tools(self) -> List[str]:
        tools = await self.server.list_tools()
        names = []
        for t in tools:
            name = getattr(t, "name", None) or (isinstance(t, dict) and t.get("name"))
            if name: names.append(str(name))
        return names

    async def search_cars(self, **filters: Any) -> List[Dict[str, Any]]:
        tools = await self.list_tools()
        if "search_cars" not in tools:
            raise RuntimeError("Failed to find 'search_cars' tools.")
        result = await self.server.execute_tool("search_cars", filters)
        return self._normalize_rows(result)

    def _normalize_rows(self, result: Any) -> List[Dict[str, Any]]:
        """
        Normalizes return as List[dict].
        """
        plain = getattr(result, "model_dump", lambda: result)()
        content = (plain or {}).get("content") if isinstance(plain, dict) else getattr(result, "content", None)
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "json" and isinstance(part.get("data"), list):
                    return part["data"]
                if isinstance(part, dict) and part.get("type") == "text":
                    try:
                        parsed = json.loads(part.get("text", ""))
                        if isinstance(parsed, list):
                            return parsed
                    except Exception:
                        pass

        if isinstance(plain, dict) and isinstance(plain.get("result"), list):
            return plain["result"]

        if isinstance(plain, list):
            return plain
        return []

# ---------------- CLI smoke test ----------------

async def _cli() -> None:
    p = argparse.ArgumentParser(description="MCP client (vendor Server) — smoke test")
    p.add_argument("--make")
    p.add_argument("--fuel", choices=["gasoline","flex","diesel","electric","hybrid"])
    p.add_argument("--year-min", type=int)
    p.add_argument("--year-max", type=int)
    p.add_argument("--price-min", type=int)
    p.add_argument("--price-max", type=int)
    p.add_argument("--limit", type=int, default=10)
    a = p.parse_args()

    filters = {k: v for k, v in {
        "make": a.make, "fuel": a.fuel, "year_min": a.year_min, "year_max": a.year_max,
        "price_min": a.price_min, "price_max": a.price_max, "limit": a.limit
    }.items() if v is not None}

    client = CarClient()
    try:
        await client.initialize()
        rows = await client.search_cars(**filters)
        if not rows:
            print("No results")
            return
        for i, car in enumerate(rows, 1):
            if not isinstance(car, dict):
                print(f"- {i}. {car}")
                continue
            price = car.get("dollar_price")
            price_fmt = f"US${int(price):,}".replace(",", ".") if isinstance(price, (int, float)) else price
            print(f"- {i}. {car.get('make')} {car.get('model')} {car.get('year')}, "
                  f"{car.get('color')}, {car.get('mileage')} km, {price_fmt}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(_cli())
