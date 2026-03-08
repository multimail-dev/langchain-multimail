# langchain-multimail

LangChain tools for [MultiMail](https://multimail.dev) — give your LangChain agents email capabilities with graduated human oversight.

## Installation

```bash
pip install langchain-multimail
```

## Quick Start

```python
from langchain_multimail import MultiMailToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Create tools
toolkit = MultiMailToolkit(api_key="mm_live_your_api_key")
tools = toolkit.get_tools()

# Create agent
llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an email assistant. Use the MultiMail tools to help the user manage email."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run
executor.invoke({"input": "Check my inbox and summarize any new emails"})
```

## Available Tools

| Tool | Description |
|------|-------------|
| `check_inbox` | List recent emails in a mailbox |
| `read_email` | Read the full content of an email |
| `send_email` | Send an email (held for approval if gated) |
| `reply_email` | Reply to an existing email thread |
| `search_contacts` | Search contacts by name or email |
| `list_pending` | List emails awaiting human approval |
| `decide_email` | Approve or reject a pending email |
| `get_thread` | Get all emails in a conversation |
| `tag_email` | Add key-value tags to an email |

## Oversight Modes

MultiMail supports graduated oversight so your agent doesn't send unsupervised email:

- **`gated_all`** — Agent drafts, human approves everything
- **`gated_send`** — Agent reads freely, human approves outbound *(default)*
- **`monitored`** — Agent sends, human can review after
- **`autonomous`** — Full agent control

When a mailbox uses gated oversight, `send_email` returns `pending_send_approval` and the email waits for human review. The agent can check status with `list_pending`.

## Using Individual Tools

```python
from multimail import MultiMail
from langchain_multimail import CheckInboxTool, SendEmailTool

client = MultiMail("mm_live_your_api_key")

inbox = CheckInboxTool(client=client)
sender = SendEmailTool(client=client)

# Use directly
print(inbox.run({"mailbox_id": "your_mailbox_id", "limit": 5}))
```

## Links

- [MultiMail](https://multimail.dev) — Homepage & docs
- [multimail](https://pypi.org/project/multimail/) — Base Python SDK
- [MCP Server](https://www.npmjs.com/package/@multimail/mcp-server) — For Claude, Cursor, and other MCP clients
