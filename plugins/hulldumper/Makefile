.PHONY: all release debug
all: release debug

release:
	msbuild /property:Configuration=Release
	mkdir -p release
	cp ModInfo.xml HullDumper.png obj/Release/HullDumper.dll release

debug:
	msbuild /property:Configuration=Debug
	mkdir -p debug
	cp ModInfo.xml HullDumper.png obj/Debug/HullDumper.dll debug
