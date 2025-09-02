# app/mcp_client.py
# Cliente MCP mínimo (STDIO), sem LLM.

import asyncio
import json
import argparse
from typing import Any, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def parse_args():
    p = argparse.ArgumentParser(description="MCP client for search_cars")
    p.add_argument("--make")
    p.add_argument("--fuel", choices=["gasoline","flex","diesel","electric","hybrid"])
    p.add_argument("--year-min", type=int)
    p.add_argument("--year-max", type=int)
    p.add_argument("--price-min", type=int)
    p.add_argument("--price-max", type=int)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--debug-raw", action="store_true", help="print raw tool result")
    return p.parse_args()

def _to_plain(obj: Any) -> Any:
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    return obj

def _extract_from_content_items(items: Any):
    if items is None:
        return None
    norm = []
    for it in items:
        itp = _to_plain(it)
        norm.append(itp)
    for part in norm:
        if isinstance(part, dict):
            t = part.get("type")
            if t == "json":
                data = part.get("data")
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and isinstance(data.get("items"), list):
                    return data["items"]
            if t == "text":
                txt = part.get("text")
                if isinstance(txt, str):
                    try:
                        parsed = json.loads(txt)
                        if isinstance(parsed, list):
                            return parsed
                    except Exception:
                        pass
    return None

def extract_cars_from_result(result: Any):
    plain = _to_plain(result)
    if isinstance(plain, dict) and "content" in plain:
        cars = _extract_from_content_items(plain.get("content"))
        if isinstance(cars, list):
            return cars
    content = getattr(result, "content", None)
    if content is not None:
        cars = _extract_from_content_items(content)
        if isinstance(cars, list):
            return cars
    if isinstance(plain, list):
        return plain
    if isinstance(plain, str):
        try:
            parsed = json.loads(plain)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
    return []

async def call_search_cars(filters: Dict[str, Any], debug_raw: bool=False) -> Any:
    params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp_server"],  # inicia o server via stdio
    )
    async with stdio_client(params) as (rx, tx):
        async with ClientSession(rx, tx) as session:
            await session.initialize()
            # >>> Enviar no shape {"filters": {...}}
            result = await session.call_tool("search_cars", filters)
            if debug_raw:
                try:
                    print("[debug] raw result:", json.dumps(_to_plain(result), indent=2, ensure_ascii=False))
                except Exception as e:
                    print("[debug] raw result (repr):", repr(result), f"(dump error: {e})")
            return result

def main():
    args = parse_args()
    filters = {
        "make": args.make,
        "fuel": args.fuel,
        "year_min": args.year_min,
        "year_max": args.year_max,
        "price_min": args.price_min,
        "price_max": args.price_max,
        "limit": args.limit,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    print("[client] calling search_cars with:", filters)

    result = asyncio.run(call_search_cars(filters, debug_raw=args.debug_raw))
    cars = extract_cars_from_result(result)

    if not cars:
        print("Sem resultados.")
        return

    print("\nResultados:")
    for i, car in enumerate(cars, 1):
        if not isinstance(car, dict):
            print(f"- {i}. {car}")
            continue
        print(
            f"- {i}. {car.get('make')} {car.get('model')} {car.get('year')}, "
            f"{car.get('color')}, {car.get('mileage')} km, US${car.get('dollar_price')}"
        )

if __name__ == "__main__":
    main()
