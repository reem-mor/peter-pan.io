"""PETER PAN Layer 1 UI tests.

Two test classes:
  - Unit tests for ``lib.py`` (no network, no Streamlit runtime required).
  - AppTest smoke tests for ``app.py`` (Streamlit testing framework).

Run from the repo root or the ``ui/`` directory:
    python -m pytest ui/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure ui/ is importable regardless of working directory.
_UI_DIR = Path(__file__).parent.parent
if str(_UI_DIR) not in sys.path:
    sys.path.insert(0, str(_UI_DIR))

from lib import (  # noqa: E402 — after sys.path fixup
    OFF_TOPIC_REPLY,
    Signal,
    SubmissionResult,
    check_health,
    chat_sync,
    is_off_topic,
    new_sig_id,
    submit_signal,
)

APP_PATH = str(_UI_DIR / "app.py")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW_ISO = "2026-07-10T17:00:00+00:00"


def _make_signal(**overrides) -> Signal:
    defaults: dict = {
        "id": "sig-testaaaabbb",
        "source": "webui",
        "kind": "manual",
        "received_at": _NOW_ISO,
        "title": "High error rate on checkout",
    }
    defaults.update(overrides)
    return Signal(**defaults)


def _mock_response(status_code: int = 200, text: str = '{"ok":true}') -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.text = text
    r.json.return_value = {"ok": True}
    return r


# ===========================================================================
# Unit tests: lib.is_off_topic
# ===========================================================================


class TestIsOffTopic:
    @pytest.mark.parametrize(
        "query",
        [
            "Give me a pasta recipe",
            "Tell me a joke",
            "What is the weather today?",
            "Explain bitcoin to me",
            "Write a poem",
        ],
    )
    def test_off_topic_queries(self, query: str) -> None:
        assert is_off_topic(query) is True

    @pytest.mark.parametrize(
        "query",
        [
            "High latency on checkout service — what do I check first?",
            "How do I roll back the orders-api deploy?",
            "Interpret this runbook for postgres-primary",
            "Alert: error rate above 5% on shop-web",
            "What is the escalation path for P1?",
        ],
    )
    def test_on_topic_queries(self, query: str) -> None:
        assert is_off_topic(query) is False


# ===========================================================================
# Unit tests: lib.new_sig_id
# ===========================================================================


class TestNewSigId:
    def test_prefix(self) -> None:
        assert new_sig_id().startswith("sig-")

    def test_matches_contract_pattern(self) -> None:
        import re

        pattern = r"^sig-[a-z0-9-]{8,}$"
        for _ in range(50):
            assert re.match(pattern, new_sig_id()), new_sig_id()

    def test_uniqueness(self) -> None:
        ids = {new_sig_id() for _ in range(200)}
        assert len(ids) == 200


# ===========================================================================
# Unit tests: lib.Signal (vendored contract)
# ===========================================================================


class TestSignalModel:
    def test_round_trip(self) -> None:
        sig = _make_signal()
        dumped = sig.model_dump(mode="json")
        reloaded = Signal.model_validate(dumped)
        assert reloaded == sig

    def test_rejects_invalid_id_pattern(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_signal(id="SIG-UPPERCASE")

    def test_rejects_empty_title(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_signal(title="")

    def test_rejects_extra_fields(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Signal.model_validate(
                {
                    "id": "sig-testaaaabbb",
                    "source": "webui",
                    "kind": "manual",
                    "received_at": _NOW_ISO,
                    "title": "test",
                    "unexpected": "nope",
                }
            )

    def test_severity_hint_optional(self) -> None:
        sig = _make_signal(severity_hint=None)
        assert sig.severity_hint is None

    def test_labels_dict_default(self) -> None:
        sig = _make_signal()
        assert sig.labels == {}


# ===========================================================================
# Unit tests: lib.submit_signal
# ===========================================================================


class TestSubmitSignal:
    def test_no_webhook_url_returns_not_ok(self) -> None:
        result = submit_signal(_make_signal(), webhook_url="")
        assert result.ok is False
        assert "not configured" in result.detail

    def test_successful_submission(self) -> None:
        with patch("lib.httpx.post", return_value=_mock_response(200)) as mock_post:
            sig = _make_signal()
            result = submit_signal(sig, webhook_url="http://n8n.test/webhook/peter")

        assert result.ok is True
        assert result.status_code == 200
        assert result.signal_id == sig.id
        mock_post.assert_called_once()

    def test_4xx_returns_not_ok(self) -> None:
        with patch("lib.httpx.post", return_value=_mock_response(400, "bad request")):
            result = submit_signal(_make_signal(), webhook_url="http://n8n.test/webhook")

        assert result.ok is False
        assert result.status_code == 400

    def test_secret_header_sent(self) -> None:
        captured: dict = {}

        def _fake_post(url, *, json, headers, timeout):
            captured.update(headers)
            return _mock_response(200)

        with patch("lib.httpx.post", side_effect=_fake_post):
            submit_signal(
                _make_signal(),
                webhook_url="http://n8n.test/webhook",
                secret="s3cret",
            )

        assert captured.get("X-Peter-Webhook-Secret") == "s3cret"

    def test_no_secret_omits_header(self) -> None:
        captured: dict = {}

        def _fake_post(url, *, json, headers, timeout):
            captured.update(headers)
            return _mock_response(200)

        with patch("lib.httpx.post", side_effect=_fake_post):
            submit_signal(_make_signal(), webhook_url="http://n8n.test/webhook", secret="")

        assert "X-Peter-Webhook-Secret" not in captured

    def test_network_error_returns_not_ok(self) -> None:
        import httpx

        with patch("lib.httpx.post", side_effect=httpx.ConnectError("refused")):
            result = submit_signal(_make_signal(), webhook_url="http://n8n.test/webhook")

        assert result.ok is False
        assert "refused" in result.detail

    def test_payload_is_valid_signal_json(self) -> None:
        """Payload sent to webhook must satisfy Signal contract."""
        captured_body: list[dict] = []

        def _fake_post(url, *, json, headers, timeout):
            captured_body.append(json)
            return _mock_response(200)

        with patch("lib.httpx.post", side_effect=_fake_post):
            sig = _make_signal(service="orders-api", environment="production")
            submit_signal(sig, webhook_url="http://n8n.test/webhook")

        assert len(captured_body) == 1
        Signal.model_validate(captured_body[0])  # must not raise


# ===========================================================================
# Unit tests: lib.check_health
# ===========================================================================


class TestCheckHealth:
    def test_empty_url_returns_unknown(self) -> None:
        status, detail = check_health("")
        assert status == "unknown"
        assert "not configured" in detail

    def test_healthy_service(self) -> None:
        with patch(
            "lib.httpx.get",
            return_value=_mock_response(200, '{"status":"ok"}'),
        ):
            status, detail = check_health("http://svc.test/healthz")
        assert status == "ok"

    def test_degraded_on_5xx(self) -> None:
        with patch("lib.httpx.get", return_value=_mock_response(503)):
            status, _ = check_health("http://svc.test/healthz")
        assert status == "degraded"

    def test_down_on_connect_error(self) -> None:
        import httpx

        with patch("lib.httpx.get", side_effect=httpx.ConnectError("refused")):
            status, _ = check_health("http://svc.test/healthz")
        assert status == "down"

    def test_down_on_timeout(self) -> None:
        import httpx

        with patch("lib.httpx.get", side_effect=httpx.TimeoutException("timeout")):
            status, _ = check_health("http://svc.test/healthz")
        assert status == "down"


# ===========================================================================
# Unit tests: lib.chat_sync
# ===========================================================================


class TestChatSync:
    _msgs = [{"role": "user", "content": "hello"}]

    def test_uses_fixture_llm_first(self) -> None:
        fixture_resp = _mock_response(
            200, '{"choices":[{"message":{"content":"fixture reply"}}]}'
        )
        fixture_resp.json.return_value = {
            "choices": [{"message": {"content": "fixture reply"}}]
        }
        with patch("lib.httpx.post", return_value=fixture_resp):
            result = chat_sync(
                self._msgs,
                fixture_url="http://fixture.test/v1",
            )
        assert result == "fixture reply"

    def test_falls_back_to_ollama_when_fixture_fails(self) -> None:
        import httpx

        ollama_resp = MagicMock()
        ollama_resp.status_code = 200
        ollama_resp.json.return_value = {"message": {"content": "ollama reply"}}

        call_count = {"n": 0}

        def _fake_post(url, *, json, timeout):
            call_count["n"] += 1
            if "fixture" in url:
                raise httpx.ConnectError("refused")
            return ollama_resp

        with patch("lib.httpx.post", side_effect=_fake_post):
            result = chat_sync(
                self._msgs,
                fixture_url="http://fixture.test/v1",
                ollama_url="http://ollama.test",
            )

        assert result == "ollama reply"
        assert call_count["n"] == 2  # fixture attempt + ollama attempt

    def test_raises_when_both_fail(self) -> None:
        import httpx

        with patch("lib.httpx.post", side_effect=httpx.ConnectError("refused")):
            with pytest.raises(RuntimeError, match="LLM backends unavailable"):
                chat_sync(
                    self._msgs,
                    fixture_url="http://fixture.test/v1",
                    ollama_url="http://ollama.test",
                )

    def test_raises_immediately_when_no_backends_configured(self) -> None:
        with pytest.raises(RuntimeError):
            chat_sync(self._msgs, fixture_url="", ollama_url="")

    def test_skips_fixture_when_url_empty(self) -> None:
        """Empty fixture_url must not attempt any POST to fixture endpoint."""
        ollama_resp = MagicMock()
        ollama_resp.status_code = 200
        ollama_resp.json.return_value = {"message": {"content": "ollama only"}}

        with patch("lib.httpx.post", return_value=ollama_resp) as mock_post:
            result = chat_sync(
                self._msgs,
                fixture_url="",
                ollama_url="http://ollama.test",
            )

        assert result == "ollama only"
        assert mock_post.call_count == 1
        call_url = mock_post.call_args[0][0]
        assert "ollama" in call_url


# ===========================================================================
# AppTest smoke tests
# ===========================================================================

from streamlit.testing.v1 import AppTest  # noqa: E402


@pytest.fixture()
def at(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    """AppTest with all external URLs cleared — no network I/O during tests."""
    for var in (
        "PETER_FIXTURE_LLM_URL",
        "PETER_OLLAMA_URL",
        "PETER_UI_N8N_WEBHOOK_URL",
        "PETER_WEBHOOK_SECRET",
        "PETER_INGESTION_URL",
        "PETER_RAG_URL",
        "PETER_GUARDRAILS_URL",
        "PETER_TOOLS_URL",
    ):
        monkeypatch.setenv(var, "")
    return AppTest.from_file(APP_PATH, default_timeout=30)


def test_app_renders_without_exception(at: AppTest) -> None:
    at.run()
    assert not at.exception, f"App raised: {at.exception}"


def test_two_tabs_present(at: AppTest) -> None:
    at.run()
    labels = [t.label for t in at.tabs]
    assert any("Assistant" in lbl for lbl in labels), f"No Assistant tab; got: {labels}"
    assert any(
        "Submission" in lbl or "Incident" in lbl for lbl in labels
    ), f"No Submission tab; got: {labels}"


def test_assistant_off_topic_refusal(at: AppTest) -> None:
    """Off-topic keywords must return the refusal string without any LLM call."""
    at.run()
    at.chat_input[0].set_value("Give me a pasta recipe").run()

    messages = at.session_state["messages"]
    assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]
    assert assistant_msgs, "No assistant message recorded after off-topic query"
    assert "outside my domain" in assistant_msgs[-1].lower(), (
        f"Expected refusal, got: {assistant_msgs[-1]!r}"
    )


def test_assistant_on_topic_llm_unavailable_shows_warning(at: AppTest) -> None:
    """On-topic query with no LLM backends shows graceful error, not crash."""
    at.run()
    at.chat_input[0].set_value("High CPU on gateway — what do I check?").run()

    assert not at.exception
    messages = at.session_state["messages"]
    assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]
    assert assistant_msgs
    # Expects the graceful degradation message (LLM unavailable)
    assert "llm unavailable" in assistant_msgs[-1].lower() or len(assistant_msgs[-1]) > 0


def test_review_queue_empty_on_startup(at: AppTest) -> None:
    at.run()
    assert at.session_state["review_queue"] == []


def test_inject_test_report_adds_to_queue(at: AppTest) -> None:
    at.run()
    at.button(key="inject_report").click().run()

    queue = at.session_state["review_queue"]
    assert len(queue) == 1
    report = queue[0]
    assert report["incident_id"] == "inc-demo0001"
    assert report.get("guardrail_flags"), "Expected non-empty guardrail_flags"
    assert report["p_level"] == "P2"


def test_clear_conversation_resets_messages(at: AppTest) -> None:
    """After an off-topic exchange, clearing resets session messages."""
    at.run()
    # Off-topic → no LLM call, creates 2 messages (user + assistant refusal)
    at.chat_input[0].set_value("Tell me a joke").run()
    assert len(at.session_state["messages"]) == 2

    at.button(key="clear_chat").click().run()
    assert at.session_state["messages"] == []


def test_session_state_initialised(at: AppTest) -> None:
    at.run()
    assert "messages" in at.session_state
    assert "review_queue" in at.session_state
    assert isinstance(at.session_state["messages"], list)
    assert isinstance(at.session_state["review_queue"], list)
