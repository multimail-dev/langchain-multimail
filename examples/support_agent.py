"""Example: Customer support agent that reads and responds to emails."""

from langchain_multimail import MultiMailToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """You are a customer support agent for Acme Corp.
Your mailbox ID is: {mailbox_id}

Your responsibilities:
1. Check the inbox for new customer emails
2. Read each email carefully
3. Draft a helpful, professional reply
4. Tag emails with category (support, billing, feature-request, bug)

Be concise and friendly. If you're unsure about something, say so rather than guessing.
The mailbox uses gated_send mode, so a human will review your replies before they're sent."""

toolkit = MultiMailToolkit(api_key="mm_live_your_api_key")
tools = toolkit.get_tools()

llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
result = executor.invoke({
    "input": "Check the inbox for new emails and respond to any that need a reply.",
    "mailbox_id": "YOUR_MAILBOX_ID",
})
print(result["output"])
