# CnGal -> VNDB

## Introduction

This is a very simple implementation of the initial filtering solution I described on [VNDB discussion board](https://vndb.org/t20918.3). It involves three parts (not exactly the same as below due to technical limitations):
1. compare VNDB release `extlink` (Steam) with CnGal `SteamId`, and pick up those CnGal entries without any matched VNDB release (missing Steam release or not released on Steam at all)
2. compare VNDB `alttitle` with CnGal `name`, and again pick up CnGal entries
3. compare release date (!), this could be wrong due to a bug on CnGal side, but the number of VNs you need to check would be significantly smaller I guess

## Components

- [`zh-rel-on-vndb.py`](zh-rel-on-vndb.py): filter zh-Hans & zh-Hant releases on VNDB whose parent VN has an original Chinese language.
- [`cngal-data-format.py`](cngal-data-format.py): make exported CnGal entries match the format of VNDB one. Exported JSON from [CnGal data page](https://www.cngal.org/data) is needed.
- [`diff-cngal-vndb.py`](diff-cngal-vndb.py): compare CnGal data w/ VNDB existing Chinese VN, and divides the results for future proofing.

## Usage

### Easy Way

Install Python & GNU Make, clone the repo and simply run `make`.
Everything should be done now. Just check `output` for the results.
To clean up the data and restart, run `make clean`.

### Vanilla Way

```sh
pip install -r requirements.txt

# Format CnGal data
python cngal-data-format.py

# Get VNDB data
# Get only Steam releases
python zh-rel-on-vndb.py -p 7 -s 1
# Get every zh-Hans & zh-Hant releases
python zh-rel-on-vndb.py -p 14 -s 0

# Diff CnGal & VNDB data
# Perform a fuzzy comparison
python diff-cngal-vndb.py -m 75 -n 50
```

## Output

- `cngal-releas-*`: formatted CnGal data
- `vndb-release-*`: formatted VNDB data
- `miss-*`: missing CnGal entries on VNDB, add these first
- `fuzzy-*`: possibly missing CnGal entries on VNDB, check these later on
- `match-*`: existing CnGal entries on VNDB, verify these at last

## Todo

- [x] Add glob support in `cngal-data-format.py`
- [x] Make Steam filter optional in `zh-rel-on-vndb.py` for better fuzzy finding
- [x] Add [Makefile](Makefile)
- [ ] Sort fuzzy output descended by similarity
- [ ] Make metadata more informative

## [License](LICENSE)

Data from CnGal and VNDB has their respective licenses applied, you need to search it on the website or source code repository.
The scripts included in this repo is licensed under MIT.
