#!/usr/bin/env python3
#$python alttester-instrument.py --help
#$python alttester-instrument.py --version=1.8.2 --assets="C:\GitHub\EndlessRunnerSampleGame\Assets" --manifest="C:\GitHub\EndlessRunnerSampleGame\Packages\manifest.json" --buildFile="C:\GitHub\EndlessRunnerSampleGame\Assets\Editor\BundleAndBuild.cs" --buildMethod="Build()"

import argparse
import urllib.request
from zipfile import ZipFile
import shutil
import json

# Parse sys args
parser=argparse.ArgumentParser()
parser.add_argument("--version", help="The AltTester version to use.")
parser.add_argument("--assets", help="The Assests folder path.")
parser.add_argument("--manifest", help="The manifest file to modify.")
parser.add_argument("--buildFile", help="The build file to modify.")
parser.add_argument("--buildMethod", help="The build method to modify.")
args=parser.parse_args()

# Download AltTester
print(f"version: {args.version}")
zip_url = f"https://github.com/alttester/AltTester-Unity-SDK/archive/refs/tags/v.{args.version}.zip"
urllib.request.urlretrieve(zip_url, "AltTester.zip")

# Add AltTester to project
print(f"assets: {args.assets}")
with ZipFile("AltTester.zip", 'r') as zip:
    zip.extractall(f"{args.assets}/temp")
# \temp\AltTester-Unity-SDK-v.1.8.2\Assets\AltTester
shutil.move(f"{args.assets}/temp/AltTester-Unity-SDK-v.1.8.2/Assets/AltTester", f"{args.assets}/AltTester") 
shutil.rmtree(f"{args.assets}/temp")

# Modify the manifest
print(f"version: {args.manifest}")
newtonsoft = {"com.unity.nuget.newtonsoft-json": "3.0.1"}
testables = {"testables":["com.unity.inputsystem"]}
editorcoroutines = {"com.unity.editorcoroutines": "1.0.0"}
with open(args.manifest,'r+') as file:
    file_data = json.load(file)
    file_data["dependencies"].update(newtonsoft)
    file_data.update(testables)
    file_data["dependencies"].update(editorcoroutines)
    file.seek(0)
    json.dump(file_data, file, indent = 2)

# Modify the build file's using directive
print(f"buildFile: {args.buildFile}")
buildUsingDirectives = """\
using Altom.AltTesterEditor;
using Altom.AltTester;"""
with open(args.buildFile, "r+") as f:
    content = f.read()
    f.seek(0, 0)
    f.write(buildUsingDirectives + "\n" + content)

# ToDo: get list of scenes from `/ProjectSettings/EditorBuildSettings.asset` and add to instrumentation list

# Modify the build file's build method
print(f"buildMethod: {args.buildMethod}")
buildMethodBody = """\
        var buildTargetGroup = BuildTargetGroup.Android;
        AltBuilder.AddAltTesterInScriptingDefineSymbolsGroup(buildTargetGroup);
        if (buildTargetGroup == UnityEditor.BuildTargetGroup.Standalone) {
            AltBuilder.CreateJsonFileForInputMappingOfAxis();
        }
        var instrumentationSettings = new AltInstrumentationSettings();
        AltBuilder.InsertAltInScene(FirstSceneOfTheGame, instrumentationSettings);"""
with open(args.buildFile, 'r') as infile:
    data = infile.read()
rowData = data.split("\n")
outData = []
line_to_add_code = 0
for i in range(len(rowData)):
    outData.append(rowData[i])
    if args.buildMethod in rowData[i]:
        line_to_add_code = i+2
if line_to_add_code > 0:
    outData.insert(line_to_add_code, buildMethodBody)
with open(args.buildFile, 'w') as outfile:
    data = outfile.write('\n'.join(outData))   
