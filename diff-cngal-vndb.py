#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
from thefuzz import fuzz

# Documentation: https://github.com/seatgeek/thefuzz

"""
This script compares CnGal data w/ VNDB existing Chinese VN, and devides the results for future proofings.
"""


# Arguments for easy customization
parser = argparse.ArgumentParser()
"""
parser.add_argument(
    "-f",
    "--fuzzy",
    type=bool,
    required=True,
    default=True,
    help="fuzzy match, boolean, default is True",
)
"""
# Should be recise enough
parser.add_argument(
    "-m",
    "--match-threshold",
    type=int,
    required=False,
    default=75,
    help="Match threshold, int, default is 75",
)
# Can NOT be smaller, counterexample: 诡偶 v.s. 詭偶
parser.add_argument(
    "-n",
    "--fuzzy-threshold",
    type=int,
    required=False,
    default=50,
    help="Miss threshold, int, default is 50, smaller threshold is strongly discouraged",
)
args = parser.parse_args()

matching_titles = []
fuzzy_titles = []
missing_titles = []

with open("output/cngal-release.json", "r", encoding="utf-8") as file:
    cngal_data = json.load(file)

with open("output/vndb-release.json", "r", encoding="utf-8") as file:
    vndb_data = json.load(file)

for cngal_item in cngal_data:
    title_cngal = cngal_item["title"]
    title_matched = False
    match_threshold = args.match_threshold
    fuzzy_threshold = args.fuzzy_threshold
    """
    if args.fuzzy is False:
        for vndb_item in vndb_data:
            # Dumb match
            if cngal_item["title"] == vndb_item["title"]:
                matching_titles.append(vndb_item)
                title_matched = True
                break
    else:
    """
    for vndb_item in vndb_data:
        title_vndb = vndb_item["title"]
        # Dummy match
        if (
            # Avoid wild mismatch like `仿` in `仿生人会梦见电子羊吗`
            len(title_cngal) >= 4
            and len(title_vndb) >= 4
            # Full match
            and (title_vndb in title_cngal or title_cngal in title_vndb)
        ):
            matching_titles.append(vndb_item)
            title_matched = True
            break
        # Fuzzy match
        similarity = fuzz.token_sort_ratio(title_cngal, title_vndb)
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

with open("output/match.json", "w", encoding="utf-8") as file:
    json.dump(matching_titles, file, ensure_ascii=False, indent=2)

with open("output/match.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(matching_titles[0].keys())
    for item in matching_titles:
        csv_writer.writerow(item.values())

with open("output/miss.json", "w", encoding="utf-8") as file:
    json.dump(missing_titles, file, ensure_ascii=False, indent=2)

with open("output/miss.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(missing_titles[0].keys())
    for item in missing_titles:
        csv_writer.writerow(item.values())

# if args.fuzzy is not False:
with open("output/fuzzy.json", "w", encoding="utf-8") as file:
    json.dump(fuzzy_titles, file, ensure_ascii=False, indent=2)

with open("output/fuzzy.csv", "w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["CNGAL Title", "VNDB Title", "Similarity"])
    for item in fuzzy_titles:
        csv_writer.writerow([item[0]["title"], item[1]["title"], item[2]])
