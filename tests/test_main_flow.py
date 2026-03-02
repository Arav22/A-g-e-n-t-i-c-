from agentic_ai.main import build_service
from agentic_ai.api.models import TaskRequest


def test_end_to_end_word_count_flow() -> None:
    service = build_service()
    response = service.run_task(TaskRequest(prompt="Count words in: one two three"))
    assert "word_count=3" in response.output
    assert "Task complete." in response.output
