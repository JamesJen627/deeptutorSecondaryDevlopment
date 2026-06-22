from __future__ import annotations

from deeptutor.services.question_bank.export import (
    EXPORT_HEADERS,
    entries_to_xlsx_bytes,
    parse_xlsx_rows,
)


def test_entries_to_xlsx_bytes_skips_failed_generation() -> None:
    payload = entries_to_xlsx_bytes(
        [
            {
                "question": "[Generation failed] intro",
                "options": {},
                "correct_answer": "N/A",
                "explanation": "N/A",
            },
            {
                "question": "Valid question",
                "options": {"A": "a"},
                "correct_answer": "A",
                "explanation": "ok",
            },
        ]
    )
    rows = parse_xlsx_rows(payload)
    assert len(rows) == 2
    assert rows[1][0] == "Valid question"


def test_entries_to_xlsx_bytes_headers_and_rows() -> None:
    payload = entries_to_xlsx_bytes(
        [
            {
                "question": "法国首都是？",
                "options": {"A": "柏林", "B": "巴黎", "C": "罗马", "D": "马德里"},
                "correct_answer": "B",
                "explanation": "巴黎是法国首都。",
            },
            {
                "question": "2+2=?",
                "options": {},
                "correct_answer": "4",
                "explanation": "基础算术",
            },
        ]
    )
    rows = parse_xlsx_rows(payload)
    assert rows[0] == EXPORT_HEADERS
    assert rows[1][0] == "法国首都是？"
    assert rows[1][1] == "柏林"
    assert rows[1][2] == "巴黎"
    assert rows[1][5] == "B"
    assert rows[1][6] == "巴黎是法国首都。"
    assert rows[2][0] == "2+2=?"
    assert rows[2][5] == "4"
