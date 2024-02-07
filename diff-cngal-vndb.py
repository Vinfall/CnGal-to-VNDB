#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
from thefuzz import fuzz

# Documentation: https://github.com/seatgeek/thefuzz

"""
This script compares CnGal data w/ VNDB existing Chinese VN, and devides the results for future proofings.
"""

with open("output/cngal-release.json", "r", encoding="utf-8") as file:
    cngal_data = json.load(file)

with open("output/vndb-release.json", "r", encoding="utf-8") as file:
    vndb_data = json.load(file)

matching_titles = []
fuzzy_titles = []
missing_titles = []

# Should be recise enough
match_threshold = 75
# Can NOT be smaller, counterexample: 诡偶 v.s. 詭偶
fuzzy_threshold = 50

for cngal_item in cngal_data:
    title_matched = False
    for vndb_item in vndb_data:
        similarity = fuzz.token_sort_ratio(cngal_item["title"], vndb_item["title"])
        if similarity >= match_threshold:
            matching_titles.append(vndb_item)
            title_matched = True
            break
        elif similarity >= fuzzy_threshold:
            fuzzy_titles.append((cngal_item, vndb_item, similarity))
            title_matched = True
            break
    if not title_matched:
        missing_titles.append(cngal_item)

"""
for cngal_item in cngal_data:
    title_exists = False
    for vndb_item in vndb_data:
        if cngal_item["title"] == vndb_item["title"]:
            matching_titles.append(vndb_item)
            title_exists = True
            break
    if not title_exists:
        missing_titles.append(cngal_item)
"""

with open("output/match.json", "w", encoding="utf-8") as file:
    json.dump(matching_titles, file, ensure_ascii=False, indent=2)

with open("output/match.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(matching_titles[0].keys())
    for item in matching_titles:
        csv_writer.writerow(item.values())

with open("output/fuzzy.json", "w", encoding="utf-8") as file:
    json.dump(fuzzy_titles, file, ensure_ascii=False, indent=2)

with open("output/fuzzy.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["CNGAL Title", "VNDB Title", "Similarity"])
    for item in fuzzy_titles:
        csv_writer.writerow([item[0]["title"], item[1]["title"], item[2]])

with open("output/miss.json", "w", encoding="utf-8") as file:
    json.dump(missing_titles, file, ensure_ascii=False, indent=2)

with open("output/miss.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(missing_titles[0].keys())
    for item in missing_titles:
        csv_writer.writerow(item.values())
