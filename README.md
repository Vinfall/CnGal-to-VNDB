# CnGal -> VNDB

## Introduction

This is a very simple implementation of the initial filtering solution I described on [VNDB discussion board](https://vndb.org/t20918.3). It involves three parts (not exactly the same as below due to technical limitations):
1. compare VNDB release extlink (Steam) with CnGal SteamId, and pick up those CnGal entries without any matched VNDB release (missing Steam release or not released on Steam at all)
2. compare VNDB alttitle with CnGal name, and again pick up CnGal entries
3. compare release date (!), this could be wrong due to a bug on CnGal side, but the number of VNs you need to check would be significantly smaller I guess

## Components

- [`zh-steam-rel-on-vndb.py`](zh-steam-rel-on-vndb.py): filter zh-Hans & zh-Hant Steam releases on VNDB whose parent VN has an original Chinese language.
- [`cngal-data-format.py`](cngal-data-format.py): make exported CnGal entries match the format of VNDB one. Exported JSON from [CnGal data page](https://www.cngal.org/data) is needed.
- [`diff-cngal-vndb.py`](diff-cngal-vndb.py): compare CnGal data w/ VNDB existing Chinese VN, and devides the results for future proofings.

## Todo

- [x] Add glob support in `cngal-data-format.py`
- [ ] Discard Steam filter since I use a fuzzy finder now
- [ ] Make metadata more informative

## [License](LICENSE)

Data from CnGal and VNDB has their respective licenses applied, you need to search it on the website or source code repository.
The scripts included in this repo is licensed under MIT.
