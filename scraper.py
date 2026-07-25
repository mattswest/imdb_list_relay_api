import re

import requests


GRAPHQL_URL = "https://api.graphql.imdb.com/"
PAGE_SIZE = 100
REQUEST_TIMEOUT = 30
LIST_ID_PATTERN = re.compile(r"^ls\d+$")

GRAPHQL_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.imdb.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}

LIST_QUERY = """
query ListItems($id: ID!, $first: Int!, $after: ID) {
  list(id: $id) {
    items(first: $first, after: $after) {
      edges {
        node {
          item {
            __typename
            ... on Title {
              id
              titleText {
                text
              }
              releaseYear {
                year
              }
              primaryImage {
                url
              }
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""


class IMDbScraperError(RuntimeError):
    """Raised when IMDb cannot provide a complete, valid list."""


def _fetch_page(list_id, after):
    try:
        response = requests.post(
            GRAPHQL_URL,
            headers=GRAPHQL_HEADERS,
            json={
                "query": LIST_QUERY,
                "variables": {
                    "id": list_id,
                    "first": PAGE_SIZE,
                    "after": after,
                },
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = getattr(response, "status_code", "unknown")
        raise IMDbScraperError(
            f"IMDb GraphQL request failed with HTTP {status_code}"
        ) from exc
    except requests.RequestException as exc:
        raise IMDbScraperError(f"IMDb GraphQL request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise IMDbScraperError("IMDb GraphQL returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise IMDbScraperError("IMDb GraphQL returned an invalid response")

    errors = payload.get("errors")
    if errors:
        messages = [
            error.get("message", "unknown GraphQL error")
            for error in errors
            if isinstance(error, dict)
        ]
        detail = "; ".join(messages) or "unknown GraphQL error"
        raise IMDbScraperError(f"IMDb GraphQL error: {detail}")

    data = payload.get("data")
    imdb_list = data.get("list") if isinstance(data, dict) else None
    if imdb_list is None:
        raise IMDbScraperError(
            f"IMDb list {list_id} was not found or is unavailable"
        )

    connection = imdb_list.get("items") if isinstance(imdb_list, dict) else None
    if not isinstance(connection, dict):
        raise IMDbScraperError("IMDb GraphQL response is missing list items")

    edges = connection.get("edges")
    page_info = connection.get("pageInfo")
    if not isinstance(edges, list) or not isinstance(page_info, dict):
        raise IMDbScraperError("IMDb GraphQL response has invalid pagination data")

    return edges, page_info


def _parse_item(edge, position):
    node = edge.get("node") if isinstance(edge, dict) else None
    item = node.get("item") if isinstance(node, dict) else None
    if not isinstance(item, dict):
        raise IMDbScraperError(
            f"IMDb list item {position} is missing title metadata"
        )

    if item.get("__typename") != "Title":
        raise IMDbScraperError(f"IMDb list item {position} is not a title")

    imdb_id = item.get("id")
    if not isinstance(imdb_id, str) or not imdb_id.startswith("tt"):
        raise IMDbScraperError(f"IMDb list item {position} is missing an IMDb ID")

    title_data = item.get("titleText")
    title = title_data.get("text") if isinstance(title_data, dict) else None
    if not isinstance(title, str) or not title:
        raise IMDbScraperError(f"IMDb list item {position} is missing a title")

    year_data = item.get("releaseYear")
    year = year_data.get("year") if isinstance(year_data, dict) else None

    image_data = item.get("primaryImage")
    poster_url = image_data.get("url") if isinstance(image_data, dict) else None

    return {
        "title": title,
        "year": year,
        "imdb_id": imdb_id,
        "poster_url": poster_url,
    }


def scrape_imdb_list(list_id: str):
    """Fetch every title in an IMDb list, preserving IMDb's list order."""
    if not isinstance(list_id, str) or not LIST_ID_PATTERN.fullmatch(list_id):
        raise IMDbScraperError(
            "Invalid IMDb list ID; expected a value such as ls031657324"
        )

    movies = []
    after = None
    seen_cursors = set()

    while True:
        edges, page_info = _fetch_page(list_id, after)
        for edge in edges:
            movies.append(_parse_item(edge, len(movies) + 1))

        has_next_page = page_info.get("hasNextPage")
        if not isinstance(has_next_page, bool):
            raise IMDbScraperError(
                "IMDb GraphQL response is missing a pagination flag"
            )
        if not has_next_page:
            return movies

        end_cursor = page_info.get("endCursor")
        if not isinstance(end_cursor, str) or not end_cursor:
            raise IMDbScraperError(
                "IMDb GraphQL indicated another page but is missing an end cursor"
            )
        if end_cursor in seen_cursors:
            raise IMDbScraperError("IMDb GraphQL returned a repeated page cursor")

        seen_cursors.add(end_cursor)
        after = end_cursor


if __name__ == "__main__":
    import pprint

    try:
        results = scrape_imdb_list("ls031657324")
        pprint.pprint(results[:2])
    except IMDbScraperError as error:
        print(f"Error: {error}")
