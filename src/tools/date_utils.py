"""
Date utility tools for the MCP server.
Convenience helpers around trading days and analysis timeframes.
"""
import logging
from datetime import datetime, timedelta
import calendar

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource

logger = logging.getLogger(__name__)


def register_date_utils_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register date utility tools with the MCP app.

    Args:
        app: The FastMCP app instance
        active_data_source: The active financial data source
    """

    @app.tool()
    def get_latest_trading_date() -> str:
        """
        Get the latest trading date up to today.

        Returns:
            The latest trading date in 'YYYY-MM-DD' format.
        """
        logger.info("Tool 'get_latest_trading_date' called")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            # Query within the current month (safe bound)
            start_date = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
            end_date = (datetime.now().replace(day=28)).strftime("%Y-%m-%d")

            df = active_data_source.get_trade_dates(
                start_date=start_date, end_date=end_date)

            valid_trading_days = df[df['is_trading_day'] == '1']['calendar_date'].tolist()

            latest_trading_date = None
            for dstr in valid_trading_days:
                if dstr <= today and (latest_trading_date is None or dstr > latest_trading_date):
                    latest_trading_date = dstr

            if latest_trading_date:
                logger.info("Latest trading date found: %s", latest_trading_date)
                return latest_trading_date
            else:
                logger.warning("No trading dates found before today, returning today's date")
                return today

        except Exception as e:
            logger.exception("Error determining latest trading date: %s", e)
            return datetime.now().strftime("%Y-%m-%d")

    @app.tool()
    def get_market_analysis_timeframe(period: str = "recent") -> str:
        """
        Get a market analysis timeframe label tuned for current calendar context.

        Args:
            period: One of 'recent' (default), 'quarter', 'half_year', 'year'.

        Returns:
            A human-friendly label plus ISO range, like "2025年1月-3月 (ISO: 2025-01-01 至 2025-03-31)".
        """
        logger.info(
            f"Tool 'get_market_analysis_timeframe' called with period={period}")

        now = datetime.now()
        end_date = now

        if period == "recent":
            if now.day < 15:
                if now.month == 1:
                    start_date = datetime(now.year - 1, 11, 1)
                    middle_date = datetime(now.year - 1, 12, 1)
                elif now.month == 2:
                    start_date = datetime(now.year, 1, 1)
                    middle_date = start_date
                else:
                    start_date = datetime(now.year, now.month - 2, 1)
                    middle_date = datetime(now.year, now.month - 1, 1)
            else:
                if now.month == 1:
                    start_date = datetime(now.year - 1, 12, 1)
                    middle_date = start_date
                else:
                    start_date = datetime(now.year, now.month - 1, 1)
                    middle_date = start_date

        elif period == "quarter":
            if now.month <= 3:
                start_date = datetime(now.year - 1, now.month + 9, 1)
            else:
                start_date = datetime(now.year, now.month - 3, 1)
            middle_date = start_date

        elif period == "half_year":
            if now.month <= 6:
                start_date = datetime(now.year - 1, now.month + 6, 1)
            else:
                start_date = datetime(now.year, now.month - 6, 1)
            middle_date = datetime(start_date.year, start_date.month + 3, 1) if start_date.month <= 9 else \
                datetime(start_date.year + 1, start_date.month - 9, 1)

        elif period == "year":
            start_date = datetime(now.year - 1, now.month, 1)
            middle_date = datetime(start_date.year, start_date.month + 6, 1) if start_date.month <= 6 else \
                datetime(start_date.year + 1, start_date.month - 6, 1)
        else:
            if now.month == 1:
                start_date = datetime(now.year - 1, 12, 1)
            else:
                start_date = datetime(now.year, now.month - 1, 1)
            middle_date = start_date

        def get_month_end_day(year, month):
            return calendar.monthrange(year, month)[1]

        end_day = min(get_month_end_day(end_date.year, end_date.month), end_date.day)
        end_iso_date = f"{end_date.year}-{end_date.month:02d}-{end_day:02d}"

        start_iso_date = f"{start_date.year}-{start_date.month:02d}-01"

        if start_date.year != end_date.year:
            date_range = f"{start_date.year}年{start_date.month}月-{end_date.year}年{end_date.month}月"
        elif middle_date.month != start_date.month and middle_date.month != end_date.month:
            date_range = f"{start_date.year}年{start_date.month}月-{middle_date.month}月-{end_date.month}月"
        elif start_date.month != end_date.month:
            date_range = f"{start_date.year}年{start_date.month}月-{end_date.month}月"
        else:
            date_range = f"{start_date.year}年{start_date.month}月"

        result = f"{date_range} (ISO: {start_iso_date} to {end_iso_date})"
        logger.info(f"Generated market analysis timeframe: {result}")
        return result

    @app.tool()
    def is_trading_day(date: str) -> str:
        """
        Check whether a given date is a trading day.

        Args:
            date: 'YYYY-MM-DD'.

        Returns:
            'Yes' or 'No'.

        Examples:
            - is_trading_day('2025-01-03')
        """
        logger.info("Tool 'is_trading_day' called date=%s", date)
        try:
            df = active_data_source.get_trade_dates(start_date=date, end_date=date)
            if df is None or df.empty:
                return "No"
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            val = str(df.iloc[0][flag_col])
            return "Yes" if val == '1' else "No"
        except Exception as e:
            logger.exception("Exception processing is_trading_day: %s", e)
            return f"Error: {e}"

    @app.tool()
    def previous_trading_day(date: str) -> str:
        """
        Get the previous trading day before a given date.

        Args:
            date: 'YYYY-MM-DD'.

        Returns:
            The previous trading day in 'YYYY-MM-DD'. If none found nearby, returns input date.
        """
        logger.info("Tool 'previous_trading_day' called date=%s", date)
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            start = (d - timedelta(days=30)).strftime("%Y-%m-%d")
            end = date
            df = active_data_source.get_trade_dates(start_date=start, end_date=end)
            if df is None or df.empty:
                return date
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            day_col = 'calendar_date' if 'calendar_date' in df.columns else df.columns[0]
            candidates = df[(df[flag_col] == '1') & (df[day_col] < date)].sort_values(by=day_col)
            if candidates.empty:
                return date
            return str(candidates.iloc[-1][day_col])
        except Exception as e:
            logger.exception("Exception processing previous_trading_day: %s", e)
            return f"Error: {e}"

    @app.tool()
    def next_trading_day(date: str) -> str:
        """
        Get the next trading day after a given date.

        Args:
            date: 'YYYY-MM-DD'.

        Returns:
            The next trading day in 'YYYY-MM-DD'. If none found nearby, returns input date.
        """
        logger.info("Tool 'next_trading_day' called date=%s", date)
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            start = date
            end = (d + timedelta(days=30)).strftime("%Y-%m-%d")
            df = active_data_source.get_trade_dates(start_date=start, end_date=end)
            if df is None or df.empty:
                return date
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            day_col = 'calendar_date' if 'calendar_date' in df.columns else df.columns[0]
            candidates = df[(df[flag_col] == '1') & (df[day_col] > date)].sort_values(by=day_col)
            if candidates.empty:
                return date
            return str(candidates.iloc[0][day_col])
        except Exception as e:
            logger.exception("Exception processing next_trading_day: %s", e)
            return f"Error: {e}"

