# NFCLI helper plugins

Currently there are two helper plugins available - `HullDumper` and `LobbyPoller`.
There is also a standalone version of `LobbyPooler` - a console app `LobbyWatcher`.

## Requirements

- Install mono-devel-6 (Linux) or dotnet-4.5 (Linux/Windows).
- Copy or symlink `Nebulous.dll`, `UnityEngine.dll`, and `UnityEngine.CoreModule.dll` to `libs/` (or `Facepunch.Steamworks.Win64.dll` for the CLI app).
- (CLI, recommended) Run `make`.
- (GUI, unsupported) Open solution in Visual Studio.
