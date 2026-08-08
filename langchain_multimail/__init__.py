"""LangChain tools for MultiMail — email capabilities for LangChain agents."""

import warnings as _warnings

_warnings.warn(
    "The langchain-multimail PyPI package is deprecated and unmaintained (retired 2026-08-08). "
    "Use MultiMail's MCP server (https://mcp.multimail.dev) or REST API "
    "(https://multimail.dev/docs) instead.",
    FutureWarning,
    stacklevel=2,
)


from langchain_multimail.tools import (
    MultiMailToolkit,
    CheckInboxTool,
    ReadEmailTool,
    SendEmailTool,
    ReplyEmailTool,
    SearchContactsTool,
    ListPendingTool,
    DecideEmailTool,
    GetThreadTool,
    TagEmailTool,
)

__version__ = "0.1.0"
__all__ = [
    "MultiMailToolkit",
    "CheckInboxTool",
    "ReadEmailTool",
    "SendEmailTool",
    "ReplyEmailTool",
    "SearchContactsTool",
    "ListPendingTool",
    "DecideEmailTool",
    "GetThreadTool",
    "TagEmailTool",
]
