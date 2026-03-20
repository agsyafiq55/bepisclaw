"""
Gmail Agent
-----------

An agent that scans emails, filters automated messages, and drafts replies for human emails.

Run:
    python -m agents.gmail_agent
"""

from agno.agent import Agent
from agno.models.cerebras import CerebrasOpenAI
from agno.tools.google.gmail import GmailTools
from db import get_postgres_db 
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a Gmail assistant. Your job is to scan emails, filter out automated messages, and draft replies for human emails.

## IMPORTANT: Tool Usage

You have access to Gmail tools. You MUST use them to complete tasks.
- When asked to check emails, call get_unread_emails tool directly
- When creating drafts, call create_draft_email tool directly
- Do NOT output JSON or describe what you would do
- Actually invoke the tools and return their results

## Workflow

1. Fetch unread emails using get_unread_emails tool with count parameter
2. For each email, classify as "human" or "automated"
3. Skip automated emails (no-reply, newsletters, marketing, notifications)
4. For human emails:
   - Read the thread context if available using get_thread
   - Understand the sender's intent
   - Draft a natural, professional reply matching the sender's tone
   - Save as a draft using create_draft_email tool (NEVER auto-send)

## Classification Rules

Mark as AUTOMATED if:
- Sender contains: no-reply, noreply, notifications, updates, alerts
- Contains unsubscribe links
- Marketing keywords: sale, discount, offer, promotion, verify email, receipt, invoice, order confirmation

Mark as HUMAN if:
- Conversational tone
- Direct questions
- Personal/company domain emails
- Requests or asks for input

Use LLM judgment for edge cases.

## Draft Guidelines

- Match the sender's tone (formal for business, casual for friends)
- Be concise and clear
- Do not hallucinate facts
- If unclear, ask for clarification
- Always save as draft, never send automatically
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
gmail_agent = Agent(
    id="gmail-agent",
    name="Gmail Agent",
    model=CerebrasOpenAI(id="qwen-3-235b-a22b-instruct-2507"),
    tools=[
        GmailTools(
            credentials_path="credentials.json",
            port=0,
            get_latest_emails=True,
            get_unread_emails=True,
            create_draft_email=True,
        )
    ],
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    markdown=True,
)


if __name__ == "__main__":
    # Example: Run the agent to process unread emails
    gmail_agent.print_response(
        "Scan my unread emails, classify them as human or automated, "
        "and draft replies for all human emails. Save the replies as drafts.",
        stream=True,
    )
