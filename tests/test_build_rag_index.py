"""実SQLiteと固定ベクトルで、索引作成から検索までを確認する。APIは呼ばない。"""

import json
from unittest.mock import Mock

import pytest

from app import retrieval
from scripts.build_rag_index import build_index


@pytest.fixture
def materials(tmp_path):
    source = tmp_path / "lectures.json"
    source.write_text(json.dumps([
        {"id": f"lec{n:02d}-main", "title": f"講義{n}", "content": [
            {"section": "章", "content": [
                {"id": f"lec{n:02d}-main-p001", "title": f"ページ{n}",
                 "page": 1, "content": f"本文{n}"}]}]}
        for n in (1, 2, 5)
    ], ensure_ascii=False), encoding="utf-8")
    return source, tmp_path / "index.sqlite3"


def test_built_index_can_be_searched(materials, monkeypatch):
    source, database = materials
    texts = []

    def embed(text, task):
        assert task == "RETRIEVAL_DOCUMENT"
        texts.append(text)
        return [1, 0] if "本文1" in text else [0, 1]

    result = build_index(source, database, embedder=embed)
    assert result["pages"] == 2  # 第5回の資料は検索対象に含めない
    assert all("章" in text and "ページ" in text for text in texts)
    monkeypatch.setattr(retrieval, "RAG_DB", database)
    monkeypatch.setattr(retrieval, "embed_text", lambda *_: [1, 0])
    hits = retrieval.search("質問")
    assert [h["page_id"] for h in hits] == ["lec01-main-p001", "lec02-main-p001"]
    assert hits[0]["content"] == "本文1"
    assert hits[0]["distance"] == pytest.approx(0)


def test_search2_adds_unique_neighbors_without_crossing_sections(monkeypatch):
    pages = [
        {"page_id": "p009", "document_id": "lec01-main", "section": "章1", "page": 9, "content": "本文9"},
        {"page_id": "p010", "document_id": "lec01-main", "section": "章1", "page": 10, "content": "本文10"},
        {"page_id": "p011", "document_id": "lec01-main", "section": "章1", "page": 11, "content": "本文11"},
        {"page_id": "p012", "document_id": "lec01-main", "section": "章2", "page": 12, "content": "本文12"},
    ]
    hits = [
        {"page_id": "p010", "distance": 0.1, "content": "本文10"},
        {"page_id": "p011", "distance": 0.2, "content": "本文11"},
    ]
    monkeypatch.setattr(retrieval, "search", lambda query: hits)
    monkeypatch.setattr(retrieval, "load_pages", lambda source: pages)

    result = retrieval.search2("質問")

    assert result["results"] == hits
    assert [page["page_id"] for page in result["context_pages"]] == ["p009"]
    assert result["context_pages"][0]["related_to"] == [
        {"page_id": "p010", "relation": "previous"}
    ]


def test_search2_deduplicates_shared_context_pages(monkeypatch):
    pages = [
        {"page_id": "p009", "document_id": "lec01-main", "section": "章1", "page": 9, "content": "本文9"},
        {"page_id": "p010", "document_id": "lec01-main", "section": "章1", "page": 10, "content": "本文10"},
        {"page_id": "p011", "document_id": "lec01-main", "section": "章1", "page": 11, "content": "本文11"},
        {"page_id": "p012", "document_id": "lec01-main", "section": "章1", "page": 12, "content": "本文12"},
    ]
    hits = [
        {"page_id": "p010", "distance": 0.1, "content": "本文10"},
        {"page_id": "p012", "distance": 0.2, "content": "本文12"},
    ]
    monkeypatch.setattr(retrieval, "search", lambda query: hits)
    monkeypatch.setattr(retrieval, "load_pages", lambda source: pages)

    result = retrieval.search2("質問")

    shared = next(page for page in result["context_pages"] if page["page_id"] == "p011")
    assert shared["related_to"] == [
        {"page_id": "p010", "relation": "next"},
        {"page_id": "p012", "relation": "previous"},
    ]


def test_existing_index_survives_failed_rebuild(materials):
    source, database = materials
    build_index(source, database, embedder=lambda *_: [1, 0])
    before = database.read_bytes()
    embed = Mock(side_effect=RuntimeError("埋め込みに失敗"))
    with pytest.raises(FileExistsError):
        build_index(source, database, embedder=embed)
    embed.assert_not_called()
    with pytest.raises(RuntimeError, match="埋め込みに失敗"):
        build_index(source, database, rebuild=True, embedder=embed)
    assert database.read_bytes() == before
    assert not list(database.parent.glob(".rag-build-*"))
