import pytest
from pathlib import Path
from instructor.v2.core.errors import InstructorRetryException

from mini_jira.ticket.parser import parse_ticket


@pytest.mark.llm
@pytest.mark.asyncio
async def test_high_priority():
    email = (Path(__file__).parent / "emails" / "email.1.txt").read_text()
    response = await parse_ticket(email)
    assert response.sender_email == "laura@company.com"
    assert response.priority == 'high'
    assert len(response.title) > 0
    assert len(response.tags) > 0


@pytest.mark.llm
@pytest.mark.asyncio
async def test_chaotic():
    email = (Path(__file__).parent / "emails" / "email.2.txt").read_text()
    response = await parse_ticket(email)
    assert response.sender_email == "mary@company.com"
    assert response.priority == 'low'
    assert len(response.title) > 0
    assert len(response.tags) > 0


@pytest.mark.llm
@pytest.mark.asyncio
async def test_low_priority():
    email = (Path(__file__).parent / "emails" / "email.3.txt").read_text()
    response = await parse_ticket(email)
    assert response.sender_email == "sean@company.com"
    assert response.priority == 'low'
    assert len(response.title) > 0
    assert len(response.tags) > 0

@pytest.mark.llm
@pytest.mark.asyncio
async def test_no_address():
    email = (Path(__file__).parent / "emails" / "email.4.txt").read_text()
    with pytest.raises(InstructorRetryException):
        await parse_ticket(email)