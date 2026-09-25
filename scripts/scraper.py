import requests
import json
import sys
import time
import csv

# Windows' default console encoding can't print Azerbaijani letters (ı, ə, ş...)
sys.stdout.reconfigure(encoding="utf-8")

url = "https://bina.az/graphql"

# Headers mimic a real browser request. x-platform is required —
# without it the server returns 400 Bad Request.
headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://bina.az/"}
headers["x-platform"] = "desktop"
headers["Content-Type"] = "application/json"


def parse_node(node):
    """Flatten one raw listing (nested JSON) into the fields we care about."""
    # .get(...) or {} guards against null nested objects — e.g. land/commercial
    # listings have no "location" or "area" in the expected shape.
    price = node.get("price") or {}
    area = node.get("area") or {}
    location = node.get("location") or {}
    city = node.get("city") or {}
    return {
        "id": node.get("id"),
        "price": price.get("total"),
        "currency": price.get("currency"),
        "rooms": node.get("rooms"),
        "area": area.get("value"),
        "floor": node.get("floor"),
        "hasRepair": node.get("hasRepair"),
        "location": location.get("name"),
        "city": city.get("name"),
    }


def fetch_page(cursor=None):
    """Fetch one page (24 listings) from bina.az's GraphQL API. cursor=None gets page 1."""
    variables = {"first": 24}
    if cursor:
        variables["cursor"] = cursor

    page_params = {
        "operationName": "FeaturedItemsRow",
        "variables": json.dumps(variables),
        # This site uses persisted queries: instead of sending the full GraphQL
        # query text, only its hash is sent. The server already knows the query.
        "extensions": json.dumps({
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "cc02557ea77b3a51bdca72328af5c60f34c8d80280918d98115862d009a0a31a"
            }
        }),
    }

    response = requests.get(url, params=page_params, headers=headers)
    return response.json()


all_items = []
cursor = None
page_number = 0

# Keep fetching pages until the API says there's nothing left (hasNextPage: false).
# We don't know the total listing count in advance.
while True:
    result = fetch_page(cursor)

    if "data" not in result:
        # A 200 response can still carry a GraphQL error (e.g. wrong operation
        # name) instead of data — print it so the failure is visible, not silent.
        print(result)
        break

    edges = result["data"]["featuredItems"]["edges"]
    page_info = result["data"]["featuredItems"]["pageInfo"]

    for edge in edges:
        all_items.append(parse_node(edge["node"]))

    print("page", page_number, "got", len(edges), "items")
    page_number += 1

    if not page_info["hasNextPage"]:
        break

    cursor = page_info["endCursor"]
    time.sleep(1)  # be polite to the server between requests

print("total", len(all_items))

# Save to disk — all_items only exists in memory otherwise and is lost
# once this script finishes running.
with open("data/items.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_items[0].keys())
    writer.writeheader()
    writer.writerows(all_items)