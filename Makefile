SOURCES = $(shell find data/fleets/ -iname '*.fleet' -o -iname '*.missile' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all clean format lint black flake isort cache steam wiki

all: $(SOURCES)

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

format:
	black nfcli
	isort nfcli

lint: black flake isort

black:
	black --check --no-color --diff nfcli

flake:
	flake8 nfcli

isort:
	isort nfcli --check --diff

cache: steam wiki

steam:
	poetry run steam

wiki:
	poetry run wiki

$(SOURCES):
	python3 -m nfcli -i "$@" -w
