"""
Market overview tools for the MCP server.
Includes trading calendar, stock list, and discovery helpers.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output

logger = logging.getLogger(__name__)


def register_market_overview_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register market overview tools with the MCP app.

    Args:
        app: The FastMCP app instance
        active_data_source: The active financial data source
    """

    @app.tool()
    def get_trade_dates(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch trading dates within a specified range.

        Args:
            start_date: Optional. Start date in 'YYYY-MM-DD' format. Defaults to 2015-01-01 if None.
            end_date: Optional. End date in 'YYYY-MM-DD' format. Defaults to the current date if None.

        Returns:
            Markdown table with 'is_trading_day' (1=trading, 0=non-trading).
        """
        logger.info(
            f"Tool 'get_trade_dates' called for range {start_date or 'default'} to {end_date or 'default'}")
        try:
            # Add date validation if desired
            df = active_data_source.get_trade_dates(
                start_date=start_date, end_date=end_date)
            logger.info("Successfully retrieved trade dates.")
            meta = {"start_date": start_date or "default", "end_date": end_date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_trade_dates: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_all_stock(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch a list of all stocks (A-shares and indices) and their trading status for a date.

        Args:
            date: Optional. The date in 'YYYY-MM-DD' format. If None, uses the current date.

        Returns:
            Markdown table listing stock codes and trading status (1=trading, 0=suspended).
        """
        logger.info(
            f"Tool 'get_all_stock' called for date={date or 'default'}")
        try:
            # Add date validation if desired
            df = active_data_source.get_all_stock(date=date)
            logger.info(
                f"Successfully retrieved stock list for {date or 'default'}.")
            meta = {"as_of": date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_all_stock: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def search_stocks(keyword: str, date: Optional[str] = None, limit: int = 50, format: str = "markdown") -> str:
        """
        Search stocks by code substring on a date.

        Args:
            keyword: Substring to match in the stock code (e.g., '600', '000001').
            date: Optional 'YYYY-MM-DD'. If None, uses current date.
            limit: Max rows to return. Defaults to 50.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Matching stock codes with their trading status.
        """
        logger.info("Tool 'search_stocks' called keyword=%s, date=%s, limit=%s, format=%s", keyword, date or "default", limit, format)
        try:
            if not keyword or not keyword.strip():
                return "Error: 'keyword' is required (substring of code)."
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            kw = keyword.strip().lower()
            # baostock returns 'code' like 'sh.600000'
            filtered = df[df["code"].str.lower().str.contains(kw, na=False)]
            meta = {"keyword": keyword, "as_of": date or "current"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing search_stocks: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_suspensions(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        List suspended stocks for a date.

        Args:
            date: Optional 'YYYY-MM-DD'. If None, uses current date.
            limit: Max rows to return. Defaults to 250.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Table of stocks where tradeStatus==0.
        """
        logger.info("Tool 'get_suspensions' called date=%s, limit=%s, format=%s", date or "current", limit, format)
        try:
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            # tradeStatus: '1' trading, '0' suspended
            if "tradeStatus" not in df.columns:
                return "Error: 'tradeStatus' column not present in data source response."
            suspended = df[df["tradeStatus"] == '0']
            meta = {"as_of": date or "current", "total_suspended": int(suspended.shape[0])}
            return format_table_output(suspended, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_suspensions: %s", e)
            return f"Error: An unexpected error occurred: {e}"
