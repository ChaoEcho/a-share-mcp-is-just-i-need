# Defines the abstract interface for ETF data sources
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List, Dict, Any
from .data_source_interface import DataSourceError, NoDataFoundError, LoginError


class ETFDataSource(ABC):
    """
    Abstract base class defining the interface for ETF data sources.
    Implementations of this class provide access to specific ETF data APIs
    (e.g., AKShare, Tushare).
    """

    @abstractmethod
    def get_etf_basic_info(self, etf_code: str) -> pd.DataFrame:
        """
        Fetches basic information for a given ETF code.

        Args:
            etf_code: The ETF code (e.g., '159919', '510300').

        Returns:
            A pandas DataFrame containing the basic ETF information.
            The structure and columns depend on the underlying data source.
            Typically contains info like name, price, change, volume, etc.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If the input code is invalid.
        """
        pass

    @abstractmethod
    def get_etf_historical_data(
        self, 
        etf_code: str, 
        start_date: str, 
        end_date: str, 
        frequency: str = "d"
    ) -> pd.DataFrame:
        """
        Fetches historical price data for a given ETF code.

        Args:
            etf_code: The ETF code (e.g., '159919', '510300').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.
            frequency: Data frequency. Common values:
                       'd': daily
                       'w': weekly
                       'm': monthly
                       Defaults to 'd'.

        Returns:
            A pandas DataFrame containing the historical price data.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If input parameters are invalid.
        """
        pass

    @abstractmethod
    def get_etf_holdings(self, etf_code: str, date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetches ETF holdings (constituent stocks) for a given ETF code.

        Args:
            etf_code: The ETF code (e.g., '159919', '510300').
            date: Optional. The date in 'YYYY-MM-DD' format. If None, uses the latest available date.

        Returns:
            A pandas DataFrame containing the ETF holdings information.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If the input code is invalid.
        """
        pass

    @abstractmethod
    def get_etf_list(self, market: str = "all") -> pd.DataFrame:
        """
        Fetches a list of all ETFs.

        Args:
            market: Market filter. Common values:
                    'all': all markets
                    'sh': Shanghai market
                    'sz': Shenzhen market
                    Defaults to 'all'.

        Returns:
            A pandas DataFrame containing the ETF list.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If the market parameter is invalid.
        """
        pass

    @abstractmethod
    def get_etf_net_value(self, etf_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches ETF net value data for a given ETF code and date range.

        Args:
            etf_code: The ETF code (e.g., '159919', '510300').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.

        Returns:
            A pandas DataFrame containing the ETF net value data.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If input parameters are invalid.
        """
        pass

    @abstractmethod
    def get_etf_analysis(self, etf_code: str) -> Dict[str, Any]:
        """
        Fetches comprehensive analysis data for a given ETF code.

        Args:
            etf_code: The ETF code (e.g., '159919', '510300').

        Returns:
            A dictionary containing various analysis data including:
            - basic_info: Basic ETF information
            - recent_performance: Recent price performance data
            - holdings: ETF holdings information

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If the input code is invalid.
        """
        pass
