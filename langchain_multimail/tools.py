"""LangChain tool wrappers for the MultiMail API."""

from __future__ import annotations
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from multimail import MultiMail


# ── Input Schemas ────────────────────────────────────────────

class CheckInboxInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID to check")
    direction: Optional[str] = Field(default=None, description="Filter by 'inbound' or 'outbound'")
    limit: int = Field(default=20, description="Number of emails to return")


class ReadEmailInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID")
    email_id: str = Field(description="The email ID to read")


class SendEmailInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID to send from")
    to: list[str] = Field(description="Recipient email addresses")
    subject: str = Field(description="Email subject line")
    markdown: str = Field(description="Email body in markdown format")
    cc: Optional[list[str]] = Field(default=None, description="CC addresses")
    bcc: Optional[list[str]] = Field(default=None, description="BCC addresses")


class ReplyEmailInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID")
    email_id: str = Field(description="The email ID to reply to")
    markdown: str = Field(description="Reply body in markdown format")


class SearchContactsInput(BaseModel):
    q: Optional[str] = Field(default=None, description="Search query for contacts")


class ListPendingInput(BaseModel):
    pass


class DecideEmailInput(BaseModel):
    email_id: str = Field(description="The email ID to approve or reject")
    action: str = Field(description="'approve' or 'reject'")
    reason: Optional[str] = Field(default=None, description="Reason for the decision")


class GetThreadInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID")
    thread_id: str = Field(description="The thread ID")


class TagEmailInput(BaseModel):
    mailbox_id: str = Field(description="The mailbox ID")
    email_id: str = Field(description="The email ID to tag")
    tags: dict[str, str] = Field(description="Tags as key-value pairs")


# ── Tools ────────────────────────────────────────────────────

class CheckInboxTool(BaseTool):
    name: str = "check_inbox"
    description: str = "Check a mailbox for recent emails. Returns subject, sender, date, and status for each email."
    args_schema: Type[BaseModel] = CheckInboxInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, direction: str | None = None, limit: int = 20) -> str:
        result = self.client.list_emails(mailbox_id, limit=limit, direction=direction)
        emails = result.get("emails", [])
        if not emails:
            return "Inbox is empty."
        lines = []
        for e in emails:
            lines.append(f"- [{e['direction']}] {e['subject']} — from {e.get('from_address', '?')} ({e['status']})")
            lines.append(f"  ID: {e['id']}")
        return "\n".join(lines)


class ReadEmailTool(BaseTool):
    name: str = "read_email"
    description: str = "Read the full content of a specific email including subject, sender, recipients, and body."
    args_schema: Type[BaseModel] = ReadEmailInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, email_id: str) -> str:
        e = self.client.get_email(mailbox_id, email_id)
        parts = [
            f"Subject: {e['subject']}",
            f"From: {e.get('from_address', '?')}",
            f"To: {', '.join(e.get('to_addresses', []))}",
            f"Date: {e.get('created_at', '?')}",
            f"Status: {e['status']}",
            f"Direction: {e['direction']}",
            "",
            e.get("text_body", "(no text body)"),
        ]
        if e.get("has_attachments"):
            parts.append(f"\nAttachments: {', '.join(a['name'] for a in e.get('attachments', []))}")
        return "\n".join(parts)


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = (
        "Send an email from a MultiMail mailbox. The body is written in markdown. "
        "If the mailbox uses gated oversight, the email will be held for human approval before delivery."
    )
    args_schema: Type[BaseModel] = SendEmailInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, to: list[str], subject: str, markdown: str,
             cc: list[str] | None = None, bcc: list[str] | None = None) -> str:
        result = self.client.send_email(mailbox_id, to=to, subject=subject, markdown=markdown, cc=cc, bcc=bcc)
        return f"Email queued — id: {result['id']}, status: {result['status']}, thread: {result['thread_id']}"


class ReplyEmailTool(BaseTool):
    name: str = "reply_email"
    description: str = "Reply to an existing email. Maintains the thread and preserves In-Reply-To headers."
    args_schema: Type[BaseModel] = ReplyEmailInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, email_id: str, markdown: str) -> str:
        result = self.client.reply_email(mailbox_id, email_id, markdown=markdown)
        return f"Reply queued — id: {result['id']}, status: {result['status']}"


class SearchContactsTool(BaseTool):
    name: str = "search_contacts"
    description: str = "Search the contact list by name or email address."
    args_schema: Type[BaseModel] = SearchContactsInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, q: str | None = None) -> str:
        contacts = self.client.list_contacts(q=q)
        if not contacts:
            return "No contacts found."
        lines = [f"- {c.get('name', '(no name)')} <{c['email']}>" for c in contacts]
        return "\n".join(lines)


class ListPendingTool(BaseTool):
    name: str = "list_pending"
    description: str = "List emails that are waiting for human approval. Use this to check what needs oversight review."
    args_schema: Type[BaseModel] = ListPendingInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self) -> str:
        pending = self.client.list_pending()
        if not pending:
            return "No emails pending approval."
        lines = []
        for e in pending:
            lines.append(f"- {e['subject']} → {', '.join(e.get('to_addresses', []))}")
            lines.append(f"  ID: {e['id']} | Status: {e['status']}")
        return "\n".join(lines)


class DecideEmailTool(BaseTool):
    name: str = "decide_email"
    description: str = "Approve or reject a pending email. Action must be 'approve' or 'reject'."
    args_schema: Type[BaseModel] = DecideEmailInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, email_id: str, action: str, reason: str | None = None) -> str:
        result = self.client.decide(email_id, action, reason=reason)
        return f"Email {email_id} — decision: {action}, new status: {result.get('status', 'updated')}"


class GetThreadTool(BaseTool):
    name: str = "get_thread"
    description: str = "Get all emails in a conversation thread, ordered chronologically."
    args_schema: Type[BaseModel] = GetThreadInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, thread_id: str) -> str:
        result = self.client.get_thread(mailbox_id, thread_id)
        emails = result.get("emails", [])
        if not emails:
            return "Empty thread."
        lines = []
        for e in emails:
            lines.append(f"[{e['direction']}] {e.get('from_address', '?')}: {e['subject']}")
            body = e.get("text_body", "")
            if body:
                preview = body[:200] + "..." if len(body) > 200 else body
                lines.append(f"  {preview}")
            lines.append("")
        return "\n".join(lines)


class TagEmailTool(BaseTool):
    name: str = "tag_email"
    description: str = "Add tags (key-value pairs) to an email for classification and retrieval."
    args_schema: Type[BaseModel] = TagEmailInput
    client: MultiMail = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, mailbox_id: str, email_id: str, tags: dict[str, str]) -> str:
        self.client.set_tags(mailbox_id, email_id, tags)
        return f"Tags set on {email_id}: {tags}"


# ── Toolkit ──────────────────────────────────────────────────

class MultiMailToolkit:
    """Creates all MultiMail tools from a single API key."""

    def __init__(self, api_key: str, *, base_url: str = "https://api.multimail.dev"):
        self.client = MultiMail(api_key, base_url=base_url)

    def get_tools(self) -> list[BaseTool]:
        """Return all MultiMail tools ready for use with a LangChain agent."""
        return [
            CheckInboxTool(client=self.client),
            ReadEmailTool(client=self.client),
            SendEmailTool(client=self.client),
            ReplyEmailTool(client=self.client),
            SearchContactsTool(client=self.client),
            ListPendingTool(client=self.client),
            DecideEmailTool(client=self.client),
            GetThreadTool(client=self.client),
            TagEmailTool(client=self.client),
        ]
