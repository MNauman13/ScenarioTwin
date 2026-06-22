"""
Unit tests for the guardrail agent.

Pass 1 (regex) is tested without any mocking - it's pure
Python regex, no LLM cost, runs in milliseconds.

Pass 2 (LLM rewrite) is tested by patching 'chat' so no
API key is needed.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from app.agents.guardrail import _DISALLOWED, run


# Table-driven regex tests
# @pytest.mark.parametrize generates one test case per entry.
# If a phrase slips through, the failure message names it exactly.

MUST_FLAG = [
    "You should invest in a global index fund.",
    "I recommend a balanced portfolio.",
    "You must start contributing more to your pension.",
    "The best option for you is a lifetime ISA.",
    "I would advise moving some cash to bonds.",
    "Move your money out of cash savings immediately.",
    "Invest in UK small-cap equities for higher returns.",
    "Buy more international exposure in your portfolio.",
    # Embedded in longer sentences
    "After reviewing your profile, you should consider this.",
    "Based on the data, I recommend a different approach.",
    "To retire at 60, you must save an additional £500/month.",
    "Buy more of what you already hold to reduce your cost basis.",
    # Case variations — patterns use re.IGNORECASE
    "YOU SHOULD diversify your holdings.",
    "I RECOMMEND this strategy.",
    "you MUST act now.",
]

MUST_PASS = [
    "The simulation suggests your median outcome is £1.2m.",
    "Historically, portfolios with higher equity fractions show greater long-run growth.",
    "The projections indicate a range from £600k to £2.4m by year 30.",
    "Based on your inputs, the 10th percentile path ends at £340k.",
    "Some paths experience multiple job disruptions during crisis regimes.",
    "The model shows sensitivity to monthly contribution changes.",
    "Diversification is commonly discussed in financial literature.",
]

@pytest.mark.parametrize("text", MUST_FLAG)
def test_flags_disallowed_phrase(text: str) -> None:
    hits = [p.pattern for p in _DISALLOWED if p.search(text)]
    assert hits, f"Expected a guardrail hit but got none for: {text!r}"

@pytest.mark.parametrize("text", MUST_PASS)
def test_allows_safe_phrase(text: str) -> None:
    hits = [p.pattern for p in _DISALLOWED if p.search(text)]
    assert not hits, f"False positive - safe phrase was flagged by {hits}: {text!r}"


# End-to-end run() tests

def test_run_clean_text_passes_unchanged() -> None:
    """Clean narrative: no regex hit → returned as-is, no flag, no LLM call."""
    clean = "The simulation projects a median portfolio of £1.4m by year 30."
    state = {"raw_narrative": clean, "agent_logs": []}

    result = run(state)

    assert result["guardrail_flag"] is None
    assert result["final_narrative"] == clean
    assert result["agent_logs"][-1]["passed"] is True

def test_run_flagged_text_triggers_rewrite() -> None:
    """Flagged narrative: regex hits → LLM rewrite called, flag set."""
    flagged = "You should put more money into equities."
    rewritten = "Historically, higher equity allocations show greater long-run growth."
    state = {"raw_narrative": flagged, "agent_logs": []}

    with patch("app.agents.guardrail.chat", return_value=rewritten) as mock_chat:
        result = run(state)

    mock_chat.assert_called_once()
    assert result["guardrail_flag"] is not None
    assert result["final_narrative"] == rewritten


def test_run_appends_agent_log() -> None:
    """Each run() call must append exactly one entry to agent_logs."""
    state = {"raw_narrative": "The projections indicate growth.", "agent_logs": []}
    result = run(state)
    assert len(result["agent_logs"]) == 1