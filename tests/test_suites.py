import json

import pytest

from venom.suites import PromptCase, load_suite


def test_load_json_suite(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(
        json.dumps(
            {
                "prompts": [
                    {"name": "hello", "prompt": "Say hello."},
                    {"name": "math", "prompt": "What is 2 + 2?"},
                ]
            }
        ),
        encoding="utf-8",
    )

    assert load_suite(path) == [
        PromptCase(name="hello", prompt="Say hello."),
        PromptCase(name="math", prompt="What is 2 + 2?"),
    ]


def test_load_yaml_suite(tmp_path):
    path = tmp_path / "suite.yaml"
    path.write_text(
        """prompts:\n  - name: concise\n    prompt: Explain recursion in one sentence.\n""",
        encoding="utf-8",
    )

    assert load_suite(path) == [
        PromptCase(name="concise", prompt="Explain recursion in one sentence.")
    ]


def test_reject_duplicate_names(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(
        json.dumps(
            [
                {"name": "same", "prompt": "First"},
                {"name": "same", "prompt": "Second"},
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate prompt name"):
        load_suite(path)


def test_reject_unknown_extension(tmp_path):
    path = tmp_path / "suite.txt"
    path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="must use .json, .yaml, or .yml"):
        load_suite(path)
