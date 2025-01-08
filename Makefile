FLEETS = $(shell find data/fleets -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')
MISSILES = $(shell find data/missiles -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')
SHIPS = $(shell find data/ships -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')
SOURCES = $(shell find data -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')

.PHONY: $(SOURCES)
.PHONY: all clean check format cache steam wiki
.PHONY: fleets missiles missiles

all: $(SOURCES)

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

check:
	poetry run ruff check nfcli/

format:
	poetry run ruff format nfcli/
	poetry run ruff check --fix nfcli/

cache: steam wiki

steam:
	poetry run steam

update:
	poetry update
	pre-commit autoupdate

wiki:
	poetry run wiki

fleets: $(FLEETS)
missiles: $(MISSILES)
ships: $(SHIPS)

$(SOURCES):
	poetry run nfcli -i "$@" -w
