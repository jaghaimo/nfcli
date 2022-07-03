SOURCES = $(shell find fleets/ -iname '*.fleet' | sed 's/ /\\ /g')

.PHONY: $(SOURCES) all copy clean

all: $(SOURCES)

copy: fleets/Starter\ -\ TF\ Ash.fleet fleets/Starter\ -\ TF\ Oak.fleet
	cp Starter\ -\ TF\ Ash.png images/tf-ash.png
	cp Starter\ -\ TF\ Oak.png images/tf-oak.png

clean:
	rm -f *.png

$(SOURCES):
	python3 -m nfcli -i "$@" -w