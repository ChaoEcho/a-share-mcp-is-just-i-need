# Implementation of the ETFDataSource interface using AKShare
import akshare as ak
import pandas as pd
from typing import Optional, List, Dict, Any
import logging
from .etf_data_source_interface import ETFDataSource, DataSourceError, NoDataFoundError, LoginError
from datetime import datetime, timedelta

# Get a logger instance for this module
logger = logging.getLogger(__name__)


class AKShareETFDataSource(ETFDataSource):
    """基于AKShare的ETF数据源实现"""

    def get_etf_basic_info(self, etf_code: str) -> pd.DataFrame:
        """获取ETF基本信息"""
        logger.info(f"Fetching ETF basic info for {etf_code}")
        try:
            # 获取ETF基本信息
            etf_info = ak.fund_etf_spot_em()
            etf_data = etf_info[etf_info['代码'] == etf_code]
            
            if etf_data.empty:
                raise NoDataFoundError(f"未找到ETF代码 {etf_code} 的基本信息")
            
            logger.info(f"Successfully retrieved ETF basic info for {etf_code}")
            return etf_data
            
        except NoDataFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ETF basic info for {etf_code}: {e}")
            raise DataSourceError(f"获取ETF基本信息失败: {e}")

    def get_etf_historical_data(
        self, 
        etf_code: str, 
        start_date: str, 
        end_date: str, 
        frequency: str = "d"
    ) -> pd.DataFrame:
        """获取ETF历史行情数据"""
        logger.info(f"Fetching ETF historical data for {etf_code} ({start_date}-{end_date}, freq={frequency})")
        try:
            # 根据频率选择不同的API
            if frequency == "d":
                data = ak.fund_etf_hist_em(
                    symbol=etf_code, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date
                )
            elif frequency == "w":
                data = ak.fund_etf_hist_em(
                    symbol=etf_code, 
                    period="weekly", 
                    start_date=start_date, 
                    end_date=end_date
                )
            elif frequency == "m":
                data = ak.fund_etf_hist_em(
                    symbol=etf_code, 
                    period="monthly", 
                    start_date=start_date, 
                    end_date=end_date
                )
            else:
                raise ValueError(f"不支持的频率: {frequency}")
            
            if data.empty:
                raise NoDataFoundError(f"未找到ETF {etf_code} 的历史数据")
            
            logger.info(f"Successfully retrieved ETF historical data for {etf_code}")
            return data
            
        except NoDataFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ETF historical data for {etf_code}: {e}")
            raise DataSourceError(f"获取ETF历史数据失败: {e}")

    def get_etf_holdings(self, etf_code: str, date: Optional[str] = None) -> pd.DataFrame:
        """获取ETF持仓明细"""
        logger.info(f"Fetching ETF holdings for {etf_code}, date={date or 'latest'}")
        try:
            # 获取ETF持仓明细
            holdings = ak.fund_etf_holdings_em(symbol=etf_code)
            
            if holdings.empty:
                raise NoDataFoundError(f"未找到ETF {etf_code} 的持仓明细")
            
            logger.info(f"Successfully retrieved ETF holdings for {etf_code}")
            return holdings
            
        except NoDataFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ETF holdings for {etf_code}: {e}")
            raise DataSourceError(f"获取ETF持仓明细失败: {e}")

    def get_etf_list(self, market: str = "all") -> pd.DataFrame:
        """获取ETF列表"""
        logger.info(f"Fetching ETF list for market={market}")
        try:
            if market == "all":
                etf_list = ak.fund_etf_spot_em()
            elif market == "sh":
                etf_list = ak.fund_etf_spot_em()
                etf_list = etf_list[etf_list['代码'].str.startswith('51')]
            elif market == "sz":
                etf_list = ak.fund_etf_spot_em()
                etf_list = etf_list[etf_list['代码'].str.startswith('15')]
            else:
                raise ValueError(f"不支持的市场: {market}")
            
            if etf_list.empty:
                raise NoDataFoundError(f"未找到{market}市场的ETF列表")
            
            logger.info(f"Successfully retrieved ETF list for {market} market, {len(etf_list)} ETFs found")
            return etf_list
            
        except NoDataFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ETF list for {market}: {e}")
            raise DataSourceError(f"获取ETF列表失败: {e}")

    def get_etf_net_value(self, etf_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取ETF净值数据"""
        logger.info(f"Fetching ETF net value for {etf_code} ({start_date}-{end_date})")
        try:
            # 获取ETF净值数据（使用历史数据API）
            net_value = ak.fund_etf_hist_em(
                symbol=etf_code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date
            )
            
            if net_value.empty:
                raise NoDataFoundError(f"未找到ETF {etf_code} 的净值数据")
            
            logger.info(f"Successfully retrieved ETF net value for {etf_code}")
            return net_value
            
        except NoDataFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ETF net value for {etf_code}: {e}")
            raise DataSourceError(f"获取ETF净值数据失败: {e}")

    def get_etf_analysis(self, etf_code: str) -> Dict[str, Any]:
        """获取ETF分析数据"""
        logger.info(f"Fetching ETF analysis data for {etf_code}")
        try:
            # 获取ETF基本信息
            basic_info = self.get_etf_basic_info(etf_code)
            
            # 获取最近30天的历史数据
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            recent_performance = self.get_etf_historical_data(etf_code, start_date, end_date)
            
            # 获取持仓明细
            holdings = self.get_etf_holdings(etf_code)
            
            analysis_data = {
                "basic_info": basic_info,
                "recent_performance": recent_performance,
                "holdings": holdings
            }
            
            logger.info(f"Successfully retrieved ETF analysis data for {etf_code}")
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error fetching ETF analysis data for {etf_code}: {e}")
            raise DataSourceError(f"获取ETF分析数据失败: {e}")
