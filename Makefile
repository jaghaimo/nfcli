SOURCES = $(shell find fleets/ -iname '*.fleet' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all copy clean format lint cache

all: $(SOURCES)

copy: fleets/Starter\ -\ TF\ Ash.fleet fleets/Starter\ -\ TF\ Oak.fleet
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
	flake8 --max-line-length 120 --max-complexity 10 nfcli
	isort nfcli --check --diff

cache:
	poetry run nfcli --update-wiki
	poetry run nfcli --update-workshop

$(SOURCES):
	python3 -m nfcli -i "$@" -w
