.PHONY: all restore build release
all: build

restore:
	dotnet restore

format:
	dotnet csharpier .

build: restore format
	dotnet build

release: build
	zip -j LobbyPoller.zip bin/Debug/net46/LobbyPoller.dll ModInfo.xml
