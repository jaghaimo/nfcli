SOURCES = $(shell find data/ -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all clean check format lint black flake isort cache steam wiki

all: $(SOURCES)

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

check: format lint

format:
	poetry run black nfcli/
	poetry run ruff check --fix nfcli/

lint: black flake isort

black:
	poetry run black --check --no-color --diff nfcli/

ruff:
	poetry run ruff check nfcli/

cache: steam wiki

steam:
	poetry run steam

wiki:
	poetry run wiki

$(SOURCES):
	poetry run nfcli -i "$@" -w
