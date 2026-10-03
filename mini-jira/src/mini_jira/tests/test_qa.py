import asyncio
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, BaseMetric, FaithfulnessMetric
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase, RetrievedContextData

from mini_jira.qa.service import answer_question

judge = LocalModel(
    model="qwen/qwen3.6-35b-a3b",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)

def _metrics() -> list[BaseMetric]:
    return [
        FaithfulnessMetric(threshold=0.7, model=judge),
        AnswerRelevancyMetric(threshold=0.7, model=judge),
    ]

@pytest.mark.llm
def test_priority_values():
    question = "What values can priority take?"
    result = asyncio.run(answer_question(question))
    
    quotes: list[str | RetrievedContextData] = []
    quotes.extend(result.quotes)

    assert_test(
        LLMTestCase(
            input=question,
            actual_output=result.answer,
            retrieval_context=quotes,
        ),
        _metrics()
    )

@pytest.mark.llm
def test_support_phone_is_absent():
    question = "What is the support phone number?"
    result = asyncio.run(answer_question(question))
    
    quotes: list[str | RetrievedContextData] = []
    quotes.extend(result.quotes)

    assert_test(
        LLMTestCase(
            input=question,
            actual_output=result.answer,
            retrieval_context=quotes,
        ),
        _metrics()
    )
