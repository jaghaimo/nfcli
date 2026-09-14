CRAFTS = $(shell find data -iname '*.craft' | sed 's/ /\\ /g')
FLEETS = $(shell find data -iname '*.fleet' | sed 's/ /\\ /g')
MISSILES = $(shell find data -iname '*.missile' | sed 's/ /\\ /g')
SHIPS = $(shell find data -iname '*.ship' | sed 's/ /\\ /g')
SOURCES = $(shell find data -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' -o -iname '*.craft' | sed 's/ /\\ /g')

.PHONY: $(SOURCES)
.PHONY: all clean check format cache steam wiki
.PHONY: crafts fleets missiles missiles

all: $(SOURCES)

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

check:
	uv run ruff check nfcli/

format:
	uv run ruff format nfcli/
	uv run ruff check --fix nfcli/

cache: steam wiki

steam:
	uv run steam

update:
	uv update
	pre-commit autoupdate

wiki:
	uv run wiki

crafts: $(CRAFTS)
fleets: $(FLEETS)
missiles: $(MISSILES)
ships: $(SHIPS)

$(SOURCES):
	uv run nfcli -i "$@" -w
