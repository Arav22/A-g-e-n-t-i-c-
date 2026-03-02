import pytest

from agentic.tool_adapters import EchoTool, ToolRegistry


def test_tool_registry_returns_registered_adapter() -> None:
    registry = ToolRegistry([EchoTool()])

    adapter = registry.get("echo")

    assert adapter.run("hello") == "echo:hello"
    assert registry.names() == ["echo"]


def test_tool_registry_rejects_unknown_adapter() -> None:
    registry = ToolRegistry([EchoTool()])

    with pytest.raises(KeyError, match="Unknown tool adapter"):
        registry.get("missing")


def test_tool_registry_requires_at_least_one_adapter() -> None:
    with pytest.raises(ValueError, match="At least one tool adapter is required"):
        ToolRegistry([])
