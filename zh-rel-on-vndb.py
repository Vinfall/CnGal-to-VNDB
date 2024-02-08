#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation
# VNDB API v2 (Kana): https://api.vndb.org/kana#post-release

import argparse
import os
import sys
import requests
import json
import csv
import re

"""
This script filters zh-Hans & zh-Hant releases on VNDB whose parent VN has an original Chinese language.
"""

# Output files
_OUTPUT_FOLDER = "output/"
_CSV_FILE = "vndb-release.csv"
_JSON_FILE = "vndb-release.json"

# Block word list full of hacky regex
_TO_REPLACE = [
    "(Windows)?( )?パッケージ(特装)?(初回)?版",
    "( )?ダウンロード(通常)?(豪華)?版",
    " オナホール同梱版",
    " ダブルパック",
    " (通常)?DL(通常)?(カード)?版",
    " (通常)?PK版",
    # " 通常DL版",
    " デラックス(DL)?(PK)?版",
    " PK版 デラックス版",
    " - .*? Version$",
    # " - .*? Patch$",
    "Normal Edition",
    " 単体版",
    " 通常版",
    " 特典版",
    " (完全生産)?限定版",
    " 豪華(限定)?(特装)?版",
    " 初回(限定)?(特典)?版",
    # Special cases
    "\\(\\);",  # v33120
    " 拡張KIT版",  # v47887
]

# Query parameters
# fields = "id,title,alttitle,languages.mtl,platforms,media,vns.rtype,producers,released,minage,patch,uncensored,official,extlinks"
fields = "id, title, alttitle, released, vns.id, platforms, producers.name, producers.original"

# To get normalized filters from compact one:
# curl https://api.vndb.org/kana/release --json '{"filters":my_filters,"normalized_filters":true,"results":0}'

# Use compact filter to get rid of all weirdness
# filters = "04122wzh_dHans-2wzh_dHant-gwcomplete-N48123wzh_dHans-3wzh_dHant-jwsteam-"
filters_zh = "03122wzh_dHans-2wzh_dHant-gwcomplete-N48123wzh_dHans-3wzh_dHant-"

# Or use lengthy filters
default_filters = [
    "and",
    ["or", ["lang", "=", "zh-Hans"], ["lang", "=", "zh-Hant"]],
    ["rtype", "=", "complete"],
    ["vn", "=", ["or", ["olang", "=", "zh-Hans"], ["olang", "=", "zh-Hant"]]],
    ["extlink", "=", "steam"],
]

data = {
    "filters": default_filters,
    "fields": fields,
    "sort": "released",
    "reverse": False,
    "results": 100,
    "page": 1,
    # "user": "null",
    # "count": False,
    "compact_filters": False,
    "normalized_filters": True,
}

# Arguments for easy customization
parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--steam",
    required=False,
    default=False,
    help="whether to match Steam releases only, boolean",
)
# 7 is recommended for Steam releases and 14 otherwise
parser.add_argument(
    "-p",
    "--max-page",
    type=int,
    required=False,
    default=2,
    help="max pages of query results, int",
)
args = parser.parse_args()


def get_page(max_page, data):
    # Reasons not using /vn
    # 1. not working well with "released" filter
    # 2. too many alttitles, or no alttitle at all
    api_url = "https://api.vndb.org/kana/release"
    headers = {"Content-Type": "application/json"}
    all_results = []
    # Parse parameter
    if args.steam is not True:
        data["filters"] = filters_zh

    for page in range(1, max_page + 1):
        data["page"] = page

        response = requests.post(api_url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            # Combine response
            if "results" in json_data:
                all_results.extend(json_data["results"])
            else:
                print("No results found for page ", page)
                print(response)
                break
        else:
            print("Post request failed")
            print(response)
            sys.exit()
    print("Post request successful")
    return all_results


# Process & Write results to JSON & CSV
def process_json(results):
    processed_results = []
    for result in results:
        # Convert list to single string in case release contains multiple VNs
        vns_ids = result.get("vns", [])
        first_vns_id = vns_ids[0]["id"] if vns_ids else None
        # Prefer original if any
        producers_data = result.get("producers", None)
        if producers_data is not None:
            producers = []
            for producer_info in producers_data:
                original_name = producer_info.get("original")
                name = producer_info.get("name")
                if original_name is not None:
                    producer = original_name
                else:
                    producer = name
                producers.append(producer)
        else:
            None
        # Build new json
        processed_result = {
            "vid": first_vns_id,
            "id": result["id"],
            "released": result["released"],
            "platform": result["platforms"],
            "producers": producers,
            # "link": result["extlinks"]["url"],
        }
        # Prefer alternative title, if available
        if result["alttitle"] is not None:
            processed_result["title"] = result["alttitle"]
        else:
            processed_result["title"] = result["title"]
        # Replace trailing release variations like `ダウンロード版` and `DLカード版`
        for keyword in _TO_REPLACE:
            processed_result["title"] = re.sub(keyword, "", processed_result["title"])

        processed_results.append(processed_result)

    # Save results to JSON file
    with open(
        f"{_OUTPUT_FOLDER + _JSON_FILE}",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(processed_results, file, ensure_ascii=False, indent=2)

    # Save results to CSV file
    with open(
        _OUTPUT_FOLDER + _CSV_FILE, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        # Do not save lengthy intro
        fields_to_save = ["vid", "id", "title", "released", "producers", "platform"]
        # Use semi-column seperator to avoid mismatches
        writer = csv.DictWriter(csv_file, fieldnames=fields_to_save, delimiter=";")

        writer.writeheader()
        for result in processed_results:
            # Compact fields
            selected_data = {field: result[field] for field in fields_to_save}
            writer.writerow(selected_data)

    return processed_results


os.makedirs(_OUTPUT_FOLDER, exist_ok=True)
j = get_page(args.max_page, data)
results = process_json(j)
