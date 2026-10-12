import json

import pytest

from venom.scoring import evaluate, load_scorers, score_rows


def test_load_scorers_and_evaluate_yaml(tmp_path):
    path = tmp_path / "scorers.yaml"
    path.write_text(
        """scorers:
  - name: includes-json
    type: contains
    value: JSON
    case_sensitive: false
  - name: greeting
    type: exact
    value: hello
    strip: true
  - name: email-ish
    type: regex
    value: '^[^@]+@[^@]+\\.[^@]+$'
""",
        encoding="utf-8",
    )

    specs = load_scorers(path)
    assert len(specs) == 3
    assert evaluate("returns json output", specs[0])[0] is True
    assert evaluate("  hello\n", specs[1])[0] is True
    assert evaluate("a@example.com", specs[2])[0] is True


def test_prompt_filter_limits_rule_application(tmp_path):
    path = tmp_path / "scorers.json"
    path.write_text(
        json.dumps(
            {
                "scorers": [
                    {
                        "name": "mentions-recursion",
                        "type": "contains",
                        "value": "recursion",
                        "case_sensitive": False,
                        "prompt": "Explain recursion.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    specs = load_scorers(path)
    rows = [
        {
            "provider": "openai",
            "model": "model-a",
            "prompt": "Explain recursion.",
            "response": "Recursion calls itself.",
        },
        {
            "provider": "anthropic",
            "model": "model-b",
            "prompt": "Say hello.",
            "response": "hello",
        },
    ]

    results = score_rows(rows, specs)

    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].score == 1.0
    assert results[0].provider == "openai"


def test_failed_rule_gets_zero_score(tmp_path):
    path = tmp_path / "scorers.json"
    path.write_text(
        json.dumps({"scorers": [{"name": "must-say-yes", "type": "exact", "value": "yes"}]}),
        encoding="utf-8",
    )
    specs = load_scorers(path)
    rows = [
        {
            "provider": "openai",
            "model": "model-a",
            "prompt": "Answer yes or no.",
            "response": "no",
        }
    ]

    result = score_rows(rows, specs)[0]
    assert result.passed is False
    assert result.score == 0.0


def test_load_scorers_rejects_duplicate_names(tmp_path):
    path = tmp_path / "scorers.json"
    path.write_text(
        json.dumps(
            {
                "scorers": [
                    {"name": "same", "type": "contains", "value": "a"},
                    {"name": "same", "type": "contains", "value": "b"},
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate scorer name"):
        load_scorers(path)


def test_load_scorers_rejects_bad_regex(tmp_path):
    path = tmp_path / "scorers.json"
    path.write_text(
        json.dumps({"scorers": [{"name": "bad", "type": "regex", "value": "["}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid regex"):
        load_scorers(path)
