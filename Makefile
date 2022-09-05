SOURCES = $(shell find data/ -iname '*.fleet' -o -iname '*.missile' -o -iname '*.ship' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all clean check format lint black flake isort cache steam wiki

all: $(SOURCES)

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

check: format lint

format:
	poetry run black nfcli
	poetry run isort nfcli
	poetry run autoflake --remove-all-unused-imports --remove-unused-variables -i -r nfcli

lint: black flake isort

black:
	poetry run black --check --no-color --diff nfcli

flake:
	poetry run flake8 nfcli

isort:
	poetry run isort nfcli --check --diff

cache: steam wiki

steam:
	poetry run steam

wiki:
	poetry run wiki

$(SOURCES):
	poetry run nfcli -i "$@" -w
