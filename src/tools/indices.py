"""
Index-related tools for the MCP server.
Includes index constituents and industry utilities with clear, discoverable parameters.
"""
import logging
from typing import Optional, List

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_index_constituent_tool
from src.formatting.markdown_formatter import format_table_output

logger = logging.getLogger(__name__)


def register_index_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register index related tools with the MCP app.

    Args:
        app: The FastMCP app instance
        active_data_source: The active financial data source
    """

    @app.tool()
    def get_stock_industry(code: Optional[str] = None, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Get industry classification for a specific stock or all stocks on a date.

        Args:
            code: Optional stock code in Baostock format (e.g., 'sh.600000'). If None, returns all.
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.

        Returns:
            Markdown table with industry data or an error message.
        """
        log_msg = f"Tool 'get_stock_industry' called for code={code or 'all'}, date={date or 'latest'}"
        logger.info(log_msg)
        try:
            # Add date validation if desired
            df = active_data_source.get_stock_industry(code=code, date=date)
            logger.info(
                f"Successfully retrieved industry data for {code or 'all'}, {date or 'latest'}.")
            meta = {"code": code or "all", "as_of": date or "latest"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"Exception processing get_stock_industry: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_sz50_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetches the constituent stocks of the SZSE 50 Index for a given date.

        Args:
            date: Optional. The date in 'YYYY-MM-DD' format. If None, uses the latest available date.

        Returns:
            Markdown table with SZSE 50 constituent stocks or an error message.
        """
        return call_index_constituent_tool(
            "get_sz50_stocks",
            active_data_source.get_sz50_stocks,
            "SZSE 50",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_hs300_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch the constituent stocks of the CSI 300 Index for a given date.

        Args:
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.

        Returns:
            Markdown table with CSI 300 constituent stocks or an error message.
        """
        return call_index_constituent_tool(
            "get_hs300_stocks",
            active_data_source.get_hs300_stocks,
            "CSI 300",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_zz500_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch the constituent stocks of the CSI 500 Index for a given date.

        Args:
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.

        Returns:
            Markdown table with CSI 500 constituent stocks or an error message.
        """
        return call_index_constituent_tool(
            "get_zz500_stocks",
            active_data_source.get_zz500_stocks,
            "CSI 500",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_index_constituents(
        index: str,
        date: Optional[str] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        Get constituents for a major index.

        Args:
            index: One of 'hs300' (CSI 300), 'sz50' (SSE 50), 'zz500' (CSI 500).
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.
            limit: Max rows to return (pagination helper). Defaults to 250.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Table of index constituents in the requested format. Defaults to Markdown.

        Examples:
            - get_index_constituents(index='hs300')
            - get_index_constituents(index='sz50', date='2024-12-31', format='json', limit=100)
        """
        logger.info(
            f"Tool 'get_index_constituents' called index={index}, date={date or 'latest'}, limit={limit}, format={format}")
        try:
            key = (index or "").strip().lower()
            if key not in {"hs300", "sz50", "zz500"}:
                return "Error: Invalid index. Valid options are 'hs300', 'sz50', 'zz500'."

            if key == "hs300":
                df = active_data_source.get_hs300_stocks(date=date)
            elif key == "sz50":
                df = active_data_source.get_sz50_stocks(date=date)
            else:
                df = active_data_source.get_zz500_stocks(date=date)

            meta = {
                "index": key,
                "as_of": date or "latest",
            }
            return format_table_output(df, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_index_constituents: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def list_industries(date: Optional[str] = None, format: str = "markdown") -> str:
        """
        List distinct industries for a given date.

        Args:
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            One-column table of industries.
        """
        logger.info("Tool 'list_industries' called date=%s", date or "latest")
        try:
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            out = df[[col]].drop_duplicates().sort_values(by=col)
            out = out.rename(columns={col: "industry"})
            meta = {"as_of": date or "latest", "count": int(out.shape[0])}
            return format_table_output(out, format=format, max_rows=out.shape[0], meta=meta)
        except Exception as e:
            logger.exception("Exception processing list_industries: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_industry_members(
        industry: str,
        date: Optional[str] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        Get all stocks that belong to a given industry on a date.

        Args:
            industry: Exact industry name to filter by (see list_industries).
            date: Optional 'YYYY-MM-DD'. If None, uses the latest available date.
            limit: Max rows to return. Defaults to 250.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Table of stocks in the given industry.
        """
        logger.info(
            "Tool 'get_industry_members' called industry=%s, date=%s, limit=%s, format=%s",
            industry, date or "latest", limit, format,
        )
        try:
            if not industry or not industry.strip():
                return "Error: 'industry' is required. Call list_industries() to discover available values."
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            filtered = df[df[col] == industry].copy()
            meta = {"industry": industry, "as_of": date or "latest"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_industry_members: %s", e)
            return f"Error: An unexpected error occurred: {e}"
