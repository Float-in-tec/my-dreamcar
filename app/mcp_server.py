"""
Simple server MCP with FastMCP
References:
- Quickstart MCP (concepts and STDIO): https://modelcontextprotocol.io/quickstart/server
- FastMCP (decorator @mcp.tool; tools sync/async): https://gofastmcp.com/getting-started/quickstart
- Docs of MCP tools https://gofastmcp.com/servers/tools

Used sync functions to keep it simple (first time coding MCP)

Author: Yara
Created on: September 2025
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import func, and_
from fastmcp import FastMCP

from app.db_utils.db_connection import DBConn
from app.dao.car_market import DAOCar

mcp = FastMCP("mcp-server")


@mcp.tool(
    name="search_cars",
    description=(
        "Query cars DB with optional filters. "
        "Returns a list of dicts with: make, model, year, color, mileage, dollar_price and flags."
    ),
)
def search_cars(
    make: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    fuel: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    limit: Optional[int] = 20,
) -> List[Dict[str, Any]]:
    """
    MCP tool. Receives filters, queries the DB and returns results.
    """
    session = DBConn().connect()
    q = session.query(DAOCar)

    # Case-insensitive equals (robusto com ENUM no MySQL)
    if make:
        q = q.filter(func.lower(DAOCar.make) == make.lower())
    if year_min is not None:
        q = q.filter(DAOCar.year >= year_min)
    if year_max is not None:
        q = q.filter(DAOCar.year <= year_max)
    if fuel:
        q = q.filter(func.lower(DAOCar.fuel) == fuel.lower())
    if price_min is not None:
        q = q.filter(DAOCar.dollar_price >= price_min)
    if price_max is not None:
        q = q.filter(DAOCar.dollar_price <= price_max)

    # Limite razoável
    if not limit or limit <= 0 or limit > 100:
        limit = 20

    rows = q.limit(limit).all()

    def to_dict(obj: DAOCar) -> Dict[str, Any]:
        return {
            "id": getattr(obj, "id", None),  # útil em dev, não precisa exibir ao usuário final
            "make": getattr(obj, "make", None),
            "model": getattr(obj, "model", None),
            "year": getattr(obj, "year", None),
            "color": getattr(obj, "color", None),
            "fuel": getattr(obj, "fuel", None),
            "mileage": getattr(obj, "mileage", None),
            "dollar_price": getattr(obj, "dollar_price", None),
            "is_new": getattr(obj, "is_new", None),
            "is_automatic": getattr(obj, "is_automatic", None),
            "has_air_conditioning": getattr(obj, "has_air_conditioning", None),
            "has_charger_plug": getattr(obj, "has_charger_plug", None),
            "is_armored": getattr(obj, "is_armored", None),
            "has_bt_radio": getattr(obj, "has_bt_radio", None),
        }

    return [to_dict(r) for r in rows]


if __name__ == "__main__":
    mcp.run()
