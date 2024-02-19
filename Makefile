# Makefile for CnGal and VNDB data processing

# Define variables
PYTHON = python
REQUIREMENTS = requirements.txt
VNDB_STEAM = zh-rel-on-vndb.py -p 7 -s 1
VNDB_ALL = zh-rel-on-vndb.py -p 14 -s 0
MIN_MATCH = 75
MAX_MISS = 50

# Default target, run one by one
all:
	$(MAKE) install
	$(MAKE) cngal vna
	$(MAKE) diff

# Install dependencies
install:
	$(PYTHON) -m pip install -r $(REQUIREMENTS)

# Format CnGal data
cngal:
	$(PYTHON) cngal-data-format.py

# Get VNDB data
# Get only Steam releases
vns:
	$(PYTHON) $(VNDB_STEAM)
# Get every zh-Hans & zh-Hant releases
vna:
	$(PYTHON) $(VNDB_ALL)

# Diff CnGal and VNDB data
diff:
	$(PYTHON) diff-cngal-vndb.py -m $(MIN_MATCH) -n $(MAX_MISS)

# Clean up files
clean:
	-rm -f output/*.csv output/*.json
