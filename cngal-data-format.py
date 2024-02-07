#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import json
import csv
import re


"""
The script makes exported CnGal entries match the format of VNDB one.
Make sure to export JSON on CnGal Data (https://www.cngal.org/data) first.
"""

# Output files
_OUTPUT_FOLDER = "output/"
_CSV_FILE = "cngal-release.csv"
_JSON_FILE = "cngal-release.json"

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
vndb_fields = "id, title, alttitle, released, vns.id"
cngal_fields = "RealId, Name, SteamId, ProductionGroup, Publisher, GamePlatforms"


# Process & Write results to JSON & CSV
def process_json(results):
    processed_results = []
    for result in results:
        full_date = result["IssueTime"]
        if full_date == None:
            iso_date = "9999-12-31"
        else:
            parsed_date = datetime.strptime(full_date, "%Y-%m-%dT%H:%M:%S%z")
            iso_date = parsed_date.strftime("%Y-%m-%d")
        # Build new json
        processed_result = {
            "id": result["RealId"],
            "title": result["Name"],
            "released": iso_date,
            "producer": result["ProductionGroup"],
            "publisher": result["Publisher"],
            "steamid": result["SteamId"],
            "platform": result["GamePlatforms"],
        }
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
        fields_to_save = [
            "id",
            "title",
            "released",
            "producer",
            "publisher",
            "steamid",
            "platform",
        ]
        # Use semi-column seperator to avoid mismatches
        writer = csv.DictWriter(csv_file, fieldnames=fields_to_save, delimiter=";")

        writer.writeheader()
        for result in processed_results:
            # Compact fields
            selected_data = {field: result[field] for field in fields_to_save}
            writer.writerow(selected_data)

    return processed_results


with open("cngal-data-698.json", "r", encoding="utf-8") as file:
    json_data = file.read()
j = json.loads(json_data)
os.makedirs(_OUTPUT_FOLDER, exist_ok=True)
results = process_json(j)
