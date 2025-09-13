"""
ETF持仓工具
"""
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from src.etf_data_source_interface import ETFDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown

logger = logging.getLogger(__name__)


def register_etf_holdings_tools(app: FastMCP, active_etf_data_source: ETFDataSource):
    """注册ETF持仓工具"""
    
    @app.tool()
    def get_etf_holdings(etf_code: str, date: Optional[str] = None) -> str:
        """
        获取ETF持仓明细
        
        Args:
            etf_code: ETF代码，如'159919'
            date: 查询日期，格式'YYYY-MM-DD'，None表示最新
            
        Returns:
            Markdown格式的持仓明细表格
        """
        logger.info(f"Tool 'get_etf_holdings' called for {etf_code}, date={date or 'latest'}")
        try:
            df = active_etf_data_source.get_etf_holdings(etf_code, date)
            logger.info(f"成功获取ETF {etf_code} 持仓明细，共{len(df)}只成分股")
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
    def get_etf_top_holdings(etf_code: str, top_n: int = 10) -> str:
        """
        获取ETF前N大持仓
        
        Args:
            etf_code: ETF代码，如'159919'
            top_n: 前N大持仓数量，默认10
            
        Returns:
            Markdown格式的前N大持仓表格
        """
        logger.info(f"Tool 'get_etf_top_holdings' called for {etf_code}, top_n={top_n}")
        try:
            df = active_etf_data_source.get_etf_holdings(etf_code)
            
            # 按持仓比例排序并取前N个
            if '持仓占比' in df.columns:
                top_holdings = df.nlargest(top_n, '持仓占比')
            elif '占净值比例' in df.columns:
                top_holdings = df.nlargest(top_n, '占净值比例')
            else:
                top_holdings = df.head(top_n)
            
            logger.info(f"成功获取ETF {etf_code} 前{top_n}大持仓")
            return format_df_to_markdown(top_holdings)
            
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
