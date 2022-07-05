SOURCES = $(shell find fleets/ -iname '*.fleet' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all copy clean

all: $(SOURCES)

copy: fleets/Starter\ -\ TF\ Ash.fleet fleets/Starter\ -\ TF\ Oak.fleet
	cp Starter\ -\ TF\ Ash.png images/tf-ash.png
	cp Starter\ -\ TF\ Oak.png images/tf-oak.png

clean:
	rm -f *.png

format:
	black nfcli
	isort nfcli

lint:
	black --check --no-color --diff nfcli
	flake8 --max-line-length 120 --max-complexity 10 nfcli
	isort nfcli --check --diff

$(SOURCES):
	python3 -m nfcli -i "$@" -w
