SOURCES = $(shell find data/fleets/ -iname '*.fleet' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all copy clean format lint cache

all: $(SOURCES)

copy: data/fleets/Starter\ -\ TF\ Ash.fleet data/fleets/Starter\ -\ TF\ Oak.fleet
	cp Starter\ -\ TF\ Ash.png images/tf-ash.png
	cp Starter\ -\ TF\ Oak.png images/tf-oak.png

clean:
	rm -f *.png
	rm -f *.log
	rm -f *.log.*

format:
	black nfcli
	isort nfcli

lint:
	black --check --no-color --diff nfcli
	flake8 nfcli
	isort nfcli --check --diff

cache:
	poetry run steam
	poetry run wiki

$(SOURCES):
	python3 -m nfcli -i "$@" -w
