.PHONY: all restore build
all: build

restore:
	dotnet restore

format:
	dotnet csharpier .

build: restore format
	dotnet build
