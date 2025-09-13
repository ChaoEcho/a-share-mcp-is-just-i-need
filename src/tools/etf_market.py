"""
ETF市场数据工具
"""
import logging
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from src.etf_data_source_interface import ETFDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown

logger = logging.getLogger(__name__)


def register_etf_market_tools(app: FastMCP, active_etf_data_source: ETFDataSource):
    """注册ETF市场数据工具"""
    
    @app.tool()
    def get_etf_basic_info(etf_code: str) -> str:
        """
        获取ETF基本信息
        
        Args:
            etf_code: ETF代码，如'159919'（沪深300ETF）
            
        Returns:
            Markdown格式的ETF基本信息表格
        """
        logger.info(f"Tool 'get_etf_basic_info' called for {etf_code}")
        try:
            df = active_etf_data_source.get_etf_basic_info(etf_code)
            logger.info(f"成功获取ETF {etf_code} 基本信息")
            return format_df_to_markdown(df)
            
        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {etf_code}: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {etf_code}: {e}")
            return f"错误: 无法连接到数据源. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {etf_code}: {e}")
            return f"错误: 获取数据时发生错误. {e}"
        except Exception as e:
            logger.exception(f"Unexpected Exception for {etf_code}: {e}")
            return f"错误: 发生意外错误: {e}"
    
    @app.tool()
    def get_etf_historical_data(etf_code: str, start_date: str, end_date: str, 
                               frequency: str = "d") -> str:
        """
        获取ETF历史行情数据
        
        Args:
            etf_code: ETF代码，如'159919'
            start_date: 开始日期，格式'YYYY-MM-DD'
            end_date: 结束日期，格式'YYYY-MM-DD'
            frequency: 数据频率，'d'=日线，'w'=周线，'m'=月线
            
        Returns:
            Markdown格式的历史数据表格
        """
        logger.info(f"Tool 'get_etf_historical_data' called for {etf_code} ({start_date}-{end_date}, freq={frequency})")
        try:
            # 验证频率参数
            valid_freqs = ['d', 'w', 'm']
            if frequency not in valid_freqs:
                return f"错误: 无效的频率 '{frequency}'. 有效选项: {valid_freqs}"
            
            df = active_etf_data_source.get_etf_historical_data(
                etf_code, start_date, end_date, frequency)
            logger.info(f"成功获取ETF {etf_code} 历史数据")
            return format_df_to_markdown(df)
            
        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {etf_code}: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {etf_code}: {e}")
            return f"错误: 无法连接到数据源. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {etf_code}: {e}")
            return f"错误: 获取数据时发生错误. {e}"
        except Exception as e:
            logger.exception(f"Unexpected Exception for {etf_code}: {e}")
            return f"错误: 发生意外错误: {e}"
    
    @app.tool()
    def get_etf_list(market: str = "all") -> str:
        """
        获取ETF列表
        
        Args:
            market: 市场筛选，'all'=全部，'sh'=上海，'sz'=深圳
            
        Returns:
            Markdown格式的ETF列表表格
        """
        logger.info(f"Tool 'get_etf_list' called for market={market}")
        try:
            df = active_etf_data_source.get_etf_list(market)
            logger.info(f"成功获取{market}市场ETF列表，共{len(df)}只")
            return format_df_to_markdown(df)
            
        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"LoginError: {e}")
            return f"错误: 无法连接到数据源. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError: {e}")
            return f"错误: 获取数据时发生错误. {e}"
        except Exception as e:
            logger.exception(f"Unexpected Exception: {e}")
            return f"错误: 发生意外错误: {e}"
    
    @app.tool()
    def get_etf_net_value(etf_code: str, start_date: str, end_date: str) -> str:
        """
        获取ETF净值数据
        
        Args:
            etf_code: ETF代码，如'159919'
            start_date: 开始日期，格式'YYYY-MM-DD'
            end_date: 结束日期，格式'YYYY-MM-DD'
            
        Returns:
            Markdown格式的净值数据表格
        """
        logger.info(f"Tool 'get_etf_net_value' called for {etf_code} ({start_date}-{end_date})")
        try:
            df = active_etf_data_source.get_etf_net_value(etf_code, start_date, end_date)
            logger.info(f"成功获取ETF {etf_code} 净值数据")
            return format_df_to_markdown(df)
            
        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {etf_code}: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {etf_code}: {e}")
            return f"错误: 无法连接到数据源. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {etf_code}: {e}")
            return f"错误: 获取数据时发生错误. {e}"
        except Exception as e:
            logger.exception(f"Unexpected Exception for {etf_code}: {e}")
            return f"错误: 发生意外错误: {e}"
