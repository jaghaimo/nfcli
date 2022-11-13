#!/bin/bash

default_dir="/mnt/c/Program Files (x86)/Steam/steamapps/common/Nebulous/Nebulous_Data/Managed"
dir=${1-${default_dir}}
libs="Facepunch.Steamworks.Win64.dll Nebulous.dll UnityEngine.CoreModule.dll"
for l in ${libs}; do
  lib=${dir}/${l}
  cp "${lib}" libs/
done
