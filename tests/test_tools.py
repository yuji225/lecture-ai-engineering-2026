"""ツールのテスト（LLMもAPIキーも使わない）。"""

import json
import inspect
from unittest.mock import patch

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} の related に存在しない id: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start タグ"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("エージェント"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "見つかりませんでした" in tools.search_glossary("存在しない用語xyz")


def test_lecture_summary():
    assert "エージェント" in tools.get_lecture_summary(3)
    assert "まだありません" in tools.get_lecture_summary(99)


def test_save_learning_log_has_no_free_text_argument():
    parameters = inspect.signature(tools.save_learning_log).parameters
    assert "content" not in parameters


def test_save_learning_log_reports_empty_quiz_content(tmp_path):
    quiz_path = tmp_path / "quiz.json"

    with patch.object(tools, "QUIZ_PATH", quiz_path):
        assert tools.save_learning_log() == "保存する学習記録が空です。"

        quiz_path.write_text("壊れたJSON", encoding="utf-8")
        assert tools.save_learning_log() == "保存する学習記録が空です。"

        quiz_path.write_text("[]", encoding="utf-8")
        assert tools.save_learning_log() == "保存する学習記録が空です。"


def test_make_quiz_appends_and_save_learning_log_clears(tmp_path):
    log_dir = tmp_path / "learning_log"
    quiz_path = log_dir / "quiz.json"

    with (
        patch.object(tools, "LEARNING_LOG_DIR", log_dir),
        patch.object(tools, "QUIZ_PATH", quiz_path),
        patch.object(tools.random, "choice", lambda items: items[0]),
        patch.object(tools, "load_glossary", return_value=[
            {"term": "用語A", "lecture": 2, "definition": "定義A", "id": "a", "aliases": [], "related": []},
            {"term": "用語B", "lecture": 2, "definition": "定義B", "id": "b", "aliases": [], "related": []},
        ]),
    ):
        tools.make_quiz(2)
        tools.make_quiz(2)

        quizzes = json.loads(quiz_path.read_text(encoding="utf-8"))
        assert len(quizzes) == 2
        assert quizzes[0]["answer"] == "定義A"
        assert quizzes[1]["answer"] == "定義A"

        result = tools.save_learning_log()
        saved_files = list(log_dir.glob("20*.md"))
        assert len(saved_files) == 1
        text = saved_files[0].read_text(encoding="utf-8")
        assert text.count("問題:") == 2
        assert json.loads(quiz_path.read_text(encoding="utf-8")) == []
        assert "保存しました" in result
