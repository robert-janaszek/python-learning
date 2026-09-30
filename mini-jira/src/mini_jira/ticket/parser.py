from mini_jira.llm_client import structured_client
from mini_jira.ticket.schemas import TicketDraft


async def parse_ticket(text: str) -> TicketDraft:
    response = await structured_client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        response_model=TicketDraft,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract a support ticket from the email. "
                    "title is a short summary of the issue. "
                    "sender_email is the From address, the person who wrote the message. "
                    "Ignore the To address and the name in the greeting. "
                    "priority is low, medium, or high, based on how urgent the mail sounds. "
                    "tags are a few short labels for the topic."
                ),
            },
            {"role": "user", "content": text},
        ],
        extra_body={"reasoning": "off"},
        context={"source": text},
        max_retries=3
    )

    return response