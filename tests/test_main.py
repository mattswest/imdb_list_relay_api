import asyncio
import json

import pytest
from fastapi import HTTPException

import main


def test_failed_scrape_is_not_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "CACHE_DIR", tmp_path)

    def fail_scrape(list_id):
        raise RuntimeError("IMDb upstream failed")

    monkeypatch.setattr(main, "scrape_imdb_list", fail_scrape)

    with pytest.raises(HTTPException, match="IMDb upstream failed"):
        asyncio.run(main.get_list("ls031657324"))

    assert not (tmp_path / "ls031657324.json").exists()


def test_successful_scrape_is_cached_only_after_completion(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "CACHE_DIR", tmp_path)
    expected = [
        {
            "title": "Example",
            "year": 2024,
            "imdb_id": "tt1234567",
            "poster_url": None,
        }
    ]
    calls = []

    def successful_scrape(list_id):
        calls.append(list_id)
        return expected

    monkeypatch.setattr(main, "scrape_imdb_list", successful_scrape)

    assert asyncio.run(main.get_list("ls031657324")) == expected
    assert json.loads((tmp_path / "ls031657324.json").read_text()) == expected
    assert asyncio.run(main.get_list("ls031657324")) == expected
    assert calls == ["ls031657324"]
