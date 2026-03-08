"""LangChain tools for MultiMail — email capabilities for LangChain agents."""

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
