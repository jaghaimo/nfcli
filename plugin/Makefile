.PHONY: all release debug
all: release debug

release:
	msbuild /property:Configuration=Release
	mkdir release
	cp ModInfo.xml obj/Release/HullDumper.dll release

debug:
	msbuild /property:Configuration=Debug
	mkdir debug
	cp ModInfo.xml obj/Debug/HullDumper.dll debug
