"""FastMCP server entry point for psx-mcp-server.

Wires one shared PSXClient into the tool/resource layers and runs over stdio.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .client import PSXClient
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools

# One client for the whole process. Constructing httpx.AsyncClient here is safe
# (no running loop needed); the lifespan below closes it on shutdown.
_client = PSXClient()


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict]:
    try:
        yield {}
    finally:
        await _client.close()

port = int(os.environ.get("PORT", "10000"))
allowed_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if not allowed_host:
    raise RuntimeError(
        "RENDER_EXTERNAL_HOSTNAME must be set by the hosting provider."
    )

transport_security = TransportSecuritySettings(
    allowed_hosts=[allowed_host, f"{allowed_host}:*"],
    allowed_origins=[f"https://{allowed_host}"],
)

mcp = FastMCP(
    "psx",
    instructions=(
        "Live Pakistan Stock Exchange (PSX) data: quotes, intraday and end-of-day "
        "history, indices (KSE-100 and others), company fundamentals, dividends and "
        "announcements. Prices are in PKR; times are Pakistan Standard Time (UTC+5). "
        "If unsure of a ticker, call search_symbols first. Data is from the public "
        "PSX Data Portal and is informational only, not investment advice."
    ),
    lifespan=_lifespan,
    host="0.0.0.0",
    port=port,
    transport_security=transport_security,
)

register_tools(mcp, _client)
register_resources(mcp, _client)
register_prompts(mcp)



def main() -> None:
    """Run the MCP server over Streamable HTTP."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
