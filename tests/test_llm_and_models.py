import pytest

from core.evidence import parse_evidence_match
from core.llm_client import OllamaClient, parse_json_from_text
from core.requirements import parse_requirements_response
from core.schemas import LLMError, ProvisionalMatchStatus


def test_parse_json_from_markdown_fence():
    raw = 'Here is data:\n```json\n{"ok": true}\n```'
    assert parse_json_from_text(raw) == {"ok": True}


def test_parse_json_trailing_comma_and_prose():
    raw = 'Sure.\n{"ok": true, "n": 1,}\nThanks'
    assert parse_json_from_text(raw)["ok"] is True


def test_parse_requirements_response():
    data = [
        {
            "id": "REQ-001",
            "description": "ID required",
            "category": "document",
            "expected_evidence": "Photo ID",
            "source_page": 1,
            "quotation": "photo identification",
        }
    ]
    reqs = parse_requirements_response(data, "instructions.pdf")
    assert len(reqs) == 1
    assert reqs[0].id == "REQ-001"


def test_parse_requirements_wrapped_object():
    wrapped = {"requirements": [{"id": "REQ-002", "description": "GPA 3.0", "category": "eligibility", "expected_evidence": "transcript", "source_page": 1, "quotation": "GPA 3.0"}]}
    reqs = parse_requirements_response(wrapped, "instructions.pdf")
    assert reqs[0].id == "REQ-002"


def test_invalid_model_response():
    match = parse_evidence_match("not a dict", "REQ-1")
    assert match.provisional_status == ProvisionalMatchStatus.UNCERTAIN


def test_ollama_connection_failure():
    client = OllamaClient(base_url="http://127.0.0.1:59999", timeout=1.0)
    assert not client.is_available()
    with pytest.raises(LLMError):
        client.generate("test")
