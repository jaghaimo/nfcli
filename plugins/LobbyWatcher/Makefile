.PHONY: all restore build release
all: build

restore:
	dotnet restore

format:
	dotnet csharpier .

build: restore format
	dotnet build

release: build
	zip -j LobbyWatcher.zip bin/Debug/net4.6/* ../libs/steam_api64.dll
