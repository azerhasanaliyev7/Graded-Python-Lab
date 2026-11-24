
"""Running queries against the flight database."""

from validator import valid_datetime


RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price"
}

ALLOWED_KEYS = RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit"
}


def valid_query(query: dict) -> bool:
    if not isinstance(query, dict):
        return False

    for key, value in query.items():

        if key not in ALLOWED_KEYS:
            return False

        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return False

        elif key in ("departure_datetime", "arrival_datetime"):
            if not isinstance(value, str):
                return False

            if not valid_datetime(value):
                return False

        elif key in ("price", "min_price"):
            if type(value) not in (int, float):
                return False

        elif key == "sort_by":
            if not isinstance(value, str):
                return False

            if value not in RECORD_KEYS:
                return False

        elif key == "order":
            if value not in ("asc", "desc"):
                return False

            if "sort_by" not in query:
                return False

        elif key == "limit":
            if type(value) is not int or value < 0:
                return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not valid_query(query):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": []
        }

    matches = []

    for flight in db:

        if "flight_id" in query:
            if flight["flight_id"] != query["flight_id"]:
                continue

        if "origin" in query:
            if flight["origin"] != query["origin"]:
                continue

        if "destination" in query:
            if flight["destination"] != query["destination"]:
                continue

        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                continue

        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                continue

        if "price" in query:
            if flight["price"] > query["price"]:
                continue

        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                continue

        matches.append(flight)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=reverse
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]
