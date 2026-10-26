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


@@ -46,8 +46,23 @@ async def _lifespan(_server: FastMCP) -> AsyncIterator[dict]:


def main() -> None:
    """Console-script entry point. Runs the MCP server over stdio."""
    mcp.run()
    """Run the MCP server over Streamable HTTP."""
    port = int(os.environ.get("PORT", "10000"))
    allowed_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if not allowed_host:
        raise RuntimeError(
            "RENDER_EXTERNAL_HOSTNAME must be set by the hosting provider."
        )

    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.settings.transport_security = TransportSecuritySettings(
        allowed_hosts=[allowed_host, f"{allowed_host}:*"],
        allowed_origins=[f"https://{allowed_host}"],
    )

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
