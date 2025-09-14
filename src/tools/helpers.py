"""
Helper tools for code normalization and constants discovery.
These are agent-friendly utilities with clear, unambiguous parameters.
"""
import logging
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_helpers_tools(app: FastMCP):
    """
    Register helper/utility tools with the MCP app.
    """

    @app.tool()
    def normalize_stock_code(code: str) -> str:
        """
        Normalize a stock code to Baostock format.

        Rules:
            - If 6 digits and starts with '6' -> 'sh.<code>'
            - If 6 digits and starts with other -> 'sz.<code>'
            - Accept '600000.SH'/'000001.SZ' -> lower and reorder to 'sh.600000'/'sz.000001'
            - Accept 'sh600000'/'sz000001' -> insert dot

        Args:
            code: Raw stock code (e.g., '600000', '000001.SZ', 'sh600000').

        Returns:
            Normalized code like 'sh.600000' or an error string if invalid.

        Examples:
            - normalize_stock_code('600000') -> 'sh.600000'
            - normalize_stock_code('000001.SZ') -> 'sz.000001'
        """
        logger.info("Tool 'normalize_stock_code' called with input=%s", code)
        try:
            raw = (code or "").strip()
            if not raw:
                return "Error: 'code' is required."

            # Patterns
            m = re.fullmatch(r"(?i)(sh|sz)[\.]?(\d{6})", raw)
            if m:
                ex = m.group(1).lower()
                num = m.group(2)
                return f"{ex}.{num}"

            m2 = re.fullmatch(r"(\d{6})[\.]?(?i)(sh|sz)", raw)
            if m2:
                num = m2.group(1)
                ex = m2.group(2).lower()
                return f"{ex}.{num}"

            m3 = re.fullmatch(r"(\d{6})", raw)
            if m3:
                num = m3.group(1)
                ex = "sh" if num.startswith("6") else "sz"
                return f"{ex}.{num}"

            return "Error: Unsupported code format. Examples: 'sh.600000', '600000', '000001.SZ'."
        except Exception as e:
            logger.exception("Exception in normalize_stock_code: %s", e)
            return f"Error: {e}"

    @app.tool()
    def list_tool_constants(kind: Optional[str] = None) -> str:
        """
        List valid constants for tool parameters.

        Args:
            kind: Optional filter: 'frequency' | 'adjust_flag' | 'year_type' | 'index'. If None, show all.

        Returns:
            Markdown table(s) of constants and meanings.
        """
        logger.info("Tool 'list_tool_constants' called kind=%s", kind or "all")
        freq = [
            ("d", "daily"), ("w", "weekly"), ("m", "monthly"),
            ("5", "5 minutes"), ("15", "15 minutes"), ("30", "30 minutes"), ("60", "60 minutes"),
        ]
        adjust = [("1", "forward adjusted"), ("2", "backward adjusted"), ("3", "unadjusted")]
        year_type = [("report", "announcement year"), ("operate", "ex-dividend year")]
        index = [("hs300", "CSI 300"), ("sz50", "SSE 50"), ("zz500", "CSI 500")]

        sections = []
        def as_md(title: str, rows):
            if not rows:
                return ""
            header = f"### {title}\n\n| value | meaning |\n|---|---|\n"
            lines = [f"| {v} | {m} |" for (v, m) in rows]
            return header + "\n".join(lines) + "\n"

        k = (kind or "").strip().lower()
        if k in ("", "frequency"):
            sections.append(as_md("frequency", freq))
        if k in ("", "adjust_flag"):
            sections.append(as_md("adjust_flag", adjust))
        if k in ("", "year_type"):
            sections.append(as_md("year_type", year_type))
        if k in ("", "index"):
            sections.append(as_md("index", index))

        out = "\n".join(s for s in sections if s)
        if not out:
            return "Error: Invalid kind. Use one of 'frequency', 'adjust_flag', 'year_type', 'index'."
        return out

