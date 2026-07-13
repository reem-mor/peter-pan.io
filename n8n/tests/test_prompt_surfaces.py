"""Prompt surfaces are versioned files — node content must match byte-for-byte.

Surfaces (prompt-log deliverable):
  #1 Extract Incident Info systemPromptTemplate  -> docs/prompt-log/prompts/surface-1-extractor.systemprompt.txt
  #2 Incident Commander systemMessage            -> docs/prompt-log/prompts/surface-2-agent.systemmessage.txt
     + the four tool descriptions                -> docs/prompt-log/prompts/surface-2-agent.tools.json

Editing a prompt means: edit the file, paste into the node, re-export the flow.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
FLOW_PATH = Path(__file__).parent.parent / "peter-flow.json"
PROMPT_DIR = ROOT / "docs" / "prompt-log" / "prompts"

TOOL_NODES = (
    "Predictor Tool",
    "RAG Query Tool",
    "LangGraph Agent Tool",
    "Service Context Tool",
)


@pytest.fixture(scope="module")
def nodes_by_name() -> dict[str, dict]:
    flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
    return {n["name"]: n for n in flow["nodes"]}


def _file_bytes(name: str) -> bytes:
    path = PROMPT_DIR / name
    assert path.exists(), f"versioned prompt file missing: {path}"
    return path.read_bytes()


def test_surface1_extractor_prompt_matches_file(nodes_by_name: dict) -> None:
    node_prompt = nodes_by_name["Extract Incident Info"]["parameters"]["options"][
        "systemPromptTemplate"
    ]
    assert node_prompt.encode("utf-8") == _file_bytes(
        "surface-1-extractor.systemprompt.txt"
    ), "Extractor systemPromptTemplate drifted from the versioned prompt file"


def test_surface2_agent_system_message_matches_file(nodes_by_name: dict) -> None:
    node_prompt = nodes_by_name["Incident Commander"]["parameters"]["options"][
        "systemMessage"
    ]
    assert node_prompt.encode("utf-8") == _file_bytes(
        "surface-2-agent.systemmessage.txt"
    ), "Incident Commander systemMessage drifted from the versioned prompt file"


def test_surface2_tool_descriptions_match_file(nodes_by_name: dict) -> None:
    tracked = json.loads(_file_bytes("surface-2-agent.tools.json").decode("utf-8"))
    assert set(tracked) == set(TOOL_NODES)
    for name in TOOL_NODES:
        node_description = nodes_by_name[name]["parameters"]["toolDescription"]
        assert node_description == tracked[name], (
            f"{name} toolDescription drifted from surface-2-agent.tools.json"
        )
