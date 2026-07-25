import pytest
import requests

import scraper


class MockResponse:
    def __init__(self, payload=None, status_code=200, json_error=None):
        self.payload = payload
        self.status_code = status_code
        self.json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error")

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


def graphql_page(items, has_next_page=False, end_cursor=None):
    return {
        "data": {
            "list": {
                "items": {
                    "edges": [
                        {
                            "node": {
                                "item": {
                                    "__typename": "Title",
                                    **item,
                                }
                            }
                        }
                        for item in items
                    ],
                    "pageInfo": {
                        "hasNextPage": has_next_page,
                        "endCursor": end_cursor,
                    },
                }
            }
        }
    }


def test_scrape_fetches_every_page_in_order_and_preserves_shape(monkeypatch):
    responses = [
        MockResponse(
            graphql_page(
                [
                    {
                        "id": "tt0000001",
                        "titleText": {"text": "First"},
                        "releaseYear": {"year": 2001},
                        "primaryImage": {"url": "https://example.com/first.jpg"},
                    },
                    {
                        "id": "tt0000002",
                        "titleText": {"text": "Second"},
                        "releaseYear": None,
                        "primaryImage": None,
                    },
                ],
                has_next_page=True,
                end_cursor="next-page",
            )
        ),
        MockResponse(
            graphql_page(
                [
                    {
                        "id": "tt0000003",
                        "titleText": {"text": "Third"},
                        "releaseYear": {"year": 2003},
                        "primaryImage": {"url": "https://example.com/third.jpg"},
                    }
                ]
            )
        ),
    ]
    calls = []

    def fake_post(url, *, headers, json, timeout):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return responses.pop(0)

    monkeypatch.setattr(scraper.requests, "post", fake_post)

    assert scraper.scrape_imdb_list("ls031657324") == [
        {
            "title": "First",
            "year": 2001,
            "imdb_id": "tt0000001",
            "poster_url": "https://example.com/first.jpg",
        },
        {
            "title": "Second",
            "year": None,
            "imdb_id": "tt0000002",
            "poster_url": None,
        },
        {
            "title": "Third",
            "year": 2003,
            "imdb_id": "tt0000003",
            "poster_url": "https://example.com/third.jpg",
        },
    ]
    assert [call["json"]["variables"]["after"] for call in calls] == [
        None,
        "next-page",
    ]
    assert all(
        call["json"]["variables"]["id"] == "ls031657324" for call in calls
    )
    assert all("$after: ID" in call["json"]["query"] for call in calls)
    assert all(call["headers"]["Origin"] == "https://www.imdb.com" for call in calls)


def test_scrape_raises_instead_of_returning_partial_graphql_output(monkeypatch):
    responses = [
        MockResponse(
            graphql_page(
                [
                    {
                        "id": "tt0000001",
                        "titleText": {"text": "First"},
                        "releaseYear": {"year": 2001},
                        "primaryImage": None,
                    }
                ],
                has_next_page=True,
                end_cursor="next-page",
            )
        ),
        MockResponse(
            {
                "errors": [
                    {
                        "message": "Upstream resolver failed",
                    }
                ],
                "data": {"list": None},
            }
        ),
    ]

    monkeypatch.setattr(
        scraper.requests,
        "post",
        lambda *args, **kwargs: responses.pop(0),
    )

    with pytest.raises(scraper.IMDbScraperError, match="Upstream resolver failed"):
        scraper.scrape_imdb_list("ls031657324")


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (MockResponse(status_code=503), "HTTP 503"),
        (
            MockResponse(json_error=ValueError("not JSON")),
            "invalid JSON",
        ),
        (
            MockResponse(
                graphql_page([], has_next_page=True, end_cursor=None)
            ),
            "missing an end cursor",
        ),
        (
            MockResponse({"data": {"list": None}}),
            "not found or is unavailable",
        ),
    ],
)
def test_scrape_reports_clear_upstream_failures(monkeypatch, response, message):
    monkeypatch.setattr(
        scraper.requests,
        "post",
        lambda *args, **kwargs: response,
    )

    with pytest.raises(scraper.IMDbScraperError, match=message):
        scraper.scrape_imdb_list("ls031657324")


def test_scrape_rejects_incomplete_items_instead_of_silently_skipping(monkeypatch):
    monkeypatch.setattr(
        scraper.requests,
        "post",
        lambda *args, **kwargs: MockResponse(
            graphql_page(
                [
                    {
                        "id": "tt0000001",
                        "titleText": None,
                        "releaseYear": {"year": 2001},
                        "primaryImage": None,
                    }
                ]
            )
        ),
    )

    with pytest.raises(scraper.IMDbScraperError, match="missing a title"):
        scraper.scrape_imdb_list("ls031657324")
