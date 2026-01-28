import asyncio
import logging
import os

import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Currency Exchange server")

@mcp.tool()
def get_exchange_rate(
    currency_from: str = "EUR",
    currency_to: str = "GBP",
    currency_date: str = "latest",
):
    """Get exchange rate on a given date.

    Args:
        currency_from: The currency to convert from (e.g., "EUR").
        currency_to: The currency to convert to (e.g., "GBP").
        currency_date: The date for the exchange rate or "latest". Defaults to "latest".

    Returns:
        A dictionary containing the exchange rate data, or an error message if the request fails.
    """
    try:
        response = httpx.get(
            f"https://api.frankfurter.dev/v1/{currency_date}?base={currency_from}&symbols={currency_to}",
        )
        response.raise_for_status()

        return response.json()
    except httpx.HTTPError as e:
        return {f"Ups...  something went wrong. {e}"}
    except ValueError:
        return {"Invalid JSON response from API."}


if __name__ == "__main__":
    PORT = int(os.getenv("MCP_SERVER_CURRENCY_CONVERTER_PORT", 5555))

    logger.info(f"MCP server started on port {PORT}")
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=PORT,
        )
    )