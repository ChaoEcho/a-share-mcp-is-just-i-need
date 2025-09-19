"""
基于 AKShare 的实时行情工具
"""

import logging
from typing import Optional

import akshare as ak
import pandas as pd

from mcp.server.fastmcp import FastMCP
from src.formatting.markdown_formatter import format_df_to_markdown

logger = logging.getLogger(__name__)


def _normalize_code(code: str) -> str:
    """标准化传入代码，去空格并统一大小写。

    说明：此工具支持股票与 ETF。A 股常见六位数字或带交易所前缀均可。
    """
    if not code:
        return code
    return code.strip().upper()


def _fetch_realtime_for_equity_or_etf(code: str) -> pd.DataFrame:
    """尽力从 AKShare 获取当日实时/最新可得行情。

    策略（尽可能返回）：
    1) 先查 ETF 实时表 fund_etf_spot_em（适配 ETF 代码，如 510300、159919）。
    2) 若未命中，再查 A 股个股实时表 stock_zh_a_spot_em（适配 6 位股票代码）。
    """
    norm = _normalize_code(code)

    # 1) ETF 实时
    try:
        etf_df = ak.fund_etf_spot_em()
        if isinstance(etf_df, pd.DataFrame) and not etf_df.empty:
            matched = etf_df[etf_df["代码"].astype(str) == norm]
            if matched is not None and not matched.empty:
                matched = matched.copy()
                matched.insert(0, "数据源", "AKShare-fund_etf_spot_em")
                return matched
    except Exception as e:
        logger.warning(f"ETF 实时接口失败，尝试股票通道: {e}")

    # 2) A 股个股实时
    try:
        stock_df = ak.stock_zh_a_spot_em()
        if isinstance(stock_df, pd.DataFrame) and not stock_df.empty:
            matched = stock_df[stock_df["代码"].astype(str) == norm]
            if matched is not None and not matched.empty:
                matched = matched.copy()
                matched.insert(0, "数据源", "AKShare-stock_zh_a_spot_em")
                return matched
    except Exception as e:
        logger.error(f"股票实时接口失败: {e}")

    # 若均无，返回空 DataFrame
    return pd.DataFrame()


def register_realtime_tools(app: FastMCP):
    """注册实时行情工具到 MCP 应用。"""

    @app.tool()
    def get_realtime_quote(code: str) -> str:
        """
        获取股票/ETF 当日可得的实时行情（尽力而为）。

        Args:
            code: 股票或 ETF 代码，如 '600519'、'000001'、'510300'、'159919'

        Returns:
            Markdown 表格（若可取得数据），否则返回说明信息。
        """
        logger.info(f"Tool 'get_realtime_quote' called for code={code}")

        norm_code = _normalize_code(code)
        if not norm_code:
            return "错误: 请输入有效的股票或ETF代码"

        try:
            df = _fetch_realtime_for_equity_or_etf(norm_code)
            if df is None or df.empty:
                return (
                    "未获取到实时数据。可能原因：代码不存在、非交易时段或数据延迟。"
                    "（AKShare 实时并非严格实时，仅尽力返回最新可得数据）"
                )

            # 只展示有限列，若存在常见列则优先
            preferred_cols = [
                "数据源",
                "代码",
                "名称",
                "最新价",
                "涨跌幅",
                "涨跌额",
                "今开",
                "昨收",
                "最高",
                "最低",
                "成交量",
                "成交额",
                "更新时间",
                "日期",
            ]
            cols = [c for c in preferred_cols if c in df.columns]
            if cols:
                df = df[cols]

            return format_df_to_markdown(df)
        except Exception as e:
            logger.exception(f"获取实时行情异常: code={norm_code}, error={e}")
            return f"错误: 获取实时行情失败: {e}"
