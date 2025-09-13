"""
ETF分析工具
"""
import logging
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from src.etf_data_source_interface import ETFDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown

logger = logging.getLogger(__name__)


def register_etf_analysis_tools(app: FastMCP, active_etf_data_source: ETFDataSource):
    """注册ETF分析工具"""
    
    @app.tool()
    def get_etf_analysis(etf_code: str, analysis_type: str = "comprehensive") -> str:
        """
        获取ETF分析报告
        
        Args:
            etf_code: ETF代码，如'159919'
            analysis_type: 分析类型，'basic'=基础，'performance'=表现，'comprehensive'=综合
            
        Returns:
            Markdown格式的ETF分析报告
        """
        logger.info(f"Tool 'get_etf_analysis' called for {etf_code}, type={analysis_type}")
        
        try:
            # 获取ETF分析数据
            analysis_data = active_etf_data_source.get_etf_analysis(etf_code)
            
            basic_info = analysis_data['basic_info']
            recent_performance = analysis_data['recent_performance']
            holdings = analysis_data['holdings']
            
            # 构建分析报告
            report = f"# ETF分析报告\n\n"
            report += "## 免责声明\n本报告基于公开数据生成，仅供参考，不构成投资建议。\n\n"
            
            # 基本信息
            if not basic_info.empty:
                report += "## 基本信息\n"
                if '名称' in basic_info.columns:
                    report += f"- ETF名称: {basic_info['名称'].iloc[0]}\n"
                if '代码' in basic_info.columns:
                    report += f"- ETF代码: {basic_info['代码'].iloc[0]}\n"
                if '最新价' in basic_info.columns:
                    report += f"- 最新价: {basic_info['最新价'].iloc[0]}\n"
                if '涨跌幅' in basic_info.columns:
                    report += f"- 涨跌幅: {basic_info['涨跌幅'].iloc[0]}%\n"
                if '成交量' in basic_info.columns:
                    report += f"- 成交量: {basic_info['成交量'].iloc[0]}\n"
                report += "\n"
            
            # 表现分析
            if analysis_type in ["performance", "comprehensive"] and not recent_performance.empty:
                report += "## 近期表现分析\n"
                
                if '收盘' in recent_performance.columns:
                    latest_price = recent_performance['收盘'].iloc[-1]
                    start_price = recent_performance['收盘'].iloc[0]
                    price_change = ((float(latest_price) / float(start_price)) - 1) * 100
                    
                    report += f"- 最新收盘价: {latest_price}\n"
                    report += f"- 30日涨跌幅: {price_change:.2f}%\n"
                    
                    # 计算波动率
                    if len(recent_performance) > 1:
                        returns = recent_performance['收盘'].pct_change().dropna()
                        volatility = returns.std() * (252 ** 0.5) * 100  # 年化波动率
                        report += f"- 年化波动率: {volatility:.2f}%\n"
                
                report += "\n"
            
            # 持仓分析
            if analysis_type in ["comprehensive"] and not holdings.empty:
                report += "## 持仓分析\n"
                report += f"- 成分股数量: {len(holdings)}\n"
                
                # 前5大持仓
                if '持仓占比' in holdings.columns:
                    top5 = holdings.nlargest(5, '持仓占比')
                    report += "\n### 前5大持仓\n"
                    for idx, row in top5.iterrows():
                        if '股票名称' in row and '持仓占比' in row:
                            report += f"- {row['股票名称']}: {row['持仓占比']}%\n"
                
                report += "\n"
            
            # 投资建议
            report += "## 数据解读建议\n"
            report += "- 以上数据仅供参考，建议结合市场环境和投资目标进行综合分析\n"
            report += "- ETF表现受跟踪指数和成分股影响，历史数据不代表未来表现\n"
            report += "- 投资决策应基于个人风险承受能力和投资目标\n"
            
            logger.info(f"成功生成ETF {etf_code} 分析报告")
            return report
            
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
    def compare_etfs(etf_codes: str, comparison_type: str = "performance") -> str:
        """
        比较多个ETF
        
        Args:
            etf_codes: ETF代码列表，用逗号分隔，如'159919,510300,512100'
            comparison_type: 比较类型，'performance'=表现，'holdings'=持仓，'comprehensive'=综合
            
        Returns:
            Markdown格式的ETF比较报告
        """
        logger.info(f"Tool 'compare_etfs' called for {etf_codes}, type={comparison_type}")
        
        try:
            codes = [code.strip() for code in etf_codes.split(',')]
            if len(codes) < 2:
                return "错误: 至少需要2个ETF代码进行比较"
            
            report = f"# ETF比较分析\n\n"
            report += "## 免责声明\n本报告基于公开数据生成，仅供参考，不构成投资建议。\n\n"
            
            # 获取每个ETF的基本信息
            etf_data = {}
            for code in codes:
                try:
                    basic_info = active_etf_data_source.get_etf_basic_info(code)
                    etf_data[code] = basic_info
                except Exception as e:
                    logger.warning(f"获取ETF {code} 数据失败: {e}")
                    etf_data[code] = None
            
            # 构建比较表格
            report += "## 基本信息比较\n"
            report += "| ETF代码 | 名称 | 最新价 | 涨跌幅 | 成交量 |\n"
            report += "|---------|------|--------|--------|--------|\n"
            
            for code, data in etf_data.items():
                if data is not None and not data.empty:
                    name = data['名称'].iloc[0] if '名称' in data.columns else 'N/A'
                    price = data['最新价'].iloc[0] if '最新价' in data.columns else 'N/A'
                    change = data['涨跌幅'].iloc[0] if '涨跌幅' in data.columns else 'N/A'
                    volume = data['成交量'].iloc[0] if '成交量' in data.columns else 'N/A'
                    report += f"| {code} | {name} | {price} | {change}% | {volume} |\n"
                else:
                    report += f"| {code} | 数据获取失败 | N/A | N/A | N/A |\n"
            
            report += "\n## 比较结论\n"
            report += "- 以上数据仅供参考，建议结合具体投资需求进行选择\n"
            report += "- 不同ETF的跟踪指数和投资策略可能存在差异\n"
            report += "- 投资决策应基于个人风险承受能力和投资目标\n"
            
            logger.info(f"成功生成ETF比较报告，比较了{len(codes)}只ETF")
            return report
            
        except Exception as e:
            logger.exception(f"Unexpected Exception in compare_etfs: {e}")
            return f"错误: 发生意外错误: {e}"
