import requests
import json
import sys
import time
import csv

sys.stdout.reconfigure(encoding="utf-8")

url = "https://bina.az/graphql"

headers = {"User-Agent":"Mozilla/5.0", "Accept":"application/json", "Referer": "https://bina.az/"}
headers["x-platform"] = "desktop"
headers["Content-Type"] = "application/json"


def parse_node(node):
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
    variables = {"first": 24}
    if cursor:
        variables["cursor"] = cursor

    page_params = {
        "operationName": "FeaturedItemsRow",
        "variables": json.dumps(variables),
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

while True:
    result = fetch_page(cursor)

    if "data" not in result:
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
    time.sleep(1)

print("total", len(all_items))

with open("data/items.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_items[0].keys())
    writer.writeheader()
    writer.writerows(all_items)
