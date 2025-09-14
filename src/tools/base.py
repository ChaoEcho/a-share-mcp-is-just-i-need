"""
Base utilities for MCP tools.
Shared helpers for calling data sources with consistent formatting and errors.
"""
import logging
from typing import Callable, Optional
import pandas as pd

from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output
from src.data_source_interface import NoDataFoundError, LoginError, DataSourceError

logger = logging.getLogger(__name__)


def call_financial_data_tool(
    tool_name: str,
    # Pass the bound method like active_data_source.get_profit_data
    data_source_method: Callable,
    data_type_name: str,
    code: str,
    year: str,
    quarter: int,
    *,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    """
    Helper function to reduce repetition for financial data tools

    Args:
        tool_name: Name of the tool for logging
        data_source_method: Method to call on the data source
        data_type_name: Type of financial data (for logging)
        code: Stock code
        year: Year to query
        quarter: Quarter to query

    Returns:
        Markdown formatted string with results or error message
    """
    logger.info(f"Tool '{tool_name}' called for {code}, {year}Q{quarter}")
    try:
        # Basic validation
        if not year.isdigit() or len(year) != 4:
            logger.warning(f"Invalid year format requested: {year}")
            return f"Error: Invalid year '{year}'. Please provide a 4-digit year."
        if not 1 <= quarter <= 4:
            logger.warning(f"Invalid quarter requested: {quarter}")
            return f"Error: Invalid quarter '{quarter}'. Must be between 1 and 4."

        # Call the appropriate method on the already instantiated active_data_source
        df = data_source_method(code=code, year=year, quarter=quarter)
        logger.info(
            f"Successfully retrieved {data_type_name} data for {code}, {year}Q{quarter}.")
        meta = {"code": code, "year": year, "quarter": quarter, "dataset": data_type_name}
        return format_table_output(df, format=format, max_rows=limit, meta=meta)

    except NoDataFoundError as e:
        logger.warning(f"NoDataFoundError for {code}, {year}Q{quarter}: {e}")
        return f"Error: {e}"
    except LoginError as e:
        logger.error(f"LoginError for {code}: {e}")
        return f"Error: Could not connect to data source. {e}"
    except DataSourceError as e:
        logger.error(f"DataSourceError for {code}: {e}")
        return f"Error: An error occurred while fetching data. {e}"
    except ValueError as e:
        logger.warning(f"ValueError processing request for {code}: {e}")
        return f"Error: Invalid input parameter. {e}"
    except Exception as e:
        logger.exception(
            f"Unexpected Exception processing {tool_name} for {code}: {e}")
        return f"Error: An unexpected error occurred: {e}"


def call_macro_data_tool(
    tool_name: str,
    data_source_method: Callable,
    data_type_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    *,
    limit: int = 250,
    format: str = "markdown",
    **kwargs  # For extra params like year_type
) -> str:
    """
    Helper function for macroeconomic data tools

    Args:
        tool_name: Name of the tool for logging
        data_source_method: Method to call on the data source
        data_type_name: Type of data (for logging)
        start_date: Optional start date
        end_date: Optional end date
        **kwargs: Additional keyword arguments to pass to data_source_method

    Returns:
        Markdown formatted string with results or error message
    """
    date_range_log = f"from {start_date or 'default'} to {end_date or 'default'}"
    kwargs_log = f", extra_args={kwargs}" if kwargs else ""
    logger.info(f"Tool '{tool_name}' called {date_range_log}{kwargs_log}")
    try:
        # Call the appropriate method on the active_data_source
        df = data_source_method(start_date=start_date, end_date=end_date, **kwargs)
        logger.info(f"Successfully retrieved {data_type_name} data.")
        meta = {"dataset": data_type_name, "start_date": start_date, "end_date": end_date} | ({"extra": kwargs} if kwargs else {})
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
        logger.exception(f"Unexpected Exception processing {tool_name}: {e}")
        return f"Error: An unexpected error occurred: {e}"


def call_index_constituent_tool(
    tool_name: str,
    data_source_method: Callable,
    index_name: str,
    date: Optional[str] = None,
    *,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    """
    Helper function for index constituent tools

    Args:
        tool_name: Name of the tool for logging
        data_source_method: Method to call on the data source
        index_name: Name of the index (for logging)
        date: Optional date to query

    Returns:
        Markdown formatted string with results or error message
    """
    log_msg = f"Tool '{tool_name}' called for date={date or 'latest'}"
    logger.info(log_msg)
    try:
        # Add date validation if desired
        df = data_source_method(date=date)
        logger.info(
            f"Successfully retrieved {index_name} constituents for {date or 'latest'}.")
        meta = {"index": index_name, "as_of": date or "latest"}
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
        logger.exception(f"Unexpected Exception processing {tool_name}: {e}")
        return f"Error: An unexpected error occurred: {e}"
